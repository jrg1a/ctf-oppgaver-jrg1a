#!/bin/sh
set -e

# Kopier konfig-filer til riktig sted
cp /app/mosquitto.conf /mosquitto/config/mosquitto.conf
cp /app/acl.conf       /mosquitto/config/acl.conf

# Generer passord-fil og sett lesbare rettigheter
mosquitto_passwd -b -c /mosquitto/config/passwd operator "Pl4tform42!"
chmod 644 /mosquitto/config/passwd
chmod 644 /mosquitto/config/acl.conf

# Start mosquitto i bakgrunnen (som root for å unngå permission-problemer i CTF)
mosquitto -c /mosquitto/config/mosquitto.conf &

# Vent til mosquitto er klar
sleep 2

# Start MQTT publisher
python3 /app/publisher.py
