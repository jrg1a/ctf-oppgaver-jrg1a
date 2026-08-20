"""
CTF Challenge: "Modbus i klartekst"
Genererer en PCAP med realistisk Modbus TCP-trafikk.
Flagget er lagret som ASCII i holding registers (adresse 100+).

Wireshark-hint for deltakere:
  Filter: modbus
  Se på "Read Holding Registers Response" pakkene
"""

import struct
import random
from pathlib import Path
from scapy.all import wrpcap, Ether, IP, TCP, Raw
from scapy.layers.inet import IPerror

FLAG = "CTF{m0dbus_1s_n0t_s3cur3}"

ATTACKER_IP  = "10.10.10.50"
PLC_IP       = "10.10.10.5"
ATTACKER_PORT_BASE = 50000
MODBUS_PORT  = 502


def modbus_tcp(transaction_id, unit_id, pdu):
    """Bygg Modbus TCP Application Data Unit (MBAP + PDU)."""
    length = 1 + len(pdu)          # unit_id (1) + PDU
    mbap = struct.pack(">HHHB",
        transaction_id,            # Transaction ID
        0x0000,                    # Protocol ID (alltid 0 for Modbus TCP)
        length,
        unit_id
    )
    return mbap + pdu


def fc3_request(start_addr, quantity):
    """Read Holding Registers request (FC=0x03)."""
    return struct.pack(">BHH", 0x03, start_addr, quantity)


def fc3_response(values):
    """Read Holding Registers response."""
    byte_count = len(values) * 2
    data = struct.pack(">BB", 0x03, byte_count)
    for v in values:
        data += struct.pack(">H", v)
    return data


def fc06_request(addr, value):
    """Write Single Register request (FC=0x06)."""
    return struct.pack(">BHH", 0x06, addr, value)


def fc06_response(addr, value):
    """Write Single Register response (echo)."""
    return struct.pack(">BHH", 0x06, addr, value)


def make_stream(src_ip, dst_ip, src_port, dst_port, packets_data, base_time=0.0):
    """
    Lag en enkel TCP-strøm (SYN, SYN-ACK, ACK, data..., FIN).
    packets_data: liste av (payload_bytes, delta_time, direction)
      direction: 'c2s' (client→server) eller 's2c' (server→client)
    """
    pkts = []
    seq_c = random.randint(1000000, 9000000)
    seq_s = random.randint(1000000, 9000000)
    t = base_time

    def pkt(src, dst, sport, dport, flags, seq, ack, payload=b"", ts=0.0):
        return (
            Ether() /
            IP(src=src, dst=dst, ttl=64) /
            TCP(sport=sport, dport=dport, flags=flags,
                seq=seq, ack=ack, window=65535) /
            Raw(load=payload)
        ) if payload else (
            Ether() /
            IP(src=src, dst=dst, ttl=64) /
            TCP(sport=sport, dport=dport, flags=flags,
                seq=seq, ack=ack, window=65535)
        )

    # SYN
    pkts.append(pkt(src_ip, dst_ip, src_port, dst_port, "S", seq_c, 0, ts=t))
    t += 0.001
    seq_c += 1

    # SYN-ACK
    pkts.append(pkt(dst_ip, src_ip, dst_port, src_port, "SA", seq_s, seq_c, ts=t))
    t += 0.001
    seq_s += 1

    # ACK
    pkts.append(pkt(src_ip, dst_ip, src_port, dst_port, "A", seq_c, seq_s, ts=t))
    t += 0.002

    for (payload, delta, direction) in packets_data:
        t += delta
        if direction == "c2s":
            pkts.append(pkt(src_ip, dst_ip, src_port, dst_port,
                            "PA", seq_c, seq_s, payload, ts=t))
            seq_c += len(payload)
            t += 0.003
            pkts.append(pkt(dst_ip, src_ip, dst_port, src_port,
                            "A", seq_s, seq_c, ts=t))
        else:
            pkts.append(pkt(dst_ip, src_ip, dst_port, src_port,
                            "PA", seq_s, seq_c, payload, ts=t))
            seq_s += len(payload)
            t += 0.003
            pkts.append(pkt(src_ip, dst_ip, src_port, dst_port,
                            "A", seq_c, seq_s, ts=t))

    t += 0.01
    # FIN
    pkts.append(pkt(src_ip, dst_ip, src_port, dst_port, "FA", seq_c, seq_s, ts=t))
    seq_c += 1
    t += 0.001
    pkts.append(pkt(dst_ip, src_ip, dst_port, src_port, "FA", seq_s, seq_c, ts=t))
    seq_s += 1
    t += 0.001
    pkts.append(pkt(src_ip, dst_ip, src_port, dst_port, "A", seq_c, seq_s, ts=t))

    # Sett tidsstempler
    for p in pkts:
        p.time = t

    return pkts, t


def flag_to_registers(flag_str):
    """Konverter flagg-streng til liste av 16-bit register-verdier (big-endian ASCII)."""
    padded = flag_str if len(flag_str) % 2 == 0 else flag_str + "\x00"
    regs = []
    for i in range(0, len(padded), 2):
        regs.append((ord(padded[i]) << 8) | ord(padded[i + 1]))
    return regs


def build_normal_traffic(t_offset):
    """Noen normale poll-forespørsler (status-registre) som støy."""
    all_pkts = []
    tid = 1
    for i in range(4):
        sport = ATTACKER_PORT_BASE + i
        # Les 5 registre fra adresse 0 (normale statusverdier)
        normal_regs = [random.randint(0, 1000) for _ in range(5)]
        req_pdu  = fc3_request(0, 5)
        resp_pdu = fc3_response(normal_regs)
        stream_data = [
            (modbus_tcp(tid, 1, req_pdu),  0.5,  "c2s"),
            (modbus_tcp(tid, 1, resp_pdu), 0.002, "s2c"),
        ]
        pkts, t_offset = make_stream(
            ATTACKER_IP, PLC_IP, sport, MODBUS_PORT,
            stream_data, base_time=t_offset
        )
        all_pkts.extend(pkts)
        tid += 1
        t_offset += 0.1
    return all_pkts, t_offset


def build_flag_traffic(t_offset):
    """Trafikk der flagget leses ut fra holding registers 100-."""
    flag_regs = flag_to_registers(FLAG)
    num_regs  = len(flag_regs)
    tid = 10

    sport = ATTACKER_PORT_BASE + 10

    req_pdu  = fc3_request(100, num_regs)
    resp_pdu = fc3_response(flag_regs)

    stream_data = [
        (modbus_tcp(tid, 1, req_pdu),  0.0,  "c2s"),
        (modbus_tcp(tid, 1, resp_pdu), 0.003, "s2c"),
    ]
    pkts, t_offset = make_stream(
        ATTACKER_IP, PLC_IP, sport, MODBUS_PORT,
        stream_data, base_time=t_offset
    )
    return pkts, t_offset


def main():
    all_pkts = []
    t = 0.0

    # Runde 1: normale poll-forespørsler
    pkts, t = build_normal_traffic(t)
    all_pkts.extend(pkts)

    # Runde 2: les ut flagget
    pkts, t = build_flag_traffic(t)
    all_pkts.extend(pkts)

    # Runde 3: mer normal trafikk etter
    pkts, t = build_normal_traffic(t)
    all_pkts.extend(pkts)

    # Sorter på tid og skriv PCAP
    all_pkts.sort(key=lambda p: p.time)
    out = Path(__file__).resolve().parent / "modbus_capture.pcap"
    wrpcap(str(out), all_pkts)
    print(f"[+] Skrev {len(all_pkts)} pakker til {out.name}")
    print(f"[+] Flagg gjemt i FC=3 response, register 100-{100 + len(flag_to_registers(FLAG)) - 1}")
    print(f"[+] Register-verdier (hex): {[hex(r) for r in flag_to_registers(FLAG)]}")


if __name__ == "__main__":
    main()
