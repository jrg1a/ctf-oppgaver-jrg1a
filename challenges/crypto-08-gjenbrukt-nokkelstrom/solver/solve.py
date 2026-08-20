#!/usr/bin/env python3
"""Organizer solver for Samme strøm to ganger."""

from __future__ import annotations

import json
import re
from pathlib import Path


ARTIFACT = Path(__file__).resolve().parents[1] / "dist" / "samband.json"


def xor_bytes(left: bytes, right: bytes) -> bytes:
    return bytes(a ^ b for a, b in zip(left, right))


def main() -> None:
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    known = data["known_plaintext_a"].encode("ascii")
    cipher_a = bytes.fromhex(data["ciphertext_a_hex"])
    cipher_b = bytes.fromhex(data["ciphertext_b_hex"])

    stream = xor_bytes(known, cipher_a)
    plaintext = xor_bytes(cipher_b, stream).decode("ascii")
    match = re.search(r"CTF\{[A-Za-z0-9_]+\}", plaintext)
    if not match:
        raise SystemExit(f"Fant ikke flagg i dekryptert tekst: {plaintext!r}")
    print(match.group(0))


if __name__ == "__main__":
    main()

