import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import httpx
import pytest


@pytest.mark.timeout(60)
class TestDashboard:

    @pytest.fixture
    def client(self):
        return httpx.AsyncClient(base_url="http://localhost:8080", timeout=30.0)

    @pytest.mark.asyncio
    async def test_dashboard_route_accessibility(self, client):
        response = await client.get("/dashboard")

        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")

    @pytest.mark.asyncio
    async def test_dashboard_content_structure(self, client):
        response = await client.get("/dashboard")
        content = response.text

        assert response.status_code == 200
        assert "FII Dashboard" in content or "dashboard" in content.lower()

    @pytest.mark.asyncio
    async def test_dashboard_material_design_components(self, client):
        response = await client.get("/dashboard")
        content = response.text

        assert response.status_code == 200
        assert "Material Design" in content or "material-components" in content

    @pytest.mark.asyncio
    async def test_dashboard_magic_numbers_section(self, client):
        response = await client.get("/dashboard")
        content = response.text

        assert response.status_code == 200
        assert "magic-numbers" in content or "Magic Numbers" in content
