#!/usr/bin/env python3
"""Organizer solver for Registersporet."""

from __future__ import annotations

import base64
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / "dist" / "operatordagbok.txt"


def main() -> None:
    characters = re.findall(
        r"^SPOR\s+\d+\s+\|\s+(.)\s+\|",
        LOG.read_text(encoding="utf-8"),
        re.MULTILINE,
    )
    encoded = "".join(characters)
    decoded = base64.b64decode(encoded).decode("ascii")
    if not re.fullmatch(r"CTF\{[A-Za-z0-9_]+\}", decoded):
        raise SystemExit(f"Uventet dekodet verdi: {decoded!r}")
    print(decoded)


if __name__ == "__main__":
    main()

