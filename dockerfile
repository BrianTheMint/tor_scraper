# Use the official Ubuntu image
FROM ubuntu:latest

# Install required packages (Python, Tor, Privoxy, and dependencies)
RUN apt-get update && apt-get install -y \
    python3 python3-venv python3-pip tor privoxy \
    python3-bs4 python3-certifi python3-charset-normalizer \
    python3-idna python3-socks python3-requests python3-soupsieve \
    python3-stem python3-urllib3

# Create the crawler directory
RUN mkdir -p /crawler

# Set the working directory to /crawler
WORKDIR /crawler

# Copy the configuration files and the Python script
COPY privoxy/config /etc/privoxy/config
COPY torrc /etc/tor/torrc
COPY crawler.py /home/crawler.py
WORKDIR /home

# Set the correct permissions for the Python script
RUN chmod 644 /home/crawler.py

# Expose necessary ports (Privoxy and Tor)
EXPOSE 8118 9050

# Start Tor and Privoxy, then run the Python crawler script (using JSON array format)
CMD ["sh", "-c", "service privoxy start && service tor start && python3 /home/crawler.py"]
