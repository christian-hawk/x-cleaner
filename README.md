# X-Cleaner: Account Scanner & Categorization Tool

An intelligent tool to scan, categorize, and analyze X (Twitter) accounts you follow using AI-powered analysis.

## Overview

X-Cleaner helps you understand your X network by automatically categorizing the accounts you follow and providing detailed statistics. Leveraging X API v2 for data collection and xAI's Grok for intelligent categorization, it delivers actionable insights into your social network.

## Features

- 🔍 **Automated Scanning**: Fetch all accounts you follow via X API v2
- 🤖 **AI-Powered Categorization**: Use Grok to intelligently categorize accounts
- 📊 **Statistical Analysis**: Get detailed insights with category distribution and metrics
- 🏆 **Top Accounts**: View top 5 accounts from each category
- 📄 **Multiple Export Formats**: JSON, CSV, and HTML reports
- 💾 **Local Caching**: Avoid redundant API calls with SQLite storage
- ⚡ **Fast & Efficient**: Batch processing and async operations

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

The tool categorizes accounts into 17 main categories:

- Technology & Development
- Business & Finance
- News & Media
- Entertainment & Pop Culture
- Science & Research
- Sports & Fitness
- Art & Design
- Marketing & Branding
- Education & Learning
- Politics & Government
- Health & Wellness
- Gaming & Esports
- Fashion & Lifestyle
- Food & Cooking
- Travel & Adventure
- Personal/Friends
- Other

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
   x-cleaner init
   ```

## Configuration

Create a `.env` file with your credentials:

```bash
# X API Credentials
X_API_BEARER_TOKEN=your_bearer_token_here
X_USER_ID=your_user_id_here

# Grok API Credentials
XAI_API_KEY=your_xai_api_key_here

# Optional Settings
DATABASE_PATH=data/accounts.db
BATCH_SIZE=100
CACHE_EXPIRY_DAYS=7
```

## Usage

### Basic Commands

**Scan and categorize your following accounts:**
```bash
x-cleaner scan
```

**Generate report from cached data:**
```bash
x-cleaner report
```

**Export to different formats:**
```bash
x-cleaner export --format json
x-cleaner export --format csv
x-cleaner export --format html
```

**Update only new follows:**
```bash
x-cleaner update
```

**Show statistics:**
```bash
x-cleaner stats
```

**Clear cache:**
```bash
x-cleaner clear-cache
```

### Advanced Usage

**Scan specific user:**
```bash
x-cleaner scan --user-id 12345678
```

**Interactive mode:**
```bash
x-cleaner interactive
```

**Custom categories:**
```bash
x-cleaner scan --categories-file custom_categories.json
```

## Project Structure

```
x-cleaner/
├── src/
│   ├── main.py              # CLI entry point
│   ├── api/                 # API clients
│   │   ├── x_client.py      # X API integration
│   │   └── grok_client.py   # Grok API integration
│   ├── analysis/            # Analysis logic
│   │   ├── categorizer.py   # Categorization
│   │   └── statistics.py    # Statistical analysis
│   └── reporting/           # Report generation
├── data/                    # Local database
├── templates/               # HTML templates
├── tests/                   # Unit tests
└── PROJECT_PLAN.md          # Detailed project plan
```

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

See [PROJECT_PLAN.md](PROJECT_PLAN.md) for detailed implementation plan.

### Phase 1: Foundation ✅
- [x] Project setup
- [x] API research
- [x] Architecture design

### Phase 2: X API Integration
- [ ] Implement X API client
- [ ] Add pagination and rate limiting
- [ ] Create data models

### Phase 3: Grok Integration
- [ ] Set up xAI SDK
- [ ] Implement categorization
- [ ] Add confidence scoring

### Phase 4: Analysis & Reporting
- [ ] Statistical calculations
- [ ] CLI interface
- [ ] Export functionality

### Phase 5: Polish
- [ ] Documentation
- [ ] Error handling
- [ ] Performance optimization

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

- 📖 [Full Documentation](PROJECT_PLAN.md)
- 🐛 [Report Issues](https://github.com/yourusername/x-cleaner/issues)
- 💬 [Discussions](https://github.com/yourusername/x-cleaner/discussions)

## Acknowledgments

- [X API v2](https://developer.x.com) for data access
- [xAI Grok](https://x.ai) for AI-powered categorization
- Built with Python, httpx, and lots of ☕

---

**Made with ❤️ for the X community**
