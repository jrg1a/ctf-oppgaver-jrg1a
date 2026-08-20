"""
LØSNING — To nøkler, samme modul (ikke gi til deltakerne!)
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


def egcd(a: int, b: int) -> tuple[int, int, int]:
    if b == 0:
        return a, 1, 0
    g, x1, y1 = egcd(b, a % b)
    return g, y1, x1 - (a // b) * y1


def mod_pow_signed(base: int, exponent: int, modulus: int) -> int:
    if exponent >= 0:
        return pow(base, exponent, modulus)
    return pow(pow(base, -1, modulus), -exponent, modulus)


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent.parent / "dist" / "rsa_felles_modulus.json"
    data = json.loads(path.read_text())
    n, e1, e2, c1, c2 = data["n"], data["e1"], data["e2"], data["c1"], data["c2"]
    g, a, b = egcd(e1, e2)
    if g != 1:
        raise SystemExit("e1 og e2 er ikke koprimiske")
    m = (mod_pow_signed(c1, a, n) * mod_pow_signed(c2, b, n)) % n
    plaintext = m.to_bytes((m.bit_length() + 7) // 8, "big")
    print(plaintext.decode())
    match = re.search(rb"CTF\{[^}]+\}", plaintext)
    if match:
        print(f"*** FLAGG: {match.group(0).decode()} ***")
        return 0
    raise SystemExit("Fant ikke flagget")


if __name__ == "__main__":
    raise SystemExit(main())
