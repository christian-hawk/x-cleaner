"""
FastAPI application entry point for X-Cleaner API.

Provides REST API endpoints for account data, categories, and statistics.
"""

import json
import logging
from typing import Dict

from dotenv import load_dotenv
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

# Load environment variables from .env file first
load_dotenv()

from backend.api.routes import accounts, scan, statistics

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log request details for debugging."""
    
    async def dispatch(self, request: Request, call_next):
        # Only log POST requests to /api/scan
        if request.method == "POST" and request.url.path == "/api/scan":
            try:
                body_bytes = await request.body()
                if body_bytes:
                    try:
                        body_json = json.loads(body_bytes.decode('utf-8'))
                        logger.info("=== INCOMING SCAN REQUEST ===")
                        logger.info("Request body (JSON): %s", json.dumps(body_json, indent=2))
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        logger.info("Request body (raw): %s", body_bytes.decode('utf-8', errors='replace'))
                    
                    # Restore body for FastAPI to read
                    async def receive():
                        return {"type": "http.request", "body": body_bytes}
                    request._receive = receive
            except Exception as e:
                logger.warning("Could not log request body: %s", e)
        
        response = await call_next(request)
        return response

# Create FastAPI application
app = FastAPI(
    title="X-Cleaner API",
    description="AI-powered X (Twitter) account scanner and categorization API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add request logging middleware (before CORS)
app.add_middleware(RequestLoggingMiddleware)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(accounts.router)
app.include_router(statistics.router)
app.include_router(scan.router)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    Custom handler for validation errors to provide clearer error messages.
    
    Args:
        request: FastAPI request object
        exc: Validation error exception
        
    Returns:
        JSON response with error details
    """
    errors = exc.errors()
    error_messages = []
    
    logger.error("=== VALIDATION ERROR ===")
    logger.error("Request path: %s", request.url.path)
    logger.error("Request method: %s", request.method)
    logger.error("Request URL: %s", request.url)
    
    # Log query parameters if any
    if request.url.query:
        logger.error("Query parameters: %s", request.url.query)
    
    for error in errors:
        field = ".".join(str(loc) for loc in error.get("loc", []))
        message = error.get("msg", "Validation error")
        error_type = error.get("type", "unknown")
        input_value = error.get("input", "N/A")
        error_messages.append(f"{field}: {message}")
        logger.error("Validation error - Field: %s, Type: %s, Message: %s, Input: %r", 
                     field, error_type, message, input_value)
    
    logger.error("Full error details: %s", errors)
    
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "detail": "; ".join(error_messages),
            "errors": errors,
        },
    )


@app.get("/")
async def root() -> Dict[str, str]:
    """
    Root endpoint providing API information.

    Returns:
        API information dictionary.
    """
    return {
        "name": "X-Cleaner API",
        "version": "1.0.0",
        "description": "AI-powered X account analysis and categorization",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint for monitoring.

    Returns:
        Health status dictionary.
    """
    return {
        "status": "healthy",
        "service": "x-cleaner-api",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
