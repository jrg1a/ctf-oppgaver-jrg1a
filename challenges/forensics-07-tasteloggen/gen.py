#!/usr/bin/env python3
"""Generate the USB HID PCAP for Tasteloggen."""

from __future__ import annotations

import struct
from pathlib import Path
from random import Random


FLAG = "CTF{usb_hid_tastene_husker}"
OUT = Path(__file__).resolve().parent / "dist" / "tasteloggen.pcap"
BASE_TIME = 1784818800
DLT_USBPCAP = 249
USB_HEADER_LEN = 27
KEYBOARD_DEVICE = 3
MOUSE_DEVICE = 5


TEXT = (
    "operator@nordverk:~$ echo nattlig kontroll\n"
    "nattlig kontroll\n"
    "operator@nordverk:~$ export RECOVERY_CODE=CTF{usb_hid_tastene_husker}\n"
    "operator@nordverk:~$ ./validate-backup\n"
    "backup ok\n"
    "operator@nordverk:~$ exit\n"
)


BASE_KEYS = {
    **{chr(ord("a") + index): 0x04 + index for index in range(26)},
    **{str(number): code for number, code in zip(range(1, 10), range(0x1E, 0x27))},
    "0": 0x27,
    "\n": 0x28,
    " ": 0x2C,
    "-": 0x2D,
    "=": 0x2E,
    "[": 0x2F,
    "]": 0x30,
    "\\": 0x31,
    ";": 0x33,
    "'": 0x34,
    "`": 0x35,
    ",": 0x36,
    ".": 0x37,
    "/": 0x38,
}

SHIFT_KEYS = {
    **{chr(ord("A") + index): 0x04 + index for index in range(26)},
    "!": 0x1E,
    "@": 0x1F,
    "#": 0x20,
    "$": 0x21,
    "%": 0x22,
    "^": 0x23,
    "&": 0x24,
    "*": 0x25,
    "(": 0x26,
    ")": 0x27,
    "_": 0x2D,
    "+": 0x2E,
    "{": 0x2F,
    "}": 0x30,
    "|": 0x31,
    ":": 0x33,
    '"': 0x34,
    "~": 0x35,
    "<": 0x36,
    ">": 0x37,
    "?": 0x38,
}


def keyboard_report(char: str) -> bytes:
    if char in BASE_KEYS:
        return bytes((0x00, 0x00, BASE_KEYS[char], 0, 0, 0, 0, 0))
    if char in SHIFT_KEYS:
        return bytes((0x02, 0x00, SHIFT_KEYS[char], 0, 0, 0, 0, 0))
    raise ValueError(f"Mangler HID mapping for {char!r}")


def usbcap_packet(
    payload: bytes,
    irp_id: int,
    ts_usec: int,
    device: int,
    endpoint: int,
) -> tuple[int, int, bytes]:
    header = struct.pack(
        "<HQIHBHHBBI",
        USB_HEADER_LEN,
        irp_id,
        0,
        0x0009,
        0,
        1,
        device,
        endpoint,
        1,
        len(payload),
    )
    return BASE_TIME, ts_usec, header + payload


def write_pcap(records: list[tuple[int, int, bytes]]) -> bytes:
    out = bytearray()
    out.extend(struct.pack("<IHHIIII", 0xA1B2C3D4, 2, 4, 0, 0, 65535, DLT_USBPCAP))
    for ts_sec, ts_usec, data in records:
        out.extend(struct.pack("<IIII", ts_sec, ts_usec, len(data), len(data)))
        out.extend(data)
    return bytes(out)


def main() -> None:
    rng = Random(26062026)
    OUT.parent.mkdir(parents=True, exist_ok=True)

    records: list[tuple[int, int, bytes]] = []
    irp_id = 0x100000
    ts_usec = 12000

    for position, char in enumerate(TEXT):
        if position % 9 == 4:
            mouse = bytes((rng.randrange(0, 2), rng.randrange(0, 5), rng.randrange(0, 5), 0))
            records.append(usbcap_packet(mouse, irp_id, ts_usec, MOUSE_DEVICE, 0x81))
            irp_id += 1
            ts_usec += rng.randrange(1500, 3000)

        records.append(usbcap_packet(keyboard_report(char), irp_id, ts_usec, KEYBOARD_DEVICE, 0x81))
        irp_id += 1
        ts_usec += rng.randrange(1800, 3600)
        records.append(usbcap_packet(b"\x00" * 8, irp_id, ts_usec, KEYBOARD_DEVICE, 0x81))
        irp_id += 1
        ts_usec += rng.randrange(1800, 5200)

    OUT.write_bytes(write_pcap(records))
    print(f"[+] Skrev {OUT} med {len(records)} USB interrupt pakker")
    print(f"[+] Forventet flagg: {FLAG}")


if __name__ == "__main__":
    main()
