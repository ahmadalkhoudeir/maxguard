"""Send a multipart body with a big file part (WITH a Content-Length header) to a route
that is not an upload route, and watch the server's temp files while it reads.
usage: form_route_spool.py PORT PID TMPDIR METHOD PATH MIB"""
import os, socket, sys, time
port, pid, tmpdir, method, path, mib = int(sys.argv[1]), sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], int(sys.argv[6])
MIB = 1024 * 1024
def tmp_bytes():
    t = 0
    for fd in os.listdir(f"/proc/{pid}/fd"):
        try:
            if os.readlink(f"/proc/{pid}/fd/{fd}").startswith(tmpdir):
                t += os.stat(f"/proc/{pid}/fd/{fd}").st_size
        except OSError:
            pass
    return t
head = (b'--B\r\nContent-Disposition: form-data; name="mode"\r\n\r\nhome\r\n'
        b'--B\r\nContent-Disposition: form-data; name="junk"; filename="big.bin"\r\n\r\n')
tail = b"\r\n--B--\r\n"
length = len(head) + mib * MIB + len(tail)
s = socket.create_connection(("127.0.0.1", port))
s.sendall((f"{method} {path} HTTP/1.1\r\nHost: 127.0.0.1:{port}\r\n"
           f"Content-Type: multipart/form-data; boundary=B\r\nContent-Length: {length}\r\n\r\n").encode() + head)
peak = 0
for i in range(mib):
    s.sendall(b"\0" * MIB)
    if (i + 1) % 10 == 0:
        time.sleep(0.3)
        peak = max(peak, tmp_bytes())
        print(f"sent {i+1} MiB (announced in Content-Length): server temp file = {tmp_bytes()/MIB:.1f} MiB")
s.sendall(tail)
s.settimeout(10)
reply = s.recv(300)
status = reply.partition(bytes([13, 10]))[0].decode()
print(f"{method} {path}: answer {status!r}; peak temp {peak/MIB:.1f} MiB")
