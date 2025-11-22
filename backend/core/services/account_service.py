"""
Account service for business logic operations.

Orchestrates account-related business operations using repositories
and external services.
"""

from typing import List, Optional

from backend.db.repositories.account_repository import AccountRepository
from backend.models import CategorizedAccount


class AccountService:
    """Service for account-related business logic."""

    def __init__(self, account_repository: AccountRepository):
        """
        Initialize account service.

        Args:
            account_repository: Repository for account data access.
        """
        self._account_repository = account_repository

    def get_all_accounts(self) -> List[CategorizedAccount]:
        """
        Retrieve all accounts.

        Returns:
            List of all categorized accounts.
        """
        return self._account_repository.get_all_accounts()

    def get_accounts_by_category(self, category: str) -> List[CategorizedAccount]:
        """
        Retrieve accounts in a specific category.

        Args:
            category: Category name to filter by.

        Returns:
            List of accounts in the specified category.
        """
        return self._account_repository.get_accounts_by_category(category)

    def get_account_by_username(self, username: str) -> Optional[CategorizedAccount]:
        """
        Retrieve account by username.

        Args:
            username: Username to search for.

        Returns:
            Account if found, None otherwise.
        """
        return self._account_repository.get_account_by_username(username)

    def get_verified_accounts(self) -> List[CategorizedAccount]:
        """
        Retrieve all verified accounts.

        Returns:
            List of verified accounts.
        """
        return self._account_repository.get_verified_accounts()

    def get_top_accounts_by_followers(
        self,
        limit: int = 10
    ) -> List[CategorizedAccount]:
        """
        Retrieve top accounts by follower count.

        Args:
            limit: Maximum number of accounts to return.

        Returns:
            List of top accounts sorted by followers descending.
        """
        all_accounts = self._account_repository.get_all_accounts()
        sorted_accounts = sorted(
            all_accounts,
            key=lambda account: account.followers_count,
            reverse=True
        )
        return sorted_accounts[:limit]

    def get_top_accounts_in_category(
        self,
        category: str,
        limit: int = 10
    ) -> List[CategorizedAccount]:
        """
        Retrieve top accounts in a category by follower count.

        Args:
            category: Category name to filter by.
            limit: Maximum number of accounts to return.

        Returns:
            List of top accounts in category sorted by followers descending.
        """
        category_accounts = self._account_repository.get_accounts_by_category(category)
        sorted_accounts = sorted(
            category_accounts,
            key=lambda account: account.followers_count,
            reverse=True
        )
        return sorted_accounts[:limit]

    def search_accounts(
        self,
        search_term: str
    ) -> List[CategorizedAccount]:
        """
        Search accounts by username or display name.

        Args:
            search_term: Term to search for (case-insensitive).

        Returns:
            List of matching accounts.
        """
        all_accounts = self._account_repository.get_all_accounts()
        search_term_lower = search_term.lower()

        return [
            account for account in all_accounts
            if (search_term_lower in account.username.lower() or
                search_term_lower in account.display_name.lower())
        ]

    def filter_accounts(
        self,
        category: Optional[str] = None,
        verified_only: bool = False,
        minimum_followers: Optional[int] = None
    ) -> List[CategorizedAccount]:
        """
        Filter accounts by multiple criteria.

        Args:
            category: Optional category name to filter by.
            verified_only: If True, return only verified accounts.
            minimum_followers: Optional minimum follower count.

        Returns:
            List of accounts matching all filter criteria.
        """
        # Start with all accounts or category-filtered accounts
        if category:
            accounts = self._account_repository.get_accounts_by_category(category)
        else:
            accounts = self._account_repository.get_all_accounts()

        # Apply verified filter
        if verified_only:
            accounts = [
                account for account in accounts
                if account.verified
            ]

        # Apply minimum followers filter
        if minimum_followers is not None:
            accounts = [
                account for account in accounts
                if account.followers_count >= minimum_followers
            ]

        return accounts
