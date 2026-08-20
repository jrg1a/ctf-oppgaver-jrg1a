"""
MQTT publisher — simulerer OT-anleggsdata og lekker credentials.
Kjører som bakgrunnsprosess i containeren ved siden av mosquitto.
"""

import time
import random
import json
import paho.mqtt.client as mqtt

BROKER   = "localhost"
PORT     = 1883
CLIENT_ID = "plant-publisher"

# Operator-credentials (lekkes på debug-topic)
OPERATOR_USER = "operator"
OPERATOR_PASS = "Pl4tform42!"

FLAG = "CTF{mqtt_w1ldcard_cr3d_l3ak}"


def connect():
    c = mqtt.Client(client_id=CLIENT_ID, protocol=mqtt.MQTTv311)
    c.username_pw_set(OPERATOR_USER, OPERATOR_PASS)
    c.connect(BROKER, PORT, keepalive=60)
    c.loop_start()
    return c


def main():
    time.sleep(2)   # Vent på at mosquitto starter
    client = connect()
    print("[publisher] Tilkoblet MQTT-broker, starter datapublisering...")

    tick = 0
    while True:
        # --- Sensor-data (støy) ---
        client.publish("plant/sensor/temperature",
            json.dumps({"value": round(random.uniform(68.0, 72.0), 2), "unit": "C"}), retain=False)

        client.publish("plant/sensor/pressure",
            json.dumps({"value": round(random.uniform(195.0, 205.0), 1), "unit": "bar"}), retain=False)

        client.publish("plant/sensor/flow_rate",
            json.dumps({"value": round(random.uniform(48.0, 52.0), 2), "unit": "m3/h"}), retain=False)

        client.publish("plant/sensor/vibration_pump_01",
            json.dumps({"value": round(random.uniform(1.1, 1.9), 3), "unit": "mm/s"}), retain=False)

        # --- Alarm-status ---
        client.publish("plant/alarm/high_temp",    "NORMAL",      retain=False)
        client.publish("plant/alarm/high_pressure", "NORMAL",     retain=False)
        client.publish("plant/alarm/esd_status",   "ARMED",       retain=False)

        # --- Systemstatus ---
        client.publish("plant/system/heartbeat",
            json.dumps({"ts": int(time.time()), "uptime_h": round(tick * 3 / 3600, 1)}), retain=False)
        client.publish("plant/system/mode", "PRODUCTION", retain=False)

        # --- Debug-topic: lekker credentials (realistisk OT-feil) ---
        # Publiseres hvert 15. sekund — nok til at deltakerne ser det
        if tick % 5 == 0:
            client.publish("plant/maintenance/debug",
                json.dumps({
                    "msg": "Scheduled credential sync",
                    "service": "SCADA-HMI-bridge",
                    "user": OPERATOR_USER,
                    "pass": OPERATOR_PASS,
                    "note": "TODO: flytt til vault før produksjon"
                }), retain=False)

        # --- Sikret styretopic: flagget (kun tilgjengelig med operator-creds) ---
        client.publish("plant/control/secure",
            json.dumps({
                "status": "ACTIVE",
                "setpoint_pressure": 200,
                "flag": FLAG,
                "auth_required": True
            }), retain=False)

        tick += 1
        time.sleep(3)


if __name__ == "__main__":
    main()
