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
from backend.api.x_client import XAPIError, XAPIClient
from backend.core.services.scan_service import ScanError, ScanService, ScanStatus
from backend.dependencies import get_scan_service, get_x_client

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
    x_client: XAPIClient = Depends(get_x_client),
) -> ScanResponse:
    """
    Start a new scan operation.

    Args:
        request: Scan request with username or user_id
        background_tasks: FastAPI background tasks
        scan_service: Injected scan service
        x_client: Injected X API client for username lookup

    Returns:
        Scan response with job_id

    Raises:
        HTTPException: If validation fails or scan already running
    """
    logger.info("=== SCAN REQUEST RECEIVED ===")
    logger.info("Raw request data - username=%r, user_id=%r", request.username, request.user_id)
    logger.info("Request type - username type=%s, user_id type=%s", type(request.username).__name__, type(request.user_id).__name__)
    
    # Validate that either username or user_id is provided
    username_cleaned = request.username.strip() if request.username else ""
    user_id_provided = request.user_id.strip() if request.user_id else ""
    
    logger.info("After cleaning: username_cleaned=%r, user_id_provided=%r", username_cleaned, user_id_provided)
    logger.info("Validation check: username_empty=%s, user_id_empty=%s", not username_cleaned, not user_id_provided)

    if not username_cleaned and not user_id_provided:
        error_msg = "Either 'username' or 'user_id' is required. Provide a valid X username (e.g., 'elonmusk') or user ID (e.g., '123456789')."
        logger.error("VALIDATION FAILED: %s", error_msg)
        logger.error("Request details: username=%r, user_id=%r", request.username, request.user_id)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg,
        )

    # If username provided, convert to user_id
    user_id_cleaned = user_id_provided
    if username_cleaned:
        logger.info("Username provided, looking up user_id for username=%r", username_cleaned)
        try:
            # Remove @ if present
            username_cleaned = username_cleaned.lstrip("@")
            logger.info("Cleaned username (after @ removal): %r", username_cleaned)
            
            # Fetch user_id from username
            logger.info("Calling x_client.get_user_by_username(%r)...", username_cleaned)
            account = await x_client.get_user_by_username(username_cleaned)
            if not account:
                error_msg = f"Username '{username_cleaned}' not found on X. Please check the username and try again."
                logger.error("USERNAME NOT FOUND: %s", error_msg)
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=error_msg,
                )
            user_id_cleaned = account.user_id
            logger.info("Successfully resolved username %r to user_id=%r", username_cleaned, user_id_cleaned)
        except XAPIError as e:
            # Map X API error codes to appropriate HTTP status codes
            x_api_status = getattr(e, 'status_code', None)
            logger.info("XAPIError caught - status_code=%s, message=%s", x_api_status, str(e))
            
            if x_api_status == 401:
                error_msg = (
                    f"X API authentication failed (401 Unauthorized). "
                    f"Please check your X_API_BEARER_TOKEN in the .env file. "
                    f"The token may be invalid, expired, or not properly configured."
                )
                logger.error("X API AUTHENTICATION ERROR: %s", error_msg)
                logger.error("Original error: %s", str(e))
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=error_msg,
                ) from e
            elif x_api_status == 403:
                error_msg = (
                    f"X API access forbidden (403). "
                    f"This may indicate that your API credentials don't have the required permissions, "
                    f"or your Developer App is not properly attached to a Project."
                )
                logger.error("X API PERMISSION ERROR: %s", error_msg)
                logger.error("Original error: %s", str(e))
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=error_msg,
                ) from e
            elif x_api_status == 404:
                error_msg = f"Username '{username_cleaned}' not found on X. Please check the username and try again."
                logger.error("USERNAME NOT FOUND: %s", error_msg)
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=error_msg,
                ) from e
            else:
                error_msg = f"Failed to lookup username '{username_cleaned}': {str(e)}"
                logger.error("X API ERROR during username lookup: %s", error_msg, exc_info=True)
                # Use 502 Bad Gateway for API errors (external service issue)
                http_status = status.HTTP_502_BAD_GATEWAY if x_api_status else status.HTTP_400_BAD_REQUEST
                raise HTTPException(
                    status_code=http_status,
                    detail=error_msg,
                ) from e
        except HTTPException:
            raise
        except Exception as e:
            error_msg = f"Unexpected error looking up username '{username_cleaned}': {str(e)}"
            logger.error("UNEXPECTED ERROR during username lookup: %s", error_msg, exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_msg,
            ) from e
    else:
        logger.info("No username provided, using user_id directly: %r", user_id_cleaned)

    # Validate user_id format (should be numeric string)
    logger.info("Validating user_id format: %r", user_id_cleaned)
    try:
        int(user_id_cleaned)
        logger.info("user_id validation passed: %r is numeric", user_id_cleaned)
    except ValueError as exc:
        error_msg = f"user_id must be a valid numeric string. Received: '{user_id_cleaned}'. This may indicate an error in username lookup."
        logger.error("USER_ID VALIDATION FAILED: %s", error_msg)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg,
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
    if _is_scan_active_for_user(user_id_cleaned):
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
    _active_scans[user_id_cleaned] = job_id

    # Define progress callback
    def progress_callback(status_update: ScanStatus) -> None:
        """Update scan status on progress."""
        _update_scan_status(job_id, status_update)

    # Start scan in background
    async def run_scan() -> None:
        """Execute scan operation."""
        try:
            await scan_service.scan_and_categorize(
                user_id=user_id_cleaned,
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
            _clear_active_scan(user_id_cleaned)

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
