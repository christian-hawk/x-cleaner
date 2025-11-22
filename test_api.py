#!/usr/bin/env python
"""
Simple test script for X-Cleaner FastAPI endpoints.

This script tests the basic functionality of the API without starting a server.
"""

from fastapi.testclient import TestClient

from backend.main import app


def test_api_endpoints() -> None:
    """Test basic API endpoints."""
    client = TestClient(app)

    print("🧪 Testing X-Cleaner API Endpoints\n")
    print("=" * 60)

    # Test 1: Root endpoint
    print("\n1. Testing root endpoint (/)...")
    response = client.get("/")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert data["message"] == "X-Cleaner API"
    print("   ✅ Root endpoint working")
    print(f"   Response: {data}")

    # Test 2: Health check
    print("\n2. Testing health check (/health)...")
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    print("   ✅ Health check working")
    print(f"   Response: {data}")

    # Test 3: Stats endpoint (should work even with empty database)
    print("\n3. Testing stats endpoint (/api/stats)...")
    response = client.get("/api/stats")
    assert response.status_code == 200
    data = response.json()
    print("   ✅ Stats endpoint working")
    print(f"   Response: {data}")

    # Test 4: Categories endpoint
    print("\n4. Testing categories endpoint (/api/categories)...")
    response = client.get("/api/categories")
    assert response.status_code == 200
    data = response.json()
    print("   ✅ Categories endpoint working")
    print(f"   Response: Found {data.get('total_categories', 0)} categories")

    # Test 5: Accounts endpoint
    print("\n5. Testing accounts endpoint (/api/accounts)...")
    response = client.get("/api/accounts")
    assert response.status_code == 200
    data = response.json()
    print("   ✅ Accounts endpoint working")
    print(f"   Response: Found {data.get('total', 0)} accounts")

    # Test 6: Scan status endpoint
    print("\n6. Testing scan status endpoint (/api/scan/status)...")
    response = client.get("/api/scan/status")
    assert response.status_code == 200
    data = response.json()
    print("   ✅ Scan status endpoint working")
    print(f"   Response: Status = {data.get('status', 'unknown')}")

    # Test 7: Export endpoint
    print("\n7. Testing export endpoint (/api/export)...")
    response = client.get("/api/export?format=json")
    assert response.status_code == 200
    data = response.json()
    print("   ✅ Export endpoint working")
    print(f"   Response: Exported {len(data.get('accounts', []))} accounts")

    print("\n" + "=" * 60)
    print("✅ All tests passed!")
    print("\n📋 Summary:")
    print("   - Total endpoints tested: 7")
    print("   - All tests passed: ✅")
    print("\n🚀 API is ready to use!")
    print("   Start the server with: uvicorn backend.main:app --reload")
    print("   API docs will be at: http://localhost:8000/docs")


if __name__ == "__main__":
    try:
        test_api_endpoints()
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        raise
