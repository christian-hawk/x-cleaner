"""
Scan service for orchestrating the complete scan workflow.

This service coordinates fetching accounts from X API, categorizing them
using AI, and saving results to the database.
"""

import logging
from typing import Callable, Optional

from backend.api.grok_client import GrokAPIError
from backend.api.x_client import XAPIError, XAPIClient
from backend.core.services.categorizer import CategorizationService
from backend.database import DatabaseManager
from backend.models import CategorizedAccount, XAccount

logger = logging.getLogger(__name__)


class ScanService:
    """
    Service for orchestrating account scanning and categorization.

    Coordinates the complete workflow:
    1. Fetch accounts from X API
    2. Categorize accounts using AI
    3. Save results to database
    """

    def __init__(
        self,
        x_client: Optional[XAPIClient] = None,
        categorization_service: Optional[CategorizationService] = None,
        db_manager: Optional[DatabaseManager] = None,
    ):
        """
        Initialize scan service.

        Args:
            x_client: X API client (creates new if not provided)
            categorization_service: Categorization service (creates new if not provided)
            db_manager: Database manager (creates new if not provided)
        """
        self.x_client = x_client or XAPIClient()
        self.categorization_service = (
            categorization_service or CategorizationService(db_manager=db_manager)
        )
        self.db_manager = db_manager or DatabaseManager()

    async def scan_and_categorize(
        self,
        user_id: str,
        progress_callback: Optional[Callable[[str, int, str], None]] = None,
    ) -> tuple[dict, list[CategorizedAccount]]:
        """
        Execute complete scan workflow: fetch → categorize → save.

        Args:
            user_id: X user ID to scan following accounts for
            progress_callback: Optional callback function(status, progress, message)
                             Called with: (status, progress_percent, message)

        Returns:
            Tuple of (category_metadata, categorized_accounts)

        Raises:
            XAPIError: If fetching accounts fails
            GrokAPIError: If categorization fails
            ValueError: If user_id is invalid
        """
        if not user_id:
            raise ValueError("user_id is required")

        try:
            # Step 1: Fetch accounts from X API
            if progress_callback:
                progress_callback("running", 10, "Fetching accounts from X API...")

            logger.info(f"Starting scan for user_id: {user_id}")
            accounts = await self.x_client.get_all_following(user_id)

            if not accounts:
                logger.warning(f"No accounts found for user_id: {user_id}")
                if progress_callback:
                    progress_callback("completed", 100, "No accounts found")
                return {}, []

            logger.info(f"Fetched {len(accounts)} accounts from X API")

            # Step 2: Categorize accounts
            if progress_callback:
                progress_callback("running", 50, f"Categorizing {len(accounts)} accounts...")

            categories_metadata, categorized_accounts = (
                await self.categorization_service.categorize_accounts(accounts)
            )

            logger.info(
                f"Categorized {len(categorized_accounts)} accounts into "
                f"{len(categories_metadata.get('categories', []))} categories"
            )

            # Step 3: Save results (already done by categorization_service, but ensure)
            if progress_callback:
                progress_callback("running", 90, "Saving results to database...")

            # Results are already saved by categorization_service, but we ensure
            # categories are saved
            self.db_manager.save_categories(categories_metadata)
            self.db_manager.save_accounts(categorized_accounts)

            if progress_callback:
                progress_callback(
                    "completed",
                    100,
                    f"Scan completed: {len(categorized_accounts)} accounts categorized",
                )

            logger.info("Scan completed successfully")

            return categories_metadata, categorized_accounts

        except XAPIError as e:
            logger.error(f"X API error during scan: {e}")
            if progress_callback:
                progress_callback("error", 0, f"X API error: {str(e)}")
            raise

        except GrokAPIError as e:
            logger.error(f"Grok API error during scan: {e}")
            if progress_callback:
                progress_callback("error", 0, f"Grok API error: {str(e)}")
            raise

        except Exception as e:
            logger.error(f"Unexpected error during scan: {e}", exc_info=True)
            if progress_callback:
                progress_callback("error", 0, f"Unexpected error: {str(e)}")
            raise
