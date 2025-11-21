"""
FastAPI routes for account-related endpoints.

Provides REST API endpoints for account data access and operations.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from backend.api.schemas.account import AccountListResponse, AccountResponse
from backend.core.services.account_service import AccountService
from backend.dependencies import get_account_service
from backend.models import CategorizedAccount

router = APIRouter(prefix="/api/accounts", tags=["accounts"])


def _convert_account_to_response(account: CategorizedAccount) -> AccountResponse:
    """
    Convert domain model to API response schema.

    Args:
        account: Domain account model.

    Returns:
        Account response schema.
    """
    return AccountResponse(
        user_id=account.user_id,
        username=account.username,
        display_name=account.display_name,
        bio=account.bio,
        verified=account.verified,
        followers_count=account.followers_count,
        following_count=account.following_count,
        tweet_count=account.tweet_count,
        location=account.location,
        website=account.website,
        profile_image_url=account.profile_image_url,
        category=account.category,
        confidence=account.confidence,
        reasoning=account.reasoning or "",
        created_at=account.created_at,
        analyzed_at=account.analyzed_at,
    )


@router.get("", response_model=AccountListResponse)
async def list_accounts(
    category: Optional[str] = Query(None, description="Filter by category"),
    verified_only: bool = Query(False, description="Return only verified accounts"),
    minimum_followers: Optional[int] = Query(None, ge=0, description="Minimum follower count"),
    account_service: AccountService = Depends(get_account_service),
) -> AccountListResponse:
    """
    List all accounts with optional filtering.

    Args:
        category: Optional category filter.
        verified_only: If True, return only verified accounts.
        minimum_followers: Optional minimum follower count filter.
        account_service: Injected account service.

    Returns:
        List of accounts matching filter criteria.
    """
    accounts = account_service.filter_accounts(
        category=category,
        verified_only=verified_only,
        minimum_followers=minimum_followers,
    )

    account_responses = [
        _convert_account_to_response(account)
        for account in accounts
    ]

    return AccountListResponse(
        accounts=account_responses,
        total=len(account_responses),
        category=category,
    )


@router.get("/top", response_model=List[AccountResponse])
async def get_top_accounts(
    limit: int = Query(10, ge=1, le=100, description="Number of accounts to return"),
    category: Optional[str] = Query(None, description="Optional category filter"),
    account_service: AccountService = Depends(get_account_service),
) -> List[AccountResponse]:
    """
    Get top accounts by follower count.

    Args:
        limit: Maximum number of accounts to return.
        category: Optional category filter.
        account_service: Injected account service.

    Returns:
        List of top accounts sorted by followers descending.
    """
    if category:
        accounts = account_service.get_top_accounts_in_category(
            category=category,
            limit=limit,
        )
    else:
        accounts = account_service.get_top_accounts_by_followers(limit=limit)

    return [
        _convert_account_to_response(account)
        for account in accounts
    ]


@router.get("/search", response_model=List[AccountResponse])
async def search_accounts(
    query: str = Query(..., min_length=1, description="Search term"),
    account_service: AccountService = Depends(get_account_service),
) -> List[AccountResponse]:
    """
    Search accounts by username or display name.

    Args:
        query: Search term (case-insensitive).
        account_service: Injected account service.

    Returns:
        List of matching accounts.
    """
    accounts = account_service.search_accounts(search_term=query)

    return [
        _convert_account_to_response(account)
        for account in accounts
    ]


@router.get("/{username}", response_model=AccountResponse)
async def get_account_by_username(
    username: str,
    account_service: AccountService = Depends(get_account_service),
) -> AccountResponse:
    """
    Get specific account by username.

    Args:
        username: Account username.
        account_service: Injected account service.

    Returns:
        Account details.

    Raises:
        HTTPException: 404 if account not found.
    """
    account = account_service.get_account_by_username(username)

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account with username '{username}' not found",
        )

    return _convert_account_to_response(account)
