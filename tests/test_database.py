"""
Tests for Database Manager.

This module contains tests for the DatabaseManager class.
"""

import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from backend.database import DatabaseManager
from backend.models import CategorizedAccount


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        yield str(db_path)


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
            display_name="Artist User",
            bio="Digital artist",
            verified=False,
            followers_count=2000,
            following_count=300,
            tweet_count=500,
            category="Art",
            confidence=0.90,
            reasoning="Creative content",
            analyzed_at=datetime.now(),
        ),
    ]


def test_database_initialization(temp_db):
    """Test database initialization and schema creation."""
    db = DatabaseManager(temp_db)

    # Check that database file was created
    assert Path(temp_db).exists()

    # Check that tables exist (try to query them)
    accounts = db.get_all_accounts()
    assert isinstance(accounts, list)
    assert len(accounts) == 0


def test_save_and_retrieve_accounts(temp_db, sample_categorized_accounts):
    """Test saving and retrieving accounts."""
    db = DatabaseManager(temp_db)

    # Save accounts
    db.save_accounts(sample_categorized_accounts)

    # Retrieve all accounts
    accounts = db.get_all_accounts()
    assert len(accounts) == 2
    assert accounts[0].username == "techuser"
    assert accounts[1].username == "artistuser"


def test_get_accounts_by_category(temp_db, sample_categorized_accounts):
    """Test filtering accounts by category."""
    db = DatabaseManager(temp_db)

    # Save accounts
    db.save_accounts(sample_categorized_accounts)

    # Get accounts by category
    tech_accounts = db.get_accounts_by_category("Technology")
    assert len(tech_accounts) == 1
    assert tech_accounts[0].username == "techuser"

    art_accounts = db.get_accounts_by_category("Art")
    assert len(art_accounts) == 1
    assert art_accounts[0].username == "artistuser"


def test_save_categories(temp_db):
    """Test saving category metadata."""
    db = DatabaseManager(temp_db)

    categories_data = {
        "categories": [
            {
                "name": "Technology",
                "description": "Tech professionals",
                "characteristics": ["Technical", "Code"],
                "estimated_percentage": 40,
            },
            {
                "name": "Art",
                "description": "Artists",
                "characteristics": ["Creative", "Visual"],
                "estimated_percentage": 30,
            },
        ]
    }

    # Save categories
    db.save_categories(categories_data)

    # Retrieve categories
    categories = db.get_categories()
    assert len(categories) == 2
    assert categories[0]["name"] == "Technology"
    assert categories[1]["name"] == "Art"


def test_update_existing_account(temp_db, sample_categorized_accounts):
    """Test updating an existing account."""
    db = DatabaseManager(temp_db)

    # Save initial account
    db.save_accounts([sample_categorized_accounts[0]])

    # Update the account
    updated_account = sample_categorized_accounts[0].model_copy(
        update={"followers_count": 10000, "confidence": 0.99}
    )
    db.save_accounts([updated_account])

    # Retrieve and verify
    accounts = db.get_all_accounts()
    assert len(accounts) == 1
    assert accounts[0].followers_count == 10000
    assert accounts[0].confidence == 0.99


def test_data_directory_creation():
    """Test that data directory is created if it doesn't exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "subdir" / "test.db"
        db = DatabaseManager(str(db_path))

        # Check that parent directory was created
        assert db_path.parent.exists()
        assert db_path.exists()


def test_get_accounts_by_ids(temp_db, sample_categorized_accounts):
    """Test getting accounts by specific IDs."""
    db = DatabaseManager(temp_db)

    # Save accounts
    db.save_accounts(sample_categorized_accounts)

    # Get specific accounts by IDs
    accounts = db.get_accounts_by_ids(["1", "2"])
    assert len(accounts) == 2
    assert "1" in accounts
    assert "2" in accounts
    assert accounts["1"].username == "techuser"
    assert accounts["2"].username == "artistuser"

    # Get subset
    accounts = db.get_accounts_by_ids(["1"])
    assert len(accounts) == 1
    assert "1" in accounts

    # Get with non-existent ID
    accounts = db.get_accounts_by_ids(["1", "999"])
    assert len(accounts) == 1
    assert "1" in accounts
    assert "999" not in accounts

    # Empty list
    accounts = db.get_accounts_by_ids([])
    assert len(accounts) == 0
