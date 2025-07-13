#!/bin/bash

# Setup script for Manalytics development environment

set -e

echo "🚀 Setting up Manalytics development environment..."

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Setup pre-commit hooks
echo "Setting up pre-commit hooks..."
pre-commit install

# Create logs directory
mkdir -p logs

# Run tests to verify installation
echo "Running tests to verify installation..."
pytest tests/ -v

echo "✅ Development environment setup complete!"
echo ""
echo "To activate the environment:"
echo "source venv/bin/activate"
echo ""
echo "To run the pipeline:"
echo "python run_full_pipeline.py --format Standard --start-date 2025-07-01 --end-date 2025-07-07" 