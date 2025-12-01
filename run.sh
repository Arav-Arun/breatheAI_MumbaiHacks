#!/bin/bash

# Setup and run script

# Check for .env
if [ ! -f .env ]; then
    echo "Creating .env from example..."
    cp .env.example .env 2>/dev/null || echo "Please create .env file manually"
fi

# Setup venv if needed
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

# Install deps
echo "Installing dependencies..."
pip install -q -r requirements.txt

echo "Starting server..."
python backend/app.py
