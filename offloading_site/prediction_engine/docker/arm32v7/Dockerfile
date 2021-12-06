FROM python:3.6.15-slim-buster
MAINTAINER Rucon@TUW "josip.zilic@tuwien.ac.at"

RUN apt-get update -y && apt-get install -y --no-install-recommends curl python3-pip python3-dev python3-numpy python3-scipy build-essential && rm -rf /var/lib/apt/lists/*

#Allow pi wheels 
RUN echo "[global]\nextra-index-url=https://www.piwheels.org/simple" >> /etc/pip.conf

#Copy the requirements.txt to leverage Docker cache
COPY docker/arm32v7/requirements.txt /app/requirements.txt
WORKDIR /app

# Upgrade pip and install requirements
RUN pip3 install --upgrade pip; pip3 install --no-cache-dir -r requirements.txt;
COPY app/ /app

EXPOSE 8001
CMD [ "python", "-u", "main.py" ]
