"""Build dns_dhcp.pcap: one DNS lookup and one DHCP lease, fully synthetic.

No lab capture contains DHCP (only dns_lookup has DNS), so this script writes the
packets byte by byte (standard library only). Zeek 9.0.0 and Suricata 7.0.10
then turn the capture into the dns.log, dhcp.log and eve.json fixtures next to
this file, so the field names are the real ones, not guesses.

Addresses: 192.168.56.0/24 (private lab range), MAC 02:00:00:aa:bb:cc (the 02
prefix marks a locally administered, made-up address), names under .invalid.

Run:  python make_dns_dhcp_pcap.py dns_dhcp.pcap
"""

from __future__ import annotations

import struct
import sys
from pathlib import Path

START_TS = 1791252600.0  # 2026-10-06 02:10:00 UTC (one hour after the lab captures)

CLIENT_MAC = bytes.fromhex("020000aabbcc")  # 02:00:00:aa:bb:cc
SERVER_MAC = bytes.fromhex("020000000001")
BROADCAST_MAC = b"\xff" * 6

CLIENT_IP = "192.168.56.50"
SERVER_IP = "192.168.56.1"
PRINTER_IP = "192.168.56.20"


def ip_bytes(ip: str) -> bytes:
    return bytes(int(part) for part in ip.split("."))


def checksum(data: bytes) -> int:
    """The 16-bit one's complement sum used by the IPv4 header."""
    if len(data) % 2:
        data += b"\x00"
    total = sum(struct.unpack(f"!{len(data) // 2}H", data))
    while total > 0xFFFF:
        total = (total & 0xFFFF) + (total >> 16)
    return ~total & 0xFFFF


def udp_packet(src_mac: bytes, dst_mac: bytes, src_ip: str, dst_ip: str,
               sport: int, dport: int, payload: bytes, ip_id: int) -> bytes:
    """Ethernet + IPv4 + UDP around a payload. UDP checksum 0 = "not used" (IPv4)."""
    udp = struct.pack("!HHHH", sport, dport, 8 + len(payload), 0) + payload
    header = struct.pack("!BBHHHBBH4s4s", 0x45, 0, 20 + len(udp), ip_id, 0, 64, 17, 0,
                         ip_bytes(src_ip), ip_bytes(dst_ip))
    header = header[:10] + struct.pack("!H", checksum(header)) + header[12:]
    return dst_mac + src_mac + b"\x08\x00" + header + udp


def dns_name(name: str) -> bytes:
    return b"".join(bytes([len(p)]) + p.encode() for p in name.split(".")) + b"\x00"


def dns_query(txid: int, name: str) -> bytes:
    # flags 0x0100 = "recursion desired"; one question, type A, class IN
    return struct.pack("!HHHHHH", txid, 0x0100, 1, 0, 0, 0) + dns_name(name) + b"\x00\x01\x00\x01"


def dns_answer(txid: int, name: str, answer_ip: str, ttl: int) -> bytes:
    # flags 0x8180 = response + recursion desired + recursion available, NOERROR
    question = dns_name(name) + b"\x00\x01\x00\x01"
    # 0xc00c is a pointer back to the name in the question (offset 12)
    answer = struct.pack("!HHHIH", 0xC00C, 1, 1, ttl, 4) + ip_bytes(answer_ip)
    return struct.pack("!HHHHHH", txid, 0x8180, 1, 1, 0, 0) + question + answer


def dhcp_message(op: int, xid: int, msg_type: int, yiaddr: str, options: bytes) -> bytes:
    """One BOOTP/DHCP message (RFC 2131) with the given options."""
    fixed = struct.pack("!BBBBIHH4s4s4s4s", op, 1, 6, 0, xid, 0, 0x8000,
                        ip_bytes("0.0.0.0"), ip_bytes(yiaddr),
                        ip_bytes("0.0.0.0"), ip_bytes("0.0.0.0"))
    chaddr = CLIENT_MAC + b"\x00" * 10
    sname_file = b"\x00" * (64 + 128)
    cookie = b"\x63\x82\x53\x63"
    return fixed + chaddr + sname_file + cookie + bytes([53, 1, msg_type]) + options + b"\xff"


def option(code: int, value: bytes) -> bytes:
    return bytes([code, len(value)]) + value


def build_packets() -> list[tuple[float, bytes]]:
    xid = 0x3903F326
    host = option(12, b"laptop-lab")
    server_opts = (option(54, ip_bytes(SERVER_IP)) + option(51, struct.pack("!I", 3600))
                   + option(1, ip_bytes("255.255.255.0")) + option(3, ip_bytes(SERVER_IP)))
    request_opts = host + option(50, ip_bytes(CLIENT_IP)) + option(54, ip_bytes(SERVER_IP))
    t = START_TS
    return [
        # DHCP: DISCOVER, OFFER, REQUEST, ACK (all broadcast, client has no IP yet)
        (t + 0.00, udp_packet(CLIENT_MAC, BROADCAST_MAC, "0.0.0.0", "255.255.255.255", 68, 67,
                              dhcp_message(1, xid, 1, "0.0.0.0", host), 1)),
        (t + 0.01, udp_packet(SERVER_MAC, BROADCAST_MAC, SERVER_IP, "255.255.255.255", 67, 68,
                              dhcp_message(2, xid, 2, CLIENT_IP, server_opts), 2)),
        (t + 0.02, udp_packet(CLIENT_MAC, BROADCAST_MAC, "0.0.0.0", "255.255.255.255", 68, 67,
                              dhcp_message(1, xid, 3, "0.0.0.0", request_opts), 3)),
        (t + 0.03, udp_packet(SERVER_MAC, BROADCAST_MAC, SERVER_IP, "255.255.255.255", 67, 68,
                              dhcp_message(2, xid, 5, CLIENT_IP, server_opts), 4)),
        # DNS: the new laptop looks up the printer
        (t + 1.00, udp_packet(CLIENT_MAC, SERVER_MAC, CLIENT_IP, SERVER_IP, 53001, 53,
                              dns_query(0x1A2B, "printer.lab.invalid"), 5)),
        (t + 1.01, udp_packet(SERVER_MAC, CLIENT_MAC, SERVER_IP, CLIENT_IP, 53, 53001,
                              dns_answer(0x1A2B, "printer.lab.invalid", PRINTER_IP, 300), 6)),
    ]


def write_pcap(path: Path, packets: list[tuple[float, bytes]]) -> None:
    # classic pcap: magic, version 2.4, timezone 0, sigfigs 0, snaplen, Ethernet
    out = [struct.pack("<IHHiIII", 0xA1B2C3D4, 2, 4, 0, 0, 65535, 1)]
    for ts, frame in packets:
        seconds = int(ts)
        micros = round((ts - seconds) * 1_000_000)
        out.append(struct.pack("<IIII", seconds, micros, len(frame), len(frame)) + frame)
    path.write_bytes(b"".join(out))


if __name__ == "__main__":
    write_pcap(Path(sys.argv[1]), build_packets())
