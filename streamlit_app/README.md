# X-Cleaner Streamlit Dashboard

This is the web-based dashboard for X-Cleaner, providing an interactive interface to explore and analyze your X (Twitter) network.

## Features

### 📊 Overview Dashboard
- **Key Metrics**: Total accounts, categories, verified accounts, and total reach
- **Category Distribution**: Visual pie and bar charts
- **Top Accounts**: See your most followed accounts
- **Category Highlights**: Quick insights into top categories
- **Analytics**: Verification rates and follower distribution

### 📁 Categories Explorer
- **Category Browser**: Explore all discovered categories
- **Detailed Views**: See all accounts within each category
- **Analytics**: Category-specific statistics and patterns
- **Export**: Download category data as JSON or CSV

### 👥 Accounts Browser
- **Advanced Search**: Search by username, name, or bio
- **Powerful Filters**: Filter by category, verification status, follower count
- **Multiple Views**: Card view or table view
- **Sorting**: Sort by followers, following, tweets, username, or confidence
- **Pagination**: Navigate through large account lists
- **Export**: Export filtered results

### 📊 Advanced Analytics
- **Category Analysis**: Distribution, comparison, and trends
- **Engagement Patterns**: Follower vs following analysis
- **Activity Levels**: Account activity categorization
- **Network Insights**: Most influential, active, and engaged accounts
- **Statistical Summary**: Comprehensive statistics and correlations

### ⚙️ Settings & Management
- **Scan Management**: Trigger new scans and check status
- **Data Export**: Export all data in JSON or CSV format
- **Database Management**: View database info and perform maintenance
- **Configuration**: Dashboard and API settings

## Installation

The dashboard dependencies are already included in the main `requirements.txt`:

```bash
pip install -r requirements.txt
```

## Running the Dashboard

### From Project Root

```bash
streamlit run streamlit_app/app.py
```

### From Streamlit App Directory

```bash
cd streamlit_app
streamlit run app.py
```

The dashboard will open in your default browser at `http://localhost:8501`

## Usage

### First Time Setup

1. **Run a scan** to populate the database:
   ```bash
   python -m backend.cli.commands scan
   ```

2. **Start the dashboard**:
   ```bash
   streamlit run streamlit_app/app.py
   ```

3. **Explore your data** through the various pages

### Navigation

The dashboard has a multi-page structure:

- **🏠 Home** (app.py): Overview and key metrics
- **📁 Categories**: Explore categories in detail
- **👥 Accounts**: Browse and search all accounts
- **📊 Analytics**: Advanced analytics and visualizations
- **⚙️ Settings**: Configuration and data management

### Refreshing Data

After running a new scan, click the "🔄 Refresh Data" button in the sidebar or go to Settings and click "🔄 Refresh Dashboard Data".

## Project Structure

```
streamlit_app/
├── app.py                    # Main dashboard (Overview)
├── pages/                    # Additional pages
│   ├── 1_📁_Categories.py   # Categories explorer
│   ├── 2_👥_Accounts.py     # Accounts browser
│   ├── 3_📊_Analytics.py    # Advanced analytics
│   └── 4_⚙️_Settings.py     # Settings and management
├── components/               # Reusable components
│   ├── charts.py            # Chart components
│   └── filters.py           # Filter components
├── utils.py                 # Utility functions
└── README.md                # This file
```

## Features in Detail

### Caching

The dashboard uses Streamlit's caching to improve performance:

- Database connections are cached with `@st.cache_resource`
- Data queries are cached for 5 minutes with `@st.cache_data(ttl=300)`
- Click "Refresh Data" to clear cache and reload

### Export Functionality

Export data in two formats:

- **JSON**: Structured data with full account information
- **CSV**: Spreadsheet-friendly format for analysis in Excel/Sheets

Export options:
- All accounts
- Filtered accounts (from Accounts Browser)
- Category-specific accounts

### Filtering and Search

Advanced filtering options:
- Text search across username, display name, and bio
- Category multi-select
- Verification status filter
- Follower count range slider
- Confidence score threshold

### Visualizations

Multiple chart types using Plotly:
- Pie/Donut charts for distribution
- Bar charts for comparisons
- Box plots for statistical distribution
- Scatter plots for relationships
- Radar charts for category comparison
- Treemaps for hierarchical data
- Histograms for frequency distribution

## Configuration

### Theme Customization

Edit `.streamlit/config.toml` to customize the theme:

```toml
[theme]
primaryColor = "#1DA1F2"  # Twitter blue
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F5F8FA"
textColor = "#14171A"
```

### Performance Settings

For large datasets (1000+ accounts):

1. Increase cache TTL in `utils.py`
2. Reduce items per page in pagination
3. Use table view instead of card view in Accounts Browser

## Troubleshooting

### No Data Displayed

- Ensure you've run a scan: `python -m backend.cli.commands scan`
- Check database exists: `data/accounts.db`
- Try clearing cache: Click "🔄 Refresh Data"

### Slow Performance

- Reduce cache TTL
- Use table view instead of cards
- Decrease items per page
- Close other browser tabs

### Charts Not Displaying

- Ensure Plotly is installed: `pip install plotly`
- Check browser console for errors
- Try refreshing the page

## Development

### Adding New Pages

1. Create a new file in `pages/` with format: `N_emoji_Name.py`
2. Use the same import pattern as existing pages
3. Follow the page template structure

### Adding New Charts

1. Add chart function to `components/charts.py`
2. Follow the existing pattern for Plotly figures
3. Return a `go.Figure` object

### Adding New Filters

1. Add filter function to `components/filters.py`
2. Return filtered DataFrame and filter info
3. Use Streamlit components for UI

## Performance Tips

1. **Use table view** for large result sets
2. **Apply filters** before browsing
3. **Limit pagination size** for faster rendering
4. **Clear cache regularly** if data is stale
5. **Close unused tabs** to free memory

## Future Enhancements

Potential features for future releases:

- Real-time scan progress via WebSocket
- Bulk account management (unfollow)
- Historical trend analysis
- Custom category creation
- Multi-user support
- Cloud deployment guide
- Mobile-optimized responsive design

## Support

For issues or questions:

1. Check the main project README
2. Review the troubleshooting section
3. Open an issue on GitHub

## License

This project is licensed under the MIT License - see the LICENSE file in the project root.
