#!/usr/bin/env python3
"""Solver for DNS i sidesporet."""

from __future__ import annotations

import re
from pathlib import Path

try:
    from scapy.all import DNSQR, rdpcap
except ImportError as exc:
    raise SystemExit("scapy mangler: pip install scapy") from exc


PCAP = Path(__file__).resolve().parents[1] / "dist" / "dns_lekkasje.pcap"
DOMAIN = ".exfil.ctf-lab.nordverk.local."


def main() -> None:
    chunks = {}
    for pkt in rdpcap(str(PCAP)):
        if DNSQR not in pkt:
            continue
        qname = pkt[DNSQR].qname.decode().lower()
        if not qname.endswith(DOMAIN):
            continue
        first_label = qname.split(".", 1)[0]
        match = re.fullmatch(r"(\d{2})-([0-9a-f]+)", first_label)
        if match:
            chunks[int(match.group(1))] = match.group(2)

    hex_data = "".join(chunks[i] for i in sorted(chunks))
    flag = bytes.fromhex(hex_data).decode()
    print(f"*** FLAGG: {flag} ***")


if __name__ == "__main__":
    main()

