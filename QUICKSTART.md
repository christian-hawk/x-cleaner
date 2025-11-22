# X-Cleaner Quick Start Guide

This guide will help you get X-Cleaner up and running in minutes.

## Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- Git (for cloning the repository)

## Installation

### 1. Clone the Repository (if not already done)

```bash
git clone https://github.com/christian-hawk/x-cleaner.git
cd x-cleaner
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install all required packages including:
- FastAPI for the backend
- Streamlit for the dashboard
- Plotly and Altair for visualizations
- SQLAlchemy for database management
- And more...

## Quick Demo with Sample Data

To quickly see X-Cleaner in action without setting up API credentials:

### 1. Generate Sample Data

```bash
python scripts/populate_sample_data.py
```

This creates a SQLite database with 900+ sample accounts across 15 categories.

### 2. Launch the Dashboard

```bash
streamlit run streamlit_app/app.py
```

The dashboard will automatically open in your browser at `http://localhost:8501`

### 3. Explore the Dashboard

Navigate through the pages:

- **🏠 Overview**: See key metrics and category distribution
- **📁 Categories**: Explore categories in detail
- **👥 Accounts**: Browse and search all accounts
- **📊 Analytics**: View advanced analytics and visualizations
- **⚙️ Settings**: Configure and manage data

## Production Setup with Real Data

### 1. Get API Credentials

#### X API (Twitter API v2)

1. Go to [X Developer Portal](https://developer.x.com/)
2. Create a new app or use an existing one
3. Subscribe to the **Basic Plan** ($200/month)
4. Generate a **Bearer Token**
5. Note your **User ID**

#### Grok API (xAI)

1. Go to [xAI Console](https://console.x.ai/)
2. Create an account or sign in
3. Generate an **API Key**

### 2. Configure Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

```env
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
```

### 3. Run Your First Scan

Scan your X following list and categorize accounts:

```bash
python -m backend.cli.commands scan
```

This will:
1. Fetch all accounts you follow from X API
2. Send them to Grok for AI-powered categorization
3. Store results in the SQLite database
4. Take approximately 5-10 minutes for 1000 accounts

### 4. Launch the Dashboard

```bash
streamlit run streamlit_app/app.py
```

## Available Commands

### Scanning

```bash
# Full scan
python -m backend.cli.commands scan

# Scan specific user
python -m backend.cli.commands scan --user-id 123456789

# Update only new follows since last scan
python -m backend.cli.commands update
```

### Dashboard

```bash
# Start dashboard
streamlit run streamlit_app/app.py

# Start on specific port
streamlit run streamlit_app/app.py --server.port 8502

# Start headless (for servers)
streamlit run streamlit_app/app.py --server.headless true
```

### Data Export

```bash
# Export all data to JSON
python -m backend.cli.commands export --format json

# Export to CSV
python -m backend.cli.commands export --format csv

# Export specific category
python -m backend.cli.commands export --category "AI/ML Researchers"
```

### Utilities

```bash
# Show statistics
python -m backend.cli.commands stats

# Clear cache
python -m backend.cli.commands clear-cache

# Generate sample data (for testing)
python scripts/populate_sample_data.py
```

## Dashboard Features

### 📊 Overview Dashboard

- **Key Metrics**: Total accounts, categories, verified percentage, total reach
- **Distribution Charts**: Pie and bar charts for category distribution
- **Top Accounts**: Most followed accounts across all categories
- **Quick Insights**: AI-generated insights about your network

### 📁 Categories Explorer

- **Category Browser**: Browse all discovered categories
- **Detailed Views**: See all accounts within each category
- **Top Accounts**: Most influential accounts per category
- **Analytics**: Category-specific statistics and patterns
- **Export**: Download category data as JSON or CSV

### 👥 Accounts Browser

- **Advanced Search**: Search by username, name, or bio
- **Multi-Filter**: Category, verification status, follower count
- **Flexible Views**: Card view or table view
- **Smart Sorting**: By followers, following, tweets, username, confidence
- **Pagination**: Navigate through large lists efficiently
- **Batch Export**: Export filtered results

### 📊 Advanced Analytics

- **Category Analysis**: Distribution, comparison, trends
- **Engagement Patterns**: Follower vs following relationships
- **Activity Levels**: Account activity categorization
- **Network Insights**: Most influential, active, and engaged accounts
- **Statistical Summary**: Comprehensive statistics and correlations
- **Visual Analytics**: 10+ chart types for deep insights

### ⚙️ Settings & Management

- **Scan Management**: Trigger scans and check status
- **Data Export**: Export all or filtered data
- **Database Management**: View info and perform maintenance
- **Configuration**: Dashboard and API settings

## Troubleshooting

### No Data in Dashboard

**Problem**: Dashboard shows "No data found"

**Solution**:
1. Ensure you've run a scan: `python -m backend.cli.commands scan`
2. Check database exists: `ls -la data/accounts.db`
3. Try sample data: `python scripts/populate_sample_data.py`

### API Rate Limits

**Problem**: Scan fails with rate limit errors

**Solution**:
1. Wait for rate limit to reset (shown in error message)
2. Reduce `BATCH_SIZE` in `.env`
3. Increase `RATE_LIMIT_DELAY` in `.env`

### Module Not Found Errors

**Problem**: Import errors when running scripts

**Solution**:
```bash
pip install -r requirements.txt
```

### Dashboard Performance Issues

**Problem**: Dashboard is slow with large datasets

**Solution**:
1. Use table view instead of card view
2. Apply filters before browsing
3. Reduce items per page in pagination
4. Clear browser cache
5. Close unused browser tabs

## Project Structure

```
x-cleaner/
├── backend/                  # Core backend code
│   ├── api/                 # X and Grok API clients
│   ├── core/                # Core services (categorizer, etc.)
│   ├── cli/                 # Command-line interface
│   ├── config.py            # Configuration management
│   ├── database.py          # Database manager
│   └── models.py            # Data models
├── streamlit_app/           # Web dashboard
│   ├── pages/              # Dashboard pages
│   ├── components/         # Reusable components
│   ├── app.py              # Main dashboard app
│   └── utils.py            # Utility functions
├── scripts/                 # Utility scripts
│   └── populate_sample_data.py
├── data/                    # SQLite database
│   └── accounts.db
├── tests/                   # Test suite
├── .env.example            # Environment variables template
├── requirements.txt         # Python dependencies
└── README.md               # Main documentation
```

## Next Steps

1. **Explore the Dashboard**: Browse all pages and features
2. **Customize Categories**: Re-run scans to refine categorization
3. **Export Data**: Download reports in JSON or CSV
4. **Schedule Scans**: Set up cron jobs for regular updates
5. **Analyze Trends**: Run multiple scans to track changes over time

## Getting Help

- **Documentation**: Check the main [README.md](README.md)
- **Dashboard Help**: See [streamlit_app/README.md](streamlit_app/README.md)
- **Architecture**: Review [ARCHITECTURE.md](ARCHITECTURE.md)
- **Issues**: Open an issue on [GitHub](https://github.com/christian-hawk/x-cleaner/issues)

## Tips for Best Results

1. **Run scans during off-peak hours** to avoid rate limits
2. **Use descriptive categories** for better insights
3. **Export data regularly** for backup and analysis
4. **Clear cache** after new scans for fresh data
5. **Filter before browsing** for better performance

## Cost Estimates

### X API
- **Basic Plan**: $200/month
- Sufficient for personal use
- 10K posts/month limit

### Grok API
- **Pay-per-use**: ~$0.05 per 1000 accounts
- Very affordable for regular scans
- No monthly minimum

### Total
- **Initial Setup**: ~$200/month (X API)
- **Per Scan**: ~$0.05 for 1000 accounts
- **Monthly** (4 scans): ~$200.20

## License

MIT License - See [LICENSE](LICENSE) for details.

---

**Ready to clean up your X following list? Start exploring! 🧹**
