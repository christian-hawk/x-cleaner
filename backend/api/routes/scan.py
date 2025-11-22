"""
FastAPI routes for scan-related endpoints.

Provides REST API endpoints and WebSocket for scan job management and progress tracking.
"""

import asyncio
import logging
import uuid
from typing import Dict, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, WebSocket, status
from fastapi.websockets import WebSocketDisconnect

from backend.api.schemas.scan import ScanProgress, ScanRequest, ScanResponse
from backend.config import Config
from backend.core.services.scan_service import ScanService
from backend.dependencies import get_scan_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/scan", tags=["scan"])

# In-memory storage for scan job progress
scan_jobs: Dict[str, ScanProgress] = {}


def update_progress(job_id: str, status: str, progress: int, message: str, current_step: Optional[str] = None, error: Optional[str] = None) -> None:
    """
    Update scan job progress.

    Args:
        job_id: Job identifier
        status: Job status
        progress: Progress percentage (0-100)
        message: Status message
        current_step: Current step in process
        error: Error message if applicable
    """
    scan_jobs[job_id] = ScanProgress(
        job_id=job_id,
        status=status,
        progress=progress,
        message=message,
        current_step=current_step,
        error=error,
    )


async def run_scan_task(
    job_id: str,
    user_id: str,
    scan_service: ScanService,
) -> None:
    """
    Background task to execute scan workflow.

    Args:
        job_id: Job identifier
        user_id: X user ID to scan
        scan_service: Scan service instance
    """
    try:
        # Progress callback function
        def progress_callback(status_val: str, progress_val: int, message_val: str) -> None:
            current_step = None
            if "fetching" in message_val.lower():
                current_step = "fetching"
            elif "categorizing" in message_val.lower():
                current_step = "categorizing"
            elif "saving" in message_val.lower():
                current_step = "saving"
            elif "completed" in status_val.lower():
                current_step = "completed"

            update_progress(job_id, status_val, progress_val, message_val, current_step)

        # Execute scan
        await scan_service.scan_and_categorize(user_id, progress_callback)

        # Mark as completed
        update_progress(
            job_id,
            "completed",
            100,
            "Scan completed successfully",
            "completed",
        )

    except Exception as e:
        logger.error(f"Scan task failed for job {job_id}: {e}", exc_info=True)
        error_message = str(e)
        update_progress(
            job_id,
            "error",
            0,
            f"Scan failed: {error_message}",
            None,
            error=error_message,
        )


@router.post("", response_model=ScanResponse, status_code=status.HTTP_202_ACCEPTED)
async def trigger_scan(
    request: ScanRequest,
    background_tasks: BackgroundTasks,
    scan_service: ScanService = Depends(get_scan_service),
) -> ScanResponse:
    """
    Trigger a new scan job.

    Args:
        request: Scan request with optional user_id
        background_tasks: FastAPI background tasks
        scan_service: Injected scan service

    Returns:
        Scan response with job_id

    Raises:
        HTTPException: If user_id is invalid or missing
    """
    # Get user_id from request or environment
    user_id = request.user_id or Config.X_USER_ID

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user_id is required. Provide it in the request or set X_USER_ID in environment.",
        )

    # Generate unique job ID
    job_id = str(uuid.uuid4())

    # Initialize progress
    update_progress(
        job_id,
        "queued",
        0,
        "Scan job queued",
        "queued",
    )

    # Start background task
    background_tasks.add_task(run_scan_task, job_id, user_id, scan_service)

    logger.info(f"Scan job {job_id} queued for user_id: {user_id}")

    return ScanResponse(
        job_id=job_id,
        status="queued",
        message="Scan job created successfully",
    )


@router.get("/{job_id}/status", response_model=ScanProgress)
async def get_scan_status(job_id: str) -> ScanProgress:
    """
    Get scan job status.

    Args:
        job_id: Job identifier

    Returns:
        Scan progress information

    Raises:
        HTTPException: If job_id not found
    """
    if job_id not in scan_jobs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scan job {job_id} not found",
        )

    return scan_jobs[job_id]


@router.websocket("/ws/{job_id}")
async def websocket_scan_progress(websocket: WebSocket, job_id: str) -> None:
    """
    WebSocket endpoint for real-time scan progress updates.

    Args:
        websocket: WebSocket connection
        job_id: Job identifier
    """
    await websocket.accept()

    try:
        # Send initial status if available
        if job_id in scan_jobs:
            await websocket.send_json(scan_jobs[job_id].model_dump())

        # Poll for updates every second
        last_status = None
        while True:
            if job_id in scan_jobs:
                current_status = scan_jobs[job_id]

                # Only send if status changed
                if current_status != last_status:
                    await websocket.send_json(current_status.model_dump())
                    last_status = current_status

                    # Close connection if completed or error
                    if current_status.status in ("completed", "error"):
                        await websocket.close()
                        break

            # Wait 1 second before next check
            await asyncio.sleep(1.0)

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for job {job_id}")
    except Exception as e:
        logger.error(f"WebSocket error for job {job_id}: {e}", exc_info=True)
        try:
            await websocket.close()
        except Exception:
            pass
