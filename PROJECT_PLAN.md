# X Account Scanner & Categorization Tool - Project Plan

## Executive Summary

This project aims to build a tool that scans X (Twitter) accounts a user follows, categorizes them based on their social activity, and provides statistical insights. The tool will leverage X API v2 for data collection and xAI's Grok API for intelligent categorization and analysis.

---

## 1. Project Overview

### 1.1 Objectives

- **Primary Goal**: Scan and categorize all accounts a user follows on X
- **Analysis**: Provide categorization based on account activity, content type, and engagement patterns
- **Insights**: Generate statistics showing distribution across categories and top accounts per category
- **Automation**: Minimize manual categorization through AI-powered analysis

### 1.2 Key Features

1. **Account Data Collection**: Fetch all following accounts using X API v2
2. **Profile Analysis**: Extract and analyze account metadata, recent tweets, engagement metrics
3. **AI-Powered Categorization**: Use Grok API to intelligently categorize accounts
4. **Interactive Web Dashboard**: Rich web UI for exploring categories, statistics, and top accounts
5. **Visual Analytics**: Charts, graphs, and interactive visualizations
6. **Export Functionality**: Save results in multiple formats (JSON, CSV, PDF report)

---

## 2. Technical Architecture

### 2.1 Technology Stack

**Backend/Core:**
- **Language**: Python 3.11+
- **Web Framework**: FastAPI (modern, async, REST API)
- **HTTP Client**: `httpx` (async support for API calls)
- **Data Processing**: `pandas` for data analysis
- **Storage**: SQLite for local data persistence
- **Configuration**: `python-dotenv` for environment variables

**API Integration:**
- **X API v2**: For fetching following accounts and user data
- **Grok API**: For AI-powered categorization and analysis
- **xAI Python SDK**: Official SDK for Grok integration

**Frontend/Web UI:**
- **Framework**: React with TypeScript (modern, component-based)
- **UI Library**: Shadcn/ui or Tailwind CSS for styling
- **Charts**: Recharts or Chart.js for visualizations
- **State Management**: TanStack Query for API data
- **Build Tool**: Vite for fast development

**Alternative (Simpler):**
- **Framework**: Streamlit or Gradio (Python-based, rapid prototyping)
- **Benefits**: No separate frontend needed, faster initial development
- **Charts**: Built-in Plotly integration

**CLI Interface:**
- **Framework**: `typer` for command-line operations
- **Purpose**: Scanning, data updates, background tasks

### 2.2 System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Web Dashboard (React)                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  Categories  │  │  Statistics  │  │   Accounts   │         │
│  │     View     │  │    Charts    │  │    Browser   │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────────────────┬────────────────────────────────────────┘
                         │ HTTP/REST API
┌────────────────────────▼────────────────────────────────────────┐
│                  FastAPI Backend Server                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  REST API    │  │  WebSocket   │  │   Auth       │         │
│  │  Endpoints   │  │  (realtime)  │  │  (optional)  │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────────────────┬────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                   Core Application Layer                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   X API      │  │   Grok API   │  │   Database   │         │
│  │   Client     │  │   Client     │  │   Manager    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────────────────┬────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────┐
│               Processing Pipeline (Background)                  │
│  1. Fetch Following → 2. Discover Categories → 3. Categorize   │
│  4. Generate Statistics → 5. Store Results                     │
└─────────────────────────────────────────────────────────────────┘
                         ▲
                         │
                ┌────────┴────────┐
                │  CLI Interface  │
                │  (Scan trigger) │
                └─────────────────┘
```

**Architecture Overview:**

**Frontend (Web Dashboard):**
- Interactive React app with real-time updates
- Category browsing with filtering and search
- Visual charts for distribution and trends
- Account detail views with profile information
- Export functionality

**Backend (FastAPI):**
- REST API for data access
- WebSocket for real-time scan progress
- Background task queue for scanning
- Caching layer for performance

**CLI:**
- Trigger scans and updates
- Admin operations
- Scheduled background tasks

---

## 3. X API Integration

### 3.1 Required Endpoints

**Primary Endpoint:**
- `GET /2/users/:id/following` - Fetch accounts user follows
  - Supports pagination (max 1000 results per request)
  - Returns user IDs and basic metadata

**Supporting Endpoints:**
- `GET /2/users` - Batch user lookup for detailed information
- `GET /2/users/:id/tweets` - Recent tweets for content analysis (optional)

### 3.2 API Access Requirements

**Tier Needed**: Basic Plan or higher
- **Cost**: $200/month (or $2,100/year)
- **Rate Limits**: 10K posts/month
- **Endpoints**: Full access to follows endpoints

**Authentication**: OAuth 2.0 Bearer Token
- Store in environment variables
- Implement token refresh mechanism

### 3.3 Data Fields to Collect

From `/2/users/:id/following`:
- User ID
- Username
- Display Name
- Bio/Description
- Verified status
- Creation date
- Profile image URL
- Public metrics (followers, following, tweet count)
- Location
- Website URL

---

## 4. Grok API Integration

### 4.1 API Capabilities

**Model**: grok-4-1-fast-reasoning
- Real-time X data access
- Agent Tools API for autonomous operations
- Compatible with OpenAI SDK format

### 4.2 Categorization Strategy

**Approach 1: Batch Categorization (Recommended)**
```python
# Send batch of account profiles to Grok
# Grok analyzes and returns categories for all accounts
```

**Approach 2: Individual Analysis**
```python
# Analyze each account separately
# More detailed but slower and more expensive
```

### 4.3 Prompting Strategy

**Phase 1: Category Discovery Prompt**
```
You are an expert at analyzing social media networks and identifying natural community patterns.

I have [N] X (Twitter) accounts that a user follows. Your task is to:
1. Analyze all accounts holistically
2. Identify 10-20 natural categories based on actual patterns in the data
3. Provide clear, descriptive names for each category
4. Explain the key characteristics of each category

For each account, you have:
- Username and display name
- Bio/description
- Follower/following counts
- Verified status
- Tweet count and account age
- Location (if provided)

Do NOT use predefined categories. Instead, discover the natural groupings that emerge from THIS specific dataset. Look for:
- Common themes and topics
- Professional domains and industries
- Content styles and engagement patterns
- Community overlap and connections
- Account types (individual, organization, bot, etc.)

Provide categories as JSON with this structure:
{
  "categories": [
    {
      "name": "AI/ML Researchers & Practitioners",
      "description": "...",
      "characteristics": [...],
      "estimated_size": "10-15%"
    }
  ]
}
```

**Phase 2: Account Categorization Prompt**
```
You are an expert at categorizing X accounts based on discovered patterns.

Using the following category system you discovered:
[Insert discovered categories from Phase 1]

Now categorize each of these accounts. For each account, provide:
- Primary category (must be from the discovered categories)
- Confidence score (0.0 to 1.0)
- Brief reasoning (1-2 sentences)
- Alternative category if confidence < 0.8

Respond as JSON array:
[
  {
    "username": "@example",
    "category": "AI/ML Researchers & Practitioners",
    "confidence": 0.95,
    "reasoning": "...",
    "alternative": null
  }
]
```

**Key Considerations:**
- Bio description and self-identification
- Content patterns and topics
- Follower/following ratio and verified status
- Account activity level and age
- Website domain patterns
- Community indicators

### 4.4 Cost Estimation

**Pricing:**
- Input: $0.20 per million tokens ($0.05 cached)
- Output: $0.50 per million tokens
- Tool usage: Free until Dec 3, 2025

**Estimated Cost for 1000 Accounts:**
- ~200 tokens per account = 200K tokens input
- ~20 tokens output per account = 20K tokens output
- **Total**: ~$0.05 per 1000 accounts (very affordable)

---

## 5. Categorization System

### 5.1 Emergent, AI-Driven Categorization

**Philosophy:** Instead of forcing accounts into predefined categories, we let Grok analyze the entire dataset and discover natural groupings based on actual patterns in the data.

**Two-Phase Approach:**

**Phase 1: Discovery & Analysis**
- Grok analyzes all accounts holistically
- Identifies common themes, patterns, and natural clusters
- Discovers emergent categories based on:
  - Content themes and topics
  - Audience overlap and community patterns
  - Account behavior and engagement style
  - Bio descriptions and self-identification
  - Activity patterns and posting frequency

**Phase 2: Categorization & Refinement**
- Assigns each account to discovered categories
- Provides reasoning for each categorization
- Identifies outliers and unique accounts
- Suggests subcategories or nuanced groupings

### 5.2 Categorization Strategy

**Approach 1: Holistic Analysis (Recommended)**
```
Step 1: Send all account data to Grok in batches
Step 2: Ask Grok to identify natural categories (10-20)
Step 3: Grok categorizes each account into discovered categories
Step 4: Generate category descriptions and characteristics
```

**Approach 2: Iterative Clustering**
```
Step 1: Analyze sample set (100-200 accounts)
Step 2: Identify initial category patterns
Step 3: Categorize remaining accounts
Step 4: Refine categories based on full dataset
```

### 5.3 Category Discovery Criteria

Grok will consider multiple dimensions:

**Content Analysis:**
- Primary topics discussed
- Language style and tone
- Expertise level (expert, enthusiast, casual)
- Content format (threads, links, media, quotes)

**Account Characteristics:**
- Professional vs. personal
- Individual vs. organization
- Influencer vs. niche expert
- Active vs. archived accounts

**Community Patterns:**
- Who they interact with
- Follower/following ratio patterns
- Verified status implications
- Cross-category influences

**Behavioral Indicators:**
- Posting frequency and consistency
- Engagement patterns
- Content curation vs. creation
- Multi-topic vs. single-focus

### 5.4 Category Metadata

Each discovered category includes:
- **Name**: AI-generated descriptive name
- **Description**: Key characteristics and themes
- **Account Count**: Number of accounts in category
- **Exemplars**: Top representative accounts
- **Subcategories**: Optional finer distinctions
- **Related Categories**: Overlap patterns

### 5.5 Example Output Structure

```json
{
  "categories": [
    {
      "name": "AI/ML Researchers & Practitioners",
      "description": "Accounts focused on artificial intelligence research, machine learning engineering, and AI product development",
      "account_count": 87,
      "characteristics": [
        "Frequent technical discussions",
        "Paper sharing and research updates",
        "High engagement with academic community"
      ],
      "exemplars": ["@user1", "@user2", "@user3"],
      "subcategories": ["Academic AI", "AI Product", "AI Safety"]
    },
    {
      "name": "Indie Makers & Bootstrapped Founders",
      "description": "Solo entrepreneurs building products independently without VC funding",
      "account_count": 64,
      "characteristics": [
        "Share building in public",
        "Revenue and metrics transparency",
        "Strong mutual support community"
      ],
      "exemplars": ["@user4", "@user5", "@user6"]
    }
  ]
}
```

### 5.6 Confidence & Quality Metrics

**Per-Account Confidence:**
- How well account fits discovered category
- Alternative category possibilities
- Uncertainty indicators

**Category Quality Scores:**
- Coherence: How similar accounts within category are
- Distinctiveness: How different from other categories
- Completeness: Coverage of the account space
- Interpretability: How clear the category definition is

---

## 6. Statistical Analysis & Reporting

### 6.1 Statistics to Generate

**Category Distribution:**
- Number of accounts per category
- Percentage distribution
- Visual pie/bar chart

**Top Accounts per Category:**
- Top 5 accounts by follower count
- Top 5 by engagement rate
- Most recently followed

**Overall Insights:**
- Total accounts analyzed
- Most popular category
- Least popular category
- Average follower count per category
- Verification rate per category

**Account Metrics:**
- Average followers per account
- Average following per account
- Average tweet count
- Average account age

### 6.2 Report Formats

**Console Output:**
```
📊 X Account Analysis Report
════════════════════════════════════════

Total Accounts Analyzed: 847
Categories Found: 15

📈 Category Distribution:
├─ Technology & Development: 234 (27.6%)
├─ Business & Finance: 156 (18.4%)
├─ News & Media: 98 (11.6%)
├─ Entertainment: 87 (10.3%)
└─ [...]

🏆 Top 5 - Technology & Development:
  1. @username1 (2.3M followers) - Software Engineer
  2. @username2 (1.8M followers) - Tech Company
  [...]
```

**JSON Export:**
```json
{
  "summary": {
    "total_accounts": 847,
    "categories": 15,
    "analyzed_date": "2025-11-20"
  },
  "categories": [
    {
      "name": "Technology & Development",
      "count": 234,
      "percentage": 27.6,
      "top_accounts": [...]
    }
  ]
}
```

**CSV Export:**
- One row per account
- All metadata included
- Easy to import into spreadsheets

---

## 7. Web Dashboard UI Design

### 7.1 Dashboard Overview

The web dashboard is the primary interface for viewing and exploring your categorized X network. It provides an intuitive, visual way to understand your following patterns.

**Key Pages:**
1. **Overview Dashboard** - Summary statistics and key metrics
2. **Categories View** - Browse all discovered categories
3. **Accounts Browser** - Search and filter all accounts
4. **Analytics** - Deep dive into trends and patterns
5. **Settings** - Configuration and scan management

### 7.2 Overview Dashboard (Landing Page)

**Hero Section:**
```
┌────────────────────────────────────────────────────────────┐
│  Your X Network Analysis                                   │
│  Last updated: 2 hours ago                    [Refresh]    │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │     847      │  │      15      │  │    234/847   │   │
│  │   Accounts   │  │  Categories  │  │   Verified   │   │
│  │   Following  │  │  Discovered  │  │    (27.6%)   │   │
│  └──────────────┘  └──────────────┘  └──────────────┘   │
└────────────────────────────────────────────────────────────┘
```

**Category Distribution Chart:**
- Interactive pie or donut chart
- Click to filter by category
- Hover for details
- Legend with counts and percentages

**Recent Insights:**
- "You follow more AI researchers than any other category"
- "Your most followed account is @username with 2.3M followers"
- "You've added 12 new follows since last scan"

### 7.3 Categories View

**Category Grid:**
```
┌─────────────────────────────────────────────────────────────┐
│  AI/ML Researchers & Practitioners          [87 accounts]  │
│  ━━━━━━━━━━━━━━━━━━━━ 10.3%                               │
│                                                             │
│  🏆 Top Accounts:                                          │
│  1. @researcher1 (2.3M) • AI Research Lead                │
│  2. @mlexpert (1.8M) • ML Engineer                        │
│  3. @aiethics (950K) • AI Safety Researcher               │
│  [View all 87 →]                                          │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  Indie Makers & Bootstrapped Founders       [64 accounts]  │
│  ━━━━━━━━━━━━━━━━ 7.6%                                     │
│                                                             │
│  🏆 Top Accounts:                                          │
│  1. @maker1 (450K) • Building in public                   │
│  2. @founder2 (380K) • SaaS founder                       │
│  [View all 64 →]                                          │
└─────────────────────────────────────────────────────────────┘
```

**Category Details Modal:**
- Full description and characteristics
- All accounts in category
- Subcategories if any
- Export category data
- Confidence scores

### 7.4 Accounts Browser

**Search and Filters:**
- Search by username, display name, or bio
- Filter by category
- Filter by verified status
- Filter by follower count range
- Sort by: followers, following, tweets, recency

**Account Cards:**
```
┌────────────────────────────────────────────────────────────┐
│  [@username]  Display Name                    ✓ Verified   │
│  [Profile Pic]                                             │
│  Bio: Machine learning engineer building AI tools...       │
│                                                            │
│  👥 2.3M followers  •  842 following  •  12.4K tweets     │
│  📁 AI/ML Researchers & Practitioners (95% confidence)     │
│  🔗 website.com                                           │
│                                                            │
│  [View on X]  [Remove]  [Re-categorize]                  │
└────────────────────────────────────────────────────────────┘
```

### 7.5 Analytics Dashboard

**Charts and Visualizations:**

1. **Category Distribution**
   - Pie chart with percentages
   - Bar chart for comparison
   - Interactive filtering

2. **Follower Distribution by Category**
   - Box plot showing follower ranges
   - Identify "high-reach" categories

3. **Verification Rate by Category**
   - Bar chart comparing verification %
   - Insights on "authority" categories

4. **Network Growth Over Time** (if multiple scans)
   - Line chart showing category growth
   - New follows by category

5. **Engagement Heatmap**
   - Activity patterns
   - Best times/days for each category

### 7.6 Settings & Management

**Scan Management:**
- Trigger new scan
- View scan history
- Schedule automatic scans
- Configure scan parameters

**API Configuration:**
- X API credentials
- Grok API settings
- Rate limiting preferences

**Data Management:**
- Export all data (JSON/CSV)
- Clear cache
- Delete old scans
- Import previous data

**Customization:**
- Theme (light/dark mode)
- Chart preferences
- Default filters
- Privacy settings

### 7.7 Real-time Scan Progress

**During Scan:**
```
┌────────────────────────────────────────────────────────────┐
│  Scanning Your X Network...                               │
│                                                            │
│  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░░░  60%                            │
│                                                            │
│  ✓ Fetched 847 accounts                                  │
│  ⟳ Discovering categories... (analyzing 200 samples)     │
│  ⏸ Categorizing accounts (507/847)                        │
│                                                            │
│  Estimated time remaining: 2 minutes                      │
└────────────────────────────────────────────────────────────┘
```

**WebSocket Updates:**
- Real-time progress bar
- Live status messages
- ETA calculation
- Pause/resume capability

### 7.8 Mobile Responsiveness

- Fully responsive design
- Mobile-optimized layouts
- Touch-friendly interactions
- Progressive Web App (PWA) support

### 7.9 Technology Choices

**Option 1: React + FastAPI (Recommended for Production)**

**Pros:**
- Full control over UI/UX
- Best performance
- Highly customizable
- Professional appearance
- Can deploy to any hosting

**Cons:**
- More development time
- Separate frontend/backend
- Requires TypeScript/React knowledge

**Timeline:** 2-3 weeks for full dashboard

---

**Option 2: Streamlit (Recommended for MVP)**

**Pros:**
- Python-only (no JavaScript needed)
- Rapid development (2-3 days)
- Built-in components
- Easy deployment
- Perfect for prototyping

**Cons:**
- Less customizable
- Limited styling options
- Not as polished
- Can feel "tool-like" vs "product-like"

**Timeline:** 2-3 days for functional dashboard

---

**Recommendation:**
- **Start with Streamlit** for quick MVP and validation
- **Migrate to React** once proven valuable and need more features

### 7.10 API Endpoints (Backend)

**GET /api/stats**
- Returns summary statistics

**GET /api/categories**
- List all discovered categories with metadata

**GET /api/categories/{name}/accounts**
- Get all accounts in specific category

**GET /api/accounts**
- List all accounts with filtering/sorting

**GET /api/accounts/{username}**
- Get specific account details

**POST /api/scan**
- Trigger new scan
- Returns scan job ID

**GET /api/scan/{job_id}/status**
- Get scan progress via REST

**WebSocket /ws/scan/{job_id}**
- Real-time scan updates

**GET /api/export**
- Export data (JSON/CSV)

---

## 8. Implementation Plan

### Phase 1: Foundation & Setup (Week 1)

**Tasks:**
1. ✅ Project initialization and repository setup
2. Set up Python virtual environment
3. Install dependencies
4. Configure X API credentials
5. Configure Grok API credentials
6. Create project structure
7. Set up database schema

**Deliverables:**
- Working development environment
- Configuration files
- Basic project structure

### Phase 2: X API Integration (Week 1-2)

**Tasks:**
1. Implement X API authentication
2. Create client for `/2/users/:id/following` endpoint
3. Implement pagination handling
4. Add rate limiting and error handling
5. Create data models for user profiles
6. Implement data persistence (SQLite)
7. Test with sample data

**Deliverables:**
- Working X API client
- Ability to fetch all following accounts
- Data stored in local database

### Phase 3: Grok API Integration (Week 2)

**Tasks:**
1. Set up xAI SDK
2. Create Grok API client
3. Design categorization prompts
4. Implement batch categorization
5. Add caching to avoid re-analyzing accounts
6. Handle API errors and retries
7. Test categorization accuracy

**Deliverables:**
- Working Grok integration
- Accurate account categorization
- Confidence scoring

### Phase 4: FastAPI Backend (Week 2-3)

**Tasks:**
1. Set up FastAPI project structure
2. Implement REST API endpoints (see section 7.10)
3. Create background task queue for scanning
4. Add WebSocket support for real-time updates
5. Implement data serialization and caching
6. Add CORS for frontend communication
7. Test API endpoints

**Deliverables:**
- Working REST API
- Real-time WebSocket updates
- Background task processing
- API documentation (Swagger)

### Phase 5: Web Dashboard MVP (Week 3 - Streamlit)

**Tasks:**
1. Set up Streamlit application
2. Create overview dashboard page
3. Implement categories view with charts
4. Build accounts browser with filtering
5. Add scan trigger and progress display
6. Implement export functionality
7. Deploy locally and test

**Deliverables:**
- Functional web UI (Streamlit)
- All core features working
- Export capabilities
- Local deployment ready

**Alternative: React Dashboard (3-4 weeks)**
1. Set up React + TypeScript + Vite
2. Design component architecture
3. Implement routing (React Router)
4. Build dashboard pages (Overview, Categories, Accounts, Analytics)
5. Integrate charts (Recharts/Chart.js)
6. Connect to FastAPI backend
7. Add state management (TanStack Query)
8. Implement WebSocket for real-time updates
9. Mobile responsive styling
10. Production build and deployment

### Phase 6: Polish & Optimization (Week 4)

**Tasks:**
1. Add progress bars and loading states
2. Implement incremental updates (only new follows)
3. Add error handling and user feedback
4. Write comprehensive documentation
5. Optimize API performance (caching, indexing)
6. Add configuration UI in dashboard
7. Create example usage scenarios and screenshots

**Deliverables:**
- Production-ready application
- User documentation
- Deployment guide
- Example configurations

### Phase 7: Advanced Features (Optional - Week 5+)

**Tasks:**
1. Scheduled automatic scans (cron jobs)
2. Historical trend analysis across multiple scans
3. Account recommendation engine
4. Multi-user support with authentication
5. Cloud deployment (Vercel/Railway/Fly.io)
6. Custom category creation
7. Account notes and tagging
8. Email/Slack notifications for changes

---

## 9. Project Structure

```
x-cleaner/
├── backend/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py               # Configuration management
│   ├── models.py               # Pydantic data models
│   ├── database.py             # SQLite database manager
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py           # FastAPI route definitions
│   │   ├── websockets.py       # WebSocket handlers
│   │   ├── x_client.py         # X API client
│   │   └── grok_client.py      # Grok API client
│   ├── core/
│   │   ├── __init__.py
│   │   ├── scanner.py          # Scanning logic
│   │   ├── categorizer.py      # Categorization engine
│   │   └── statistics.py       # Statistical analysis
│   ├── tasks/
│   │   ├── __init__.py
│   │   └── background.py       # Background task queue
│   └── cli/
│       ├── __init__.py
│       └── commands.py         # CLI commands (Typer)
│
├── frontend/                   # React dashboard (optional)
│   ├── src/
│   │   ├── components/
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Categories.tsx
│   │   │   ├── AccountBrowser.tsx
│   │   │   └── Analytics.tsx
│   │   ├── api/
│   │   │   └── client.ts       # API client
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts
│
├── streamlit_app/              # Streamlit dashboard (MVP)
│   ├── app.py                  # Main Streamlit app
│   ├── pages/
│   │   ├── 1_Categories.py
│   │   ├── 2_Accounts.py
│   │   └── 3_Analytics.py
│   └── components/
│       ├── charts.py
│       └── filters.py
│
├── tests/
│   ├── __init__.py
│   ├── test_x_client.py
│   ├── test_grok_client.py
│   ├── test_categorizer.py
│   └── test_api.py
│
├── data/                       # Local data storage
│   └── accounts.db             # SQLite database
│
├── docs/                       # Documentation
│   ├── API.md                  # API documentation
│   ├── DEPLOYMENT.md           # Deployment guide
│   └── ARCHITECTURE.md         # Architecture details
│
├── .env.example                # Example environment variables
├── .gitignore
├── README.md
├── requirements.txt            # Python dependencies
├── package.json                # Node dependencies (if React)
├── pyproject.toml              # Poetry/pip configuration
├── docker-compose.yml          # Docker setup (optional)
└── PROJECT_PLAN.md             # This file
```

---

## 9. Configuration

### 9.1 Environment Variables

```bash
# X API Credentials
X_API_BEARER_TOKEN=your_bearer_token_here
X_USER_ID=your_user_id_here

# Grok API Credentials
XAI_API_KEY=your_xai_api_key_here

# Application Settings
DATABASE_PATH=data/accounts.db
BATCH_SIZE=100
RATE_LIMIT_DELAY=1.0
CACHE_EXPIRY_DAYS=7

# Reporting
DEFAULT_EXPORT_FORMAT=json
REPORT_OUTPUT_DIR=reports/
```

### 9.2 CLI Commands

```bash
# Scan and categorize following accounts
x-cleaner scan

# Scan with specific user ID
x-cleaner scan --user-id 12345678

# Generate report from cached data
x-cleaner report

# Export to specific format
x-cleaner export --format json
x-cleaner export --format csv
x-cleaner export --format html

# Update only new follows since last scan
x-cleaner update

# Show statistics
x-cleaner stats

# Clear cache
x-cleaner clear-cache

# Interactive mode
x-cleaner interactive
```

---

## 10. API Cost Estimation

### 10.1 X API Costs

**Basic Plan**: $200/month
- Sufficient for personal use
- 10K posts/month limit
- All follow endpoints included

### 10.2 Grok API Costs

**Example for 1000 Accounts:**
- Input: ~$0.04
- Output: ~$0.01
- **Total**: ~$0.05

**Monthly Cost (1 scan/week, 1000 accounts):**
- ~$0.20/month (negligible)

### 10.3 Total Cost

**Minimum**: $200/month (X API Basic Plan)
**Additional**: ~$0.20/month (Grok API)
**Total**: ~$200-$201/month

---

## 11. Security & Privacy Considerations

### 11.1 Data Protection

- Store API keys in environment variables (never commit)
- Use `.env` file for local development
- Encrypt sensitive data in database
- Don't store unnecessary personal data

### 11.2 Rate Limiting

- Respect X API rate limits
- Implement exponential backoff
- Cache results to minimize API calls
- Use batch requests where possible

### 11.3 Privacy

- Only access public account information
- Don't scrape or store DMs or private data
- Comply with X API Terms of Service
- Allow users to delete their data

---

## 12. Success Metrics

### 12.1 Performance Metrics

- **Speed**: Scan 1000 accounts in <5 minutes
- **Accuracy**: >90% categorization accuracy
- **Reliability**: <1% API error rate
- **Cost**: <$0.001 per account analyzed

### 12.2 User Experience Metrics

- **CLI Response**: Commands execute in <2 seconds
- **Report Generation**: <10 seconds for any size
- **Ease of Use**: Single command to get full analysis
- **Documentation**: Clear setup in <5 minutes

---

## 13. Future Enhancements

### 13.1 Short-term (3-6 months)

1. **Content Analysis**: Analyze tweet sentiment and topics
2. **Engagement Metrics**: Track likes, retweets, replies
3. **Follow/Unfollow Tracking**: Monitor changes over time
4. **Account Recommendations**: Suggest similar accounts to follow
5. **Custom Categories**: Allow user-defined categories

### 13.2 Long-term (6-12 months)

1. **Web Dashboard**: Full-featured web interface
2. **Multi-Account Support**: Manage multiple X accounts
3. **Team Collaboration**: Share reports with team
4. **Advanced Analytics**: ML-powered insights
5. **Integration with other platforms**: LinkedIn, Instagram, etc.
6. **API for third-party integrations**
7. **Scheduled Reports**: Automated weekly/monthly reports

---

## 14. Risk Management

### 14.1 Technical Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| X API changes | High | Medium | Use official SDK, version pinning |
| Rate limiting | Medium | High | Implement robust rate limit handling |
| Grok API downtime | Medium | Low | Implement fallback categorization |
| Data corruption | High | Low | Regular backups, data validation |

### 14.2 Business Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| API cost increases | High | Medium | Monitor usage, optimize calls |
| API access revoked | High | Low | Follow ToS strictly |
| Categorization inaccuracy | Medium | Low | Manual review option, confidence scores |

---

## 15. Timeline Summary

**MVP with Streamlit Dashboard**: 3-4 weeks

- **Week 1**: Setup + X API Integration
  - Project structure, X API client, database setup
- **Week 2**: Grok Integration + Backend
  - AI categorization, FastAPI backend, REST API
- **Week 3**: Web Dashboard (Streamlit)
  - UI pages, charts, real-time updates, export
- **Week 4**: Polish + Documentation
  - Error handling, optimization, docs, deployment

**Full React Dashboard**: 5-6 weeks
- Weeks 1-2: Same as MVP
- Weeks 3-4: React frontend development
- Week 5: Integration and styling
- Week 6: Polish and deployment

**Quick CLI-Only Version**: 1-2 weeks
- Basic scan and categorization
- Simple console output
- JSON/CSV export
- No web UI

---

## 16. Getting Started Checklist

### Prerequisites
- [ ] Python 3.11+ installed
- [ ] X API Basic Plan subscription ($200/month)
- [ ] X API Bearer Token obtained
- [ ] xAI API account created
- [ ] xAI API key obtained
- [ ] Git repository initialized

### Initial Setup
- [ ] Clone repository
- [ ] Create virtual environment
- [ ] Install dependencies
- [ ] Configure `.env` file with API credentials
- [ ] Run initial database migration
- [ ] Test X API connection
- [ ] Test Grok API connection

### First Run
- [ ] Start FastAPI backend: `uvicorn backend.main:app --reload`
- [ ] Start Streamlit dashboard: `streamlit run streamlit_app/app.py`
- [ ] Open dashboard in browser (usually http://localhost:8501)
- [ ] Trigger scan from web UI
- [ ] Verify accounts are fetched and categorized
- [ ] Explore categories and statistics
- [ ] Export data if needed

---

## 17. References & Resources

### Documentation
- [X API v2 Docs](https://developer.x.com/en/docs/twitter-api)
- [xAI API Docs](https://docs.x.ai/)
- [Grok API Guide](https://latenode.com/blog/complete-guide-to-xais-grok-api-documentation-and-implementation)

### Tools & Libraries
- [httpx](https://www.python-httpx.org/) - Async HTTP client
- [Typer](https://typer.tiangolo.com/) - CLI framework
- [Pandas](https://pandas.pydata.org/) - Data analysis
- [Plotly](https://plotly.com/python/) - Data visualization

### Community
- [X Developers Forum](https://devcommunity.x.com/)
- [xAI Community](https://x.ai/)

---

## Conclusion

This project plan provides a comprehensive roadmap for building a sophisticated X account scanner and categorization tool. By leveraging the X API v2 for data collection and Grok API for intelligent analysis, we can create a powerful tool that provides valuable insights into a user's X following network.

The combination of automated categorization, statistical analysis, and multiple report formats will deliver a professional-grade solution that helps users understand and organize their X network effectively.

**Next Steps**: Review this plan, adjust priorities if needed, and begin Phase 1 implementation.
