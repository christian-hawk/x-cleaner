"""
Categories page for X-Cleaner dashboard.

This page provides detailed views of all discovered categories,
allowing users to explore accounts within each category.
"""

import sys
from pathlib import Path

import streamlit as st

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from streamlit_app.components import charts, filters
from streamlit_app.utils import (
    accounts_to_dataframe,
    calculate_category_stats,
    export_to_csv,
    export_to_json,
    format_account_card,
    format_number,
    get_top_accounts_by_category,
    load_all_accounts,
)

st.set_page_config(
    page_title="Categories - X-Cleaner",
    page_icon="📁",
    layout="wide",
)

st.title("📁 Category Explorer")
st.markdown("Explore all discovered categories and their accounts in detail")

# Load data
with st.spinner("Loading categories..."):
    try:
        accounts = load_all_accounts()

        if not accounts:
            st.warning("⚠️ No data found. Please run a scan first.")
            st.stop()

        accounts_df = accounts_to_dataframe(accounts)
        category_stats = calculate_category_stats(accounts)

    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
        st.stop()

# Sidebar - Category selector
with st.sidebar:
    st.markdown("## 📋 Categories")

    # Search/filter categories
    category_search = st.text_input("🔍 Search categories", placeholder="Type to search...")

    # Filter categories by search term
    if category_search:
        filtered_categories = [
            cat for cat in category_stats['Category'].tolist()
            if category_search.lower() in cat.lower()
        ]
    else:
        filtered_categories = category_stats['Category'].tolist()

    # Sort options
    sort_option = st.selectbox(
        "Sort by",
        ["Account Count (High to Low)", "Name (A-Z)", "Name (Z-A)", "Verification Rate"]
    )

    # Apply sorting
    if sort_option == "Account Count (High to Low)":
        filtered_categories = category_stats['Category'].tolist()
    elif sort_option == "Name (A-Z)":
        filtered_categories = sorted(filtered_categories)
    elif sort_option == "Name (Z-A)":
        filtered_categories = sorted(filtered_categories, reverse=True)
    elif sort_option == "Verification Rate":
        filtered_stats = category_stats[category_stats['Category'].isin(filtered_categories)]
        filtered_categories = filtered_stats.sort_values('Verification Rate (%)', ascending=False)['Category'].tolist()

    # Display category list
    selected_category = st.radio(
        "Select a category",
        options=filtered_categories,
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.caption(f"Showing {len(filtered_categories)} categories")

# Main content
if selected_category:
    # Get category data
    category_accounts = [acc for acc in accounts if acc.category == selected_category]
    category_info = category_stats[category_stats['Category'] == selected_category].iloc[0]

    # Category header
    st.markdown(f"## {selected_category}")

    # Key metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Accounts",
            category_info['Account Count'],
            help="Number of accounts in this category"
        )

    with col2:
        st.metric(
            "Percentage",
            f"{category_info['Percentage']:.1f}%",
            help="Percentage of total accounts"
        )

    with col3:
        st.metric(
            "Avg Followers",
            format_number(int(category_info['Avg Followers'])),
            help="Average follower count"
        )

    with col4:
        st.metric(
            "Verified",
            f"{category_info['Verification Rate (%)']:.1f}%",
            help="Verification rate in this category"
        )

    st.markdown("---")

    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["📊 Overview", "👥 All Accounts", "📈 Analytics"])

    with tab1:
        st.markdown("### Top Accounts")

        # Top accounts by followers
        top_accounts = get_top_accounts_by_category(accounts, selected_category, n=10)

        col1, col2 = st.columns([2, 1])

        with col1:
            fig = charts.top_accounts_chart(top_accounts, n=10)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("#### Account Details")
            for i, acc in enumerate(top_accounts[:5], 1):
                with st.expander(f"{i}. @{acc.username}"):
                    st.markdown(format_account_card(acc))
                    if acc.website:
                        st.markdown(f"[Visit X Profile](https://x.com/{acc.username})")

        st.markdown("---")

        # Distribution charts
        col1, col2 = st.columns(2)

        category_df = accounts_df[accounts_df['category'] == selected_category]

        with col1:
            st.markdown("### Follower Distribution")
            # Create histogram
            import plotly.express as px
            fig = px.histogram(
                category_df,
                x='followers_count',
                nbins=20,
                title='Follower Count Distribution',
                labels={'followers_count': 'Followers', 'count': 'Number of Accounts'}
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("### Verification Status")
            verified_counts = category_df['verified'].value_counts()
            import plotly.graph_objects as go
            fig = go.Figure(data=[
                go.Pie(
                    labels=['Verified', 'Not Verified'],
                    values=[
                        verified_counts.get(True, 0),
                        verified_counts.get(False, 0)
                    ],
                    marker=dict(colors=['#1DA1F2', '#E8E8E8'])
                )
            ])
            fig.update_layout(title='Verification Status', height=400)
            st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.markdown(f"### All Accounts in {selected_category}")

        # Search within category
        account_search = st.text_input(
            "🔍 Search accounts",
            placeholder="Search by username or name...",
            key="category_account_search"
        )

        # Filter accounts
        filtered_category_df = category_df.copy()
        if account_search:
            search_lower = account_search.lower()
            filtered_category_df = filtered_category_df[
                filtered_category_df['username'].str.lower().str.contains(search_lower, na=False) |
                filtered_category_df['display_name'].str.lower().str.contains(search_lower, na=False)
            ]

        # Sort options
        col1, col2 = st.columns([3, 1])
        with col1:
            sort_by = st.selectbox(
                "Sort by",
                ["Followers (High to Low)", "Followers (Low to High)", "Username (A-Z)", "Username (Z-A)"],
                key="category_sort"
            )

        # Apply sorting
        if "Followers" in sort_by:
            ascending = "Low to High" in sort_by
            filtered_category_df = filtered_category_df.sort_values('followers_count', ascending=ascending)
        else:
            ascending = "A-Z" in sort_by
            filtered_category_df = filtered_category_df.sort_values('username', ascending=ascending)

        st.caption(f"Showing {len(filtered_category_df)} of {len(category_df)} accounts")

        # Pagination
        items_per_page = 20
        total_pages = (len(filtered_category_df) - 1) // items_per_page + 1 if len(filtered_category_df) > 0 else 1

        page = st.number_input(
            f"Page (1-{total_pages})",
            min_value=1,
            max_value=total_pages,
            value=1,
            step=1,
            key="category_page"
        )

        start_idx = (page - 1) * items_per_page
        end_idx = min(start_idx + items_per_page, len(filtered_category_df))

        # Display accounts
        page_accounts = filtered_category_df.iloc[start_idx:end_idx]

        for _, row in page_accounts.iterrows():
            with st.container():
                col1, col2 = st.columns([3, 1])

                with col1:
                    verified_badge = "✓ " if row['verified'] else ""
                    st.markdown(f"### {verified_badge}@{row['username']}")
                    st.markdown(f"**{row['display_name']}**")

                    if row['bio']:
                        bio_preview = row['bio'][:200] + "..." if len(row['bio']) > 200 else row['bio']
                        st.markdown(bio_preview)

                with col2:
                    st.metric("Followers", format_number(row['followers_count']))
                    st.metric("Following", format_number(row['following_count']))
                    st.progress(row['confidence'], text=f"Confidence: {row['confidence']:.0%}")

                if row['website']:
                    st.caption(f"🔗 {row['website']}")

                st.markdown(f"[View on X](https://x.com/{row['username']})")
                st.markdown("---")

    with tab3:
        st.markdown("### Category Analytics")

        # Engagement scatter
        st.markdown("#### Account Engagement Pattern")
        import plotly.express as px
        fig = px.scatter(
            category_df,
            x='following_count',
            y='followers_count',
            size='tweet_count',
            hover_data=['username', 'display_name'],
            title='Followers vs Following',
            labels={'following_count': 'Following', 'followers_count': 'Followers'},
            log_x=True,
            log_y=True
        )
        st.plotly_chart(fig, use_container_width=True)

        # Statistics
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Key Statistics")
            st.metric("Total Followers (Combined)", format_number(category_df['followers_count'].sum()))
            st.metric("Median Followers", format_number(int(category_df['followers_count'].median())))
            st.metric("Total Tweets (Combined)", format_number(category_df['tweet_count'].sum()))

        with col2:
            st.markdown("#### Distribution Stats")
            st.metric("Min Followers", format_number(category_df['followers_count'].min()))
            st.metric("Max Followers", format_number(category_df['followers_count'].max()))
            st.metric("Std Deviation", format_number(int(category_df['followers_count'].std())))

    # Export section
    st.markdown("---")
    st.markdown("### 📥 Export Category Data")

    col1, col2, col3 = st.columns(3)

    with col1:
        json_data = export_to_json(category_accounts)
        st.download_button(
            label="📄 Download JSON",
            data=json_data,
            file_name=f"{selected_category.replace(' ', '_')}_accounts.json",
            mime="application/json",
            use_container_width=True
        )

    with col2:
        csv_data = export_to_csv(category_accounts)
        st.download_button(
            label="📊 Download CSV",
            data=csv_data,
            file_name=f"{selected_category.replace(' ', '_')}_accounts.csv",
            mime="text/csv",
            use_container_width=True
        )

else:
    st.info("👈 Select a category from the sidebar to explore")
