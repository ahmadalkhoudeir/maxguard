"""Ask the lab DNS server (UDP port 53) for three made-up names."""
import socket
import struct

from _common import SERVER, finish, wait_for_sniffer

NAMES = ["printer.lab.invalid", "nas.lab.invalid", "camera.lab.invalid"]

def dns_query(txid, name):
    # flags 0x0100 = "recursion desired"; one question of type A (1), class IN (1)
    labels = b"".join(bytes([len(part)]) + part.encode() for part in name.split("."))
    return struct.pack("!HHHHHH", txid, 0x0100, 1, 0, 0, 0) + labels + b"\x00\x00\x01\x00\x01"

wait_for_sniffer()
server_ip = socket.gethostbyname(SERVER)  # Docker's built-in DNS: not on the captured link
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.settimeout(5)
    for txid, name in enumerate(NAMES, start=0x1001):
        s.sendto(dns_query(txid, name), (server_ip, 53))
        s.recv(512)  # wait for each answer so the capture has query + reply pairs
finish()
