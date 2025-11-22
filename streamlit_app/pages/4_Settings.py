"""
Settings and Scan Management page for X-Cleaner dashboard.

This page provides configuration options, scan management,
and data export/import functionality.
"""

import platform
import sys
import time
from datetime import datetime
from pathlib import Path

import streamlit as st

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from streamlit_app.utils import (
    export_to_csv,
    export_to_json,
    format_number,
    load_all_accounts,
)

st.set_page_config(
    page_title="Settings - X-Cleaner",
    page_icon="🔧",
    layout="wide",
)

st.title("⚙️ Settings & Management")
st.markdown("Configure X-Cleaner and manage your data")

st.markdown("---")

# Scan Management Section - MOVED TO TOP FOR VISIBILITY
st.markdown("## 🔄 Scan Management")
st.info("💡 **Start here!** Use the section below to scan your X network and categorize accounts.")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Trigger New Scan")

    # Get user_id from environment or allow input
    import os
    default_user_id = os.getenv("X_USER_ID", "")

    user_id_input = st.text_input(
        "X User ID",
        value=default_user_id,
        help="Your X (Twitter) user ID. Leave empty to use value from .env file.",
        placeholder="Enter your X user ID"
    )

    user_id_to_use = user_id_input.strip() if user_id_input.strip() else default_user_id

    if not user_id_to_use:
        st.warning("⚠️ Please provide a X User ID to start a scan.")
        st.info("""
        You can:
        1. Enter your X User ID above, or
        2. Set `X_USER_ID` in your `.env` file
        """)
        # Disable button if no user_id
        st.button("🔄 Start New Scan", type="primary", use_container_width=True, disabled=True)
    else:
        # Validate user_id is numeric before allowing scan
        user_id_valid = True
        try:
            int(user_id_to_use)
        except ValueError:
            user_id_valid = False
            st.error("❌ X User ID must be a numeric value (e.g., 123456789)")

        if st.button("🔄 Start New Scan", type="primary", use_container_width=True, disabled=not user_id_valid):
            try:
                from streamlit_app.api_client import start_scan_sync

                with st.spinner("Starting scan..."):
                    scan_response = start_scan_sync(user_id=user_id_to_use)
                    job_id = scan_response.get("job_id")
                    st.session_state["current_scan_job_id"] = job_id
                    st.success(f"✅ Scan started! Job ID: {job_id}")
                    st.rerun()
            except Exception as e:
                error_message = str(e)
                if "already running" in error_message.lower():
                    st.warning("⚠️ A scan is already running for this user. Please wait for it to complete.")
                elif "400" in error_message or "Bad Request" in error_message:
                    st.error(f"❌ Invalid request: {error_message}. Please check that user_id is a valid numeric string.")
                else:
                    st.error(f"❌ Error starting scan: {error_message}")

    # Display current scan progress if available
    if "current_scan_job_id" in st.session_state:
        st.markdown("---")
        st.markdown("### Current Scan Progress")
        from streamlit_app.components.scan_progress import render_scan_progress

        job_id = st.session_state["current_scan_job_id"]
        final_status = render_scan_progress(job_id)

        if final_status.get("status") in ("completed", "error"):
            # Clear job_id after completion
            del st.session_state["current_scan_job_id"]
            st.cache_data.clear()
            if final_status.get("status") == "completed":
                st.success("✅ Scan completed! Refreshing dashboard...")
                time.sleep(2)
                st.rerun()

with col2:
    st.markdown("### Scan Status")

    try:
        accounts = load_all_accounts()

        if accounts:
            # Get most recent analysis date
            most_recent = max(accounts, key=lambda x: x.get("analyzed_at", ""))

            st.success("✅ Data Available")
            st.metric("Total Accounts", format_number(len(accounts)))
            analyzed_at_str = most_recent.get("analyzed_at", "Unknown")
            st.metric("Last Scan", str(analyzed_at_str))

            st.markdown("---")

            if st.button("🔄 Refresh Dashboard Data", use_container_width=True):
                st.cache_data.clear()
                st.success("✅ Cache cleared! Reload the page to see updated data.")
                st.rerun()

        else:
            st.warning("⚠️ No scan data found")
            st.caption("Start a new scan using the button on the left")

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
                "total_categories": len(set(acc.get("category", "") for acc in accounts)),
                "verified_count": sum(1 for acc in accounts if acc.get("verified", False)),
                "verification_rate": sum(1 for acc in accounts if acc.get("verified", False)) / len(accounts) * 100,
                "total_followers": sum(acc.get("followers_count", 0) for acc in accounts),
                "avg_followers": sum(acc.get("followers_count", 0) for acc in accounts) / len(accounts),
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
        # Get record counts from API
        accounts = load_all_accounts()
        st.metric("Total Records", len(accounts))

        st.info("💡 Database size information is available via the backend API")

    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

with col2:
    st.markdown("### Maintenance")

    st.warning("⚠️ **Danger Zone**")

    if st.button("🗑️ Clear All Data", type="secondary", use_container_width=True):
        st.error("This action would delete all data. This feature is disabled in the dashboard for safety.")
        st.info("To clear data, delete the database file manually or use the CLI.")

    st.markdown("---")

    st.info("💡 To rebuild database indexes or perform maintenance, use the CLI tools.")

st.markdown("---")

# Configuration
st.markdown("## 🔧 Configuration")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Dashboard Settings")

    _theme = st.selectbox("Theme", ["Light", "Dark", "Auto"], index=0)
    st.caption("Theme changes require a page reload")

    _items_per_page = st.number_input("Default Items Per Page", min_value=10, max_value=100, value=20, step=10)

    _show_confidence = st.checkbox("Show Confidence Scores", value=True)
    _show_reasoning = st.checkbox("Show AI Reasoning", value=False)

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
