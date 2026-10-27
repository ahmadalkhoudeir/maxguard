"""Announce a huge body (Content-Length 10 GiB) with a wrong or missing token, send only a
little of it, and see whether the server answers before the body arrives.

usage: huge_wrong_token.py PORT PID TMPDIR [TOKEN_FILE]
"""
import os
import socket
import sys
import time

port, pid, tmpdir = int(sys.argv[1]), sys.argv[2], sys.argv[3]
auth = ""
if len(sys.argv) > 4:
    auth = "Authorization: Bearer " + open(sys.argv[4]).read().strip() + "\r\n"
MIB = 1024 * 1024
ANNOUNCED = 10 * 1024 * MIB  # 10 GiB, never sent


def rss_kib():
    for line in open(f"/proc/{pid}/status"):
        if line.startswith("VmRSS"):
            return int(line.split()[1])


def tmp_bytes():
    total = 0
    for fd in os.listdir(f"/proc/{pid}/fd"):
        try:
            if os.readlink(f"/proc/{pid}/fd/{fd}").startswith(tmpdir):
                total += os.stat(f"/proc/{pid}/fd/{fd}").st_size
        except OSError:
            pass
    return total


s = socket.create_connection(("127.0.0.1", port))
print(f"before: rss={rss_kib()} KiB tmp={tmp_bytes()} B")
t0 = time.time()
s.sendall((f"POST /api/ingest HTTP/1.1\r\nHost: 127.0.0.1:{port}\r\n{auth}"
           "Content-Type: multipart/form-data; boundary=BOUNDARY\r\n"
           f"Content-Length: {ANNOUNCED}\r\n\r\n").encode())
s.sendall(b'--BOUNDARY\r\nContent-Disposition: form-data; name="file"; filename="x.tar.gz"'
          b"\r\n\r\n" + b"\x1f\x8b" + b"\0" * (64 * 1024))
s.settimeout(5)
reply = s.recv(4096)
status = reply.partition(b"\r\n")[0].decode() if reply else "none"
print(f"answer after {time.time()-t0:.3f}s with 64 KiB of {ANNOUNCED} bytes sent: {status}")
# keep sending: does the server read it, store it, or close the connection?
sent = 0
s.settimeout(10)
try:
    for _ in range(200):
        s.sendall(b"\0" * MIB)
        sent += MIB
except OSError as err:
    print(f"server stopped the upload after {sent // MIB} more MiB: {err!r}")
print(f"after sending {sent // MIB} more MiB: rss={rss_kib()} KiB tmp={tmp_bytes()} B")
s.close()
