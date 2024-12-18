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

# Set up logging
logging.basicConfig(filename="scraper_log.txt", level=logging.INFO, format="%(asctime)s - %(message)s")

# Tor and Privoxy settings
TOR_PROXY = 'socks5h://127.0.0.1:9050'  # Tor default SOCKS proxy
PRIVOXY_PROXY = 'http://127.0.0.1:8118'  # Privoxy default HTTP proxy

# Configure the requests session to use Privoxy via Tor
session = requests.Session()
session.proxies = {
    'http': PRIVOXY_PROXY,
    'https': PRIVOXY_PROXY,
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

# Function to request a new Tor IP address
def renew_tor_ip():
    with Controller.from_port(port=9051) as controller:
        controller.authenticate()  # Authenticate with the Tor Controller
        controller.signal(Signal.NEWNYM)  # Request a new IP address
        time.sleep(5)  # Wait for the new IP to be assigned

# Function to scrape .onion address for the title
def scrape_onion(url, depth, max_depth, visited, writer):
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
            logging.info(f"Depth {depth} - URL: {url} - Title: {title}")
            print(f"Scraped: Depth {depth} - {url} - Title: {title}")

            # Write the .onion URL and title to the CSV file
            writer.writerow([url, title])

            # Extract and follow links on this page
            links = soup.find_all('a', href=True)
            for link in links:
                next_url = urljoin(url, link['href'])  # Resolve relative URLs
                if next_url.startswith('http'):
                    scrape_onion(next_url, depth + 1, max_depth, visited, writer)
        else:
            logging.warning(f"Failed to access {url}, Status Code: {response.status_code}")
            print(f"Failed to access {url}, Status Code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error accessing {url}: {e}")
        print(f"Error accessing {url}: {e}")

# Main function to read .onion addresses from a file and scrape
def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Scrape .onion websites via Tor.")
    parser.add_argument("onion_file", help="Path to a text file containing .onion URLs")
    parser.add_argument("--max_depth", type=int, default=3, help="Maximum depth to scrape")
    args = parser.parse_args()

    # Read .onion URLs from the file
    try:
        with open(args.onion_file, 'r') as file:
            onion_addresses = [line.strip() for line in file.readlines()]
    except FileNotFoundError:
        print(f"Error: The file {args.onion_file} was not found.")
        return

    visited = set()  # To track visited URLs

    # Open CSV file for writing the results
    with open('scraped_onions.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Write the header row in CSV
        writer.writerow(['.onion URL', 'Page Title'])

        for address in onion_addresses:
            scrape_onion(address, 1, args.max_depth, visited, writer)

            # Optionally, renew the Tor IP after each request to avoid being tracked
            renew_tor_ip()

if __name__ == "__main__":
    main()
