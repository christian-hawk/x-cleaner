"""
Grok API Client for AI-powered account categorization.

This module provides a client for the xAI Grok API, implementing
emergent categorization through a two-phase approach.
"""

import json
import os
from typing import Dict, List, Optional, Tuple

from openai import AsyncOpenAI
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from ..models import CategorizedAccount, XAccount


class GrokAPIError(Exception):
    """Custom exception for Grok API errors."""

    pass


class GrokClient:
    """
    Client for xAI Grok API with emergent categorization.

    Implements a two-phase categorization approach:
    1. Discovery: Analyze accounts to discover natural categories
    2. Categorization: Assign accounts to discovered categories
    """

    DEFAULT_MODEL = "grok-beta"
    DISCOVERY_SAMPLE_SIZE = 200
    CATEGORIZATION_BATCH_SIZE = 50

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Grok API client.

        Args:
            api_key: xAI API key. If not provided, reads from
                    XAI_API_KEY environment variable.

        Raises:
            ValueError: If API key is not provided or found in environment
        """
        self.api_key = api_key or os.getenv("XAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "xAI API key not provided. Set XAI_API_KEY environment "
                "variable or pass api_key parameter."
            )

        self.client = AsyncOpenAI(
            api_key=self.api_key, base_url="https://api.x.ai/v1"
        )
        self.discovered_categories: Optional[Dict] = None

    async def analyze_and_categorize(
        self, accounts: List[XAccount], sample_size: Optional[int] = None
    ) -> Tuple[Dict, List[CategorizedAccount]]:
        """
        Two-phase categorization process.

        Phase 1: Discover natural categories from a sample of accounts
        Phase 2: Categorize all accounts using discovered categories

        Args:
            accounts: List of X accounts to categorize
            sample_size: Number of accounts to use for category discovery
                        (defaults to DISCOVERY_SAMPLE_SIZE)

        Returns:
            Tuple of (category_metadata, categorized_accounts)

        Raises:
            GrokAPIError: If API request fails
        """
        if not accounts:
            raise ValueError("No accounts provided for categorization")

        sample_size = sample_size or self.DISCOVERY_SAMPLE_SIZE

        # Phase 1: Discover categories from sample
        sample = accounts[:sample_size] if len(accounts) > sample_size else accounts
        categories = await self._discover_categories(sample)
        self.discovered_categories = categories

        # Phase 2: Categorize all accounts
        categorized = await self._categorize_with_discovered(accounts, categories)

        return categories, categorized

    @retry(
        retry=retry_if_exception_type(GrokAPIError),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    async def _discover_categories(self, sample_accounts: List[XAccount]) -> Dict:
        """
        Phase 1: Discover natural categories from account data.

        Implements retry logic with exponential backoff for API resilience.

        Args:
            sample_accounts: Sample of accounts for category discovery

        Returns:
            Dictionary containing discovered categories and metadata

        Raises:
            GrokAPIError: If API request fails after retries
        """
        # Build account summaries
        accounts_summary = []
        for account in sample_accounts[:100]:  # First 100 for prompt
            summary = f"@{account.username}: {account.bio or 'No bio'} "
            summary += f"({account.followers_count:,} followers)"
            accounts_summary.append(summary)

        prompt = f"""You are an expert at analyzing social media networks and identifying natural community patterns.

I have {len(sample_accounts)} X (Twitter) accounts. Analyze them and discover 10-20 natural categories based on actual patterns in the data.

Accounts summary (username: bio, followers):
{chr(10).join(accounts_summary)}
... and {len(sample_accounts) - 100} more accounts

Your task:
1. Identify natural groupings and communities
2. Create 10-20 descriptive category names
3. Explain key characteristics of each category
4. Estimate the percentage of accounts in each

DO NOT use predefined categories. Discover what's actually in THIS network.

Respond with JSON:
{{
  "categories": [
    {{
      "name": "Descriptive Category Name",
      "description": "What defines this category",
      "characteristics": ["trait 1", "trait 2", "trait 3"],
      "estimated_percentage": 15
    }}
  ],
  "total_categories": 12,
  "analysis_summary": "Brief overview of the network"
}}"""

        try:
            response = await self.client.chat.completions.create(
                model=self.DEFAULT_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a social network analysis expert who "
                            "discovers natural patterns in data."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
            )

            result_text = response.choices[0].message.content
            if not result_text:
                raise GrokAPIError("Empty response from Grok API")

            categories_data = self._extract_json(result_text)
            return categories_data

        except Exception as e:
            raise GrokAPIError(f"Category discovery failed: {str(e)}") from e

    async def _categorize_with_discovered(
        self, accounts: List[XAccount], categories: Dict
    ) -> List[CategorizedAccount]:
        """
        Phase 2: Categorize accounts using discovered categories.

        Args:
            accounts: All accounts to categorize
            categories: Discovered categories from Phase 1

        Returns:
            List of categorized accounts

        Raises:
            GrokAPIError: If categorization fails
        """
        categorized: List[CategorizedAccount] = []
        category_names = [cat["name"] for cat in categories["categories"]]

        # Process in batches
        batch_size = self.CATEGORIZATION_BATCH_SIZE
        for i in range(0, len(accounts), batch_size):
            batch = accounts[i : i + batch_size]
            batch_results = await self._categorize_batch(
                batch, category_names, categories
            )
            categorized.extend(batch_results)

        return categorized

    @retry(
        retry=retry_if_exception_type(GrokAPIError),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    async def _categorize_batch(
        self,
        accounts: List[XAccount],
        category_names: List[str],
        categories_metadata: Dict,
    ) -> List[CategorizedAccount]:
        """
        Categorize a batch of accounts.

        Implements retry logic with exponential backoff for API resilience.

        Args:
            accounts: Batch of accounts to categorize
            category_names: List of discovered category names
            categories_metadata: Full category metadata

        Returns:
            List of categorized accounts

        Raises:
            GrokAPIError: If API request fails after retries
        """
        # Build account details
        accounts_info = []
        for idx, account in enumerate(accounts):
            info = f"""
{idx + 1}. @{account.username} ({account.display_name})
   Bio: {account.bio or 'N/A'}
   Followers: {account.followers_count:,} | Following: {account.following_count:,}
   Verified: {account.verified} | Tweets: {account.tweet_count:,}
"""
            accounts_info.append(info)

        prompt = f"""Categorize these X accounts using the discovered category system.

Available categories:
{', '.join(category_names)}

Category descriptions:
{json.dumps([{c['name']: c['description']} for c in categories_metadata['categories']], indent=2)}

Accounts to categorize:
{''.join(accounts_info)}

For each account, provide:
- Primary category (must be from the list above)
- Confidence (0.0 to 1.0)
- Brief reasoning
- Alternative category if confidence < 0.8

Respond as JSON array:
[
  {{
    "account_index": 1,
    "category": "Category Name",
    "confidence": 0.95,
    "reasoning": "Why this category fits",
    "alternative": null
  }}
]"""

        try:
            response = await self.client.chat.completions.create(
                model=self.DEFAULT_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You categorize accounts accurately based on "
                            "discovered patterns."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
            )

            result_text = response.choices[0].message.content
            if not result_text:
                raise GrokAPIError("Empty response from Grok API")

            categorizations = self._extract_json(result_text)

            # Convert to CategorizedAccount objects
            categorized_accounts = []
            for account, cat_data in zip(accounts, categorizations):
                categorized_accounts.append(
                    CategorizedAccount(
                        **account.model_dump(),
                        category=cat_data["category"],
                        confidence=cat_data["confidence"],
                        reasoning=cat_data.get("reasoning"),
                    )
                )

            return categorized_accounts

        except Exception as e:
            raise GrokAPIError(f"Batch categorization failed: {str(e)}") from e

    def _extract_json(self, response_text: str) -> Dict:
        """
        Extract JSON from response (handles markdown formatting).

        Args:
            response_text: Raw response text from Grok API

        Returns:
            Parsed JSON dictionary

        Raises:
            GrokAPIError: If JSON parsing fails
        """
        try:
            # Handle markdown code blocks
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]

            return json.loads(response_text.strip())
        except (json.JSONDecodeError, IndexError) as e:
            raise GrokAPIError(f"Failed to parse JSON response: {str(e)}") from e

    def get_discovered_categories(self) -> Optional[Dict]:
        """
        Get the currently discovered categories.

        Returns:
            Dictionary of discovered categories or None if not yet discovered
        """
        return self.discovered_categories
