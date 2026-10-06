"""Build rdp.pcap: two RDP connection starts, fully synthetic.

None of the lab captures contains RDP, so this script writes the packets byte
by byte (standard library only). Zeek 9.0.0 then turns the capture into the
rdp.log and conn.log next to this file, so the field names and values are the
real ones, not guesses.

Each connection is only the first RDP exchange (MS-RDPBCGR 2.2.1.1 and 2.2.1.2):
the client's X.224 Connection Request and the server's X.224 Connection Confirm,
whose RDP_NEG_RSP says which security protocol the server picked. That one
value is what Zeek logs as rdp.log `security_protocol`:
- old server 192.168.56.30 picks PROTOCOL_RDP (0) -> "RDP" (Standard RDP Security)
- new server 192.168.56.31 picks PROTOCOL_HYBRID (2) -> "HYBRID" (TLS + CredSSP)

Addresses: 192.168.56.0/24 (private lab range), MACs start with 02 (locally
administered, made up). The cookie user name "labuser" is made up too.

Run:  python make_rdp_pcap.py rdp.pcap
"""

from __future__ import annotations

import struct
import sys
from pathlib import Path

START_TS = 1791253200.0  # 2026-10-06 02:20:00 UTC (after the other hand-made fixtures)

CLIENT_MAC = bytes.fromhex("020000aabbcc")
SERVER_MAC = bytes.fromhex("020000000002")

CLIENT_IP = "192.168.56.50"
OLD_SERVER_IP = "192.168.56.30"  # answers with Standard RDP Security
NEW_SERVER_IP = "192.168.56.31"  # answers with HYBRID (Network Level Authentication)
RDP_PORT = 3389

# RDP_NEG_REQ / RDP_NEG_RSP protocol values (MS-RDPBCGR 2.2.1.1.1 and 2.2.1.2.1)
PROTOCOL_RDP = 0x00
PROTOCOL_SSL = 0x01
PROTOCOL_HYBRID = 0x02

# TCP flag bits
FIN, SYN, PSH, ACK = 0x01, 0x02, 0x08, 0x10


def ip_bytes(ip: str) -> bytes:
    return bytes(int(part) for part in ip.split("."))


def checksum(data: bytes) -> int:
    """The 16-bit one's complement sum used by IPv4 and TCP headers."""
    if len(data) % 2:
        data += b"\x00"
    total = sum(struct.unpack(f"!{len(data) // 2}H", data))
    while total > 0xFFFF:
        total = (total & 0xFFFF) + (total >> 16)
    return ~total & 0xFFFF


def tcp_packet(src_ip: str, dst_ip: str, sport: int, dport: int, seq: int, ack: int,
               flags: int, payload: bytes, ip_id: int) -> bytes:
    """Ethernet + IPv4 + TCP (20-byte header, no options) around a payload."""
    src_mac, dst_mac = (CLIENT_MAC, SERVER_MAC) if src_ip == CLIENT_IP else (SERVER_MAC, CLIENT_MAC)
    header = struct.pack("!HHIIBBHHH", sport, dport, seq, ack, 5 << 4, flags, 65535, 0, 0)
    # The TCP checksum covers a "pseudo header" with both IPs, then header + data.
    pseudo = ip_bytes(src_ip) + ip_bytes(dst_ip) + struct.pack("!BBH", 0, 6,
                                                                len(header) + len(payload))
    header = header[:16] + struct.pack("!H", checksum(pseudo + header + payload)) + header[18:]
    tcp = header + payload
    ip = struct.pack("!BBHHHBBH4s4s", 0x45, 0, 20 + len(tcp), ip_id, 0x4000, 64, 6, 0,
                     ip_bytes(src_ip), ip_bytes(dst_ip))
    ip = ip[:10] + struct.pack("!H", checksum(ip)) + ip[12:]
    return dst_mac + src_mac + b"\x08\x00" + ip + tcp


def tpkt(x224: bytes) -> bytes:
    """TPKT header (RFC 1006): version 3, reserved 0, total length, big-endian."""
    return struct.pack("!BBH", 3, 0, 4 + len(x224)) + x224


def connection_request(cookie: str, requested_protocols: int) -> bytes:
    """Client X.224 Connection Request PDU (MS-RDPBCGR 2.2.1.1)."""
    cookie_bytes = f"Cookie: mstshash={cookie}\r\n".encode("ascii")
    neg_req = struct.pack("<BBHI", 0x01, 0, 8, requested_protocols)  # RDP_NEG_REQ
    body = struct.pack("!BHHB", 0xE0, 0, 0, 0) + cookie_bytes + neg_req  # CR, refs, class 0
    return tpkt(bytes([len(body)]) + body)  # first byte = X.224 length indicator


def connection_confirm(selected_protocol: int) -> bytes:
    """Server X.224 Connection Confirm PDU (MS-RDPBCGR 2.2.1.2)."""
    neg_rsp = struct.pack("<BBHI", 0x02, 0, 8, selected_protocol)  # RDP_NEG_RSP
    body = struct.pack("!BHHB", 0xD0, 0, 0x1234, 0) + neg_rsp  # CC, refs, class 0
    return tpkt(bytes([len(body)]) + body)


def rdp_session(server_ip: str, client_port: int, request: bytes, confirm: bytes,
                start: float, first_ip_id: int) -> list[tuple[float, bytes]]:
    """Handshake, one request, one confirm, then a clean close (FIN both ways)."""
    c_seq, s_seq = 1000, 5000  # fixed initial sequence numbers: same bytes every run
    c_end = c_seq + 1 + len(request)  # client's next sequence number after its data
    s_end = s_seq + 1 + len(confirm)
    # (sent by client?, seq, ack, flags, data)
    steps = [
        (True, c_seq, 0, SYN, b""),
        (False, s_seq, c_seq + 1, SYN | ACK, b""),
        (True, c_seq + 1, s_seq + 1, ACK, b""),
        (True, c_seq + 1, s_seq + 1, PSH | ACK, request),
        (False, s_seq + 1, c_end, PSH | ACK, confirm),
        (True, c_end, s_end, FIN | ACK, b""),
        (False, s_end, c_end + 1, FIN | ACK, b""),
        (True, c_end + 1, s_end + 1, ACK, b""),
    ]
    packets = []
    for i, (from_client, seq, ack, flags, data) in enumerate(steps):
        if from_client:
            frame = tcp_packet(CLIENT_IP, server_ip, client_port, RDP_PORT,
                               seq, ack, flags, data, first_ip_id + i)
        else:
            frame = tcp_packet(server_ip, CLIENT_IP, RDP_PORT, client_port,
                               seq, ack, flags, data, first_ip_id + i)
        packets.append((start + i * 0.001, frame))
    return packets


def build_packets() -> list[tuple[float, bytes]]:
    # A legacy client that asks only for Standard RDP Security, and a server that agrees.
    old = rdp_session(OLD_SERVER_IP, 50001,
                      connection_request("labuser", PROTOCOL_RDP),
                      connection_confirm(PROTOCOL_RDP), START_TS, 1)
    # A modern client offering TLS or CredSSP; the server picks CredSSP (HYBRID).
    new = rdp_session(NEW_SERVER_IP, 50002,
                      connection_request("labuser", PROTOCOL_SSL | PROTOCOL_HYBRID),
                      connection_confirm(PROTOCOL_HYBRID), START_TS + 1.0, 101)
    return old + new


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
