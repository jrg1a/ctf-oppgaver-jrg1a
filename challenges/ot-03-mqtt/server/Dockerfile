FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    mosquitto \
    mosquitto-clients \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir paho-mqtt==1.6.1

RUN mkdir -p /mosquitto/config /mosquitto/data /mosquitto/log

WORKDIR /app
COPY mosquitto.conf acl.conf publisher.py entrypoint.sh ./
RUN chmod +x entrypoint.sh

EXPOSE 1883

ENTRYPOINT ["/app/entrypoint.sh"]
