#!/bin/bash

# Exit on any error
set -e

# Base directory and configuration paths
BASE_DIR="/tor_scraper"
TORRC_DEST="/etc/tor/torrc"
PRIVOXY_CONFIG_DEST="/etc/privoxy/config"

# Stop services before cleanup
echo "Stopping Tor and Privoxy services..."
sudo systemctl stop tor
sudo systemctl stop privoxy

# Remove the base directory and its contents
if [ -d "$BASE_DIR" ]; then
    echo "Removing base directory at $BASE_DIR..."
    sudo rm -rf "$BASE_DIR"
else
    echo "Base directory $BASE_DIR does not exist, skipping..."
fi

# Remove the Tor configuration file
if [ -f "$TORRC_DEST" ]; then
    echo "Removing Tor configuration..."
    sudo rm -f "$TORRC_DEST"
else
    echo "Tor configuration file $TORRC_DEST does not exist, skipping..."
fi

# Remove the Privoxy configuration file
if [ -f "$PRIVOXY_CONFIG_DEST" ]; then
    echo "Removing Privoxy configuration..."
    sudo rm -f "$PRIVOXY_CONFIG_DEST"
else
    echo "Privoxy configuration file $PRIVOXY_CONFIG_DEST does not exist, skipping..."
fi

# Uninstall Tor and Privoxy
echo "Uninstalling Tor and Privoxy..."
sudo apt-get remove --purge -y tor privoxy
sudo apt-get autoremove --purge -y

# Remove any remaining dependencies for Python virtual environment
echo "Removing Python virtual environment and dependencies..."
sudo apt-get remove --purge -y python3-venv python3-pip
sudo apt-get autoremove --purge -y

# Clean up any remaining configuration or cache files
echo "Cleaning up remaining files..."
sudo apt-get clean

# Restart services to apply changes
echo "Restarting remaining services..."
sudo systemctl daemon-reload

echo "Cleanup complete. All files, services, and packages set by the installation script have been removed."
