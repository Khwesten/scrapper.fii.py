from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.repositories.fii_dynamodb_repository import FiiDynamoDBRepository
from tests.factories.fii_domain_factory import FiiDomainFactory


class TestFiiDynamoDbRepositoryUnit:

    @pytest.fixture
    def mock_table(self):
        table = AsyncMock()
        table.put_item = AsyncMock()
        table.get_item = AsyncMock()
        table.scan = AsyncMock()
        table.update_item = AsyncMock()
        return table

    @pytest.fixture
    def mock_session(self, mock_table):
        session = MagicMock()

        # Mock the resource context manager
        resource_mock = AsyncMock()
        resource_mock.__aenter__ = AsyncMock(return_value=MagicMock())
        resource_mock.__aenter__.return_value.Table = AsyncMock(return_value=mock_table)
        resource_mock.__aexit__ = AsyncMock(return_value=None)
        session.resource.return_value = resource_mock

        # Mock the client context manager for table creation
        client_mock = AsyncMock()
        client_mock.__aenter__ = AsyncMock(return_value=MagicMock())
        client_mock.__aenter__.return_value.describe_table = AsyncMock()
        client_mock.__aexit__ = AsyncMock(return_value=None)
        session.client.return_value = client_mock

        return session

    @pytest.fixture
    def repository(self, mock_session):
        with patch("app.repositories.fii_dynamodb_repository.Session", return_value=mock_session):
            return FiiDynamoDBRepository("test_table")

    @pytest.mark.asyncio
    async def test_add_fii_calls_put_item(self, repository, mock_table):
        fii = FiiDomainFactory.build()

        await repository.add(fii)

        mock_table.put_item.assert_called_once()
        call_args = mock_table.put_item.call_args[1]
        assert "Item" in call_args
        assert call_args["Item"]["ticker"] == fii.ticker

    @pytest.mark.asyncio
    async def test_get_fii_calls_get_item(self, repository, mock_table):
        mock_table.get_item.return_value = {}  # No "Item" key when not found

        result = await repository.get("TEST11")

        mock_table.get_item.assert_called_once_with(Key={"ticker": "TEST11"})
        assert result is None

    @pytest.mark.asyncio
    async def test_get_fii_returns_domain_when_found(self, repository, mock_table):
        fii_data = {
            "ticker": "TEST11",
            "p_vp": "0.95",
            "segment": "Logística",
            "duration": "Indeterminado",
            "last_12_month_evaluation": "8.5",
            "current_month_evaluation": "1.2",
            "dy_12": "8.5",
            "last_dividend": "1.20",
            "last_price": "100.0",
            "dialy_liquidity": "50000",
        }
        mock_table.get_item.return_value = {"Item": fii_data}

        result = await repository.get("TEST11")

        assert result is not None
        assert result.ticker == "TEST11"

    @pytest.mark.asyncio
    async def test_list_fiis_calls_scan(self, repository, mock_table):
        mock_table.scan.return_value = {"Items": []}

        result = await repository.list()

        mock_table.scan.assert_called_once()
        assert result == []
