"""
X API v2 Client for fetching following accounts.

This module provides a client for interacting with the X (Twitter) API v2
to fetch user following data and account information.
"""

from __future__ import annotations

import asyncio
import os
from types import TracebackType
from typing import List, Optional, Tuple, Type

import httpx
from httpx import HTTPStatusError, RequestError

from ..models import XAccount


class XAPIError(Exception):
    """Custom exception for X API errors."""

    def __init__(self, message: str, status_code: Optional[int] = None):
        """
        Initialize X API error.

        Args:
            message: Error message
            status_code: HTTP status code if applicable
        """
        self.status_code = status_code
        super().__init__(message)


class XAPIClient:
    """
    Client for X API v2.

    Handles authentication, pagination, rate limiting, and data fetching
    from the X (Twitter) API v2.
    """

    BASE_URL = "https://api.twitter.com/2"
    DEFAULT_MAX_RESULTS = 1000

    def __init__(self, bearer_token: Optional[str] = None):
        """
        Initialize X API client.

        Args:
            bearer_token: X API Bearer Token. If not provided, reads from
                         X_API_BEARER_TOKEN environment variable.

        Raises:
            ValueError: If bearer token is not provided or found in environment
        """
        self.bearer_token = bearer_token or os.getenv("X_API_BEARER_TOKEN")
        if not self.bearer_token:
            raise ValueError(
                "X API Bearer Token not provided. Set X_API_BEARER_TOKEN "
                "environment variable or pass bearer_token parameter."
            )

        self.headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "Content-Type": "application/json",
        }
        self.client = httpx.AsyncClient(headers=self.headers, timeout=30.0)

    async def get_following(
        self,
        user_id: str,
        max_results: int = 1000,
        pagination_token: Optional[str] = None,
    ) -> Tuple[List[XAccount], Optional[str]]:
        """
        Fetch accounts that a user follows.

        Args:
            user_id: X user ID to fetch following accounts for
            max_results: Maximum number of results per request (max 1000)
            pagination_token: Token for pagination (from previous request)

        Returns:
            Tuple of (list of XAccount objects, next pagination token)

        Raises:
            XAPIError: If API request fails
        """
        url = f"{self.BASE_URL}/users/{user_id}/following"

        # Build params dict with explicit types for httpx
        params: dict[str, str | int] = {
            "max_results": min(max_results, self.DEFAULT_MAX_RESULTS),
            "user.fields": (
                "id,username,name,description,verified,created_at,"
                "public_metrics,location,url,profile_image_url"
            ),
        }

        if pagination_token:
            params["pagination_token"] = pagination_token

        try:
            response = await self.client.get(url, params=params)
            response.raise_for_status()
        except HTTPStatusError as e:
            if e.response.status_code == 429:
                # Rate limit exceeded
                reset_time = e.response.headers.get("x-rate-limit-reset", "unknown")
                raise XAPIError(
                    f"Rate limit exceeded. Resets at: {reset_time}",
                    status_code=429,
                ) from e
            elif e.response.status_code == 401:
                raise XAPIError(
                    "Authentication failed. Check your Bearer Token.",
                    status_code=401,
                ) from e
            elif e.response.status_code == 404:
                raise XAPIError(
                    f"User ID {user_id} not found.",
                    status_code=404,
                ) from e
            else:
                raise XAPIError(
                    f"HTTP {e.response.status_code}: {e.response.text}",
                    status_code=e.response.status_code,
                ) from e
        except RequestError as e:
            raise XAPIError(f"Request failed: {str(e)}") from e

        data = response.json()
        accounts = [self._parse_account(user) for user in data.get("data", [])]
        next_token = data.get("meta", {}).get("next_token")

        return accounts, next_token

    async def get_all_following(
        self, user_id: str, rate_limit_delay: float = 1.0
    ) -> List[XAccount]:
        """
        Fetch all following accounts with pagination.

        Automatically handles pagination to fetch all accounts a user follows.

        Args:
            user_id: X user ID to fetch following accounts for
            rate_limit_delay: Delay in seconds between paginated requests

        Returns:
            List of all XAccount objects

        Raises:
            XAPIError: If API request fails
        """
        all_accounts: List[XAccount] = []
        next_token: Optional[str] = None

        while True:
            accounts, next_token = await self.get_following(
                user_id, pagination_token=next_token
            )
            all_accounts.extend(accounts)

            if not next_token:
                break

            # Rate limiting: wait between requests
            await asyncio.sleep(rate_limit_delay)

        return all_accounts

    async def get_user_by_username(self, username: str) -> Optional[XAccount]:
        """
        Fetch user information by username.

        Args:
            username: X username (without @ symbol)

        Returns:
            XAccount object or None if user not found

        Raises:
            XAPIError: If API request fails
        """
        url = f"{self.BASE_URL}/users/by/username/{username}"
        params = {
            "user.fields": (
                "id,username,name,description,verified,created_at,"
                "public_metrics,location,url,profile_image_url"
            )
        }

        try:
            response = await self.client.get(url, params=params)
            response.raise_for_status()
        except HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            raise XAPIError(
                f"HTTP {e.response.status_code}: {e.response.text}",
                status_code=e.response.status_code,
            ) from e
        except RequestError as e:
            raise XAPIError(f"Request failed: {str(e)}") from e

        data = response.json()
        user_data = data.get("data")
        if not user_data:
            return None

        return self._parse_account(user_data)

    def _parse_account(self, user_data: dict) -> XAccount:
        """
        Parse API response into XAccount model.

        Args:
            user_data: Raw user data from X API

        Returns:
            XAccount object
        """
        metrics = user_data.get("public_metrics", {})

        return XAccount(
            user_id=user_data["id"],
            username=user_data["username"],
            display_name=user_data["name"],
            bio=user_data.get("description"),
            verified=user_data.get("verified", False),
            created_at=user_data.get("created_at"),
            followers_count=metrics.get("followers_count", 0),
            following_count=metrics.get("following_count", 0),
            tweet_count=metrics.get("tweet_count", 0),
            location=user_data.get("location"),
            website=user_data.get("url"),
            profile_image_url=user_data.get("profile_image_url"),
        )

    async def close(self) -> None:
        """Close the HTTP client connection."""
        await self.client.aclose()

    async def __aenter__(self) -> XAPIClient:
        """Async context manager entry."""
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        """Async context manager exit."""
        await self.close()
