#!/bin/bash

# WaveWatch Setup Script
# This script installs all dependencies for both Python and Node.js components
# Set INSTALL_DEPS=true to install dependencies, or false to skip installation

# Configuration: Set to "true" to install dependencies, "false" to skip
INSTALL_DEPS="${INSTALL_DEPS:-false}"
CLEAR_PORTS="${CLEAR_PORTS:-true}"

# Function to kill processes on ports
kill_port() {
    local port=$1
    local pids=$(lsof -ti :$port 2>/dev/null)
    if [ -n "$pids" ]; then
        echo "   Stopping process on port $port (PIDs: $pids)..."
        kill -9 $pids 2>/dev/null
        return 0
    fi
    return 1
}

# Clear ports if CLEAR_PORTS is set to true
if [ "${CLEAR_PORTS:-false}" = "true" ]; then
    echo "🧹 Clearing ports 3000, 8001, 5001..."
    kill_port 3000
    kill_port 8001
    kill_port 5001
    sleep 1
    echo ""
fi

echo "🌊 Setting up WaveWatch..."
echo "================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.7+ first."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js first."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm first."
    exit 1
fi

echo "✅ Python and Node.js are installed"

# Install dependencies if INSTALL_DEPS is true
if [ "$INSTALL_DEPS" = "true" ]; then
    echo ""
    echo "📦 Installing dependencies (INSTALL_DEPS=true)..."
    echo ""
    
    # Install Python dependencies
    echo "📦 Installing Python dependencies..."
    pip install -r requirements.txt

    # Install Node.js dependencies for React client
    echo "📦 Installing React client dependencies..."
    cd src/wavewatch/ui/client
    npm install
    cd ../../../

    # Install Node.js dependencies for Express server
    echo "📦 Installing Express server dependencies..."
    if [ -d "src/wavewatch/ui/server" ]; then
        cd src/wavewatch/ui/server
        npm install
        cd ../../../
    else
        echo "⚠️  Express server directory not found, skipping..."
    fi
    
    echo ""
    echo "✅ Dependencies installed!"
else
    echo ""
    echo "⏭️  Skipping dependency installation (INSTALL_DEPS=false)"
    echo "   To install dependencies, run: INSTALL_DEPS=true ./setup.sh"
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp env.example .env
    echo "⚠️  Please edit .env file and add your API keys:"
    echo "   - GEMINI_API_KEY (get from https://makersuite.google.com/app/apikey)"
    echo "   - STORMGLASS_API_KEY (get from https://stormglass.io)"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "🚀 Starting full stack application..."
echo ""

# Get the script directory to ensure we're in the right place
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Start FastAPI backend in background
echo "📡 Starting FastAPI backend (port 8001)..."
PYTHONPATH=src python3 surf_api.py &
FASTAPI_PID=$!
echo "   FastAPI started (PID: $FASTAPI_PID)"

# Wait a moment for FastAPI to start
sleep 2

# Start Express server in background
if [ -d "src/wavewatch/ui/server" ]; then
    echo "🗄️  Starting Express/MongoDB server (port 5001)..."
    cd src/wavewatch/ui/server
    npm start &
    EXPRESS_PID=$!
    echo "   Express server started (PID: $EXPRESS_PID)"
    cd "$SCRIPT_DIR"
    # Wait a moment for Express to start
    sleep 2
else
    echo "⚠️  Express server directory not found, skipping..."
    EXPRESS_PID=""
fi

# Start React frontend in background
echo "⚛️  Starting React frontend (port 3000)..."
cd src/wavewatch/ui/client
npm start &
REACT_PID=$!
echo "   React frontend started (PID: $REACT_PID)"
cd "$SCRIPT_DIR"../

echo ""
echo "✅ All services started!"
echo ""
echo "📡 Services running:"
echo "   - FastAPI backend: http://localhost:8001"
echo "   - Express server: http://localhost:5001"
echo "   - React frontend: http://localhost:3000"
echo ""
echo "💡 To stop all services, run:"
if [ -n "$EXPRESS_PID" ]; then
    echo "   kill $FASTAPI_PID $EXPRESS_PID $REACT_PID"
else
    echo "   kill $FASTAPI_PID $REACT_PID"
fi
echo ""
echo "🌊 Happy surfing!"
echo ""
echo "Opening browser in 5 seconds..."
sleep 5
open http://localhost:3000 2>/dev/null || xdg-open http://localhost:3000 2>/dev/null || echo "Please open http://localhost:3000 in your browser"
