import pytest
from unittest.mock import MagicMock, AsyncMock

from app.usecases.fii_scrape_usecase import FiiScrapeUseCase
from app.repositories.fii_repository import FiiRepository
from app.gateways.status_invest_gateway import FiiGateway
from app.domain.fii_domain import FiiDomain
from tests.factories.fii_domain_factory import FiiDomainFactory


@pytest.fixture
def mock_fii_repository():
    repository = MagicMock(spec=FiiRepository)
    repository.list = AsyncMock(return_value=[])
    repository.get = AsyncMock(return_value=None)
    repository.add = AsyncMock(return_value=1)
    return repository


@pytest.fixture
def mock_fii_gateway():
    gateway = MagicMock(spec=FiiGateway)
    gateway.list = AsyncMock(return_value=["TEST11", "TEST12"])
    gateway.get = AsyncMock(return_value=FiiDomainFactory.build())
    gateway.close = AsyncMock()
    return gateway


@pytest.fixture
def scrape_usecase(mock_fii_repository, mock_fii_gateway):
    return FiiScrapeUseCase(
        fii_repository=mock_fii_repository,
        fii_gateway=mock_fii_gateway,
        max_concurrent_requests=1
    )


@pytest.mark.asyncio
async def test_execute_with_ticker_list(scrape_usecase, mock_fii_repository, mock_fii_gateway):
    # Arrange
    tickers = ["TEST11", "TEST12"]
    test_fii = FiiDomainFactory.build()
    mock_fii_gateway.get.return_value = test_fii
    
    # Act
    result = await scrape_usecase.execute(tickers=tickers)
    
    # Assert
    assert len(result) == 2
    assert all(isinstance(fii, FiiDomain) for fii in result)
    assert mock_fii_gateway.get.call_count == 2
    mock_fii_repository.add.assert_called()
    mock_fii_gateway.close.assert_called_once()


@pytest.mark.asyncio
async def test_execute_without_tickers_uses_gateway_list(scrape_usecase, mock_fii_gateway):
    # Arrange
    test_fii = FiiDomainFactory.build()
    mock_fii_gateway.get.return_value = test_fii
    
    # Act
    result = await scrape_usecase.execute()
    
    # Assert
    mock_fii_gateway.list.assert_called_once()
    assert len(result) == 2
    mock_fii_gateway.close.assert_called_once()


@pytest.mark.asyncio
async def test_execute_skips_existing_fiis(scrape_usecase, mock_fii_repository, mock_fii_gateway):
    # Arrange
    existing_fii = FiiDomainFactory.build()
    mock_fii_repository.get.return_value = existing_fii
    tickers = ["TEST11"]
    
    # Act
    result = await scrape_usecase.execute(tickers=tickers)
    
    # Assert
    mock_fii_gateway.get.assert_not_called()
    mock_fii_repository.add.assert_not_called()
    assert len(result) == 1
    assert result[0] == existing_fii
    mock_fii_gateway.close.assert_called_once()
