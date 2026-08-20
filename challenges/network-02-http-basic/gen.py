#!/usr/bin/env python3
from __future__ import annotations

import base64
import socket
import struct
from pathlib import Path


FLAG = "CTF{basic_auth_er_bare_base64}"
BASE_TS = 1781260800

TCP_FIN = 0x01
TCP_SYN = 0x02
TCP_PSH = 0x08
TCP_ACK = 0x10

MACS = {
    "10.26.0.42": bytes.fromhex("020000000042"),
    "10.26.0.10": bytes.fromhex("020000000010"),
    "10.26.0.11": bytes.fromhex("020000000011"),
    "10.26.0.12": bytes.fromhex("020000000012"),
    "10.26.0.30": bytes.fromhex("020000000030"),
    "10.26.0.31": bytes.fromhex("020000000031"),
}


def checksum(data: bytes) -> int:
    if len(data) % 2:
        data += b"\x00"
    total = sum(struct.unpack(f"!{len(data) // 2}H", data))
    total = (total >> 16) + (total & 0xFFFF)
    total += total >> 16
    return (~total) & 0xFFFF


def tcp_packet(
    src: str,
    dst: str,
    sport: int,
    dport: int,
    seq: int,
    ack: int,
    flags: int,
    payload: bytes = b"",
    ident: int = 0,
) -> bytes:
    src_ip = socket.inet_aton(src)
    dst_ip = socket.inet_aton(dst)

    eth = MACS[dst] + MACS[src] + bytes.fromhex("0800")

    tcp_header = struct.pack(
        "!HHIIHHHH",
        sport,
        dport,
        seq,
        ack,
        (5 << 12) | flags,
        8192,
        0,
        0,
    )
    pseudo = (
        src_ip
        + dst_ip
        + struct.pack("!BBH", 0, socket.IPPROTO_TCP, len(tcp_header) + len(payload))
    )
    tcp_sum = checksum(pseudo + tcp_header + payload)
    tcp_header = struct.pack(
        "!HHIIHHHH",
        sport,
        dport,
        seq,
        ack,
        (5 << 12) | flags,
        8192,
        tcp_sum,
        0,
    )

    ip_total_len = 20 + len(tcp_header) + len(payload)
    ip_header = struct.pack(
        "!BBHHHBBH4s4s",
        0x45,
        0,
        ip_total_len,
        ident & 0xFFFF,
        0x4000,
        64,
        socket.IPPROTO_TCP,
        0,
        src_ip,
        dst_ip,
    )
    ip_sum = checksum(ip_header)
    ip_header = struct.pack(
        "!BBHHHBBH4s4s",
        0x45,
        0,
        ip_total_len,
        ident & 0xFFFF,
        0x4000,
        64,
        socket.IPPROTO_TCP,
        ip_sum,
        src_ip,
        dst_ip,
    )
    return eth + ip_header + tcp_header + payload


def basic(username: str, password: str) -> str:
    return base64.b64encode(f"{username}:{password}".encode()).decode()


def request(
    method: str,
    path: str,
    host: str,
    *,
    headers: dict[str, str] | None = None,
    body: str = "",
) -> bytes:
    headers = headers or {}
    lines = [
        f"{method} {path} HTTP/1.1",
        f"Host: {host}",
        "User-Agent: ConferenceStand/1.0",
        "Accept: */*",
    ]
    for key, value in headers.items():
        lines.append(f"{key}: {value}")
    if body:
        lines.append(f"Content-Length: {len(body.encode())}")
    lines.append("")
    lines.append(body)
    return "\r\n".join(lines).encode()


def response(status: str, body: str, *, content_type: str = "text/plain") -> bytes:
    encoded = body.encode()
    return (
        f"HTTP/1.1 {status}\r\n"
        f"Content-Type: {content_type}\r\n"
        f"Content-Length: {len(encoded)}\r\n"
        "\r\n"
    ).encode() + encoded


def tcp_exchange(
    client: str,
    server: str,
    sport: int,
    req: bytes,
    resp: bytes,
    *,
    client_seq: int,
    server_seq: int,
    ident: int,
) -> list[bytes]:
    dport = 80
    client_data_seq = client_seq + 1
    server_data_seq = server_seq + 1
    after_req = client_data_seq + len(req)
    after_resp = server_data_seq + len(resp)

    return [
        tcp_packet(client, server, sport, dport, client_seq, 0, TCP_SYN, ident=ident),
        tcp_packet(
            server,
            client,
            dport,
            sport,
            server_seq,
            client_seq + 1,
            TCP_SYN | TCP_ACK,
            ident=ident + 1,
        ),
        tcp_packet(
            client,
            server,
            sport,
            dport,
            client_data_seq,
            server_data_seq,
            TCP_ACK,
            ident=ident + 2,
        ),
        tcp_packet(
            client,
            server,
            sport,
            dport,
            client_data_seq,
            server_data_seq,
            TCP_PSH | TCP_ACK,
            req,
            ident=ident + 3,
        ),
        tcp_packet(
            server,
            client,
            dport,
            sport,
            server_data_seq,
            after_req,
            TCP_PSH | TCP_ACK,
            resp,
            ident=ident + 4,
        ),
        tcp_packet(
            client,
            server,
            sport,
            dport,
            after_req,
            after_resp,
            TCP_ACK,
            ident=ident + 5,
        ),
        tcp_packet(
            client,
            server,
            sport,
            dport,
            after_req,
            after_resp,
            TCP_FIN | TCP_ACK,
            ident=ident + 6,
        ),
    ]


def main() -> None:
    out = Path(__file__).resolve().parent / "dist" / "basic_auth.pcap"
    out.parent.mkdir(parents=True, exist_ok=True)

    exchanges = [
        (
            "10.26.0.11",
            51002,
            request("GET", "/program/program.json", "portal.nordverk.local"),
            response("200 OK", '{"status":"public","cache":"S0F7aWtrZV9mbGFnZ2V0fQ=="}', content_type="application/json"),
        ),
        (
            "10.26.0.30",
            51014,
            request(
                "GET",
                "/login",
                "printer-stand.nordverk.local",
                headers={"Authorization": f"Basic {basic('demo', 'demo2026')}"},
            ),
            response("403 Forbidden", "demo credentials are not valid for this panel\n"),
        ),
        (
            "10.26.0.31",
            51026,
            request(
                "GET",
                "/snapshot",
                "camera-1.nordverk.local",
                headers={"Authorization": f"Basic {basic('viewer', 'NordverkViewer2026!')}"},
            ),
            response("200 OK", "camera snapshot disabled during event\n"),
        ),
        (
            "10.26.0.12",
            51038,
            request(
                "POST",
                "/session",
                "idp.nordverk.local",
                headers={"Authorization": f"Basic {basic('operator', 'MFA-required')}", "Content-Type": "application/json"},
                body='{"station":"stand-pc"}',
            ),
            response("401 Unauthorized", "MFA required\n"),
        ),
        (
            "10.26.0.10",
            51042,
            request("GET", "/api/health", "status.nordverk.local"),
            response("200 OK", "status=green; note=public endpoint\n"),
        ),
        (
            "10.26.0.10",
            51055,
            request(
                "GET",
                "/admin/status",
                "status.nordverk.local",
                headers={"Authorization": f"Basic {basic('stand', FLAG)}"},
            ),
            response("200 OK", "admin status unlocked\n"),
        ),
        (
            "10.26.0.10",
            51071,
            request(
                "GET",
                "/admin/status?cache=1",
                "status.nordverk.local",
                headers={"Authorization": f"Basic {basic('support', 'summer-rotation-2026')}"},
            ),
            response("403 Forbidden", "support account cannot read stand secret\n"),
        ),
    ]

    frames: list[bytes] = []
    for index, (server, sport, req, resp) in enumerate(exchanges):
        frames.extend(
            tcp_exchange(
                "10.26.0.42",
                server,
                sport,
                req,
                resp,
                client_seq=0x10000000 + index * 0x1000,
                server_seq=0x50000000 + index * 0x1000,
                ident=0x2600 + index * 16,
            )
        )

    pcap = struct.pack("<IHHIIII", 0xA1B2C3D4, 2, 4, 0, 0, 65535, 1)
    for index, frame in enumerate(frames):
        pcap += (
            struct.pack("<IIII", BASE_TS, 260000 + index * 1000, len(frame), len(frame))
            + frame
        )
    out.write_bytes(pcap)


if __name__ == "__main__":
    main()
