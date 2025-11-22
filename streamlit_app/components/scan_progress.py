"""
Scan progress component for Streamlit dashboard.

Provides real-time progress monitoring for scan operations.
"""

import time
from typing import Optional

import requests
import streamlit as st

# API base URL
API_BASE = "http://localhost:8000"


def trigger_scan(user_id: str = "") -> Optional[str]:
    """
    Trigger a new scan via API.

    Args:
        user_id: X user ID to scan (optional).

    Returns:
        Job ID if successful, None otherwise.
    """
    try:
        params = {"user_id": user_id} if user_id else {}
        response = requests.post(f"{API_BASE}/api/scan", params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            return data.get("job_id")
        else:
            st.error(f"Failed to start scan: {response.text}")
            return None

    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to API: {str(e)}")
        return None


def show_scan_progress(job_id: str) -> bool:
    """
    Display real-time scan progress.

    Args:
        job_id: Scan job identifier.

    Returns:
        True if scan completed successfully, False otherwise.
    """
    progress_bar = st.progress(0)
    status_text = st.empty()
    details = st.empty()

    max_polls = 300  # 5 minutes max (300 seconds with 1s interval)
    poll_count = 0

    while poll_count < max_polls:
        try:
            response = requests.get(
                f"{API_BASE}/api/scan/{job_id}/status",
                timeout=5,
            )

            if response.status_code == 200:
                progress_data = response.json()

                # Update progress bar
                progress_value = progress_data.get("progress", 0) / 100
                progress_bar.progress(progress_value)

                # Update status text
                status = progress_data.get("status", "unknown")
                message = progress_data.get("message", "Processing...")

                if status == "complete":
                    status_text.success(f"✅ {message}")
                    with details:
                        st.write(
                            f"**Accounts scanned:** {progress_data.get('accounts_scanned', 0)}"
                        )
                        st.write(
                            f"**Categories discovered:** {progress_data.get('categories_discovered', 0)}"
                        )
                    return True

                elif status == "error":
                    error_msg = progress_data.get("error_message", "Unknown error")
                    status_text.error(f"❌ {message}")
                    details.error(f"Error: {error_msg}")
                    return False

                else:
                    status_text.info(f"🔄 {message}")

            elif response.status_code == 404:
                status_text.warning("Scan job not found")
                return False

            else:
                status_text.error(f"Error fetching status: {response.status_code}")
                return False

        except requests.exceptions.RequestException as e:
            status_text.error(f"Connection error: {str(e)}")
            return False

        time.sleep(1)
        poll_count += 1

    status_text.warning("Scan timeout - took longer than expected")
    return False


def render_scan_button() -> None:
    """
    Render scan trigger button and handle scan workflow.

    This function should be called in the Streamlit sidebar or main area.
    """
    st.markdown("### 🔄 Scan Controls")

    # Check if scan is active
    if "scan_job_id" in st.session_state and st.session_state.scan_job_id:
        st.info("ℹ️ Scan in progress...")

        if st.button("🔄 Refresh Progress", use_container_width=True):
            st.rerun()

        if st.button("🗑️ Clear Scan Status", use_container_width=True):
            st.session_state.scan_job_id = None
            st.rerun()

    else:
        # Show scan button
        if st.button("▶️ Start New Scan", type="primary", use_container_width=True):
            with st.spinner("Starting scan..."):
                job_id = trigger_scan()

                if job_id:
                    st.session_state.scan_job_id = job_id
                    st.success(f"✅ Scan started! Job ID: {job_id[:8]}...")
                    st.rerun()
                else:
                    st.error("Failed to start scan. Check API connection.")

        st.markdown("---")
        st.caption(
            "**Note:** Scanning will fetch your X following accounts "
            "and categorize them with AI."
        )


def check_active_scan() -> None:
    """
    Check and display active scan progress.

    Should be called early in the Streamlit app to show ongoing scans.
    """
    if "scan_job_id" in st.session_state and st.session_state.scan_job_id:
        job_id = st.session_state.scan_job_id

        st.markdown("## 🔄 Scan in Progress")

        success = show_scan_progress(job_id)

        if success:
            st.balloons()
            st.success("🎉 Scan completed! Refreshing data...")
            st.session_state.scan_job_id = None
            st.cache_data.clear()
            time.sleep(2)
            st.rerun()

        elif not success:
            st.warning("Scan did not complete successfully.")
            if st.button("Clear and Try Again"):
                st.session_state.scan_job_id = None
                st.rerun()

        st.markdown("---")
