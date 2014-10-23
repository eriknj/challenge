FROM debian:jessie
RUN apt-get update && apt-get install -y python-flask python-pip
RUN pip install docker-py
ADD httpd.py /opt/httpd/httpd.py
EXPOSE 5000
CMD [ "python", "/opt/httpd/httpd.py" ]
