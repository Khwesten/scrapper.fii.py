from unittest.mock import AsyncMock, Mock, patch

import pytest

from app.scheduler import FiiBootstrap, FiiScheduler


class TestFiiBootstrapIntegration:
    """Integration tests for FiiBootstrap"""

    @pytest.fixture
    def bootstrap(self):
        """Fixture providing a FiiBootstrap instance"""
        return FiiBootstrap()

    async def test_initial_seed_skips_when_database_has_fiis(self, bootstrap):
        """Test initial_seed skips when database already has FIIs"""
        with patch("app.scheduler.FiiScrapeUseCase") as mock_usecase_class:
            mock_usecase = Mock()
            mock_usecase.fii_repository.list.return_value = [Mock(), Mock()]  # Non-empty list
            mock_usecase_class.return_value = mock_usecase

            await bootstrap.initial_seed()

            # Should check repository but not execute scraping
            mock_usecase.fii_repository.list.assert_called_once()
            mock_usecase.execute.assert_not_called()

    async def test_initial_seed_uses_gateway_when_available(self, bootstrap):
        """Test initial_seed uses gateway when available"""
        with patch("app.scheduler.FiiScrapeUseCase") as mock_usecase_class:
            mock_usecase = Mock()
            mock_usecase.fii_repository.list = AsyncMock(return_value=[])  # Empty list
            mock_usecase.execute = AsyncMock(return_value=[Mock(), Mock(), Mock()])  # 3 FIIs scraped
            mock_usecase_class.return_value = mock_usecase

            with patch("asyncio.sleep", new_callable=AsyncMock):  # Mock sleep to speed up test
                await bootstrap.initial_seed()

            # Should check repository and execute scraping
            mock_usecase.fii_repository.list.assert_called_once()
            mock_usecase.execute.assert_called_once_with()

    async def test_initial_seed_uses_fallback_on_gateway_error(self, bootstrap):
        """Test initial_seed uses popular FIIs fallback when gateway fails"""
        with patch("app.scheduler.FiiScrapeUseCase") as mock_usecase_class:
            mock_usecase = Mock()
            mock_usecase.fii_repository.list = AsyncMock(return_value=[])  # Empty list
            # First call raises exception, second call succeeds
            mock_usecase.execute = AsyncMock(side_effect=[Exception("Gateway error"), [Mock(), Mock()]])
            mock_usecase_class.return_value = mock_usecase

            with patch("asyncio.sleep", new_callable=AsyncMock):  # Mock sleep to speed up test
                await bootstrap.initial_seed()

            # Should check repository and execute scraping twice (gateway + fallback)
            mock_usecase.fii_repository.list.assert_called_once()
            assert mock_usecase.execute.call_count == 2
            # Second call should have tickers parameter
            mock_usecase.execute.assert_called_with(tickers=bootstrap.popular_fiis)

    async def test_initial_seed_handles_repository_error(self, bootstrap):
        """Test initial_seed handles repository error gracefully"""
        with patch("app.scheduler.FiiScrapeUseCase") as mock_usecase_class:
            mock_usecase = Mock()
            mock_usecase.fii_repository.list.side_effect = Exception("Database error")
            mock_usecase_class.return_value = mock_usecase

            # Should not raise exception
            await bootstrap.initial_seed()

            mock_usecase.fii_repository.list.assert_called_once()


class TestFiiSchedulerIntegration:
    """Integration tests for FiiScheduler"""

    @pytest.fixture
    def scheduler(self):
        """Fixture providing a FiiScheduler instance"""
        return FiiScheduler()

    async def test_scheduled_update_executes_scrape_usecase(self, scheduler):
        """Test scheduled_update executes FiiScrapeUseCase"""
        with patch("app.scheduler.FiiScrapeUseCase") as mock_usecase_class:
            mock_usecase = Mock()
            mock_usecase.fii_repository.list = AsyncMock(return_value=[Mock()])  # Existing FIIs
            mock_usecase.execute = AsyncMock(return_value=[Mock(), Mock()])  # 2 FIIs scraped
            mock_usecase_class.return_value = mock_usecase

            await scheduler.scheduled_update()

            mock_usecase_class.assert_called_once()
            mock_usecase.execute.assert_called_once()

    async def test_scheduled_update_handles_usecase_error(self, scheduler):
        """Test scheduled_update handles usecase error gracefully"""
        with patch("app.scheduler.FiiScrapeUseCase") as mock_usecase_class:
            mock_usecase = Mock()
            mock_usecase.fii_repository.list = AsyncMock(return_value=[Mock(ticker="TEST11")])  # Existing FIIs
            mock_usecase.execute = AsyncMock(side_effect=Exception("Scraping error"))
            mock_usecase_class.return_value = mock_usecase

            # Should not raise exception
            await scheduler.scheduled_update()

            mock_usecase_class.assert_called_once()
            # Should be called twice: first attempt fails, then fallback with existing tickers
            assert mock_usecase.execute.call_count == 2

    def test_scheduler_is_async_io_scheduler(self, scheduler):
        """Test that scheduler uses AsyncIOScheduler"""
        from apscheduler.schedulers.asyncio import AsyncIOScheduler

        assert isinstance(scheduler.scheduler, AsyncIOScheduler)

    def test_start_configures_scheduler_correctly(self, scheduler):
        """Test start method configures scheduler with correct parameters"""
        with patch.object(scheduler.scheduler, "add_job") as mock_add_job:
            with patch.object(scheduler.scheduler, "start") as mock_start:
                scheduler.start()

                # Should add job and start scheduler
                mock_add_job.assert_called_once()
                mock_start.assert_called_once()

    def test_stop_shuts_down_scheduler(self, scheduler):
        """Test stop method shuts down scheduler"""
        with patch.object(scheduler.scheduler, "shutdown") as mock_shutdown:
            scheduler.stop()

            mock_shutdown.assert_called_once()

    def test_multiple_start_calls_are_safe(self, scheduler):
        """Test multiple start calls don't cause errors"""
        with patch.object(scheduler.scheduler, "add_job"):
            with patch.object(scheduler.scheduler, "start") as mock_start:
                # Should not raise exception on multiple calls
                scheduler.start()
                scheduler.start()

                # start might be called multiple times but shouldn't error
                assert mock_start.call_count >= 1

    def test_multiple_stop_calls_are_safe(self, scheduler):
        """Test multiple stop calls don't cause errors"""
        with patch.object(scheduler.scheduler, "shutdown") as mock_shutdown:
            # Should not raise exception on multiple calls
            scheduler.stop()
            scheduler.stop()

            # shutdown might be called multiple times but shouldn't error
            assert mock_shutdown.call_count >= 1
