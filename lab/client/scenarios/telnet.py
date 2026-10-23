import socket
import time

from _common import SERVER, finish, wait_for_sniffer

wait_for_sniffer()
s = socket.create_connection((SERVER, 23), timeout=10)
s.recv(4096)
for cmd in (b"labuser\r\n", b"whoami\r\n", b"exit\r\n"):
    s.sendall(cmd)
    time.sleep(0.5)
    try:
        s.recv(4096)
    except TimeoutError:
        pass
s.close()
finish()
