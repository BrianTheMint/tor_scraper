# tor_scraper | Tested on Ubuntu 24.04 with python 3.12.3
bot based on python to scrape for .onion addresses 
  install dependancies
    sudo apt-get update && sudo apt-get install python3 python3-venv python3-pip privoxy nyx -y

# clone repository
  
    git clone https://github.com/OrlandB2045/tor_scraper.git
    cd tor_scraper

 # You should have the following files
    
      -torrc
      -privoxy/config
      -crawler.py
      -requirements.txt

# Place files in their respective places
    
    cp torrc /etc/tor/torrc
    cp privoxy/config /etc/privoxy/config

# restart tor and privoxy
    
    sudo service restart tor
    sudo service restart privoxy

# create and enter venv
    
    python -m venv venv
    . venv/bin/activate

# install requirements

    pip install -r requirements.txt

# Customize the script!
    Customize as follows 
        OUTPUT_FILE = "onion_sites_with_titles.txt"  # File to store discovered .onion links and titles
        SEED_URLS = ["http://3mcm3cat*****************************f4rnx2ug7ab3ilzvgwfyd.onion/"]  # Replace with the onion you want to crawl
        MAX_DEPTH = 6  # set to the crawl depth you want

# Run The Script!

    python crawler.py
        
