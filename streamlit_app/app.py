"""
X-Cleaner Streamlit Dashboard - Main Application

This is the main entry point for the X-Cleaner Streamlit dashboard.
It provides an overview of your X network analysis with key metrics,
category distribution, and top accounts.
"""

import sys
from pathlib import Path

import streamlit as st

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from streamlit_app.components import charts
from streamlit_app.utils import (
    accounts_to_dataframe,
    calculate_category_stats,
    format_number,
    get_overall_stats,
    get_top_accounts_by_category,
    load_all_accounts,
)

# Page configuration
st.set_page_config(
    page_title="X-Cleaner Dashboard",
    page_icon="🧹",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
    .category-card {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        margin: 10px 0;
    }
    .account-card {
        background-color: #f9f9f9;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #1DA1F2;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)


def main() -> None:
    """Main application function."""

    # Header
    st.title("🧹 X-Cleaner Dashboard")
    st.markdown("### Analyze and Understand Your X Network")

    # Sidebar
    with st.sidebar:
        st.image("https://abs.twimg.com/icons/apple-touch-icon-192x192.png", width=100)
        st.title("Navigation")
        st.markdown("---")
        st.markdown("📊 **Overview** (Current Page)")
        st.markdown("📁 Categories")
        st.markdown("👥 Accounts Browser")
        st.markdown("⚙️ Settings")
        st.markdown("---")

        # Refresh button
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

        st.markdown("---")
        st.caption("X-Cleaner v1.0")

    # Load data
    with st.spinner("Loading data..."):
        try:
            accounts = load_all_accounts()

            if not accounts:
                st.warning("⚠️ No data found. Please run a scan first.")
                st.info("Use the CLI to scan your X following: `x-cleaner scan`")
                st.stop()

            accounts_df = accounts_to_dataframe(accounts)
            category_stats = calculate_category_stats(accounts)
            overall_stats = get_overall_stats(accounts)

        except Exception as error:
            st.error(f"❌ Could not load data from API: {error}")
            st.info("Please ensure the backend API is running: `python -m backend.main`")
            st.stop()

    # Hero Section - Key Metrics
    st.markdown("## 📈 Overview")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Total Accounts",
            value=format_number(overall_stats['total_accounts']),
            help="Total number of accounts you follow"
        )

    with col2:
        st.metric(
            label="Categories",
            value=overall_stats['total_categories'],
            help="Number of discovered categories"
        )

    with col3:
        verified_count = overall_stats['verified_count']
        verified_rate = overall_stats['verification_rate']
        st.metric(
            label="Verified Accounts",
            value=f"{verified_count} ({verified_rate:.1f}%)",
            help="Number and percentage of verified accounts"
        )

    with col4:
        st.metric(
            label="Total Reach",
            value=format_number(overall_stats['total_followers']),
            help="Combined follower count of all accounts you follow"
        )

    st.markdown("---")

    # Category Distribution
    st.markdown("## 📊 Category Distribution")

    tab1, tab2 = st.tabs(["📊 Pie Chart", "📈 Bar Chart"])

    with tab1:
        fig_pie = charts.category_distribution_pie_chart(category_stats)
        st.plotly_chart(fig_pie, use_container_width=True)

    with tab2:
        fig_bar = charts.category_distribution_bar_chart(category_stats)
        st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("---")

    # Category Statistics Table
    st.markdown("## 📋 Category Summary")

    # Format the table for display
    display_stats = category_stats.copy()
    display_stats['Avg Followers'] = display_stats['Avg Followers'].apply(format_number)
    display_stats['Percentage'] = display_stats['Percentage'].apply(lambda x: f"{x:.1f}%")
    display_stats['Verification Rate (%)'] = display_stats['Verification Rate (%)'].apply(lambda x: f"{x:.1f}%")

    st.dataframe(
        display_stats,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Category": st.column_config.TextColumn("Category", width="large"),
            "Account Count": st.column_config.NumberColumn("Accounts", width="small"),
            "Percentage": st.column_config.TextColumn("%", width="small"),
            "Avg Followers": st.column_config.TextColumn("Avg Followers", width="medium"),
            "Verification Rate (%)": st.column_config.TextColumn("Verified", width="small"),
        }
    )

    st.markdown("---")

    # Top Accounts
    st.markdown("## 🏆 Top Accounts by Followers")

    col1, col2 = st.columns([2, 1])

    with col2:
        top_n = st.slider("Number of accounts to show", min_value=5, max_value=20, value=10, step=5)

    fig_top = charts.top_accounts_chart(accounts, n=top_n)
    st.plotly_chart(fig_top, use_container_width=True)

    st.markdown("---")

    # Category Highlights
    st.markdown("## 🌟 Category Highlights")

    # Show top 3 categories
    top_categories = category_stats.head(3)

    cols = st.columns(3)

    for idx, (_, cat_row) in enumerate(top_categories.iterrows()):
        with cols[idx]:
            st.markdown(f"### {cat_row['Category']}")
            st.metric("Accounts", cat_row['Account Count'])

            # Get top 3 accounts in this category
            top_accounts = get_top_accounts_by_category(category=cat_row['Category'], limit=3)

            st.markdown("**Top Accounts:**")
            for i, account in enumerate(top_accounts, 1):
                verified_badge = "✓" if account.get("verified", False) else ""
                st.markdown(
                    f"{i}. **@{account.get('username')}** {verified_badge}  \n"
                    f"   {format_number(account.get('followers_count', 0))} followers"
                )

    st.markdown("---")

    # Additional Analytics
    st.markdown("## 📊 Additional Analytics")

    tab1, tab2 = st.tabs(["Verification Rates", "Follower Distribution"])

    with tab1:
        fig_verification = charts.verification_rate_chart(category_stats)
        st.plotly_chart(fig_verification, use_container_width=True)

    with tab2:
        fig_box = charts.followers_distribution_box_plot(accounts_df)
        st.plotly_chart(fig_box, use_container_width=True)

    st.markdown("---")

    # Insights Section
    st.markdown("## 💡 Quick Insights")

    col1, col2 = st.columns(2)

    with col1:
        most_popular = overall_stats.get('most_popular_category', 'N/A')
        st.info(f"📌 Your most followed category is **{most_popular}**")

        avg_followers = format_number(overall_stats['avg_followers'])
        st.info(f"📊 Average followers per account: **{avg_followers}**")

    with col2:
        verified_rate = overall_stats['verification_rate']
        st.info(f"✅ **{verified_rate:.1f}%** of accounts you follow are verified")

        avg_tweets = format_number(overall_stats['avg_tweets'])
        st.info(f"📝 Average tweets per account: **{avg_tweets}**")

    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: gray;'>
            <p>X-Cleaner Dashboard | Powered by Streamlit, X API v2, and Grok AI</p>
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
