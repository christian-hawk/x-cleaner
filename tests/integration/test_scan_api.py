"""
Integration tests for scan API endpoints.

Tests the FastAPI scan endpoints with real HTTP requests.
"""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from backend.core.progress_tracker import progress_tracker
from backend.main import app
from backend.models import CategorizedAccount, XAccount


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_x_accounts():
    """Create mock X accounts."""
    return [
        XAccount(
            user_id="1",
            username="testuser",
            display_name="Test User",
            bio="Test bio",
            verified=False,
            followers_count=100,
            following_count=50,
            tweet_count=200,
        )
    ]


@pytest.fixture
def mock_categorized_accounts(mock_x_accounts):
    """Create mock categorized accounts."""
    return [
        CategorizedAccount(
            **mock_x_accounts[0].model_dump(),
            category="Test Category",
            confidence=0.9,
            reasoning="Test reasoning",
        )
    ]


@pytest.fixture
def mock_categories():
    """Create mock categories."""
    return {
        "categories": [
            {
                "name": "Test Category",
                "description": "Test description",
                "characteristics": ["test"],
                "estimated_percentage": 100,
            }
        ],
        "total_categories": 1,
        "analysis_summary": "Test summary",
    }


def test_trigger_scan_endpoint(client):
    """Test POST /api/scan endpoint."""

    with patch("backend.api.routes.scan.run_scan_task") as mock_task:
        # Trigger scan
        response = client.post("/api/scan", params={"user_id": "test_user_123"})

        # Verify response
        assert response.status_code == 200
        data = response.json()

        assert "job_id" in data
        assert data["status"] == "started"
        assert "message" in data

        # Verify background task was scheduled
        # Note: We can't easily test if BackgroundTasks actually runs,
        # but we can verify the endpoint responds correctly


def test_get_scan_status_endpoint(client):
    """Test GET /api/scan/{job_id}/status endpoint."""

    # Create a mock job
    job_id = "test-job-123"
    progress_tracker.create_job(job_id)
    progress_tracker.update_progress(job_id, "Testing", 50)

    try:
        # Get status
        response = client.get(f"/api/scan/{job_id}/status")

        # Verify response
        assert response.status_code == 200
        data = response.json()

        assert data["job_id"] == job_id
        assert data["message"] == "Testing"
        assert data["progress"] == 50
        assert data["status"] == "running"

    finally:
        # Cleanup
        progress_tracker.remove_job(job_id)


def test_get_scan_status_not_found(client):
    """Test GET /api/scan/{job_id}/status with non-existent job."""

    response = client.get("/api/scan/nonexistent-job-id/status")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_cancel_scan_endpoint(client):
    """Test DELETE /api/scan/{job_id} endpoint."""

    # Create a mock job
    job_id = "test-job-456"
    progress_tracker.create_job(job_id)

    # Cancel/remove job
    response = client.delete(f"/api/scan/{job_id}")

    # Verify response
    assert response.status_code == 200
    data = response.json()

    assert data["job_id"] == job_id
    assert "removed" in data["message"].lower()

    # Verify job is removed
    assert progress_tracker.get_job(job_id) is None


def test_cancel_scan_not_found(client):
    """Test DELETE /api/scan/{job_id} with non-existent job."""

    response = client.delete("/api/scan/nonexistent-job-id")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_api_health_check(client):
    """Test that API is healthy and running."""

    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "healthy"
    assert data["service"] == "x-cleaner-api"


def test_api_documentation_available(client):
    """Test that API documentation is accessible."""

    # Test OpenAPI JSON
    response = client.get("/docs")
    assert response.status_code == 200

    # Test root endpoint
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()

    assert data["name"] == "X-Cleaner API"
    assert data["version"] == "1.0.0"
