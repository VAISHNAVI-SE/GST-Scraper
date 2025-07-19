#!/usr/bin/env bash

# Step 1: Install Python dependencies
echo "Installing Python packages..."
pip install -r requirements.txt

# Step 2: Install Playwright browser (Chromium)
echo "Installing Playwright browser..."
playwright install chromium
