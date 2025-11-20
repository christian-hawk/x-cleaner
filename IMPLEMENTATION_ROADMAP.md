# Implementation Roadmap

Quick reference guide for implementing the X-Cleaner project.

## Immediate Next Steps

### 1. Environment Setup (Day 1)

```bash
# Create project structure
mkdir -p src/api src/analysis src/reporting tests data templates

# Create __init__.py files
touch src/__init__.py src/api/__init__.py src/analysis/__init__.py src/reporting/__init__.py

# Create requirements.txt
cat > requirements.txt << EOF
httpx>=0.25.0
pandas>=2.1.0
python-dotenv>=1.0.0
typer>=0.9.0
rich>=13.0.0
pydantic>=2.5.0
sqlalchemy>=2.0.0
jinja2>=3.1.0
plotly>=5.18.0
openai>=1.0.0
EOF

# Install dependencies
pip install -r requirements.txt

# Create .env.example
cat > .env.example << EOF
X_API_BEARER_TOKEN=your_bearer_token_here
X_USER_ID=your_user_id_here
XAI_API_KEY=your_xai_api_key_here
DATABASE_PATH=data/accounts.db
BATCH_SIZE=100
CACHE_EXPIRY_DAYS=7
EOF
```

### 2. Core Models (Day 1-2)

**File: `src/models.py`**

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

**File: `src/api/x_client.py`**

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

**File: `src/api/grok_client.py`**

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

**File: `src/database.py`**

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

### 6. CLI Interface (Day 5)

**File: `src/main.py`**

```python
import typer
import asyncio
from rich.console import Console
from rich.progress import Progress
from .api.x_client import XAPIClient
from .api.grok_client import GrokClient
from .database import DatabaseManager
from .reporting.console import ConsoleReporter

app = typer.Typer()
console = Console()

@app.command()
def scan(user_id: str = typer.Option(None, help="X user ID to scan")):
    """Scan and categorize following accounts"""
    asyncio.run(_scan_async(user_id))

async def _scan_async(user_id: Optional[str]):
    x_client = XAPIClient()
    grok_client = GrokClient()
    db = DatabaseManager()

    user_id = user_id or os.getenv("X_USER_ID")

    with Progress() as progress:
        # Fetch accounts
        task = progress.add_task("[cyan]Fetching following accounts...", total=None)
        accounts = await x_client.get_all_following(user_id)
        progress.update(task, completed=100)

        console.print(f"✓ Found {len(accounts)} accounts")

        # Phase 1: Discover categories
        task = progress.add_task(
            "[cyan]Discovering natural categories...",
            total=None
        )
        categories, categorized = await grok_client.analyze_and_categorize(accounts)
        progress.update(task, completed=100)

        console.print(f"✓ Discovered {len(categories['categories'])} categories")
        console.print(f"✓ Categorized all {len(categorized)} accounts")

        # Save
        db.save_accounts(categorized)
        db.save_categories(categories)  # Store discovered categories
        console.print("✓ Saved to database")

    # Show report with discovered categories
    reporter = ConsoleReporter()
    reporter.show_summary(categorized, categories)

    await x_client.close()

@app.command()
def report():
    """Generate report from cached data"""
    db = DatabaseManager()
    accounts = db.get_all_accounts()

    if not accounts:
        console.print("❌ No data found. Run 'scan' first.")
        return

    reporter = ConsoleReporter()
    reporter.show_summary(accounts)

if __name__ == "__main__":
    app()
```

## Timeline

| Day | Tasks | Deliverables |
|-----|-------|--------------|
| 1 | Setup, Models | Working environment, data models |
| 2-3 | X API Client | Fetch following accounts |
| 3-4 | Grok Client | Categorization working |
| 4 | Database | Data persistence |
| 5 | CLI | Basic commands working |
| 6-7 | Reporting | Console + export formats |
| 8 | Testing & Polish | Production ready |

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

- [ ] All tests passing
- [ ] Documentation complete
- [ ] .env.example up to date
- [ ] Error handling robust
- [ ] Rate limiting implemented
- [ ] Logging configured
- [ ] Performance optimized
- [ ] Security reviewed

## Next Actions

1. **Immediate**: Set up Python environment and project structure
2. **Day 1**: Implement core models and database
3. **Day 2-3**: Build X API client and test
4. **Day 4-5**: Integrate Grok and create CLI
5. **Day 6-7**: Add reporting and polish
6. **Day 8**: Final testing and documentation

---

**Ready to start coding!** 🚀
