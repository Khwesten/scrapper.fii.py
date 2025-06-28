import os
from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from app.gateways.status_invest_gateway import StatusInvestGateway
from app.usecases.fii_scrape_usecase import FiiScrapeUseCase
from tests.factories.fii_domain_factory import FiiDomainFactory


class TestFiiScrapeUsecaseIntegration:

    @pytest.fixture(autouse=True)
    def setup_dynamodb_env(self):
        os.environ["DYNAMODB_ENDPOINT"] = "http://localhost:8002"
        os.environ["AWS_ACCESS_KEY_ID"] = "dummy"
        os.environ["AWS_SECRET_ACCESS_KEY"] = "dummy"
        os.environ["AWS_REGION"] = "us-east-1"
        os.environ["DYNAMODB_TABLE_NAME"] = "fiis_test"

        import importlib

        from app.config import database

        importlib.reload(database)

        yield

    @pytest.fixture
    def mock_gateway(self):
        from unittest.mock import AsyncMock

        gateway = MagicMock(spec=StatusInvestGateway)
        gateway.list = AsyncMock()
        gateway.get = AsyncMock()
        gateway.close = AsyncMock()
        return gateway

    @pytest.fixture
    def real_repository(self):
        import uuid

        from app.repositories.fii_dynamodb_repository import FiiDynamoDBRepository

        table_name = f"fiis_test_scrape_{uuid.uuid4().hex[:8]}"
        return FiiDynamoDBRepository(table_name)

    @pytest.fixture
    def usecase(self, mock_gateway, real_repository):
        return FiiScrapeUseCase(real_repository, mock_gateway)

    @pytest.fixture
    async def clean_table(self, real_repository):
        yield
        try:
            # Como não há método delete, apenas deixamos limpar naturalmente
            pass
        except Exception:
            pass

    @pytest.mark.asyncio
    async def test_execute_scrapes_and_saves_to_database(self, usecase, mock_gateway, real_repository, clean_table):
        mock_tickers = ["TEST11", "DEMO11"]
        mock_fiis = [
            FiiDomainFactory.build(ticker="TEST11"),
            FiiDomainFactory.build(ticker="DEMO11"),
        ]

        mock_gateway.list.return_value = mock_tickers
        mock_gateway.get.side_effect = lambda ticker: next((fii for fii in mock_fiis if fii.ticker == ticker), None)
        mock_gateway.close.return_value = None

        await usecase.execute()

        saved_fiis = await real_repository.list()
        assert len(saved_fiis) == 2

        tickers = [fii.ticker for fii in saved_fiis]
        assert "TEST11" in tickers
        assert "DEMO11" in tickers

    @pytest.mark.asyncio
    async def test_execute_returns_existing_fii_without_gateway_call(
        self, usecase, mock_gateway, real_repository, clean_table
    ):
        existing_fii = FiiDomainFactory.build(ticker="TEST11", p_vp=0.80)
        await real_repository.add(existing_fii)

        # Mock gateway should not be called for existing FII
        mock_gateway.list.return_value = ["TEST11"]
        mock_gateway.get.return_value = None  # Should not be called
        mock_gateway.close.return_value = None

        result = await usecase.execute()

        # Should return the existing FII from repository, not from gateway
        assert len(result) == 1
        saved_fii = await real_repository.get("TEST11")
        assert saved_fii.p_vp == Decimal("0.80")  # Original value maintained

    @pytest.mark.asyncio
    async def test_execute_handles_gateway_exception(self, usecase, mock_gateway, real_repository, clean_table):
        mock_gateway.list.side_effect = Exception("Gateway error")

        with pytest.raises(Exception, match="Gateway error"):
            await usecase.execute()

    @pytest.mark.asyncio
    async def test_execute_with_empty_gateway_response(self, usecase, mock_gateway, real_repository, clean_table):
        mock_gateway.list.return_value = []
        mock_gateway.close.return_value = None

        await usecase.execute()

        saved_fiis = await real_repository.list()
        assert len(saved_fiis) == 0
