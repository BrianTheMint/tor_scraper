#!/bin/bash

# Navigate to the /tor_scraper directory
cd /
cd /tor_scraper

# Activate the virtual environment
source venv/bin/activate

# Run the Python script
python3 ./crawler.py

# Deactivate the virtual environment after the script finishes
deactivate
