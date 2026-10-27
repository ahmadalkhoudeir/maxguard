"""Chunked upload that grows past MAXGUARD_MAX_UPLOAD_MB, watching the server's temp folder.

usage: chunked_growth.py PORT PID TMPDIR TOTAL_MIB [PATH] [AUTH_TOKEN_FILE]
Sends a multipart body with Transfer-Encoding: chunked (no Content-Length), one MiB
per chunk. After every 5 MiB it pauses, then prints: bytes sent, total size of files
in the server's TMPDIR, the server's RSS, and whether the server has answered yet.
"""
import os
import select
import socket
import sys
import time

port, pid, tmpdir, total_mib = int(sys.argv[1]), sys.argv[2], sys.argv[3], int(sys.argv[4])
path = sys.argv[5] if len(sys.argv) > 5 else "/api/analyses"
auth = ""
if len(sys.argv) > 6:
    auth = "Authorization: Bearer " + open(sys.argv[6]).read().strip() + "\r\n"
MIB = 1024 * 1024


def tmp_bytes():
    """Size of the files the server holds open in TMPDIR. Python's TemporaryFile has no
    name in the folder (O_TMPFILE / unlinked), so look through /proc/PID/fd instead."""
    total = 0
    for fd in os.listdir(f"/proc/{pid}/fd"):
        try:
            target = os.readlink(f"/proc/{pid}/fd/{fd}")
            if target.startswith(tmpdir):
                total += os.stat(f"/proc/{pid}/fd/{fd}").st_size
        except OSError:
            pass
    return total


def rss_kib():
    for line in open(f"/proc/{pid}/status"):
        if line.startswith("VmRSS"):
            return int(line.split()[1])


def chunk(data: bytes) -> bytes:
    return b"%x\r\n" % len(data) + data + b"\r\n"


s = socket.create_connection(("127.0.0.1", port))
s.sendall((f"POST {path} HTTP/1.1\r\nHost: 127.0.0.1:{port}\r\n{auth}"
           "Content-Type: multipart/form-data; boundary=BOUNDARY\r\n"
           "Transfer-Encoding: chunked\r\n\r\n").encode())
s.sendall(chunk(b'--BOUNDARY\r\nContent-Disposition: form-data; name="file"; '
                b'filename="big.pcap"\r\nContent-Type: application/octet-stream\r\n\r\n'))
print(f"start: tmp={tmp_bytes()} B rss={rss_kib()} KiB")
t0 = time.time()
block = b"\xd4\xc3\xb2\xa1" + b"\0" * (MIB - 4)
answered = None
for i in range(1, total_mib + 1):
    try:
        s.sendall(chunk(block if i == 1 else b"\0" * MIB))
    except OSError as err:
        print(f"send failed after {i-1} MiB: {err!r}")
        break
    if i % 5 == 0:
        time.sleep(0.7)
        ready = select.select([s], [], [], 0)[0]
        if ready and answered is None:
            answered = s.recv(200)
        print(f"sent {i:3d} MiB: server tmp={tmp_bytes()/MIB:6.1f} MiB rss={rss_kib()} KiB "
              f"answered_yet={'yes' if answered else 'no'}")
s.sendall(chunk(b"\r\n--BOUNDARY--\r\n") + b"0\r\n\r\n")
reply = answered or b""
s.settimeout(30)
while b"\r\n\r\n" not in reply:
    reply += s.recv(65536)
status_line, _, rest = reply.partition(b"\r\n")
body = reply.partition(b"\r\n\r\n")[2]
print(f"reply after {time.time()-t0:.2f}s: {status_line.decode()} body={body[:80]!r}")
time.sleep(0.5)
print(f"end: tmp={tmp_bytes()} B rss={rss_kib()} KiB")
