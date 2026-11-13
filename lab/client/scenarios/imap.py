import socket
import time

from _common import SERVER, finish, wait_for_sniffer

wait_for_sniffer()
s = socket.create_connection((SERVER, 143), timeout=10)
s.recv(4096)
for cmd in (b"a1 LOGIN labuser labpass\r\n", b"a2 LOGOUT\r\n"):
    s.sendall(cmd)
    time.sleep(0.5)
    s.recv(4096)
s.close()
finish()
