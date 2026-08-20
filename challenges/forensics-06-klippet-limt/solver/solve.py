#!/usr/bin/env python3
"""Organizer solver for Klippet og limt."""

from __future__ import annotations

import re
import struct
import zlib
from pathlib import Path


ARTIFACT = Path(__file__).resolve().parents[1] / "dist" / "utklipp.bin"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def find_all(data: bytes, needle: bytes) -> list[int]:
    offsets: list[int] = []
    start = 0
    while True:
        found = data.find(needle, start)
        if found == -1:
            return offsets
        offsets.append(found)
        start = found + 1


def infer_layout(data: bytes) -> tuple[int, int]:
    offsets = find_all(data, PNG_SIGNATURE)
    if len(offsets) < 2 or offsets[0] != 0:
        raise SystemExit("Fant ikke nok PNG signaturer til aa finne layout")

    block_size = offsets[1] - offsets[0]
    streams = 1
    while streams < len(offsets) and offsets[streams] == streams * block_size:
        streams += 1

    if streams < 2:
        raise SystemExit("Klarte ikke aa tolke sammenflettingen")
    return block_size, streams


def png_end(data: bytes) -> int:
    pos = len(PNG_SIGNATURE)
    while pos + 12 <= len(data):
        length = struct.unpack(">I", data[pos:pos + 4])[0]
        chunk_type = data[pos + 4:pos + 8]
        chunk_end = pos + 12 + length
        if chunk_end > len(data):
            break
        if chunk_type == b"IEND":
            return chunk_end
        pos = chunk_end
    raise ValueError("Fant ikke IEND")


def deinterleave(blob: bytes, block_size: int, streams: int) -> list[bytes]:
    recovered = [bytearray() for _ in range(streams)]
    group_size = block_size * streams

    for group_start in range(0, len(blob), group_size):
        group = blob[group_start:group_start + group_size]
        for index in range(streams):
            start = index * block_size
            recovered[index].extend(group[start:start + block_size])

    return [bytes(data[:png_end(data)]) for data in recovered]


def ztxt_values(png: bytes, keyword: str) -> list[str]:
    values: list[str] = []
    pos = len(PNG_SIGNATURE)
    while pos + 12 <= len(png):
        length = struct.unpack(">I", png[pos:pos + 4])[0]
        chunk_type = png[pos + 4:pos + 8]
        payload = png[pos + 8:pos + 8 + length]
        pos += 12 + length

        if chunk_type != b"zTXt":
            continue
        key, sep, rest = payload.partition(b"\x00")
        if not sep or key.decode("latin-1") != keyword:
            continue
        if not rest or rest[0] != 0:
            continue
        values.append(zlib.decompress(rest[1:]).decode("utf-8"))
    return values


def main() -> None:
    blob = ARTIFACT.read_bytes()
    block_size, streams = infer_layout(blob)
    print(f"[*] Layout: {streams} strommer med blokker paa {block_size} byte")

    images = deinterleave(blob, block_size, streams)
    fragments: list[tuple[int, str]] = []
    for index, image in enumerate(images, 1):
        fragment_values = ztxt_values(image, "Fragment")
        order_values = ztxt_values(image, "Order")
        if not fragment_values:
            raise SystemExit(f"Mangler fragment i bilde {index}")
        order = int(order_values[0]) if order_values else index
        fragment = fragment_values[0]
        fragments.append((order, fragment))
        print(f"[*] Bilde {index}: rekkefolge {order}, fragment {fragment!r}")

    flag = "".join(fragment for _order, fragment in sorted(fragments))
    if not re.fullmatch(r"CTF\{[A-Za-z0-9_]+\}", flag):
        raise SystemExit(f"Uventet flaggformat: {flag}")
    print(f"\n*** FLAGG: {flag} ***")


if __name__ == "__main__":
    main()
