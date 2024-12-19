#!/bin/bash

# Clone the repository and checkout the gui-muli-tor branch
git clone -b gui-muli-tor https://github.com/BrianTheMint/tor_scraper.git /tor_scraper_gui_multi

# Make the folder accessible to everyone
chmod -R 777 /tor_scraper_gui_multi

# Copy the tor_scraper folder to the new location
cp -r /home/brian/tor_scraper /tor_scraper_gui_multi

# Install necessary packages
sudo apt-get update
sudo apt-get install -y python3 python3-venv python3-pip python3-tk tor

# Set up a virtual environment in /tor_scraper_gui_multi/tor_scraper
cd /tor_scraper_gui_multi/tor_scraper
python3 -m venv venv

# Activate the virtual environment and install requirements
source venv/bin/activate
pip install -r requirements.txt

echo "Setup complete."