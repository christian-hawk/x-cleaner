"""
Dependency injection container for FastAPI.

Provides dependency injection functions for services and repositories,
following FastAPI's dependency injection pattern.
"""

from collections.abc import Generator
from typing import Annotated

from fastapi import Depends

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
    database: Annotated[DatabaseManager, Depends(get_database)],
) -> AccountRepository:
    """
    Dependency for account repository.

    Returns:
        Account repository instance.
    """
    return AccountRepository(database_manager=database)


def get_category_repository(
    database: Annotated[DatabaseManager, Depends(get_database)],
) -> CategoryRepository:
    """
    Dependency for category repository.

    Returns:
        Category repository instance.
    """
    return CategoryRepository(database_manager=database)


def get_account_service(
    account_repository: Annotated[AccountRepository, Depends(get_account_repository)],
) -> AccountService:
    """
    Dependency for account service.

    Returns:
        Account service instance.
    """
    return AccountService(account_repository=account_repository)


def get_statistics_service(
    account_repository: Annotated[AccountRepository, Depends(get_account_repository)],
    category_repository: Annotated[CategoryRepository, Depends(get_category_repository)],
) -> StatisticsService:
    """
    Dependency for statistics service.

    Returns:
        Statistics service instance.
    """
    return StatisticsService(
        account_repository=account_repository,
        category_repository=category_repository,
    )
