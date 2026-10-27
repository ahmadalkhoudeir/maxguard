"""Upload the telnet log zip under hostile file names (raw multipart, so NUL and
other bytes curl will not send can be used). usage: hostile_names.py PORT ZIPFILE"""
import json
import socket
import sys

port, zip_path = int(sys.argv[1]), sys.argv[2]
data = open(zip_path, "rb").read()
NAMES = [
    b"../../evil.zip",
    b"evil\x00.pcap/../../../x.zip",
    b"\x00",
    b"..\\..\\windows\\evil.zip",
    b"/etc/passwd",
    b'a";filename="../../b.zip',
    b"<img src=x onerror=alert(1)>.zip",
    b"x" * 5000 + b".zip",
]


def post(filename: bytes) -> tuple[str, bytes]:
    body = (b"--B\r\nContent-Disposition: form-data; name=\"file\"; filename=\"" + filename
            + b"\"\r\nContent-Type: application/zip\r\n\r\n" + data + b"\r\n--B--\r\n")
    head = (f"POST /api/analyses HTTP/1.1\r\nHost: 127.0.0.1:{port}\r\n"
            "Content-Type: multipart/form-data; boundary=B\r\n"
            f"Content-Length: {len(body)}\r\nConnection: close\r\n\r\n").encode()
    s = socket.create_connection(("127.0.0.1", port))
    s.sendall(head + body)
    reply = b""
    while chunk := s.recv(65536):
        reply += chunk
    s.close()
    status = reply.partition(b"\r\n")[0].decode()
    return status, reply.partition(b"\r\n\r\n")[2]


for name in NAMES:
    status, body = post(name)
    shown = name if len(name) < 60 else name[:20] + b"...(%d bytes)" % len(name)
    print(f"{shown!r:50} -> {status} {body[:60]!r}")
