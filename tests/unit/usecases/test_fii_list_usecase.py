import pytest
from unittest.mock import MagicMock, AsyncMock

from app.usecases.fii_list_usecase import FiiListUseCase
from app.repositories.fii_repository import FiiRepository
from tests.factories.fii_domain_factory import FiiDomainFactory


class TestFiiListUseCase:
    @pytest.fixture
    def mock_fii_repository(self):
        return MagicMock(spec=FiiRepository)

    @pytest.fixture
    def list_usecase(self, mock_fii_repository):
        return FiiListUseCase(fii_repository=mock_fii_repository)

    @pytest.mark.asyncio
    async def test_execute_returns_all_fiis(self, list_usecase, mock_fii_repository):
        fiis = [FiiDomainFactory.build() for _ in range(3)]
        mock_fii_repository.list.return_value = fiis
        
        result = await list_usecase.execute()
        
        assert result == fiis
        mock_fii_repository.list.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_with_empty_repository(self, list_usecase, mock_fii_repository):
        mock_fii_repository.list.return_value = []
        
        result = await list_usecase.execute()
        
        assert result == []
        mock_fii_repository.list.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_with_single_fii(self, list_usecase, mock_fii_repository):
        fii = FiiDomainFactory.build()
        mock_fii_repository.list.return_value = [fii]
        
        result = await list_usecase.execute()
        
        assert len(result) == 1
        assert result[0] == fii
        mock_fii_repository.list.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_calls_repository_once(self, list_usecase, mock_fii_repository):
        mock_fii_repository.list.return_value = []
        
        await list_usecase.execute()
        await list_usecase.execute()
        
        assert mock_fii_repository.list.call_count == 2
