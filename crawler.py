import requests
from bs4 import BeautifulSoup
from stem import Signal
from stem.control import Controller
import time
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from urllib.parse import urljoin

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

# Configure retries (fix the method_whitelist to allowed_methods)
retry_strategy = Retry(
    total=5,  # Retry up to 5 times
    backoff_factor=1,  # Exponential backoff factor
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
def scrape_onion(url, depth, max_depth, visited):
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
            
            # Extract and follow links on this page
            links = soup.find_all('a', href=True)
            for link in links:
                next_url = urljoin(url, link['href'])  # Resolve relative URLs
                if next_url.startswith('http'):
                    scrape_onion(next_url, depth + 1, max_depth, visited)
        else:
            logging.warning(f"Failed to access {url}, Status Code: {response.status_code}")
            print(f"Failed to access {url}, Status Code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error accessing {url}: {e}")
        print(f"Error accessing {url}: {e}")

# Main function to read .onion addresses and scrape
def main():
    # Define max depth and .onion URLs directly in the script
    max_depth = 6  # Set the desired max depth here
    onion_addresses = [
        "http://3mcm3cathoi5eahjeq7e5tgessfktszioxyf4rnx2ug7ab3ilzvgwfyd.onion/",  # Replace with actual .onion URLs
        "http://t3g5mz7kgivhgzua64vxmu7ieyyoyzgd423itqjortjhh64lcvspyayd.onion/",
        "http://dreadytofatroptsdj6io7l3xptbet6onoyno2yv7jicoxknyazubrad.onion/search/?p=4&q=gore&fuzziness=auto"
    ]
    
    visited = set()  # To track visited URLs
    
    for address in onion_addresses:
        scrape_onion(address, 1, max_depth, visited)
        
        # Optionally, renew the Tor IP after each request to avoid being tracked
        renew_tor_ip()

if __name__ == "__main__":
    main()
