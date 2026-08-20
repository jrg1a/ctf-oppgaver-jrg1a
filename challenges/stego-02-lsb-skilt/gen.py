#!/usr/bin/env python3
from __future__ import annotations

import binascii
import struct
import zlib
from pathlib import Path


FLAG = b"CTF{lsb_i_bla_kanalen}"
WIDTH = 180
HEIGHT = 90


def chunk(kind: bytes, data: bytes) -> bytes:
    crc = binascii.crc32(kind + data) & 0xFFFFFFFF
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", crc)


def bits_from_payload(payload: bytes) -> list[int]:
    framed = struct.pack(">I", len(payload)) + payload
    return [(byte >> shift) & 1 for byte in framed for shift in range(7, -1, -1)]


def main() -> None:
    out = Path(__file__).resolve().parent / "dist" / "skilt.png"
    out.parent.mkdir(parents=True, exist_ok=True)

    raw = bytearray()
    for y in range(HEIGHT):
        raw.append(0)
        for x in range(WIDTH):
            r = 34 + (x * 3 + y) % 32
            g = 94 + (x + y * 2) % 44
            b = 150 + (x * 5 + y * 7) % 70
            raw.extend((r, g, b))

    bits = bits_from_payload(FLAG)
    if len(bits) > WIDTH * HEIGHT:
        raise ValueError("image is too small for payload")

    for index, bit in enumerate(bits):
        row = index // WIDTH
        col = index % WIDTH
        blue_offset = row * (1 + WIDTH * 3) + 1 + col * 3 + 2
        raw[blue_offset] = (raw[blue_offset] & 0xFE) | bit

    ihdr = struct.pack(">IIBBBBB", WIDTH, HEIGHT, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", zlib.compress(bytes(raw), level=9))
    png += chunk(b"IEND", b"")
    out.write_bytes(png)


if __name__ == "__main__":
    main()
