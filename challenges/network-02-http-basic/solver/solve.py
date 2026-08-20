#!/usr/bin/env python3
from __future__ import annotations

import base64
import re
from pathlib import Path


def main() -> None:
    path = Path(__file__).resolve().parents[1] / "dist" / "basic_auth.pcap"
    data = path.read_bytes()
    matches = re.findall(rb"Authorization: Basic ([A-Za-z0-9+/=]+)", data)
    if not matches:
        raise SystemExit("Authorization header not found")

    for candidate in matches:
        credentials = base64.b64decode(candidate).decode()
        _username, password = credentials.split(":", 1)
        if password.startswith("CTF{"):
            print(password)
            return

    raise SystemExit("No flag-looking Basic Auth password found")


if __name__ == "__main__":
    main()
