"""
FastAPI application entry point for X-Cleaner API.

Provides REST API endpoints for account data, categories, and statistics.
"""

from typing import Dict

from dotenv import load_dotenv
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Load environment variables from .env file first
load_dotenv()

from backend.api.routes import accounts, scan, statistics

# Create FastAPI application
app = FastAPI(
    title="X-Cleaner API",
    description="AI-powered X (Twitter) account scanner and categorization API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

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
    for error in errors:
        field = ".".join(str(loc) for loc in error.get("loc", []))
        message = error.get("msg", "Validation error")
        error_messages.append(f"{field}: {message}")
    
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
