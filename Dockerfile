FROM python:3.5.2
MAINTAINER Kyle P. Johnson "kyle@kyle-p-johnson.com"

# Setup
EXPOSE 5000
RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential

COPY . /app
WORKDIR /app

# Install API requirements
RUN pip install -r requirements.txt

# Install necessary corpora
RUN python install_corpora.py

CMD gunicorn -w 4 -b 0.0.0.0:5000 app:app
