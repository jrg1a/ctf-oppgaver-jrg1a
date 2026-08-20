#!/usr/bin/env python3
"""Organizer solver for Raymonds RSA."""

from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path


def fermat_factor(n: int) -> tuple[int, int]:
    a = math.isqrt(n)
    if a * a < n:
        a += 1

    while True:
        b2 = a * a - n
        b = math.isqrt(b2)
        if b * b == b2:
            p = a - b
            q = a + b
            if p * q == n:
                return p, q
        a += 1


def main() -> int:
    path = (
        Path(sys.argv[1])
        if len(sys.argv) > 1
        else Path(__file__).resolve().parents[1] / "dist" / "raymond_rsa.json"
    )
    data = json.loads(path.read_text(encoding="utf-8"))
    e, n, c = data["e"], data["n"], data["c"]

    p, q = fermat_factor(n)
    phi = (p - 1) * (q - 1)
    d = pow(e, -1, phi)
    m = pow(c, d, n)
    plaintext = m.to_bytes((m.bit_length() + 7) // 8, "big")
    print(plaintext.decode())

    match = re.search(rb"CTF\{[^}]+\}", plaintext)
    if match:
        print(f"*** FLAGG: {match.group(0).decode()} ***")
        return 0
    raise SystemExit("Fant ikke flagg")


if __name__ == "__main__":
    raise SystemExit(main())
