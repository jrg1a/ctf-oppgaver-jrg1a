"""
Generer Sensorstrømmen.

LCG-basert stream cipher med lekkede påfølgende outputs.
Flagg: CTF{lcg_er_ikke_streamkrypto}
"""

from __future__ import annotations

import json
from pathlib import Path


FLAG = "CTF{lcg_er_ikke_streamkrypto}"
M = 2**31 - 1
A = 1103515245
C = 12345
SEED = 0x4B415F26

PLAINTEXT = (
    "Nordverk sensor archive export\n"
    "Channel: demo-partner/tank7\n"
    "Status: simulated\n"
    f"Flag: {FLAG}\n"
).encode()


def lcg_values(seed: int):
    x = seed
    while True:
        x = (A * x + C) % M
        yield x


def keystream_from_values(values, length: int) -> bytes:
    out = bytearray()
    for value in values:
        out.extend(value.to_bytes(4, "big"))
        if len(out) >= length:
            return bytes(out[:length])
    raise RuntimeError("unreachable")


def main() -> None:
    values = lcg_values(SEED)
    leaked = [next(values) for _ in range(4)]
    stream = keystream_from_values(values, len(PLAINTEXT))
    ciphertext = bytes(p ^ k for p, k in zip(PLAINTEXT, stream))
    data = {
        "modulus": M,
        "leaked_consecutive_outputs": leaked,
        "ciphertext_hex": ciphertext.hex(),
        "note": "Outputs after the leaked values were used as XOR keystream, 4 bytes per output, big-endian.",
    }
    out_dir = Path(__file__).parent / "dist"
    out_dir.mkdir(exist_ok=True)
    (out_dir / "sensorstrom.json").write_text(json.dumps(data, indent=2) + "\n")
    print("[+] Skrev dist/sensorstrom.json")
    print(f"[+] a={A}, c={C}, m={M}")
    print(f"[+] Flagg: {FLAG}")


if __name__ == "__main__":
    main()
