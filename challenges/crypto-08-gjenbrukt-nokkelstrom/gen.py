#!/usr/bin/env python3
"""Generate a two-time-pad style artifact."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


FLAG = "CTF{aldri_gjenbruk_en_nokkelstrom}"
ROOT = Path(__file__).resolve().parent
OUT = ROOT / "dist" / "samband.json"
MESSAGE_LENGTH = 160


def fit_message(text: str) -> bytes:
    filler = " | LOGGDATA=NORMAL"
    while len(text) < MESSAGE_LENGTH:
        text += filler
    return text[:MESSAGE_LENGTH].encode("ascii")


def key_stream(length: int) -> bytes:
    seed = b"nordverk-emergency-radio-counter-zero"
    chunks = []
    counter = 0
    while sum(map(len, chunks)) < length:
        chunks.append(hashlib.sha256(seed + counter.to_bytes(4, "big")).digest())
        counter += 1
    return b"".join(chunks)[:length]


def xor_bytes(left: bytes, right: bytes) -> bytes:
    return bytes(a ^ b for a, b in zip(left, right))


def main() -> None:
    known = fit_message(
        "STATUS: ALLE SYSTEMER NOMINELLE. SKIFT=KVELD. OPERATOER=ANNA."
    )
    secret = fit_message(
        f"VARSEL: NOEDRUTINEN BLE AKTIVERT. KONTROLLKODE={FLAG}."
    )
    stream = key_stream(MESSAGE_LENGTH)

    document = {
        "system": "Nordverk sambandsgateway",
        "cipher": "XOR stream",
        "incident": "Counter reset before packet B",
        "known_plaintext_a": known.decode("ascii"),
        "ciphertext_a_hex": xor_bytes(known, stream).hex(),
        "ciphertext_b_hex": xor_bytes(secret, stream).hex(),
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    print(f"[+] Skrev {OUT}")


if __name__ == "__main__":
    main()

