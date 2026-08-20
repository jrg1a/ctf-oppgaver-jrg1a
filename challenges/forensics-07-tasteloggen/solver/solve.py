#!/usr/bin/env python3
"""Organizer solver for Tasteloggen."""

from __future__ import annotations

import re
import struct
from pathlib import Path


PCAP = Path(__file__).resolve().parents[1] / "dist" / "tasteloggen.pcap"
USB_HEADER = struct.Struct("<HQIHBHHBBI")

KEYS = {
    **{0x04 + index: chr(ord("a") + index) for index in range(26)},
    **{code: str(number) for number, code in zip(range(1, 10), range(0x1E, 0x27))},
    0x27: "0",
    0x28: "\n",
    0x2C: " ",
    0x2D: "-",
    0x2E: "=",
    0x2F: "[",
    0x30: "]",
    0x31: "\\",
    0x33: ";",
    0x34: "'",
    0x35: "`",
    0x36: ",",
    0x37: ".",
    0x38: "/",
}

SHIFT_KEYS = {
    **{0x04 + index: chr(ord("A") + index) for index in range(26)},
    0x1E: "!",
    0x1F: "@",
    0x20: "#",
    0x21: "$",
    0x22: "%",
    0x23: "^",
    0x24: "&",
    0x25: "*",
    0x26: "(",
    0x27: ")",
    0x2D: "_",
    0x2E: "+",
    0x2F: "{",
    0x30: "}",
    0x31: "|",
    0x33: ":",
    0x34: '"',
    0x35: "~",
    0x36: "<",
    0x37: ">",
    0x38: "?",
}


def pcap_records(data: bytes) -> list[bytes]:
    if len(data) < 24:
        raise SystemExit("PCAP er for kort")
    magic = data[:4]
    if magic == b"\xd4\xc3\xb2\xa1":
        endian = "<"
    elif magic == b"\xa1\xb2\xc3\xd4":
        endian = ">"
    else:
        raise SystemExit("Ukjent PCAP magic")

    _magic, _major, _minor, _zone, _sigfigs, _snaplen, linktype = struct.unpack(
        f"{endian}IHHIIII", data[:24]
    )
    if linktype != 249:
        raise SystemExit(f"Forventet USBPcap linktype 249, fikk {linktype}")

    records: list[bytes] = []
    offset = 24
    record_header = struct.Struct(f"{endian}IIII")
    while offset + record_header.size <= len(data):
        _ts_sec, _ts_usec, incl_len, _orig_len = record_header.unpack(
            data[offset:offset + record_header.size]
        )
        offset += record_header.size
        records.append(data[offset:offset + incl_len])
        offset += incl_len
    return records


def hid_reports(records: list[bytes]) -> list[bytes]:
    reports: list[bytes] = []
    for record in records:
        if len(record) < USB_HEADER.size:
            continue
        (
            header_len,
            _irp_id,
            _status,
            _function,
            _info,
            _bus,
            _device,
            endpoint,
            transfer,
            data_length,
        ) = USB_HEADER.unpack(record[:USB_HEADER.size])
        if header_len < USB_HEADER.size or transfer != 1 or endpoint & 0x80 == 0:
            continue
        payload = record[header_len:header_len + data_length]
        if len(payload) == 8:
            reports.append(payload)
    return reports


def decode_report(report: bytes) -> str:
    modifier = report[0]
    shifted = bool(modifier & 0x22)
    output = []
    for keycode in report[2:8]:
        if keycode == 0:
            continue
        table = SHIFT_KEYS if shifted else KEYS
        output.append(table.get(keycode, "?"))
    return "".join(output)


def main() -> None:
    records = pcap_records(PCAP.read_bytes())
    reports = hid_reports(records)
    print(f"[*] Leste {len(records)} USB pakker, fant {len(reports)} tastaturrapporter")

    text = "".join(decode_report(report) for report in reports if any(report[2:8]))
    print("[*] Rekonstruert tekst:")
    print(text)

    match = re.search(r"CTF\{[A-Za-z0-9_]+\}", text)
    if not match:
        raise SystemExit("Fant ikke flagg i tasteloggen")
    print(f"\n*** FLAGG: {match.group(0)} ***")


if __name__ == "__main__":
    main()
