import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.repositories.fii_repository import FiiRepository
from app.scheduler import FiiBootstrap, FiiScheduler, bootstrap_and_start_scheduler
from app.usecases.fii_scrape_usecase import FiiScrapeUseCase
from tests.factories.fii_domain_factory import FiiDomainFactory


class TestFiiBootstrap:
    @pytest.fixture
    def mock_fii_repository(self):
        repository = MagicMock(spec=FiiRepository)
        repository.list = AsyncMock(return_value=[])
        return repository

    @pytest.fixture
    def mock_fii_scrape_usecase(self, mock_fii_repository):
        usecase = MagicMock(spec=FiiScrapeUseCase)
        usecase.fii_repository = mock_fii_repository
        usecase.execute = AsyncMock(return_value=[FiiDomainFactory.build() for _ in range(3)])
        return usecase

    @pytest.fixture
    def bootstrap(self):
        return FiiBootstrap()

    @pytest.mark.asyncio
    async def test_initial_seed_empty_db(self, bootstrap, mock_fii_scrape_usecase):
        mock_fii_scrape_usecase.fii_repository.list.return_value = []

        with patch("app.scheduler.FiiScrapeUseCase", return_value=mock_fii_scrape_usecase):
            with patch("asyncio.sleep", new_callable=AsyncMock):
                await bootstrap.initial_seed()

        mock_fii_scrape_usecase.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_initial_seed_with_existing_data(self, bootstrap, mock_fii_scrape_usecase):
        existing_fiis = [FiiDomainFactory.build() for _ in range(2)]
        mock_fii_scrape_usecase.fii_repository.list.return_value = existing_fiis

        with patch("app.scheduler.FiiScrapeUseCase", return_value=mock_fii_scrape_usecase):
            await bootstrap.initial_seed()

        mock_fii_scrape_usecase.execute.assert_not_called()

    @pytest.mark.asyncio
    async def test_initial_seed_gateway_error_fallback(self, bootstrap, mock_fii_scrape_usecase):
        mock_fii_scrape_usecase.fii_repository.list.return_value = []
        mock_fii_scrape_usecase.execute.side_effect = [
            Exception("Gateway error"),
            [FiiDomainFactory.build() for _ in range(3)],
        ]

        with patch("app.scheduler.FiiScrapeUseCase", return_value=mock_fii_scrape_usecase):
            with patch("asyncio.sleep", new_callable=AsyncMock):
                await bootstrap.initial_seed()

        assert mock_fii_scrape_usecase.execute.call_count == 2
        second_call_args = mock_fii_scrape_usecase.execute.call_args_list[1]
        assert "tickers" in second_call_args.kwargs
        assert len(second_call_args.kwargs["tickers"]) == 20

    @pytest.mark.asyncio
    async def test_initial_seed_complete_failure(self, bootstrap, mock_fii_scrape_usecase):
        mock_fii_scrape_usecase.fii_repository.list.side_effect = Exception("Repository error")

        with patch("app.scheduler.FiiScrapeUseCase", return_value=mock_fii_scrape_usecase):
            await bootstrap.initial_seed()

        mock_fii_scrape_usecase.execute.assert_not_called()

    def test_bootstrap_has_popular_fiis(self, bootstrap):
        assert len(bootstrap.popular_fiis) == 20
        assert "BCRI11" in bootstrap.popular_fiis
        assert "BBFI11" in bootstrap.popular_fiis


class TestFiiScheduler:
    @pytest.fixture
    def scheduler(self):
        return FiiScheduler()

    @pytest.mark.asyncio
    async def test_scheduler_start_stop(self, scheduler):
        scheduler.start()

        assert scheduler.scheduler.state == 1

        scheduler.stop()

        assert scheduler.scheduler.state in [0, 1]

    def test_scheduler_initialization(self, scheduler):
        assert scheduler.scheduler is not None
        assert hasattr(scheduler, "start")
        assert hasattr(scheduler, "stop")


class TestBootstrapAndStartScheduler:
    @pytest.fixture
    def mock_fii_scrape_usecase(self):
        usecase = MagicMock(spec=FiiScrapeUseCase)
        mock_repository = MagicMock()
        mock_repository.list = AsyncMock(return_value=[])
        usecase.fii_repository = mock_repository
        usecase.execute = AsyncMock(return_value=[FiiDomainFactory.build() for _ in range(3)])
        return usecase

    @pytest.mark.asyncio
    async def test_bootstrap_and_start_scheduler(self, mock_fii_scrape_usecase):
        with patch("app.scheduler.FiiScrapeUseCase", return_value=mock_fii_scrape_usecase):
            with patch("asyncio.sleep", new_callable=AsyncMock):
                scheduler = await bootstrap_and_start_scheduler()
                await asyncio.sleep(0.1)
                scheduler.stop()

        assert scheduler is not None
        mock_fii_scrape_usecase.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_bootstrap_and_start_scheduler_with_existing_data(self, mock_fii_scrape_usecase):
        existing_fiis = [FiiDomainFactory.build()]
        mock_fii_scrape_usecase.fii_repository.list.return_value = existing_fiis

        with patch("app.scheduler.FiiScrapeUseCase", return_value=mock_fii_scrape_usecase):
            scheduler = await bootstrap_and_start_scheduler()
            scheduler.stop()

        assert scheduler is not None
        mock_fii_scrape_usecase.execute.assert_not_called()
