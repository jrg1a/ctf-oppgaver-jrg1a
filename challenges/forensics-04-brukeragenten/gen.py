#!/usr/bin/env python3
"""Generate the packet capture for Brukeragenten."""

from __future__ import annotations

from pathlib import Path
from random import Random

from scapy.all import Ether, IP, Raw, TCP, wrpcap


FLAG = "CTF{nikto_2.5.0}"
OUT = Path(__file__).resolve().parent / "dist" / "brukeragenten.pcap"

CLIENT = "10.42.7.23"
SERVER = "10.42.7.80"
CLIENT_MAC = "02:42:07:00:00:23"
SERVER_MAC = "02:42:07:00:00:80"
BASE_TIME = 1784815200.0

NORMAL_AGENTS = (
    "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126.0.0.0 Safari/537.36",
    "curl/8.7.1",
    "Nordverk-Update/4.2",
)
SCANNER_AGENT = "Mozilla/5.00 (Nikto/2.5.0) (Evasions:None)"


def http_request(path: str, agent: str) -> bytes:
    return (
        f"GET {path} HTTP/1.1\r\n"
        f"Host: intranett.nordverk.local\r\n"
        f"User-Agent: {agent}\r\n"
        "Accept: */*\r\n"
        "Connection: close\r\n\r\n"
    ).encode()


def http_response(found: bool) -> bytes:
    status = "200 OK" if found else "404 Not Found"
    body = b"ok\n" if found else b"not found\n"
    return (
        f"HTTP/1.1 {status}\r\n"
        "Content-Type: text/plain\r\n"
        f"Content-Length: {len(body)}\r\n"
        "Connection: close\r\n\r\n"
    ).encode() + body


def flow(
    sport: int,
    client_seq: int,
    server_seq: int,
    request: bytes,
    response: bytes,
    started: float,
) -> list:
    client = Ether(src=CLIENT_MAC, dst=SERVER_MAC) / IP(src=CLIENT, dst=SERVER)
    server = Ether(src=SERVER_MAC, dst=CLIENT_MAC) / IP(src=SERVER, dst=CLIENT)
    client_data = client_seq + 1
    server_data = server_seq + 1
    after_request = client_data + len(request)
    after_response = server_data + len(response)

    packets = [
        client / TCP(sport=sport, dport=80, seq=client_seq, flags="S"),
        server
        / TCP(
            sport=80,
            dport=sport,
            seq=server_seq,
            ack=client_data,
            flags="SA",
        ),
        client
        / TCP(
            sport=sport,
            dport=80,
            seq=client_data,
            ack=server_data,
            flags="A",
        ),
        client
        / TCP(
            sport=sport,
            dport=80,
            seq=client_data,
            ack=server_data,
            flags="PA",
        )
        / Raw(request),
        server
        / TCP(
            sport=80,
            dport=sport,
            seq=server_data,
            ack=after_request,
            flags="PA",
        )
        / Raw(response),
        client
        / TCP(
            sport=sport,
            dport=80,
            seq=after_request,
            ack=after_response,
            flags="FA",
        ),
        server
        / TCP(
            sport=80,
            dport=sport,
            seq=after_response,
            ack=after_request + 1,
            flags="A",
        ),
    ]
    for index, packet in enumerate(packets):
        packet.time = started + index * 0.002
    return packets


def main() -> None:
    rng = Random(26062026)
    OUT.parent.mkdir(parents=True, exist_ok=True)

    normal_paths = (
        "/",
        "/status",
        "/assets/app.css",
        "/assets/logo.png",
        "/api/news",
        "/favicon.ico",
    )
    scan_paths = (
        "/admin/",
        "/backup/",
        "/cgi-bin/test-cgi",
        "/config.php.bak",
        "/.env",
        "/phpinfo.php",
        "/server-status",
        "/robots.txt",
        "/old/",
        "/console/",
        "/manager/html",
        "/wp-login.php",
    )

    events: list[tuple[str, str, bool]] = []
    for index in range(18):
        events.append(
            (
                normal_paths[index % len(normal_paths)],
                NORMAL_AGENTS[index % len(NORMAL_AGENTS)],
                True,
            )
        )
    for index in range(72):
        events.append((scan_paths[index % len(scan_paths)], SCANNER_AGENT, False))
    rng.shuffle(events)

    packets = []
    for index, (path, agent, found) in enumerate(events):
        packets.extend(
            flow(
                sport=41000 + index,
                client_seq=rng.randrange(100000, 900000),
                server_seq=rng.randrange(100000, 900000),
                request=http_request(path, agent),
                response=http_response(found),
                started=BASE_TIME + index * 0.08,
            )
        )

    wrpcap(str(OUT), packets)
    print(f"[+] Skrev {len(packets)} pakker til {OUT}")
    print(f"[+] Forventet flagg: {FLAG}")


if __name__ == "__main__":
    main()

