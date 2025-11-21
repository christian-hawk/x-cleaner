"""
Dependency injection container for FastAPI.

Provides dependency injection functions for services and repositories,
following FastAPI's dependency injection pattern.
"""

from typing import Generator, Optional

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


def get_account_repository(
    database: Optional[DatabaseManager] = None,
) -> AccountRepository:
    """
    Dependency for account repository.

    Args:
        database: Database manager instance (injected).

    Returns:
        Account repository instance.
    """
    if database is None:
        database = DatabaseManager()
    return AccountRepository(database_manager=database)


def get_category_repository(
    database: Optional[DatabaseManager] = None,
) -> CategoryRepository:
    """
    Dependency for category repository.

    Args:
        database: Database manager instance (injected).

    Returns:
        Category repository instance.
    """
    if database is None:
        database = DatabaseManager()
    return CategoryRepository(database_manager=database)


def get_account_service(
    account_repository: Optional[AccountRepository] = None,
) -> AccountService:
    """
    Dependency for account service.

    Args:
        account_repository: Account repository instance (injected).

    Returns:
        Account service instance.
    """
    if account_repository is None:
        account_repository = get_account_repository()
    return AccountService(account_repository=account_repository)


def get_statistics_service(
    account_repository: Optional[AccountRepository] = None,
    category_repository: Optional[CategoryRepository] = None,
) -> StatisticsService:
    """
    Dependency for statistics service.

    Args:
        account_repository: Account repository instance (injected).
        category_repository: Category repository instance (injected).

    Returns:
        Statistics service instance.
    """
    if account_repository is None:
        account_repository = get_account_repository()
    if category_repository is None:
        category_repository = get_category_repository()

    return StatisticsService(
        account_repository=account_repository,
        category_repository=category_repository,
    )
