#!/bin/bash

# Exit on any error
set -e

# Repository URL to clone
REPO_URL="https://github.com/BrianTheMint/tor_scraper.git"

# Base directory for the setup
BASE_DIR="/tor_scraper"

# Destination paths
TORRC_DEST="/etc/tor/torrc"
CRAWLER_DEST="$BASE_DIR/crawler.py"
REQUIREMENTS_DEST="$BASE_DIR/requirements.txt"
VENV_DIR="$BASE_DIR/venv"

# Create the base directory
echo "Creating base directory at $BASE_DIR..."
sudo mkdir -p "$BASE_DIR"
sudo chown $USER:$USER "$BASE_DIR"

echo "Updating package list and upgrading system..."
sudo apt-get update -y && sudo apt-get upgrade -y

echo "Installing required packages: git, python3, python3-venv, python3-pip, privoxy, tor, wget..."
sudo apt-get install -y git python3 python3-venv python3-pip tor wget python3-tk

# Clone the repository
echo "Cloning the repository from $REPO_URL..."
git clone "$REPO_URL" -b gui "$BASE_DIR"

# Move the configuration files to the correct locations
echo "Moving torrc to $TORRC_DEST..."
sudo mv "$BASE_DIR/torrc" "$TORRC_DEST"

# Set permissions for crawler.py
echo "Setting permissions for crawler.py..."
chmod 644 "$BASE_DIR/crawler.py"

# Create a Python virtual environment
echo "Creating Python virtual environment in $VENV_DIR..."
python3 -m venv "$VENV_DIR"

# Activate the virtual environment and install requirements
echo "Activating virtual environment and installing requirements..."
source "$VENV_DIR/bin/activate"
pip install --no-cache-dir -r "$BASE_DIR/requirements.txt"
deactivate

# Set permissions on the base directory
echo "Setting permissions for base directory..."
sudo chmod -R 777 "$BASE_DIR"

# Restart services to apply changes
echo "Restarting Tor and Privoxy services..."
sudo systemctl restart tor

echo "Installation, configuration, and virtual environment setup complete."
echo "All files are located in $BASE_DIR."