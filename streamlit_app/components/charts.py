"""
Chart components for Streamlit dashboard.

This module provides reusable chart components using Plotly.
"""

from typing import List

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from backend.models import CategorizedAccount


def category_distribution_pie_chart(category_stats: pd.DataFrame) -> go.Figure:
    """
    Create pie chart for category distribution.

    Args:
        category_stats: DataFrame with category statistics

    Returns:
        Plotly figure
    """
    if category_stats.empty:
        return go.Figure()

    fig = px.pie(
        category_stats,
        values='Account Count',
        names='Category',
        title='Category Distribution',
        hole=0.4,  # Donut chart
        color_discrete_sequence=px.colors.qualitative.Set3
    )

    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Accounts: %{value}<br>Percentage: %{percent}<extra></extra>'
    )

    fig.update_layout(
        showlegend=True,
        height=500,
        margin=dict(t=50, l=0, r=0, b=0)
    )

    return fig


def category_distribution_bar_chart(category_stats: pd.DataFrame) -> go.Figure:
    """
    Create horizontal bar chart for category distribution.

    Args:
        category_stats: DataFrame with category statistics

    Returns:
        Plotly figure
    """
    if category_stats.empty:
        return go.Figure()

    fig = px.bar(
        category_stats,
        x='Account Count',
        y='Category',
        orientation='h',
        title='Accounts per Category',
        color='Account Count',
        color_continuous_scale='Blues',
        text='Account Count'
    )

    fig.update_traces(
        texttemplate='%{text}',
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Accounts: %{x}<extra></extra>'
    )

    fig.update_layout(
        height=max(400, len(category_stats) * 40),
        showlegend=False,
        yaxis={'categoryorder': 'total ascending'},
        margin=dict(t=50, l=200, r=50, b=50)
    )

    return fig


def followers_distribution_box_plot(accounts_df: pd.DataFrame) -> go.Figure:
    """
    Create box plot showing follower distribution by category.

    Args:
        accounts_df: DataFrame with account data

    Returns:
        Plotly figure
    """
    if accounts_df.empty:
        return go.Figure()

    # Filter out extreme outliers for better visualization
    q1 = accounts_df['followers_count'].quantile(0.25)
    q3 = accounts_df['followers_count'].quantile(0.75)
    iqr = q3 - q1
    upper_bound = q3 + 3 * iqr

    filtered_df = accounts_df[accounts_df['followers_count'] <= upper_bound]

    fig = px.box(
        filtered_df,
        x='category',
        y='followers_count',
        title='Follower Count Distribution by Category',
        color='category',
        labels={'followers_count': 'Followers', 'category': 'Category'}
    )

    fig.update_layout(
        height=500,
        showlegend=False,
        xaxis_tickangle=-45,
        margin=dict(t=50, l=50, r=50, b=150)
    )

    return fig


def verification_rate_chart(category_stats: pd.DataFrame) -> go.Figure:
    """
    Create bar chart for verification rate by category.

    Args:
        category_stats: DataFrame with category statistics

    Returns:
        Plotly figure
    """
    if category_stats.empty:
        return go.Figure()

    fig = px.bar(
        category_stats,
        x='Category',
        y='Verification Rate (%)',
        title='Verification Rate by Category',
        color='Verification Rate (%)',
        color_continuous_scale='Greens',
        text='Verification Rate (%)'
    )

    fig.update_traces(
        texttemplate='%{text:.1f}%',
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Verification Rate: %{y:.1f}%<extra></extra>'
    )

    fig.update_layout(
        height=500,
        showlegend=False,
        xaxis_tickangle=-45,
        yaxis_range=[0, 100],
        margin=dict(t=50, l=50, r=50, b=150)
    )

    return fig


def top_accounts_chart(accounts: List[CategorizedAccount], n: int = 10) -> go.Figure:
    """
    Create horizontal bar chart for top accounts by followers.

    Args:
        accounts: List of categorized accounts
        n: Number of top accounts to show

    Returns:
        Plotly figure
    """
    if not accounts:
        return go.Figure()

    # Sort by followers and take top N
    sorted_accounts = sorted(accounts, key=lambda x: x.followers_count, reverse=True)[:n]

    usernames = [f"@{acc.username}" for acc in sorted_accounts]
    followers = [acc.followers_count for acc in sorted_accounts]
    verified = ["✓ Verified" if acc.verified else "Not Verified" for acc in sorted_accounts]

    fig = go.Figure(data=[
        go.Bar(
            y=usernames,
            x=followers,
            orientation='h',
            text=[f"{f:,}" for f in followers],
            textposition='outside',
            marker=dict(
                color=followers,
                colorscale='Blues',
                showscale=False
            ),
            hovertemplate='<b>%{y}</b><br>Followers: %{x:,}<extra></extra>',
            customdata=verified
        )
    ])

    fig.update_layout(
        title=f'Top {n} Accounts by Followers',
        height=max(400, n * 50),
        yaxis={'categoryorder': 'total ascending'},
        xaxis_title='Followers',
        margin=dict(t=50, l=150, r=100, b=50)
    )

    return fig


def engagement_scatter_plot(accounts_df: pd.DataFrame) -> go.Figure:
    """
    Create scatter plot of followers vs following by category.

    Args:
        accounts_df: DataFrame with account data

    Returns:
        Plotly figure
    """
    if accounts_df.empty:
        return go.Figure()

    # Work on a copy to avoid side effects
    df = accounts_df.copy()

    # Add follower/following ratio
    df['ratio'] = df['followers_count'] / (df['following_count'] + 1)

    fig = px.scatter(
        df,
        x='following_count',
        y='followers_count',
        color='category',
        size='tweet_count',
        hover_data=['username', 'display_name'],
        title='Followers vs Following by Category',
        labels={
            'following_count': 'Following',
            'followers_count': 'Followers',
            'category': 'Category'
        },
        log_x=True,
        log_y=True
    )

    fig.update_layout(
        height=600,
        margin=dict(t=50, l=50, r=50, b=50)
    )

    return fig


def category_comparison_radar(category_stats: pd.DataFrame, categories: List[str]) -> go.Figure:
    """
    Create radar chart comparing selected categories.

    Args:
        category_stats: DataFrame with category statistics
        categories: List of category names to compare

    Returns:
        Plotly figure
    """
    if category_stats.empty or not categories:
        return go.Figure()

    filtered_stats = category_stats[category_stats['Category'].isin(categories)]

    if filtered_stats.empty:
        return go.Figure()

    # Normalize metrics to 0-100 scale for comparison
    metrics = ['Account Count', 'Avg Followers', 'Verification Rate (%)']
    normalized_data = filtered_stats.copy()

    for metric in metrics:
        if metric != 'Verification Rate (%)':  # Already in percentage
            max_val = category_stats[metric].max()
            if max_val > 0:
                normalized_data[metric] = (filtered_stats[metric] / max_val * 100)

    fig = go.Figure()

    for _, row in normalized_data.iterrows():
        fig.add_trace(go.Scatterpolar(
            r=[
                row['Account Count'],
                row['Avg Followers'],
                row['Verification Rate (%)']
            ],
            theta=['Account Count', 'Avg Followers', 'Verification Rate'],
            fill='toself',
            name=row['Category']
        ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        showlegend=True,
        title='Category Comparison (Normalized)',
        height=500
    )

    return fig
