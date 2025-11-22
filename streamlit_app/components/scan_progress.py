"""
Streamlit component for displaying scan progress.

Provides reusable UI component for showing real-time scan progress
with progress bar, status messages, and metrics.
"""

import time
from typing import Dict, Optional

import streamlit as st

from streamlit_app.api_client import XCleanerAPIClient, run_async


def render_scan_progress(job_id: str) -> Dict[str, Optional[str]]:
    """
    Render scan progress component with real-time updates.

    Args:
        job_id: Job identifier for the scan

    Returns:
        Dictionary with final status information
    """
    client = XCleanerAPIClient()
    progress_container = st.container()

    with progress_container:
        st.markdown("### 📊 Scan Progress")

        # Create placeholders for dynamic content
        status_placeholder = st.empty()
        progress_bar_placeholder = st.empty()
        message_placeholder = st.empty()
        metrics_placeholder = st.empty()

        # Poll for progress updates
        max_polls = 3600  # Maximum 1 hour of polling (1 second intervals)
        poll_count = 0

        while poll_count < max_polls:
            try:
                # Fetch current progress
                progress_data = run_async(client.get_scan_progress(job_id))

                status = progress_data.get("status", "unknown")
                progress_percentage = progress_data.get("progress", 0.0)
                message = progress_data.get("message", "")
                current_step = progress_data.get("current_step", "")
                current = progress_data.get("current", 0)
                total = progress_data.get("total", 0)
                accounts_fetched = progress_data.get("accounts_fetched", 0)
                accounts_categorized = progress_data.get("accounts_categorized", 0)
                accounts_saved = progress_data.get("accounts_saved", 0)
                error = progress_data.get("error")

                # Display status badge
                if status == "completed":
                    status_placeholder.success(f"✅ Status: {status.upper()}")
                elif status == "error":
                    status_placeholder.error(f"❌ Status: {status.upper()}")
                elif status == "running":
                    status_placeholder.info(f"🔄 Status: {status.upper()}")
                else:
                    status_placeholder.warning(f"⏳ Status: {status.upper()}")

                # Display progress bar
                progress_bar_placeholder.progress(
                    float(progress_percentage) / 100.0,
                    text=f"{progress_percentage:.1f}%",
                )

                # Display current message
                message_placeholder.markdown(f"**{message}**")

                # Display metrics
                with metrics_placeholder.container():
                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        st.metric("Step", current_step.replace("_", " ").title())

                    with col2:
                        if total > 0:
                            st.metric("Progress", f"{current} / {total}")
                        else:
                            st.metric("Progress", "-")

                    with col3:
                        st.metric("Fetched", accounts_fetched)

                    with col4:
                        st.metric("Categorized", accounts_categorized)

                # Show error if present
                if error:
                    st.error(f"**Error:** {error}")

                # Break if scan completed or errored
                if status in ("completed", "error"):
                    break

                # Wait before next poll
                time.sleep(2)  # Poll every 2 seconds
                poll_count += 1

            except Exception as e:
                st.error(f"Error fetching progress: {str(e)}")
                break

        # Final status
        if poll_count >= max_polls:
            st.warning("⏱️ Progress polling timeout. Scan may still be running.")

        # Return final status
        try:
            final_progress = run_async(client.get_scan_progress(job_id))
            return {
                "status": final_progress.get("status", "unknown"),
                "message": final_progress.get("message", ""),
                "error": final_progress.get("error"),
            }
        except Exception:
            return {
                "status": "unknown",
                "message": "Could not fetch final status",
                "error": None,
            }


def render_scan_status_summary(job_id: str) -> None:
    """
    Render a compact scan status summary.

    Args:
        job_id: Job identifier for the scan
    """
    client = XCleanerAPIClient()

    try:
        status_data = run_async(client.get_scan_status(job_id))

        status = status_data.get("status", "unknown")
        progress = status_data.get("progress", 0.0)
        message = status_data.get("message", "")

        col1, col2 = st.columns([1, 3])

        with col1:
            if status == "completed":
                st.success("✅ Completed")
            elif status == "error":
                st.error("❌ Error")
            elif status == "running":
                st.info("🔄 Running")
            else:
                st.warning("⏳ Pending")

        with col2:
            st.progress(float(progress) / 100.0)
            st.caption(message)

    except Exception as e:
        st.error(f"Error fetching status: {str(e)}")
