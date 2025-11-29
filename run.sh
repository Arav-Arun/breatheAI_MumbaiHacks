#!/bin/bash

# BREATHAI Startup Script
echo "🌬️ Starting BREATHAI..."
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found"
    echo "📝 Creating .env from .env.example..."
    cp .env.example .env 2>/dev/null || echo "Please create .env file manually"
    echo ""
    echo "ℹ️  Note: The app will work with mock data if API keys are not set"
    echo ""
fi

# Check if virtual environment exists
if [ ! -d "venv" ] && [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
    echo ""
fi

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt

echo ""
echo "🚀 Starting Flask app..."
echo ""

python app.py

