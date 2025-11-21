"""
Settings and Scan Management page for X-Cleaner dashboard.

This page provides configuration options, scan management,
and data export/import functionality.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

import streamlit as st

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from streamlit_app.utils import (
    export_to_csv,
    export_to_json,
    format_number,
    get_database,
    load_all_accounts,
)

st.set_page_config(
    page_title="Settings - X-Cleaner",
    page_icon="⚙️",
    layout="wide",
)

st.title("⚙️ Settings & Management")
st.markdown("Configure X-Cleaner and manage your data")

st.markdown("---")

# Scan Management Section
st.markdown("## 🔄 Scan Management")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Trigger New Scan")
    st.info("""
    **Important:** To scan your X network, you need to use the CLI.

    Run the following command in your terminal:
    ```bash
    python -m backend.cli.commands scan
    ```

    This will:
    1. Fetch all accounts you follow from X API
    2. Analyze and categorize them using Grok AI
    3. Store results in the database
    4. Update this dashboard automatically
    """)

    if st.button("📋 Copy CLI Command", use_container_width=True):
        st.code("python -m backend.cli.commands scan", language="bash")
        st.success("Copy the command above to your terminal")

with col2:
    st.markdown("### Scan Status")

    try:
        accounts = load_all_accounts()

        if accounts:
            # Get most recent analysis date
            most_recent = max(accounts, key=lambda x: x.analyzed_at)

            st.success("✅ Data Available")
            st.metric("Total Accounts", format_number(len(accounts)))
            st.metric("Last Scan", most_recent.analyzed_at.strftime("%Y-%m-%d %H:%M"))

            st.markdown("---")

            if st.button("🔄 Refresh Dashboard Data", use_container_width=True):
                st.cache_data.clear()
                st.success("✅ Cache cleared! Reload the page to see updated data.")
                st.rerun()

        else:
            st.warning("⚠️ No scan data found")
            st.caption("Run a scan using the CLI to populate the dashboard")

    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

st.markdown("---")

# Data Export Section
st.markdown("## 📥 Data Export")

try:
    accounts = load_all_accounts()

    if accounts:
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("### Export All Data")

            export_format = st.radio(
                "Select format",
                ["JSON", "CSV"],
                label_visibility="collapsed"
            )

            if export_format == "JSON":
                json_data = export_to_json(accounts)
                st.download_button(
                    label="📄 Download JSON",
                    data=json_data,
                    file_name=f"x_cleaner_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )
            else:
                csv_data = export_to_csv(accounts)
                st.download_button(
                    label="📊 Download CSV",
                    data=csv_data,
                    file_name=f"x_cleaner_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )

        with col2:
            st.markdown("### Export Statistics")

            # Generate summary report
            summary = {
                "export_date": datetime.now().isoformat(),
                "total_accounts": len(accounts),
                "total_categories": len(set(acc.category for acc in accounts)),
                "verified_count": sum(1 for acc in accounts if acc.verified),
                "verification_rate": sum(1 for acc in accounts if acc.verified) / len(accounts) * 100,
                "total_followers": sum(acc.followers_count for acc in accounts),
                "avg_followers": sum(acc.followers_count for acc in accounts) / len(accounts),
            }

            st.json(summary)

        with col3:
            st.markdown("### Export Options")

            st.checkbox("Include reasoning", value=True, disabled=True)
            st.checkbox("Include confidence scores", value=True, disabled=True)
            st.checkbox("Include metadata", value=True, disabled=True)

            st.caption("All options are currently included in exports")

    else:
        st.warning("⚠️ No data to export. Run a scan first.")

except Exception as e:
    st.error(f"❌ Error loading data: {str(e)}")

st.markdown("---")

# Database Management
st.markdown("## 🗄️ Database Management")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Database Info")

    try:
        db = get_database()

        # Get database file size
        db_path = Path(db.db_path)
        if db_path.exists():
            size_bytes = db_path.stat().st_size
            size_mb = size_bytes / (1024 * 1024)

            st.metric("Database Size", f"{size_mb:.2f} MB")
            st.metric("Database Path", db.db_path)

            # Get record counts
            accounts = load_all_accounts()
            st.metric("Total Records", len(accounts))

        else:
            st.warning("⚠️ Database file not found")

    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

with col2:
    st.markdown("### Maintenance")

    st.warning("⚠️ **Danger Zone**")

    if st.button("🗑️ Clear All Data", type="secondary", use_container_width=True):
        st.error("This action would delete all data. This feature is disabled in the dashboard for safety.")
        st.info("To clear data, delete the database file manually or use the CLI.")

    st.markdown("---")

    if st.button("🔄 Rebuild Database Indexes", use_container_width=True):
        try:
            db = get_database()
            db._init_db()  # Reinitialize schema and indexes
            st.success("✅ Database indexes rebuilt successfully")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

st.markdown("---")

# Configuration
st.markdown("## 🔧 Configuration")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Dashboard Settings")

    theme = st.selectbox("Theme", ["Light", "Dark", "Auto"], index=0)
    st.caption("Theme changes require a page reload")

    items_per_page = st.number_input("Default Items Per Page", min_value=10, max_value=100, value=20, step=10)

    show_confidence = st.checkbox("Show Confidence Scores", value=True)
    show_reasoning = st.checkbox("Show AI Reasoning", value=False)

    st.markdown("---")

    if st.button("💾 Save Settings", use_container_width=True):
        st.info("Settings will be saved in a future update")

with col2:
    st.markdown("### API Configuration")

    st.info("""
    API credentials are configured via environment variables.

    Edit the `.env` file in the project root:
    ```
    X_API_BEARER_TOKEN=your_token_here
    XAI_API_KEY=your_grok_key_here
    ```

    Restart the dashboard after making changes.
    """)

    if st.button("📋 Show .env Example", use_container_width=True):
        st.code("""
# X API Credentials
X_API_BEARER_TOKEN=your_bearer_token_here
X_USER_ID=your_user_id_here

# Grok API Credentials
XAI_API_KEY=your_xai_api_key_here

# Application Settings
DATABASE_PATH=data/accounts.db
BATCH_SIZE=100
RATE_LIMIT_DELAY=1.0
CACHE_EXPIRY_DAYS=7
        """, language="bash")

st.markdown("---")

# About Section
st.markdown("## ℹ️ About X-Cleaner")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Version Information")

    version_info = {
        "Version": "1.0.0",
        "Dashboard": "Streamlit",
        "Backend": "Python 3.11+",
        "Database": "SQLite",
        "AI Model": "Grok (xAI)",
        "Data Source": "X API v2"
    }

    for key, value in version_info.items():
        st.text(f"{key}: {value}")

with col2:
    st.markdown("### Resources")

    st.markdown("""
    - [Project Documentation](https://github.com/christian-hawk/x-cleaner)
    - [X API Documentation](https://developer.x.com/en/docs/twitter-api)
    - [Grok API Documentation](https://docs.x.ai/)
    - [Report Issues](https://github.com/christian-hawk/x-cleaner/issues)
    """)

st.markdown("---")

# System Information
with st.expander("🖥️ System Information"):
    import platform

    system_info = {
        "Python Version": platform.python_version(),
        "Platform": platform.platform(),
        "Processor": platform.processor(),
        "Streamlit Version": st.__version__,
    }

    st.json(system_info)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
        <p>X-Cleaner Dashboard | Built with ❤️ using Streamlit</p>
    </div>
    """,
    unsafe_allow_html=True
)
