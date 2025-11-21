"""
Tests for Grok API Client.

This module contains tests for the GrokClient class, including
category discovery and account categorization.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from backend.api.grok_client import GrokClient, GrokAPIError
from backend.models import XAccount, CategorizedAccount


@pytest.fixture
def sample_accounts():
    """Sample X accounts for testing."""
    return [
        XAccount(
            user_id="1",
            username="techuser",
            display_name="Tech User",
            bio="Software engineer building cool stuff",
            verified=True,
            followers_count=5000,
            following_count=500,
            tweet_count=1000,
        ),
        XAccount(
            user_id="2",
            username="artistuser",
            display_name="Artist User",
            bio="Digital artist creating beautiful art",
            verified=False,
            followers_count=2000,
            following_count=300,
            tweet_count=500,
        ),
    ]


@pytest.fixture
def mock_category_response():
    """Mock category discovery response."""
    return {
        "categories": [
            {
                "name": "Technology & Engineering",
                "description": "Software engineers and tech professionals",
                "characteristics": ["Technical content", "Code sharing", "Tech news"],
                "estimated_percentage": 40,
            },
            {
                "name": "Art & Design",
                "description": "Artists and designers",
                "characteristics": [
                    "Creative content",
                    "Portfolio sharing",
                    "Art discussions",
                ],
                "estimated_percentage": 30,
            },
        ],
        "total_categories": 2,
        "analysis_summary": "A network focused on tech and art",
    }


@pytest.fixture
def mock_categorization_response():
    """Mock account categorization response."""
    return [
        {
            "account_index": 1,
            "category": "Technology & Engineering",
            "confidence": 0.95,
            "reasoning": "Clear tech focus in bio",
            "alternative": None,
        },
        {
            "account_index": 2,
            "category": "Art & Design",
            "confidence": 0.90,
            "reasoning": "Digital artist with portfolio",
            "alternative": None,
        },
    ]


@pytest.mark.asyncio
async def test_discover_categories(sample_accounts, mock_category_response):
    """Test category discovery."""
    import json

    with patch.dict("os.environ", {"XAI_API_KEY": "test_key"}):
        client = GrokClient()

        # Mock OpenAI client response
        mock_choice = MagicMock()
        mock_message = MagicMock()
        mock_message.content = f"```json\n{json.dumps(mock_category_response)}\n```"
        mock_choice.message = mock_message

        mock_completion = MagicMock()
        mock_completion.choices = [mock_choice]

        # Create async mock
        async_mock = AsyncMock()
        async_mock.return_value = mock_completion

        with patch.object(
            client.client.chat.completions,
            "create",
            async_mock,
        ):
            # Execute
            categories = await client._discover_categories(sample_accounts)

            # Assert
            assert "categories" in categories
            assert len(categories["categories"]) == 2
            assert categories["categories"][0]["name"] == "Technology & Engineering"
            assert categories["total_categories"] == 2


@pytest.mark.asyncio
async def test_categorize_batch(
    sample_accounts, mock_category_response, mock_categorization_response
):
    """Test batch categorization."""
    import json

    with patch.dict("os.environ", {"XAI_API_KEY": "test_key"}):
        client = GrokClient()

        # Mock OpenAI client response
        mock_choice = MagicMock()
        mock_message = MagicMock()
        mock_message.content = (
            f"```json\n{json.dumps(mock_categorization_response)}\n```"
        )
        mock_choice.message = mock_message

        mock_completion = MagicMock()
        mock_completion.choices = [mock_choice]

        category_names = [cat["name"] for cat in mock_category_response["categories"]]

        # Create async mock
        async_mock = AsyncMock()
        async_mock.return_value = mock_completion

        with patch.object(
            client.client.chat.completions,
            "create",
            async_mock,
        ):
            # Execute
            categorized = await client._categorize_batch(
                sample_accounts, category_names, mock_category_response
            )

            # Assert
            assert len(categorized) == 2
            assert isinstance(categorized[0], CategorizedAccount)
            assert categorized[0].category == "Technology & Engineering"
            assert categorized[0].confidence == 0.95
            assert categorized[1].category == "Art & Design"
            assert categorized[1].confidence == 0.90


@pytest.mark.asyncio
async def test_extract_json_with_markdown():
    """Test JSON extraction from markdown code blocks."""
    with patch.dict("os.environ", {"XAI_API_KEY": "test_key"}):
        client = GrokClient()

        # Test with markdown
        response = '```json\n{"test": "value"}\n```'
        result = client._extract_json(response)
        assert result["test"] == "value"

        # Test without markdown
        response = '{"test": "value2"}'
        result = client._extract_json(response)
        assert result["test"] == "value2"


@pytest.mark.asyncio
async def test_extract_json_error():
    """Test JSON extraction error handling."""
    with patch.dict("os.environ", {"XAI_API_KEY": "test_key"}):
        client = GrokClient()

        # Test with invalid JSON
        with pytest.raises(GrokAPIError) as exc_info:
            client._extract_json("invalid json {")

        assert "Failed to parse JSON" in str(exc_info.value)


def test_missing_api_key():
    """Test error when API key is missing."""
    with patch.dict("os.environ", {}, clear=True):
        with pytest.raises(ValueError) as exc_info:
            GrokClient()

        assert "API key" in str(exc_info.value)


@pytest.mark.asyncio
async def test_analyze_and_categorize_full_flow(
    sample_accounts, mock_category_response, mock_categorization_response
):
    """Test full analyze and categorize flow."""
    import json

    with patch.dict("os.environ", {"XAI_API_KEY": "test_key"}):
        client = GrokClient()

        # Track call count to return different responses
        call_count = {"count": 0}

        async def mock_create(*args, **kwargs):
            """Mock create method that returns different responses."""
            call_count["count"] += 1

            mock_choice = MagicMock()
            mock_message = MagicMock()

            # First call is discovery
            if call_count["count"] == 1:
                mock_message.content = (
                    f"```json\n{json.dumps(mock_category_response)}\n```"
                )
            # Subsequent calls are categorization
            else:
                mock_message.content = (
                    f"```json\n{json.dumps(mock_categorization_response)}\n```"
                )

            mock_choice.message = mock_message
            mock_completion = MagicMock()
            mock_completion.choices = [mock_choice]

            return mock_completion

        # Create async mock with side effect
        async_mock = AsyncMock(side_effect=mock_create)

        with patch.object(
            client.client.chat.completions,
            "create",
            async_mock,
        ):
            # Execute
            categories, categorized = await client.analyze_and_categorize(sample_accounts)

        # Assert
        assert "categories" in categories
        assert len(categorized) == 2
        assert isinstance(categorized[0], CategorizedAccount)
        assert client.discovered_categories is not None
