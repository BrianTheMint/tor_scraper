# Tor Scraper | Tested on Ubuntu 24.04 with python 3.12.3
Bot written in Python to crawl the given onionsite(s) for any .onion address and qurys them for a title, outputting to a text file

# AUTOMATIC INSTALL
  Only known working on Ubuntu 24.04

    sudo apt install curl wget -y
    curl https://raw.githubusercontent.com/BrianTheMint/tor_scraper/refs/heads/main/setup_torscraper.sh | sudo bash
  
   
# MANUAL INSTALL
  
  
  install dependancies
  
    sudo apt-get update && sudo apt-get install python3 python3-venv python3-pip privoxy nyx -y

# UNINSTALL 

    curl https://raw.githubusercontent.com/BrianTheMint/tor_scraper/refs/heads/main/uninstall.sh | sudo bash

# Clone Repository
  
    git clone https://github.com/OrlandB2045/tor_scraper.git
    cd tor_scraper

 # You Should have the Following Files
    
      -torrc
      -privoxy/config
      -crawler.py
      -requirements.txt

# Place Files in Their Respective Locations
    
    cp torrc /etc/tor/torrc
    cp privoxy/config /etc/privoxy/config

# Restart Tor and Privoxy
    
    sudo service restart tor
    sudo service restart privoxy

# Use Nyx to Make Sure Tor is Running Correctly

    sudo nyx
    Ctrl+C to escape
# Create and Enter venv
    
    python -m venv venv
    . venv/bin/activate

# Install Requirements

    pip install -r requirements.txt

# Customize the Script!

    Customize as follows 
        OUTPUT_FILE = "onion_sites_with_titles.txt"  # File to store discovered .onion links and titles
        SEED_URLS = ["http://3mcm3cat*****************************f4rnx2ug7ab3ilzvgwfyd.onion/"]  # Replace with the onion you want to crawl
        MAX_DEPTH = 6  # set to the crawl depth you want

# Run The Script!

    python crawler.py



# Docker Install Instructions

    git clone https://github.com/BrianTheMint/tor_scraper.git
    cd tor_scraper
    docker-compose up -d

# Dockerfile is included
  
        
