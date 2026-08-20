"""
Brønnplattform MQTT — Startpunkt
==================================
Installer avhengigheter:
  pip install paho-mqtt==1.6.1

Bruk:
  python mqtt_recon.py <IP> [PORT]

Dette scriptet kobler til MQTT-brokeren og lytter på ALLE topics
i 30 sekunder. Analyser hva du ser — noe er ikke som det skal.
"""

import sys
import time
import json
import paho.mqtt.client as mqtt

TARGET_IP   = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
TARGET_PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 1883
LISTEN_SECS = 30


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"[+] Tilkoblet {TARGET_IP}:{TARGET_PORT}")
        client.subscribe("#")   # Wildcard — abonner på ALLE topics
        print(f"[*] Lytter på alle topics i {LISTEN_SECS} sekunder...\n")
    else:
        print(f"[-] Tilkobling feilet, kode: {rc}")


def on_message(client, userdata, msg):
    topic   = msg.topic
    payload = msg.payload.decode("utf-8", errors="replace")

    # Prøv å parse JSON for lesbarhet
    try:
        data = json.loads(payload)
        payload_str = json.dumps(data, ensure_ascii=False)
    except Exception:
        payload_str = payload

    print(f"  [{topic}]  {payload_str}")


def main():
    client = mqtt.Client(protocol=mqtt.MQTTv311)
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(TARGET_IP, TARGET_PORT, keepalive=60)
    client.loop_start()

    time.sleep(LISTEN_SECS)
    client.loop_stop()
    client.disconnect()
    print("\n[*] Ferdig. Hva fant du?")


if __name__ == "__main__":
    main()
