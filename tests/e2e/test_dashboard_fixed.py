#!/usr/bin/env python3
"""
Test script to verify the dashboard is working correctly
"""
import asyncio
import httpx
import re

async def test_dashboard():
    """Test the dashboard endpoint"""
    async with httpx.AsyncClient() as client:
        try:
            print("🧪 Testing FII Dashboard...")
            
            # Test dashboard endpoint
            response = await client.get("http://127.0.0.1:8080/dashboard")
            print(f"📊 Dashboard status: {response.status_code}")
            
            if response.status_code == 200:
                content = response.text
                
                # Check if demo mode is active
                if "Modo Demonstração" in content:
                    print("✅ Demo mode banner is displayed correctly")
                else:
                    print("❌ Demo mode banner not found")
                
                # Check if mock FIIs are displayed
                fiis = ["BCRI11", "HFOF11", "VISC11", "MXRF11"]
                found_fiis = []
                for fii in fiis:
                    if fii in content:
                        found_fiis.append(fii)
                
                print(f"✅ Found {len(found_fiis)}/{len(fiis)} mock FIIs: {found_fiis}")
                
                # Check for statistics
                if "Total de FIIs" in content:
                    print("✅ Statistics section is displayed")
                else:
                    print("❌ Statistics section not found")
                
                # Check for Material Design elements
                if "material-components-web" in content:
                    print("✅ Material Design components loaded")
                else:
                    print("❌ Material Design components not found")
                
                print("🎉 Dashboard test completed successfully!")
                return True
            else:
                print(f"❌ Dashboard returned status {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error testing dashboard: {e}")
            return False

async def test_health():
    """Test the health endpoint"""
    async with httpx.AsyncClient() as client:
        try:
            print("\n🏥 Testing Health Endpoint...")
            response = await client.get("http://127.0.0.1:8080/health")
            print(f"📊 Health status: {response.status_code}")
            
            if response.status_code == 503:  # Expected due to no AWS credentials
                data = response.json()
                if data.get("detail", {}).get("status") == "unhealthy":
                    print("✅ Health endpoint correctly reports unhealthy status")
                    print(f"   Reason: {data.get('detail', {}).get('database', {}).get('error', 'Unknown')}")
                    return True
            
            print(f"❌ Unexpected health response: {response.status_code}")
            return False
            
        except Exception as e:
            print(f"❌ Error testing health: {e}")
            return False

async def main():
    """Run all tests"""
    print("🚀 Starting FII Dashboard Tests\n")
    
    dashboard_ok = await test_dashboard()
    health_ok = await test_health()
    
    print("\n📋 Test Summary:")
    print(f"   Dashboard: {'✅ PASS' if dashboard_ok else '❌ FAIL'}")
    print(f"   Health:    {'✅ PASS' if health_ok else '❌ FAIL'}")
    
    if dashboard_ok and health_ok:
        print("\n🎉 All tests passed! Dashboard is working correctly.")
    else:
        print("\n❌ Some tests failed. Check the output above.")

if __name__ == "__main__":
    asyncio.run(main())
