"""
Utility functions for Streamlit dashboard.

This module provides helper functions for data processing, formatting,
and common operations across the dashboard. Uses API client for data access
following proper layer separation.
"""

import json
from datetime import datetime
from typing import Any, Dict, List

import pandas as pd

from streamlit_app.api_client import (
    get_all_accounts_sync,
    get_category_statistics_sync,
    get_overall_statistics_sync,
    get_top_accounts_sync,
)


def load_all_accounts() -> List[Dict[str, Any]]:
    """
    Load all accounts from API.

    Returns:
        List of account dictionaries from API.
    """
    return get_all_accounts_sync()


def load_overall_statistics() -> Dict[str, Any]:
    """
    Load overall statistics from API.

    Returns:
        Overall statistics dictionary.
    """
    return get_overall_statistics_sync()


def load_category_statistics() -> List[Dict[str, Any]]:
    """
    Load category statistics from API.

    Returns:
        List of category statistics dictionaries.
    """
    return get_category_statistics_sync()


def accounts_to_dataframe(accounts: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Convert list of account dictionaries to pandas DataFrame.

    Args:
        accounts: List of account dictionaries.

    Returns:
        DataFrame with account data.
    """
    if not accounts:
        return pd.DataFrame()

    return pd.DataFrame(accounts)


def category_stats_to_dataframe(
    category_stats: List[Dict[str, Any]]
) -> pd.DataFrame:
    """
    Convert category statistics to DataFrame.

    Args:
        category_stats: List of category statistics dictionaries.

    Returns:
        DataFrame with category statistics.
    """
    if not category_stats:
        return pd.DataFrame()

    dataframe = pd.DataFrame(category_stats)

    # Rename columns for display
    column_mapping = {
        "category": "Category",
        "account_count": "Account Count",
        "percentage": "Percentage",
        "avg_followers": "Avg Followers",
        "verification_rate": "Verification Rate (%)",
    }

    dataframe = dataframe.rename(columns=column_mapping)

    # Round numeric columns
    if "Avg Followers" in dataframe.columns:
        dataframe["Avg Followers"] = dataframe["Avg Followers"].round(0).astype(int)
    if "Verification Rate (%)" in dataframe.columns:
        dataframe["Verification Rate (%)"] = dataframe["Verification Rate (%)"].round(1)
    if "Percentage" in dataframe.columns:
        dataframe["Percentage"] = dataframe["Percentage"].round(2)

    return dataframe


def format_number(number: int) -> str:
    """
    Format large numbers with K, M suffixes.

    Args:
        number: Number to format.

    Returns:
        Formatted string (e.g., "1.2K", "2.5M").
    """
    if number >= 1_000_000:
        return f"{number / 1_000_000:.1f}M"
    elif number >= 1_000:
        return f"{number / 1_000:.1f}K"
    else:
        return str(number)


def export_to_json(accounts: List[Dict[str, Any]]) -> str:
    """
    Export accounts to JSON string.

    Args:
        accounts: List of account dictionaries to export.

    Returns:
        JSON string.
    """
    data = {
        "export_date": datetime.now().isoformat(),
        "total_accounts": len(accounts),
        "accounts": accounts,
    }
    return json.dumps(data, indent=2)


def export_to_csv(accounts: List[Dict[str, Any]]) -> str:
    """
    Export accounts to CSV string.

    Args:
        accounts: List of account dictionaries to export.

    Returns:
        CSV string.
    """
    dataframe = accounts_to_dataframe(accounts)
    csv_string: str = dataframe.to_csv(index=False)
    return csv_string


def get_top_accounts_by_category(
    category: str,
    limit: int = 5
) -> List[Dict[str, Any]]:
    """
    Get top N accounts in a category by follower count.

    Args:
        category: Category name.
        limit: Number of top accounts to return.

    Returns:
        List of top account dictionaries.
    """
    return get_top_accounts_sync(limit=limit, category=category)


def format_account_card(account: Dict[str, Any]) -> str:
    """
    Format account information as a markdown card.

    Args:
        account: Account dictionary to format.

    Returns:
        Markdown string.
    """
    verified_badge = "✓ " if account.get("verified", False) else ""
    followers_formatted = format_number(account.get("followers_count", 0))
    following_formatted = format_number(account.get("following_count", 0))
    tweets_formatted = format_number(account.get("tweet_count", 0))

    bio = account.get("bio", "") or "No bio"
    if len(bio) > 100:
        bio = bio[:100] + "..."

    card = f"""
    **@{account.get('username', 'unknown')}** {verified_badge}
    {account.get('display_name', '')}

    {bio}

    👥 {followers_formatted} followers • {following_formatted} following • {tweets_formatted} tweets
    """

    location = account.get("location")
    if location:
        card += f"\n📍 {location}"

    website = account.get("website")
    if website:
        card += f"\n🔗 {website}"

    return card


def calculate_category_stats(accounts: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Calculate statistics for each category from account list.

    This is a local calculation alternative to the API endpoint.
    Prefer using load_category_statistics() for API-based stats.

    Args:
        accounts: List of account dictionaries.

    Returns:
        DataFrame with category statistics.
    """
    if not accounts:
        return pd.DataFrame()

    dataframe = accounts_to_dataframe(accounts)

    statistics = dataframe.groupby("category").agg({
        "user_id": "count",
        "followers_count": "mean",
        "verified": lambda verified_values: (verified_values.sum() / len(verified_values) * 100)
    }).reset_index()

    statistics.columns = [
        "Category",
        "Account Count",
        "Avg Followers",
        "Verification Rate (%)"
    ]

    # Calculate percentage of total
    total_accounts = len(dataframe)
    statistics["Percentage"] = (
        statistics["Account Count"] / total_accounts * 100
    ).round(2)

    # Round numeric columns
    statistics["Avg Followers"] = statistics["Avg Followers"].round(0).astype(int)
    statistics["Verification Rate (%)"] = statistics["Verification Rate (%)"].round(1)

    # Sort by account count descending
    statistics = statistics.sort_values("Account Count", ascending=False)

    return statistics


def get_overall_stats(accounts: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate overall statistics from account list.

    This is a local calculation alternative to the API endpoint.
    Prefer using load_overall_statistics() for API-based stats.

    Args:
        accounts: List of account dictionaries.

    Returns:
        Dictionary of overall statistics.
    """
    if not accounts:
        return {
            "total_accounts": 0,
            "total_categories": 0,
            "verified_count": 0,
            "verification_rate": 0.0,
            "avg_followers": 0,
            "avg_following": 0,
            "avg_tweets": 0,
            "total_followers": 0,
            "most_popular_category": None,
        }

    dataframe = accounts_to_dataframe(accounts)

    return {
        "total_accounts": len(accounts),
        "total_categories": dataframe["category"].nunique(),
        "verified_count": int(dataframe["verified"].sum()),
        "verification_rate": (dataframe["verified"].sum() / len(dataframe) * 100),
        "avg_followers": int(dataframe["followers_count"].mean()),
        "avg_following": int(dataframe["following_count"].mean()),
        "avg_tweets": int(dataframe["tweet_count"].mean()),
        "total_followers": int(dataframe["followers_count"].sum()),
        "most_popular_category": (
            dataframe["category"].mode()[0] if len(dataframe) > 0 else None
        ),
    }
