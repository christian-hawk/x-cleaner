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
        Categorize accounts with intelligent partial caching.

        Checks database for existing categorizations. Uses partial cache hits:
        - Fresh cached accounts are reused
        - Only missing/stale accounts are re-categorized via API
        - Results are merged to minimize API costs

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

        # Get categories metadata (needed for return value)
        categories = self.db_manager.get_categories()
        categories_dict = {
            "categories": categories,
            "total_categories": len(categories),
        } if categories else None

        # If force refresh, skip cache entirely
        if force_refresh:
            categories_metadata, categorized = await self.grok_client.analyze_and_categorize(
                accounts
            )
            self._save_categorization_results(categories_metadata, categorized)
            return categories_metadata, categorized

        # Identify which accounts are cached and fresh vs need categorization
        fresh_cached, accounts_to_categorize = self._partition_accounts_by_cache(
            accounts
        )

        # If all accounts are cached and fresh, return cached data
        if not accounts_to_categorize:
            return categories_dict, fresh_cached

        # Need to categorize some accounts
        if not accounts_to_categorize:
            # All cached, return early
            return categories_dict, fresh_cached

        # Categorize only the accounts that need it
        if categories_dict and len(fresh_cached) > 0:
            # We have existing categories, use them for consistency
            newly_categorized = await self.grok_client.categorize_with_existing_categories(
                accounts_to_categorize, categories_dict
            )
            # Keep existing categories metadata
            final_categories = categories_dict
        else:
            # No existing categories or no cached accounts, do full discovery
            final_categories, newly_categorized = await self.grok_client.analyze_and_categorize(
                accounts_to_categorize
            )

        # Save new categorizations
        self.db_manager.save_categories(final_categories)
        self.db_manager.save_accounts(newly_categorized)

        # Merge fresh cached with newly categorized
        all_categorized = fresh_cached + newly_categorized

        # Sort by original order (preserve input order)
        account_order = {acc.user_id: idx for idx, acc in enumerate(accounts)}
        all_categorized.sort(key=lambda acc: account_order.get(acc.user_id, 999999))

        return final_categories, all_categorized

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

        # Use public method instead of private _categorize_with_discovered
        categorized = await self.grok_client.categorize_with_existing_categories(
            new_accounts, categories_dict
        )

        # Save new categorizations
        self.db_manager.save_accounts(categorized)

        return categorized

    def _partition_accounts_by_cache(
        self, accounts: List[XAccount]
    ) -> Tuple[List[CategorizedAccount], List[XAccount]]:
        """
        Partition accounts into fresh cached vs needs categorization.

        This enables partial cache hits: accounts that are already cached
        and fresh are returned immediately, while missing/stale accounts
        are identified for re-categorization.

        Args:
            accounts: Accounts to partition

        Returns:
            Tuple of (fresh_cached_accounts, accounts_to_categorize)
        """
        # Get user IDs to check
        user_ids = [acc.user_id for acc in accounts]

        # Fetch only requested accounts from database (more efficient)
        cached_lookup = self.db_manager.get_accounts_by_ids(user_ids)

        fresh_cached = []
        accounts_to_categorize = []
        cutoff_date = datetime.now() - timedelta(days=self.cache_expiry_days)

        for account in accounts:
            cached = cached_lookup.get(account.user_id)

            if cached and cached.analyzed_at >= cutoff_date:
                # Fresh cached account
                fresh_cached.append(cached)
            else:
                # Missing or stale, needs categorization
                accounts_to_categorize.append(account)

        return fresh_cached, accounts_to_categorize

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
