#!/bin/bash

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  Healthcare Contract Analysis System - Setup               ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check if python3-venv is installed
if ! dpkg -l | grep -q python3-venv; then
    echo "📦 Installing python3-venv package..."
    sudo apt update
    sudo apt install -y python3-venv python3-pip
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "✅ Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📦 Installing dependencies (this may take a few minutes)..."
pip install -r requirements.txt

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║  ✅ Setup Complete!                                        ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "🚀 To run the system:"
echo ""
echo "   CLI Mode:"
echo "   $ source venv/bin/activate"
echo "   $ python3 src/cli.py --provider claude"
echo ""
echo "   Web Interface:"
echo "   $ source venv/bin/activate"
echo "   $ streamlit run app.py"
echo ""
echo "   Quick Test:"
echo "   $ source venv/bin/activate"
echo "   $ python3 src/cli.py --provider claude -q \"What is the reimbursement rate for CPT 99213?\""
echo ""
