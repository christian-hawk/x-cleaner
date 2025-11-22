"""
FastAPI routes for scan-related endpoints.

Provides REST API endpoints and WebSocket for scan operations
and real-time progress tracking.
"""

import asyncio
import logging
import os
import uuid
from typing import Dict, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, WebSocket, status
from fastapi.websockets import WebSocketDisconnect

from backend.api.schemas.scan import (
    ScanProgress,
    ScanRequest,
    ScanResponse,
    ScanStatus as ScanStatusSchema,
    WebSocketProgressMessage,
)
from backend.core.services.scan_service import ScanError, ScanService, ScanStatus
from backend.dependencies import get_scan_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/scan", tags=["scan"])

# In-memory storage for scan statuses (MVP - use Redis/database in production)
_scan_statuses: Dict[str, ScanStatus] = {}
_active_scans: Dict[str, str] = {}  # Maps user_id to job_id


def _update_scan_status(job_id: str, status_update: ScanStatus) -> None:
    """
    Update scan status in memory storage.

    Args:
        job_id: Job identifier
        status_update: Updated scan status
    """
    _scan_statuses[job_id] = status_update


def _get_scan_status(job_id: str) -> Optional[ScanStatus]:
    """
    Get scan status by job ID.

    Args:
        job_id: Job identifier

    Returns:
        Scan status if found, None otherwise
    """
    return _scan_statuses.get(job_id)


def _is_scan_active_for_user(user_id: str) -> bool:
    """
    Check if there's an active scan for a user.

    Args:
        user_id: User identifier

    Returns:
        True if scan is active, False otherwise
    """
    job_id = _active_scans.get(user_id)
    if not job_id:
        return False

    scan_status = _get_scan_status(job_id)
    if not scan_status:
        return False

    return scan_status.status == "running"


def _clear_active_scan(user_id: str) -> None:
    """
    Clear active scan for user.

    Args:
        user_id: User identifier
    """
    _active_scans.pop(user_id, None)


@router.post("", response_model=ScanResponse, status_code=status.HTTP_202_ACCEPTED)
async def start_scan(
    request: ScanRequest,
    background_tasks: BackgroundTasks,
    scan_service: ScanService = Depends(get_scan_service),
) -> ScanResponse:
    """
    Start a new scan operation.

    Args:
        request: Scan request with user_id
        background_tasks: FastAPI background tasks
        scan_service: Injected scan service

    Returns:
        Scan response with job_id

    Raises:
        HTTPException: If validation fails or scan already running
    """
    # Validate user_id
    if not request.user_id or not request.user_id.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user_id is required and cannot be empty",
        )

    # Validate user_id format (should be numeric string)
    try:
        int(request.user_id.strip())
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user_id must be a valid numeric string",
        ) from exc

    # Validate API credentials before starting scan
    x_api_token = os.getenv("X_API_BEARER_TOKEN")
    xai_api_key = os.getenv("XAI_API_KEY")

    if not x_api_token or not x_api_token.strip():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="X API Bearer Token not configured. Set X_API_BEARER_TOKEN environment variable.",
        )

    if not xai_api_key or not xai_api_key.strip():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Grok API key not configured. Set XAI_API_KEY environment variable.",
        )

    # Check if scan already running for this user
    if _is_scan_active_for_user(request.user_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A scan is already running for this user. Please wait for it to complete.",
        )

    # Generate job ID
    job_id = f"scan_{uuid.uuid4().hex[:12]}"

    # Create initial status
    scan_status = ScanStatus(job_id=job_id)
    scan_status.status = "pending"
    scan_status.message = "Scan queued"
    _update_scan_status(job_id, scan_status)
    _active_scans[request.user_id] = job_id

    # Define progress callback
    def progress_callback(status_update: ScanStatus) -> None:
        """Update scan status on progress."""
        _update_scan_status(job_id, status_update)

    # Start scan in background
    async def run_scan() -> None:
        """Execute scan operation."""
        try:
            await scan_service.scan_and_categorize(
                user_id=request.user_id,
                progress_callback=progress_callback,
            )
        except ScanError as e:
            logger.error("Scan %s failed: %s", job_id, e)
            scan_status = _get_scan_status(job_id)
            if scan_status:
                scan_status.status = "error"
                scan_status.error = str(e)
                _update_scan_status(job_id, scan_status)
        except Exception as e:
            logger.error("Unexpected error in scan %s: %s", job_id, e, exc_info=True)
            scan_status = _get_scan_status(job_id)
            if scan_status:
                scan_status.status = "error"
                scan_status.error = f"Unexpected error: {str(e)}"
                _update_scan_status(job_id, scan_status)
        finally:
            _clear_active_scan(request.user_id)

    background_tasks.add_task(run_scan)

    return ScanResponse(
        job_id=job_id,
        status="running",
        message="Scan started successfully",
    )


@router.get("/{job_id}/status", response_model=ScanStatusSchema)
async def get_scan_status_endpoint(job_id: str) -> ScanStatusSchema:
    """
    Get scan status by job ID.

    Args:
        job_id: Job identifier

    Returns:
        Scan status information

    Raises:
        HTTPException: If job not found
    """
    scan_status = _get_scan_status(job_id)

    if not scan_status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scan job {job_id} not found",
        )

    return ScanStatusSchema(
        job_id=scan_status.job_id,
        status=scan_status.status,
        progress=scan_status.progress,
        message=scan_status.message,
        error=scan_status.error,
        started_at=scan_status.started_at,
        completed_at=scan_status.completed_at,
    )


@router.get("/{job_id}/progress", response_model=ScanProgress)
async def get_scan_progress(job_id: str) -> ScanProgress:
    """
    Get detailed scan progress by job ID.

    Args:
        job_id: Job identifier

    Returns:
        Detailed progress information

    Raises:
        HTTPException: If job not found
    """
    scan_status = _get_scan_status(job_id)

    if not scan_status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scan job {job_id} not found",
        )

    return ScanProgress(
        job_id=scan_status.job_id,
        status=scan_status.status,
        progress=scan_status.progress,
        current_step=scan_status.current_step,
        message=scan_status.message,
        current=scan_status.current,
        total=scan_status.total,
        accounts_fetched=scan_status.accounts_fetched,
        accounts_categorized=scan_status.accounts_categorized,
        accounts_saved=scan_status.accounts_saved,
        error=scan_status.error,
        started_at=scan_status.started_at,
        completed_at=scan_status.completed_at,
    )


@router.websocket("/{job_id}/ws")
async def websocket_scan_progress(
    websocket: WebSocket,
    job_id: str,
) -> None:
    """
    WebSocket endpoint for real-time scan progress updates.

    Args:
        websocket: WebSocket connection
        job_id: Job identifier
    """
    await websocket.accept()

    try:
        # Verify job exists
        scan_status = _get_scan_status(job_id)
        if not scan_status:
            await websocket.send_json({
                "type": "error",
                "message": f"Scan job {job_id} not found",
            })
            await websocket.close()
            return

        # Send initial status
        initial_message = WebSocketProgressMessage(
            type="progress",
            job_id=scan_status.job_id,
            status=scan_status.status,
            progress=scan_status.progress,
            message=scan_status.message,
            current=scan_status.current,
            total=scan_status.total,
        )
        await websocket.send_json(initial_message.model_dump())

        # Poll for updates
        last_progress = scan_status.progress
        while True:
            await asyncio.sleep(1)  # Poll every second

            current_status = _get_scan_status(job_id)
            if not current_status:
                await websocket.send_json({
                    "type": "error",
                    "message": "Scan job no longer exists",
                })
                break

            # Send update if progress changed
            if (
                current_status.progress != last_progress
                or current_status.status != scan_status.status
                or current_status.message != scan_status.message
            ):
                progress_message = WebSocketProgressMessage(
                    type="progress",
                    job_id=current_status.job_id,
                    status=current_status.status,
                    progress=current_status.progress,
                    message=current_status.message,
                    current=current_status.current,
                    total=current_status.total,
                )
                await websocket.send_json(progress_message.model_dump())
                last_progress = current_status.progress
                scan_status = current_status

            # Close connection if scan completed or errored
            if current_status.status in ("completed", "error"):
                final_message = WebSocketProgressMessage(
                    type="progress",
                    job_id=current_status.job_id,
                    status=current_status.status,
                    progress=current_status.progress,
                    message=current_status.message,
                    current=current_status.current,
                    total=current_status.total,
                )
                await websocket.send_json(final_message.model_dump())
                break

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected for job %s", job_id)
    except Exception as e:
        logger.error("WebSocket error for job %s: %s", job_id, e, exc_info=True)
        try:
            await websocket.send_json({
                "type": "error",
                "message": f"WebSocket error: {str(e)}",
            })
        except Exception:
            pass
    finally:
        try:
            await websocket.close()
        except Exception:
            pass
