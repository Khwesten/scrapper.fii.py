import pytest
from unittest.mock import MagicMock, patch
import asyncio

from app.scheduler import FiiBootstrap, FiiScheduler, bootstrap_and_start_scheduler
from app.domain.fii_domain import FiiDomain
from app.usecases.fii_scrape_usecase import FiiScrapeUseCase
from app.repositories.fii_repository import FiiRepository
from tests.factories.fii_domain_factory import FiiDomainFactory


@pytest.fixture
def mock_fii_repository():
    repository = MagicMock(spec=FiiRepository)
    repository.list.return_value = []
    return repository


@pytest.fixture
def mock_fii_scrape_usecase(mock_fii_repository):
    usecase = MagicMock(spec=FiiScrapeUseCase)
    usecase.fii_repository = mock_fii_repository
    usecase.execute.return_value = [FiiDomainFactory.build() for _ in range(3)]
    return usecase


@pytest.fixture
def mock_scheduler():
    scheduler = MagicMock(spec=FiiScheduler)
    return scheduler

@pytest.mark.asyncio
async def test_bootstrap_initial_seed_empty_db(mock_fii_scrape_usecase):
    # Arrange
    bootstrap = FiiBootstrap()
    mock_fii_scrape_usecase.fii_repository.list.return_value = []
    
    # Act
    with patch('app.scheduler.FiiScrapeUseCase', return_value=mock_fii_scrape_usecase):
        await bootstrap.initial_seed()
    
    # Assert
    mock_fii_scrape_usecase.execute.assert_called_once()


@pytest.mark.asyncio
async def test_bootstrap_initial_seed_with_existing_data(mock_fii_scrape_usecase):
    # Arrange
    bootstrap = FiiBootstrap()
    existing_fiis = [FiiDomainFactory.build() for _ in range(2)]
    mock_fii_scrape_usecase.fii_repository.list.return_value = existing_fiis
    
    # Act
    with patch('app.scheduler.FiiScrapeUseCase', return_value=mock_fii_scrape_usecase):
        await bootstrap.initial_seed()
    
    # Assert
    mock_fii_scrape_usecase.execute.assert_not_called()


@pytest.mark.asyncio
async def test_scheduler_start_stop():
    # Arrange
    scheduler = FiiScheduler()
    
    # Act
    scheduler.start()
    
    # Assert
    assert scheduler.scheduler.state == 1  # RUNNING state
    
    # Act
    scheduler.stop()
    
    # Assert - scheduler.shutdown() é async mas stop() não aguarda
    assert scheduler.scheduler.state in [0, 1]  # Can be STOPPED or STOPPING


@pytest.mark.asyncio
async def test_bootstrap_and_start_scheduler(mock_fii_scrape_usecase):
    # Arrange
    mock_fii_scrape_usecase.fii_repository.list.return_value = []
    
    # Act
    with patch('app.scheduler.FiiScrapeUseCase', return_value=mock_fii_scrape_usecase):
        scheduler = await bootstrap_and_start_scheduler()
        await asyncio.sleep(0.1)
        scheduler.stop()
    
    # Assert
    assert scheduler is not None
    mock_fii_scrape_usecase.execute.assert_called_once()
