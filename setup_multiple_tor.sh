#!/bin/bash

# Check if Tor is installed
if ! command -v tor &> /dev/null
then
    echo "Tor could not be found, please install Tor first."
    exit 1
fi

# Define the number of Tor instances you want to run
NUM_INSTANCES=3

# Tor data directory base
TOR_DATA_DIR_BASE="/var/lib/tor"

# Define the ports to use for the Tor instances (9050, 9052, 9054, ...)
TOR_PORTS=(9050 9052 9054)

# Define the control port for each instance (9051, 9053, 9055, ...)
CONTROL_PORTS=(9051 9053 9055)

# Define the socks5 proxy port and control port incrementally
for i in $(seq 0 $((NUM_INSTANCES - 1)))
do
    TOR_PORT=${TOR_PORTS[$i]}
    CONTROL_PORT=${CONTROL_PORTS[$i]}

    # Data directory for this Tor instance
    TOR_DATA_DIR="${TOR_DATA_DIR_BASE}_instance_$i"

    # Create the Tor data directory if it doesn't exist
    if [ ! -d "$TOR_DATA_DIR" ]; then
        mkdir -p "$TOR_DATA_DIR"
    fi

    # Tor configuration file for this instance
    TOR_CONFIG_FILE="$TOR_DATA_DIR/torrc"

    # Create or overwrite the torrc configuration file
    echo "Creating Tor instance configuration for instance $i..."

    cat > "$TOR_CONFIG_FILE" <<EOF
# Tor Configuration for Instance $i

SocksPort $TOR_PORT
ControlPort $CONTROL_PORT
DataDirectory $TOR_DATA_DIR
CookieAuthentication 1

# Log settings (adjust verbosity as needed)
Log notice file $TOR_DATA_DIR/tor.log
EOF

    # Start the Tor instance using the newly created config
    echo "Starting Tor instance $i on port $TOR_PORT with control port $CONTROL_PORT..."
    tor -f "$TOR_CONFIG_FILE" &

    # Wait a bit for the Tor instance to initialize
    sleep 5
done

echo "Multiple Tor instances have been started on the following ports:"
echo "SOCKS5 Ports: ${TOR_PORTS[@]}"
echo "Control Ports: ${CONTROL_PORTS[@]}"

echo "You can now use these ports in your scraping script to utilize multiple Tor instances."
