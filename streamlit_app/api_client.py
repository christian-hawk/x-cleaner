"""
HTTP API client for X-Cleaner backend.

Provides async HTTP client for Streamlit to communicate with FastAPI backend,
maintaining proper layer separation (Presentation → API).
"""

import asyncio
from typing import Any, Dict, List, Optional, TypeVar, Coroutine

import httpx
import streamlit as st

# Type variable for run_async return type
T = TypeVar("T")


class XCleanerAPIClient:
    """HTTP client for X-Cleaner FastAPI backend."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize API client.

        Args:
            base_url: Base URL for the FastAPI backend.
        """
        self._base_url = base_url
        self._timeout = httpx.Timeout(30.0, connect=5.0)

    async def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Perform GET request to API.

        Args:
            endpoint: API endpoint path.
            params: Optional query parameters.

        Returns:
            JSON response as dictionary.

        Raises:
            httpx.HTTPError: If request fails.
        """
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.get(
                f"{self._base_url}{endpoint}",
                params=params or {},
            )
            response.raise_for_status()
            json_response: Dict[str, Any] = response.json()
            return json_response

    async def get_all_accounts(
        self,
        category: Optional[str] = None,
        verified_only: bool = False,
        minimum_followers: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve all accounts with optional filtering.

        Args:
            category: Optional category filter.
            verified_only: If True, return only verified accounts.
            minimum_followers: Optional minimum follower count.

        Returns:
            List of account dictionaries.
        """
        params: Dict[str, Any] = {
            "verified_only": verified_only,
        }
        if category:
            params["category"] = category
        if minimum_followers is not None:
            params["minimum_followers"] = minimum_followers

        response = await self._get("/api/accounts", params=params)
        accounts: List[Dict[str, Any]] = response.get("accounts", [])
        return accounts

    async def get_top_accounts(
        self,
        limit: int = 10,
        category: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve top accounts by follower count.

        Args:
            limit: Maximum number of accounts to return.
            category: Optional category filter.

        Returns:
            List of top account dictionaries.
        """
        params: Dict[str, Any] = {"limit": limit}
        if category:
            params["category"] = category

        response = await self._get("/api/accounts/top", params=params)
        accounts: List[Dict[str, Any]] = response.get("accounts", [])
        return accounts

    async def search_accounts(self, query: str) -> List[Dict[str, Any]]:
        """
        Search accounts by username or display name.

        Args:
            query: Search term.

        Returns:
            List of matching account dictionaries.
        """
        params: Dict[str, Any] = {"query": query}
        response = await self._get("/api/accounts/search", params=params)
        accounts: List[Dict[str, Any]] = response.get("results", [])
        return accounts

    async def get_account_by_username(self, username: str) -> Dict[str, Any]:
        """
        Retrieve specific account by username.

        Args:
            username: Account username.

        Returns:
            Account dictionary.

        Raises:
            httpx.HTTPError: If account not found (404).
        """
        return await self._get(f"/api/accounts/{username}")

    async def get_overall_statistics(self) -> Dict[str, Any]:
        """
        Retrieve overall statistics for all accounts.

        Returns:
            Overall statistics dictionary.
        """
        return await self._get("/api/statistics/overall")

    async def get_category_statistics(self) -> List[Dict[str, Any]]:
        """
        Retrieve statistics for each category.

        Returns:
            List of category statistics dictionaries.
        """
        response = await self._get("/api/statistics/categories")
        categories: List[Dict[str, Any]] = response.get("categories", [])
        return categories

    async def get_engagement_metrics(self) -> Dict[str, Any]:
        """
        Retrieve engagement-related metrics.

        Returns:
            Engagement metrics dictionary.
        """
        return await self._get("/api/statistics/engagement")

    async def _post(self, endpoint: str, json_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Perform POST request to API.

        Args:
            endpoint: API endpoint path.
            json_data: Optional JSON data for request body.

        Returns:
            JSON response as dictionary.

        Raises:
            httpx.HTTPError: If request fails.
        """
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.post(
                f"{self._base_url}{endpoint}",
                json=json_data or {},
            )
            response.raise_for_status()
            json_response: Dict[str, Any] = response.json()
            return json_response

    async def start_scan(
        self,
        username: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Start a new scan operation.

        Args:
            username: X username (without @) to scan following accounts for.
            user_id: X user ID to scan following accounts for (alternative to username).

        Returns:
            Scan response with job_id.
        """
        json_data: Dict[str, Any] = {}
        if username:
            json_data["username"] = username
        if user_id:
            json_data["user_id"] = user_id
        return await self._post("/api/scan", json_data=json_data)

    async def get_scan_status(self, job_id: str) -> Dict[str, Any]:
        """
        Get scan status by job ID.

        Args:
            job_id: Job identifier.

        Returns:
            Scan status information.
        """
        return await self._get(f"/api/scan/{job_id}/status")

    async def get_scan_progress(self, job_id: str) -> Dict[str, Any]:
        """
        Get detailed scan progress by job ID.

        Args:
            job_id: Job identifier.

        Returns:
            Detailed progress information.
        """
        return await self._get(f"/api/scan/{job_id}/progress")


# Synchronous wrappers for Streamlit (which doesn't support async directly)

def run_async(coroutine: Coroutine[Any, Any, T]) -> T:
    """
    Run async coroutine synchronously for Streamlit.

    Args:
        coroutine: Async coroutine to execute.

    Returns:
        Coroutine result.
    """
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    return loop.run_until_complete(coroutine)


@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_all_accounts_sync(
    category: Optional[str] = None,
    verified_only: bool = False,
    minimum_followers: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """
    Synchronous wrapper for get_all_accounts.

    Args:
        category: Optional category filter.
        verified_only: If True, return only verified accounts.
        minimum_followers: Optional minimum follower count.

    Returns:
        List of account dictionaries.
    """
    client = XCleanerAPIClient()
    return run_async(
        client.get_all_accounts(
            category=category,
            verified_only=verified_only,
            minimum_followers=minimum_followers,
        )
    )


@st.cache_data(ttl=300)
def get_top_accounts_sync(
    limit: int = 10,
    category: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Synchronous wrapper for get_top_accounts.

    Args:
        limit: Maximum number of accounts to return.
        category: Optional category filter.

    Returns:
        List of top account dictionaries.
    """
    client = XCleanerAPIClient()
    return run_async(client.get_top_accounts(limit=limit, category=category))


@st.cache_data(ttl=300)
def get_overall_statistics_sync() -> Dict[str, Any]:
    """
    Synchronous wrapper for get_overall_statistics.

    Returns:
        Overall statistics dictionary.
    """
    client = XCleanerAPIClient()
    return run_async(client.get_overall_statistics())


@st.cache_data(ttl=300)
def get_category_statistics_sync() -> List[Dict[str, Any]]:
    """
    Synchronous wrapper for get_category_statistics.

    Returns:
        List of category statistics dictionaries.
    """
    client = XCleanerAPIClient()
    return run_async(client.get_category_statistics())


@st.cache_data(ttl=300)
def get_engagement_metrics_sync() -> Dict[str, Any]:
    """
    Synchronous wrapper for get_engagement_metrics.

    Returns:
        Engagement metrics dictionary.
    """
    client = XCleanerAPIClient()
    return run_async(client.get_engagement_metrics())


def search_accounts_sync(query: str) -> List[Dict[str, Any]]:
    """
    Synchronous wrapper for search_accounts (not cached, always fresh).

    Args:
        query: Search term.

    Returns:
        List of matching account dictionaries.
    """
    client = XCleanerAPIClient()
    return run_async(client.search_accounts(query=query))


def start_scan_sync(
    username: Optional[str] = None,
    user_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Synchronous wrapper for start_scan.

    Args:
        username: X username (without @) to scan following accounts for.
        user_id: X user ID to scan following accounts for (alternative to username).

    Returns:
        Scan response with job_id.
    """
    client = XCleanerAPIClient()
    return run_async(client.start_scan(username=username, user_id=user_id))


def get_scan_status_sync(job_id: str) -> Dict[str, Any]:
    """
    Synchronous wrapper for get_scan_status.

    Args:
        job_id: Job identifier.

    Returns:
        Scan status information.
    """
    client = XCleanerAPIClient()
    return run_async(client.get_scan_status(job_id=job_id))


def get_scan_progress_sync(job_id: str) -> Dict[str, Any]:
    """
    Synchronous wrapper for get_scan_progress.

    Args:
        job_id: Job identifier.

    Returns:
        Detailed progress information.
    """
    client = XCleanerAPIClient()
    return run_async(client.get_scan_progress(job_id=job_id))
