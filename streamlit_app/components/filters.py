"""
Filter components for Streamlit dashboard.

This module provides reusable filter components for account browsing.
"""

from typing import List, Tuple

import pandas as pd
import streamlit as st


def account_search_filters(
    accounts_df: pd.DataFrame,
    categories: List[str]
) -> Tuple[pd.DataFrame, dict]:
    """
    Render account search and filter controls.

    Args:
        accounts_df: DataFrame with all accounts
        categories: List of available categories

    Returns:
        Tuple of (filtered_df, filter_info)
    """
    st.subheader("🔍 Search & Filter")

    col1, col2 = st.columns(2)

    with col1:
        # Text search
        search_term = st.text_input(
            "Search by username, name, or bio",
            placeholder="Type to search...",
            help="Search across username, display name, and bio"
        )

        # Category filter
        selected_categories = st.multiselect(
            "Filter by Category",
            options=["All"] + sorted(categories),
            default=["All"]
        )

    with col2:
        # Verified filter
        verified_filter = st.selectbox(
            "Verified Status",
            options=["All", "Verified Only", "Not Verified"]
        )

        # Follower count range
        if not accounts_df.empty:
            min_followers = int(accounts_df['followers_count'].min())
            max_followers = int(accounts_df['followers_count'].max())

            follower_range = st.slider(
                "Follower Count Range",
                min_value=min_followers,
                max_value=max_followers,
                value=(min_followers, max_followers),
                format="%d"
            )
        else:
            follower_range = (0, 0)

    # Apply filters
    filtered_df = accounts_df.copy()

    # Text search
    if search_term:
        search_lower = search_term.lower()
        filtered_df = filtered_df[
            filtered_df['username'].str.lower().str.contains(search_lower, na=False) |
            filtered_df['display_name'].str.lower().str.contains(search_lower, na=False) |
            filtered_df['bio'].str.lower().str.contains(search_lower, na=False)
        ]

    # Category filter
    if "All" not in selected_categories:
        filtered_df = filtered_df[filtered_df['category'].isin(selected_categories)]

    # Verified filter
    if verified_filter == "Verified Only":
        filtered_df = filtered_df[filtered_df['verified'].astype(bool)]
    elif verified_filter == "Not Verified":
        filtered_df = filtered_df[~filtered_df['verified'].astype(bool)]

    # Follower range filter
    filtered_df = filtered_df[
        (filtered_df['followers_count'] >= follower_range[0]) &
        (filtered_df['followers_count'] <= follower_range[1])
    ]

    filter_info = {
        'search_term': search_term,
        'categories': selected_categories,
        'verified_filter': verified_filter,
        'follower_range': follower_range,
        'total_results': len(filtered_df),
        'total_accounts': len(accounts_df)
    }

    return filtered_df, filter_info


def sort_controls(df: pd.DataFrame) -> pd.DataFrame:
    """
    Render sort controls and return sorted DataFrame.

    Args:
        df: DataFrame to sort

    Returns:
        Sorted DataFrame
    """
    col1, _ = st.columns([3, 1])

    with col1:
        sort_by = st.selectbox(
            "Sort by",
            options=[
                "Followers (High to Low)",
                "Followers (Low to High)",
                "Following (High to Low)",
                "Following (Low to High)",
                "Tweets (High to Low)",
                "Tweets (Low to High)",
                "Username (A-Z)",
                "Username (Z-A)",
                "Confidence (High to Low)",
                "Confidence (Low to High)"
            ],
            index=0
        )

    # Apply sorting
    if "Followers" in sort_by:
        ascending = "Low to High" in sort_by
        return df.sort_values('followers_count', ascending=ascending)
    if "Following" in sort_by:
        ascending = "Low to High" in sort_by
        return df.sort_values('following_count', ascending=ascending)
    if "Tweets" in sort_by:
        ascending = "Low to High" in sort_by
        return df.sort_values('tweet_count', ascending=ascending)
    if "Username" in sort_by:
        ascending = "A-Z" in sort_by
        return df.sort_values('username', ascending=ascending)
    if "Confidence" in sort_by:
        ascending = "Low to High" in sort_by
        return df.sort_values('confidence', ascending=ascending)

    return df


def pagination_controls(
    total_items: int,
    items_per_page: int = 20
) -> Tuple[int, int]:
    """
    Render pagination controls.

    Args:
        total_items: Total number of items
        items_per_page: Number of items per page

    Returns:
        Tuple of (start_index, end_index)
    """
    if total_items == 0:
        return 0, 0

    total_pages = (total_items - 1) // items_per_page + 1

    _, col2, _ = st.columns([2, 1, 2])

    with col2:
        page = st.number_input(
            f"Page (1-{total_pages})",
            min_value=1,
            max_value=total_pages,
            value=1,
            step=1
        )

    start_idx = (page - 1) * items_per_page
    end_idx = min(start_idx + items_per_page, total_items)

    st.caption(f"Showing {start_idx + 1}-{end_idx} of {total_items}")

    return start_idx, end_idx


def confidence_filter(accounts_df: pd.DataFrame, min_confidence: float = 0.0) -> pd.DataFrame:
    """
    Filter accounts by confidence score.

    Args:
        accounts_df: DataFrame with accounts
        min_confidence: Minimum confidence threshold

    Returns:
        Filtered DataFrame
    """
    confidence_threshold = st.slider(
        "Minimum Confidence Score",
        min_value=0.0,
        max_value=1.0,
        value=min_confidence,
        step=0.05,
        help="Filter accounts by categorization confidence"
    )

    filtered_df = accounts_df[accounts_df['confidence'] >= confidence_threshold]

    st.caption(f"Showing {len(filtered_df)} accounts with confidence ≥ {confidence_threshold:.0%}")

    return filtered_df
