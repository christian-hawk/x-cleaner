"""
Tests for X API Client.

This module contains tests for the XAPIClient class, including
mocked API responses and error handling.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from backend.api.x_client import XAPIClient, XAPIError
from backend.models import XAccount


@pytest.fixture
def mock_response_data():
    """Mock X API response data."""
    return {
        "data": [
            {
                "id": "123456",
                "username": "testuser",
                "name": "Test User",
                "description": "Test bio",
                "verified": True,
                "created_at": "2020-01-01T00:00:00.000Z",
                "public_metrics": {
                    "followers_count": 1000,
                    "following_count": 500,
                    "tweet_count": 2000,
                },
                "location": "Test City",
                "url": "https://example.com",
                "profile_image_url": "https://example.com/image.jpg",
            }
        ],
        "meta": {"next_token": "next_page_token"},
    }


@pytest.mark.asyncio
async def test_get_following_success(mock_response_data):
    """Test successful get_following request."""
    with patch.dict("os.environ", {"X_API_BEARER_TOKEN": "test_token"}):
        client = XAPIClient()

        # Mock the HTTP client
        mock_response = MagicMock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status = MagicMock()

        client.client.get = AsyncMock(return_value=mock_response)

        # Execute
        accounts, next_token = await client.get_following("test_user_id")

        # Assert
        assert len(accounts) == 1
        assert isinstance(accounts[0], XAccount)
        assert accounts[0].username == "testuser"
        assert accounts[0].display_name == "Test User"
        assert accounts[0].followers_count == 1000
        assert next_token == "next_page_token"

        await client.close()


@pytest.mark.asyncio
async def test_get_following_rate_limit():
    """Test rate limit error handling."""
    with patch.dict("os.environ", {"X_API_BEARER_TOKEN": "test_token"}):
        client = XAPIClient()

        # Mock rate limit error
        from httpx import HTTPStatusError, Response, Request

        mock_response = Response(
            status_code=429,
            headers={"x-rate-limit-reset": "1234567890"},
            request=Request("GET", "http://test.com"),
        )
        client.client.get = AsyncMock(
            side_effect=HTTPStatusError(
                "Rate limit", request=mock_response.request, response=mock_response
            )
        )

        # Execute and assert
        with pytest.raises(XAPIError) as exc_info:
            await client.get_following("test_user_id")

        assert exc_info.value.status_code == 429
        assert "Rate limit" in str(exc_info.value)

        await client.close()


@pytest.mark.asyncio
async def test_parse_account():
    """Test account parsing from API response."""
    with patch.dict("os.environ", {"X_API_BEARER_TOKEN": "test_token"}):
        client = XAPIClient()

        user_data = {
            "id": "123",
            "username": "testuser",
            "name": "Test User",
            "description": "Bio text",
            "verified": True,
            "created_at": "2020-01-01T00:00:00.000Z",
            "public_metrics": {
                "followers_count": 1000,
                "following_count": 500,
                "tweet_count": 2000,
            },
        }

        account = client._parse_account(user_data)

        assert isinstance(account, XAccount)
        assert account.user_id == "123"
        assert account.username == "testuser"
        assert account.display_name == "Test User"
        assert account.bio == "Bio text"
        assert account.verified is True
        assert account.followers_count == 1000

        await client.close()


def test_missing_bearer_token():
    """Test error when bearer token is missing."""
    with patch.dict("os.environ", {}, clear=True):
        with pytest.raises(ValueError) as exc_info:
            XAPIClient()

        assert "Bearer Token" in str(exc_info.value)
