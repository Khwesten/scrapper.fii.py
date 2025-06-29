import httpx
import pytest

BASE_URL = "http://localhost:8080"
TIMEOUT = 30.0


@pytest.mark.timeout(120)
class TestFIIScraperE2E:

    @pytest.fixture
    def client(self):
        return httpx.AsyncClient(base_url=BASE_URL, timeout=TIMEOUT)

    @pytest.mark.asyncio
    async def test_health_check(self, client):
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
    async def test_list_fiis(self, client):
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
    async def test_magic_numbers(self, client):
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
    async def test_magic_numbers_with_custom_value(self, client):
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
    async def test_root_redirect(self, client):
        response = await client.get("/", follow_redirects=False)

        assert response.status_code == 302
        assert response.headers["location"] == "/dashboard"

    @pytest.mark.asyncio
    async def test_complete_workflow(self, client):
        status_response = await client.get("/health")
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
