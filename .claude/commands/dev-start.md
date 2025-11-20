---
description: Start development servers (FastAPI backend + Streamlit dashboard)
---

Start the X-Cleaner development environment with both backend and frontend servers.

## Prerequisites Check

1. **Virtual environment activated?**
   ```bash
   which python  # Should show venv path
   ```

2. **Dependencies installed?**
   ```bash
   pip list | grep -E "fastapi|streamlit|httpx|pydantic"
   ```

3. **Environment variables configured?**
   ```bash
   cat .env | grep -E "X_API_BEARER_TOKEN|XAI_API_KEY|X_USER_ID"
   ```

## Start Servers

**Terminal 1 - Backend API (FastAPI):**
```bash
cd /home/user/x-cleaner
source venv/bin/activate  # If not already activated
uvicorn backend.main:app --reload --port 8000 --host 0.0.0.0
```

**Terminal 2 - Frontend Dashboard (Streamlit):**
```bash
cd /home/user/x-cleaner
source venv/bin/activate  # If not already activated
streamlit run streamlit_app/app.py --server.port 8501 --server.address 0.0.0.0
```

## Access URLs

- 📊 **Dashboard**: http://localhost:8501
- 🔌 **API**: http://localhost:8000
- 📚 **API Docs (Swagger)**: http://localhost:8000/docs
- 📖 **API Docs (ReDoc)**: http://localhost:8000/redoc

## Health Checks

Test backend is running:
```bash
curl http://localhost:8000/
# Should return: {"message": "X-Cleaner API", "version": "1.0.0"}
```

Test API endpoints:
```bash
curl http://localhost:8000/api/stats
curl http://localhost:8000/api/categories
```

## Common Issues

**Port already in use:**
```bash
# Find process using port 8000
lsof -i :8000
# Kill it
kill -9 <PID>
```

**Import errors:**
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

**Module not found:**
```bash
# Add project root to PYTHONPATH
export PYTHONPATH="/home/user/x-cleaner:$PYTHONPATH"
```
