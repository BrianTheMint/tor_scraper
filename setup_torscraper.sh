#!/bin/bash

# Clone the repository and checkout the gui-multi-tor branch using SSH
git clone git@github.com:BrianTheMint/tor_crawler.git -b gui-multi-tor

# Navigate to the cloned repository
cd tor_crawler

# Install necessary packages
sudo apt-get update
sudo apt-get install -y python3 python3-venv python3-pip

# Set up a virtual environment in the cloned repository
python3 -m venv venv

# Activate the virtual environment and install requirements
source venv/bin/activate
pip install -r requirements.txt

echo "Setup complete."