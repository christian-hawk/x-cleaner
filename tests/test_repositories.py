"""Tests for repository layer."""

import pytest
from backend.database import DatabaseManager
from backend.db.repositories.account_repository import AccountRepository
from backend.db.repositories.category_repository import CategoryRepository
from backend.models import CategorizedAccount


@pytest.fixture
def database_manager(tmp_path):
    """Create a temporary database for testing."""
    db_path = tmp_path / "test.db"
    database = DatabaseManager(str(db_path))
    yield database


@pytest.fixture
def account_repository(database_manager):
    """Create account repository with test database."""
    return AccountRepository(database_manager=database_manager)


@pytest.fixture
def category_repository(database_manager):
    """Create category repository with test database."""
    return CategoryRepository(database_manager=database_manager)


@pytest.fixture
def sample_account():
    """Create a sample categorized account."""
    return CategorizedAccount(
        user_id="123456789",
        username="testuser",
        display_name="Test User",
        bio="Test bio",
        followers_count=1000,
        following_count=500,
        tweet_count=250,
        verified=True,
        category="Tech Professional",
        confidence=0.95,
        reasoning="Active in tech community",
    )


class TestAccountRepository:
    """Test AccountRepository class."""

    def test_get_all_accounts_empty(self, account_repository):
        """Test getting all accounts when database is empty."""
        accounts = account_repository.get_all_accounts()
        assert accounts == []

    def test_get_all_accounts_with_data(self, account_repository, sample_account):
        """Test getting all accounts with data."""
        # Save account first
        account_repository._database.save_accounts([sample_account])

        # Retrieve accounts
        accounts = account_repository.get_all_accounts()
        assert len(accounts) == 1
        assert accounts[0].username == "testuser"
        assert accounts[0].category == "Tech Professional"

    def test_get_accounts_by_category(self, account_repository, sample_account):
        """Test filtering accounts by category."""
        # Save account
        account_repository._database.save_accounts([sample_account])

        # Get by category
        tech_accounts = account_repository.get_accounts_by_category("Tech Professional")
        assert len(tech_accounts) == 1
        assert tech_accounts[0].username == "testuser"

        # Get by non-existent category
        other_accounts = account_repository.get_accounts_by_category("Non-existent")
        assert len(other_accounts) == 0

    def test_save_accounts(self, account_repository, sample_account):
        """Test saving accounts."""
        # Save account
        account_repository.save_accounts([sample_account])

        # Verify saved
        accounts = account_repository.get_all_accounts()
        assert len(accounts) == 1
        assert accounts[0].user_id == "123456789"

    def test_get_verified_accounts(self, account_repository, database_manager):
        """Test getting verified accounts only."""
        # Save accounts with different verified status
        accounts = [
            CategorizedAccount(
                user_id="1",
                username="user1",
                display_name="User 1",
                category="Tech",
                confidence=0.9,
                followers_count=100,
                following_count=50,
                tweet_count=10,
                verified=True,
            ),
            CategorizedAccount(
                user_id="2",
                username="user2",
                display_name="User 2",
                category="Business",
                confidence=0.8,
                followers_count=200,
                following_count=60,
                tweet_count=20,
                verified=False,
            ),
            CategorizedAccount(
                user_id="3",
                username="user3",
                display_name="User 3",
                category="Tech",
                confidence=0.85,
                followers_count=150,
                following_count=70,
                tweet_count=15,
                verified=True,
            ),
        ]
        database_manager.save_accounts(accounts)

        # Get verified accounts
        verified = account_repository.get_verified_accounts()
        assert len(verified) == 2
        assert all(acc.verified for acc in verified)

    def test_get_account_by_username(self, account_repository, sample_account):
        """Test getting account by username."""
        # Save account
        account_repository.save_accounts([sample_account])

        # Get by username
        found = account_repository.get_account_by_username("testuser")
        assert found is not None
        assert found.username == "testuser"

        # Test non-existent
        not_found = account_repository.get_account_by_username("nonexistent")
        assert not_found is None

    def test_get_account_by_user_id(self, account_repository, sample_account):
        """Test getting account by user ID."""
        # Save account
        account_repository.save_accounts([sample_account])

        # Get by user ID
        found = account_repository.get_account_by_user_id("123456789")
        assert found is not None
        assert found.user_id == "123456789"

        # Test non-existent
        not_found = account_repository.get_account_by_user_id("999999999")
        assert not_found is None

    def test_count_total_accounts(self, account_repository, database_manager):
        """Test counting total accounts."""
        # Initially empty
        assert account_repository.count_total_accounts() == 0

        # Add accounts
        accounts = [
            CategorizedAccount(
                user_id=str(i),
                username=f"user{i}",
                display_name=f"User {i}",
                category="Tech",
                confidence=0.9,
                followers_count=100,
                following_count=50,
                tweet_count=10,
                verified=False,
            )
            for i in range(5)
        ]
        database_manager.save_accounts(accounts)

        assert account_repository.count_total_accounts() == 5

    def test_get_accounts_with_minimum_followers(
        self, account_repository, database_manager
    ):
        """Test getting accounts with minimum followers."""
        accounts = [
            CategorizedAccount(
                user_id="1",
                username="user1",
                display_name="User 1",
                category="Tech",
                confidence=0.9,
                followers_count=1000,
                following_count=100,
                tweet_count=10,
                verified=False,
            ),
            CategorizedAccount(
                user_id="2",
                username="user2",
                display_name="User 2",
                category="Tech",
                confidence=0.9,
                followers_count=5000,
                following_count=200,
                tweet_count=20,
                verified=False,
            ),
            CategorizedAccount(
                user_id="3",
                username="user3",
                display_name="User 3",
                category="Tech",
                confidence=0.9,
                followers_count=500,
                following_count=50,
                tweet_count=5,
                verified=False,
            ),
        ]
        database_manager.save_accounts(accounts)

        # Get accounts with at least 1000 followers
        result = account_repository.get_accounts_with_minimum_followers(1000)
        assert len(result) == 2
        assert all(acc.followers_count >= 1000 for acc in result)


class TestCategoryRepository:
    """Test CategoryRepository class."""

    def test_get_all_categories_empty(self, category_repository):
        """Test getting categories when none exist."""
        categories = category_repository.get_all_categories()
        assert categories == []

    def test_get_all_categories_with_data(self, category_repository):
        """Test getting categories with metadata."""
        # Save categories
        categories_data = {
            "categories": [
                {
                    "name": "Tech Professional",
                    "description": "Technology professionals",
                    "characteristics": ["coding", "tech"],
                    "estimated_percentage": 30,
                },
                {
                    "name": "Business Leader",
                    "description": "Business executives",
                    "characteristics": ["leadership", "strategy"],
                    "estimated_percentage": 20,
                },
            ],
            "total_categories": 2,
        }
        category_repository._database.save_categories(categories_data)

        # Retrieve categories
        categories = category_repository.get_all_categories()
        assert len(categories) == 2
        assert categories[0]["name"] == "Tech Professional"
        assert categories[1]["name"] == "Business Leader"

    def test_get_category_names_empty(self, category_repository):
        """Test getting category names when none exist."""
        names = category_repository.get_category_names()
        assert names == []

    def test_get_category_names_with_data(self, category_repository):
        """Test getting category names."""
        # Save categories
        categories_data = {
            "categories": [
                {"name": "Tech", "description": "Tech people"},
                {"name": "Business", "description": "Business people"},
            ],
            "total_categories": 2,
        }
        category_repository._database.save_categories(categories_data)

        # Get names
        names = category_repository.get_category_names()
        assert "Tech" in names
        assert "Business" in names
        assert len(names) == 2

    def test_save_categories(self, category_repository):
        """Test saving categories metadata."""
        categories_data = {
            "categories": [
                {"name": "Category A", "description": "Description A"},
            ],
            "total_categories": 1,
        }

        # Save categories
        category_repository.save_categories(categories_data)

        # Verify saved
        categories = category_repository.get_all_categories()
        assert len(categories) == 1
        assert categories[0]["name"] == "Category A"
