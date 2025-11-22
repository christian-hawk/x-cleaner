# Implementation Roadmap

Quick reference guide for implementing the X-Cleaner project with web dashboard.

## 🎯 Current Status

**⚠️ PARTIAL - Components Ready, Core Functionality Missing (v0.5-alpha)**

Component implementation (Phases 1-6):
- Phase 1: Foundation & Setup ✅ COMPLETE
- Phase 2: X API Integration ⚠️ PARTIAL (client ready, no endpoint uses it)
- Phase 3: Grok Integration ⚠️ PARTIAL (client ready, no endpoint uses it)
- Phase 4: FastAPI Backend ⚠️ PARTIAL (read-only endpoints, no scan trigger)
- Phase 5: Streamlit Web Dashboard ⚠️ PARTIAL (visualization only, no scan UI)
- Phase 6: Quality & Testing ⚠️ PARTIAL (94% coverage of components, no integration test)

**🚧 CRITICAL GAP: Core Scan Functionality NOT Implemented**

**📋 NEXT STEPS (In Order):**
1. **Phase 5.5: Implement Scan Functionality** - POST /api/scan endpoint + orchestration service
2. **Phase 5.6: Add Scan UI** - Scan trigger button + progress display in Streamlit
3. Phase 7: Bulk Account Management
4. Phase 8: Advanced Features

## Overview

This roadmap provides step-by-step instructions for building X-Cleaner with:
- **Backend**: FastAPI REST API with WebSocket support ✅ **COMPLETE**
- **Frontend**: Streamlit dashboard (MVP) ✅ **COMPLETE**
- **CLI**: Command-line interface for admin tasks ✅ **COMPLETE**

**Recommended Path**: Streamlit MVP (3-4 weeks) ✅ **COMPLETE**

---

## 📚 Implementation Summary

### ✅ What's Been Implemented (Components Only)

**Backend Components**
- ✅ X API v2 client with pagination and rate limiting - **NOT USED YET**
- ✅ Grok AI client with emergent categorization - **NOT USED YET**
- ✅ FastAPI REST API with ~10 GET endpoints - **READ-ONLY**
- ✅ 4-layer architecture (Presentation/API/Business/Data)
- ✅ Repository pattern for data access
- ✅ Service layer for business logic
- ✅ Dependency injection
- ✅ Comprehensive unit tests (94% coverage) - **COMPONENTS ONLY**

**Frontend (Visualization Only)**
- ✅ Streamlit dashboard with 5 interactive pages - **CANNOT TRIGGER SCANS**
- ✅ Overview with key metrics and charts
- ✅ Categories explorer
- ✅ Accounts browser with search/filter
- ✅ Advanced analytics
- ✅ Settings & management
- ✅ Export functionality (JSON/CSV)

**Quality Assurance**
- ✅ GitHub Actions CI/CD (mypy + pylint)
- ✅ Type safety with strict mypy
- ✅ Code quality enforcement with pylint
- ✅ 57 unit tests passing - **COMPONENTS ONLY, NO INTEGRATION TEST**
- ✅ Sample data generator - **FAKE DATA ONLY**
- ✅ Deployment documentation

### ❌ What's NOT Implemented (CRITICAL)

**Core Scan Functionality - THE MAIN FEATURE**
- ❌ ScanService to orchestrate: fetch accounts → categorize → save
- ❌ POST /api/scan endpoint to trigger scans
- ❌ Background task processing
- ❌ WebSocket /ws/scan for real-time progress
- ❌ Scan trigger UI in Streamlit dashboard
- ❌ Real-time scan progress display
- ❌ End-to-end integration test

**Current Limitation:**
The app can only display sample/fake data. It CANNOT scan real X accounts yet.

### 🚧 What's Next (Priority Order)

**Phase 5.5: Core Scan Functionality** ⚠️ **CRITICAL - MUST DO FIRST**
- Implement ScanService orchestration
- Add POST /api/scan endpoint
- Background task processing
- WebSocket for progress
- Scan UI in dashboard
- Integration test

**Phase 5.6: Scan Progress UI**
- Real-time progress display
- Error handling UI
- Scan history

**Phase 7: Bulk Account Management** (After core works)
- Unfollow entire category feature
- Bulk selection with pagination persistence
- Real-time progress tracking via WebSocket
- Undo/refollow buffer (24h)

**Phase 8: Advanced Features** (Optional)
- Scheduled scans, historical trends, authentication, cloud deployment

---

## 📖 Reference: Original Implementation Guide

The sections below contain the original step-by-step implementation guide
that was followed to build X-Cleaner. They are kept for reference and for
implementing future phases.

### 1. Environment Setup (Day 1) ✅ **IMPLEMENTED**

```bash
# Create project structure
mkdir -p backend/api backend/core backend/tasks backend/cli
mkdir -p streamlit_app/pages streamlit_app/components
mkdir -p tests data docs

# Create __init__.py files
touch backend/__init__.py backend/api/__init__.py backend/core/__init__.py
touch backend/tasks/__init__.py backend/cli/__init__.py
touch streamlit_app/__init__.py tests/__init__.py

# Create requirements.txt
cat > requirements.txt << EOF
# Core
httpx>=0.27.0
pandas>=2.1.0
python-dotenv>=1.0.0
pydantic>=2.5.0

# Backend API
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
websockets>=12.0
python-multipart>=0.0.6

# Database
sqlalchemy>=2.0.0
aiosqlite>=0.19.0

# AI/ML APIs
openai>=1.10.0

# Web Dashboard
streamlit>=1.31.0
plotly>=5.18.0
altair>=5.2.0

# CLI
typer>=0.9.0
rich>=13.0.0

# Utils
jinja2>=3.1.0
python-jose>=3.3.0
passlib>=1.7.4
EOF

# Install dependencies
pip install -r requirements.txt

# Create .env.example
cat > .env.example << EOF
# X API Credentials
X_API_BEARER_TOKEN=your_bearer_token_here
X_USER_ID=your_user_id_here

# Grok API Credentials
XAI_API_KEY=your_xai_api_key_here

# Application Settings
DATABASE_PATH=data/accounts.db
BATCH_SIZE=100
CACHE_EXPIRY_DAYS=7

# Web Server
HOST=0.0.0.0
PORT=8000
RELOAD=true

# Streamlit
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
EOF
```

### 2. Core Models (Day 1-2)

**File: `backend/models.py`**

```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class XAccount(BaseModel):
    """X Account data model"""
    user_id: str
    username: str
    display_name: str
    bio: Optional[str] = None
    verified: bool = False
    created_at: Optional[datetime] = None
    followers_count: int = 0
    following_count: int = 0
    tweet_count: int = 0
    location: Optional[str] = None
    website: Optional[str] = None
    profile_image_url: Optional[str] = None

class CategorizedAccount(XAccount):
    """Account with category information"""
    category: str
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: Optional[str] = None
    analyzed_at: datetime = Field(default_factory=datetime.now)

class CategoryStats(BaseModel):
    """Statistics for a category"""
    name: str
    count: int
    percentage: float
    top_accounts: list[XAccount]
    avg_followers: float
    verification_rate: float

class AnalysisReport(BaseModel):
    """Complete analysis report"""
    total_accounts: int
    categories_count: int
    analyzed_date: datetime
    category_stats: list[CategoryStats]
    overall_metrics: dict
```

### 3. X API Client (Day 2-3)

**File: `backend/api/x_client.py`**

```python
import httpx
import os
from typing import List, Optional
from ..models import XAccount

class XAPIClient:
    """Client for X API v2"""

    BASE_URL = "https://api.twitter.com/2"

    def __init__(self, bearer_token: Optional[str] = None):
        self.bearer_token = bearer_token or os.getenv("X_API_BEARER_TOKEN")
        self.headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "Content-Type": "application/json"
        }
        self.client = httpx.AsyncClient(headers=self.headers, timeout=30.0)

    async def get_following(
        self,
        user_id: str,
        max_results: int = 1000,
        pagination_token: Optional[str] = None
    ) -> tuple[List[XAccount], Optional[str]]:
        """
        Fetch accounts that user follows

        Returns:
            tuple: (list of accounts, next pagination token)
        """
        url = f"{self.BASE_URL}/users/{user_id}/following"
        params = {
            "max_results": min(max_results, 1000),
            "user.fields": "id,username,name,description,verified,created_at,"
                          "public_metrics,location,url,profile_image_url"
        }

        if pagination_token:
            params["pagination_token"] = pagination_token

        response = await self.client.get(url, params=params)
        response.raise_for_status()

        data = response.json()
        accounts = [self._parse_account(user) for user in data.get("data", [])]
        next_token = data.get("meta", {}).get("next_token")

        return accounts, next_token

    async def get_all_following(self, user_id: str) -> List[XAccount]:
        """Fetch all following accounts with pagination"""
        all_accounts = []
        next_token = None

        while True:
            accounts, next_token = await self.get_following(
                user_id,
                pagination_token=next_token
            )
            all_accounts.extend(accounts)

            if not next_token:
                break

        return all_accounts

    def _parse_account(self, user_data: dict) -> XAccount:
        """Parse API response into XAccount model"""
        metrics = user_data.get("public_metrics", {})

        return XAccount(
            user_id=user_data["id"],
            username=user_data["username"],
            display_name=user_data["name"],
            bio=user_data.get("description"),
            verified=user_data.get("verified", False),
            created_at=user_data.get("created_at"),
            followers_count=metrics.get("followers_count", 0),
            following_count=metrics.get("following_count", 0),
            tweet_count=metrics.get("tweet_count", 0),
            location=user_data.get("location"),
            website=user_data.get("url"),
            profile_image_url=user_data.get("profile_image_url")
        )

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
```

### 4. Grok API Client (Day 3-4)

**File: `backend/api/grok_client.py`**

```python
import os
import json
from typing import List, Dict, Optional
from openai import OpenAI
from ..models import XAccount, CategorizedAccount

class GrokClient:
    """Client for xAI Grok API with emergent categorization"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("XAI_API_KEY")
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.x.ai/v1"
        )
        self.discovered_categories = None

    async def analyze_and_categorize(
        self,
        accounts: List[XAccount],
        sample_size: int = 200
    ) -> tuple[Dict, List[CategorizedAccount]]:
        """
        Two-phase categorization:
        1. Discover natural categories from data
        2. Categorize all accounts using discovered categories

        Returns:
            tuple: (category_metadata, categorized_accounts)
        """
        # Phase 1: Discover categories from sample
        sample = accounts[:sample_size] if len(accounts) > sample_size else accounts
        categories = await self._discover_categories(sample)
        self.discovered_categories = categories

        # Phase 2: Categorize all accounts
        categorized = await self._categorize_with_discovered(accounts, categories)

        return categories, categorized

    async def _discover_categories(
        self,
        sample_accounts: List[XAccount]
    ) -> Dict:
        """Phase 1: Discover natural categories from account data"""

        # Build account summaries
        accounts_summary = []
        for account in sample_accounts:
            summary = f"@{account.username}: {account.bio or 'No bio'} "
            summary += f"({account.followers_count:,} followers)"
            accounts_summary.append(summary)

        prompt = f"""You are an expert at analyzing social media networks and identifying natural community patterns.

I have {len(sample_accounts)} X (Twitter) accounts. Analyze them and discover 10-20 natural categories based on actual patterns in the data.

Accounts summary (username: bio, followers):
{chr(10).join(accounts_summary[:100])}  # First 100 for discovery
... and {len(sample_accounts) - 100} more accounts

Your task:
1. Identify natural groupings and communities
2. Create 10-20 descriptive category names
3. Explain key characteristics of each category
4. Estimate the percentage of accounts in each

DO NOT use predefined categories. Discover what's actually in THIS network.

Respond with JSON:
{{
  "categories": [
    {{
      "name": "Descriptive Category Name",
      "description": "What defines this category",
      "characteristics": ["trait 1", "trait 2", "trait 3"],
      "estimated_percentage": 15
    }}
  ],
  "total_categories": 12,
  "analysis_summary": "Brief overview of the network"
}}"""

        response = self.client.chat.completions.create(
            model="grok-4-1-fast-reasoning",
            messages=[
                {
                    "role": "system",
                    "content": "You are a social network analysis expert who discovers natural patterns in data."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3
        )

        result_text = response.choices[0].message.content
        categories_data = self._extract_json(result_text)

        return categories_data

    async def _categorize_with_discovered(
        self,
        accounts: List[XAccount],
        categories: Dict,
        batch_size: int = 50
    ) -> List[CategorizedAccount]:
        """Phase 2: Categorize accounts using discovered categories"""

        categorized = []
        category_names = [cat["name"] for cat in categories["categories"]]

        # Process in batches
        for i in range(0, len(accounts), batch_size):
            batch = accounts[i:i + batch_size]
            batch_results = await self._categorize_batch(batch, category_names, categories)
            categorized.extend(batch_results)

        return categorized

    async def _categorize_batch(
        self,
        accounts: List[XAccount],
        category_names: List[str],
        categories_metadata: Dict
    ) -> List[CategorizedAccount]:
        """Categorize a batch of accounts"""

        # Build account details
        accounts_info = []
        for idx, account in enumerate(accounts):
            info = f"""
{idx + 1}. @{account.username} ({account.display_name})
   Bio: {account.bio or 'N/A'}
   Followers: {account.followers_count:,} | Following: {account.following_count:,}
   Verified: {account.verified} | Tweets: {account.tweet_count:,}
"""
            accounts_info.append(info)

        prompt = f"""Categorize these X accounts using the discovered category system.

Available categories:
{', '.join(category_names)}

Category descriptions:
{json.dumps([{c['name']: c['description']} for c in categories_metadata['categories']], indent=2)}

Accounts to categorize:
{''.join(accounts_info)}

For each account, provide:
- Primary category (must be from the list above)
- Confidence (0.0 to 1.0)
- Brief reasoning
- Alternative category if confidence < 0.8

Respond as JSON array:
[
  {{
    "account_index": 1,
    "category": "Category Name",
    "confidence": 0.95,
    "reasoning": "Why this category fits",
    "alternative": null
  }}
]"""

        response = self.client.chat.completions.create(
            model="grok-4-1-fast-reasoning",
            messages=[
                {
                    "role": "system",
                    "content": "You categorize accounts accurately based on discovered patterns."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2
        )

        result_text = response.choices[0].message.content
        categorizations = self._extract_json(result_text)

        # Convert to CategorizedAccount objects
        categorized_accounts = []
        for account, cat_data in zip(accounts, categorizations):
            categorized_accounts.append(
                CategorizedAccount(
                    **account.model_dump(),
                    category=cat_data["category"],
                    confidence=cat_data["confidence"],
                    reasoning=cat_data.get("reasoning")
                )
            )

        return categorized_accounts

    def _extract_json(self, response_text: str) -> Dict:
        """Extract JSON from response (handles markdown formatting)"""
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0]

        return json.loads(response_text.strip())
```

### 5. Database Manager (Day 4)

**File: `backend/database.py`**

```python
import sqlite3
from typing import List, Optional
from datetime import datetime
from .models import CategorizedAccount

class DatabaseManager:
    """SQLite database manager for account storage"""

    def __init__(self, db_path: str = "data/accounts.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                user_id TEXT PRIMARY KEY,
                username TEXT NOT NULL,
                display_name TEXT,
                bio TEXT,
                verified INTEGER,
                created_at TEXT,
                followers_count INTEGER,
                following_count INTEGER,
                tweet_count INTEGER,
                location TEXT,
                website TEXT,
                profile_image_url TEXT,
                category TEXT,
                confidence REAL,
                reasoning TEXT,
                analyzed_at TEXT,
                updated_at TEXT
            )
        """)

        conn.commit()
        conn.close()

    def save_accounts(self, accounts: List[CategorizedAccount]):
        """Save or update accounts"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for account in accounts:
            cursor.execute("""
                INSERT OR REPLACE INTO accounts VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
            """, (
                account.user_id,
                account.username,
                account.display_name,
                account.bio,
                int(account.verified),
                account.created_at.isoformat() if account.created_at else None,
                account.followers_count,
                account.following_count,
                account.tweet_count,
                account.location,
                account.website,
                account.profile_image_url,
                account.category,
                account.confidence,
                account.reasoning,
                account.analyzed_at.isoformat(),
                datetime.now().isoformat()
            ))

        conn.commit()
        conn.close()

    def get_all_accounts(self) -> List[CategorizedAccount]:
        """Retrieve all accounts"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM accounts")
        rows = cursor.fetchall()

        accounts = [self._row_to_account(row) for row in rows]

        conn.close()
        return accounts

    def _row_to_account(self, row: sqlite3.Row) -> CategorizedAccount:
        """Convert database row to CategorizedAccount"""
        return CategorizedAccount(
            user_id=row["user_id"],
            username=row["username"],
            display_name=row["display_name"],
            bio=row["bio"],
            verified=bool(row["verified"]),
            created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else None,
            followers_count=row["followers_count"],
            following_count=row["following_count"],
            tweet_count=row["tweet_count"],
            location=row["location"],
            website=row["website"],
            profile_image_url=row["profile_image_url"],
            category=row["category"],
            confidence=row["confidence"],
            reasoning=row["reasoning"],
            analyzed_at=datetime.fromisoformat(row["analyzed_at"])
        )
```

### 6. FastAPI Backend (Day 5-7)

**File: `backend/main.py`**

```python
from fastapi import FastAPI, BackgroundTasks, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict
import asyncio

from .api.x_client import XAPIClient
from .api.grok_client import GrokClient
from .database import DatabaseManager
from .models import XAccount, CategorizedAccount

app = FastAPI(title="X-Cleaner API", version="1.0.0")

# Enable CORS for Streamlit/React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state for scan progress
scan_progress = {"status": "idle", "progress": 0, "message": ""}

@app.get("/")
async def root():
    return {"message": "X-Cleaner API", "version": "1.0.0"}

@app.get("/api/stats")
async def get_stats():
    """Get summary statistics"""
    db = DatabaseManager()
    accounts = db.get_all_accounts()
    categories = db.get_categories()

    return {
        "total_accounts": len(accounts),
        "total_categories": len(categories) if categories else 0,
        "verified_count": sum(1 for a in accounts if a.verified),
        "last_updated": max((a.analyzed_at for a in accounts), default=None)
    }

@app.get("/api/categories")
async def get_categories():
    """List all discovered categories"""
    db = DatabaseManager()
    return db.get_categories()

@app.get("/api/categories/{category_name}/accounts")
async def get_category_accounts(category_name: str):
    """Get all accounts in a category"""
    db = DatabaseManager()
    accounts = db.get_accounts_by_category(category_name)
    return accounts

@app.get("/api/accounts")
async def get_accounts(
    category: str = None,
    verified: bool = None,
    search: str = None,
    limit: int = 100,
    offset: int = 0
):
    """List accounts with filtering"""
    db = DatabaseManager()
    accounts = db.get_all_accounts()

    # Apply filters
    if category:
        accounts = [a for a in accounts if a.category == category]
    if verified is not None:
        accounts = [a for a in accounts if a.verified == verified]
    if search:
        search = search.lower()
        accounts = [a for a in accounts if
                   search in a.username.lower() or
                   search in a.display_name.lower() or
                   (a.bio and search in a.bio.lower())]

    # Pagination
    total = len(accounts)
    accounts = accounts[offset:offset + limit]

    return {"total": total, "accounts": accounts, "limit": limit, "offset": offset}

@app.post("/api/scan")
async def trigger_scan(background_tasks: BackgroundTasks, user_id: str = None):
    """Trigger a new scan"""
    global scan_progress

    if scan_progress["status"] == "running":
        return {"error": "Scan already in progress"}

    scan_progress = {"status": "running", "progress": 0, "message": "Starting scan..."}
    background_tasks.add_task(run_scan, user_id)

    return {"status": "started", "message": "Scan initiated"}

async def run_scan(user_id: str = None):
    """Background task to run the scan"""
    global scan_progress

    try:
        x_client = XAPIClient()
        grok_client = GrokClient()
        db = DatabaseManager()

        user_id = user_id or os.getenv("X_USER_ID")

        # Fetch accounts
        scan_progress["message"] = "Fetching accounts..."
        scan_progress["progress"] = 10
        accounts = await x_client.get_all_following(user_id)

        scan_progress["message"] = f"Found {len(accounts)} accounts"
        scan_progress["progress"] = 30

        # Discover and categorize
        scan_progress["message"] = "Discovering categories..."
        scan_progress["progress"] = 50
        categories, categorized = await grok_client.analyze_and_categorize(accounts)

        scan_progress["message"] = "Saving results..."
        scan_progress["progress"] = 80
        db.save_accounts(categorized)
        db.save_categories(categories)

        scan_progress = {
            "status": "completed",
            "progress": 100,
            "message": f"Scan completed! {len(categorized)} accounts categorized into {len(categories['categories'])} categories"
        }

        await x_client.close()

    except Exception as e:
        scan_progress = {"status": "error", "progress": 0, "message": str(e)}

@app.get("/api/scan/status")
async def get_scan_status():
    """Get current scan status"""
    return scan_progress

@app.websocket("/ws/scan")
async def websocket_scan(websocket: WebSocket):
    """WebSocket for real-time scan updates"""
    await websocket.accept()

    try:
        while True:
            await websocket.send_json(scan_progress)
            await asyncio.sleep(1)  # Send updates every second

            if scan_progress["status"] in ["completed", "error"]:
                break
    except:
        pass
    finally:
        await websocket.close()

@app.get("/api/export")
async def export_data(format: str = "json"):
    """Export data in various formats"""
    db = DatabaseManager()
    accounts = db.get_all_accounts()
    categories = db.get_categories()

    if format == "json":
        return {"accounts": accounts, "categories": categories}
    # Add CSV, PDF export logic here

    return {"error": "Unsupported format"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**File: `backend/api/routes.py`** - Additional REST endpoints

**File: `backend/api/websockets.py`** - WebSocket handlers

**File: `backend/tasks/background.py`** - Background task queue

---

### 7. Streamlit Dashboard (Day 8-10)

**File: `streamlit_app/app.py`**

```python
import streamlit as st
import requests
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime

# Configure page
st.set_page_config(
    page_title="X-Cleaner Dashboard",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_BASE = "http://localhost:8000/api"

def fetch_stats():
    """Fetch summary statistics"""
    response = requests.get(f"{API_BASE}/stats")
    return response.json()

def fetch_categories():
    """Fetch all categories"""
    response = requests.get(f"{API_BASE}/categories")
    return response.json()

def fetch_accounts(category=None):
    """Fetch accounts with optional filter"""
    params = {"limit": 1000}
    if category:
        params["category"] = category
    response = requests.get(f"{API_BASE}/accounts", params=params)
    return response.json()

def trigger_scan():
    """Trigger a new scan"""
    response = requests.post(f"{API_BASE}/scan")
    return response.json()

# Main Dashboard
st.title("🔍 X-Cleaner Dashboard")
st.markdown("Analyze and categorize your X network")

# Sidebar
with st.sidebar:
    st.header("Actions")
    if st.button("🔄 Trigger New Scan", type="primary"):
        result = trigger_scan()
        st.success(result.get("message", "Scan started!"))

    st.header("Filters")
    show_verified_only = st.checkbox("Verified accounts only")

    st.header("Settings")
    st.markdown("[API Documentation](http://localhost:8000/docs)")

# Hero metrics
stats = fetch_stats()

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Accounts", stats.get("total_accounts", 0))
with col2:
    st.metric("Categories", stats.get("total_categories", 0))
with col3:
    st.metric("Verified", stats.get("verified_count", 0))
with col4:
    verified_pct = (stats.get("verified_count", 0) / stats.get("total_accounts", 1)) * 100
    st.metric("Verified %", f"{verified_pct:.1f}%")

# Tabs for different views
tab1, tab2, tab3 = st.tabs(["📊 Overview", "📁 Categories", "👥 Accounts"])

with tab1:
    st.header("Category Distribution")

    categories = fetch_categories()
    if categories:
        # Create dataframe for visualization
        cat_data = []
        for cat in categories.get("categories", []):
            cat_data.append({
                "Category": cat["name"],
                "Count": cat.get("account_count", 0),
                "Percentage": cat.get("estimated_percentage", 0)
            })

        df_cats = pd.DataFrame(cat_data)

        # Pie chart
        fig = px.pie(
            df_cats,
            values="Count",
            names="Category",
            title="Account Distribution by Category",
            hole=0.4
        )
        st.plotly_chart(fig, use_container_width=True)

        # Bar chart
        fig2 = px.bar(
            df_cats.sort_values("Count", ascending=False),
            x="Category",
            y="Count",
            title="Accounts per Category",
            color="Count",
            color_continuous_scale="Blues"
        )
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("No data available. Run a scan to get started!")

with tab2:
    st.header("Categories")

    categories = fetch_categories()
    if categories and "categories" in categories:
        for cat in categories["categories"]:
            with st.expander(f"📁 {cat['name']} ({cat.get('account_count', 0)} accounts)"):
                st.markdown(f"**Description:** {cat.get('description', 'N/A')}")

                if "characteristics" in cat:
                    st.markdown("**Characteristics:**")
                    for char in cat["characteristics"]:
                        st.markdown(f"- {char}")

                # Show top accounts in this category
                cat_accounts = requests.get(
                    f"{API_BASE}/categories/{cat['name']}/accounts"
                ).json()

                if cat_accounts:
                    st.markdown("**Top Accounts:**")
                    for acc in cat_accounts[:5]:
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.markdown(f"[@{acc['username']}]({acc.get('website', '#')}) - {acc['display_name']}")
                        with col2:
                            st.caption(f"{acc['followers_count']:,} followers")

with tab3:
    st.header("All Accounts")

    # Search
    search = st.text_input("🔍 Search accounts", placeholder="Search by username, name, or bio...")

    # Fetch and display accounts
    accounts_data = fetch_accounts()
    accounts = accounts_data.get("accounts", [])

    if accounts:
        # Filter by search
        if search:
            search = search.lower()
            accounts = [a for a in accounts if
                       search in a["username"].lower() or
                       search in a["display_name"].lower() or
                       (a.get("bio") and search in a["bio"].lower())]

        # Filter by verified if checkbox is selected
        if show_verified_only:
            accounts = [a for a in accounts if a.get("verified", False)]

        st.caption(f"Showing {len(accounts)} accounts")

        # Display accounts
        for acc in accounts[:50]:  # Limit to 50 for performance
            col1, col2, col3 = st.columns([2, 3, 1])

            with col1:
                verified = "✓" if acc.get("verified") else ""
                st.markdown(f"**@{acc['username']}** {verified}")
                st.caption(acc["display_name"])

            with col2:
                st.caption(f"📁 {acc.get('category', 'Uncategorized')}")
                if acc.get("bio"):
                    st.caption(acc["bio"][:100] + "..." if len(acc.get("bio", "")) > 100 else acc.get("bio", ""))

            with col3:
                st.metric("Followers", f"{acc['followers_count']:,}")

            st.divider()
    else:
        st.info("No accounts found. Run a scan first!")
```

**File: `streamlit_app/pages/1_Analytics.py`** - Advanced analytics

**File: `streamlit_app/pages/2_Settings.py`** - Configuration UI

**File: `streamlit_app/components/charts.py`** - Reusable chart components

---

### 8. CLI Interface (Optional - Day 11)

**File: `backend/cli/commands.py`**

```python
import typer
import asyncio
from rich.console import Console
from rich.progress import Progress

app = typer.Typer()
console = Console()

@app.command()
def scan(user_id: str = None):
    """Trigger scan via CLI"""
    console.print("[cyan]Triggering scan...[/cyan]")
    # Call FastAPI endpoint or run directly
    import requests
    response = requests.post("http://localhost:8000/api/scan", json={"user_id": user_id})
    console.print(response.json())

@app.command()
def export(format: str = "json"):
    """Export data"""
    import requests
    response = requests.get(f"http://localhost:8000/api/export?format={format}")
    console.print(f"[green]Exported to {format}[/green]")

if __name__ == "__main__":
    app()
```

## Timeline

### Web Dashboard MVP (Streamlit) ✅ **COMPLETE**

| Week | Days | Tasks | Status | PR |
|------|------|-------|--------|-----|
| 1 | 1-2 | Setup, Models, X API | ✅ Complete | #3 |
| 1 | 3-4 | Grok Client, Database | ✅ Complete | #4, #5 |
| 2 | 5-7 | FastAPI Backend | ✅ Complete | #6 |
| 2-3 | 8-10 | Streamlit Dashboard | ✅ Complete | #7 |
| 3 | 11-12 | Polish & Testing | ✅ Complete | #8, #9 |

**Total**: ✅ 3 weeks - Functional web dashboard delivered

**Achievement Unlocked**: Production-ready Streamlit MVP with 94% test coverage!

### Full React Dashboard (Optional)

| Week | Tasks |
|------|-------|
| 1-2 | Same as Streamlit MVP (backend + data layer) |
| 3-4 | React frontend development, component library |
| 5 | Integration, styling, responsive design |
| 6 | Testing, optimization, deployment |

**Total**: ~6 weeks for production-grade web app

## Testing Strategy

```python
# tests/test_x_client.py
import pytest
from src.api.x_client import XAPIClient

@pytest.mark.asyncio
async def test_get_following():
    client = XAPIClient()
    accounts, token = await client.get_following("12345", max_results=10)
    assert len(accounts) <= 10
    assert all(account.user_id for account in accounts)
```

## Deployment Checklist

- [x] All tests passing (94% coverage)
- [x] Documentation complete (README, ARCHITECTURE, CODE_CONVENTIONS, etc.)
- [x] .env.example up to date
- [x] Error handling robust
- [x] Rate limiting implemented
- [x] Logging configured
- [x] Performance optimized (caching, async operations)
- [x] Security reviewed (type safety, validation)
- [x] CI/CD pipeline (GitHub Actions for mypy + pylint)
- [x] Sample data generator for testing
- [x] Deployment documentation (PHASE5_DEPLOYMENT.md)
- [x] Quick start guide (QUICKSTART.md)

## ✅ Completed Actions

1. ✅ **Day 1-2**: Set up Python environment and project structure
2. ✅ **Day 3-4**: Implement core models, database, and X API client
3. ✅ **Day 5-6**: Integrate Grok with emergent categorization
4. ✅ **Day 7-10**: Build FastAPI backend with REST API
5. ✅ **Day 11-15**: Create Streamlit dashboard with charts and filtering
6. ✅ **Day 16-18**: Polish, test, and document

## 🔜 Next Actions (Phase 7)

See **Phase 7: Bulk Account Management Implementation** section below for detailed implementation guide.

---

## Running the Application

### Development Mode

**Terminal 1 - Backend API:**
```bash
cd x-cleaner
source venv/bin/activate
uvicorn backend.main:app --reload --port 8000
```

**Terminal 2 - Streamlit Dashboard:**
```bash
cd x-cleaner
source venv/bin/activate
streamlit run streamlit_app/app.py
```

**Access:**
- Dashboard: http://localhost:8501
- API Docs: http://localhost:8000/docs
- API Root: http://localhost:8000

### Production Mode

```bash
# Backend (with gunicorn)
gunicorn backend.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Streamlit (with custom config)
streamlit run streamlit_app/app.py --server.port 8501 --server.address 0.0.0.0
```

### Docker (Optional)

```yaml
# docker-compose.yml
version: '3.8'
services:
  backend:
    build: .
    command: uvicorn backend.main:app --host 0.0.0.0 --port 8000
    ports:
      - "8000:8000"
    environment:
      - X_API_BEARER_TOKEN=${X_API_BEARER_TOKEN}
      - XAI_API_KEY=${XAI_API_KEY}
    volumes:
      - ./data:/app/data

  frontend:
    build: .
    command: streamlit run streamlit_app/app.py
    ports:
      - "8501:8501"
    depends_on:
      - backend
    environment:
      - API_BASE=http://backend:8000/api
```

---

## Phase 7: Bulk Account Management Implementation

This phase adds the critical feature of unfollowing accounts in bulk - either entire categories or selected accounts with pagination persistence.

### 7.1 X API Unfollow Client

Add unfollow functionality to the X API client:

```python
# backend/api/x_client.py (add to existing XClient class)

class XClient:
    # ... existing methods ...

    async def unfollow_user(self, target_user_id: str) -> bool:
        """Unfollow a user by their ID.

        Args:
            target_user_id: The X user ID to unfollow

        Returns:
            True if successful, False otherwise

        Raises:
            XAPIError: If API call fails
        """
        # X API v2 endpoint: DELETE /2/users/:source_user_id/following/:target_user_id
        url = f"{self.base_url}/users/{self.authenticated_user_id}/following/{target_user_id}"

        try:
            response = await self.client.delete(
                url,
                headers=self.headers,
                timeout=30.0
            )

            if response.status_code == 200:
                return True
            elif response.status_code == 429:
                # Rate limit exceeded
                reset_time = response.headers.get("x-rate-limit-reset")
                raise XAPIError(
                    f"Rate limit exceeded. Resets at {reset_time}",
                    details={"reset_time": reset_time}
                )
            else:
                logger.error(f"Unfollow failed: {response.status_code} - {response.text}")
                return False

        except httpx.HTTPError as e:
            raise XAPIError(f"Failed to unfollow user {target_user_id}: {e}") from e

    async def bulk_unfollow(
        self,
        user_ids: List[str],
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
        rate_limit_delay: float = 1.2  # ~50 requests per 15min = 1.2s between requests
    ) -> Dict[str, Any]:
        """Unfollow multiple users with rate limiting.

        Args:
            user_ids: List of user IDs to unfollow
            progress_callback: Optional callback for progress updates
            rate_limit_delay: Seconds to wait between requests

        Returns:
            Dict with success_count, failed_accounts, total_time
        """
        results = {
            "success_count": 0,
            "failed_accounts": [],
            "total_time": 0
        }

        start_time = time.time()

        for idx, user_id in enumerate(user_ids):
            try:
                success = await self.unfollow_user(user_id)

                if success:
                    results["success_count"] += 1
                else:
                    results["failed_accounts"].append({
                        "user_id": user_id,
                        "error": "Unfollow returned false"
                    })

                # Progress callback
                if progress_callback:
                    await progress_callback(idx + 1, len(user_ids), user_id)

                # Rate limiting: wait between requests
                if idx < len(user_ids) - 1:  # Don't wait after last request
                    await asyncio.sleep(rate_limit_delay)

            except XAPIError as e:
                results["failed_accounts"].append({
                    "user_id": user_id,
                    "error": str(e)
                })

                # If rate limit error, wait longer
                if "rate limit" in str(e).lower():
                    logger.warning(f"Rate limit hit, waiting 60 seconds...")
                    await asyncio.sleep(60)

        results["total_time"] = time.time() - start_time
        return results
```

### 7.2 Backend Unfollow Service

Create a service to manage unfollow operations:

```python
# backend/core/services/unfollow_service.py

import uuid
from typing import List, Dict, Optional, Callable
from datetime import datetime, timedelta
from backend.api.x_client import XClient
from backend.db.repositories.account_repository import AccountRepository
from backend.db.repositories.unfollow_history_repository import UnfollowHistoryRepository

class UnfollowService:
    """Service for managing bulk unfollow operations."""

    def __init__(
        self,
        x_client: XClient,
        account_repo: AccountRepository,
        history_repo: UnfollowHistoryRepository
    ):
        self._x_client = x_client
        self._accounts = account_repo
        self._history = history_repo
        self._active_jobs: Dict[str, Dict] = {}

    async def unfollow_category(
        self,
        category_name: str,
        progress_callback: Optional[Callable] = None
    ) -> str:
        """Unfollow all accounts in a category.

        Args:
            category_name: Name of category to unfollow
            progress_callback: Optional async callback for progress updates

        Returns:
            Job ID for tracking progress
        """
        # Get all accounts in category
        accounts = self._accounts.get_by_category(category_name)

        if not accounts:
            raise ValueError(f"No accounts found in category '{category_name}'")

        # Create job
        job_id = str(uuid.uuid4())
        self._active_jobs[job_id] = {
            "status": "running",
            "category": category_name,
            "total": len(accounts),
            "current": 0,
            "success": 0,
            "failed": []
        }

        # Extract user IDs
        user_ids = [acc.id for acc in accounts]

        # Create progress wrapper
        async def track_progress(current: int, total: int, user_id: str):
            self._active_jobs[job_id]["current"] = current
            if progress_callback:
                await progress_callback(current, total, user_id)

        # Execute bulk unfollow
        results = await self._x_client.bulk_unfollow(user_ids, track_progress)

        # Update job status
        self._active_jobs[job_id]["status"] = "complete"
        self._active_jobs[job_id]["success"] = results["success_count"]
        self._active_jobs[job_id]["failed"] = results["failed_accounts"]

        # Save to history
        await self._history.save({
            "job_id": job_id,
            "operation": "unfollow_category",
            "category": category_name,
            "account_ids": user_ids,
            "success_count": results["success_count"],
            "failed_count": len(results["failed_accounts"]),
            "timestamp": datetime.utcnow()
        })

        return job_id

    async def unfollow_bulk(
        self,
        account_ids: List[str],
        progress_callback: Optional[Callable] = None
    ) -> str:
        """Unfollow selected accounts in bulk.

        Args:
            account_ids: List of account IDs to unfollow
            progress_callback: Optional async callback for progress updates

        Returns:
            Job ID for tracking progress
        """
        # Create job
        job_id = str(uuid.uuid4())
        self._active_jobs[job_id] = {
            "status": "running",
            "total": len(account_ids),
            "current": 0,
            "success": 0,
            "failed": []
        }

        # Create progress wrapper
        async def track_progress(current: int, total: int, user_id: str):
            self._active_jobs[job_id]["current"] = current
            if progress_callback:
                await progress_callback(current, total, user_id)

        # Execute bulk unfollow
        results = await self._x_client.bulk_unfollow(account_ids, track_progress)

        # Update job status
        self._active_jobs[job_id]["status"] = "complete"
        self._active_jobs[job_id]["success"] = results["success_count"]
        self._active_jobs[job_id]["failed"] = results["failed_accounts"]

        # Save to history
        await self._history.save({
            "job_id": job_id,
            "operation": "unfollow_bulk",
            "account_ids": account_ids,
            "success_count": results["success_count"],
            "failed_count": len(results["failed_accounts"]),
            "timestamp": datetime.utcnow()
        })

        return job_id

    def get_job_status(self, job_id: str) -> Optional[Dict]:
        """Get status of unfollow job."""
        return self._active_jobs.get(job_id)

    async def get_recent_history(self, hours: int = 24) -> List[Dict]:
        """Get recent unfollow operations for undo feature."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        return await self._history.get_since(cutoff)

    async def refollow_batch(self, account_ids: List[str]) -> Dict:
        """Refollow accounts (undo feature).

        Note: This requires using the X API follow endpoint.
        """
        # Implementation similar to bulk_unfollow but using follow endpoint
        # Left as exercise - similar pattern to unfollow
        pass
```

### 7.3 FastAPI Endpoints

Add the unfollow endpoints to your API:

```python
# backend/routes/unfollow.py

from fastapi import APIRouter, BackgroundTasks, Depends, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import List
from backend.core.services.unfollow_service import UnfollowService
from backend.dependencies import get_unfollow_service

router = APIRouter(prefix="/api/unfollow", tags=["unfollow"])

class BulkUnfollowRequest(BaseModel):
    """Request model for bulk unfollow."""
    account_ids: List[str]

class RefollowRequest(BaseModel):
    """Request model for refollow."""
    account_ids: List[str]

@router.post("/category/{category_name}")
async def unfollow_category(
    category_name: str,
    background_tasks: BackgroundTasks,
    service: UnfollowService = Depends(get_unfollow_service)
):
    """Unfollow all accounts in a category.

    Returns job_id for tracking progress via WebSocket or polling.
    """
    job_id = await service.unfollow_category(category_name)

    return {
        "job_id": job_id,
        "message": f"Unfollow operation started for category '{category_name}'"
    }

@router.post("/bulk")
async def unfollow_bulk(
    request: BulkUnfollowRequest,
    background_tasks: BackgroundTasks,
    service: UnfollowService = Depends(get_unfollow_service)
):
    """Unfollow selected accounts in bulk.

    Returns job_id for tracking progress.
    """
    job_id = await service.unfollow_bulk(request.account_ids)

    return {
        "job_id": job_id,
        "message": f"Unfollow operation started for {len(request.account_ids)} accounts"
    }

@router.get("/{job_id}/status")
async def get_unfollow_status(
    job_id: str,
    service: UnfollowService = Depends(get_unfollow_service)
):
    """Get status of unfollow operation."""
    status = service.get_job_status(job_id)

    if not status:
        return {"error": "Job not found"}, 404

    return status

@router.get("/history")
async def get_unfollow_history(
    hours: int = 24,
    service: UnfollowService = Depends(get_unfollow_service)
):
    """Get recent unfollow operations (for undo feature)."""
    history = await service.get_recent_history(hours)
    return {"history": history}

@router.post("/refollow")
async def refollow_batch(
    request: RefollowRequest,
    service: UnfollowService = Depends(get_unfollow_service)
):
    """Refollow accounts (undo feature)."""
    results = await service.refollow_batch(request.account_ids)
    return results

@router.websocket("/ws/{job_id}")
async def websocket_unfollow_progress(
    websocket: WebSocket,
    job_id: str,
    service: UnfollowService = Depends(get_unfollow_service)
):
    """WebSocket endpoint for real-time unfollow progress."""
    await websocket.accept()

    try:
        while True:
            status = service.get_job_status(job_id)

            if not status:
                await websocket.send_json({"error": "Job not found"})
                break

            await websocket.send_json(status)

            if status["status"] == "complete":
                break

            await asyncio.sleep(0.5)  # Update every 500ms

    except WebSocketDisconnect:
        logger.info(f"Client disconnected from unfollow progress WebSocket")
```

### 7.4 Streamlit UI - Bulk Selection

Add bulk selection with pagination persistence:

```python
# streamlit_app/components/bulk_selector.py

import streamlit as st
from typing import List, Set

class BulkSelector:
    """Component for bulk selection with pagination persistence."""

    def __init__(self, session_key: str = "selected_accounts"):
        self.session_key = session_key

        # Initialize session state
        if self.session_key not in st.session_state:
            st.session_state[self.session_key] = set()

    def render(self, accounts: List[dict], page_size: int = 20):
        """Render bulk selector UI with pagination.

        Args:
            accounts: List of account dicts with 'id', 'username', 'name', etc.
            page_size: Number of accounts per page
        """
        # Get current selection
        selected: Set[str] = st.session_state[self.session_key]

        # Pagination
        total_pages = (len(accounts) + page_size - 1) // page_size

        if "current_page" not in st.session_state:
            st.session_state.current_page = 0

        # Selection controls
        col1, col2, col3 = st.columns([2, 2, 3])

        with col1:
            if st.button("✓ Select All on Page"):
                page_accounts = accounts[
                    st.session_state.current_page * page_size:
                    (st.session_state.current_page + 1) * page_size
                ]
                for acc in page_accounts:
                    selected.add(acc["id"])
                st.rerun()

        with col2:
            if st.button("Clear Selection"):
                selected.clear()
                st.rerun()

        with col3:
            st.markdown(f"**Selected: {len(selected)} accounts** across all pages")

        st.markdown("---")

        # Display accounts for current page
        start_idx = st.session_state.current_page * page_size
        end_idx = min(start_idx + page_size, len(accounts))
        page_accounts = accounts[start_idx:end_idx]

        for account in page_accounts:
            col1, col2 = st.columns([1, 20])

            with col1:
                is_selected = account["id"] in selected
                if st.checkbox("", value=is_selected, key=f"cb_{account['id']}"):
                    selected.add(account["id"])
                else:
                    selected.discard(account["id"])

            with col2:
                st.markdown(f"""
                **[@{account['username']}](https://x.com/{account['username']})** {account['name']}
                👥 {account.get('followers_count', 0):,} followers
                {account.get('description', '')[:100]}...
                """)

            st.markdown("---")

        # Pagination controls
        col1, col2, col3 = st.columns([1, 2, 1])

        with col1:
            if st.button("← Previous") and st.session_state.current_page > 0:
                st.session_state.current_page -= 1
                st.rerun()

        with col2:
            st.markdown(f"Page {st.session_state.current_page + 1} of {total_pages}")

        with col3:
            if st.button("Next →") and st.session_state.current_page < total_pages - 1:
                st.session_state.current_page += 1
                st.rerun()

        # Action buttons
        st.markdown("---")

        if len(selected) > 0:
            col1, col2, col3 = st.columns([2, 2, 2])

            with col1:
                if st.button(f"⚠️ Unfollow Selected ({len(selected)})", type="primary"):
                    self.show_confirmation_dialog(list(selected))

            with col2:
                if st.button("Export Selection"):
                    self.export_selection(accounts, selected)

        return selected

    def show_confirmation_dialog(self, account_ids: List[str]):
        """Show confirmation dialog before unfollowing."""
        st.session_state.show_unfollow_confirm = True
        st.session_state.accounts_to_unfollow = account_ids

    def export_selection(self, all_accounts: List[dict], selected_ids: Set[str]):
        """Export selected accounts to CSV."""
        import pandas as pd

        selected_accounts = [acc for acc in all_accounts if acc["id"] in selected_ids]
        df = pd.DataFrame(selected_accounts)

        csv = df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name="selected_accounts.csv",
            mime="text/csv"
        )


# streamlit_app/pages/3_Category_Details.py

import streamlit as st
import requests
from components.bulk_selector import BulkSelector

st.set_page_config(page_title="Category Details", layout="wide")

# Get category from query params
category_name = st.query_params.get("category")

if not category_name:
    st.error("No category selected")
    st.stop()

st.title(f"📁 {category_name}")

# Fetch accounts in category
response = requests.get(f"http://localhost:8000/api/categories/{category_name}/accounts")
accounts = response.json()

st.markdown(f"**{len(accounts)} accounts** in this category")

# Show unfollow all button
if st.button(f"⚠️ Unfollow All {len(accounts)} Accounts", type="primary"):
    st.session_state.show_category_unfollow_confirm = True

# Confirmation dialog for unfollow all
if st.session_state.get("show_category_unfollow_confirm"):
    with st.expander("⚠️ Confirm Unfollow All", expanded=True):
        st.warning(f"""
        You are about to unfollow **all {len(accounts)} accounts** in "{category_name}".

        This action will:
        - Unfollow {len(accounts)} accounts on X
        - Take approximately {len(accounts) * 1.2 / 60:.1f} minutes (rate limiting)
        - Remove these accounts from your X following list

        ⚠️ This action cannot be easily undone.
        """)

        confirm = st.checkbox("I understand and want to proceed")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Cancel"):
                st.session_state.show_category_unfollow_confirm = False
                st.rerun()

        with col2:
            if st.button(f"⚠️ Unfollow All {len(accounts)}", disabled=not confirm):
                # Trigger unfollow
                response = requests.post(
                    f"http://localhost:8000/api/unfollow/category/{category_name}"
                )
                job_data = response.json()
                st.session_state.unfollow_job_id = job_data["job_id"]
                st.session_state.show_category_unfollow_confirm = False
                st.rerun()

st.markdown("---")

# Bulk selector
st.subheader("Select Individual Accounts")
selector = BulkSelector(session_key=f"selected_{category_name}")
selected = selector.render(accounts)

# Show unfollow confirmation for bulk selection
if st.session_state.get("show_unfollow_confirm"):
    account_ids = st.session_state.accounts_to_unfollow

    with st.expander("⚠️ Confirm Bulk Unfollow", expanded=True):
        st.warning(f"""
        You have selected **{len(account_ids)} accounts** to unfollow.

        Estimated time: ~{len(account_ids) * 1.2 / 60:.1f} minutes
        """)

        confirm = st.checkbox("I understand this action cannot be easily undone")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Cancel"):
                st.session_state.show_unfollow_confirm = False
                st.rerun()

        with col2:
            if st.button(f"⚠️ Unfollow {len(account_ids)} Accounts", disabled=not confirm):
                # Trigger bulk unfollow
                response = requests.post(
                    "http://localhost:8000/api/unfollow/bulk",
                    json={"account_ids": account_ids}
                )
                job_data = response.json()
                st.session_state.unfollow_job_id = job_data["job_id"]
                st.session_state.show_unfollow_confirm = False
                st.rerun()

# Show progress if unfollow job is running
if st.session_state.get("unfollow_job_id"):
    job_id = st.session_state.unfollow_job_id

    with st.container():
        st.subheader("⏳ Unfollow Progress")

        progress_placeholder = st.empty()
        status_placeholder = st.empty()

        # Poll for status
        response = requests.get(f"http://localhost:8000/api/unfollow/{job_id}/status")
        status = response.json()

        if status["status"] == "running":
            progress = status["current"] / status["total"]
            progress_placeholder.progress(progress)
            status_placeholder.markdown(f"""
            **Unfollowing accounts...** {status['current']}/{status['total']}

            ✓ Successful: {status['success']}
            ⚠️ Failed: {len(status['failed'])}
            """)
        elif status["status"] == "complete":
            st.success(f"""
            ✓ **Unfollow Complete!**

            Successfully unfollowed: {status['success']} accounts
            Failed: {len(status['failed'])} accounts
            """)

            if status['failed']:
                with st.expander("View failed accounts"):
                    st.json(status['failed'])

            # Clear job ID
            del st.session_state.unfollow_job_id
```

### 7.5 Database Schema for Unfollow History

Add table for tracking unfollow operations:

```python
# backend/db/models.py (add to existing models)

from sqlalchemy import Column, String, Integer, DateTime, JSON
from datetime import datetime

class UnfollowHistory(Base):
    """Track unfollow operations for undo feature."""

    __tablename__ = "unfollow_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(String, unique=True, nullable=False)
    operation = Column(String, nullable=False)  # 'unfollow_category' or 'unfollow_bulk'
    category = Column(String, nullable=True)  # If category unfollow
    account_ids = Column(JSON, nullable=False)  # List of account IDs
    success_count = Column(Integer, nullable=False)
    failed_count = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<UnfollowHistory {self.job_id} - {self.operation}>"
```

---

**Ready to start coding!** 🚀
