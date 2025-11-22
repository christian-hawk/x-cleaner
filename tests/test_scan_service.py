"""
Unit tests for ScanService.

Tests scan orchestration logic with mocked dependencies.
"""

import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.api.grok_client import GrokAPIError
from backend.api.x_client import XAPIError
from backend.core.services.scan_service import ScanError, ScanService, ScanStatus
from backend.models import CategorizedAccount, XAccount


@pytest.fixture
def mock_x_client():
    """Create mock X API client."""
    client = MagicMock()
    client.get_all_following = AsyncMock(return_value=[
        XAccount(
            user_id="123",
            username="test_user",
            display_name="Test User",
            bio="Test bio",
            verified=False,
            followers_count=100,
            following_count=50,
            tweet_count=200,
        )
    ])
    return client


@pytest.fixture
def mock_grok_client():
    """Create mock Grok API client."""
    client = MagicMock()
    categories_metadata = {
        "categories": [
            {
                "name": "Test Category",
                "description": "Test description",
                "characteristics": ["trait1", "trait2"],
                "estimated_percentage": 50.0,
            }
        ],
        "total_categories": 1,
        "analysis_summary": "Test summary",
    }
    categorized_accounts = [
        CategorizedAccount(
            user_id="123",
            username="test_user",
            display_name="Test User",
            bio="Test bio",
            verified=False,
            followers_count=100,
            following_count=50,
            tweet_count=200,
            category="Test Category",
            confidence=0.95,
            reasoning="Test reasoning",
        )
    ]
    client.analyze_and_categorize = AsyncMock(
        return_value=(categories_metadata, categorized_accounts)
    )
    return client


@pytest.fixture
def mock_account_repository():
    """Create mock account repository."""
    repository = MagicMock()
    repository.save_accounts = MagicMock()
    return repository


@pytest.fixture
def mock_category_repository():
    """Create mock category repository."""
    repository = MagicMock()
    repository.save_categories = MagicMock()
    return repository


@pytest.fixture
def scan_service(
    mock_x_client,
    mock_grok_client,
    mock_account_repository,
    mock_category_repository,
):
    """Create ScanService instance with mocked dependencies."""
    return ScanService(
        x_client=mock_x_client,
        grok_client=mock_grok_client,
        account_repository=mock_account_repository,
        category_repository=mock_category_repository,
    )


@pytest.mark.asyncio
async def test_scan_and_categorize_success(
    scan_service,
    mock_x_client,
    mock_grok_client,
    mock_account_repository,
    mock_category_repository,
):
    """Test successful scan and categorize workflow."""
    user_id = "123456789"
    progress_updates = []

    def progress_callback(status: ScanStatus) -> None:
        """Capture progress updates."""
        progress_updates.append(status)

    result = await scan_service.scan_and_categorize(
        user_id=user_id,
        progress_callback=progress_callback,
    )

    # Verify result
    assert result.job_id.startswith("scan_")
    assert result.accounts_fetched == 1
    assert result.accounts_categorized == 1
    assert result.accounts_saved == 1
    assert result.categories_discovered == 1
    assert result.duration_seconds > 0

    # Verify progress updates were called
    assert len(progress_updates) > 0
    assert any(update.current_step == "fetch_accounts" for update in progress_updates)
    assert any(update.current_step == "discover_categories" for update in progress_updates)
    assert any(update.current_step == "categorize_accounts" for update in progress_updates)
    assert any(update.current_step == "save_to_database" for update in progress_updates)

    # Verify dependencies were called
    mock_x_client.get_all_following.assert_called_once_with(user_id)
    mock_grok_client.analyze_and_categorize.assert_called()
    mock_account_repository.save_accounts.assert_called_once()
    mock_category_repository.save_categories.assert_called_once()


@pytest.mark.asyncio
async def test_scan_and_categorize_x_api_error(scan_service, mock_x_client):
    """Test scan failure when X API raises error."""
    mock_x_client.get_all_following = AsyncMock(
        side_effect=XAPIError("X API error", status_code=401)
    )

    with pytest.raises(ScanError) as exc_info:
        await scan_service.scan_and_categorize(
            user_id="123456789",
            progress_callback=None,
        )

    assert "X API error" in str(exc_info.value)
    assert exc_info.value.step == "fetch_accounts"


@pytest.mark.asyncio
async def test_scan_and_categorize_grok_api_error(
    scan_service,
    mock_x_client,
    mock_grok_client,
):
    """Test scan failure when Grok API raises error."""
    mock_grok_client.analyze_and_categorize = AsyncMock(
        side_effect=GrokAPIError("Grok API error")
    )

    with pytest.raises(ScanError) as exc_info:
        await scan_service.scan_and_categorize(
            user_id="123456789",
            progress_callback=None,
        )

    assert "Grok API error" in str(exc_info.value)
    assert exc_info.value.step in ("discover_categories", "categorize_accounts")


@pytest.mark.asyncio
async def test_scan_and_categorize_no_accounts(scan_service, mock_x_client):
    """Test scan failure when no accounts are found."""
    mock_x_client.get_all_following = AsyncMock(return_value=[])

    with pytest.raises(ScanError) as exc_info:
        await scan_service.scan_and_categorize(
            user_id="123456789",
            progress_callback=None,
        )

    assert "No accounts found" in str(exc_info.value)
    assert exc_info.value.step == "fetch_accounts"


@pytest.mark.asyncio
async def test_scan_progress_tracking(scan_service):
    """Test that progress is tracked correctly throughout scan."""
    progress_steps = []

    def progress_callback(status: ScanStatus) -> None:
        """Track progress steps."""
        progress_steps.append({
            "step": status.current_step,
            "progress": status.progress,
            "message": status.message,
        })

    await scan_service.scan_and_categorize(
        user_id="123456789",
        progress_callback=progress_callback,
    )

    # Verify progress increases
    assert len(progress_steps) > 0
    assert progress_steps[0]["progress"] >= 0.0
    assert progress_steps[-1]["progress"] == 100.0

    # Verify all steps were executed
    step_names = [step["step"] for step in progress_steps]
    assert "fetch_accounts" in step_names
    assert "discover_categories" in step_names
    assert "categorize_accounts" in step_names
    assert "save_to_database" in step_names


@pytest.mark.asyncio
async def test_scan_progress_callback_error_handling(scan_service):
    """Test that scan continues even if progress callback fails."""
    def failing_callback(status: ScanStatus) -> None:
        """Callback that raises exception."""
        raise Exception("Callback error")

    # Scan should complete despite callback error
    result = await scan_service.scan_and_categorize(
        user_id="123456789",
        progress_callback=failing_callback,
    )

    assert result.accounts_fetched == 1
    assert result.accounts_categorized == 1
