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
6. **Bulk Account Management**: Unfollow entire categories or select multiple accounts with persistent selection across pagination
7. **Export Functionality**: Save results in multiple formats (JSON, CSV, PDF report)

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

### 7.6 Bulk Account Management

The bulk account management feature allows users to efficiently clean up their X following list by unfollowing entire categories or selecting specific accounts in bulk.

#### 7.6.1 Unfollow Entire Category

**Category Actions Menu:**
```
┌─────────────────────────────────────────────────────────────┐
│  AI/ML Researchers & Practitioners          [87 accounts]  │
│  ━━━━━━━━━━━━━━━━━━━━ 10.3%                               │
│                                                             │
│  🏆 Top Accounts:                                          │
│  1. @researcher1 (2.3M) • AI Research Lead                │
│  2. @mlexpert (1.8M) • ML Engineer                        │
│  3. @aiethics (950K) • AI Safety Researcher               │
│                                                             │
│  [View all] [Bulk Select] [⚠️ Unfollow All]                │
└─────────────────────────────────────────────────────────────┘
```

**Unfollow All Confirmation Dialog:**
```
┌─────────────────────────────────────────────────────────────┐
│  ⚠️  Unfollow Entire Category?                             │
│                                                             │
│  You are about to unfollow all 87 accounts in:            │
│  "AI/ML Researchers & Practitioners"                       │
│                                                             │
│  This action will:                                         │
│  • Unfollow 87 accounts on X                              │
│  • Take approximately 2-3 minutes (rate limiting)          │
│  • Remove these accounts from your X following list        │
│                                                             │
│  ⚠️  This action cannot be easily undone.                  │
│                                                             │
│  [ ] I understand and want to proceed                      │
│                                                             │
│  [Cancel]                [⚠️ Unfollow All 87 Accounts]     │
└─────────────────────────────────────────────────────────────┘
```

**Progress Tracking:**
```
┌─────────────────────────────────────────────────────────────┐
│  Unfollowing Accounts...                                   │
│                                                             │
│  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░  70% (61/87 unfollowed)            │
│                                                             │
│  ✓ Successfully unfollowed: 61 accounts                   │
│  ⏳ In progress: @current_account                          │
│  ⚠️  Skipped (errors): 0 accounts                          │
│                                                             │
│  Rate limit: 48 requests remaining (resets in 12 min)     │
│  Estimated time: 45 seconds                                │
│                                                             │
│  [Pause] [Cancel]                                         │
└─────────────────────────────────────────────────────────────┘
```

#### 7.6.2 Bulk Selection with Pagination Persistence

**Category Detail View with Selection:**
```
┌─────────────────────────────────────────────────────────────┐
│  AI/ML Researchers & Practitioners - 87 accounts           │
│                                                             │
│  [✓ Select All on Page] [Clear Selection]                 │
│  Selected: 23 accounts across all pages                    │
│                                                             │
│  Search: [___________] 🔍  Sort: [Followers ▼]            │
├─────────────────────────────────────────────────────────────┤
│  [✓] @researcher1         2.3M followers  ✓               │
│      AI Research Lead • Posts about ML...                  │
│      Last active: 2 hours ago                              │
├─────────────────────────────────────────────────────────────┤
│  [ ] @mlexpert           1.8M followers  ✓                │
│      ML Engineer • Building AI systems...                  │
│      Last active: 1 day ago                                │
├─────────────────────────────────────────────────────────────┤
│  [✓] @aiethics           950K followers                    │
│      AI Safety Researcher • Ethical AI...                  │
│      Last active: 3 hours ago                              │
├─────────────────────────────────────────────────────────────┤
│  [✓] @deeplearning       720K followers  ✓                │
│      Deep Learning Expert • Teaching...                    │
│      Last active: 5 hours ago                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Showing 1-20 of 87    [< Previous]  [Next >]  [3/5]      │
│                                                             │
│  [Unfollow Selected (23)] [Export Selection] [Clear]      │
└─────────────────────────────────────────────────────────────┘
```

**Selection Features:**
- ✅ **Persistent Selection**: Selected accounts remain selected when navigating between pages
- ✅ **Visual Counter**: Shows total selected accounts across all pages
- ✅ **Select All on Page**: Quick select all accounts on current page
- ✅ **Clear Selection**: Reset all selections
- ✅ **Selection Preview**: Shows selected count before action
- ✅ **Multi-page Selection**: Can select accounts from page 1, go to page 3, select more, etc.

**Bulk Unfollow Confirmation:**
```
┌─────────────────────────────────────────────────────────────┐
│  ⚠️  Unfollow Selected Accounts?                           │
│                                                             │
│  You have selected 23 accounts to unfollow:               │
│                                                             │
│  From "AI/ML Researchers & Practitioners":                 │
│  • @researcher1                                            │
│  • @aiethics                                               │
│  • @deeplearning                                           │
│  • ... and 20 more                                         │
│                                                             │
│  [View Full List]                                          │
│                                                             │
│  This will unfollow 23 accounts on X.                     │
│  Estimated time: ~1 minute                                 │
│                                                             │
│  [ ] I understand this action cannot be easily undone      │
│                                                             │
│  [Cancel]              [⚠️ Unfollow 23 Accounts]           │
└─────────────────────────────────────────────────────────────┘
```

#### 7.6.3 Unfollow Results & Rollback

**Results Summary:**
```
┌─────────────────────────────────────────────────────────────┐
│  ✓ Unfollow Operation Complete                            │
│                                                             │
│  Results:                                                  │
│  ✓ Successfully unfollowed: 22 accounts                   │
│  ⚠️  Failed (rate limit): 1 account                        │
│                                                             │
│  Failed accounts:                                          │
│  • @researcher1 - Rate limit exceeded                      │
│    [Retry Later]                                           │
│                                                             │
│  Your X following list has been updated.                  │
│  Next scan will reflect these changes.                     │
│                                                             │
│  [View Updated Category] [Scan Again] [Close]             │
└─────────────────────────────────────────────────────────────┘
```

**Error Handling:**
- Rate limit detection with retry suggestions
- Failed account tracking
- Partial success handling
- Detailed error messages

#### 7.6.4 Undo/Refollow Feature (Optional)

**Undo Buffer:**
```
┌─────────────────────────────────────────────────────────────┐
│  Recent Unfollow Actions                                   │
│                                                             │
│  📝 5 minutes ago: Unfollowed 23 accounts                  │
│     from "AI/ML Researchers"                               │
│     [View List] [⟲ Refollow All]                          │
│                                                             │
│  📝 2 hours ago: Unfollowed entire category (87 accounts)  │
│     "Crypto Influencers"                                   │
│     [View List] [⟲ Refollow All]                          │
│                                                             │
│  Note: Undo is available for 24 hours after unfollow      │
└─────────────────────────────────────────────────────────────┘
```

### 7.7 Settings & Management

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

### 7.8 Real-time Scan Progress

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

### 7.9 Mobile Responsiveness

- Fully responsive design
- Mobile-optimized layouts
- Touch-friendly interactions
- Progressive Web App (PWA) support

### 7.10 Technology Choices

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

### 7.11 API Endpoints (Backend)

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

**POST /api/unfollow/category/{category_name}**
- Unfollow all accounts in a category
- Returns unfollow job ID for tracking

**POST /api/unfollow/bulk**
- Request body: `{"account_ids": ["123", "456", ...]}`
- Unfollow selected accounts in bulk
- Returns unfollow job ID

**GET /api/unfollow/{job_id}/status**
- Get unfollow operation progress
- Returns: current, total, success_count, failed_accounts

**WebSocket /ws/unfollow/{job_id}**
- Real-time unfollow progress updates

**GET /api/unfollow/history**
- Get recent unfollow operations (for undo feature)

**POST /api/refollow/batch**
- Request body: `{"account_ids": ["123", "456", ...]}`
- Refollow accounts (undo feature)

---

## 8. Implementation Plan

### Phase 1: Foundation & Setup ✅ **COMPLETE**

**Tasks:**
1. ✅ Project initialization and repository setup
2. ✅ Set up Python virtual environment
3. ✅ Install dependencies
4. ✅ Configure X API credentials
5. ✅ Configure Grok API credentials
6. ✅ Create project structure
7. ✅ Set up database schema

**Deliverables:**
- ✅ Working development environment
- ✅ Configuration files (.env.example, pyproject.toml)
- ✅ Basic project structure with 4-layer architecture
- ✅ Documentation framework (ARCHITECTURE.md, CODE_CONVENTIONS.md)

**Completed:** Phase 1 (#3)

---

### Phase 2: X API Integration ⚠️ **PARTIAL - Components Only**

**Tasks:**
1. ✅ Implement X API authentication
2. ✅ Create client for `/2/users/:id/following` endpoint
3. ✅ Implement pagination handling
4. ✅ Add rate limiting and error handling
5. ✅ Create Pydantic data models for user profiles
6. ✅ Implement data persistence (SQLite)
7. ✅ Test with sample data
8. ✅ Repository pattern for data access
9. ❌ **Endpoint/service to EXECUTE scan using the client**

**Deliverables:**
- ✅ Working X API client (backend/api/x_client.py) - tested in isolation
- ⚠️ Ability to fetch all following accounts - client exists but no endpoint uses it
- ✅ Data stored in local database - via sample data script only
- ✅ AccountRepository with comprehensive methods
- ✅ Unit tests with high coverage - components only

**Status:** Components implemented (#4), but not integrated into scan flow

---

### Phase 3: Grok API Integration ⚠️ **PARTIAL - Components Only**

**Tasks:**
1. ✅ Set up xAI SDK
2. ✅ Create Grok API client
3. ✅ Design categorization prompts (2-phase approach)
4. ✅ Implement emergent category discovery
5. ✅ Implement batch categorization
6. ✅ Add confidence scoring
7. ✅ Handle API errors and retries
8. ✅ Test categorization accuracy - in isolation
9. ❌ **Endpoint/service to EXECUTE categorization in scan flow**

**Deliverables:**
- ✅ Working Grok integration (backend/api/grok_client.py) - tested in isolation
- ⚠️ Accurate account categorization - logic exists but no endpoint uses it
- ✅ Confidence scoring
- ✅ CategoryRepository for category management
- ✅ Categorizer service with business logic - service exists but not called

**Status:** Components implemented (#5), but not integrated into scan flow

---

### Phase 4: FastAPI Backend ⚠️ **PARTIAL - Read-Only Endpoints**

**Tasks:**
1. ✅ Set up FastAPI project structure
2. ✅ Implement REST API endpoints (accounts, categories, statistics) - READ ONLY
3. ✅ Create Pydantic schemas for request/response
4. ✅ Implement dependency injection
5. ✅ Add service layer (AccountService, StatisticsService)
6. ✅ Implement 4-layer architecture
7. ✅ Add CORS for frontend communication
8. ✅ Test API endpoints - GET endpoints only
9. ❌ **POST /api/scan endpoint**
10. ❌ **WebSocket /ws/scan for progress**
11. ❌ **Background task queue**

**Deliverables:**
- ✅ Working REST API (backend/main.py) - for reading existing data only
- ✅ Clean architecture with dependency injection
- ⚠️ API endpoints - GET only, no scan trigger
- ✅ API documentation (Swagger at /docs)
- ⚠️ Unit tests (94% coverage) - components only, no integration test

**Status:** Read-only API implemented (#6), scan endpoints missing

---

### Phase 5: Web Dashboard ⚠️ **PARTIAL - Visualization Only**

**Tasks:**
1. ✅ Set up Streamlit application
2. ✅ Create overview dashboard page
3. ✅ Implement categories explorer with charts
4. ✅ Build accounts browser with filtering
5. ✅ Add advanced analytics page
6. ✅ Add settings & management page
7. ✅ Implement export functionality (JSON/CSV)
8. ✅ Create sample data generator
9. ✅ Deploy locally and test - with sample data only
10. ✅ Write deployment documentation
11. ❌ **Scan trigger button/UI**
12. ❌ **Real-time scan progress display**

**Deliverables:**
- ✅ Functional web UI (Streamlit with 5 pages) - visualization only
- ⚠️ "Core features" - can only VIEW data, not SCAN
- ✅ Interactive Plotly charts
- ✅ Export capabilities
- ✅ Local deployment ready
- ✅ Sample data for testing (scripts/populate_sample_data.py)
- ✅ Deployment guide (docs/PHASE5_DEPLOYMENT.md)
- ✅ Quick start guide (QUICKSTART.md)

**Status:** Dashboard implemented (#7), but cannot trigger scans

---

### Phase 5.5: Core Scan Functionality 🚧 **NEXT - CRITICAL**

**Status:** Not started - this is the CORE functionality gap

**Tasks:**
1. Create ScanService to orchestrate: X API fetch → Grok categorize → DB save
2. Add POST /api/scan endpoint to FastAPI
3. Implement background task processing (FastAPI BackgroundTasks)
4. Add WebSocket /ws/scan/{job_id} for real-time progress
5. Create scan progress tracking (job status, current step, ETA)
6. Add "Start Scan" button to Streamlit dashboard
7. Add real-time progress UI in Streamlit (via WebSocket client)
8. End-to-end integration test
9. Error handling and retry logic

**Deliverables:**
- Working scan orchestration service
- POST /api/scan endpoint
- WebSocket for progress updates
- Scan UI in dashboard
- Full integration test (fetch → categorize → save → display)

**This is what makes the app FUNCTIONAL instead of just a demo viewer**

---

### Phase 6: Quality & Testing ⚠️ **PARTIAL**

**Tasks:**
1. ✅ GitHub Actions for CI/CD (mypy, pylint)
2. ✅ Unit tests for repositories (100% coverage)
3. ✅ Unit tests for services (85%+ coverage)
4. ✅ Code quality standards enforcement
5. ✅ Error handling improvements
6. ✅ Type safety with mypy strict mode
7. ❌ **Integration test for scan flow**

**Deliverables:**
- ✅ CI/CD pipeline (.github/workflows/linting.yml)
- ✅ Comprehensive test suite (tests/) - components only
- ⚠️ 94% overall test coverage - of components, not full flow
- ✅ Type-safe codebase (mypy passing)
- ✅ Clean code (pylint passing)

**Status:** Components tested, integration missing

---

**Alternative: React Dashboard (POSTPONED - not priority)**
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

### Phase 7: Bulk Account Management 📋 **PLANNED**

**Status:** Design complete, implementation pending

Documentation available in:
- PROJECT_PLAN.md (Section 7.6)
- IMPLEMENTATION_ROADMAP.md (Phase 7)

**Tasks:**
1. Implement X API unfollow endpoint client
2. Add rate limiting for unfollow operations (respect X API limits)
3. Create backend unfollow service with batch processing
4. Implement unfollow job queue and progress tracking
5. Add WebSocket support for real-time unfollow progress
6. Create unfollow history tracking for undo feature
7. Build UI for "Unfollow All Category" with confirmation dialog
8. Implement bulk selection UI with pagination persistence
9. Add session state management for multi-page selection
10. Create unfollow progress modal with rate limit display
11. Implement error handling and retry logic
12. Add unfollow results summary with failed accounts list
13. Build optional undo/refollow feature with 24h buffer
14. Test bulk unfollow with various category sizes

**Key Considerations:**
- **X API Rate Limits**:
  - Unfollow endpoint: ~50 requests per 15 minutes
  - Must implement careful rate limiting and queuing
  - Show accurate ETA based on rate limits
- **State Persistence**:
  - Use session state (Streamlit) or Redux (React) for selection
  - Persist selection across pagination
  - Clear selection after successful unfollow
- **User Safety**:
  - Require explicit confirmation with checkbox
  - Show detailed preview before action
  - Provide undo buffer for accidental unfollows
  - Log all unfollow operations for audit trail

**Deliverables:**
- Fully functional unfollow entire category feature
- Bulk selection with pagination persistence
- Real-time progress tracking with rate limit display
- Error handling and retry mechanism
- Optional undo/refollow feature
- Comprehensive testing with different scenarios

### Phase 8: Advanced Features 🔮 **FUTURE**

**Status:** Not yet started (optional enhancements)

**Potential Tasks:**
1. Scheduled automatic scans (cron jobs)
2. Historical trend analysis across multiple scans
3. Account recommendation engine
4. Multi-user support with authentication
5. Cloud deployment (Vercel/Railway/Fly.io)
6. Custom category creation
7. Account notes and tagging
8. Email/Slack notifications

**Note:** These are optional enhancements that can be implemented based on user feedback and requirements. for changes

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
