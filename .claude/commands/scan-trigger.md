---
description: Trigger a new X account scan and categorization
---

Trigger a new scan of X accounts to fetch and categorize all accounts you follow.

## Prerequisites

1. **API credentials configured in .env:**
   ```bash
   grep -E "X_API_BEARER_TOKEN|XAI_API_KEY|X_USER_ID" .env
   ```

2. **Backend server running:**
   ```bash
   curl http://localhost:8000/
   ```

## Option 1: Via Web Dashboard (Recommended)

1. Open dashboard: http://localhost:8501
2. Click **"Trigger New Scan"** button in sidebar
3. Watch real-time progress
4. View results when complete

## Option 2: Via API

Trigger scan via REST API:
```bash
curl -X POST http://localhost:8000/api/scan \
  -H "Content-Type: application/json" \
  -d '{"user_id": "YOUR_USER_ID"}'
```

Response:
```json
{
  "status": "started",
  "job_id": "abc-123-def",
  "message": "Scan initiated"
}
```

Check progress:
```bash
curl http://localhost:8000/api/scan/status
```

## Option 3: Via CLI (Future)

Once CLI is implemented:
```bash
python -m backend.cli scan
```

## What Happens During Scan

**Phase 1: Fetch Accounts (X API)**
- Fetches all accounts you follow via X API v2
- Handles pagination (max 1000 per request)
- Respects rate limits
- Duration: ~30 seconds per 1000 accounts

**Phase 2: Discover Categories (Grok AI)**
- Samples first 200 accounts
- Grok analyzes and discovers 10-20 natural categories
- Generates category metadata
- Duration: ~15 seconds

**Phase 3: Categorize All Accounts (Grok AI)**
- Processes accounts in batches of 50
- Assigns each account to discovered category
- Provides confidence score and reasoning
- Duration: ~2 minutes per 1000 accounts

**Phase 4: Save Results (Database)**
- Stores categorized accounts in SQLite
- Updates statistics
- Caches results
- Duration: ~5 seconds

**Total Time: ~3 minutes per 1000 accounts**

## Expected Cost

For 1000 accounts:
- X API: Included in $200/month plan
- Grok API: ~$0.05
- **Total: $0.05 per scan**

## Monitoring Progress

**WebSocket (Real-time):**
```javascript
ws://localhost:8000/ws/scan
```

**Polling (REST):**
```bash
watch -n 2 'curl -s http://localhost:8000/api/scan/status | jq'
```

## Post-Scan Actions

After scan completes:

1. **View Statistics:**
   ```bash
   curl http://localhost:8000/api/stats | jq
   ```

2. **List Categories:**
   ```bash
   curl http://localhost:8000/api/categories | jq
   ```

3. **Export Data:**
   ```bash
   curl http://localhost:8000/api/export?format=json > data/export.json
   ```

4. **Explore in Dashboard:**
   - Visit http://localhost:8501
   - Browse categories, view charts, search accounts

## Troubleshooting

**"Invalid Bearer Token":**
- Check X_API_BEARER_TOKEN in .env
- Verify Basic Plan access

**"Rate limit exceeded":**
- Wait for rate limit reset (shown in error)
- Check X API rate limit status

**"Categorization failed":**
- Check XAI_API_KEY is valid
- Verify internet connection
- Check xAI API status

**"No accounts found":**
- Verify X_USER_ID is correct
- Check account follows some accounts
- Check X API permissions
