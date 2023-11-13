FROM selenium/standalone-chrome:latest
RUN sudo apt-get update
RUN sudo apt-get install -y python3-pip
RUN pwd
COPY scraper /scraper
COPY requirements.txt /requirements.txt
# CMD ["pip", "install", "requirements.txt"]
