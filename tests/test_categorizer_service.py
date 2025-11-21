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
    mock_db.get_accounts_by_ids.return_value = {}  # Empty cache
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
    # Return cached accounts by ID
    mock_db.get_accounts_by_ids.return_value = {
        "1": sample_categorized_accounts[0],
        "2": sample_categorized_accounts[1],
    }
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
    # Return stale accounts by ID
    mock_db.get_accounts_by_ids.return_value = {
        "1": stale_accounts[0],
        "2": stale_accounts[1],
    }
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
    # Use public method now
    mock_grok.categorize_with_existing_categories = AsyncMock(
        return_value=sample_categorized_accounts
    )

    mock_db = MagicMock()
    mock_db.get_categories.return_value = mock_categories["categories"]

    service = CategorizationService(grok_client=mock_grok, db_manager=mock_db)

    categorized = await service.categorize_new_accounts(sample_accounts)

    # Should use existing categories (public method)
    mock_grok.categorize_with_existing_categories.assert_called_once()
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


@pytest.mark.asyncio
async def test_categorize_accounts_partial_cache_hit(
    sample_accounts, sample_categorized_accounts, mock_categories
):
    """Test partial cache hits - some accounts cached, some need categorization."""
    # Only first account is cached
    cached_account = sample_categorized_accounts[0]
    new_account = sample_accounts[1]

    # Create new categorized account for the second one
    new_categorized = CategorizedAccount(
        **new_account.model_dump(),
        category="Art & Design",
        confidence=0.90,
        reasoning="Artist bio",
        analyzed_at=datetime.now(),
    )

    mock_grok = MagicMock()
    mock_grok.categorize_with_existing_categories = AsyncMock(
        return_value=[new_categorized]
    )

    mock_db = MagicMock()
    # Return only first account from cache
    mock_db.get_accounts_by_ids.return_value = {"1": cached_account}
    mock_db.get_categories.return_value = mock_categories["categories"]

    service = CategorizationService(
        grok_client=mock_grok, db_manager=mock_db, cache_expiry_days=7
    )

    categories, categorized = await service.categorize_accounts(sample_accounts)

    # Should use existing categories method (not full discovery)
    mock_grok.categorize_with_existing_categories.assert_called_once()

    # Should only categorize the new account
    call_args = mock_grok.categorize_with_existing_categories.call_args
    accounts_sent = call_args[0][0]
    assert len(accounts_sent) == 1
    assert accounts_sent[0].user_id == "2"

    # Should return both accounts (cached + newly categorized)
    assert len(categorized) == 2

    # Should save only new categorizations
    mock_db.save_accounts.assert_called_once()


@pytest.mark.asyncio
async def test_partition_accounts_by_cache_efficiency(
    sample_accounts, sample_categorized_accounts
):
    """Test that partition method efficiently uses get_accounts_by_ids."""
    mock_grok = MagicMock()
    mock_db = MagicMock()

    # Setup: first account cached and fresh, second is stale
    fresh_account = sample_categorized_accounts[0]
    stale_account = CategorizedAccount(
        **sample_categorized_accounts[1].model_dump(exclude={"analyzed_at"}),
        analyzed_at=datetime.now() - timedelta(days=10),
    )

    mock_db.get_accounts_by_ids.return_value = {
        "1": fresh_account,
        "2": stale_account,
    }

    service = CategorizationService(
        grok_client=mock_grok, db_manager=mock_db, cache_expiry_days=7
    )

    fresh, to_categorize = service._partition_accounts_by_cache(sample_accounts)

    # Should have called get_accounts_by_ids with correct IDs
    mock_db.get_accounts_by_ids.assert_called_once_with(["1", "2"])

    # Fresh account should be in fresh list
    assert len(fresh) == 1
    assert fresh[0].user_id == "1"

    # Stale account should be in to_categorize list
    assert len(to_categorize) == 1
    assert to_categorize[0].user_id == "2"
