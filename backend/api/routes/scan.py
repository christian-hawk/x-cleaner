"""
FastAPI routes for scan operations.

Provides endpoints for triggering scans and monitoring progress.
"""

import asyncio
import uuid
from typing import Annotated, Dict

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status

from backend.config import config
from backend.core.progress_tracker import progress_tracker
from backend.core.services.scan_service import ScanService
from backend.dependencies import get_scan_service

router = APIRouter(prefix="/api/scan", tags=["scan"])


async def run_scan_task(
    job_id: str,
    user_id: str,
    scan_service: ScanService,
) -> None:
    """
    Execute scan in background.

    Args:
        job_id: Unique job identifier.
        user_id: X user ID to scan.
        scan_service: Scan service instance.
    """

    def progress_callback(message: str, progress: int) -> None:
        """Update progress tracker."""
        progress_tracker.update_progress(
            job_id=job_id,
            message=message,
            progress=progress,
        )

    try:
        # Execute scan with progress callbacks
        result = await scan_service.execute_scan(
            user_id=user_id,
            progress_callback=progress_callback,
        )

        if result.success:
            progress_tracker.complete_job(
                job_id=job_id,
                accounts_scanned=result.accounts_scanned,
                categories_discovered=result.categories_discovered,
            )
        else:
            progress_tracker.fail_job(
                job_id=job_id,
                error_message=result.error_message or "Unknown error",
            )

    except Exception as e:
        progress_tracker.fail_job(
            job_id=job_id,
            error_message=f"Unexpected error: {str(e)}",
        )


@router.post("")
async def trigger_scan(
    background_tasks: BackgroundTasks,
    user_id: str = "",
    scan_service: ScanService = Depends(get_scan_service),
) -> Dict[str, str]:
    """
    Trigger new scan in background.

    Args:
        background_tasks: FastAPI background tasks handler.
        user_id: X user ID to scan (optional, defaults to config).
        scan_service: Injected scan service.

    Returns:
        Job information with job_id and status.

    Raises:
        HTTPException: If configuration is invalid.
    """
    # Use configured user ID if not provided
    if not user_id:
        user_id = config.X_USER_ID

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="X_USER_ID not configured and not provided in request",
        )

    # Generate unique job ID
    job_id = str(uuid.uuid4())

    # Create job in tracker
    progress_tracker.create_job(job_id)

    # Start background task
    background_tasks.add_task(
        run_scan_task,
        job_id,
        user_id,
        scan_service,
    )

    return {
        "job_id": job_id,
        "status": "started",
        "message": "Scan job started successfully",
    }


@router.get("/{job_id}/status")
async def get_scan_status(job_id: str) -> Dict:
    """
    Get scan progress status.

    Args:
        job_id: Job identifier.

    Returns:
        Progress information dictionary.

    Raises:
        HTTPException: If job not found.
    """
    progress = progress_tracker.get_job(job_id)

    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scan job '{job_id}' not found",
        )

    return progress


@router.delete("/{job_id}")
async def cancel_scan(job_id: str) -> Dict[str, str]:
    """
    Cancel/remove scan job.

    Note: This only removes the job from tracking. Background tasks
    cannot be cancelled once started.

    Args:
        job_id: Job identifier.

    Returns:
        Confirmation message.

    Raises:
        HTTPException: If job not found.
    """
    progress = progress_tracker.get_job(job_id)

    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scan job '{job_id}' not found",
        )

    progress_tracker.remove_job(job_id)

    return {
        "job_id": job_id,
        "message": "Job removed from tracking",
    }
