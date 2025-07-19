#!/usr/bin/env bash
set -e

echo "Setting up Python environment..."

# Install Python dependencies
echo "Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

# Install Playwright browser (Chromium)
echo "Installing Playwright browser..."
playwright install chromium

echo "Build completed successfully!"