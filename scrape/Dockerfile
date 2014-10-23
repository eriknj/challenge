FROM debian:jessie
RUN apt-get update && apt-get install -y python-bs4
ADD scrape.py /opt/scrape/scrape.py
ENTRYPOINT [ "python", "/opt/scrape/scrape.py" ]
