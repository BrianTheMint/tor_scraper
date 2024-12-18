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
import argparse
import tkinter as tk
from tkinter import filedialog, messagebox
import threading

# Set up logging
logging.basicConfig(filename="scraper_log.txt", level=logging.INFO, format="%(asctime)s - %(message)s")

# Function to create a requests session that uses a specific Tor instance (SOCKS proxy)
def create_tor_session(tor_port):
    session = requests.Session()
    tor_proxy = f'socks5h://127.0.0.1:{tor_port}'  # Specify the port for each Tor instance
    session.proxies = {
        'http': tor_proxy,
        'https': tor_proxy,
    }

    # Configure retries (fix allowed_methods)
    retry_strategy = Retry(
        total=5,  # Retry up to 5 times
        backoff_factor=2,  # Exponential backoff factor
        status_forcelist=[500, 502, 503, 504],  # Retry on server errors
        allowed_methods=["GET", "POST"],  # Retry only GET and POST requests
    )

    # Attach retry strategy to the session
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    return session

# Function to request a new Tor IP address
def renew_tor_ip(tor_port):
    with Controller.from_port(port=9051) as controller:
        controller.authenticate()  # Authenticate with the Tor Controller
        controller.signal(Signal.NEWNYM)  # Request a new IP address
        time.sleep(5)  # Wait for the new IP to be assigned

# Function to scrape .onion address for the title
def scrape_onion(url, depth, max_depth, visited, writer, text_widget, session):
    if depth > max_depth:
        return  # Stop recursion if max depth is reached

    # Avoid revisiting the same URL
    if url in visited:
        return

    visited.add(url)  # Mark this URL as visited

    try:
        response = session.get(url, timeout=30)  # Increased timeout to 30 seconds
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.title.string if soup.title else "No title"
            log_message = f"Depth {depth} - URL: {url} - Title: {title}"
            logging.info(log_message)
            text_widget.insert(tk.END, log_message + '\n')
            text_widget.yview(tk.END)  # Scroll to the bottom
            print(f"Scraped: Depth {depth} - {url} - Title: {title}")

            # Write the .onion URL and title to the CSV file
            writer.writerow([url, title])

            # Extract and follow links on this page
            links = soup.find_all('a', href=True)
            for link in links:
                next_url = urljoin(url, link['href'])  # Resolve relative URLs
                if next_url.startswith('http'):
                    scrape_onion(next_url, depth + 1, max_depth, visited, writer, text_widget, session)
        else:
            log_message = f"Failed to access {url}, Status Code: {response.status_code}"
            logging.warning(log_message)
            text_widget.insert(tk.END, log_message + '\n')
            text_widget.yview(tk.END)  # Scroll to the bottom
            print(f"Failed to access {url}, Status Code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        log_message = f"Error accessing {url}: {e}"
        logging.error(log_message)
        text_widget.insert(tk.END, log_message + '\n')
        text_widget.yview(tk.END)  # Scroll to the bottom
        print(f"Error accessing {url}: {e}")

# Function to handle the scraping process in a separate thread
def start_scraping(onion_file, max_depth, text_widget, tor_ports):
    visited = set()  # To track visited URLs

    # Open CSV file for writing the results
    with open('scraped_onions.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Write the header row in CSV
        writer.writerow(['.onion URL', 'Page Title'])

        with open(onion_file, 'r') as file:
            onion_addresses = [line.strip() for line in file.readlines()]

        # Loop through onion addresses and use a different Tor instance for each thread
        threads = []
        for i, address in enumerate(onion_addresses):
            tor_port = 9050 + (i % len(tor_ports))  # Cycle through the list of Tor ports
            session = create_tor_session(tor_port)  # Create a new session for this thread
            thread = threading.Thread(target=scrape_onion, args=(address, 1, max_depth, visited, writer, text_widget, session))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

    text_widget.insert(tk.END, "Scraping completed!\n")
    text_widget.yview(tk.END)  # Scroll to the bottom

# Function to load the max depth from a configuration file
def load_max_depth():
    try:
        with open('config.txt', 'r') as config_file:
            return int(config_file.read().strip())  # Read and return the integer value
    except (FileNotFoundError, ValueError):
        return 3  # Return the default value if the file doesn't exist or the value is invalid

# Function to save the max depth to a configuration file
def save_max_depth(max_depth):
    with open('config.txt', 'w') as config_file:
        config_file.write(str(max_depth))  # Save the max depth as a string

# GUI function
def open_file_dialog():
    filename = filedialog.askopenfilename(title="Select .onion URL file", filetypes=[("Text files", "*.txt")])
    if filename:
        onion_file_var.set(filename)

def run_scraping():
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
    start_button.config(state=tk.DISABLED)

    # List of Tor ports to use for multiple instances (e.g., 9050, 9052, 9054, etc.)
    tor_ports = [9050, 9052, 9054]

    # Start scraping in a new thread to keep the GUI responsive
    threading.Thread(target=start_scraping, args=(onion_file, max_depth, text_widget, tor_ports), daemon=True).start()

    # Update the GUI text
    text_widget.insert(tk.END, "Scraping started...\n")
    text_widget.yview(tk.END)  # Scroll to the bottom

# Create the main window
root = tk.Tk()
root.title("Tor .onion Scraper")

# Set window size
root.geometry("700x500")

# Initialize the Tkinter GUI variable with the value read from config.txt (or default to 3)
depth_var = tk.StringVar(value=str(load_max_depth()))  # Initialize depth_var with the saved value

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

# Start the GUI main loop
root.mainloop()
