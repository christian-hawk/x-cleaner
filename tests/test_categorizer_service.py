"""
Tests for Categorization Service.

This module tests the categorization service with caching functionality.
"""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.core.services.categorizer import CategorizationService
from backend.models import CategorizedAccount, XAccount


@pytest.fixture
def sample_accounts():
    """Sample X accounts for testing."""
    return [
        XAccount(
            user_id="1",
            username="techuser",
            display_name="Tech User",
            bio="Software engineer",
            verified=True,
            followers_count=5000,
            following_count=500,
            tweet_count=1000,
        ),
        XAccount(
            user_id="2",
            username="artistuser",
            display_name="Artist",
            bio="Digital artist",
            verified=False,
            followers_count=2000,
            following_count=300,
            tweet_count=500,
        ),
    ]


@pytest.fixture
def sample_categorized_accounts():
    """Sample categorized accounts for testing."""
    return [
        CategorizedAccount(
            user_id="1",
            username="techuser",
            display_name="Tech User",
            bio="Software engineer",
            verified=True,
            followers_count=5000,
            following_count=500,
            tweet_count=1000,
            category="Technology",
            confidence=0.95,
            reasoning="Clear tech focus",
            analyzed_at=datetime.now(),
        ),
        CategorizedAccount(
            user_id="2",
            username="artistuser",
            display_name="Artist",
            bio="Digital artist",
            verified=False,
            followers_count=2000,
            following_count=300,
            tweet_count=500,
            category="Art & Design",
            confidence=0.90,
            reasoning="Artist bio",
            analyzed_at=datetime.now(),
        ),
    ]


@pytest.fixture
def mock_categories():
    """Mock category metadata."""
    return {
        "categories": [
            {"name": "Technology", "description": "Tech professionals"},
            {"name": "Art & Design", "description": "Artists"},
        ],
        "total_categories": 2,
    }


@pytest.mark.asyncio
async def test_categorize_accounts_without_cache(
    sample_accounts, sample_categorized_accounts, mock_categories
):
    """Test categorization without cached data."""
    mock_grok = MagicMock()
    mock_grok.analyze_and_categorize = AsyncMock(
        return_value=(mock_categories, sample_categorized_accounts)
    )

    mock_db = MagicMock()
    mock_db.get_all_accounts.return_value = []
    mock_db.get_categories.return_value = []

    service = CategorizationService(grok_client=mock_grok, db_manager=mock_db)

    categories, categorized = await service.categorize_accounts(sample_accounts)

    # Should call Grok API since no cache
    mock_grok.analyze_and_categorize.assert_called_once()
    assert len(categorized) == 2
    assert categories == mock_categories

    # Should save to database
    mock_db.save_categories.assert_called_once()
    mock_db.save_accounts.assert_called_once()


@pytest.mark.asyncio
async def test_categorize_accounts_with_fresh_cache(
    sample_accounts, sample_categorized_accounts, mock_categories
):
    """Test using fresh cached categorizations."""
    mock_grok = MagicMock()
    mock_grok.analyze_and_categorize = AsyncMock()

    mock_db = MagicMock()
    mock_db.get_all_accounts.return_value = sample_categorized_accounts
    mock_db.get_categories.return_value = mock_categories["categories"]

    service = CategorizationService(
        grok_client=mock_grok, db_manager=mock_db, cache_expiry_days=7
    )

    categories, categorized = await service.categorize_accounts(sample_accounts)

    # Should NOT call Grok API (using cache)
    mock_grok.analyze_and_categorize.assert_not_called()
    assert len(categorized) == 2
    assert categorized[0].category == "Technology"


@pytest.mark.asyncio
async def test_categorize_accounts_with_stale_cache(
    sample_accounts, sample_categorized_accounts, mock_categories
):
    """Test re-categorization when cache is stale."""
    # Make cached accounts stale (10 days old)
    stale_accounts = [
        CategorizedAccount(
            **acc.model_dump(exclude={"analyzed_at"}),
            analyzed_at=datetime.now() - timedelta(days=10),
        )
        for acc in sample_categorized_accounts
    ]

    mock_grok = MagicMock()
    mock_grok.analyze_and_categorize = AsyncMock(
        return_value=(mock_categories, sample_categorized_accounts)
    )

    mock_db = MagicMock()
    mock_db.get_all_accounts.return_value = stale_accounts
    mock_db.get_categories.return_value = mock_categories["categories"]

    service = CategorizationService(
        grok_client=mock_grok, db_manager=mock_db, cache_expiry_days=7
    )

    categories, categorized = await service.categorize_accounts(sample_accounts)

    # Should call Grok API (cache is stale)
    mock_grok.analyze_and_categorize.assert_called_once()
    assert len(categorized) == 2


@pytest.mark.asyncio
async def test_categorize_accounts_force_refresh(
    sample_accounts, sample_categorized_accounts, mock_categories
):
    """Test force refresh bypasses cache."""
    mock_grok = MagicMock()
    mock_grok.analyze_and_categorize = AsyncMock(
        return_value=(mock_categories, sample_categorized_accounts)
    )

    mock_db = MagicMock()
    mock_db.get_all_accounts.return_value = sample_categorized_accounts
    mock_db.get_categories.return_value = mock_categories["categories"]

    service = CategorizationService(grok_client=mock_grok, db_manager=mock_db)

    categories, categorized = await service.categorize_accounts(
        sample_accounts, force_refresh=True
    )

    # Should call Grok API even with fresh cache
    mock_grok.analyze_and_categorize.assert_called_once()


@pytest.mark.asyncio
async def test_categorize_new_accounts_with_existing_categories(
    sample_accounts, sample_categorized_accounts, mock_categories
):
    """Test categorizing new accounts with existing categories."""
    mock_grok = MagicMock()
    mock_grok._categorize_with_discovered = AsyncMock(
        return_value=sample_categorized_accounts
    )

    mock_db = MagicMock()
    mock_db.get_categories.return_value = mock_categories["categories"]

    service = CategorizationService(grok_client=mock_grok, db_manager=mock_db)

    categorized = await service.categorize_new_accounts(sample_accounts)

    # Should use existing categories
    mock_grok._categorize_with_discovered.assert_called_once()
    assert len(categorized) == 2
    mock_db.save_accounts.assert_called_once()


@pytest.mark.asyncio
async def test_categorize_new_accounts_without_existing_categories(
    sample_accounts, sample_categorized_accounts, mock_categories
):
    """Test categorizing new accounts without existing categories."""
    mock_grok = MagicMock()
    mock_grok.analyze_and_categorize = AsyncMock(
        return_value=(mock_categories, sample_categorized_accounts)
    )

    mock_db = MagicMock()
    mock_db.get_categories.return_value = []

    service = CategorizationService(grok_client=mock_grok, db_manager=mock_db)

    categorized = await service.categorize_new_accounts(sample_accounts)

    # Should perform full categorization
    mock_grok.analyze_and_categorize.assert_called_once()
    assert len(categorized) == 2


@pytest.mark.asyncio
async def test_get_categorization_stats(sample_categorized_accounts):
    """Test retrieving categorization statistics."""
    mock_grok = MagicMock()
    mock_db = MagicMock()
    mock_db.get_all_accounts.return_value = sample_categorized_accounts
    mock_db.get_categories.return_value = [
        {"name": "Technology"},
        {"name": "Art & Design"},
    ]

    service = CategorizationService(
        grok_client=mock_grok, db_manager=mock_db, cache_expiry_days=7
    )

    stats = await service.get_categorization_stats()

    assert stats["total_cached"] == 2
    assert stats["fresh_cached"] == 2
    assert stats["stale_cached"] == 0
    assert stats["categories_count"] == 2
    assert stats["cache_expiry_days"] == 7


@pytest.mark.asyncio
async def test_categorize_empty_accounts():
    """Test that empty account list raises ValueError."""
    mock_grok = MagicMock()
    mock_db = MagicMock()
    service = CategorizationService(grok_client=mock_grok, db_manager=mock_db)

    with pytest.raises(ValueError, match="No accounts provided"):
        await service.categorize_accounts([])
