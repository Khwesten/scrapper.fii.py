import asyncio
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from main import app


class TestAPIResilience:

    @pytest.fixture
    def client(self):
        return TestClient(app)

    def test_fiis_endpoint_returns_empty_list_on_repository_failure(self, client):
        with patch("app.repositories.fii_repository_factory.FiiRepositoryFactory.create") as mock_factory:
            mock_repository = AsyncMock()
            mock_repository.list.side_effect = Exception("Database connection error")
            mock_factory.return_value = mock_repository

            response = client.get("/fiis")

            assert response.status_code == 200
            assert response.json() == []

    def test_magic_numbers_endpoint_returns_empty_list_on_repository_failure(self, client):
        with patch("app.repositories.fii_repository_factory.FiiRepositoryFactory.create") as mock_factory:
            mock_repository = AsyncMock()
            mock_repository.list.side_effect = Exception("Database connection error")
            mock_factory.return_value = mock_repository

            response = client.get("/fiis/magic_numbers")

            assert response.status_code == 200
            assert response.json() == []

    def test_magic_numbers_with_invested_value_returns_empty_list_on_failure(self, client):
        with patch("app.repositories.fii_repository_factory.FiiRepositoryFactory.create") as mock_factory:
            mock_repository = AsyncMock()
            mock_repository.list.side_effect = Exception("Database timeout")
            mock_factory.return_value = mock_repository

            response = client.get("/fiis/magic_numbers?invested_value=50000")

            assert response.status_code == 200
            assert response.json() == []

    def test_health_endpoint_graceful_degradation_on_repository_failure(self, client):
        with patch("app.repositories.fii_repository_factory.FiiRepositoryFactory.create") as mock_factory:
            mock_repository = AsyncMock()
            mock_repository.list.side_effect = Exception("Database unavailable")
            mock_factory.return_value = mock_repository

            response = client.get("/health")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert data["database"]["status"] == "initializing"
            assert data["database"]["total_fiis"] == 0
            assert data["scheduler"]["next_update"] == "seeding in progress"

    def test_dashboard_endpoint_returns_empty_stats_on_repository_failure(self, client):
        with patch("app.repositories.fii_repository_factory.FiiRepositoryFactory.create") as mock_factory:
            mock_repository = AsyncMock()
            mock_repository.list.side_effect = Exception("Database error")
            mock_factory.return_value = mock_repository

            response = client.get("/dashboard")

            assert response.status_code == 200
            assert "text/html" in response.headers["content-type"]
