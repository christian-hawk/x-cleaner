"""
Pydantic schemas for scan-related API requests and responses.

Defines data models for scan endpoints following REST API best practices.
"""

from typing import Literal, Optional

from pydantic import BaseModel, Field


class ScanRequest(BaseModel):
    """Schema for scan request."""

    user_id: Optional[str] = Field(
        None,
        description="X user ID to scan. If not provided, uses X_USER_ID from environment",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "user_id": "123456789",
            }
        }
    }


class ScanResponse(BaseModel):
    """Schema for scan response."""

    job_id: str = Field(..., description="Unique job identifier for tracking scan progress")
    status: str = Field(..., description="Initial status (usually 'queued' or 'running')")
    message: str = Field(..., description="Status message")

    model_config = {
        "json_schema_extra": {
            "example": {
                "job_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "queued",
                "message": "Scan job created successfully",
            }
        }
    }


class ScanProgress(BaseModel):
    """Schema for scan progress tracking."""

    job_id: str = Field(..., description="Job identifier")
    status: Literal["queued", "running", "completed", "error"] = Field(
        ..., description="Current scan status"
    )
    progress: int = Field(
        ..., ge=0, le=100, description="Progress percentage (0-100)"
    )
    message: str = Field(..., description="Current status message")
    current_step: Optional[str] = Field(
        None, description="Current step in the scan process"
    )
    error: Optional[str] = Field(None, description="Error message if status is 'error'")

    model_config = {
        "json_schema_extra": {
            "example": {
                "job_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "running",
                "progress": 50,
                "message": "Categorizing 500 accounts...",
                "current_step": "categorizing",
                "error": None,
            }
        }
    }
