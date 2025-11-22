"""
Scan service for orchestrating account scanning and categorization.

Orchestrates the complete scan flow: fetch accounts from X API,
discover categories, categorize accounts, and save to database.
"""

import logging
from datetime import datetime
from typing import Callable, Dict, List, Optional

from backend.api.grok_client import GrokAPIError, GrokClient
from backend.api.x_client import XAPIError, XAPIClient
from backend.db.repositories.account_repository import AccountRepository
from backend.db.repositories.category_repository import CategoryRepository
from backend.models import CategorizedAccount, XAccount

logger = logging.getLogger(__name__)


class ScanError(Exception):
    """Custom exception for scan operation errors."""

    def __init__(self, message: str, step: Optional[str] = None):
        """
        Initialize scan error.

        Args:
            message: Error message
            step: Current scan step when error occurred
        """
        self.step = step
        super().__init__(message)


class ScanStatus:
    """Status tracking for scan operations."""

    def __init__(self, job_id: str):
        """
        Initialize scan status.

        Args:
            job_id: Unique job identifier
        """
        self.job_id = job_id
        self.status: str = "pending"
        self.progress: float = 0.0
        self.current_step: str = ""
        self.message: str = ""
        self.current: int = 0
        self.total: int = 0
        self.error: Optional[str] = None
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.accounts_fetched: int = 0
        self.accounts_categorized: int = 0
        self.accounts_saved: int = 0


class ScanResult:
    """Result of a completed scan operation."""

    def __init__(
        self,
        job_id: str,
        accounts_fetched: int,
        accounts_categorized: int,
        accounts_saved: int,
        categories_discovered: int,
        duration_seconds: float,
    ):
        """
        Initialize scan result.

        Args:
            job_id: Unique job identifier
            accounts_fetched: Number of accounts fetched from X API
            accounts_categorized: Number of accounts successfully categorized
            accounts_saved: Number of accounts saved to database
            categories_discovered: Number of categories discovered
            duration_seconds: Total scan duration in seconds
        """
        self.job_id = job_id
        self.accounts_fetched = accounts_fetched
        self.accounts_categorized = accounts_categorized
        self.accounts_saved = accounts_saved
        self.categories_discovered = categories_discovered
        self.duration_seconds = duration_seconds


class ScanService:
    """
    Service for orchestrating account scanning and categorization.

    Coordinates the complete workflow:
    1. Fetch accounts from X API
    2. Discover categories using Grok AI
    3. Categorize all accounts
    4. Save to database
    """

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
            x_client: X API client for fetching accounts
            grok_client: Grok API client for categorization
            account_repository: Repository for account data access
            category_repository: Repository for category data access
        """
        self._x_client = x_client
        self._grok_client = grok_client
        self._account_repository = account_repository
        self._category_repository = category_repository

    async def scan_and_categorize(
        self,
        user_id: str,
        progress_callback: Optional[Callable[[ScanStatus], None]] = None,
    ) -> ScanResult:
        """
        Execute complete scan and categorization workflow.

        Args:
            user_id: X user ID to fetch following accounts for
            progress_callback: Optional callback function for progress updates

        Returns:
            ScanResult with operation summary

        Raises:
            ScanError: If scan operation fails
        """
        job_id = f"scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{user_id}"
        scan_status = ScanStatus(job_id=job_id)
        scan_status.started_at = datetime.now()

        try:
            # Step 1: Fetch accounts (0-30%)
            scan_status.status = "running"
            scan_status.current_step = "fetch_accounts"
            scan_status.message = "Fetching accounts from X API..."
            scan_status.progress = 0.0
            self._notify_progress(scan_status, progress_callback)

            accounts = await self._fetch_accounts(user_id, scan_status, progress_callback)
            scan_status.accounts_fetched = len(accounts)
            scan_status.progress = 30.0
            scan_status.message = f"Fetched {len(accounts)} accounts"
            self._notify_progress(scan_status, progress_callback)

            if not accounts:
                raise ScanError("No accounts found to categorize", step="fetch_accounts")

            # Step 2: Discover categories (30-50%)
            scan_status.current_step = "discover_categories"
            scan_status.message = "Discovering categories using AI..."
            scan_status.progress = 30.0
            self._notify_progress(scan_status, progress_callback)

            categories_metadata = await self._discover_categories(
                accounts, scan_status, progress_callback
            )
            categories_count = len(categories_metadata.get("categories", []))
            scan_status.progress = 50.0
            scan_status.message = f"Discovered {categories_count} categories"
            self._notify_progress(scan_status, progress_callback)

            # Step 3: Categorize accounts (50-90%)
            scan_status.current_step = "categorize_accounts"
            scan_status.message = "Categorizing accounts..."
            scan_status.total = len(accounts)
            scan_status.current = 0
            scan_status.progress = 50.0
            self._notify_progress(scan_status, progress_callback)

            categorized_accounts = await self._categorize_accounts(
                accounts, categories_metadata, scan_status, progress_callback
            )
            scan_status.accounts_categorized = len(categorized_accounts)
            scan_status.progress = 90.0
            scan_status.message = f"Categorized {len(categorized_accounts)} accounts"
            self._notify_progress(scan_status, progress_callback)

            # Step 4: Save to database (90-100%)
            scan_status.current_step = "save_to_database"
            scan_status.message = "Saving accounts to database..."
            scan_status.progress = 90.0
            self._notify_progress(scan_status, progress_callback)

            await self._save_results(categorized_accounts, categories_metadata)
            scan_status.accounts_saved = len(categorized_accounts)
            scan_status.progress = 100.0
            scan_status.message = "Scan completed successfully"
            self._notify_progress(scan_status, progress_callback)

            # Complete
            scan_status.status = "completed"
            scan_status.completed_at = datetime.now()

            duration = (
                scan_status.completed_at - scan_status.started_at
            ).total_seconds()

            return ScanResult(
                job_id=job_id,
                accounts_fetched=scan_status.accounts_fetched,
                accounts_categorized=scan_status.accounts_categorized,
                accounts_saved=scan_status.accounts_saved,
                categories_discovered=categories_count,
                duration_seconds=duration,
            )

        except XAPIError as e:
            error_message = f"X API error: {str(e)}"
            logger.error(error_message, exc_info=True)
            scan_status.status = "error"
            scan_status.error = error_message
            scan_status.completed_at = datetime.now()
            self._notify_progress(scan_status, progress_callback)
            raise ScanError(error_message, step=scan_status.current_step) from e

        except GrokAPIError as e:
            error_message = f"Grok API error: {str(e)}"
            logger.error(error_message, exc_info=True)
            scan_status.status = "error"
            scan_status.error = error_message
            scan_status.completed_at = datetime.now()
            self._notify_progress(scan_status, progress_callback)
            raise ScanError(error_message, step=scan_status.current_step) from e

        except Exception as e:
            error_message = f"Unexpected error: {str(e)}"
            logger.error(error_message, exc_info=True)
            scan_status.status = "error"
            scan_status.error = error_message
            scan_status.completed_at = datetime.now()
            self._notify_progress(scan_status, progress_callback)
            raise ScanError(error_message, step=scan_status.current_step) from e

    async def _fetch_accounts(
        self,
        user_id: str,
        scan_status: ScanStatus,
        progress_callback: Optional[Callable[[ScanStatus], None]],
    ) -> List[XAccount]:
        """
        Fetch accounts from X API.

        Args:
            user_id: X user ID
            scan_status: Status tracker for progress updates
            progress_callback: Optional progress callback

        Returns:
            List of fetched accounts

        Raises:
            XAPIError: If API request fails
        """
        try:
            accounts = await self._x_client.get_all_following(user_id)
            return accounts
        except XAPIError as e:
            logger.error(f"Failed to fetch accounts for user {user_id}: {e}")
            raise

    async def _discover_categories(
        self,
        accounts: List[XAccount],
        scan_status: ScanStatus,
        progress_callback: Optional[Callable[[ScanStatus], None]],
    ) -> Dict:
        """
        Discover categories from account sample.

        Args:
            accounts: List of accounts to analyze
            scan_status: Status tracker for progress updates
            progress_callback: Optional progress callback

        Returns:
            Dictionary containing discovered categories metadata

        Raises:
            GrokAPIError: If category discovery fails
        """
        try:
            # Use a sample for discovery (more efficient)
            # analyze_and_categorize will use sample_size internally
            # but we call it with all accounts and it handles sampling
            sample_size = min(200, len(accounts))  # Use sample for discovery
            sample_accounts = accounts[:sample_size]
            
            # Call analyze_and_categorize with sample to discover categories
            # This will discover categories and categorize the sample
            categories_metadata, _ = await self._grok_client.analyze_and_categorize(
                sample_accounts, sample_size=sample_size
            )
            return categories_metadata
        except GrokAPIError as e:
            logger.error(f"Failed to discover categories: {e}")
            raise

    async def _categorize_accounts(
        self,
        accounts: List[XAccount],
        categories_metadata: Dict,
        scan_status: ScanStatus,
        progress_callback: Optional[Callable[[ScanStatus], None]],
    ) -> List[CategorizedAccount]:
        """
        Categorize all accounts using discovered categories.

        Args:
            accounts: List of accounts to categorize
            categories_metadata: Discovered categories metadata
            scan_status: Status tracker for progress updates
            progress_callback: Optional progress callback

        Returns:
            List of categorized accounts

        Raises:
            GrokAPIError: If categorization fails
        """
        try:
            # Use existing categories for categorization (more efficient)
            categorized_accounts = await self._grok_client.categorize_with_existing_categories(
                accounts, categories_metadata
            )

            # Update progress during categorization
            total_accounts = len(accounts)
            for index, _ in enumerate(categorized_accounts, start=1):
                if index % 10 == 0 or index == total_accounts:
                    progress = 50.0 + (index / total_accounts) * 40.0
                    scan_status.progress = min(progress, 90.0)
                    scan_status.current = index
                    scan_status.message = f"Categorizing account {index}/{total_accounts}"
                    self._notify_progress(scan_status, progress_callback)

            return categorized_accounts
        except GrokAPIError as e:
            logger.error(f"Failed to categorize accounts: {e}")
            raise

    async def _save_results(
        self,
        categorized_accounts: List[CategorizedAccount],
        categories_metadata: Dict,
    ) -> None:
        """
        Save categorized accounts and categories to database.

        Args:
            categorized_accounts: List of categorized accounts to save
            categories_metadata: Categories metadata to save
        """
        try:
            self._account_repository.save_accounts(categorized_accounts)
            self._category_repository.save_categories(categories_metadata)
            logger.info(
                f"Saved {len(categorized_accounts)} accounts and "
                f"{len(categories_metadata.get('categories', []))} categories"
            )
        except Exception as e:
            logger.error(f"Failed to save results to database: {e}")
            raise ScanError(f"Database save failed: {str(e)}", step="save_to_database")

    def _notify_progress(
        self,
        scan_status: ScanStatus,
        progress_callback: Optional[Callable[[ScanStatus], None]],
    ) -> None:
        """
        Notify progress callback if provided.

        Args:
            scan_status: Current scan status
            progress_callback: Optional callback function
        """
        if progress_callback:
            try:
                progress_callback(scan_status)
            except Exception as e:
                logger.warning(f"Progress callback failed: {e}")
