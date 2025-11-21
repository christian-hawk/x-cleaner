#!/bin/bash
# Start X-Cleaner FastAPI Backend Server

echo "🚀 Starting X-Cleaner API Server..."
echo "="
echo "API will be available at:"
echo "  - Main API: http://localhost:8000"
echo "  - API Docs: http://localhost:8000/docs"
echo "  - ReDoc: http://localhost:8000/redoc"
echo "="
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "   Please create .env file with your API credentials"
    echo "   See .env.example for reference"
    echo ""
fi

# Start uvicorn with hot reload
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
