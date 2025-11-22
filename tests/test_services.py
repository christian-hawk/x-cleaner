"""Tests for service layer."""

import pytest
from backend.core.services.account_service import AccountService
from backend.core.services.statistics_service import StatisticsService
from backend.db.repositories.account_repository import AccountRepository
from backend.database import DatabaseManager
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
    from backend.db.repositories.category_repository import CategoryRepository
    return CategoryRepository(database_manager=database_manager)


@pytest.fixture
def account_service(account_repository):
    """Create account service."""
    return AccountService(account_repository=account_repository)


@pytest.fixture
def statistics_service(account_repository, category_repository):
    """Create statistics service."""
    return StatisticsService(
        account_repository=account_repository,
        category_repository=category_repository
    )


@pytest.fixture
def sample_accounts(database_manager):
    """Create and save sample accounts."""
    accounts = [
        CategorizedAccount(
            user_id="1",
            username="techuser1",
            display_name="Tech User 1",
            bio="Software developer",
            followers_count=5000,
            following_count=500,
            tweet_count=1000,
            verified=True,
            category="Tech Professional",
            confidence=0.95,
            reasoning="Active in tech community",
        ),
        CategorizedAccount(
            user_id="2",
            username="techuser2",
            display_name="Tech User 2",
            bio="Data scientist",
            followers_count=3000,
            following_count=300,
            tweet_count=800,
            verified=False,
            category="Tech Professional",
            confidence=0.90,
            reasoning="Data science expert",
        ),
        CategorizedAccount(
            user_id="3",
            username="businessuser1",
            display_name="Business User 1",
            bio="CEO and entrepreneur",
            followers_count=10000,
            following_count=1000,
            tweet_count=2000,
            verified=True,
            category="Business Leader",
            confidence=0.92,
            reasoning="Business executive",
        ),
        CategorizedAccount(
            user_id="4",
            username="contentcreator1",
            display_name="Content Creator 1",
            bio="YouTuber and blogger",
            followers_count=500,
            following_count=200,
            tweet_count=300,
            verified=False,
            category="Content Creator",
            confidence=0.88,
            reasoning="Creates content",
        ),
    ]
    database_manager.save_accounts(accounts)
    return accounts


class TestAccountService:
    """Test AccountService class."""

    def test_get_all_accounts(self, account_service, sample_accounts):
        """Test getting all accounts."""
        accounts = account_service.get_all_accounts()
        assert len(accounts) == 4

    def test_filter_by_category(self, account_service, sample_accounts):
        """Test filtering accounts by category."""
        tech_accounts = account_service.filter_accounts(category="Tech Professional")
        assert len(tech_accounts) == 2
        assert all(acc.category == "Tech Professional" for acc in tech_accounts)

    def test_filter_verified_only(self, account_service, sample_accounts):
        """Test filtering verified accounts only."""
        verified_accounts = account_service.filter_accounts(verified_only=True)
        assert len(verified_accounts) == 2
        assert all(acc.verified for acc in verified_accounts)

    def test_filter_by_minimum_followers(self, account_service, sample_accounts):
        """Test filtering by minimum followers."""
        popular_accounts = account_service.filter_accounts(minimum_followers=4000)
        assert len(popular_accounts) == 2
        assert all(acc.followers_count >= 4000 for acc in popular_accounts)

    def test_filter_combined_criteria(self, account_service, sample_accounts):
        """Test filtering with multiple criteria."""
        filtered = account_service.filter_accounts(
            category="Tech Professional", verified_only=True, minimum_followers=4000
        )
        assert len(filtered) == 1
        assert filtered[0].username == "techuser1"

    def test_filter_no_matches(self, account_service, sample_accounts):
        """Test filtering with no matches."""
        filtered = account_service.filter_accounts(
            category="Non-existent Category"
        )
        assert len(filtered) == 0

    def test_get_accounts_by_category(self, account_service, sample_accounts):
        """Test getting accounts by category."""
        tech_accounts = account_service.get_accounts_by_category("Tech Professional")
        assert len(tech_accounts) == 2
        assert all(acc.category == "Tech Professional" for acc in tech_accounts)

    def test_get_account_by_username(self, account_service, sample_accounts):
        """Test getting account by username."""
        account = account_service.get_account_by_username("techuser1")
        assert account is not None
        assert account.username == "techuser1"
        assert account.display_name == "Tech User 1"

        # Test non-existent user
        non_existent = account_service.get_account_by_username("nonexistent")
        assert non_existent is None

    def test_get_verified_accounts(self, account_service, sample_accounts):
        """Test getting only verified accounts."""
        verified = account_service.get_verified_accounts()
        assert len(verified) == 2
        assert all(acc.verified for acc in verified)


class TestStatisticsService:
    """Test StatisticsService class."""

    def test_calculate_overall_statistics(self, statistics_service, sample_accounts):
        """Test calculating overall statistics."""
        stats = statistics_service.calculate_overall_statistics()

        assert stats["total_accounts"] == 4
        assert stats["verified_count"] == 2
        assert "total_categories" in stats
        assert "most_popular_category" in stats
        assert stats["total_followers"] == 18500
        assert stats["avg_followers"] == pytest.approx(4625.0, rel=0.01)

    def test_calculate_overall_statistics_empty(self, statistics_service):
        """Test statistics with no accounts."""
        stats = statistics_service.calculate_overall_statistics()

        assert stats["total_accounts"] == 0
        assert stats["verified_count"] == 0
        assert stats["total_followers"] == 0

    def test_calculate_category_statistics(
        self, statistics_service, category_repository, sample_accounts
    ):
        """Test calculating per-category statistics."""
        # First save category metadata
        categories_data = {
            "categories": [
                {"name": "Tech Professional", "description": "Tech people"},
                {"name": "Business Leader", "description": "Business people"},
                {"name": "Content Creator", "description": "Content creators"},
            ],
            "total_categories": 3,
        }
        category_repository.save_categories(categories_data)

        stats = statistics_service.calculate_category_statistics()

        assert len(stats) >= 1

        # Should have stats for each category
        categories = [s["category"] for s in stats]
        assert "Tech Professional" in categories

    def test_calculate_category_statistics_empty(self, statistics_service):
        """Test category statistics with no accounts."""
        stats = statistics_service.calculate_category_statistics()
        assert stats == []

    def test_calculate_engagement_metrics(self, statistics_service, sample_accounts):
        """Test calculating engagement metrics."""
        metrics = statistics_service.calculate_engagement_metrics()

        assert "avg_follower_following_ratio" in metrics
        assert "avg_tweets_per_follower" in metrics
        assert "median_followers" in metrics
        assert "median_following" in metrics
        assert metrics["avg_follower_following_ratio"] > 0
        assert metrics["median_followers"] > 0
