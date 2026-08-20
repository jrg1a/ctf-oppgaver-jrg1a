"""
LØSNING — Sensorstrømmen (ikke gi til deltakerne!)
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


def recover_lcg_params(outputs: list[int], modulus: int) -> tuple[int, int]:
    x0, x1, x2 = outputs[:3]
    a = ((x2 - x1) * pow((x1 - x0) % modulus, -1, modulus)) % modulus
    c = (x1 - a * x0) % modulus
    if (a * x2 + c) % modulus != outputs[3]:
        raise ValueError("Parameterne verifiserte ikke mot fjerde output")
    return a, c


def lcg_values(seed: int, a: int, c: int, modulus: int):
    x = seed
    while True:
        x = (a * x + c) % modulus
        yield x


def keystream(values, length: int) -> bytes:
    out = bytearray()
    for value in values:
        out.extend(value.to_bytes(4, "big"))
        if len(out) >= length:
            return bytes(out[:length])
    raise RuntimeError("unreachable")


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent.parent / "dist" / "sensorstrom.json"
    data = json.loads(path.read_text())
    modulus = data["modulus"]
    leaked = data["leaked_consecutive_outputs"]
    ciphertext = bytes.fromhex(data["ciphertext_hex"])
    a, c = recover_lcg_params(leaked, modulus)
    print(f"[+] a={a}")
    print(f"[+] c={c}")
    values = lcg_values(leaked[-1], a, c, modulus)
    stream = keystream(values, len(ciphertext))
    plaintext = bytes(x ^ y for x, y in zip(ciphertext, stream))
    print(plaintext.decode())
    match = re.search(rb"CTF\{[^}]+\}", plaintext)
    if match:
        print(f"*** FLAGG: {match.group(0).decode()} ***")
        return 0
    raise SystemExit("Fant ikke flagget")


if __name__ == "__main__":
    raise SystemExit(main())
