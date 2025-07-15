#!/bin/bash

# SwiftGen Server Startup Script
echo "🚀 Starting SwiftGen Server..."

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "✓ Using virtual environment"
    source venv/bin/activate
else
    echo "⚠️  No virtual environment found, using system Python"
fi

# Export environment variables if .env exists
if [ -f ".env" ]; then
    echo "✓ Loading environment variables from .env"
    export $(cat .env | xargs)
fi

# Check required API keys
if [ -z "$CLAUDE_API_KEY" ]; then
    echo "⚠️  Warning: CLAUDE_API_KEY not set"
fi

if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  Warning: OPENAI_API_KEY not set"
fi

# Start the server
echo "📡 Starting FastAPI server on http://localhost:8000"
echo "📖 API documentation available at http://localhost:8000/docs"
echo ""

# Use uvicorn with auto-reload for development
python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000