# X-Cleaner: Account Scanner & Categorization Tool
Project created to prove that, even trying hard, vibe coding with Claude will always sucks.

An intelligent tool to scan, categorize, and analyze X (Twitter) accounts you follow using AI-powered analysis.

## Overview

X-Cleaner helps you understand your X network by automatically categorizing the accounts you follow and providing detailed statistics through an interactive web dashboard. Leveraging X API v2 for data collection and xAI's Grok for intelligent categorization, it delivers actionable insights into your social network.

## Features

- 🌐 **Interactive Web Dashboard**: Beautiful, responsive UI for exploring your network
- 🔍 **Automated Scanning**: Fetch all accounts you follow via X API v2
- 🤖 **AI-Powered Categorization**: Grok discovers natural categories from your network
- 📊 **Visual Analytics**: Charts, graphs, and statistics at a glance
- 🏆 **Top Accounts**: View top 5 accounts from each category
- 🧹 **Bulk Account Management**: Unfollow entire categories or select accounts in bulk with pagination persistence
- 🔄 **Real-time Updates**: Watch scans and unfollow operations progress in real-time via WebSocket
- ↩️ **Undo Operations**: 24-hour buffer to refollow accidentally unfollowed accounts
- 📄 **Multiple Export Formats**: JSON, CSV, and PDF reports
- 💾 **Local Caching**: Avoid redundant API calls with SQLite storage
- ⚡ **Fast & Efficient**: Async operations and background task processing

## 🚀 Project Status

**Current Version**: v0.5-alpha (Components Ready, Core Functionality Pending)

**✅ Implemented Components:**
- X API v2 client with pagination and rate limiting
- Grok AI client with emergent categorization logic
- Database layer with repositories (SQLite + SQLAlchemy)
- Service layer (AccountService, StatisticsService, CategorizationService)
- FastAPI backend with REST API endpoints (READ-only, for existing data)
- Streamlit web dashboard with 5 interactive pages (visualization only)
- Sample data generator for testing/demo (900+ fake accounts)
- Advanced analytics and visualizations (Plotly charts)
- Data export (JSON/CSV)
- Comprehensive test suite (94% coverage of components)
- CI/CD with GitHub Actions (mypy, pylint)

**❌ NOT Implemented (CORE FUNCTIONALITY):**
- **Scan endpoint/command** to fetch real accounts from X API → categorize with Grok → save to DB
- Web UI to trigger scans
- Real-time scan progress tracking via WebSocket
- Background task processing for scans

**📊 What Works Today:**
- Generate sample data: `python scripts/populate_sample_data.py`
- View dashboard: `streamlit run streamlit_app/app.py`
- Explore 900+ fake accounts across 15 categories

**🔜 Next Steps (In Order):**
1. **Implement scan functionality** - endpoint/service to execute: fetch → categorize → save
2. **Add web UI to trigger scans** - button in Streamlit dashboard + progress display
3. **WebSocket for real-time progress** - watch scan happen live
4. Phase 7: Bulk account management (unfollow operations)
5. Phase 8: Advanced features (authentication, cloud deployment)

**⚠️ Current Limitation:**
The project has all the building blocks but cannot yet scan real X accounts. You can only visualize sample/fake data.

## Quick Statistics Example

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
  1. @username1 (2.3M followers)
  2. @username2 (1.8M followers)
  [...]
```

## Categories

**Emergent, AI-Driven Categorization**

Unlike traditional tools that force accounts into predefined categories, X-Cleaner uses Grok AI to **discover natural categories** from your specific network.

**How it works:**
1. **Discovery Phase**: Grok analyzes all your followed accounts and identifies natural groupings (typically 10-20 categories)
2. **Categorization Phase**: Each account is assigned to the most appropriate discovered category
3. **Results**: You get categories that actually reflect YOUR network's composition

**Example discovered categories might include:**
- "AI/ML Researchers & Practitioners"
- "Indie Makers & Bootstrapped Founders"
- "Crypto/Web3 Builders"
- "Technical Writers & Educators"
- "DevRel & Developer Advocates"
- "VC Investors & Startup Advisors"
- "Design Systems & UI/UX Experts"
- "Security Researchers & Ethical Hackers"

**Benefits:**
- ✅ More accurate than predefined categories
- ✅ Reflects YOUR specific network
- ✅ Discovers niche communities
- ✅ Adapts to emerging trends
- ✅ No manual category selection needed

## Prerequisites

### API Access Required

1. **X API Basic Plan** ($200/month)
   - Get API access at [developer.x.com](https://developer.x.com)
   - Need Bearer Token and User ID
   - Endpoint required: `GET /2/users/:id/following`

2. **xAI API Key** (~$0.05 per 1000 accounts)
   - Sign up at [x.ai/api](https://x.ai/api)
   - Get API key from xAI Console
   - Uses Grok-4-1-Fast model

### System Requirements

- Python 3.11 or higher
- Internet connection
- ~100MB disk space for data storage

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/x-cleaner.git
   cd x-cleaner
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your API credentials
   ```

5. **Initialize database**
   ```bash
   python -m backend.database --init
   ```

## Configuration

Create a `.env` file with your credentials:

```bash
# X API Credentials
X_API_BEARER_TOKEN=your_bearer_token_here
X_USER_ID=your_user_id_here

# Grok API Credentials
XAI_API_KEY=your_xai_api_key_here

# Application Settings
DATABASE_PATH=data/accounts.db
BATCH_SIZE=100
CACHE_EXPIRY_DAYS=7

# Web Server (optional)
HOST=0.0.0.0
PORT=8000
```

## Usage

### Running the Web Dashboard

**Start the backend API server:**
```bash
uvicorn backend.main:app --reload --port 8000
```

**Start the Streamlit dashboard (in a new terminal):**
```bash
streamlit run streamlit_app/app.py
```

**Open your browser:**
- Dashboard: http://localhost:8501
- API docs: http://localhost:8000/docs

**From the web interface you can:**
- Trigger scans and watch real-time progress
- Browse discovered categories
- Explore all accounts with search/filter
- View interactive charts and analytics
- Export data in multiple formats

### CLI Commands (Alternative)

**Scan via CLI:**
```bash
python -m backend.cli scan
```

**Export data:**
```bash
python -m backend.cli export --format json
python -m backend.cli export --format csv
```

**View statistics:**
```bash
python -m backend.cli stats
```

## Project Structure

```
x-cleaner/
├── backend/                 # FastAPI backend
│   ├── main.py              # API server entry point
│   ├── api/                 # API clients
│   │   ├── routes.py        # REST endpoints
│   │   ├── websockets.py    # Real-time updates
│   │   ├── x_client.py      # X API integration
│   │   └── grok_client.py   # Grok AI integration
│   ├── core/                # Core logic
│   │   ├── scanner.py       # Scanning engine
│   │   ├── categorizer.py   # AI categorization
│   │   └── statistics.py    # Analytics
│   └── cli/                 # CLI commands
│
├── streamlit_app/           # Web dashboard (Streamlit)
│   ├── app.py               # Main dashboard
│   └── pages/               # Additional pages
│
├── frontend/                # React dashboard (optional)
│   └── src/                 # React components
│
├── data/                    # SQLite database
├── tests/                   # Unit tests
│
├── PROJECT_PLAN.md          # Complete project plan
├── IMPLEMENTATION_ROADMAP.md # Developer guide with code
├── ARCHITECTURE.md          # System architecture & patterns
└── CODE_CONVENTIONS.md      # Code quality standards
```

See the **[Documentation](#documentation)** section below for detailed guides.

## Cost Estimation

### Monthly Costs

| Service | Cost | Notes |
|---------|------|-------|
| X API Basic Plan | $200/month | Required for follow endpoints |
| Grok API | ~$0.20/month | Based on 4 scans/month with 1000 accounts |
| **Total** | **~$200/month** | Grok costs are negligible |

### Per-Scan Costs

- 1000 accounts: ~$0.05 (Grok API only)
- 5000 accounts: ~$0.25
- 10000 accounts: ~$0.50

## Development Roadmap

See **[Documentation](#documentation)** section for complete planning and implementation guides.

### Phase 1: Foundation ✅ COMPLETE
- [x] Project setup and structure
- [x] API research and planning
- [x] Architecture design with web dashboard
- [x] Development environment configuration
- [x] Documentation framework (ARCHITECTURE.md, CODE_CONVENTIONS.md)

### Phase 2: X API Integration ⚠️ PARTIAL (Components Only)
- [x] Implement X API client with async support
- [x] Add pagination and rate limiting
- [x] Create Pydantic data models
- [x] Repository pattern for data access
- [x] Comprehensive unit tests
- [ ] **Scan endpoint/service to actually USE the client**

### Phase 3: Grok Integration ⚠️ PARTIAL (Components Only)
- [x] Set up xAI SDK integration
- [x] Implement emergent categorization (2-phase approach)
- [x] Add confidence scoring
- [x] Category discovery and assignment
- [x] Service layer architecture
- [ ] **Scan endpoint/service to actually USE the categorizer**

### Phase 4: FastAPI Backend ⚠️ PARTIAL (Read-Only)
- [x] REST API endpoints (accounts, categories, statistics) - READ ONLY
- [x] Pydantic schemas for request/response
- [x] Dependency injection
- [x] 4-layer architecture (Presentation/API/Business/Data)
- [x] Comprehensive test coverage (94% of components)
- [ ] **POST /api/scan endpoint to trigger scans**
- [ ] **WebSocket /ws/scan for real-time progress**
- [ ] **Background task processing**

### Phase 5: Web Dashboard (Streamlit) ⚠️ PARTIAL (Visualization Only)
- [x] Overview dashboard page with metrics
- [x] Categories explorer with interactive charts
- [x] Accounts browser with advanced search/filter
- [x] Advanced analytics page
- [x] Settings & management page
- [x] Export functionality (JSON/CSV)
- [x] Sample data generator
- [x] Deployment documentation
- [ ] **Scan trigger UI (button to start scan)**
- [ ] **Real-time scan progress display**

### Phase 5.5: Core Scan Functionality 🚧 **IN PROGRESS - PRIORITY**
- [ ] Implement scan orchestration service
- [ ] Create POST /api/scan endpoint
- [ ] Add background task processing
- [ ] WebSocket for real-time progress
- [ ] Add scan UI to Streamlit dashboard
- [ ] End-to-end integration test

### Phase 6: Quality & Testing ⚠️ PARTIAL
- [x] GitHub Actions for CI/CD (mypy, pylint)
- [x] Unit tests (repositories, services) - 94% coverage of components
- [x] Code quality standards enforcement
- [x] Error handling improvements
- [x] Type safety with mypy
- [ ] **Integration test for full scan flow**

### Phase 7: Bulk Account Management 📋 PLANNED
- [ ] Unfollow entire category feature
- [ ] Bulk selection with pagination persistence
- [ ] Real-time unfollow progress tracking via WebSocket
- [ ] Undo/refollow buffer (24h)
- [ ] Rate limiting for X API unfollow operations

### Phase 8: Advanced Features (Optional) 🔮 FUTURE
- [ ] Scheduled automatic scans
- [ ] Historical trend analysis
- [ ] Multi-user support with authentication
- [ ] Cloud deployment (Railway/Vercel)
- [ ] Email/Slack notifications

## Documentation

Comprehensive planning and technical documentation:

### 📋 Planning & Features
- **[PROJECT_PLAN.md](PROJECT_PLAN.md)** - Complete project plan with 17 sections
  - Feature specifications and UI mockups
  - Emergent AI categorization approach
  - Web dashboard design (FastAPI + Streamlit/React)
  - Implementation phases and timeline
  - Cost analysis and risk mitigation

### 🛠️ Implementation Guide
- **[IMPLEMENTATION_ROADMAP.md](IMPLEMENTATION_ROADMAP.md)** - Developer implementation guide
  - Step-by-step setup instructions
  - Complete code examples (backend, frontend, API clients)
  - Database schema and models
  - Running instructions (development & production)
  - Phase 7: Bulk unfollow implementation with UI code

### 🏗️ Architecture & Patterns
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture and design patterns
  - 4-layer architecture (Presentation/API/Business/Data)
  - Design patterns (Repository, Service, Factory, Strategy, Observer, DI)
  - Component structure and communication rules
  - Error handling and logging strategies
  - Testing strategy (unit/integration/e2e)
  - Type system and API design principles

### 📝 Code Quality Standards
- **[CODE_CONVENTIONS.md](CODE_CONVENTIONS.md)** - Code style and quality guidelines
  - Clean Code principles (DRY, self-documenting code)
  - **Mandatory limits**: Files ≤500 lines, Functions ≤60 lines, Complexity ≤15
  - PEP 8 style guide (imports at top, formatting rules)
  - Naming conventions (EXTREMELY self-explanatory, NO abbreviations)
  - Forbidden patterns and refactoring triggers
  - Code review checklist

## Architecture

```
┌─────────────────────────────────────────────┐
│            CLI Interface                    │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│         Core Application                    │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│  │ X API    │ │ Grok API │ │ Database │   │
│  │ Client   │ │ Client   │ │ Manager  │   │
│  └──────────┘ └──────────┘ └──────────┘   │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│        Processing Pipeline                  │
│  Fetch → Enrich → Categorize → Report      │
└─────────────────────────────────────────────┘
```

## Security & Privacy

- ✅ API keys stored in environment variables
- ✅ No storage of private/sensitive data
- ✅ Only public account information accessed
- ✅ Full compliance with X API Terms of Service
- ✅ Local data storage (no cloud by default)
- ✅ Rate limiting and error handling

## Troubleshooting

### Common Issues

**"Invalid Bearer Token"**
- Verify your X API Bearer Token in `.env`
- Ensure you have Basic Plan or higher access

**"Rate limit exceeded"**
- Wait for rate limit reset (shown in error message)
- Reduce `BATCH_SIZE` in configuration

**"Categorization failed"**
- Check xAI API key is valid
- Verify internet connection
- Check xAI API status

**"Database locked"**
- Close other instances of x-cleaner
- Delete `data/accounts.db.lock` if exists

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

See [LICENSE](LICENSE) file for details.

## Support

- 📖 [Full Documentation](#documentation)
- 🐛 [Report Issues](https://github.com/yourusername/x-cleaner/issues)
- 💬 [Discussions](https://github.com/yourusername/x-cleaner/discussions)

## Acknowledgments

- [X API v2](https://developer.x.com) for data access
- [xAI Grok](https://x.ai) for AI-powered categorization
- Built with Python, httpx, and lots of ☕

---

**Made with ❤️ for the X community**
