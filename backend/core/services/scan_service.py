"""
Scan service for orchestrating complete scan workflow.

This service coordinates the entire scan process: fetching accounts from X API,
categorizing with Grok AI, and persisting results to the database.
"""

import asyncio
from typing import Callable, Dict, List, Optional

from backend.api.grok_client import GrokAPIError, GrokClient
from backend.api.x_client import XAPIClient, XAPIError
from backend.db.repositories.account_repository import AccountRepository
from backend.db.repositories.category_repository import CategoryRepository
from backend.models import CategorizedAccount, XAccount


class ScanResult:
    """Result of a complete scan operation."""

    def __init__(
        self,
        success: bool,
        accounts_scanned: int = 0,
        categories_discovered: int = 0,
        error_message: Optional[str] = None,
        category_metadata: Optional[Dict] = None,
    ):
        """
        Initialize scan result.

        Args:
            success: Whether scan completed successfully.
            accounts_scanned: Number of accounts processed.
            categories_discovered: Number of categories discovered.
            error_message: Error message if scan failed.
            category_metadata: Discovered categories metadata.
        """
        self.success = success
        self.accounts_scanned = accounts_scanned
        self.categories_discovered = categories_discovered
        self.error_message = error_message
        self.category_metadata = category_metadata


class ScanService:
    """Service for orchestrating complete scan workflow."""

    def __init__(
        self,
        x_client: XAPIClient,
        grok_client: GrokClient,
        account_repository: AccountRepository,
        category_repository: CategoryRepository,
    ):
        """
        Initialize scan service.

        Args:
            x_client: X API client for fetching accounts.
            grok_client: Grok AI client for categorization.
            account_repository: Repository for account persistence.
            category_repository: Repository for category persistence.
        """
        self._x_client = x_client
        self._grok = grok_client
        self._accounts = account_repository
        self._categories = category_repository

    async def execute_scan(
        self,
        user_id: str,
        progress_callback: Optional[Callable[[str, int], None]] = None,
    ) -> ScanResult:
        """
        Execute complete scan workflow.

        Workflow steps:
        1. Fetch accounts from X API
        2. Discover categories with Grok
        3. Categorize all accounts
        4. Save to database

        Args:
            user_id: X user ID to scan following accounts for.
            progress_callback: Optional callback for progress updates.
                              Receives (message: str, progress: int) where
                              progress is 0-100.

        Returns:
            ScanResult with operation details.
        """
        try:
            # Step 1: Fetch accounts from X API
            self._update_progress(progress_callback, "Fetching accounts from X API...", 10)

            accounts = await self._fetch_accounts_from_x(user_id)

            if not accounts:
                return ScanResult(
                    success=False,
                    error_message="No accounts found or user has no following",
                )

            self._update_progress(
                progress_callback,
                f"Fetched {len(accounts)} accounts from X API",
                30,
            )

            # Step 2: Discover categories and categorize with Grok
            self._update_progress(
                progress_callback,
                "Analyzing accounts and discovering categories...",
                40,
            )

            category_metadata, categorized_accounts = await self._categorize_accounts(
                accounts
            )

            self._update_progress(
                progress_callback,
                f"Discovered {len(category_metadata.get('categories', []))} categories",
                70,
            )

            # Step 3: Save to database
            self._update_progress(progress_callback, "Saving results to database...", 80)

            await self._save_results(category_metadata, categorized_accounts)

            self._update_progress(progress_callback, "Scan complete!", 100)

            return ScanResult(
                success=True,
                accounts_scanned=len(categorized_accounts),
                categories_discovered=len(category_metadata.get("categories", [])),
                category_metadata=category_metadata,
            )

        except XAPIError as e:
            error_msg = f"X API error: {str(e)}"
            self._update_progress(progress_callback, f"Error: {error_msg}", 0)
            return ScanResult(success=False, error_message=error_msg)

        except GrokAPIError as e:
            error_msg = f"Grok AI error: {str(e)}"
            self._update_progress(progress_callback, f"Error: {error_msg}", 0)
            return ScanResult(success=False, error_message=error_msg)

        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            self._update_progress(progress_callback, f"Error: {error_msg}", 0)
            return ScanResult(success=False, error_message=error_msg)

    async def _fetch_accounts_from_x(self, user_id: str) -> List[XAccount]:
        """
        Fetch all following accounts from X API.

        Args:
            user_id: X user ID to fetch following for.

        Returns:
            List of XAccount objects.

        Raises:
            XAPIError: If API request fails.
        """
        accounts = await self._x_client.get_all_following(user_id)
        return accounts

    async def _categorize_accounts(
        self, accounts: List[XAccount]
    ) -> tuple[Dict, List[CategorizedAccount]]:
        """
        Discover categories and categorize accounts with Grok.

        Args:
            accounts: List of accounts to categorize.

        Returns:
            Tuple of (category_metadata, categorized_accounts).

        Raises:
            GrokAPIError: If categorization fails.
        """
        category_metadata, categorized_accounts = (
            await self._grok.analyze_and_categorize(accounts)
        )

        return category_metadata, categorized_accounts

    async def _save_results(
        self,
        category_metadata: Dict,
        categorized_accounts: List[CategorizedAccount],
    ) -> None:
        """
        Save scan results to database.

        Args:
            category_metadata: Discovered categories metadata.
            categorized_accounts: List of categorized accounts.
        """
        # Save in parallel using asyncio
        await asyncio.gather(
            asyncio.to_thread(self._categories.save_categories, category_metadata),
            asyncio.to_thread(self._accounts.save_accounts, categorized_accounts),
        )

    def _update_progress(
        self,
        callback: Optional[Callable[[str, int], None]],
        message: str,
        progress: int,
    ) -> None:
        """
        Update progress via callback if provided.

        Args:
            callback: Progress callback function.
            message: Progress message.
            progress: Progress percentage (0-100).
        """
        if callback:
            callback(message, progress)
