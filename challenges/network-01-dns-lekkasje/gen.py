#!/usr/bin/env python3
"""Generate DNS exfiltration PCAP."""

from __future__ import annotations

from pathlib import Path
from random import randint, seed

from scapy.all import DNS, DNSQR, DNSRR, Ether, IP, UDP, wrpcap


FLAG = "CTF{dns_l3kkasje_i_subdomener}"
OUT = Path(__file__).resolve().parent / "dist" / "dns_lekkasje.pcap"

CLIENT = "10.26.6.42"
DNS_SERVER = "10.26.6.53"
CLIENT_MAC = "02:26:06:00:00:42"
DNS_MAC = "02:26:06:00:00:53"
DOMAIN = "exfil.ctf-lab.nordverk.local"


def query(name: str, sport: int, txid: int, t: float):
    pkt = (
        Ether(src=CLIENT_MAC, dst=DNS_MAC)
        / IP(src=CLIENT, dst=DNS_SERVER)
        / UDP(sport=sport, dport=53)
        / DNS(id=txid, rd=1, qd=DNSQR(qname=name))
    )
    pkt.time = t
    return pkt


def response(name: str, sport: int, txid: int, t: float):
    pkt = (
        Ether(src=DNS_MAC, dst=CLIENT_MAC)
        / IP(src=DNS_SERVER, dst=CLIENT)
        / UDP(sport=53, dport=sport)
        / DNS(
            id=txid,
            qr=1,
            aa=1,
            rd=1,
            ra=1,
            qd=DNSQR(qname=name),
            an=DNSRR(rrname=name, ttl=60, rdata="127.0.0.1"),
        )
    )
    pkt.time = t
    return pkt


def main() -> None:
    seed(2606)
    OUT.parent.mkdir(parents=True, exist_ok=True)

    benign = [
        "teknologidagene.example",
        "www.example.org",
        "nsm.no",
        "cdn.example.net",
        "updates.vendor.example",
    ]

    packets = []
    t = 0.0

    for i, name in enumerate(benign):
        txid = randint(1000, 65000)
        sport = 41000 + i
        packets.append(query(name, sport, txid, t))
        packets.append(response(name, sport, txid, t + 0.01))
        t += 0.2

    hex_flag = FLAG.encode().hex()
    chunks = [hex_flag[i : i + 8] for i in range(0, len(hex_flag), 8)]

    for idx, chunk in enumerate(chunks):
        name = f"{idx:02d}-{chunk}.{DOMAIN}"
        txid = randint(1000, 65000)
        sport = 43000 + idx
        packets.append(query(name, sport, txid, t))
        packets.append(response(name, sport, txid, t + 0.015))
        t += 0.17

    for i, name in enumerate(reversed(benign)):
        txid = randint(1000, 65000)
        sport = 45000 + i
        packets.append(query(name, sport, txid, t))
        packets.append(response(name, sport, txid, t + 0.01))
        t += 0.2

    wrpcap(str(OUT), packets)
    print(f"[+] Skrev {len(packets)} pakker til {OUT}")
    print(f"[+] Flagg: {FLAG}")


if __name__ == "__main__":
    main()
