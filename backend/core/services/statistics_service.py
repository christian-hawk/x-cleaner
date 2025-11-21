"""
Statistics service for analytics and calculations.

Provides business logic for statistical analysis and metrics calculation
based on account data.
"""

from typing import Any, Dict, List

from backend.db.repositories.account_repository import AccountRepository
from backend.db.repositories.category_repository import CategoryRepository
from backend.models import CategorizedAccount


class StatisticsService:
    """Service for statistical analysis and metrics."""

    def __init__(
        self,
        account_repository: AccountRepository,
        category_repository: CategoryRepository
    ):
        """
        Initialize statistics service.

        Args:
            account_repository: Repository for account data access.
            category_repository: Repository for category data access.
        """
        self._account_repository = account_repository
        self._category_repository = category_repository

    def calculate_overall_statistics(self) -> Dict[str, Any]:
        """
        Calculate overall statistics for all accounts.

        Returns:
            Dictionary containing overall statistics.
        """
        all_accounts = self._account_repository.get_all_accounts()

        if not all_accounts:
            return self._empty_overall_statistics()

        total_accounts = len(all_accounts)
        verified_accounts = [
            account for account in all_accounts
            if account.verified
        ]
        verified_count = len(verified_accounts)

        total_followers = sum(
            account.followers_count for account in all_accounts
        )
        total_following = sum(
            account.following_count for account in all_accounts
        )
        total_tweets = sum(
            account.tweet_count for account in all_accounts
        )

        # Find most popular category
        category_counts: Dict[str, int] = {}
        for account in all_accounts:
            category_counts[account.category] = category_counts.get(
                account.category, 0
            ) + 1

        most_popular_category = max(
            category_counts.items(),
            key=lambda item: item[1]
        )[0] if category_counts else None

        return {
            "total_accounts": total_accounts,
            "total_categories": self._category_repository.get_category_count(),
            "verified_count": verified_count,
            "verification_rate": (verified_count / total_accounts) * 100,
            "avg_followers": total_followers / total_accounts,
            "avg_following": total_following / total_accounts,
            "avg_tweets": total_tweets / total_accounts,
            "total_followers": total_followers,
            "total_following": total_following,
            "total_tweets": total_tweets,
            "most_popular_category": most_popular_category,
        }

    def calculate_category_statistics(self) -> List[Dict[str, Any]]:
        """
        Calculate statistics for each category.

        Returns:
            List of dictionaries containing per-category statistics.
        """
        all_accounts = self._account_repository.get_all_accounts()
        category_names = self._category_repository.get_category_names()

        if not all_accounts or not category_names:
            return []

        total_accounts = len(all_accounts)
        category_statistics: List[Dict[str, Any]] = []

        for category_name in category_names:
            category_accounts = [
                account for account in all_accounts
                if account.category == category_name
            ]

            if not category_accounts:
                continue

            account_count = len(category_accounts)
            verified_count = sum(
                1 for account in category_accounts
                if account.verified
            )
            avg_followers = sum(
                account.followers_count for account in category_accounts
            ) / account_count

            category_statistics.append({
                "category": category_name,
                "account_count": account_count,
                "percentage": (account_count / total_accounts) * 100,
                "avg_followers": avg_followers,
                "verification_rate": (verified_count / account_count) * 100,
            })

        # Sort by account count descending
        category_statistics.sort(
            key=lambda stat: stat["account_count"],
            reverse=True
        )

        return category_statistics

    def calculate_engagement_metrics(self) -> Dict[str, Any]:
        """
        Calculate engagement-related metrics.

        Returns:
            Dictionary containing engagement metrics.
        """
        all_accounts = self._account_repository.get_all_accounts()

        if not all_accounts:
            return {
                "avg_follower_following_ratio": 0.0,
                "avg_tweets_per_follower": 0.0,
                "median_followers": 0,
                "median_following": 0,
            }

        # Calculate follower/following ratios
        ratios = [
            account.followers_count / max(account.following_count, 1)
            for account in all_accounts
        ]
        avg_ratio = sum(ratios) / len(ratios)

        # Calculate tweets per follower (per 1000 followers for readability)
        tweets_per_follower = [
            (account.tweet_count / max(account.followers_count, 1)) * 1000
            for account in all_accounts
        ]
        avg_tweets_per_follower = sum(tweets_per_follower) / len(tweets_per_follower)

        # Calculate medians
        sorted_by_followers = sorted(
            all_accounts,
            key=lambda account: account.followers_count
        )
        sorted_by_following = sorted(
            all_accounts,
            key=lambda account: account.following_count
        )

        median_index = len(all_accounts) // 2
        median_followers = sorted_by_followers[median_index].followers_count
        median_following = sorted_by_following[median_index].following_count

        return {
            "avg_follower_following_ratio": avg_ratio,
            "avg_tweets_per_follower": avg_tweets_per_follower,
            "median_followers": median_followers,
            "median_following": median_following,
        }

    def _empty_overall_statistics(self) -> Dict[str, Any]:
        """
        Return empty statistics structure when no data available.

        Returns:
            Dictionary with zeroed statistics.
        """
        return {
            "total_accounts": 0,
            "total_categories": 0,
            "verified_count": 0,
            "verification_rate": 0.0,
            "avg_followers": 0,
            "avg_following": 0,
            "avg_tweets": 0,
            "total_followers": 0,
            "total_following": 0,
            "total_tweets": 0,
            "most_popular_category": None,
        }
