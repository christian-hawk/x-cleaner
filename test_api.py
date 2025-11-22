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
    assert data["name"] == "X-Cleaner API"
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

    # Test 3: Overall statistics endpoint
    print("\n3. Testing overall stats endpoint (/api/statistics/overall)...")
    response = client.get("/api/statistics/overall")
    assert response.status_code == 200
    data = response.json()
    print("   ✅ Overall stats endpoint working")
    print(f"   Response: {data}")

    # Test 4: Category statistics endpoint
    print("\n4. Testing category stats endpoint (/api/statistics/categories)...")
    response = client.get("/api/statistics/categories")
    assert response.status_code == 200
    data = response.json()
    print("   ✅ Category stats endpoint working")
    print(f"   Response: Found {len(data.get('categories', []))} categories")

    # Test 5: Accounts endpoint
    print("\n5. Testing accounts endpoint (/api/accounts)...")
    response = client.get("/api/accounts")
    assert response.status_code == 200
    data = response.json()
    print("   ✅ Accounts endpoint working")
    print(f"   Response: Found {data.get('total', 0)} accounts")

    print("\n" + "=" * 60)
    print("✅ All tests passed!")
    print("\n📋 Summary:")
    print("   - Total endpoints tested: 5")
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
