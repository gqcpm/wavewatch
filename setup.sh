#!/bin/bash

# WaveWatch Setup Script
# This script installs all dependencies for both Python and Node.js components

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
cd src/wavewatch/ui/server
npm install
cd ../../../

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
echo "To run your application:"
echo ""
echo "Option 1 - Streamlit App (Recommended for quick start):"
echo "  streamlit run streamlit_app.py"
echo ""
echo "Option 2 - Full Stack (React + FastAPI + MongoDB):"
echo "  # Terminal 1 - Start FastAPI backend:"
echo "  python surf_api.py"
echo ""
echo "  # Terminal 2 - Start React frontend:"
echo "  cd src/wavewatch/ui/client && npm start"
echo ""
echo "  # Terminal 3 - Start Express server (optional, for MongoDB):"
echo "  cd src/wavewatch/ui/server && npm start"
echo ""
echo "🌊 Happy surfing!"
