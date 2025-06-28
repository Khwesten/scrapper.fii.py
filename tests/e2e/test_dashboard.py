#!/usr/bin/env python3

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi.testclient import TestClient

from main import app


def test_dashboard():
    """Test the dashboard route"""
    print("🧪 Testing Dashboard Route")
    print("=" * 50)

    client = TestClient(app)

    try:
        # Test dashboard route
        response = client.get("/dashboard")
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            print("✅ Dashboard route working!")
            print(f"Content-Type: {response.headers.get('content-type')}")
            print(f"Content length: {len(response.content)} bytes")

            # Check if it's HTML
            if "text/html" in response.headers.get("content-type", ""):
                print("✅ HTML response confirmed")

                # Check for key HTML elements
                content = response.text
                if "FII Dashboard" in content:
                    print("✅ Dashboard title found")
                if "Material Design" in content:
                    print("✅ Material Design components found")
                if "magic-numbers" in content:
                    print("✅ Magic numbers section found")

            else:
                print("❌ Response is not HTML")

        else:
            print(f"❌ Dashboard route failed: {response.status_code}")
            print(f"Error: {response.text}")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_dashboard()
