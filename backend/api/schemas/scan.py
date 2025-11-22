"""
Pydantic schemas for scan-related API requests and responses.

Defines data models for scan endpoints and WebSocket messages.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class ScanRequest(BaseModel):
    """Schema for scan request body."""

    user_id: str = Field(..., description="X user ID to scan following accounts for")
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user_id": "123456789"
            }
        }
    )


class ScanResponse(BaseModel):
    """Schema for scan response with job identifier."""

    job_id: str = Field(..., description="Unique job identifier for tracking scan progress")
    status: str = Field(..., description="Initial scan status")
    message: str = Field(..., description="Status message")
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "job_id": "scan_20250120_153000_123456789",
                "status": "running",
                "message": "Scan started successfully"
            }
        }
    )


class ScanProgress(BaseModel):
    """Schema for scan progress updates."""

    job_id: str = Field(..., description="Job identifier")
    status: str = Field(..., description="Current status (pending, running, completed, error)")
    progress: float = Field(..., ge=0.0, le=100.0, description="Progress percentage")
    current_step: str = Field(..., description="Current scan step")
    message: str = Field(..., description="Status message")
    current: int = Field(0, ge=0, description="Current item being processed")
    total: int = Field(0, ge=0, description="Total items to process")
    accounts_fetched: int = Field(0, ge=0, description="Number of accounts fetched")
    accounts_categorized: int = Field(0, ge=0, description="Number of accounts categorized")
    accounts_saved: int = Field(0, ge=0, description="Number of accounts saved")
    error: Optional[str] = Field(None, description="Error message if status is error")
    started_at: Optional[datetime] = Field(None, description="Scan start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Scan completion timestamp")
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "job_id": "scan_20250120_153000_123456789",
                "status": "running",
                "progress": 45.5,
                "current_step": "categorize_accounts",
                "message": "Categorizing accounts...",
                "current": 450,
                "total": 1000,
                "accounts_fetched": 1000,
                "accounts_categorized": 450,
                "accounts_saved": 0,
                "error": None,
                "started_at": "2025-01-20T15:30:00Z",
                "completed_at": None
            }
        }
    )


class ScanStatus(BaseModel):
    """Schema for scan status response."""

    job_id: str = Field(..., description="Job identifier")
    status: str = Field(..., description="Current status")
    progress: float = Field(..., ge=0.0, le=100.0, description="Progress percentage")
    message: str = Field(..., description="Status message")
    error: Optional[str] = Field(None, description="Error message if failed")
    started_at: Optional[datetime] = Field(None, description="Start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "job_id": "scan_20250120_153000_123456789",
                "status": "completed",
                "progress": 100.0,
                "message": "Scan completed successfully",
                "error": None,
                "started_at": "2025-01-20T15:30:00Z",
                "completed_at": "2025-01-20T15:35:00Z"
            }
        }
    )


class WebSocketProgressMessage(BaseModel):
    """Schema for WebSocket progress messages."""

    type: str = Field("progress", description="Message type")
    job_id: str = Field(..., description="Job identifier")
    status: str = Field(..., description="Current status")
    progress: float = Field(..., ge=0.0, le=100.0, description="Progress percentage")
    message: str = Field(..., description="Status message")
    current: int = Field(0, ge=0, description="Current item")
    total: int = Field(0, ge=0, description="Total items")
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "type": "progress",
                "job_id": "scan_20250120_153000_123456789",
                "status": "running",
                "progress": 45.5,
                "message": "Categorizing accounts...",
                "current": 450,
                "total": 1000
            }
        }
    )
