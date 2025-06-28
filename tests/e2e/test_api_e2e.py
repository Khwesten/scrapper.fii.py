import httpx
import pytest


@pytest.mark.timeout(120)
class TestAPIE2E:

    @pytest.fixture
    def client(self):
        return httpx.AsyncClient(base_url="http://localhost:8080", timeout=30.0)

    @pytest.mark.asyncio
    async def test_health_endpoint_success(self, client):
        response = await client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "FII Scraper API is running" in data["message"]
        assert "database" in data
        assert data["database"]["type"] == "dynamodb"
        assert data["database"]["status"] == "connected"
        assert isinstance(data["database"]["total_fiis"], int)
        assert "scheduler" in data

    @pytest.mark.asyncio
    async def test_database_status_endpoint(self, client):
        response = await client.get("/database/status")

        assert response.status_code == 200
        data = response.json()
        assert "database" in data
        assert data["database"]["type"] == "dynamodb"
        assert data["database"]["status"] == "connected"
        assert isinstance(data["database"]["total_fiis"], int)
        assert "scheduler" in data
        assert data["scheduler"]["status"] == "active"

    @pytest.mark.asyncio
    async def test_status_endpoint(self, client):
        response = await client.get("/status")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "database" in data
        assert "services" in data
        assert "timestamp" in data

    @pytest.mark.asyncio
    async def test_list_fiis_endpoint(self, client):
        response = await client.get("/fiis")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

        if len(data) > 0:
            fii = data[0]
            required_fields = ["ticker", "p_vp", "segment", "duration", "last_price"]
            for field in required_fields:
                assert field in fii

    @pytest.mark.asyncio
    async def test_magic_numbers_endpoint(self, client):
        response = await client.get("/fiis/magic_numbers")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

        if len(data) > 0:
            magic = data[0]
            required_fields = ["ticker", "magic_number", "quotas_for_invested_value", "invested_value"]
            for field in required_fields:
                assert field in magic

    @pytest.mark.asyncio
    async def test_magic_numbers_with_custom_invested_value(self, client):
        custom_value = 5000
        response = await client.get(f"/fiis/magic_numbers?invested_value={custom_value}")

        assert response.status_code == 200
        data = response.json()
        if len(data) > 0:
            assert data[0]["invested_value"] == custom_value

    @pytest.mark.asyncio
    async def test_dashboard_endpoint(self, client):
        response = await client.get("/dashboard")

        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")
        content = response.text
        assert "FII Dashboard" in content or "dashboard" in content.lower()

    @pytest.mark.asyncio
    async def test_root_redirect_to_dashboard(self, client):
        response = await client.get("/", follow_redirects=False)

        assert response.status_code == 302
        assert "/dashboard" in response.headers.get("location", "")

    @pytest.mark.asyncio
    async def test_complete_api_workflow(self, client):
        status_response = await client.get("/database/status")
        assert status_response.status_code == 200
        status_data = status_response.json()
        assert status_data["database"]["status"] == "connected"
        assert status_data["scheduler"]["status"] == "active"

        list_response = await client.get("/fiis")
        assert list_response.status_code == 200
        fiis = list_response.json()
        assert isinstance(fiis, list)

        if len(fiis) > 0:
            magic_response = await client.get("/fiis/magic_numbers")
            assert magic_response.status_code == 200
            magic_data = magic_response.json()
            assert isinstance(magic_data, list)

            if len(magic_data) > 0:
                magic = magic_data[0]
                assert isinstance(magic["magic_number"], int)
                assert magic["magic_number"] >= 0


class TestDashboardE2E:

    @pytest.fixture
    def client(self):
        return httpx.AsyncClient(base_url="http://localhost:8080", timeout=30.0)

    @pytest.mark.asyncio
    async def test_dashboard_accessibility(self, client):
        response = await client.get("/dashboard")

        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")

    @pytest.mark.asyncio
    async def test_dashboard_contains_required_elements(self, client):
        response = await client.get("/dashboard")
        content = response.text

        assert response.status_code == 200
        assert "FII Dashboard" in content or "dashboard" in content.lower() or "Material Design" in content

    @pytest.mark.asyncio
    async def test_dashboard_mock_data_display(self, client):
        response = await client.get("/dashboard")
        content = response.text

        assert response.status_code == 200
        mock_elements = ["BCRI11", "HFOF11", "VISC11", "MXRF11", "Total de FIIs", "statistics"]
        found_elements = [element for element in mock_elements if element in content]
        assert len(found_elements) > 0
