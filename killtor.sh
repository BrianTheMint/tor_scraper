#!/bin/bash

# Script to kill all instances of Tor

# Find all Tor processes and kill them
pkill -f tor

echo "All Tor instances have been killed."