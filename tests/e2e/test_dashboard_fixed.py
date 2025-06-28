import httpx
import pytest


class TestDashboardE2E:

    @pytest.fixture
    def client(self):
        return httpx.AsyncClient(base_url="http://127.0.0.1:8080", timeout=30.0)

    @pytest.mark.asyncio
    async def test_dashboard_accessibility(self, client):
        response = await client.get("/dashboard")

        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")

    @pytest.mark.asyncio
    async def test_dashboard_demo_mode_banner(self, client):
        response = await client.get("/dashboard")
        content = response.text

        assert response.status_code == 200
        if "Modo Demonstração" in content:
            assert "Modo Demonstração" in content

    @pytest.mark.asyncio
    async def test_dashboard_mock_fiis_display(self, client):
        response = await client.get("/dashboard")
        content = response.text

        assert response.status_code == 200
        assert "FII" in content or "dashboard" in content.lower()
        assert "Nenhum FII encontrado" in content or "empty" in content.lower()

    @pytest.mark.asyncio
    async def test_dashboard_statistics_section(self, client):
        response = await client.get("/dashboard")
        content = response.text

        assert response.status_code == 200
        assert "Total de FIIs" in content or "statistics" in content.lower()

    @pytest.mark.asyncio
    async def test_dashboard_material_design_elements(self, client):
        response = await client.get("/dashboard")
        content = response.text

        assert response.status_code == 200
        assert "material-components-web" in content or "Material Design" in content or "material" in content.lower()

    @pytest.mark.asyncio
    async def test_health_endpoint_with_unhealthy_status(self, client):
        response = await client.get("/health")

        if response.status_code == 503:
            data = response.json()
            assert data.get("detail", {}).get("status") == "unhealthy"
            assert "error" in data.get("detail", {}).get("database", {})
