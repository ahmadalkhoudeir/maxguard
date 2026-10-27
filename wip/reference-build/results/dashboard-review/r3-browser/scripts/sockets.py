"""Remote peers of every TCP socket a process holds (from /proc), to show nothing leaves 127.0.0.1."""
import os, sys
pid = sys.argv[1]
inodes = set()
for fd in os.listdir(f"/proc/{pid}/fd"):
    try:
        link = os.readlink(f"/proc/{pid}/fd/{fd}")
    except OSError:
        continue
    if link.startswith("socket:["):
        inodes.add(link[8:-1])
def addr(hexaddr, v6):
    host, port = hexaddr.split(":")
    if v6:
        b = bytes.fromhex(host)
        words = [b[i:i+4][::-1].hex() for i in range(0, 16, 4)]
        ip = ":".join(w[j:j+4] for w in words for j in (0, 4))
    else:
        ip = ".".join(str(int(host[i:i+2], 16)) for i in (6, 4, 2, 0))
    return f"{ip}:{int(port, 16)}"
rows = []
for name, v6 in (("/proc/net/tcp", False), ("/proc/net/tcp6", True)):
    if not os.path.exists(name):
        continue
    for line in open(name).read().splitlines()[1:]:
        f = line.split()
        if f[9] in inodes:
            rows.append((addr(f[1], v6), addr(f[2], v6), {"01": "ESTABLISHED", "0A": "LISTEN"}.get(f[3], f[3])))
for local, remote, state in sorted(rows):
    print(f"  {state:12} local {local:22} remote {remote}")
print("non-loopback peers:", [r for r in rows if r[2] != "LISTEN" and not r[1].startswith(("127.", "0.0.0.0:0", "0000:0000:0000:0000:0000:0000:0000:0000"))])
