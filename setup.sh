#!/bin/bash
# POC Setup Script

set -e

echo "=========================================="
echo "StockCharts Hybrid Automation POC Setup"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Found Python $python_version"
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip -q
echo "✓ pip upgraded"
echo ""

# Install requirements
echo "Installing dependencies..."
pip install -r requirements.txt -q
echo "✓ Dependencies installed"
echo ""

# Install Playwright browsers
echo "Installing Playwright browsers (this may take a few minutes)..."
playwright install chromium
echo "✓ Playwright browsers installed"
echo ""

# Setup config
if [ ! -f "config/.env" ]; then
    echo "Creating .env configuration file..."
    cp config/.env.example config/.env
    echo "✓ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit config/.env with your credentials:"
    echo "   - StockCharts.com username and password"
    echo "   - Anthropic API key"
else
    echo "✓ .env file already exists"
fi
echo ""

# Create screenshots directory
mkdir -p screenshots
echo "✓ Screenshots directory created"
echo ""

echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit config/.env with your credentials"
echo "2. Activate venv: source venv/bin/activate"
echo "3. Run test: python main.py --mode single --ticker AAPL"
echo ""
echo "See README.md for full documentation"
echo ""
