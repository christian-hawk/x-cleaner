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
4. **Statistical Dashboard**: Display category distribution, account counts, and top accounts
5. **Export Functionality**: Save results in multiple formats (JSON, CSV, HTML report)

---

## 2. Technical Architecture

### 2.1 Technology Stack

**Backend/Core:**
- **Language**: Python 3.11+
- **HTTP Client**: `httpx` (async support for API calls)
- **Data Processing**: `pandas` for data analysis
- **Storage**: SQLite for local data persistence
- **Configuration**: `python-dotenv` for environment variables

**API Integration:**
- **X API v2**: For fetching following accounts and user data
- **Grok API**: For AI-powered categorization and analysis
- **xAI Python SDK**: Official SDK for Grok integration

**Analysis & Reporting:**
- **Data Visualization**: `plotly` or `matplotlib` for charts
- **Report Generation**: `jinja2` for HTML reports
- **CLI Interface**: `typer` or `click` for command-line interaction

### 2.2 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      CLI Interface                          │
│                    (User Commands)                          │
└─────────────────┬───────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────┐
│                  Core Application                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   X API      │  │   Grok API   │  │   Database   │     │
│  │   Client     │  │   Client     │  │   Manager    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────┬───────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────┐
│              Processing Pipeline                            │
│                                                             │
│  1. Fetch Following → 2. Enrich Data → 3. Categorize →    │
│  4. Analyze → 5. Generate Report                           │
└─────────────────────────────────────────────────────────────┘
```

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

**System Prompt Template:**
```
You are an expert at analyzing X (Twitter) accounts and categorizing them.
Analyze the following account profile and categorize it into ONE primary category.

Categories to choose from:
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

Consider:
- Bio description
- Tweet content patterns
- Follower/following ratio
- Verified status
- Account age and activity level
```

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

### 5.1 Primary Categories

1. **Technology & Development**
   - Software engineers, developers, tech companies
   - Programming languages, frameworks, tools

2. **Business & Finance**
   - Entrepreneurs, investors, business news
   - Startups, venture capital, economics

3. **News & Media**
   - Journalists, news outlets, reporters
   - Breaking news, current events

4. **Entertainment & Pop Culture**
   - Celebrities, actors, musicians
   - Movies, TV shows, music industry

5. **Science & Research**
   - Scientists, researchers, academic institutions
   - Research papers, discoveries, education

6. **Sports & Fitness**
   - Athletes, sports teams, coaches
   - Fitness influencers, sports news

7. **Art & Design**
   - Artists, designers, photographers
   - Creative work, galleries, exhibitions

8. **Marketing & Branding**
   - Marketers, agencies, brand strategists
   - Social media experts, growth hackers

9. **Education & Learning**
   - Educators, teachers, educational content
   - Online courses, learning resources

10. **Politics & Government**
    - Politicians, political analysts, government
    - Policy, elections, political movements

11. **Health & Wellness**
    - Health professionals, fitness experts
    - Nutrition, mental health, wellness

12. **Gaming & Esports**
    - Gamers, streamers, esports teams
    - Game developers, gaming news

13. **Fashion & Lifestyle**
    - Fashion designers, influencers, brands
    - Lifestyle content, trends

14. **Food & Cooking**
    - Chefs, food bloggers, restaurants
    - Recipes, food photography

15. **Travel & Adventure**
    - Travel bloggers, tour guides
    - Destinations, travel tips

16. **Personal/Friends**
    - Personal connections, friends, family
    - Non-public figures with small following

17. **Other**
    - Accounts that don't fit other categories
    - Bots, inactive accounts

### 5.2 Categorization Criteria

**Primary Factors:**
- Bio keywords and hashtags
- Recent tweet content analysis
- Account metrics (followers, engagement)
- Verified status and account type
- Links in bio (website domains)

**Confidence Scoring:**
- High (>80%): Clear category match
- Medium (50-80%): Likely category
- Low (<50%): Uncertain, may need manual review

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

**HTML Report:**
- Interactive dashboard with charts
- Sortable tables
- Category filters
- Export buttons

**CSV Export:**
- One row per account
- All metadata included
- Easy to import into spreadsheets

---

## 7. Implementation Plan

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

### Phase 4: Analysis & Reporting (Week 3)

**Tasks:**
1. Implement statistical calculations
2. Create data visualization charts
3. Design CLI interface with Typer
4. Build HTML report generator
5. Implement JSON/CSV export
6. Add filtering and sorting options
7. Create summary statistics

**Deliverables:**
- Complete reporting system
- Multiple export formats
- Interactive CLI

### Phase 5: Polish & Optimization (Week 3-4)

**Tasks:**
1. Add progress bars for long operations
2. Implement incremental updates (only new follows)
3. Add configuration options
4. Write comprehensive documentation
5. Add error handling and logging
6. Optimize performance
7. Create example usage scenarios

**Deliverables:**
- Production-ready tool
- User documentation
- Example configurations

### Phase 6: Advanced Features (Optional - Week 4+)

**Tasks:**
1. Web dashboard (Flask/FastAPI)
2. Scheduled automatic scans
3. Historical trend analysis
4. Account recommendation engine
5. Multi-user support
6. Cloud deployment option

---

## 8. Project Structure

```
x-cleaner/
├── src/
│   ├── __init__.py
│   ├── main.py                 # CLI entry point
│   ├── config.py               # Configuration management
│   ├── models.py               # Data models (Pydantic)
│   ├── database.py             # SQLite database manager
│   ├── api/
│   │   ├── __init__.py
│   │   ├── x_client.py         # X API client
│   │   └── grok_client.py      # Grok API client
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── categorizer.py      # Categorization logic
│   │   └── statistics.py       # Statistical analysis
│   └── reporting/
│       ├── __init__.py
│       ├── console.py          # Console output
│       ├── html_report.py      # HTML generation
│       └── export.py           # JSON/CSV export
├── tests/
│   ├── __init__.py
│   ├── test_x_client.py
│   ├── test_categorizer.py
│   └── test_statistics.py
├── data/                       # Local data storage
│   └── accounts.db             # SQLite database
├── templates/
│   └── report.html             # HTML report template
├── .env.example                # Example environment variables
├── .gitignore
├── README.md
├── requirements.txt
├── pyproject.toml             # Poetry/pip configuration
└── PROJECT_PLAN.md            # This file
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

**Total Duration**: 3-4 weeks for MVP

- Week 1: Setup + X API Integration
- Week 2: Grok Integration + Basic Analysis
- Week 3: Reporting + CLI
- Week 4: Polish + Documentation

**Quick Start (Minimal)**: 1-2 weeks
- Basic scan and categorization
- Simple console output
- JSON export

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
- [ ] Execute `x-cleaner scan` command
- [ ] Verify accounts are fetched
- [ ] Verify categorization works
- [ ] Generate first report
- [ ] Review accuracy of categories

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
