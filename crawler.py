import requests
from bs4 import BeautifulSoup
from stem import Signal
from stem.control import Controller
import time
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from urllib.parse import urljoin
import csv
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import subprocess
import json
import os

# Set up logging
logging.basicConfig(filename="scraper_log.txt", level=logging.INFO, format="%(asctime)s - %(message)s")

# JSON file to store the max depth value and Tor proxy settings
CONFIG_FILE = "config.json"

# Function to load configuration from JSON file
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {"max_depth": 3, "tor_proxies": ["socks5h://127.0.0.1:9050", "socks5h://127.0.0.1:9051", "socks5h://127.0.0.1:9052", "socks5h://127.0.0.1:9053"]}

# Function to save configuration to JSON file
def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)

# Function to start Tor instances
def start_tor_instances():
    home_dir = os.path.expanduser("~")
    torrc_files = [os.path.join(home_dir, f"torrc{i}") for i in range(4)]
    for i, torrc in enumerate(torrc_files):
        with open(torrc, "w") as f:
            f.write(f"SocksPort 905{i}\nDataDirectory {home_dir}/.tor{i}")
        subprocess.Popen(["tor", "-f", torrc])

# Function to switch Tor proxies in a round-robin fashion
class TorProxyManager:
    def __init__(self, proxies):
        self.proxies = proxies
        self.index = 0

    def get_next_proxy(self):
        proxy = self.proxies[self.index]
        self.index = (self.index + 1) % len(self.proxies)
        return proxy

# Load configuration and start Tor instances
config = load_config()
start_tor_instances()
proxy_manager = TorProxyManager(config["tor_proxies"])

# Function to make a request using the next Tor proxy
def make_request(url, proxy):
    session = requests.Session()
    session.proxies = {"http": proxy, "https": proxy}
    retry = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    response = session.get(url)
    return response

# Function to load max depth from JSON file
def load_max_depth():
    return config.get("max_depth", 3)

# Function to save max depth to JSON file
def save_max_depth(value):
    config["max_depth"] = value
    save_config(config)

# Function to request a new Tor IP address
def renew_tor_ip(port):
    with Controller.from_port(port=port) as controller:
        controller.authenticate()  # Authenticate with the Tor Controller
        controller.signal(Signal.NEWNYM)  # Request a new IP address
        time.sleep(5)  # Wait for the new IP to be assigned

# Function to scrape .onion address for the title
def scrape_onion(url, depth, max_depth, visited, writer, text_widget, proxy):
    if depth > max_depth or stop_scraping_flag.is_set():
        return  # Stop recursion if max depth is reached or stop flag is set

    # Avoid revisiting the same URL
    if url in visited:
        return

    visited.add(url)  # Mark this URL as visited

    try:
        response = make_request(url, proxy)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.title.string if soup.title else "No title"
            log_message = f"Depth {depth} - URL: {url} - Title: {title}"
            logging.info(log_message)
            text_widget.insert(tk.END, log_message + '\n')
            text_widget.yview(tk.END)  # Scroll to the bottom
            print(f"Scraped: Depth {depth} - {url} - Title: {title}")

            for link in soup.find_all("a"):
                href = link.get("href")
                if href and href.startswith("http"):
                    scrape_onion(href, depth + 1, max_depth, visited, writer, text_widget, proxy)
    except Exception as e:
        logging.error(f"Error scraping {url}: {e}")
        text_widget.insert(tk.END, f"Error scraping {url}: {e}\n")
        text_widget.yview(tk.END)  # Scroll to the bottom

# Function to open the Tor proxy settings window
def open_tor_proxy_settings():
    def save_tor_proxy_settings():
        ip_port = ip_port_entry.get()
        config["tor_proxy"] = f"socks5h://{ip_port}"
        save_config(config)
        settings_window.destroy()
        messagebox.showinfo("Settings Saved", "Tor proxy settings have been saved. Please restart the application for changes to take effect.")

    settings_window = tk.Toplevel(root)
    settings_window.title("Tor Proxy Settings")
    settings_window.geometry("300x200")

    ip_port_label = tk.Label(settings_window, text="SOCKS5 IP:PORT:")
    ip_port_label.pack(pady=5)
    ip_port_entry = tk.Entry(settings_window)
    ip_port_entry.pack(pady=5)
    ip_port_entry.insert(0, config.get("tor_proxy", "socks5h://127.0.0.1:9050").split("//")[1])

    save_button = tk.Button(settings_window, text="Save", command=save_tor_proxy_settings)
    save_button.pack(pady=20)

# Function to handle the scraping process in a separate thread
def start_scraping(onion_file, max_depth, text_widget):
    visited = set()  # To track visited URLs

    # Open CSV file for writing the results
    with open('scraped_onions.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Write the header row in CSV
        writer.writerow(['.onion URL', 'Page Title'])

        with open(onion_file, 'r') as file:
            onion_addresses = [line.strip() for line in file.readlines()]

        threads = []
        for address in onion_addresses:
            if stop_scraping_flag.is_set():
                break
            proxy = proxy_manager.get_next_proxy()
            thread = threading.Thread(target=scrape_onion, args=(address, 1, max_depth, visited, writer, text_widget, proxy))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

    text_widget.insert(tk.END, "Scraping completed!\n")
    text_widget.yview(tk.END)  # Scroll to the bottom
    start_button.config(text="Start Scraping", state=tk.NORMAL)  # Reset button text and state

# GUI function
def open_file_dialog():
    filename = filedialog.askopenfilename(title="Select .onion URL file", filetypes=[("Text files", "*.txt")])
    if filename:
        onion_file_var.set(filename)

def run_scraping():
    if start_button.config('text')[-1] == 'Start Scraping':
        onion_file = onion_file_var.get()
        if not onion_file:
            messagebox.showerror("Error", "Please select a valid .onion URL file.")
            return

        try:
            max_depth = int(depth_var.get())
            if max_depth < 1:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid integer for depth.")
            return

        # Save the max depth for future sessions
        save_max_depth(max_depth)

        # Disable the button to prevent multiple clicks
        start_button.config(text="Stop Scraping", state=tk.NORMAL)

        # Clear the stop flag
        stop_scraping_flag.clear()

        # Start scraping in a new thread to keep the GUI responsive
        threading.Thread(target=start_scraping, args=(onion_file, max_depth, text_widget), daemon=True).start()

        # Update the GUI text
        text_widget.insert(tk.END, "Scraping started...\n")
        text_widget.yview(tk.END)  # Scroll to the bottom
    else:
        stop_scraping_flag.set()
        start_button.config(text="Start Scraping", state=tk.NORMAL)

# Function to call setup_multiple_tor.py
def setup_multiple_tor():
    subprocess.Popen(['python3', 'setup_multiple_tor.py'])

# Function to close all Tor instances
def close_all_tor_instances():
    subprocess.Popen(['pkill', 'tor'])

# Create the main window
root = tk.Tk()
root.title("Tor .onion Scraper")

# Set window size (25% bigger)
root.geometry("875x625")

# Create a menu bar
menu_bar = tk.Menu(root)
root.config(menu=menu_bar)

# Create a File menu and add it to the menu bar
file_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="File", menu=file_menu)

# Add a Quit option to the File menu
file_menu.add_command(label="Quit", command=root.quit)

# Initialize the Tkinter GUI variable with the value read from config.json (or default to 3)
depth_var = tk.StringVar(value=str(load_max_depth()))

# Update the JSON file when the depth_var changes
def on_depth_change(*args):
    save_max_depth(depth_var.get())

depth_var.trace_add("write", on_depth_change)

# File selection section
file_frame = tk.Frame(root)
file_frame.pack(pady=10)

onion_file_var = tk.StringVar()

file_label = tk.Label(file_frame, text="Select .onion URL file:")
file_label.pack(pady=5)

file_button = tk.Button(file_frame, text="Browse", command=open_file_dialog)
file_button.pack(side=tk.TOP)

file_path_label = tk.Label(file_frame, textvariable=onion_file_var, width=40)
file_path_label.pack(side=tk.LEFT, padx=5)

# Max depth section
depth_frame = tk.Frame(root)
depth_frame.pack(pady=10)

depth_label = tk.Label(depth_frame, text="Max Depth:")
depth_label.pack(side=tk.TOP, padx=5)

depth_entry = tk.Entry(depth_frame, textvariable=depth_var, width=10)
depth_entry.pack(side=tk.LEFT)

# Start button
start_button = tk.Button(root, text="Start Scraping", command=run_scraping)
start_button.pack(pady=20)

# Text widget to show logs
text_frame = tk.Frame(root)
text_frame.pack(pady=10)

text_widget = tk.Text(text_frame, height=15, width=80)
text_widget.pack()

# Frame for Tor control buttons
tor_control_frame = tk.Frame(root)
tor_control_frame.pack(pady=10)

# Setup Tor button
setup_tor_button = tk.Button(tor_control_frame, text="Setup Tor Instance", command=setup_multiple_tor)
setup_tor_button.pack(side=tk.LEFT, padx=10)

# Close Tor button centered
close_tor_button = tk.Button(tor_control_frame, text="Close Tor Instances", command=close_all_tor_instances)
close_tor_button.pack(side=tk.LEFT, padx=10)

# Flag to control stopping scraping
stop_scraping_flag = threading.Event()

# Start the GUI main loop
root.mainloop()
