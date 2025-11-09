#!/bin/bash

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  Healthcare Contract Analysis - Quick Test                 ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Activate virtual environment
source venv/bin/activate

# Run a quick test query
python3 src/cli.py --provider claude -q "What is the reimbursement rate for CPT 99213 according to United Healthcare?"
