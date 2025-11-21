"""
FastAPI application entry point for X-Cleaner API.

Provides REST API endpoints for account data, categories, and statistics.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import accounts, statistics

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


@app.get("/")
async def root():
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
async def health_check():
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
