"""
Analytics page for X-Cleaner dashboard.

This page provides advanced analytics and visualizations
for deeper insights into your X network.
"""

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from streamlit_app.components import charts
from streamlit_app.utils import (
    accounts_to_dataframe,
    calculate_category_stats,
    format_number,
    load_all_accounts,
)


def categorize_activity(tweet_count: int) -> str:
    """
    Categorize account activity level based on tweet count.

    Args:
        tweet_count: Number of tweets

    Returns:
        Activity level category
    """
    if tweet_count < 100:
        return 'Inactive'
    elif tweet_count < 1000:
        return 'Low Activity'
    elif tweet_count < 10000:
        return 'Moderate Activity'
    elif tweet_count < 50000:
        return 'High Activity'
    else:
        return 'Very High Activity'


st.set_page_config(
    page_title="Analytics - X-Cleaner",
    page_icon="📊",
    layout="wide",
)

st.title("📊 Advanced Analytics")
st.markdown("Deep dive into your X network patterns and trends")

# Load data
with st.spinner("Loading analytics..."):
    try:
        accounts = load_all_accounts()

        if not accounts:
            st.warning("⚠️ No data found. Please run a scan first.")
            st.stop()

        accounts_df = accounts_to_dataframe(accounts)
        category_stats = calculate_category_stats(accounts)

        # Create analytics dataframe with calculated metrics for use across tabs
        analytics_df = accounts_df.copy()
        analytics_df['follower_following_ratio'] = analytics_df['followers_count'] / (analytics_df['following_count'] + 1)
        analytics_df['tweets_per_follower'] = analytics_df['tweet_count'] / (analytics_df['followers_count'] + 1) * 1000

    except (FileNotFoundError, IOError) as e:
        st.error("❌ Could not load data from the database.")
        st.info("Please ensure the database file exists and is not corrupted. You may need to run a scan using the CLI.")
        st.stop()
    except Exception:
        st.error("❌ An unexpected error occurred while loading data.")
        st.stop()

st.markdown("---")

# Category Analysis
st.markdown("## 📁 Category Analysis")

tab1, tab2, tab3 = st.tabs(["Distribution", "Comparison", "Trends"])

with tab1:
    col1, col2 = st.columns(2)

    with col1:
        fig_pie = charts.category_distribution_pie_chart(category_stats)
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        fig_bar = charts.category_distribution_bar_chart(category_stats)
        st.plotly_chart(fig_bar, use_container_width=True)

    # Verification rates
    st.markdown("### Verification Rates by Category")
    fig_verification = charts.verification_rate_chart(category_stats)
    st.plotly_chart(fig_verification, use_container_width=True)

with tab2:
    st.markdown("### Compare Categories")

    # Select categories to compare
    selected_categories = st.multiselect(
        "Select categories to compare (2-5)",
        options=category_stats['Category'].tolist(),
        default=category_stats['Category'].head(3).tolist(),
        max_selections=5
    )

    if len(selected_categories) >= 2:
        # Radar chart
        fig_radar = charts.category_comparison_radar(category_stats, selected_categories)
        st.plotly_chart(fig_radar, use_container_width=True)

        # Comparison table
        st.markdown("### Detailed Comparison")
        comparison_df = category_stats[category_stats['Category'].isin(selected_categories)].copy()
        comparison_df = comparison_df.set_index('Category')
        st.dataframe(comparison_df, use_container_width=True)
    else:
        st.info("Select at least 2 categories to compare")

with tab3:
    st.markdown("### Category Trends")

    # Category size distribution
    fig = px.treemap(
        category_stats,
        path=['Category'],
        values='Account Count',
        title='Category Size Visualization (Treemap)',
        color='Verification Rate (%)',
        color_continuous_scale='RdYlGn',
        hover_data=['Account Count', 'Percentage']
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Account Engagement Analysis
st.markdown("## 👥 Account Engagement Analysis")

tab1, tab2, tab3 = st.tabs(["Follower Patterns", "Engagement Metrics", "Activity Analysis"])

with tab1:
    st.markdown("### Follower Distribution")

    col1, col2 = st.columns(2)

    with col1:
        # Box plot by category
        fig_box = charts.followers_distribution_box_plot(accounts_df)
        st.plotly_chart(fig_box, use_container_width=True)

    with col2:
        # Overall distribution histogram
        fig = px.histogram(
            accounts_df,
            x='followers_count',
            nbins=50,
            title='Overall Follower Count Distribution',
            labels={'followers_count': 'Followers', 'count': 'Number of Accounts'},
            log_x=True
        )
        st.plotly_chart(fig, use_container_width=True)

    # Top accounts
    st.markdown("### Top Accounts")
    top_n = st.slider("Number of top accounts", 5, 30, 15, 5)
    fig_top = charts.top_accounts_chart(accounts, n=top_n)
    st.plotly_chart(fig_top, use_container_width=True)

with tab2:
    st.markdown("### Engagement Patterns")

    # Followers vs Following scatter
    fig_scatter = charts.engagement_scatter_plot(accounts_df)
    st.plotly_chart(fig_scatter, use_container_width=True)

    # Use already calculated analytics_df from above
    col1, col2 = st.columns(2)

    with col1:
        # Follower/Following ratio by category
        ratio_by_category = analytics_df.groupby('category')['follower_following_ratio'].mean().sort_values(ascending=False)

        fig = px.bar(
            x=ratio_by_category.values,
            y=ratio_by_category.index,
            orientation='h',
            title='Average Follower/Following Ratio by Category',
            labels={'x': 'Ratio', 'y': 'Category'}
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Tweet activity by category
        tweets_by_category = analytics_df.groupby('category')['tweet_count'].mean().sort_values(ascending=False)

        fig = px.bar(
            x=tweets_by_category.values,
            y=tweets_by_category.index,
            orientation='h',
            title='Average Tweet Count by Category',
            labels={'x': 'Tweets', 'y': 'Category'},
            color=tweets_by_category.values,
            color_continuous_scale='Viridis'
        )
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.markdown("### Activity Levels")

    # Work on a copy to avoid side effects
    activity_df = accounts_df.copy()
    activity_df['activity_level'] = activity_df['tweet_count'].apply(categorize_activity)

    activity_counts = activity_df['activity_level'].value_counts()

    col1, col2 = st.columns(2)

    with col1:
        # Activity level distribution
        fig = px.pie(
            values=activity_counts.values,
            names=activity_counts.index,
            title='Activity Level Distribution',
            color_discrete_sequence=px.colors.sequential.RdBu
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Activity by category
        activity_by_category = pd.crosstab(activity_df['category'], activity_df['activity_level'])

        fig = px.bar(
            activity_by_category,
            title='Activity Levels by Category',
            labels={'value': 'Count', 'category': 'Category'},
            barmode='stack'
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Network Insights
st.markdown("## 🔍 Network Insights")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 👑 Most Influential")
    top_by_followers = accounts_df.nlargest(5, 'followers_count')[['username', 'followers_count', 'category']]
    for _, row in top_by_followers.iterrows():
        st.markdown(f"**@{row['username']}**")
        st.caption(f"{format_number(row['followers_count'])} followers • {row['category']}")
        st.markdown("---")

with col2:
    st.markdown("### 📢 Most Active")
    top_by_tweets = accounts_df.nlargest(5, 'tweet_count')[['username', 'tweet_count', 'category']]
    for _, row in top_by_tweets.iterrows():
        st.markdown(f"**@{row['username']}**")
        st.caption(f"{format_number(row['tweet_count'])} tweets • {row['category']}")
        st.markdown("---")

with col3:
    st.markdown("### 🌟 Most Engaged")
    top_by_ratio = analytics_df.nlargest(5, 'follower_following_ratio')[['username', 'follower_following_ratio', 'category']]
    for _, row in top_by_ratio.iterrows():
        st.markdown(f"**@{row['username']}**")
        st.caption(f"{row['follower_following_ratio']:.1f}x ratio • {row['category']}")
        st.markdown("---")

st.markdown("---")

# Statistical Summary
st.markdown("## 📈 Statistical Summary")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### Follower Statistics")
    st.metric("Mean", format_number(int(accounts_df['followers_count'].mean())))
    st.metric("Median", format_number(int(accounts_df['followers_count'].median())))
    st.metric("Std Dev", format_number(int(accounts_df['followers_count'].std())))

with col2:
    st.markdown("### Following Statistics")
    st.metric("Mean", format_number(int(accounts_df['following_count'].mean())))
    st.metric("Median", format_number(int(accounts_df['following_count'].median())))
    st.metric("Std Dev", format_number(int(accounts_df['following_count'].std())))

with col3:
    st.markdown("### Tweet Statistics")
    st.metric("Mean", format_number(int(accounts_df['tweet_count'].mean())))
    st.metric("Median", format_number(int(accounts_df['tweet_count'].median())))
    st.metric("Std Dev", format_number(int(accounts_df['tweet_count'].std())))

# Correlation analysis
st.markdown("---")
st.markdown("### 🔗 Correlation Analysis")

correlation_data = accounts_df[['followers_count', 'following_count', 'tweet_count', 'confidence']].corr()

fig = px.imshow(
    correlation_data,
    text_auto=True,
    aspect="auto",
    title="Correlation Matrix",
    color_continuous_scale='RdBu_r',
    zmin=-1,
    zmax=1
)
st.plotly_chart(fig, use_container_width=True)

st.caption("""
**Interpretation:**
- Values close to 1 indicate strong positive correlation
- Values close to -1 indicate strong negative correlation
- Values close to 0 indicate no correlation
""")
