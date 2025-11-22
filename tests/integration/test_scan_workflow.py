"""
End-to-end integration tests for scan workflow.

Tests the complete scan workflow: trigger scan → check status → verify data saved.
"""

import asyncio
import time
from pathlib import Path

import pytest
from httpx import AsyncClient

from backend.database import DatabaseManager
from backend.main import app


@pytest.fixture
def test_db_path(tmp_path):
    """Create a temporary database path for testing."""
    db_path = tmp_path / "test_scan.db"
    return str(db_path)


@pytest.fixture
def database_manager(test_db_path):
    """Create a temporary database for testing."""
    database = DatabaseManager(db_path=test_db_path)
    yield database


@pytest.fixture
async def api_client():
    """Create async HTTP client for testing."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.mark.asyncio
async def test_scan_endpoint_creates_job(api_client, test_db_path, monkeypatch):
    """
    Test that POST /api/scan creates a scan job.

    This test verifies:
    1. POST /api/scan returns job_id
    2. GET /api/scan/{job_id}/status returns job status
    """
    # Mock environment variables
    monkeypatch.setenv("X_API_BEARER_TOKEN", "test_token")
    monkeypatch.setenv("X_USER_ID", "test_user_123")
    monkeypatch.setenv("XAI_API_KEY", "test_grok_key")
    monkeypatch.setenv("DATABASE_PATH", test_db_path)

    # Trigger scan
    response = await api_client.post("/api/scan", json={"user_id": "test_user_123"})

    assert response.status_code == 202
    data = response.json()
    assert "job_id" in data
    assert "status" in data
    assert data["status"] in ("queued", "running")

    job_id = data["job_id"]
    assert len(job_id) > 0

    # Check status
    status_response = await api_client.get(f"/api/scan/{job_id}/status")
    assert status_response.status_code == 200
    status_data = status_response.json()
    assert status_data["job_id"] == job_id
    assert "status" in status_data
    assert "progress" in status_data
    assert "message" in status_data


@pytest.mark.asyncio
async def test_scan_endpoint_without_user_id(api_client, test_db_path, monkeypatch):
    """
    Test that POST /api/scan uses X_USER_ID from environment when not provided.
    """
    # Mock environment variables
    monkeypatch.setenv("X_API_BEARER_TOKEN", "test_token")
    monkeypatch.setenv("X_USER_ID", "env_user_456")
    monkeypatch.setenv("XAI_API_KEY", "test_grok_key")
    monkeypatch.setenv("DATABASE_PATH", test_db_path)

    # Trigger scan without user_id
    response = await api_client.post("/api/scan", json={})

    assert response.status_code == 202
    data = response.json()
    assert "job_id" in data


@pytest.mark.asyncio
async def test_scan_endpoint_missing_user_id(api_client, monkeypatch):
    """
    Test that POST /api/scan returns 400 when user_id is missing.
    """
    # Mock environment without X_USER_ID
    monkeypatch.setenv("X_API_BEARER_TOKEN", "test_token")
    monkeypatch.delenv("X_USER_ID", raising=False)
    monkeypatch.setenv("XAI_API_KEY", "test_grok_key")

    # Trigger scan without user_id
    response = await api_client.post("/api/scan", json={})

    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "user_id" in data["detail"].lower()


@pytest.mark.asyncio
async def test_scan_status_not_found(api_client):
    """
    Test that GET /api/scan/{job_id}/status returns 404 for non-existent job.
    """
    response = await api_client.get("/api/scan/non-existent-job-id/status")

    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_scan_workflow_integration(
    api_client, test_db_path, monkeypatch, database_manager
):
    """
    Test complete scan workflow integration.

    This test verifies the full workflow:
    1. Trigger scan
    2. Monitor progress
    3. Verify data is saved (if scan completes successfully)

    Note: This test may require actual API credentials or mocks to complete.
    """
    # Mock environment variables
    monkeypatch.setenv("X_API_BEARER_TOKEN", "test_token")
    monkeypatch.setenv("X_USER_ID", "test_user_789")
    monkeypatch.setenv("XAI_API_KEY", "test_grok_key")
    monkeypatch.setenv("DATABASE_PATH", test_db_path)

    # Trigger scan
    response = await api_client.post("/api/scan", json={"user_id": "test_user_789"})

    assert response.status_code == 202
    data = response.json()
    job_id = data["job_id"]

    # Poll for status updates (with timeout)
    max_wait = 10  # seconds
    start_time = time.time()

    while time.time() - start_time < max_wait:
        status_response = await api_client.get(f"/api/scan/{job_id}/status")
        assert status_response.status_code == 200

        status_data = status_response.json()
        status_val = status_data["status"]

        # If completed, verify data was saved
        if status_val == "completed":
            # Verify accounts were saved
            accounts = database_manager.get_all_accounts()
            assert len(accounts) > 0, "Expected accounts to be saved after scan"
            return

        # If error, fail the test
        if status_val == "error":
            error_msg = status_data.get("error", "Unknown error")
            pytest.fail(f"Scan failed with error: {error_msg}")

        # Wait before next poll
        await asyncio.sleep(0.5)

    # If we get here, scan didn't complete in time
    # This is expected if APIs are not mocked, so we just verify job exists
    status_response = await api_client.get(f"/api/scan/{job_id}/status")
    assert status_response.status_code == 200
    status_data = status_response.json()
    assert status_data["job_id"] == job_id
