#!/usr/bin/env python3
"""Build a small FAT12 image with one deleted gzip file."""

from __future__ import annotations

import gzip
import struct
from pathlib import Path


FLAG = "CTF{slettet_betyr_ikke_borte}"
ROOT = Path(__file__).resolve().parent
OUT = ROOT / "dist" / "skiftminne.img"

BYTES_PER_SECTOR = 512
TOTAL_SECTORS = 2880
RESERVED_SECTORS = 1
FAT_COUNT = 2
SECTORS_PER_FAT = 9
ROOT_ENTRIES = 224
ROOT_SECTORS = 14
ROOT_START_SECTOR = RESERVED_SECTORS + FAT_COUNT * SECTORS_PER_FAT
DATA_START_SECTOR = ROOT_START_SECTOR + ROOT_SECTORS


def fat_time(hour: int, minute: int, second: int = 0) -> int:
    return (hour << 11) | (minute << 5) | (second // 2)


def fat_date(year: int, month: int, day: int) -> int:
    return ((year - 1980) << 9) | (month << 5) | day


def directory_entry(name: bytes, cluster: int, size: int, deleted: bool = False) -> bytes:
    if len(name) != 11:
        raise ValueError("Et FAT 8.3 navn må være 11 byte")
    if deleted:
        name = b"\xe5" + name[1:]

    timestamp = fat_time(18, 42, 0)
    date = fat_date(2026, 8, 19)
    return struct.pack(
        "<11sBBBHHHHHHHI",
        name,
        0x20,
        0,
        0,
        timestamp,
        date,
        date,
        0,
        timestamp,
        date,
        cluster,
        size,
    )


def set_fat12_entry(fat: bytearray, cluster: int, value: int) -> None:
    offset = cluster + cluster // 2
    value &= 0xFFF
    if cluster % 2 == 0:
        fat[offset] = value & 0xFF
        fat[offset + 1] = (fat[offset + 1] & 0xF0) | ((value >> 8) & 0x0F)
    else:
        fat[offset] = (fat[offset] & 0x0F) | ((value << 4) & 0xF0)
        fat[offset + 1] = (value >> 4) & 0xFF


def cluster_offset(cluster: int) -> int:
    sector = DATA_START_SECTOR + (cluster - 2)
    return sector * BYTES_PER_SECTOR


def write_cluster(image: bytearray, cluster: int, data: bytes) -> None:
    if len(data) > BYTES_PER_SECTOR:
        raise ValueError("Denne generatoren bruker én klynge per fil")
    start = cluster_offset(cluster)
    image[start:start + len(data)] = data


def boot_sector() -> bytes:
    boot = bytearray(BYTES_PER_SECTOR)
    boot[0:3] = b"\xeb\x3c\x90"
    boot[3:11] = b"NORDVERK"
    struct.pack_into("<H", boot, 11, BYTES_PER_SECTOR)
    boot[13] = 1
    struct.pack_into("<H", boot, 14, RESERVED_SECTORS)
    boot[16] = FAT_COUNT
    struct.pack_into("<H", boot, 17, ROOT_ENTRIES)
    struct.pack_into("<H", boot, 19, TOTAL_SECTORS)
    boot[21] = 0xF0
    struct.pack_into("<H", boot, 22, SECTORS_PER_FAT)
    struct.pack_into("<H", boot, 24, 18)
    struct.pack_into("<H", boot, 26, 2)
    struct.pack_into("<I", boot, 28, 0)
    struct.pack_into("<I", boot, 32, 0)
    boot[36] = 0
    boot[38] = 0x29
    struct.pack_into("<I", boot, 39, 0x26081942)
    boot[43:54] = b"SKIFTMINNE "
    boot[54:62] = b"FAT12   "
    boot[510:512] = b"\x55\xaa"
    return bytes(boot)


def main() -> None:
    image = bytearray(TOTAL_SECTORS * BYTES_PER_SECTOR)
    image[:BYTES_PER_SECTOR] = boot_sector()

    readme = (
        "NORDVERK VEDLIKEHOLDSMINNE\r\n"
        "Synlige logger er eksportert fra skiftterminal 4.\r\n"
        "Slettede filer skal ikke brukes i produksjon.\r\n"
    ).encode("ascii")
    status = (
        "tid,trykk,temperatur,status\r\n"
        "18:10,74.2,31.4,NORMAL\r\n"
        "18:20,74.4,31.5,NORMAL\r\n"
        "18:30,74.1,31.5,NORMAL\r\n"
    ).encode("ascii")
    decoy = (
        "Eldre testkode: CTF-OLD{bare_en_test}\r\n"
        "Denne filen er ikke en hendelseslogg.\r\n"
    ).encode("ascii")
    deleted_plain = (
        "Nordverk skiftlogg 2026-08-19\n"
        "18:37 Alarmkvittering mottatt\n"
        "18:40 Kontrollkode: " + FLAG + "\n"
        "18:42 Loggen markert for sletting\n"
    ).encode("ascii")
    deleted_gzip = gzip.compress(deleted_plain, mtime=0)

    files = [
        (b"README  TXT", 2, readme, False),
        (b"STATUS  CSV", 3, status, False),
        (b"SKIFT   TXT", 4, decoy, False),
        (b"SKIFTLOGGZ ", 5, deleted_gzip, True),
    ]

    fat = bytearray(SECTORS_PER_FAT * BYTES_PER_SECTOR)
    fat[0:3] = b"\xf0\xff\xff"
    for _name, cluster, _data, deleted in files:
        set_fat12_entry(fat, cluster, 0x000 if deleted else 0xFFF)

    first_fat = RESERVED_SECTORS * BYTES_PER_SECTOR
    second_fat = first_fat + len(fat)
    image[first_fat:first_fat + len(fat)] = fat
    image[second_fat:second_fat + len(fat)] = fat

    root_offset = ROOT_START_SECTOR * BYTES_PER_SECTOR
    for index, (name, cluster, data, deleted) in enumerate(files):
        entry = directory_entry(name, cluster, len(data), deleted)
        start = root_offset + index * 32
        image[start:start + 32] = entry
        write_cluster(image, cluster, data)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_bytes(bytes(image))
    print(f"[+] Skrev {OUT} ({len(image)} byte)")


if __name__ == "__main__":
    main()

