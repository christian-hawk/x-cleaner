"""
Accounts Browser page for X-Cleaner dashboard.

This page provides a searchable, filterable browser for all accounts
with advanced filtering and sorting capabilities.
"""

import sys
from pathlib import Path

import streamlit as st

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from streamlit_app.components import filters
from streamlit_app.utils import (
    accounts_to_dataframe,
    export_to_csv,
    export_to_json,
    format_number,
    load_all_accounts,
)

st.set_page_config(
    page_title="Accounts Browser - X-Cleaner",
    page_icon="👥",
    layout="wide",
)

st.title("👥 Accounts Browser")
st.markdown("Search, filter, and explore all your followed accounts")

# Load data
with st.spinner("Loading accounts..."):
    try:
        accounts = load_all_accounts()

        if not accounts:
            st.warning("⚠️ No data found. Please run a scan first.")
            st.stop()

        accounts_df = accounts_to_dataframe(accounts)

    except (FileNotFoundError, IOError):
        st.error("❌ Could not load accounts from the database.")
        st.info("Please ensure the database file exists and is not corrupted. You may need to run a scan using the CLI.")
        st.stop()
    except Exception:
        st.error("❌ An unexpected error occurred while loading accounts.")
        st.stop()

# Get unique categories
categories = sorted(accounts_df['category'].unique().tolist())

st.markdown("---")

# Filters
filtered_df, filter_info = filters.account_search_filters(accounts_df, categories)

# Display filter results summary
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    st.info(f"📊 Showing **{filter_info['total_results']}** of **{filter_info['total_accounts']}** accounts")

with col2:
    if st.button("🔄 Reset Filters", use_container_width=True):
        st.rerun()

with col3:
    view_mode = st.selectbox(
        "View",
        ["Cards", "Table"],
        label_visibility="collapsed"
    )

st.markdown("---")

# Sort controls
sorted_df = filters.sort_controls(filtered_df)

st.markdown("---")

# Pagination
items_per_page = st.select_slider(
    "Items per page",
    options=[10, 20, 50, 100],
    value=20
)

total_items = len(sorted_df)
total_pages = (total_items - 1) // items_per_page + 1 if total_items > 0 else 1

col1, col2, col3 = st.columns([2, 1, 2])

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

st.markdown("---")

# Display accounts
if total_items == 0:
    st.warning("No accounts match your filters. Try adjusting your search criteria.")
else:
    page_df = sorted_df.iloc[start_idx:end_idx]

    if view_mode == "Cards":
        # Card view
        for _, row in page_df.iterrows():
            with st.container():
                col1, col2, col3 = st.columns([2, 1, 1])

                with col1:
                    # Account header
                    verified_badge = "✅ " if row['verified'] else ""
                    st.markdown(f"### {verified_badge}@{row['username']}")
                    st.markdown(f"**{row['display_name']}**")

                    # Bio
                    if row['bio']:
                        bio_text = row['bio'][:200] + "..." if len(row['bio']) > 200 else row['bio']
                        st.markdown(bio_text)
                    else:
                        st.caption("_No bio_")

                    # Category
                    st.markdown(f"📁 **{row['category']}** (Confidence: {row['confidence']:.0%})")

                with col2:
                    st.metric("Followers", format_number(row['followers_count']))
                    st.metric("Following", format_number(row['following_count']))

                with col3:
                    st.metric("Tweets", format_number(row['tweet_count']))

                    # Confidence bar
                    st.progress(row['confidence'], text=f"Confidence")

                # Additional info
                col_a, col_b = st.columns(2)

                with col_a:
                    if row['location']:
                        st.caption(f"📍 {row['location']}")

                with col_b:
                    if row['website']:
                        st.caption(f"🔗 {row['website']}")

                # Action buttons
                col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 3])

                with col_btn1:
                    st.link_button(
                        "View on X",
                        f"https://x.com/{row['username']}",
                        use_container_width=True
                    )

                with col_btn2:
                    if st.button("ℹ️ Details", key=f"details_{row['user_id']}", use_container_width=True):
                        with st.expander("Full Details", expanded=True):
                            st.json({
                                'user_id': row['user_id'],
                                'username': row['username'],
                                'display_name': row['display_name'],
                                'verified': row['verified'],
                                'category': row['category'],
                                'confidence': row['confidence'],
                                'followers': row['followers_count'],
                                'following': row['following_count'],
                                'tweets': row['tweet_count'],
                                'location': row['location'],
                                'website': row['website'],
                                'bio': row['bio'],
                                'reasoning': row['reasoning']
                            })

                st.markdown("---")

    else:
        # Table view
        display_df = page_df[[
            'username',
            'display_name',
            'category',
            'verified',
            'followers_count',
            'following_count',
            'tweet_count',
            'confidence'
        ]].copy()

        display_df.columns = [
            'Username',
            'Name',
            'Category',
            'Verified',
            'Followers',
            'Following',
            'Tweets',
            'Confidence'
        ]

        # Format confidence as percentage
        display_df['Confidence'] = display_df['Confidence'].apply(lambda x: f"{x:.0%}")

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Username": st.column_config.TextColumn("Username", width="medium"),
                "Name": st.column_config.TextColumn("Name", width="medium"),
                "Category": st.column_config.TextColumn("Category", width="medium"),
                "Verified": st.column_config.CheckboxColumn("Verified", width="small"),
                "Followers": st.column_config.NumberColumn("Followers", width="small", format="%d"),
                "Following": st.column_config.NumberColumn("Following", width="small", format="%d"),
                "Tweets": st.column_config.NumberColumn("Tweets", width="small", format="%d"),
                "Confidence": st.column_config.TextColumn("Confidence", width="small"),
            }
        )

# Export section
st.markdown("---")
st.markdown("### 📥 Export Filtered Results")

col1, col2, col3 = st.columns(3)

# Convert filtered dataframe back to account objects for export
filtered_accounts = [acc for acc in accounts if acc.user_id in sorted_df['user_id'].tolist()]

with col1:
    json_data = export_to_json(filtered_accounts)
    st.download_button(
        label="📄 Download JSON",
        data=json_data,
        file_name=f"accounts_filtered_{page}.json",
        mime="application/json",
        use_container_width=True
    )

with col2:
    csv_data = export_to_csv(filtered_accounts)
    st.download_button(
        label="📊 Download CSV",
        data=csv_data,
        file_name=f"accounts_filtered_{page}.csv",
        mime="text/csv",
        use_container_width=True
    )

with col3:
    if st.button("📋 Copy Usernames", use_container_width=True):
        usernames = "\n".join([f"@{acc.username}" for acc in filtered_accounts])
        st.code(usernames, language="text")
        st.info("Copy the usernames above to your clipboard")

# Summary statistics
st.markdown("---")
st.markdown("### 📊 Filtered Results Summary")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Accounts", len(filtered_accounts))

with col2:
    verified_count = sorted_df['verified'].sum()
    st.metric("Verified", f"{verified_count} ({verified_count/len(sorted_df)*100:.1f}%)" if len(sorted_df) > 0 else "0")

with col3:
    avg_followers = int(sorted_df['followers_count'].mean()) if len(sorted_df) > 0 else 0
    st.metric("Avg Followers", format_number(avg_followers))

with col4:
    categories_count = sorted_df['category'].nunique()
    st.metric("Categories", categories_count)
