"""PATCH /api/alerts/{id} with a huge JSON body (Content-Length announced) and report the
server's resident memory. usage: json_memory.py PORT PID FINDING_ID MIB"""
import socket, sys, time
port, pid, fid, mib = int(sys.argv[1]), sys.argv[2], sys.argv[3], int(sys.argv[4])
MIB = 1024 * 1024
def mem():
    d = {}
    for line in open(f"/proc/{pid}/status"):
        if line.startswith(("VmRSS", "VmHWM")):
            k, v = line.split(":")
            d[k] = int(v.split()[0]) // 1024
    return d
print("before:", mem(), "MiB")
head, tail = b'{"actor":"x","status":"new","assignee":"', b'"}'
s = socket.create_connection(("127.0.0.1", port))
s.sendall((f"PATCH /api/alerts/{fid} HTTP/1.1\r\nHost: 127.0.0.1:{port}\r\nContent-Type: application/json\r\n"
           f"Content-Length: {len(head) + mib * MIB + len(tail)}\r\n\r\n").encode() + head)
t0, sent = time.time(), 0
try:
    for _ in range(mib):
        s.sendall(b"a" * MIB)
        sent += 1
    s.sendall(tail)
except OSError as err:
    print(f"server closed the connection after {sent} MiB: {err!r}")
s.settimeout(60)
reply = s.recv(300)
status = reply.partition(b"\r\n")[0].decode()
print(f"PATCH with a {mib} MiB JSON body: {status!r} after {time.time() - t0:.1f}s")
time.sleep(1)
print("after:", mem(), "MiB (VmHWM = peak)")
