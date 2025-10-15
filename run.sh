#!/bin/bash
# WhaleRadar.ai Launch Script

echo "🐋 WhaleRadar.ai Launcher 🐋"
echo "=========================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Check Python version
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Install/update dependencies
echo "Checking dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found!"
    echo "Creating .env from template..."
    cp .env.example .env
    echo "Please edit .env with your API credentials before running."
    exit 1
fi

# Create necessary directories
mkdir -p logs data

# Run the test script first
echo ""
echo "Running setup verification..."
python test_setup.py

# Ask if user wants to continue
echo ""
read -p "Do you want to start WhaleRadar.ai? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Starting WhaleRadar.ai..."
    python -m src.main
else
    echo "Setup complete. Run 'python -m src.main' when ready."
fi