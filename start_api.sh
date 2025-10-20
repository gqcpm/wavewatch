#!/bin/bash

# Start WaveWatch API server
echo "🌊 Starting WaveWatch API server..."
echo "📡 API will be available at: http://localhost:8000"
echo "📚 API docs available at: http://localhost:8000/docs"
echo ""

# Install FastAPI dependencies if needed
pip install fastapi uvicorn

# Start the API server
python surf_api.py
