"""
Category repository for data access operations.

Provides abstraction layer for category-related database operations
following the Repository Pattern.
"""

from typing import Any, Dict, List

from backend.database import DatabaseManager


class CategoryRepository:
    """Repository for category data access operations."""

    def __init__(self, database_manager: DatabaseManager):
        """
        Initialize category repository.

        Args:
            database_manager: Database manager instance for data access.
        """
        self._database = database_manager

    def get_all_categories(self) -> List[Dict[str, Any]]:
        """
        Retrieve all categories metadata from database.

        Returns:
            List of category dictionaries.
        """
        return self._database.get_categories()

    def get_category_names(self) -> List[str]:
        """
        Retrieve list of all category names.

        Returns:
            List of category names.
        """
        categories_list = self._database.get_categories()
        if not categories_list:
            return []

        return [
            category["name"]
            for category in categories_list
            if "name" in category
        ]

    def save_categories(self, categories_data: Dict[str, Any]) -> None:
        """
        Persist categories metadata to database.

        Args:
            categories_data: Dictionary containing categories metadata.
        """
        self._database.save_categories(categories_data)

    def get_category_count(self) -> int:
        """
        Count total number of categories.

        Returns:
            Total category count.
        """
        return len(self.get_all_categories())
