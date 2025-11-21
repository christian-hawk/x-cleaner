"""
FastAPI application for X-Cleaner.

This module provides the REST API and WebSocket endpoints for the X-Cleaner
application, including scan management, account retrieval, and real-time updates.
"""

import asyncio
import os
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import BackgroundTasks, FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .api.grok_client import GrokClient
from .api.x_client import XAPIClient
from .config import config
from .core.services.categorizer import CategorizationService
from .database import DatabaseManager
from .models import CategorizedAccount


# Global state for scan progress
scan_progress = {
    "status": "idle",
    "progress": 0,
    "message": "",
    "total_accounts": 0,
    "processed_accounts": 0,
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application.

    Handles startup and shutdown events.
    """
    # Startup
    print("🚀 Starting X-Cleaner API...")
    config.ensure_data_directory()

    # Validate configuration
    if not config.validate():
        print("⚠️  Warning: Some configuration values are missing")

    yield

    # Shutdown
    print("👋 Shutting down X-Cleaner API...")


app = FastAPI(
    title="X-Cleaner API",
    version="1.0.0",
    description="API for scanning and categorizing X (Twitter) accounts",
    lifespan=lifespan,
)

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501",  # Streamlit
        "http://localhost:3000",   # React
        "http://127.0.0.1:8501",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
class ScanRequest(BaseModel):
    """Request model for triggering a scan."""
    user_id: Optional[str] = None
    force_refresh: bool = False


class StatsResponse(BaseModel):
    """Response model for statistics."""
    total_accounts: int
    total_categories: int
    verified_count: int
    last_updated: Optional[datetime]


class AccountsResponse(BaseModel):
    """Response model for paginated accounts."""
    total: int
    accounts: List[CategorizedAccount]
    limit: int
    offset: int


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint returning API information."""
    return {
        "message": "X-Cleaner API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running",
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


# Statistics endpoint
@app.get("/api/stats", response_model=StatsResponse)
async def get_stats():
    """
    Get summary statistics.

    Returns overview statistics including total accounts, categories,
    verified accounts, and last update time.
    """
    db = DatabaseManager()
    accounts = db.get_all_accounts()
    categories = db.get_categories()

    last_updated = None
    if accounts:
        last_updated = max((a.analyzed_at for a in accounts), default=None)

    return StatsResponse(
        total_accounts=len(accounts),
        total_categories=len(categories),
        verified_count=sum(1 for a in accounts if a.verified),
        last_updated=last_updated,
    )


# Categories endpoints
@app.get("/api/categories")
async def get_categories():
    """
    List all discovered categories with metadata.

    Returns list of categories with their descriptions, characteristics,
    and account counts.
    """
    db = DatabaseManager()
    categories = db.get_categories()

    # Update account counts for each category
    for category in categories:
        accounts = db.get_accounts_by_category(category["name"])
        category["account_count"] = len(accounts)

    return {"categories": categories, "total_categories": len(categories)}


@app.get("/api/categories/{category_name}/accounts")
async def get_category_accounts(category_name: str):
    """
    Get all accounts in a specific category.

    Args:
        category_name: Name of the category

    Returns:
        List of accounts in the specified category
    """
    db = DatabaseManager()
    accounts = db.get_accounts_by_category(category_name)

    if not accounts:
        raise HTTPException(
            status_code=404,
            detail=f"Category '{category_name}' not found or has no accounts"
        )

    return accounts


# Accounts endpoint with filtering
@app.get("/api/accounts", response_model=AccountsResponse)
async def get_accounts(
    category: Optional[str] = None,
    verified: Optional[bool] = None,
    search: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
):
    """
    List accounts with filtering and pagination.

    Args:
        category: Filter by category name
        verified: Filter by verified status
        search: Search in username, display name, or bio
        limit: Maximum number of results to return
        offset: Number of results to skip

    Returns:
        Paginated list of accounts
    """
    db = DatabaseManager()
    accounts = db.get_all_accounts()

    # Apply filters
    if category:
        accounts = [a for a in accounts if a.category == category]

    if verified is not None:
        accounts = [a for a in accounts if a.verified == verified]

    if search:
        search = search.lower()
        accounts = [
            a for a in accounts
            if (
                search in a.username.lower()
                or search in a.display_name.lower()
                or (a.bio and search in a.bio.lower())
            )
        ]

    # Pagination
    total = len(accounts)
    accounts = accounts[offset : offset + limit]

    return AccountsResponse(
        total=total,
        accounts=accounts,
        limit=limit,
        offset=offset,
    )


# Scan endpoints
@app.post("/api/scan")
async def trigger_scan(
    scan_request: ScanRequest,
    background_tasks: BackgroundTasks,
):
    """
    Trigger a new scan of X accounts.

    Args:
        scan_request: Scan configuration
        background_tasks: FastAPI background tasks

    Returns:
        Status message and job information
    """
    global scan_progress

    if scan_progress["status"] == "running":
        raise HTTPException(
            status_code=409,
            detail="Scan already in progress",
        )

    # Reset progress
    scan_progress = {
        "status": "running",
        "progress": 0,
        "message": "Starting scan...",
        "total_accounts": 0,
        "processed_accounts": 0,
    }

    # Get user ID from request or config
    user_id = scan_request.user_id or config.X_USER_ID
    if not user_id:
        raise HTTPException(
            status_code=400,
            detail="User ID not provided and X_USER_ID not configured",
        )

    # Add background task
    background_tasks.add_task(
        run_scan,
        user_id=user_id,
        force_refresh=scan_request.force_refresh,
    )

    return {
        "status": "started",
        "message": "Scan initiated successfully",
        "user_id": user_id,
    }


@app.get("/api/scan/status")
async def get_scan_status():
    """
    Get current scan status.

    Returns:
        Current scan progress and status
    """
    return scan_progress


# WebSocket for real-time scan updates
@app.websocket("/ws/scan")
async def websocket_scan(websocket: WebSocket):
    """
    WebSocket endpoint for real-time scan updates.

    Sends scan progress updates to connected clients.
    """
    await websocket.accept()

    try:
        while True:
            await websocket.send_json(scan_progress)
            await asyncio.sleep(1)  # Send updates every second

            if scan_progress["status"] in ["completed", "error", "idle"]:
                break
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        try:
            await websocket.close()
        except:
            pass


# Export endpoint
@app.get("/api/export")
async def export_data(format: str = "json"):
    """
    Export data in various formats.

    Args:
        format: Export format (json, csv)

    Returns:
        Exported data in requested format
    """
    db = DatabaseManager()
    accounts = db.get_all_accounts()
    categories = db.get_categories()

    if format == "json":
        return {
            "accounts": [account.model_dump() for account in accounts],
            "categories": categories,
            "exported_at": datetime.now().isoformat(),
        }
    elif format == "csv":
        # TODO: Implement CSV export
        raise HTTPException(
            status_code=501,
            detail="CSV export not yet implemented",
        )
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format: {format}",
        )


# Background task for running scan
async def run_scan(user_id: str, force_refresh: bool = False):
    """
    Background task to run the scan.

    Args:
        user_id: X user ID to scan
        force_refresh: Whether to force refresh all categorizations
    """
    global scan_progress

    try:
        # Initialize clients
        x_client = XAPIClient()
        categorization_service = CategorizationService()
        db = DatabaseManager()

        # Fetch accounts
        scan_progress["message"] = "Fetching accounts from X..."
        scan_progress["progress"] = 10

        accounts = await x_client.get_all_following(user_id)
        scan_progress["total_accounts"] = len(accounts)

        if not accounts:
            scan_progress = {
                "status": "error",
                "progress": 0,
                "message": "No accounts found",
                "total_accounts": 0,
                "processed_accounts": 0,
            }
            return

        scan_progress["message"] = f"Found {len(accounts)} accounts"
        scan_progress["progress"] = 30

        # Categorize accounts
        scan_progress["message"] = "Discovering categories and categorizing accounts..."
        scan_progress["progress"] = 50

        categories_metadata, categorized = await categorization_service.categorize_accounts(
            accounts,
            force_refresh=force_refresh,
        )

        scan_progress["processed_accounts"] = len(categorized)

        # Save results
        scan_progress["message"] = "Saving results..."
        scan_progress["progress"] = 80

        db.save_accounts(categorized)
        if categories_metadata:
            db.save_categories(categories_metadata)

        # Complete
        scan_progress = {
            "status": "completed",
            "progress": 100,
            "message": (
                f"Scan completed! {len(categorized)} accounts categorized into "
                f"{categories_metadata.get('total_categories', 0)} categories"
            ),
            "total_accounts": len(accounts),
            "processed_accounts": len(categorized),
        }

        # Close client
        await x_client.close()

    except Exception as e:
        scan_progress = {
            "status": "error",
            "progress": 0,
            "message": f"Error: {str(e)}",
            "total_accounts": scan_progress.get("total_accounts", 0),
            "processed_accounts": scan_progress.get("processed_accounts", 0),
        }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.RELOAD,
    )
