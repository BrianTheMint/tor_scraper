FROM ubuntu:latest

RUN apt-get update && apt-get install python3 python3-venv python3-pip tor privoxy -y
COPY privoxy/config:/etc/privoxy/config
COPY torrc:/etc/tor/torrc
RUN python3 -m venv venv
RUN . venv/bin/activate
RUN pip install -r requirements.txt
ENTRYPOINT ["python3", "crawler.py"]
