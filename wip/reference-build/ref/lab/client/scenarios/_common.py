"""Helpers shared by every scenario."""
import socket
import ssl
import time

SERVER = "server"

def wait_for_sniffer():
    time.sleep(3)  # give tcpdump time to start before we send anything

def finish():
    time.sleep(2)  # let the last packets reach tcpdump before the lab stops

def tls_get(port, minimum=ssl.TLSVersion.TLSv1, maximum=ssl.TLSVersion.TLSv1_3,
            ciphers="ALL:@SECLEVEL=0"):
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE  # lab certificates are fake on purpose
    ctx.minimum_version, ctx.maximum_version = minimum, maximum
    if ciphers:
        ctx.set_ciphers(ciphers)
    with socket.create_connection((SERVER, port), timeout=10) as raw:
        with ctx.wrap_socket(raw, server_hostname=f"port{port}.lab.invalid") as s:
            s.sendall(b"GET / HTTP/1.0\r\n\r\n")
            return s.recv(4096)
