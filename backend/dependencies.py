"""
Dependency injection container for FastAPI.

Provides dependency injection functions for services and repositories,
following FastAPI's dependency injection pattern.
"""

from typing import Generator

from backend.core.services.account_service import AccountService
from backend.core.services.statistics_service import StatisticsService
from backend.database import DatabaseManager
from backend.db.repositories.account_repository import AccountRepository
from backend.db.repositories.category_repository import CategoryRepository


def get_database() -> Generator[DatabaseManager, None, None]:
    """
    Dependency for database access.

    Yields:
        Database manager instance.
    """
    database = DatabaseManager()
    try:
        yield database
    finally:
        # Database cleanup if needed
        pass


def get_account_repository() -> AccountRepository:
    """
    Dependency for account repository.

    Returns:
        Account repository instance.
    """
    database = DatabaseManager()
    return AccountRepository(database_manager=database)


def get_category_repository() -> CategoryRepository:
    """
    Dependency for category repository.

    Returns:
        Category repository instance.
    """
    database = DatabaseManager()
    return CategoryRepository(database_manager=database)


def get_account_service() -> AccountService:
    """
    Dependency for account service.

    Returns:
        Account service instance.
    """
    account_repository = get_account_repository()
    return AccountService(account_repository=account_repository)


def get_statistics_service() -> StatisticsService:
    """
    Dependency for statistics service.

    Returns:
        Statistics service instance.
    """
    account_repository = get_account_repository()
    category_repository = get_category_repository()

    return StatisticsService(
        account_repository=account_repository,
        category_repository=category_repository,
    )
