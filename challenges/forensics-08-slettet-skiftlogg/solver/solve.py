#!/usr/bin/env python3
"""Organizer solver for Slettet skiftlogg."""

from __future__ import annotations

import gzip
import re
import struct
from pathlib import Path


ARTIFACT = Path(__file__).resolve().parents[1] / "dist" / "skiftminne.img"


def main() -> None:
    image = ARTIFACT.read_bytes()
    bytes_per_sector = struct.unpack_from("<H", image, 11)[0]
    reserved = struct.unpack_from("<H", image, 14)[0]
    fat_count = image[16]
    root_entries = struct.unpack_from("<H", image, 17)[0]
    sectors_per_fat = struct.unpack_from("<H", image, 22)[0]
    root_start = (reserved + fat_count * sectors_per_fat) * bytes_per_sector
    root_size = root_entries * 32
    root_sectors = (root_size + bytes_per_sector - 1) // bytes_per_sector
    data_start = root_start + root_sectors * bytes_per_sector

    for offset in range(root_start, root_start + root_size, 32):
        entry = image[offset:offset + 32]
        if not entry or entry[0] == 0x00:
            break
        if entry[0] != 0xE5 or entry[11] == 0x0F:
            continue
        cluster = struct.unpack_from("<H", entry, 26)[0]
        size = struct.unpack_from("<I", entry, 28)[0]
        content_offset = data_start + (cluster - 2) * bytes_per_sector
        recovered = image[content_offset:content_offset + size]
        try:
            plaintext = gzip.decompress(recovered).decode("ascii")
        except (gzip.BadGzipFile, UnicodeDecodeError):
            continue
        match = re.search(r"CTF\{[A-Za-z0-9_]+\}", plaintext)
        if match:
            print(match.group(0))
            return
    raise SystemExit("Fant ikke flagget i en slettet katalogoppføring")


if __name__ == "__main__":
    main()

