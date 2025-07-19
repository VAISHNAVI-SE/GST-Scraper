#!/usr/bin/env bash
set -e

echo "Python version: $(python --version)"
echo "Setting up Python environment..."

# Upgrade pip
echo "Upgrading pip..."
python -m pip install --upgrade pip

# Install Python dependencies
echo "Installing Python packages..."
pip install -r requirements.txt

# Install Playwright browser
echo "Installing Playwright browser..."
playwright install chromium

# Verify installation
echo "Verifying Playwright installation..."
python -c "from playwright.sync_api import sync_playwright; print('Playwright imported successfully')"

echo "Build completed successfully!"