"""
Integration tests for complete scan workflow.

Tests the end-to-end flow from scan trigger to data persistence.
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.api.grok_client import GrokClient
from backend.api.x_client import XAPIClient
from backend.config import config
from backend.core.services.scan_service import ScanService, ScanResult
from backend.database import DatabaseManager
from backend.db.repositories.account_repository import AccountRepository
from backend.db.repositories.category_repository import CategoryRepository
from backend.models import CategorizedAccount, XAccount


@pytest.fixture
def test_database():
    """Create test database."""
    db = DatabaseManager(db_path=":memory:")
    return db


@pytest.fixture
def account_repository(test_database):
    """Create account repository with test database."""
    return AccountRepository(test_database)


@pytest.fixture
def category_repository(test_database):
    """Create category repository with test database."""
    return CategoryRepository(test_database)


@pytest.fixture
def mock_x_accounts():
    """Create mock X accounts data."""
    return [
        XAccount(
            user_id="1",
            username="techguru",
            display_name="Tech Guru",
            bio="Software engineer and tech enthusiast",
            verified=True,
            followers_count=10000,
            following_count=500,
            tweet_count=2000,
        ),
        XAccount(
            user_id="2",
            username="airesearcher",
            display_name="AI Researcher",
            bio="PhD in Machine Learning. Research at BigTech",
            verified=True,
            followers_count=25000,
            following_count=300,
            tweet_count=1500,
        ),
        XAccount(
            user_id="3",
            username="cryptotrader",
            display_name="Crypto Trader",
            bio="Bitcoin maximalist. Trading since 2013",
            verified=False,
            followers_count=5000,
            following_count=1000,
            tweet_count=5000,
        ),
    ]


@pytest.fixture
def mock_categories():
    """Create mock category metadata."""
    return {
        "categories": [
            {
                "name": "Tech Professionals",
                "description": "Software engineers and developers",
                "characteristics": ["coding", "tech", "software"],
                "estimated_percentage": 40,
            },
            {
                "name": "AI/ML Researchers",
                "description": "Artificial intelligence researchers",
                "characteristics": ["AI", "ML", "research"],
                "estimated_percentage": 30,
            },
            {
                "name": "Crypto Enthusiasts",
                "description": "Cryptocurrency traders and enthusiasts",
                "characteristics": ["crypto", "bitcoin", "trading"],
                "estimated_percentage": 30,
            },
        ],
        "total_categories": 3,
        "analysis_summary": "Tech-focused network",
    }


@pytest.fixture
def mock_categorized_accounts(mock_x_accounts):
    """Create mock categorized accounts."""
    return [
        CategorizedAccount(
            **mock_x_accounts[0].model_dump(),
            category="Tech Professionals",
            confidence=0.95,
            reasoning="Clear tech focus in bio",
        ),
        CategorizedAccount(
            **mock_x_accounts[1].model_dump(),
            category="AI/ML Researchers",
            confidence=0.98,
            reasoning="PhD and research background",
        ),
        CategorizedAccount(
            **mock_x_accounts[2].model_dump(),
            category="Crypto Enthusiasts",
            confidence=0.90,
            reasoning="Bitcoin focus and trading activity",
        ),
    ]


@pytest.mark.asyncio
async def test_scan_service_complete_workflow(
    account_repository,
    category_repository,
    mock_x_accounts,
    mock_categories,
    mock_categorized_accounts,
):
    """Test complete scan workflow with mocked API clients."""

    # Mock X API Client
    mock_x_client = AsyncMock(spec=XAPIClient)
    mock_x_client.get_all_following.return_value = mock_x_accounts

    # Mock Grok Client
    mock_grok_client = AsyncMock(spec=GrokClient)
    mock_grok_client.analyze_and_categorize.return_value = (
        mock_categories,
        mock_categorized_accounts,
    )

    # Create scan service with mocked clients
    scan_service = ScanService(
        x_client=mock_x_client,
        grok_client=mock_grok_client,
        account_repository=account_repository,
        category_repository=category_repository,
    )

    # Track progress updates
    progress_updates = []

    def progress_callback(message: str, progress: int) -> None:
        progress_updates.append({"message": message, "progress": progress})

    # Execute scan
    result = await scan_service.execute_scan(
        user_id="test_user_123",
        progress_callback=progress_callback,
    )

    # Verify result
    assert isinstance(result, ScanResult)
    assert result.success is True
    assert result.accounts_scanned == 3
    assert result.categories_discovered == 3

    # Verify progress updates were received
    assert len(progress_updates) > 0
    assert any("Fetching accounts" in update["message"] for update in progress_updates)
    assert any(update["progress"] == 100 for update in progress_updates)

    # Verify data was saved to database
    saved_accounts = account_repository.get_all_accounts()
    assert len(saved_accounts) == 3

    saved_categories = category_repository.get_all_categories()
    assert len(saved_categories) == 3

    # Verify account data
    tech_account = account_repository.get_account_by_username("techguru")
    assert tech_account is not None
    assert tech_account.category == "Tech Professionals"
    assert tech_account.confidence == 0.95

    # Verify category data
    category_names = category_repository.get_category_names()
    assert "Tech Professionals" in category_names
    assert "AI/ML Researchers" in category_names
    assert "Crypto Enthusiasts" in category_names


@pytest.mark.asyncio
async def test_scan_service_handles_x_api_error(
    account_repository,
    category_repository,
):
    """Test scan service handles X API errors gracefully."""

    # Mock X API Client that raises error
    mock_x_client = AsyncMock(spec=XAPIClient)
    mock_x_client.get_all_following.side_effect = Exception("X API connection failed")

    mock_grok_client = AsyncMock(spec=GrokClient)

    scan_service = ScanService(
        x_client=mock_x_client,
        grok_client=mock_grok_client,
        account_repository=account_repository,
        category_repository=category_repository,
    )

    # Execute scan
    result = await scan_service.execute_scan(user_id="test_user")

    # Verify error handling
    assert result.success is False
    assert result.error_message is not None
    assert "error" in result.error_message.lower()


@pytest.mark.asyncio
async def test_scan_service_handles_empty_accounts(
    account_repository,
    category_repository,
):
    """Test scan service handles no accounts found."""

    # Mock X API Client returning empty list
    mock_x_client = AsyncMock(spec=XAPIClient)
    mock_x_client.get_all_following.return_value = []

    mock_grok_client = AsyncMock(spec=GrokClient)

    scan_service = ScanService(
        x_client=mock_x_client,
        grok_client=mock_grok_client,
        account_repository=account_repository,
        category_repository=category_repository,
    )

    # Execute scan
    result = await scan_service.execute_scan(user_id="test_user")

    # Verify result
    assert result.success is False
    assert "no accounts" in result.error_message.lower()


@pytest.mark.asyncio
async def test_scan_service_progress_callback(
    account_repository,
    category_repository,
    mock_x_accounts,
    mock_categories,
    mock_categorized_accounts,
):
    """Test that progress callback is called correctly."""

    mock_x_client = AsyncMock(spec=XAPIClient)
    mock_x_client.get_all_following.return_value = mock_x_accounts

    mock_grok_client = AsyncMock(spec=GrokClient)
    mock_grok_client.analyze_and_categorize.return_value = (
        mock_categories,
        mock_categorized_accounts,
    )

    scan_service = ScanService(
        x_client=mock_x_client,
        grok_client=mock_grok_client,
        account_repository=account_repository,
        category_repository=category_repository,
    )

    progress_calls = []

    def progress_callback(message: str, progress: int) -> None:
        progress_calls.append((message, progress))

    # Execute scan
    await scan_service.execute_scan(
        user_id="test_user",
        progress_callback=progress_callback,
    )

    # Verify progress callback was called multiple times
    assert len(progress_calls) >= 4  # At least 4 progress updates

    # Verify progress is sequential
    messages = [msg for msg, _ in progress_calls]
    progress_values = [prog for _, prog in progress_calls]

    # Check that we have key milestones
    assert any("Fetching accounts" in msg for msg in messages)
    assert any("Analyzing accounts" in msg for msg in messages)
    assert any("Saving results" in msg for msg in messages)
    assert any("complete" in msg.lower() for msg in messages)

    # Verify final progress is 100
    assert progress_values[-1] == 100
