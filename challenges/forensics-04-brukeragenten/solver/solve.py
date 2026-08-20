#!/usr/bin/env python3
"""Organizer solver for Brukeragenten."""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

from scapy.all import Raw, rdpcap


PCAP = Path(__file__).resolve().parents[1] / "dist" / "brukeragenten.pcap"
AGENT_PATTERN = re.compile(rb"^User-Agent:\s*(.+?)\r?$", re.MULTILINE)


def main() -> None:
    agents: Counter[str] = Counter()
    for packet in rdpcap(str(PCAP)):
        if Raw not in packet:
            continue
        for match in AGENT_PATTERN.findall(bytes(packet[Raw].load)):
            agents[match.decode("ascii", errors="replace")] += 1

    if not agents:
        raise SystemExit("Fant ingen HTTP brukeragenter")

    print("[*] Observerte brukeragenter:")
    for agent, count in agents.most_common():
        print(f"    {count:3d}  {agent}")

    for agent, _count in agents.most_common():
        match = re.search(r"\b(Nikto)/(\d+(?:\.\d+)+)", agent, re.IGNORECASE)
        if match:
            flag = f"CTF{{{match.group(1).lower()}_{match.group(2)}}}"
            print(f"\n*** FLAGG: {flag} ***")
            return

    raise SystemExit("Fant ikke skannerens navn og versjon")


if __name__ == "__main__":
    main()

