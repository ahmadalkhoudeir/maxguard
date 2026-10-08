"""Send a few made-up flow records to a NetFlow collector (Jakub, JAK-10 step 6).

NetFlow v5, NetFlow v9 and IPFIX, each with its own header. Only documentation
addresses (RFC 5737). Fixed times, so every run sends the same bytes. Send them
only to your own collector (docker/netflow-compose.yaml): the records are fake.

    python3 scripts/send_test_flows.py <collector-host> [port]
"""

from __future__ import annotations

import socket
import struct
import sys

EXPORT_TIME = 1791295200  # 2026-10-06 14:00:00 UTC
UPTIME_MS = 600_000       # the router has been up for 10 minutes
TCP, UDP, ICMP = 6, 17, 1


def ip(text: str) -> bytes:
    return socket.inet_aton(text)


# ---------- NetFlow v5 (fixed layout: 24-byte header, 48-byte records) ----------

def v5_record(src: str, dst: str, sport: int, dport: int, proto: int,
              packets: int, octets: int, first_ms: int, last_ms: int) -> bytes:
    """One NetFlow v5 flow record. first/last are router uptimes in milliseconds."""
    tcp_flags = 0x1B if proto == TCP else 0  # FIN SYN PSH ACK
    return struct.pack("!4s4s4sHHIIIIHHBBBBHHBBH",
                       ip(src), ip(dst), ip("0.0.0.0"), 1, 2,  # next hop, in/out interface
                       packets, octets, first_ms, last_ms,
                       sport, dport, 0, tcp_flags, proto, 0,   # pad, flags, protocol, ToS
                       0, 0, 24, 24, 0)                        # AS numbers, masks, pad


def v5_packet(records: list[bytes], sequence: int) -> bytes:
    header = struct.pack("!HHIIIIBBH", 5, len(records), UPTIME_MS, EXPORT_TIME, 0,
                         sequence, 0, 0, 0)
    return header + b"".join(records)


# ---------- NetFlow v9 (RFC 3954) and IPFIX (RFC 7011): template, then data ----------

# (field type, length): IPv4 src, IPv4 dst, src port, dst port, protocol, bytes, packets
V9_FIELDS = [(8, 4), (12, 4), (7, 2), (11, 2), (4, 1), (1, 4), (2, 4), (22, 4), (21, 4)]
#                                                        FIRST_SWITCHED^  ^LAST_SWITCHED
IPFIX_FIELDS = [(8, 4), (12, 4), (7, 2), (11, 2), (4, 1), (1, 8), (2, 8), (152, 8), (153, 8)]
#                                              flowStartMilliseconds^    ^flowEndMilliseconds


def template_body(template_id: int, fields: list[tuple[int, int]]) -> bytes:
    body = struct.pack("!HH", template_id, len(fields))
    return body + b"".join(struct.pack("!HH", t, n) for t, n in fields)


def flow_set(set_id: int, body: bytes) -> bytes:
    return struct.pack("!HH", set_id, 4 + len(body)) + body


def v9_packet(sequence: int) -> bytes:
    """Template 256 (flowset id 0), then one data record: an SSH flow."""
    data = struct.pack("!4s4sHHBIIII", ip("192.0.2.12"), ip("198.51.100.22"), 50022, 22,
                       TCP, 4200, 30, UPTIME_MS - 8000, UPTIME_MS - 1000)
    flowsets = flow_set(0, template_body(256, V9_FIELDS)) + flow_set(256, data)
    # version, count (records incl. template), sysUptime, unix secs, sequence, source id
    return struct.pack("!HHIIII", 9, 2, UPTIME_MS, EXPORT_TIME, sequence, 1) + flowsets


def ipfix_packet(sequence: int) -> bytes:
    """Template 256 (set id 2), then one data record: an HTTPS flow."""
    start_ms = EXPORT_TIME * 1000 - 5000
    data = struct.pack("!4s4sHHBQQQQ", ip("192.0.2.11"), ip("203.0.113.5"), 50000, 443,
                       TCP, 5200, 14, start_ms, start_ms + 3000)
    sets = flow_set(2, template_body(256, IPFIX_FIELDS)) + flow_set(256, data)
    return struct.pack("!HHIII", 10, 16 + len(sets), EXPORT_TIME, sequence, 1) + sets


def main() -> None:
    host = sys.argv[1]
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 2055
    telnet = v5_record("192.0.2.10", "198.51.100.20", 49152, 23, TCP, 12, 900, 590_000, 592_000)
    answer = v5_record("198.51.100.20", "192.0.2.10", 23, 49152, TCP, 10, 1400, 590_010, 592_000)
    web = v5_record("192.0.2.10", "198.51.100.20", 49153, 80, TCP, 6, 640, 595_000, 595_500)
    dns = v5_record("192.0.2.10", "198.51.100.53", 40000, 53, UDP, 1, 60, 596_000, 596_000)
    ping = v5_record("192.0.2.10", "198.51.100.20", 0, 8 * 256 + 0, ICMP, 1, 84,
                     597_000, 597_000)  # echo request: type 8, code 0
    packets = [v5_packet([telnet, answer], 0), v5_packet([web, dns, ping], 2),
               v9_packet(0), ipfix_packet(0)]
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        for packet in packets:
            sock.sendto(packet, (host, port))
    print(f"sent {len(packets)} packets (2 NetFlow v5, 1 NetFlow v9, 1 IPFIX) to {host}:{port}")


if __name__ == "__main__":
    main()
