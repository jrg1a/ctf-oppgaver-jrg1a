#!/usr/bin/env python3
from __future__ import annotations

import struct
import zlib
from pathlib import Path


def read_png(path: Path) -> tuple[int, int, bytes]:
    data = path.read_bytes()
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError("not a PNG")

    pos = 8
    width = height = 0
    idat = bytearray()
    while pos < len(data):
        length = struct.unpack(">I", data[pos : pos + 4])[0]
        kind = data[pos + 4 : pos + 8]
        payload = data[pos + 8 : pos + 8 + length]
        pos += 12 + length

        if kind == b"IHDR":
            width, height, bit_depth, color_type, *_ = struct.unpack(">IIBBBBB", payload)
            if bit_depth != 8 or color_type != 2:
                raise ValueError("expected 8-bit RGB PNG")
        elif kind == b"IDAT":
            idat.extend(payload)
        elif kind == b"IEND":
            break

    return width, height, zlib.decompress(bytes(idat))


def main() -> None:
    path = Path(__file__).resolve().parents[1] / "dist" / "skilt.png"
    width, height, raw = read_png(path)

    bits: list[int] = []
    for y in range(height):
        row_start = y * (1 + width * 3)
        if raw[row_start] != 0:
            raise ValueError("unexpected PNG filter")
        for x in range(width):
            blue = raw[row_start + 1 + x * 3 + 2]
            bits.append(blue & 1)

    def take_byte(offset: int) -> int:
        value = 0
        for bit in bits[offset : offset + 8]:
            value = (value << 1) | bit
        return value

    length = 0
    for index in range(4):
        length = (length << 8) | take_byte(index * 8)

    message = bytes(take_byte(32 + index * 8) for index in range(length))
    print(message.decode("ascii"))


if __name__ == "__main__":
    main()
