"""
Utility functions for Streamlit dashboard.

This module provides helper functions for data processing, formatting,
and common operations across the dashboard.
"""

import json
from datetime import datetime
from typing import Any, Dict, List

import pandas as pd
import streamlit as st
from backend.database import DatabaseManager
from backend.models import CategorizedAccount


@st.cache_resource
def get_database() -> DatabaseManager:
    """
    Get cached database connection.

    Returns:
        DatabaseManager instance
    """
    return DatabaseManager()


@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_all_accounts() -> List[CategorizedAccount]:
    """
    Load all accounts from database with caching.

    Returns:
        List of all categorized accounts
    """
    db = get_database()
    return db.get_all_accounts()


@st.cache_data(ttl=300)
def load_categories() -> List[Dict[str, Any]]:
    """
    Load all categories with caching.

    Returns:
        List of category dictionaries
    """
    db = get_database()
    return db.get_categories()


def accounts_to_dataframe(accounts: List[CategorizedAccount]) -> pd.DataFrame:
    """
    Convert list of accounts to pandas DataFrame.

    Args:
        accounts: List of CategorizedAccount objects

    Returns:
        DataFrame with account data
    """
    if not accounts:
        return pd.DataFrame()

    data = []
    for account in accounts:
        data.append({
            'user_id': account.user_id,
            'username': account.username,
            'display_name': account.display_name,
            'bio': account.bio or '',
            'verified': account.verified,
            'followers_count': account.followers_count,
            'following_count': account.following_count,
            'tweet_count': account.tweet_count,
            'location': account.location or '',
            'website': account.website or '',
            'category': account.category,
            'confidence': account.confidence,
            'reasoning': account.reasoning or '',
        })

    return pd.DataFrame(data)


def calculate_category_stats(accounts: List[CategorizedAccount]) -> pd.DataFrame:
    """
    Calculate statistics for each category.

    Args:
        accounts: List of categorized accounts

    Returns:
        DataFrame with category statistics
    """
    if not accounts:
        return pd.DataFrame()

    df = accounts_to_dataframe(accounts)

    stats = df.groupby('category').agg({
        'user_id': 'count',
        'followers_count': 'mean',
        'verified': lambda x: (x.sum() / len(x) * 100)  # Verification rate as percentage
    }).reset_index()

    stats.columns = ['Category', 'Account Count', 'Avg Followers', 'Verification Rate (%)']

    # Calculate percentage of total
    total_accounts = len(df)
    stats['Percentage'] = (stats['Account Count'] / total_accounts * 100).round(2)

    # Round numeric columns
    stats['Avg Followers'] = stats['Avg Followers'].round(0).astype(int)
    stats['Verification Rate (%)'] = stats['Verification Rate (%)'].round(1)

    # Sort by account count descending
    stats = stats.sort_values('Account Count', ascending=False)

    return stats


def format_number(num: int) -> str:
    """
    Format large numbers with K, M suffixes.

    Args:
        num: Number to format

    Returns:
        Formatted string (e.g., "1.2K", "2.5M")
    """
    if num >= 1_000_000:
        return f"{num / 1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num / 1_000:.1f}K"
    else:
        return str(num)


def export_to_json(accounts: List[CategorizedAccount]) -> str:
    """
    Export accounts to JSON string.

    Args:
        accounts: List of accounts to export

    Returns:
        JSON string
    """
    data = {
        'export_date': datetime.now().isoformat(),
        'total_accounts': len(accounts),
        'accounts': [
            {
                'user_id': acc.user_id,
                'username': acc.username,
                'display_name': acc.display_name,
                'bio': acc.bio,
                'verified': acc.verified,
                'followers_count': acc.followers_count,
                'following_count': acc.following_count,
                'tweet_count': acc.tweet_count,
                'location': acc.location,
                'website': acc.website,
                'category': acc.category,
                'confidence': acc.confidence,
                'reasoning': acc.reasoning,
            }
            for acc in accounts
        ]
    }
    return json.dumps(data, indent=2)


def export_to_csv(accounts: List[CategorizedAccount]) -> str:
    """
    Export accounts to CSV string.

    Args:
        accounts: List of accounts to export

    Returns:
        CSV string
    """
    df = accounts_to_dataframe(accounts)
    return df.to_csv(index=False)


def get_top_accounts_by_category(
    accounts: List[CategorizedAccount],
    category: str,
    n: int = 5
) -> List[CategorizedAccount]:
    """
    Get top N accounts in a category by follower count.

    Args:
        accounts: List of all accounts
        category: Category name
        n: Number of top accounts to return

    Returns:
        List of top accounts
    """
    category_accounts = [acc for acc in accounts if acc.category == category]
    category_accounts.sort(key=lambda x: x.followers_count, reverse=True)
    return category_accounts[:n]


def format_account_card(account: CategorizedAccount) -> str:
    """
    Format account information as a markdown card.

    Args:
        account: Account to format

    Returns:
        Markdown string
    """
    verified_badge = "✓ " if account.verified else ""
    followers_fmt = format_number(account.followers_count)
    following_fmt = format_number(account.following_count)
    tweets_fmt = format_number(account.tweet_count)

    bio = account.bio[:100] + "..." if account.bio and len(account.bio) > 100 else account.bio or "No bio"

    card = f"""
    **@{account.username}** {verified_badge}
    {account.display_name}

    {bio}

    👥 {followers_fmt} followers • {following_fmt} following • {tweets_fmt} tweets
    """

    if account.location:
        card += f"\n📍 {account.location}"

    if account.website:
        card += f"\n🔗 {account.website}"

    return card


def get_overall_stats(accounts: List[CategorizedAccount]) -> Dict[str, Any]:
    """
    Calculate overall statistics.

    Args:
        accounts: List of all accounts

    Returns:
        Dictionary of overall statistics
    """
    if not accounts:
        return {
            'total_accounts': 0,
            'total_categories': 0,
            'verified_count': 0,
            'verification_rate': 0.0,
            'avg_followers': 0,
            'avg_following': 0,
            'avg_tweets': 0,
            'total_followers': 0,
            'most_popular_category': None,
        }

    df = accounts_to_dataframe(accounts)

    return {
        'total_accounts': len(accounts),
        'total_categories': df['category'].nunique(),
        'verified_count': df['verified'].sum(),
        'verification_rate': (df['verified'].sum() / len(df) * 100),
        'avg_followers': int(df['followers_count'].mean()),
        'avg_following': int(df['following_count'].mean()),
        'avg_tweets': int(df['tweet_count'].mean()),
        'total_followers': int(df['followers_count'].sum()),
        'most_popular_category': df['category'].mode()[0] if len(df) > 0 else None,
    }
