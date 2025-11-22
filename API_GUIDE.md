# X-Cleaner API Guide

## Overview

The X-Cleaner API provides RESTful endpoints and WebSocket support for scanning, categorizing, and analyzing X (Twitter) accounts.

## Quick Start

### 1. Start the API Server

```bash
# Using the start script
./start_api.sh

# Or manually
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Access the API

- **Main API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs (Swagger UI)
- **Alternative Docs**: http://localhost:8000/redoc

## API Endpoints

### Health & Info

#### `GET /`
Get API information and status.

**Response:**
```json
{
  "message": "X-Cleaner API",
  "version": "1.0.0",
  "docs": "/docs",
  "status": "running"
}
```

#### `GET /health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-21T01:36:31.398365"
}
```

### Statistics

#### `GET /api/stats`
Get summary statistics.

**Response:**
```json
{
  "total_accounts": 847,
  "total_categories": 15,
  "verified_count": 234,
  "last_updated": "2025-11-21T01:30:00"
}
```

### Categories

#### `GET /api/categories`
List all discovered categories with metadata.

**Response:**
```json
{
  "categories": [
    {
      "id": 1,
      "name": "AI/ML Researchers & Practitioners",
      "description": "Accounts focused on AI research...",
      "characteristics": "['Technical discussions', 'Paper sharing']",
      "estimated_percentage": 10.3,
      "account_count": 87,
      "created_at": "2025-11-21T00:00:00",
      "updated_at": "2025-11-21T00:00:00"
    }
  ],
  "total_categories": 15
}
```

#### `GET /api/categories/{category_name}/accounts`
Get all accounts in a specific category.

**Parameters:**
- `category_name` (path): Name of the category

**Response:**
```json
[
  {
    "user_id": "123456789",
    "username": "researcher1",
    "display_name": "AI Researcher",
    "bio": "Machine learning enthusiast",
    "verified": true,
    "followers_count": 2300000,
    "following_count": 842,
    "tweet_count": 12400,
    "category": "AI/ML Researchers & Practitioners",
    "confidence": 0.95,
    "reasoning": "Strong focus on ML research",
    "analyzed_at": "2025-11-21T00:00:00"
  }
]
```

### Accounts

#### `GET /api/accounts`
List accounts with filtering and pagination.

**Query Parameters:**
- `category` (optional): Filter by category name
- `verified` (optional): Filter by verified status (true/false)
- `search` (optional): Search in username, display name, or bio
- `limit` (optional, default: 100): Maximum results to return
- `offset` (optional, default: 0): Number of results to skip

**Examples:**
```bash
# Get all accounts
GET /api/accounts

# Get verified accounts
GET /api/accounts?verified=true

# Get accounts in specific category
GET /api/accounts?category=AI/ML%20Researchers

# Search accounts
GET /api/accounts?search=python

# Paginated results
GET /api/accounts?limit=20&offset=40
```

**Response:**
```json
{
  "total": 847,
  "accounts": [...],
  "limit": 100,
  "offset": 0
}
```

### Scanning

#### `POST /api/scan`
Trigger a new scan of X accounts.

**Request Body:**
```json
{
  "username": "elonmusk"
}
```

Or alternatively:
```json
{
  "user_id": "123456789"
}
```

**Response:**
```json
{
  "job_id": "scan_abc123def456",
  "status": "running",
  "message": "Scan started successfully"
}
```

**Status Codes:**
- `202 Accepted`: Scan started successfully
- `400 Bad Request`: Invalid request (missing username/user_id or username not found)
- `404 Not Found`: Username not found on X
- `409 Conflict`: Scan already in progress for this user
- `500 Internal Server Error`: API credentials not configured

**Example:**
```bash
# Using username (recommended)
curl -X POST http://localhost:8000/api/scan \
  -H "Content-Type: application/json" \
  -d '{"username": "elonmusk"}'

# Or using user_id directly
curl -X POST http://localhost:8000/api/scan \
  -H "Content-Type: application/json" \
  -d '{"user_id": "123456789"}'
```

**Note:** If `username` is provided, the API will automatically look up the corresponding `user_id` before starting the scan.

#### `GET /api/scan/{job_id}/status`
Get scan status by job ID.

**Response:**
```json
{
  "job_id": "scan_abc123def456",
  "status": "running",
  "progress": 45.5,
  "message": "Categorizing accounts...",
  "error": null,
  "started_at": "2025-01-20T15:30:00Z",
  "completed_at": null
}
```

**Status Values:**
- `pending`: Scan queued but not started
- `running`: Scan in progress
- `completed`: Scan finished successfully
- `error`: Scan failed

#### `GET /api/scan/{job_id}/progress`
Get detailed scan progress by job ID.

**Response:**
```json
{
  "job_id": "scan_abc123def456",
  "status": "running",
  "progress": 45.5,
  "current_step": "categorize_accounts",
  "message": "Categorizing accounts...",
  "current": 450,
  "total": 1000,
  "accounts_fetched": 1000,
  "accounts_categorized": 450,
  "accounts_saved": 0,
  "error": null,
  "started_at": "2025-01-20T15:30:00Z",
  "completed_at": null
}
```

**Progress Steps:**
- `fetch_accounts` (0-30%): Fetching accounts from X API
- `discover_categories` (30-50%): Discovering categories using Grok AI
- `categorize_accounts` (50-90%): Categorizing all accounts
- `save_to_database` (90-100%): Saving results to database

### WebSocket - Real-time Updates

#### `WS /ws/scan/{job_id}`
WebSocket endpoint for real-time scan progress updates.

**Connection:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/scan/scan_abc123def456');

ws.onmessage = (event) => {
  const progress = JSON.parse(event.data);
  console.log(`Progress: ${progress.progress}%`);
  console.log(`Status: ${progress.status}`);
  console.log(`Message: ${progress.message}`);
  
  if (progress.status === 'completed') {
    console.log('Scan complete!');
    ws.close();
  } else if (progress.status === 'error') {
    console.error('Scan failed:', progress.message);
    ws.close();
  }
};
```

**Message Format:**
```json
{
  "type": "progress",
  "job_id": "scan_abc123def456",
  "status": "running",
  "progress": 45.5,
  "message": "Categorizing accounts...",
  "current": 450,
  "total": 1000
}
```

**Updates:**
The WebSocket sends progress updates every second until the scan is completed or errors.

### Export

#### `GET /api/export`
Export data in various formats.

**Query Parameters:**
- `format` (optional, default: json): Export format (json, csv)

**Response (JSON format):**
```json
{
  "accounts": [...],
  "categories": [...],
  "exported_at": "2025-11-21T01:36:31.398365"
}
```

## Error Handling

All endpoints use standard HTTP status codes:

- `200 OK`: Request succeeded
- `400 Bad Request`: Invalid request parameters
- `404 Not Found`: Resource not found
- `409 Conflict`: Resource conflict (e.g., scan already running)
- `500 Internal Server Error`: Server error

Error responses include a detail message:
```json
{
  "detail": "Error description here"
}
```

## CORS Configuration

The API is configured to accept requests from:
- http://localhost:8501 (Streamlit)
- http://localhost:3000 (React)
- http://127.0.0.1:8501
- http://127.0.0.1:3000

## Development

### Running Tests

```bash
# Test API endpoints
python test_api.py

# Run full test suite
pytest tests/
```

### Interactive API Documentation

Visit http://localhost:8000/docs to:
- View all available endpoints
- Test endpoints directly in the browser
- See request/response schemas
- Generate code examples

## Example Workflows

### 1. Complete Scan Workflow

```bash
# 1. Check API health
curl http://localhost:8000/health

# 2. Trigger scan (using username - recommended)
curl -X POST http://localhost:8000/api/scan \
  -H "Content-Type: application/json" \
  -d '{"username": "elonmusk"}'

# Response includes job_id:
# {"job_id": "scan_abc123def456", "status": "running", "message": "Scan started successfully"}

# 3. Check status using job_id
curl http://localhost:8000/api/scan/scan_abc123def456/status

# 4. Get detailed progress
curl http://localhost:8000/api/scan/scan_abc123def456/progress

# 5. Or use WebSocket for real-time updates (see WebSocket section above)

# 6. Get results after completion
curl http://localhost:8000/api/statistics/overall
curl http://localhost:8000/api/statistics/categories
```

### 2. Explore Categories

```bash
# 1. Get all categories
curl http://localhost:8000/api/categories

# 2. Get accounts in specific category
curl http://localhost:8000/api/categories/AI%2FML%20Researchers%20%26%20Practitioners/accounts

# 3. Filter accounts
curl "http://localhost:8000/api/accounts?verified=true&limit=10"
```

### 3. Real-time Monitoring (JavaScript)

```javascript
// 1. Trigger scan and get job_id (using username)
fetch('http://localhost:8000/api/scan', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({username: 'elonmusk'})
})
.then(res => res.json())
.then(data => {
  const jobId = data.job_id;
  console.log('Scan started with job_id:', jobId);
  
  // 2. Connect WebSocket using job_id
  const ws = new WebSocket(`ws://localhost:8000/ws/scan/${jobId}`);
  
  ws.onmessage = (event) => {
    const progress = JSON.parse(event.data);
    console.log(`Progress: ${progress.progress}% - ${progress.message}`);
    
    if (progress.status === 'completed') {
      console.log('Scan complete!');
      ws.close();
    } else if (progress.status === 'error') {
      console.error('Scan failed:', progress.message);
      ws.close();
    }
  };
  
  ws.onerror = (error) => {
    console.error('WebSocket error:', error);
  };
});
```

## Configuration

### Environment Variables

Create a `.env` file with:

```bash
# X API Credentials
X_API_BEARER_TOKEN=your_bearer_token_here
X_USERNAME=your_username_here

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
```

## Performance Tips

1. **Use Pagination**: For large datasets, use `limit` and `offset` parameters
2. **Cache Results**: The API caches categorizations for 7 days by default
3. **WebSocket for Real-time**: Use WebSocket for scan progress instead of polling
4. **Batch Exports**: Use export endpoint for bulk data access

## Troubleshooting

### Scan Not Starting

Check:
1. `.env` file exists with valid credentials (`X_API_BEARER_TOKEN` and `XAI_API_KEY`)
2. `username` or `user_id` is provided in request body (username is recommended)
3. Username exists on X (if using username, API will verify automatically)
4. No other scan is running for the same user (check with `GET /api/scan/{job_id}/status`)
5. Backend API server is running (`uvicorn backend.main:app --reload --port 8000`)

### Database Errors

Check:
1. `data/` directory exists and is writable
2. Database file isn't locked by another process

### Connection Refused

Check:
1. API server is running (`./start_api.sh`)
2. Port 8000 is not blocked by firewall
3. Correct host/port in configuration

## Support

- **Documentation**: http://localhost:8000/docs
- **Project Issues**: Check project README.md
- **API Source**: `backend/main.py`
