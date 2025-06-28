import pytest
from unittest.mock import MagicMock

from app.usecases.fii_list_usecase import FiiListUseCase
from app.repositories.fii_repository import FiiRepository
from tests.factories.fii_domain_factory import FiiDomainFactory


@pytest.fixture
def mock_fii_repository():
    return MagicMock(spec=FiiRepository)


@pytest.fixture
def list_usecase(mock_fii_repository):
    return FiiListUseCase(fii_repository=mock_fii_repository)


@pytest.mark.asyncio
async def test_execute_returns_all_fiis(list_usecase, mock_fii_repository):
    # Arrange
    fiis = [FiiDomainFactory.build() for _ in range(3)]
    mock_fii_repository.list.return_value = fiis
    
    # Act
    result = await list_usecase.execute()
    
    # Assert
    assert result == fiis
    mock_fii_repository.list.assert_called_once()


@pytest.mark.asyncio
async def test_execute_with_empty_repository(list_usecase, mock_fii_repository):
    # Arrange
    mock_fii_repository.list.return_value = []
    
    # Act
    result = await list_usecase.execute()
    
    # Assert
    assert result == []
    mock_fii_repository.list.assert_called_once()
