FROM python:3.8.10-slim-buster
MAINTAINER Rucon@TUW "josip.zilic@tuwien.ac.at"

RUN apt-get update -y && apt-get install -y --no-install-recommends curl python3-pip python3-dev build-essential && rm -rf /var/lib/apt/lists/*

#Allow pi wheels 
RUN echo "[global]\nextra-index-url=https://www.piwheels.org/simple" >> /etc/pip.conf

#Copy the requirements.txt to leverage Docker cache
COPY docker/requirements.txt /app/requirements.txt
WORKDIR /app

# Upgrade pip and install requirements
RUN pip3 install --upgrade pip; pip3 install --no-cache-dir -r requirements.txt;
COPY app/ /app

EXPOSE 5000
ENTRYPOINT [ "python3" ]
CMD [ "main.py" ]
