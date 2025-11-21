"""
Categorization service for X-Cleaner.

This module orchestrates the AI-powered categorization process with
intelligent caching to minimize API calls and costs.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from ...api.grok_client import GrokAPIError, GrokClient
from ...database import DatabaseManager
from ...models import CategorizedAccount, XAccount


class CategorizationService:
    """
    Service for managing account categorization with caching.

    Orchestrates the categorization process, intelligently using cached
    results when available to minimize API costs.
    """

    def __init__(
        self,
        grok_client: Optional[GrokClient] = None,
        db_manager: Optional[DatabaseManager] = None,
        cache_expiry_days: int = 7,
    ):
        """
        Initialize categorization service.

        Args:
            grok_client: Grok API client (creates new if not provided)
            db_manager: Database manager (creates new if not provided)
            cache_expiry_days: Number of days before cached categorizations
                              are considered stale
        """
        self.grok_client = grok_client or GrokClient()
        self.db_manager = db_manager or DatabaseManager()
        self.cache_expiry_days = cache_expiry_days

    async def categorize_accounts(
        self, accounts: List[XAccount], force_refresh: bool = False
    ) -> Tuple[Dict, List[CategorizedAccount]]:
        """
        Categorize accounts with intelligent caching.

        Checks database for existing categorizations. Only re-categorizes
        if forced, data is stale, or accounts are new.

        Args:
            accounts: List of accounts to categorize
            force_refresh: If True, ignore cache and re-categorize all

        Returns:
            Tuple of (category_metadata, categorized_accounts)

        Raises:
            GrokAPIError: If categorization fails
            ValueError: If no accounts provided
        """
        if not accounts:
            raise ValueError("No accounts provided for categorization")

        # Check cache unless force refresh
        if not force_refresh:
            cached_result = self._get_cached_categorizations(accounts)
            if cached_result:
                categories_metadata, cached_accounts = cached_result

                # If all accounts are cached and fresh, return cached data
                if len(cached_accounts) == len(accounts):
                    return categories_metadata, cached_accounts

        # Perform fresh categorization
        categories_metadata, categorized = await self.grok_client.analyze_and_categorize(
            accounts
        )

        # Save to database for future caching
        self._save_categorization_results(categories_metadata, categorized)

        return categories_metadata, categorized

    async def categorize_new_accounts(
        self, new_accounts: List[XAccount]
    ) -> List[CategorizedAccount]:
        """
        Categorize only new accounts using existing categories.

        Uses discovered categories from database if available, otherwise
        performs full discovery.

        Args:
            new_accounts: List of new accounts to categorize

        Returns:
            List of newly categorized accounts

        Raises:
            GrokAPIError: If categorization fails
        """
        # Get existing categories from database
        existing_categories = self.db_manager.get_categories()

        if not existing_categories:
            # No existing categories, perform full categorization
            categories_metadata, categorized = await self.grok_client.analyze_and_categorize(
                new_accounts
            )
            self._save_categorization_results(categories_metadata, categorized)
            return categorized

        # Use existing categories for new accounts
        categories_dict = {
            "categories": existing_categories,
            "total_categories": len(existing_categories),
        }

        categorized = await self.grok_client._categorize_with_discovered(
            new_accounts, categories_dict
        )

        # Save new categorizations
        self.db_manager.save_accounts(categorized)

        return categorized

    def _get_cached_categorizations(
        self, accounts: List[XAccount]
    ) -> Optional[Tuple[Dict, List[CategorizedAccount]]]:
        """
        Retrieve cached categorizations if available and fresh.

        Args:
            accounts: Accounts to check for cached data

        Returns:
            Tuple of (categories, categorized_accounts) if cache is valid,
            None otherwise
        """
        # Get all cached accounts
        cached_accounts = self.db_manager.get_all_accounts()

        if not cached_accounts:
            return None

        # Create lookup by user_id
        cached_lookup = {acc.user_id: acc for acc in cached_accounts}

        # Check if all accounts are cached and fresh
        categorized_accounts = []
        cutoff_date = datetime.now() - timedelta(days=self.cache_expiry_days)

        for account in accounts:
            cached = cached_lookup.get(account.user_id)
            if not cached or cached.analyzed_at < cutoff_date:
                # Cache miss or stale data
                return None
            categorized_accounts.append(cached)

        # Get categories metadata
        categories = self.db_manager.get_categories()
        if not categories:
            return None

        categories_dict = {
            "categories": categories,
            "total_categories": len(categories),
        }

        return categories_dict, categorized_accounts

    def _save_categorization_results(
        self, categories_metadata: Dict, categorized_accounts: List[CategorizedAccount]
    ) -> None:
        """
        Save categorization results to database.

        Args:
            categories_metadata: Categories discovered by Grok
            categorized_accounts: Categorized accounts
        """
        # Save categories metadata
        self.db_manager.save_categories(categories_metadata)

        # Save categorized accounts
        self.db_manager.save_accounts(categorized_accounts)

    async def get_categorization_stats(self) -> Dict:
        """
        Get statistics about cached categorizations.

        Returns:
            Dictionary with cache statistics
        """
        all_accounts = self.db_manager.get_all_accounts()
        categories = self.db_manager.get_categories()

        cutoff_date = datetime.now() - timedelta(days=self.cache_expiry_days)
        fresh_accounts = [acc for acc in all_accounts if acc.analyzed_at >= cutoff_date]

        return {
            "total_cached": len(all_accounts),
            "fresh_cached": len(fresh_accounts),
            "stale_cached": len(all_accounts) - len(fresh_accounts),
            "categories_count": len(categories),
            "cache_expiry_days": self.cache_expiry_days,
            "oldest_analysis": min(
                (acc.analyzed_at for acc in all_accounts), default=None
            ),
            "newest_analysis": max(
                (acc.analyzed_at for acc in all_accounts), default=None
            ),
        }
