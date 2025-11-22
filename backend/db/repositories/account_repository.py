"""
Account repository for data access operations.

Provides abstraction layer for account-related database operations
following the Repository Pattern.
"""

from typing import List, Optional

from backend.database import DatabaseManager
from backend.models import CategorizedAccount


class AccountRepository:
    """Repository for account data access operations."""

    def __init__(self, database_manager: DatabaseManager):
        """
        Initialize account repository.

        Args:
            database_manager: Database manager instance for data access.
        """
        self._database = database_manager

    def get_all_accounts(self) -> List[CategorizedAccount]:
        """
        Retrieve all categorized accounts from database.

        Returns:
            List of all categorized accounts.
        """
        return self._database.get_all_accounts()

    def get_accounts_by_category(self, category: str) -> List[CategorizedAccount]:
        """
        Retrieve accounts filtered by category.

        Args:
            category: Category name to filter by.

        Returns:
            List of accounts in the specified category.
        """
        all_accounts = self._database.get_all_accounts()
        return [
            account for account in all_accounts
            if account.category == category
        ]

    def get_account_by_username(self, username: str) -> Optional[CategorizedAccount]:
        """
        Retrieve account by username.

        Args:
            username: Username to search for.

        Returns:
            Account if found, None otherwise.
        """
        all_accounts = self._database.get_all_accounts()
        for account in all_accounts:
            if account.username == username:
                return account
        return None

    def get_account_by_user_id(self, user_id: str) -> Optional[CategorizedAccount]:
        """
        Retrieve account by user ID.

        Args:
            user_id: User ID to search for.

        Returns:
            Account if found, None otherwise.
        """
        all_accounts = self._database.get_all_accounts()
        for account in all_accounts:
            if account.user_id == user_id:
                return account
        return None

    def save_accounts(self, accounts: List[CategorizedAccount]) -> None:
        """
        Persist multiple accounts to database.

        Args:
            accounts: List of accounts to save.
        """
        self._database.save_accounts(accounts)

    def count_total_accounts(self) -> int:
        """
        Count total number of accounts in database.

        Returns:
            Total account count.
        """
        return len(self._database.get_all_accounts())

    def get_verified_accounts(self) -> List[CategorizedAccount]:
        """
        Retrieve all verified accounts.

        Returns:
            List of verified accounts.
        """
        all_accounts = self._database.get_all_accounts()
        return [
            account for account in all_accounts
            if account.verified
        ]

    def get_accounts_with_minimum_followers(
        self,
        minimum_followers: int
    ) -> List[CategorizedAccount]:
        """
        Retrieve accounts with at least the specified follower count.

        Args:
            minimum_followers: Minimum number of followers required.

        Returns:
            List of accounts meeting the follower threshold.
        """
        all_accounts = self._database.get_all_accounts()
        return [
            account for account in all_accounts
            if account.followers_count >= minimum_followers
        ]
