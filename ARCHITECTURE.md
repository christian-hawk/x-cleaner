# X-Cleaner Architecture & Design Patterns

## Table of Contents

1. [System Architecture](#1-system-architecture)
2. [Design Patterns](#2-design-patterns)
3. [Code Conventions](#3-code-conventions)
4. [Component Architecture](#4-component-architecture)
5. [Error Handling](#5-error-handling)
6. [Logging Strategy](#6-logging-strategy)
7. [Testing Strategy](#7-testing-strategy)
8. [File Organization](#8-file-organization)
9. [Type System](#9-type-system)
10. [API Design Principles](#10-api-design-principles)

---

## 1. System Architecture

### 1.1 Layered Architecture

X-Cleaner follows a **4-layer architecture** pattern:

```
┌─────────────────────────────────────────────┐
│         PRESENTATION LAYER                  │
│  • Streamlit Dashboard (streamlit_app/)     │
│  • React Frontend (frontend/)               │
│  • CLI Interface (backend/cli/)             │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│         API LAYER                           │
│  • FastAPI Routes (backend/api/routes.py)   │
│  • WebSocket Handlers (websockets.py)       │
│  • Request/Response Models (schemas.py)     │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│         BUSINESS LOGIC LAYER                │
│  • Scanner (backend/core/scanner.py)        │
│  • Categorizer (backend/core/categorizer.py)│
│  • Statistics (backend/core/statistics.py)  │
│  • Exporters (backend/core/exporters.py)    │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│         DATA LAYER                          │
│  • Database Manager (backend/db/manager.py) │
│  • Models (backend/db/models.py)            │
│  • X API Client (backend/api/x_client.py)   │
│  • Grok Client (backend/api/grok_client.py) │
└─────────────────────────────────────────────┘
```

**Layer Responsibilities:**

- **Presentation**: User interaction, display logic, input validation
- **API**: Request handling, authentication, response formatting
- **Business Logic**: Core application logic, orchestration, business rules
- **Data**: Persistence, external API integration, data retrieval

**Key Principle**: Layers can only communicate with adjacent layers (no skipping layers).

### 1.2 Dependency Direction

Dependencies flow **downward and inward**:
- Presentation depends on API
- API depends on Business Logic
- Business Logic depends on Data
- Data depends on nothing (pure infrastructure)

**Example:**
```python
# ✅ CORRECT
from backend.core.scanner import Scanner  # API layer using Business Logic
from backend.db.manager import DatabaseManager  # Business Logic using Data

# ❌ INCORRECT
from streamlit_app.pages.dashboard import render_stats  # Business Logic should NOT import from Presentation
```

---

## 2. Design Patterns

### 2.1 Repository Pattern

**Purpose**: Abstracts data access logic from business logic.

**Implementation:**
```python
# backend/db/repositories/account_repository.py
from typing import List, Optional
from backend.db.models import Account

class AccountRepository:
    """Repository for Account data access."""

    def __init__(self, db_manager: DatabaseManager):
        self._db = db_manager

    def get_by_username(self, username: str) -> Optional[Account]:
        """Retrieve account by username."""
        pass

    def get_all(self, category: Optional[str] = None) -> List[Account]:
        """Retrieve all accounts, optionally filtered by category."""
        pass

    def save(self, account: Account) -> None:
        """Persist account to database."""
        pass

    def bulk_save(self, accounts: List[Account]) -> None:
        """Persist multiple accounts efficiently."""
        pass
```

**Benefits:**
- Single source of truth for data operations
- Easy to mock for testing
- Can swap database implementations

### 2.2 Service Layer Pattern

**Purpose**: Encapsulates business logic and orchestrates operations.

**Implementation:**
```python
# backend/core/services/scan_service.py
from backend.db.repositories.account_repository import AccountRepository
from backend.api.x_client import XClient
from backend.api.grok_client import GrokClient

class ScanService:
    """Service for orchestrating account scanning."""

    def __init__(
        self,
        account_repo: AccountRepository,
        x_client: XClient,
        grok_client: GrokClient
    ):
        self._accounts = account_repo
        self._x_client = x_client
        self._grok = grok_client

    async def scan_and_categorize(
        self,
        user_id: str,
        progress_callback: Optional[Callable] = None
    ) -> ScanResult:
        """
        Complete scan workflow:
        1. Fetch accounts from X
        2. Discover categories with Grok
        3. Categorize all accounts
        4. Save to database
        """
        # Orchestration logic here
        pass
```

**Benefits:**
- Business logic separated from API/presentation
- Reusable across CLI, API, and web UI
- Testable without HTTP layer

### 2.3 Factory Pattern

**Purpose**: Create complex objects with multiple configurations.

**Implementation:**
```python
# backend/core/factories/client_factory.py
from backend.api.x_client import XClient
from backend.api.grok_client import GrokClient
from backend.config import Settings

class ClientFactory:
    """Factory for creating API clients."""

    @staticmethod
    def create_x_client(settings: Settings) -> XClient:
        """Create configured X API client."""
        return XClient(
            bearer_token=settings.X_API_BEARER_TOKEN,
            rate_limit=settings.X_RATE_LIMIT,
            timeout=settings.X_TIMEOUT
        )

    @staticmethod
    def create_grok_client(settings: Settings) -> GrokClient:
        """Create configured Grok API client."""
        return GrokClient(
            api_key=settings.XAI_API_KEY,
            model=settings.GROK_MODEL,
            max_retries=settings.GROK_MAX_RETRIES
        )
```

### 2.4 Strategy Pattern

**Purpose**: Swap algorithms at runtime (e.g., different categorization strategies).

**Implementation:**
```python
# backend/core/strategies/categorization_strategy.py
from abc import ABC, abstractmethod
from typing import List
from backend.db.models import Account, Category

class CategorizationStrategy(ABC):
    """Abstract base for categorization strategies."""

    @abstractmethod
    async def discover_categories(self, accounts: List[Account]) -> List[Category]:
        """Discover categories from accounts."""
        pass

    @abstractmethod
    async def categorize(self, account: Account, categories: List[Category]) -> str:
        """Assign account to a category."""
        pass

class GrokCategorizationStrategy(CategorizationStrategy):
    """Grok-based emergent categorization."""

    async def discover_categories(self, accounts: List[Account]) -> List[Category]:
        # Grok discovery implementation
        pass

class RuleBasedCategorizationStrategy(CategorizationStrategy):
    """Rule-based categorization (for testing/fallback)."""

    async def discover_categories(self, accounts: List[Account]) -> List[Category]:
        # Rule-based implementation
        pass
```

**Usage:**
```python
# Choose strategy at runtime
if settings.USE_AI_CATEGORIZATION:
    strategy = GrokCategorizationStrategy(grok_client)
else:
    strategy = RuleBasedCategorizationStrategy()

categorizer = Categorizer(strategy)
```

### 2.5 Observer Pattern (for WebSocket Progress)

**Purpose**: Notify multiple listeners of scan progress.

**Implementation:**
```python
# backend/core/observers/scan_observer.py
from abc import ABC, abstractmethod
from typing import List

class ScanObserver(ABC):
    """Abstract observer for scan events."""

    @abstractmethod
    async def on_progress(self, current: int, total: int, message: str):
        """Called when scan makes progress."""
        pass

    @abstractmethod
    async def on_complete(self, result: ScanResult):
        """Called when scan completes."""
        pass

    @abstractmethod
    async def on_error(self, error: Exception):
        """Called when scan encounters error."""
        pass

class WebSocketScanObserver(ScanObserver):
    """WebSocket-based progress updates."""

    def __init__(self, websocket: WebSocket):
        self._ws = websocket

    async def on_progress(self, current: int, total: int, message: str):
        await self._ws.send_json({
            "type": "progress",
            "current": current,
            "total": total,
            "message": message
        })
```

### 2.6 Dependency Injection

**Purpose**: Decouple components and improve testability.

**Implementation:**
```python
# backend/dependencies.py
from fastapi import Depends
from backend.db.manager import DatabaseManager
from backend.core.services.scan_service import ScanService

def get_db() -> DatabaseManager:
    """Dependency for database access."""
    db = DatabaseManager()
    try:
        yield db
    finally:
        db.close()

def get_scan_service(db: DatabaseManager = Depends(get_db)) -> ScanService:
    """Dependency for scan service."""
    account_repo = AccountRepository(db)
    x_client = ClientFactory.create_x_client(settings)
    grok_client = ClientFactory.create_grok_client(settings)
    return ScanService(account_repo, x_client, grok_client)
```

**Usage in FastAPI:**
```python
@app.post("/api/scan")
async def trigger_scan(
    user_id: str,
    scan_service: ScanService = Depends(get_scan_service)
):
    result = await scan_service.scan_and_categorize(user_id)
    return result
```

---

## 3. Code Conventions

### 3.1 Python Style Guide

**Base Standard**: PEP 8 with modifications

**Line Length**: 88 characters (Black formatter default)

**Imports Order**:
```python
# 1. Standard library
import os
from typing import List, Optional

# 2. Third-party libraries
import httpx
from fastapi import FastAPI

# 3. Local application
from backend.db.models import Account
from backend.core.scanner import Scanner
```

**Naming Conventions**:
```python
# Classes: PascalCase
class AccountRepository:
    pass

# Functions/methods: snake_case
def scan_accounts():
    pass

# Constants: UPPER_SNAKE_CASE
MAX_RETRIES = 3
API_BASE_URL = "https://api.x.com"

# Private members: leading underscore
class Scanner:
    def __init__(self):
        self._rate_limiter = RateLimiter()  # Private

    def _fetch_batch(self):  # Private method
        pass

# Type aliases: PascalCase
AccountList = List[Account]
```

**String Quotes**:
- Use double quotes `"` for regular strings
- Use single quotes `'` for dict keys and f-string embedded quotes

```python
# ✅ CORRECT
name = "John Doe"
data = {"user_id": "123", "name": f"Hello {name}"}

# ❌ INCORRECT
name = 'John Doe'
data = {'user_id': '123'}
```

### 3.2 Async/Await Conventions

**Rule**: Prefix all async functions with `async_` for clarity (when not obvious from context).

```python
# ✅ CORRECT - Obvious from context
async def fetch_accounts(user_id: str) -> List[Account]:
    pass

# ✅ CORRECT - Using async_ prefix when mixed with sync
def process_accounts(accounts: List[Account]) -> None:
    """Sync processing."""
    pass

async def async_process_accounts(accounts: List[Account]) -> None:
    """Async processing."""
    pass
```

**Always use `async with` for async context managers**:
```python
# ✅ CORRECT
async with httpx.AsyncClient() as client:
    response = await client.get(url)

# ❌ INCORRECT
client = httpx.AsyncClient()
response = await client.get(url)
await client.aclose()  # Easy to forget!
```

### 3.3 Docstring Format (Google Style)

```python
def categorize_account(
    account: Account,
    categories: List[Category],
    confidence_threshold: float = 0.7
) -> CategoryAssignment:
    """Categorize an account using AI analysis.

    Analyzes account profile and activity to assign it to the most
    appropriate category from the discovered categories.

    Args:
        account: The account to categorize.
        categories: List of discovered categories to choose from.
        confidence_threshold: Minimum confidence score (0-1) required
            for category assignment. Defaults to 0.7.

    Returns:
        CategoryAssignment with category ID and confidence score.

    Raises:
        CategorizationError: If AI service fails or confidence too low.
        ValueError: If categories list is empty.

    Example:
        >>> categories = discover_categories(accounts)
        >>> assignment = categorize_account(account, categories)
        >>> print(f"Category: {assignment.category_id} ({assignment.confidence:.2f})")
    """
    pass
```

### 3.4 Comments

**When to comment**:
- Complex algorithms that aren't immediately obvious
- Business logic decisions
- Workarounds for known issues
- Performance-critical sections

**When NOT to comment**:
- Obvious code (e.g., `# Increment counter` for `counter += 1`)
- What the code does (use clear names instead)

```python
# ✅ GOOD COMMENTS
# Rate limit: X API allows 500 requests per 15 minutes
# We batch requests to stay under this limit
await asyncio.sleep(self._calculate_delay())

# Workaround: Grok API sometimes returns malformed JSON
# for very long category descriptions. Truncate to 500 chars.
description = description[:500]

# ❌ BAD COMMENTS
# Get the username
username = account.username

# Loop through accounts
for account in accounts:
    pass
```

### 3.5 Error Messages

**Format**: `"<Context>: <specific error>. <suggestion>"`

```python
# ✅ GOOD
raise ValueError(
    f"Invalid user_id '{user_id}': must be numeric. "
    "Check your X API credentials in .env file."
)

# ❌ BAD
raise ValueError("Invalid user_id")
```

---

## 4. Component Architecture

### 4.1 Backend Component Structure

```
backend/
├── main.py                      # FastAPI app entry point
├── config.py                    # Settings (Pydantic BaseSettings)
├── dependencies.py              # FastAPI dependencies
│
├── api/                         # External API clients
│   ├── __init__.py
│   ├── x_client.py              # X API client
│   ├── grok_client.py           # Grok API client
│   └── base_client.py           # Shared HTTP client logic
│
├── core/                        # Business logic
│   ├── __init__.py
│   ├── scanner.py               # Main scanning orchestration
│   ├── categorizer.py           # Categorization logic
│   ├── statistics.py            # Analytics calculations
│   ├── exporters.py             # Data export (JSON/CSV/PDF)
│   │
│   ├── services/                # Service layer
│   │   ├── scan_service.py
│   │   └── analytics_service.py
│   │
│   ├── strategies/              # Strategy pattern implementations
│   │   └── categorization_strategy.py
│   │
│   └── observers/               # Observer pattern implementations
│       └── scan_observer.py
│
├── db/                          # Data layer
│   ├── __init__.py
│   ├── manager.py               # Database connection manager
│   ├── models.py                # SQLAlchemy ORM models
│   │
│   └── repositories/            # Repository pattern
│       ├── account_repository.py
│       └── category_repository.py
│
├── routes/                      # FastAPI routes
│   ├── __init__.py
│   ├── scan.py                  # Scan endpoints
│   ├── accounts.py              # Account CRUD endpoints
│   ├── categories.py            # Category endpoints
│   ├── statistics.py            # Analytics endpoints
│   └── websockets.py            # WebSocket handlers
│
├── schemas/                     # Pydantic models (request/response)
│   ├── __init__.py
│   ├── account.py               # Account-related schemas
│   ├── category.py              # Category-related schemas
│   └── scan.py                  # Scan-related schemas
│
├── middleware/                  # FastAPI middleware
│   ├── error_handler.py         # Global error handling
│   ├── logging.py               # Request/response logging
│   └── cors.py                  # CORS configuration
│
├── utils/                       # Utility functions
│   ├── rate_limiter.py          # Rate limiting utilities
│   ├── cache.py                 # Caching helpers
│   └── validators.py            # Custom validators
│
└── cli/                         # CLI interface
    ├── __init__.py
    └── commands.py              # Click commands
```

### 4.2 Component Communication Rules

**API Clients** (`backend/api/`):
- Should be **stateless** (except for connection pooling)
- Should handle **retries and rate limiting** internally
- Should raise **domain-specific exceptions**, not HTTP errors

```python
# ✅ CORRECT
class XClient:
    async def fetch_following(self, user_id: str) -> List[Dict]:
        try:
            response = await self._http.get(f"/users/{user_id}/following")
            return response.json()["data"]
        except httpx.HTTPError as e:
            raise XAPIError(f"Failed to fetch following: {e}") from e
```

**Repositories** (`backend/db/repositories/`):
- Should **only** perform database operations
- Should **not** contain business logic
- Should return domain models, not DB models

```python
# ✅ CORRECT
class AccountRepository:
    def get_all(self) -> List[Account]:
        db_accounts = self._session.query(AccountModel).all()
        return [Account.from_orm(db_acc) for db_acc in db_accounts]

# ❌ INCORRECT - Business logic in repository
class AccountRepository:
    def get_popular_accounts(self) -> List[Account]:
        accounts = self.get_all()
        # ❌ This is business logic, belongs in service layer
        return sorted(accounts, key=lambda a: a.followers, reverse=True)[:5]
```

**Services** (`backend/core/services/`):
- Orchestrate multiple repositories and API clients
- Contain business logic
- Should be **transaction-aware**

```python
# ✅ CORRECT
class ScanService:
    async def scan_and_categorize(self, user_id: str) -> ScanResult:
        # 1. Fetch from X API
        accounts_data = await self._x_client.fetch_following(user_id)

        # 2. Discover categories (business logic)
        categories = await self._grok_client.discover_categories(accounts_data)

        # 3. Save to database (transaction)
        async with self._db.transaction():
            self._category_repo.bulk_save(categories)
            self._account_repo.bulk_save(accounts_data)

        return ScanResult(total=len(accounts_data), categories=len(categories))
```

### 4.3 Frontend Component Structure (Streamlit)

```
streamlit_app/
├── app.py                       # Main dashboard entry point
│
├── pages/                       # Multi-page app
│   ├── 1_Overview.py            # Overview dashboard
│   ├── 2_Categories.py          # Category exploration
│   ├── 3_Accounts.py            # Account browser
│   └── 4_Analytics.py           # Deep analytics
│
├── components/                  # Reusable components
│   ├── __init__.py
│   ├── charts.py                # Plotly chart builders
│   ├── filters.py               # Filter widgets
│   ├── tables.py                # Data table displays
│   └── scan_progress.py         # Scan progress bar
│
├── api_client.py                # Backend API client
├── state.py                     # Session state management
└── config.py                    # Frontend configuration
```

**Component Principles**:
- Each component should be **pure** (same input = same output)
- Use `@st.cache_data` for expensive computations
- Use `st.session_state` for app state

```python
# components/charts.py
import plotly.express as px
import streamlit as st

@st.cache_data
def create_category_pie_chart(categories: List[dict]) -> go.Figure:
    """Create pie chart for category distribution.

    Args:
        categories: List of dicts with 'name' and 'count' keys.

    Returns:
        Plotly figure object.
    """
    df = pd.DataFrame(categories)
    fig = px.pie(df, values="count", names="name", title="Category Distribution")
    return fig
```

---

## 5. Error Handling

### 5.1 Exception Hierarchy

```python
# backend/exceptions.py

class XCleanerError(Exception):
    """Base exception for all X-Cleaner errors."""

    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

# API Errors
class APIError(XCleanerError):
    """Base for external API errors."""
    pass

class XAPIError(APIError):
    """X API errors (rate limit, auth, etc.)."""
    pass

class GrokAPIError(APIError):
    """Grok API errors (timeout, invalid response, etc.)."""
    pass

# Database Errors
class DatabaseError(XCleanerError):
    """Database operation errors."""
    pass

# Business Logic Errors
class CategorizationError(XCleanerError):
    """Category discovery/assignment errors."""
    pass

class ValidationError(XCleanerError):
    """Input validation errors."""
    pass
```

### 5.2 Error Handling Patterns

**In API Clients** - Wrap and translate:
```python
class XClient:
    async def fetch_following(self, user_id: str) -> List[Dict]:
        try:
            response = await self._http.get(f"/users/{user_id}/following")
            response.raise_for_status()
            return response.json()["data"]

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                retry_after = e.response.headers.get("x-rate-limit-reset")
                raise XAPIError(
                    "Rate limit exceeded",
                    details={"retry_after": retry_after}
                ) from e
            elif e.response.status_code == 401:
                raise XAPIError("Invalid authentication credentials") from e
            else:
                raise XAPIError(f"X API request failed: {e}") from e

        except httpx.TimeoutException as e:
            raise XAPIError("X API request timed out") from e
```

**In Services** - Handle and enrich:
```python
class ScanService:
    async def scan_and_categorize(self, user_id: str) -> ScanResult:
        try:
            accounts = await self._x_client.fetch_following(user_id)
        except XAPIError as e:
            logger.error(f"Failed to fetch accounts for {user_id}: {e}")
            raise CategorizationError(
                f"Unable to scan accounts: {e.message}",
                details={"user_id": user_id, **e.details}
            ) from e

        if not accounts:
            raise ValidationError(
                f"User {user_id} is not following any accounts",
                details={"user_id": user_id}
            )

        # Continue processing...
```

**In FastAPI Routes** - Convert to HTTP responses:
```python
# backend/middleware/error_handler.py
from fastapi import Request, status
from fastapi.responses import JSONResponse

@app.exception_handler(XCleanerError)
async def xcleaner_exception_handler(request: Request, exc: XCleanerError):
    """Convert XCleanerError to JSON response."""

    status_map = {
        ValidationError: status.HTTP_400_BAD_REQUEST,
        XAPIError: status.HTTP_502_BAD_GATEWAY,
        GrokAPIError: status.HTTP_502_BAD_GATEWAY,
        DatabaseError: status.HTTP_500_INTERNAL_SERVER_ERROR,
    }

    status_code = status_map.get(type(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)

    return JSONResponse(
        status_code=status_code,
        content={
            "error": exc.__class__.__name__,
            "message": exc.message,
            "details": exc.details
        }
    )
```

### 5.3 Retry Strategy

**Exponential Backoff with Jitter**:
```python
# backend/utils/retry.py
import asyncio
import random
from typing import Callable, TypeVar

T = TypeVar("T")

async def retry_with_backoff(
    func: Callable[[], T],
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exceptions: tuple = (Exception,)
) -> T:
    """Retry function with exponential backoff and jitter.

    Args:
        func: Async function to retry.
        max_retries: Maximum number of retry attempts.
        base_delay: Initial delay in seconds.
        max_delay: Maximum delay in seconds.
        exceptions: Tuple of exceptions to catch and retry.

    Returns:
        Result of successful function call.

    Raises:
        Last exception if all retries fail.
    """
    last_exception = None

    for attempt in range(max_retries + 1):
        try:
            return await func()
        except exceptions as e:
            last_exception = e

            if attempt == max_retries:
                break

            # Exponential backoff: 2^attempt * base_delay
            delay = min(base_delay * (2 ** attempt), max_delay)

            # Add jitter: random ±25%
            jitter = delay * 0.25 * (2 * random.random() - 1)
            delay += jitter

            logger.warning(
                f"Attempt {attempt + 1}/{max_retries} failed: {e}. "
                f"Retrying in {delay:.2f}s..."
            )

            await asyncio.sleep(delay)

    raise last_exception
```

**Usage**:
```python
# Retry Grok API calls
async def categorize_with_retry(account: Account) -> str:
    return await retry_with_backoff(
        lambda: self._grok.categorize(account),
        max_retries=3,
        base_delay=2.0,
        exceptions=(GrokAPIError,)
    )
```

---

## 6. Logging Strategy

### 6.1 Logging Levels

| Level | Use Case | Example |
|-------|----------|---------|
| **DEBUG** | Detailed diagnostic info | Variable values, function entry/exit |
| **INFO** | General informational events | "Scan started", "100 accounts fetched" |
| **WARNING** | Unexpected but handled situations | Rate limit hit, cache miss |
| **ERROR** | Errors that prevent specific operation | API call failed, invalid data |
| **CRITICAL** | System-level failures | Database unreachable, config missing |

### 6.2 Structured Logging

**Configuration**:
```python
# backend/utils/logging.py
import logging
import sys
from pythonjsonlogger import jsonlogger

def setup_logging(level: str = "INFO") -> None:
    """Configure structured JSON logging."""

    logger = logging.getLogger()
    logger.setLevel(level)

    handler = logging.StreamHandler(sys.stdout)

    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    handler.setFormatter(formatter)
    logger.addHandler(handler)
```

**Output Example**:
```json
{
  "asctime": "2025-01-20 15:30:45",
  "levelname": "INFO",
  "name": "backend.core.scanner",
  "message": "Scan completed",
  "user_id": "12345",
  "accounts_fetched": 847,
  "duration_seconds": 12.3
}
```

### 6.3 Logging Conventions

**What to log**:
```python
class ScanService:
    async def scan_and_categorize(self, user_id: str) -> ScanResult:
        # INFO: Start of significant operations
        logger.info(f"Starting scan for user {user_id}")

        start_time = time.time()

        try:
            # DEBUG: Detailed progress
            logger.debug(f"Fetching following list for {user_id}")
            accounts = await self._x_client.fetch_following(user_id)
            logger.debug(f"Fetched {len(accounts)} accounts")

            # INFO: Progress milestones
            logger.info(f"Discovering categories from {len(accounts)} accounts")
            categories = await self._grok.discover_categories(accounts)
            logger.info(f"Discovered {len(categories)} categories")

            # WARNING: Non-critical issues
            if len(categories) < 5:
                logger.warning(
                    f"Only {len(categories)} categories discovered. "
                    "Expected 10-20. Dataset may be too small."
                )

            # INFO: Completion with metrics
            duration = time.time() - start_time
            logger.info(
                f"Scan completed for user {user_id}",
                extra={
                    "accounts": len(accounts),
                    "categories": len(categories),
                    "duration_seconds": duration
                }
            )

            return ScanResult(...)

        except XAPIError as e:
            # ERROR: Operation failures
            logger.error(
                f"Scan failed for user {user_id}: {e}",
                exc_info=True,  # Include stack trace
                extra={"user_id": user_id}
            )
            raise
```

**What NOT to log**:
- ❌ Sensitive data (API keys, tokens)
- ❌ Full request/response bodies (use digests)
- ❌ Personal information (unless anonymized)
- ❌ Every single iteration of loops

### 6.4 Request Logging Middleware

```python
# backend/middleware/logging.py
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log all HTTP requests and responses."""

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # Log request
        logger.info(
            f"Request: {request.method} {request.url.path}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "query": str(request.query_params),
                "client_ip": request.client.host
            }
        )

        # Process request
        response = await call_next(request)

        # Log response
        duration = time.time() - start_time
        logger.info(
            f"Response: {response.status_code} in {duration:.3f}s",
            extra={
                "status_code": response.status_code,
                "duration_seconds": duration,
                "path": request.url.path
            }
        )

        return response
```

---

## 7. Testing Strategy

### 7.1 Test Organization

```
tests/
├── unit/                        # Unit tests (fast, isolated)
│   ├── api/
│   │   ├── test_x_client.py
│   │   └── test_grok_client.py
│   ├── core/
│   │   ├── test_scanner.py
│   │   ├── test_categorizer.py
│   │   └── test_statistics.py
│   └── db/
│       └── test_repositories.py
│
├── integration/                 # Integration tests (DB, external APIs)
│   ├── test_scan_workflow.py
│   ├── test_database.py
│   └── test_api_endpoints.py
│
├── e2e/                         # End-to-end tests (full system)
│   └── test_complete_scan.py
│
├── conftest.py                  # Shared fixtures
└── factories.py                 # Test data factories
```

### 7.2 Testing Pyramid

```
         /\
        /  \  E2E (Few)
       /____\
      /      \  Integration (Some)
     /________\
    /          \  Unit (Many)
   /____________\
```

**Distribution**:
- **70%** Unit tests (fast, isolated, mock dependencies)
- **20%** Integration tests (real DB, mocked external APIs)
- **10%** E2E tests (full system, slow)

### 7.3 Unit Testing Patterns

**Use pytest fixtures for dependencies**:
```python
# tests/conftest.py
import pytest
from unittest.mock import AsyncMock
from backend.api.x_client import XClient
from backend.db.repositories.account_repository import AccountRepository

@pytest.fixture
def mock_x_client():
    """Mock X API client."""
    client = AsyncMock(spec=XClient)
    client.fetch_following.return_value = [
        {"id": "123", "username": "alice", "name": "Alice"},
        {"id": "456", "username": "bob", "name": "Bob"}
    ]
    return client

@pytest.fixture
def mock_account_repo():
    """Mock account repository."""
    repo = AsyncMock(spec=AccountRepository)
    return repo
```

**Test structure (Arrange-Act-Assert)**:
```python
# tests/unit/core/test_scanner.py
import pytest
from backend.core.scanner import Scanner

@pytest.mark.asyncio
async def test_scan_accounts_success(mock_x_client, mock_account_repo):
    """Test successful account scanning."""
    # Arrange
    scanner = Scanner(x_client=mock_x_client, account_repo=mock_account_repo)
    user_id = "123456"

    # Act
    result = await scanner.scan_accounts(user_id)

    # Assert
    assert result.total_accounts == 2
    assert result.success is True
    mock_x_client.fetch_following.assert_called_once_with(user_id)
    mock_account_repo.bulk_save.assert_called_once()

@pytest.mark.asyncio
async def test_scan_accounts_api_error(mock_x_client, mock_account_repo):
    """Test scan handles API errors gracefully."""
    # Arrange
    scanner = Scanner(x_client=mock_x_client, account_repo=mock_account_repo)
    mock_x_client.fetch_following.side_effect = XAPIError("Rate limit exceeded")

    # Act & Assert
    with pytest.raises(XAPIError, match="Rate limit exceeded"):
        await scanner.scan_accounts("123456")
```

### 7.4 Integration Testing

**Use real database with rollback**:
```python
# tests/integration/conftest.py
import pytest
from backend.db.manager import DatabaseManager

@pytest.fixture
def db():
    """Provide test database with rollback."""
    db = DatabaseManager(database_url="sqlite:///:memory:")
    db.create_tables()

    yield db

    db.close()

@pytest.fixture
def account_repo(db):
    """Provide real account repository with test DB."""
    return AccountRepository(db)
```

**Test real interactions**:
```python
# tests/integration/test_database.py
def test_save_and_retrieve_account(account_repo):
    """Test saving and retrieving account from database."""
    # Arrange
    account = Account(
        id="123",
        username="alice",
        name="Alice",
        followers_count=1000
    )

    # Act
    account_repo.save(account)
    retrieved = account_repo.get_by_username("alice")

    # Assert
    assert retrieved is not None
    assert retrieved.username == "alice"
    assert retrieved.followers_count == 1000
```

### 7.5 Test Factories

**Use factories for test data**:
```python
# tests/factories.py
from backend.db.models import Account, Category

class AccountFactory:
    """Factory for creating test accounts."""

    @staticmethod
    def create(
        id: str = "123",
        username: str = "testuser",
        name: str = "Test User",
        followers_count: int = 1000,
        **kwargs
    ) -> Account:
        """Create account with defaults."""
        return Account(
            id=id,
            username=username,
            name=name,
            followers_count=followers_count,
            **kwargs
        )

    @staticmethod
    def create_batch(count: int) -> list[Account]:
        """Create multiple accounts."""
        return [
            AccountFactory.create(
                id=str(i),
                username=f"user{i}",
                name=f"User {i}"
            )
            for i in range(count)
        ]
```

**Usage**:
```python
def test_categorization_with_many_accounts():
    accounts = AccountFactory.create_batch(100)
    categorizer = Categorizer()
    result = categorizer.discover_categories(accounts)
    assert len(result) >= 5
```

### 7.6 Testing Async Code

**Always use `@pytest.mark.asyncio`**:
```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
    assert result == expected
```

**Mock async functions with `AsyncMock`**:
```python
from unittest.mock import AsyncMock

mock_client = AsyncMock()
mock_client.fetch_data.return_value = {"data": "value"}

result = await mock_client.fetch_data()
assert result == {"data": "value"}
```

### 7.7 Coverage Goals

**Minimum Coverage**:
- Overall: **80%**
- Core business logic (`backend/core/`): **90%**
- API clients (`backend/api/`): **85%**
- Repositories (`backend/db/repositories/`): **85%**

**Run coverage**:
```bash
pytest --cov=backend --cov-report=html --cov-report=term
```

---

## 8. File Organization

### 8.1 Module Structure

**Each module should have**:
```python
# backend/core/scanner.py

"""Account scanning module.

This module provides functionality for scanning X accounts that a user
follows, including rate limiting, pagination, and progress tracking.
"""

# Imports (grouped and sorted)
import asyncio
from typing import List, Optional

from backend.api.x_client import XClient
from backend.db.repositories.account_repository import AccountRepository

# Public exports (if applicable)
__all__ = ["Scanner", "ScanResult"]

# Constants
MAX_CONCURRENT_REQUESTS = 5
BATCH_SIZE = 100

# Classes and functions
class Scanner:
    ...
```

### 8.2 Import Organization Rules

1. **Standard library** (built-in modules)
2. **Third-party** (installed packages)
3. **Local application** (project modules)

Within each group, sort alphabetically.

```python
# Standard library
import asyncio
import os
from datetime import datetime
from typing import List, Optional

# Third-party
import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Local application
from backend.api.x_client import XClient
from backend.core.scanner import Scanner
from backend.db.models import Account
```

### 8.3 File Naming Conventions

- **Modules**: `snake_case.py`
- **Classes**: One per file (usually), file named after class
- **Tests**: `test_<module>.py`

```
✅ Good:
backend/core/scanner.py         # Contains Scanner class
tests/unit/core/test_scanner.py # Tests for Scanner

❌ Bad:
backend/core/ScannerModule.py   # PascalCase file name
tests/scanner_test.py           # Wrong naming pattern
```

---

## 9. Type System

### 9.1 Type Hints

**Always use type hints** for function signatures:

```python
from typing import List, Optional, Dict, Any, Union

# ✅ CORRECT - Full type hints
async def fetch_accounts(
    user_id: str,
    limit: int = 1000,
    include_inactive: bool = False
) -> List[Account]:
    """Fetch accounts with type safety."""
    pass

# ❌ INCORRECT - No type hints
async def fetch_accounts(user_id, limit=1000, include_inactive=False):
    pass
```

### 9.2 Common Type Patterns

**Optional values**:
```python
from typing import Optional

def get_account(username: str) -> Optional[Account]:
    """Return account or None if not found."""
    pass
```

**Union types (multiple possible types)**:
```python
from typing import Union

def process_input(data: Union[str, dict]) -> Account:
    """Accept string or dict."""
    pass
```

**Type aliases for readability**:
```python
from typing import List, Dict

# Define aliases
AccountList = List[Account]
CategoryMap = Dict[str, List[Account]]

# Use in function signatures
def group_by_category(accounts: AccountList) -> CategoryMap:
    pass
```

**Protocol for structural typing (duck typing)**:
```python
from typing import Protocol

class Categorizer(Protocol):
    """Protocol for any categorization implementation."""

    async def categorize(self, account: Account) -> str:
        """Categorize an account."""
        ...

# Any class with this method signature satisfies the protocol
class GrokCategorizer:
    async def categorize(self, account: Account) -> str:
        return await self._grok.categorize(account)
```

### 9.3 Pydantic for Data Validation

**Use Pydantic for all data models**:
```python
from pydantic import BaseModel, Field, validator
from typing import Optional

class Account(BaseModel):
    """Account data model with validation."""

    id: str = Field(..., description="X account ID")
    username: str = Field(..., min_length=1, max_length=15)
    name: str
    followers_count: int = Field(ge=0, description="Number of followers")
    category: Optional[str] = None

    @validator("username")
    def username_no_spaces(cls, v):
        """Ensure username has no spaces."""
        if " " in v:
            raise ValueError("Username cannot contain spaces")
        return v

    class Config:
        """Pydantic configuration."""
        orm_mode = True  # Allow creation from ORM models
        frozen = False   # Allow modification
```

**Benefits**:
- Runtime validation
- Automatic JSON serialization
- Clear error messages
- IDE autocomplete support

### 9.4 Type Checking with mypy

**Configuration** (`.mypy.ini`):
```ini
[mypy]
python_version = 3.11
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
disallow_incomplete_defs = True
check_untyped_defs = True
no_implicit_optional = True

[mypy-tests.*]
disallow_untyped_defs = False
```

**Run type checking**:
```bash
mypy backend/
```

---

## 10. API Design Principles

### 10.1 RESTful Endpoint Design

**Resource naming**:
- Use **plural nouns** for collections: `/api/accounts`, `/api/categories`
- Use **IDs** for specific resources: `/api/accounts/{account_id}`
- Use **nested routes** for relationships: `/api/categories/{category_id}/accounts`

**HTTP Methods**:
| Method | Purpose | Example |
|--------|---------|---------|
| GET | Retrieve resource(s) | `GET /api/accounts` |
| POST | Create new resource | `POST /api/scan` |
| PUT | Replace entire resource | `PUT /api/accounts/{id}` |
| PATCH | Update part of resource | `PATCH /api/accounts/{id}` |
| DELETE | Delete resource | `DELETE /api/accounts/{id}` |

**Complete API Design**:
```python
# backend/routes/accounts.py
from fastapi import APIRouter, HTTPException, status, Query
from typing import List, Optional

router = APIRouter(prefix="/api/accounts", tags=["accounts"])

@router.get("", response_model=List[AccountResponse])
async def list_accounts(
    category: Optional[str] = Query(None, description="Filter by category"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: DatabaseManager = Depends(get_db)
) -> List[AccountResponse]:
    """List accounts with optional filtering and pagination."""
    pass

@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(
    account_id: str,
    db: DatabaseManager = Depends(get_db)
) -> AccountResponse:
    """Get specific account by ID."""
    account = db.get_account(account_id)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account {account_id} not found"
        )
    return account

@router.post("", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
async def create_account(
    account: AccountCreate,
    db: DatabaseManager = Depends(get_db)
) -> AccountResponse:
    """Create new account."""
    pass

@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    account_id: str,
    db: DatabaseManager = Depends(get_db)
):
    """Delete account by ID."""
    pass
```

### 10.2 Request/Response Models

**Separate models for different operations**:
```python
# backend/schemas/account.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AccountBase(BaseModel):
    """Shared account fields."""
    username: str
    name: str
    followers_count: int

class AccountCreate(AccountBase):
    """Fields required to create account."""
    id: str

class AccountUpdate(BaseModel):
    """Fields that can be updated (all optional)."""
    name: Optional[str] = None
    category: Optional[str] = None

class AccountResponse(AccountBase):
    """Account returned by API (includes computed fields)."""
    id: str
    category: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
```

### 10.3 Error Response Format

**Consistent error structure**:
```python
from fastapi import HTTPException, status

class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str          # Error type (e.g., "ValidationError")
    message: str        # Human-readable message
    details: dict = {}  # Additional context

# Usage
raise HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail={
        "error": "ValidationError",
        "message": "Invalid user_id format",
        "details": {"user_id": user_id, "expected": "numeric string"}
    }
)
```

### 10.4 Pagination

**Standard pagination parameters**:
```python
@router.get("/api/accounts")
async def list_accounts(
    limit: int = Query(100, ge=1, le=1000, description="Items per page"),
    offset: int = Query(0, ge=0, description="Number of items to skip")
) -> PaginatedResponse[Account]:
    """List accounts with pagination."""

    accounts = db.get_accounts(limit=limit, offset=offset)
    total = db.count_accounts()

    return PaginatedResponse(
        items=accounts,
        total=total,
        limit=limit,
        offset=offset,
        has_more=offset + limit < total
    )
```

### 10.5 WebSocket Message Format

**Consistent message structure**:
```python
from pydantic import BaseModel
from enum import Enum

class MessageType(str, Enum):
    """WebSocket message types."""
    PROGRESS = "progress"
    COMPLETE = "complete"
    ERROR = "error"

class WebSocketMessage(BaseModel):
    """Standard WebSocket message."""
    type: MessageType
    data: dict
    timestamp: datetime

# Usage
await websocket.send_json(
    WebSocketMessage(
        type=MessageType.PROGRESS,
        data={
            "current": 500,
            "total": 1000,
            "message": "Fetching accounts..."
        },
        timestamp=datetime.utcnow()
    ).dict()
)
```

---

## Summary

This architecture document defines:

1. **4-Layer Architecture** - Clear separation of concerns
2. **Design Patterns** - Repository, Service Layer, Factory, Strategy, Observer, DI
3. **Code Conventions** - PEP 8, naming, async/await, docstrings
4. **Component Structure** - Module organization for backend and frontend
5. **Error Handling** - Exception hierarchy, retry strategies
6. **Logging** - Structured logging with appropriate levels
7. **Testing** - Pyramid approach with unit/integration/e2e tests
8. **File Organization** - Consistent module structure and imports
9. **Type System** - Full type hints with Pydantic validation
10. **API Design** - RESTful principles, consistent responses

**Key Principles**:
- ✅ **Separation of Concerns** - Each component has single responsibility
- ✅ **Dependency Injection** - Loosely coupled, testable code
- ✅ **Type Safety** - Full type hints and runtime validation
- ✅ **Error Transparency** - Clear error messages with context
- ✅ **Observable System** - Comprehensive logging and monitoring
- ✅ **Test Coverage** - High coverage with fast feedback

**Next Steps**:
1. Review this architecture with the team
2. Set up linting/formatting tools (Black, isort, mypy, pylint)
3. Create project templates following these patterns
4. Begin Phase 2 implementation using these guidelines

---

**Document Version**: 1.0
**Last Updated**: 2025-01-20
**Maintained By**: Development Team
