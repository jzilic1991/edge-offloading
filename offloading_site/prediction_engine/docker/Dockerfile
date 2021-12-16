FROM python:3.7-slim-buster
MAINTAINER Rucon@TUW "josip.zilic@tuwien.ac.at"

WORKDIR /app
COPY app/ /app
COPY docker/requirements.txt /app/requirements.txt
RUN echo "[global]\nextra-index-url=https://www.piwheels.org/simple" >> /etc/pip.conf 
RUN apt-get update -y && apt-get install -y --no-install-recommends curl libglu1 libaio1 libaio-dev libjbig0 liblcms2-2 libopenjp2-7 libtiff5 libwebp6 libwebpdemux2 libwebpmux3 python3-pip python3-dev build-essential libatlas3-base libgfortran5 && rm -rf /var/lib/apt/lists/*
RUN pip3 install --upgrade pip && pip3 install --no-cache-dir -r requirements.txt -v

EXPOSE 8001
CMD [ "python", "-u", "main.py" ]
