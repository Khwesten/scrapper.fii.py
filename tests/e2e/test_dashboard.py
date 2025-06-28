import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import pytest
from fastapi.testclient import TestClient

from main import app


class TestDashboard:

    @pytest.fixture
    def client(self):
        return TestClient(app)

    def test_dashboard_route_accessibility(self, client):
        response = client.get("/dashboard")

        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")

    def test_dashboard_content_structure(self, client):
        response = client.get("/dashboard")
        content = response.text

        assert response.status_code == 200
        assert "FII Dashboard" in content or "dashboard" in content.lower()

    def test_dashboard_material_design_components(self, client):
        response = client.get("/dashboard")
        content = response.text

        assert response.status_code == 200
        assert "Material Design" in content or "material-components" in content

    def test_dashboard_magic_numbers_section(self, client):
        response = client.get("/dashboard")
        content = response.text

        assert response.status_code == 200
        assert "magic-numbers" in content or "Magic Numbers" in content
