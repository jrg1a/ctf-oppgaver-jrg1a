#!/usr/bin/env python3
"""Solver for Modbus i klartekst."""

from __future__ import annotations

import re
import struct
from pathlib import Path

try:
    from scapy.all import Raw, TCP, rdpcap
except ImportError as exc:
    raise SystemExit("scapy mangler: pip install scapy") from exc


PCAP = Path(__file__).resolve().parents[1] / "modbus_capture.pcap"


def decode_registers(data: bytes) -> str:
    chars = []
    for i in range(0, len(data), 2):
        if i + 2 > len(data):
            break
        value = struct.unpack(">H", data[i : i + 2])[0]
        chars.append(chr((value >> 8) & 0xFF))
        chars.append(chr(value & 0xFF))
    return "".join(chars).rstrip("\x00")


def main() -> None:
    packets = rdpcap(str(PCAP))

    for pkt in packets:
        if TCP not in pkt or Raw not in pkt:
            continue

        payload = bytes(pkt[Raw].load)
        if len(payload) < 9:
            continue

        # MBAP header: transaction id, protocol id, length, unit id.
        protocol_id = struct.unpack(">H", payload[2:4])[0]
        if protocol_id != 0:
            continue

        function_code = payload[7]
        if function_code != 0x03:
            continue

        byte_count = payload[8]
        register_data = payload[9 : 9 + byte_count]
        decoded = decode_registers(register_data)

        match = re.search(r"CTF\{[^}]+\}", decoded)
        if match:
            print(f"*** FLAGG: {match.group(0)} ***")
            return

    raise SystemExit("Fant ikke CTF{...} i Modbus-responsene")


if __name__ == "__main__":
    main()

