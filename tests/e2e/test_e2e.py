import asyncio
import pytest
import httpx
from typing import Dict, Any

BASE_URL = "http://localhost:8001"
TIMEOUT = 30.0

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
    async def test_database_status(self, client):
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
                
        # Test with custom invested value
        response = await client.get("/fiis/magic_numbers?invested_value=5000")
        assert response.status_code == 200
        data = response.json()
        if len(data) > 0:
            assert data[0]["invested_value"] == 5000
    
    @pytest.mark.asyncio
    async def test_complete_workflow(self, client):
        status_response = await client.get("/database/status")
        assert status_response.status_code == 200
        status_data = status_response.json()
        assert status_data["database"]["status"] == "connected"
        assert status_data["scheduler"]["status"] == "active"
        
        # 2. List FIIs (should have data from scheduler)
        list_response = await client.get("/fiis")
        assert list_response.status_code == 200
        fiis = list_response.json()
        assert isinstance(fiis, list)
        
        # 3. Calculate magic numbers if there are FIIs
        if len(fiis) > 0:
            magic_response = await client.get("/fiis/magic_numbers")
            assert magic_response.status_code == 200
            magic_data = magic_response.json()
            assert isinstance(magic_data, list)
        
        # 4. List FIIs and verify our ticker is there
        list_response = await client.get("/fiis")
        assert list_response.status_code == 200
        fiis = list_response.json()
        tickers = [fii["ticker"] for fii in fiis]
        
        # 5. Calculate magic numbers
        magic_response = await client.get("/fiis/magic_numbers")
        assert magic_response.status_code == 200
        magic_numbers = magic_response.json()
        
        # Verify magic numbers structure
        if len(magic_numbers) > 0:
            magic = magic_numbers[0]
            assert isinstance(magic["magic_number"], int)
            assert magic["magic_number"] >= 0

async def run_e2e_tests():
    """Run all E2E tests."""
    import sys
    
    print("🧪 Starting E2E Tests for FII Scraper API")
    print(f"📡 Testing API at: {BASE_URL}")
    
    # Check if API is available
    try:
        async with httpx.AsyncClient(base_url=BASE_URL, timeout=5.0) as client:
            response = await client.get("/health")
            if response.status_code != 200:
                print("❌ API is not responding correctly")
                sys.exit(1)
    except Exception as e:
        print(f"❌ Could not connect to API: {e}")
        print("💡 Make sure the API is running with: make dev-up")
        sys.exit(1)
    
    # Run tests
    test_instance = TestFIIScraperE2E()
    
    tests = [
        ("Health Check", test_instance.test_health_check),
        ("Database Status", test_instance.test_database_status),
        ("List FIIs", test_instance.test_list_fiis),
        ("Magic Numbers", test_instance.test_magic_numbers),
        ("Complete Workflow", test_instance.test_complete_workflow),
    ]
    
    passed = 0
    failed = 0
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=TIMEOUT) as client:
        for test_name, test_func in tests:
            try:
                print(f"🔍 Running: {test_name}")
                await test_func(client)
                print(f"✅ {test_name}: PASSED")
                passed += 1
            except Exception as e:
                print(f"❌ {test_name}: FAILED - {e}")
                failed += 1
    
    print(f"\n📊 Test Results: {passed} passed, {failed} failed")
    
    if failed > 0:
        print("❌ Some tests failed!")
        sys.exit(1)
    else:
        print("🎉 All tests passed!")

if __name__ == "__main__":
    asyncio.run(run_e2e_tests())
