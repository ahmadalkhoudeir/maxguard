"""All lab services in one process. Every protocol here is insecure on purpose."""
import socketserver
import ssl
import struct
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer


class Telnet(socketserver.StreamRequestHandler):
    def handle(self):
        self.wfile.write(b"lab login: ")
        for line in self.rfile:
            self.wfile.write(b"$ " + line)
            if line.strip() == b"exit":
                break

class POP3(socketserver.StreamRequestHandler):
    def handle(self):
        self.wfile.write(b"+OK POP3 ready\r\n")
        for line in self.rfile:
            self.wfile.write(b"+OK\r\n")
            if line.upper().startswith(b"QUIT"):
                break

class IMAP(socketserver.StreamRequestHandler):
    def handle(self):
        self.wfile.write(b"* OK IMAP4rev1 ready\r\n")
        for line in self.rfile:
            self.wfile.write(line.split(b" ", 1)[0] + b" OK done\r\n")
            if b"LOGOUT" in line.upper():
                break

LAB_ANSWER_IP = bytes([10, 99, 0, 7])  # made-up address, never a real host

def dns_reply(query):
    """Answer one DNS question: every A query gets LAB_ANSWER_IP, anything else "no records"."""
    txid = query[:2]
    end = query.index(b"\x00", 12) + 5  # the name ends with a zero byte, then type + class
    question = query[12:end]
    qtype = struct.unpack("!H", query[end - 4:end - 2])[0]
    # flags 0x8180 = response + recursion desired + recursion available, NOERROR
    if qtype != 1:
        return txid + struct.pack("!HHHHH", 0x8180, 1, 0, 0, 0) + question
    # 0xc00c points back to the name in the question (offset 12); TTL 300 s
    answer = struct.pack("!HHHIH", 0xC00C, 1, 1, 300, 4) + LAB_ANSWER_IP
    return txid + struct.pack("!HHHHH", 0x8180, 1, 1, 0, 0) + question + answer

class DNS(socketserver.BaseRequestHandler):
    def handle(self):
        query, sock = self.request  # UDP: one datagram per request
        sock.sendto(dns_reply(query), self.client_address)

class Hello(socketserver.StreamRequestHandler):
    def handle(self):
        self.rfile.readline()
        self.wfile.write(b"HTTP/1.0 200 OK\r\nContent-Length: 2\r\n\r\nok")

def serve(server):
    threading.Thread(target=server.serve_forever, daemon=True).start()

def tls_server(port, cert, minimum, maximum, ciphers):
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.minimum_version, ctx.maximum_version = minimum, maximum
    if ciphers:
        ctx.set_ciphers(ciphers)
    ctx.load_cert_chain(f"/srv/{cert}.crt", f"/srv/{cert}.key")
    srv = socketserver.ThreadingTCPServer(("0.0.0.0", port), Hello)
    srv.socket = ctx.wrap_socket(srv.socket, server_side=True)
    serve(srv)

socketserver.ThreadingTCPServer.allow_reuse_address = True
for port, handler in ((23, Telnet), (110, POP3), (143, IMAP)):
    serve(socketserver.ThreadingTCPServer(("0.0.0.0", port), handler))
for port in (80, 8080):
    handler = partial(SimpleHTTPRequestHandler, directory="/srv")
    serve(ThreadingHTTPServer(("0.0.0.0", port), handler))
serve(socketserver.ThreadingUDPServer(("0.0.0.0", 53), DNS))

V = ssl.TLSVersion
LEGACY = "ALL:@SECLEVEL=0"
tls_server(4431, "good", V.TLSv1, V.TLSv1, LEGACY)                    # TLS 1.0
tls_server(4432, "good", V.TLSv1_2, V.TLSv1_2, "NULL-SHA256:@SECLEVEL=0")  # no encryption
tls_server(4433, "expired", V.TLSv1_2, V.TLSv1_2, LEGACY)             # expired cert
tls_server(4434, "weak", V.TLSv1_2, V.TLSv1_2, LEGACY)                # 1024-bit key
tls_server(4435, "sha1", V.TLSv1_2, V.TLSv1_2, LEGACY)                # SHA-1 signature
tls_server(4436, "good", V.TLSv1_3, V.TLSv1_3, None)                  # clean TLS 1.3
tls_server(4437, "selfsigned", V.TLSv1_2, V.TLSv1_2, None)            # self-signed cert

auth = DummyAuthorizer()
auth.add_user("labuser", "labpass", "/srv", perm="elr")
FTPHandler.authorizer = auth
print("lab services running", flush=True)
FTPServer(("0.0.0.0", 21), FTPHandler).serve_forever()
