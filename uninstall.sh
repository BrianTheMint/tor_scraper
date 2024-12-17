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

# Restore default Tor configuration if backup exists
if [ -f "$TORRC_DEST" ]; then
    echo "Restoring default Tor configuration..."
    sudo rm -f "$TORRC_DEST"
    sudo touch "$TORRC_DEST"
else
    echo "Tor configuration file $TORRC_DEST does not exist, skipping..."
fi

# Restore default Privoxy configuration if backup exists
if [ -f "$PRIVOXY_CONFIG_DEST" ]; then
    echo "Restoring default Privoxy configuration..."
    sudo rm -f "$PRIVOXY_CONFIG_DEST"
    sudo touch "$PRIVOXY_CONFIG_DEST"
else
    echo "Privoxy configuration file $PRIVOXY_CONFIG_DEST does not exist, skipping..."
fi

# Restart services to ensure they run with default configurations
echo "Restarting Tor and Privoxy services..."
sudo systemctl restart tor
sudo systemctl restart privoxy

echo "Cleanup complete. All files and configurations set by the installation script have been removed."
