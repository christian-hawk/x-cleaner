"""
Progress tracking system for background scan jobs.

Provides in-memory tracking of scan job progress with thread-safe access.
For production, consider using Redis or similar distributed cache.
"""

import threading
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional


@dataclass
class ScanProgress:
    """Progress information for a scan job."""

    job_id: str
    status: str  # 'started', 'running', 'complete', 'error'
    message: str
    progress: int  # 0-100
    accounts_scanned: int = 0
    categories_discovered: int = 0
    error_message: Optional[str] = None
    started_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "job_id": self.job_id,
            "status": self.status,
            "message": self.message,
            "progress": self.progress,
            "accounts_scanned": self.accounts_scanned,
            "categories_discovered": self.categories_discovered,
            "error_message": self.error_message,
            "started_at": self.started_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class ProgressTracker:
    """
    Thread-safe progress tracker for scan jobs.

    Stores progress information in memory with thread-safe access.
    """

    def __init__(self) -> None:
        """Initialize progress tracker."""
        self._jobs: Dict[str, ScanProgress] = {}
        self._lock = threading.Lock()

    def create_job(self, job_id: str) -> None:
        """
        Create new scan job.

        Args:
            job_id: Unique job identifier.
        """
        with self._lock:
            self._jobs[job_id] = ScanProgress(
                job_id=job_id,
                status="started",
                message="Scan job created",
                progress=0,
            )

    def update_progress(
        self,
        job_id: str,
        message: str,
        progress: int,
        status: str = "running",
    ) -> None:
        """
        Update job progress.

        Args:
            job_id: Job identifier.
            message: Progress message.
            progress: Progress percentage (0-100).
            status: Job status.
        """
        with self._lock:
            if job_id in self._jobs:
                job = self._jobs[job_id]
                job.message = message
                job.progress = progress
                job.status = status
                job.updated_at = datetime.now()

    def complete_job(
        self,
        job_id: str,
        accounts_scanned: int,
        categories_discovered: int,
    ) -> None:
        """
        Mark job as complete.

        Args:
            job_id: Job identifier.
            accounts_scanned: Number of accounts scanned.
            categories_discovered: Number of categories discovered.
        """
        with self._lock:
            if job_id in self._jobs:
                job = self._jobs[job_id]
                job.status = "complete"
                job.message = "Scan completed successfully"
                job.progress = 100
                job.accounts_scanned = accounts_scanned
                job.categories_discovered = categories_discovered
                job.updated_at = datetime.now()

    def fail_job(self, job_id: str, error_message: str) -> None:
        """
        Mark job as failed.

        Args:
            job_id: Job identifier.
            error_message: Error description.
        """
        with self._lock:
            if job_id in self._jobs:
                job = self._jobs[job_id]
                job.status = "error"
                job.message = "Scan failed"
                job.error_message = error_message
                job.updated_at = datetime.now()

    def get_job(self, job_id: str) -> Optional[Dict]:
        """
        Get job progress information.

        Args:
            job_id: Job identifier.

        Returns:
            Job progress dictionary or None if not found.
        """
        with self._lock:
            if job_id in self._jobs:
                return self._jobs[job_id].to_dict()
            return None

    def remove_job(self, job_id: str) -> None:
        """
        Remove job from tracker.

        Args:
            job_id: Job identifier.
        """
        with self._lock:
            self._jobs.pop(job_id, None)


# Global singleton instance
progress_tracker = ProgressTracker()
