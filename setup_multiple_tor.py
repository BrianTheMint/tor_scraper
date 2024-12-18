import os
import subprocess

# Function to check if Tor is installed
def check_tor_installed():
    try:
        subprocess.run(['command', '-v', 'tor'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except subprocess.CalledProcessError:
        return False

# Function to create and start Tor instance
def create_and_start_tor_instance(instance_num, tor_port, control_port, tor_data_dir_base="/var/lib/tor"):
    # Create data directory for this instance
    tor_data_dir = f"{tor_data_dir_base}_instance_{instance_num}"
    os.makedirs(tor_data_dir, exist_ok=True)
    
    # Path for torrc configuration file
    tor_config_file = os.path.join(tor_data_dir, "torrc")

    # Create torrc configuration for the instance
    with open(tor_config_file, "w") as f:
        f.write(f"""# Tor Configuration for Instance {instance_num}

SocksPort {tor_port}
ControlPort {control_port}
DataDirectory {tor_data_dir}
CookieAuthentication 1

# Log settings
Log notice file {tor_data_dir}/tor.log
""")
    
    # Start the Tor instance using the generated config
    print(f"Starting Tor instance {instance_num} on SOCKS5 port {tor_port} and control port {control_port}...")
    subprocess.Popen(['tor', '-f', tor_config_file])

# Main function to configure and run multiple Tor instances
def run_multiple_tor_instances(num_instances=3):
    # Check if Tor is installed
    if not check_tor_installed():
        print("Tor is not installed. Please install Tor first.")
        return

    # Define ports for SOCKS and control ports
    tor_ports = [9050 + i * 2 for i in range(num_instances)]  # Ports like 9050, 9052, 9054, ...
    control_ports = [9051 + i * 2 for i in range(num_instances)]  # Ports like 9051, 9053, 9055, ...

    # Run the Tor instances
    for i in range(num_instances):
        create_and_start_tor_instance(i, tor_ports[i], control_ports[i])

    print(f"\nMultiple Tor instances have been started on the following ports:")
    print(f"SOCKS5 Ports: {tor_ports}")
    print(f"Control Ports: {control_ports}")
    print("You can now use these ports in your scraping script to utilize multiple Tor instances.")

if __name__ == "__main__":
    # Start 3 Tor instances (you can modify the number as needed)
    run_multiple_tor_instances(num_instances=3)
