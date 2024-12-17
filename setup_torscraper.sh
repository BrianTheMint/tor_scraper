#!/bin/bash

# Exit on any error
set -e

# URLs for downloading files
TORRC_URL="https://raw.githubusercontent.com/BrianTheMint/tor_scraper/refs/heads/main/torrc"
PRIVOXY_CONFIG_URL="https://raw.githubusercontent.com/BrianTheMint/tor_scraper/refs/heads/main/privoxy/config"
CRAWLER_SCRIPT_URL="https://raw.githubusercontent.com/BrianTheMint/tor_scraper/refs/heads/main/crawler.py"
REQUIREMENTS_URL="https://raw.githubusercontent.com/BrianTheMint/tor_scraper/refs/heads/main/requirements.txt"

# Detect the user's home directory
HOME_DIR=$(eval echo "~$USER")
BASE_DIR="/tor_scraper"

# Destination paths
TORRC_DEST="/etc/tor/torrc"
PRIVOXY_CONFIG_DEST="/etc/privoxy/config"
CRAWLER_DEST="$BASE_DIR/crawler.py"
REQUIREMENTS_DEST="$BASE_DIR/requirements.txt"
VENV_DIR="$BASE_DIR/venv"

# Create the base directory
echo "Creating base directory at $BASE_DIR..."
mkdir -p "$BASE_DIR"

echo "Updating package list and upgrading system..."
sudo apt-get update -y && sudo apt-get upgrade -y

echo "Installing required packages: python3, python3-venv, python3-pip, privoxy, tor, wget..."
sudo apt-get install -y python3 python3-venv python3-pip privoxy tor wget

# Download and place the torrc file
echo "Downloading torrc from $TORRC_URL..."
sudo wget -O "$TORRC_DEST" "$TORRC_URL"

# Download and place the privoxy config file
echo "Downloading privoxy config from $PRIVOXY_CONFIG_URL..."
sudo wget -O "$PRIVOXY_CONFIG_DEST" "$PRIVOXY_CONFIG_URL"

# Download and place the crawler script
echo "Downloading crawler.py from $CRAWLER_SCRIPT_URL..."
wget -O "$CRAWLER_DEST" "$CRAWLER_SCRIPT_URL"

# Download and place the requirements.txt
echo "Downloading requirements.txt from $REQUIREMENTS_URL..."
wget -O "$REQUIREMENTS_DEST" "$REQUIREMENTS_URL"

# Set permissions for crawler.py
echo "Setting permissions for crawler.py..."
chmod 644 "$CRAWLER_DEST"

# Create a Python virtual environment
echo "Creating Python virtual environment in $VENV_DIR..."
python3 -m venv "$VENV_DIR"

# Activate the virtual environment and install requirements
echo "Activating virtual environment and installing requirements..."
source "$VENV_DIR/bin/activate"
pip install --no-cache-dir -r "$REQUIREMENTS_DEST"
deactivate

# Restart services to apply changes
echo "Restarting Tor and Privoxy services..."
sudo systemctl restart tor
sudo systemctl restart privoxy

echo "All files have been placed in $BASE_DIR"
echo "Installation, configuration, and virtual environment setup complete."
