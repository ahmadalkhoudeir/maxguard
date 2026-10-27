"""A fake OPNsense on 127.0.0.1 for the AHM-04 review (row 9). Synthetic only.

Modes:
  http        plain HTTP (no TLS at all)
  selfsigned  HTTPS with a self-signed leaf certificate (issuer == subject, no CA)
  privateca   HTTPS with a leaf signed by a private test CA (SAN 127.0.0.1)
  wrongname   HTTPS with a leaf from the private CA, valid only for fw.home.arpa

Every HTTP request that reaches the handler is recorded in .requests, and every
TLS handshake failure in .tls_errors, so the review can prove whether the
console's API call reached the "firewall".
"""
from __future__ import annotations

import base64
import datetime
import ipaddress
import json
import ssl
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID

KEY = "review-key"
SECRET = "review-secret=="


def _name(cn):
    return x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, cn)])


def _pem_key(k):
    return k.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
                           serialization.NoEncryption())


def make_certs(folder: Path, mode: str):
    """Returns (ca_file or None, cert_file, key_file)."""
    now = datetime.datetime.now(datetime.UTC)
    folder.mkdir(parents=True, exist_ok=True)
    leaf_key = ec.generate_private_key(ec.SECP256R1())
    if mode == "selfsigned":
        cert = (x509.CertificateBuilder().subject_name(_name("127.0.0.1"))
                .issuer_name(_name("127.0.0.1")).public_key(leaf_key.public_key())
                .serial_number(x509.random_serial_number())
                .not_valid_before(now - datetime.timedelta(minutes=5))
                .not_valid_after(now + datetime.timedelta(days=1))
                .add_extension(x509.SubjectAlternativeName(
                    [x509.IPAddress(ipaddress.ip_address("127.0.0.1"))]), critical=False)
                .sign(leaf_key, hashes.SHA256()))
        (folder / "leaf.pem").write_bytes(cert.public_bytes(serialization.Encoding.PEM))
        (folder / "leaf.key").write_bytes(_pem_key(leaf_key))
        return None, folder / "leaf.pem", folder / "leaf.key"
    ca_key = ec.generate_private_key(ec.SECP256R1())
    ca = (x509.CertificateBuilder().subject_name(_name("review CA")).issuer_name(_name("review CA"))
          .public_key(ca_key.public_key()).serial_number(x509.random_serial_number())
          .not_valid_before(now - datetime.timedelta(minutes=5))
          .not_valid_after(now + datetime.timedelta(days=1))
          .add_extension(x509.BasicConstraints(ca=True, path_length=0), critical=True)
          .add_extension(x509.KeyUsage(False, False, False, False, False, True, True, False, False),
                         critical=True)
          .add_extension(x509.SubjectKeyIdentifier.from_public_key(ca_key.public_key()),
                         critical=False)
          .sign(ca_key, hashes.SHA256()))
    if mode == "wrongname":
        sans = [x509.DNSName("fw.home.arpa")]
    else:
        sans = [x509.DNSName("fw.home.arpa"), x509.IPAddress(ipaddress.ip_address("127.0.0.1"))]
    leaf = (x509.CertificateBuilder().subject_name(_name("fw.home.arpa")).issuer_name(ca.subject)
            .public_key(leaf_key.public_key()).serial_number(x509.random_serial_number())
            .not_valid_before(now - datetime.timedelta(minutes=5))
            .not_valid_after(now + datetime.timedelta(days=1))
            .add_extension(x509.SubjectAlternativeName(sans), critical=False)
            .add_extension(x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH]), critical=False)
            .add_extension(x509.AuthorityKeyIdentifier.from_issuer_public_key(ca_key.public_key()),
                           critical=False)
            .sign(ca_key, hashes.SHA256()))
    (folder / "ca.pem").write_bytes(ca.public_bytes(serialization.Encoding.PEM))
    (folder / "leaf.pem").write_bytes(leaf.public_bytes(serialization.Encoding.PEM))
    (folder / "leaf.key").write_bytes(_pem_key(leaf_key))
    return folder / "ca.pem", folder / "leaf.pem", folder / "leaf.key"


class FakeFirewall:
    def __init__(self, folder: Path, mode: str):
        self.mode = mode
        self.requests: list[tuple[str, str, dict]] = []
        self.tls_errors: list[str] = []
        self.aliases = {"maxguard_block_in": set(), "maxguard_block_out": set()}
        fake = self
        expected = "Basic " + base64.b64encode(f"{KEY}:{SECRET}".encode()).decode()

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):  # noqa: N802
                length = int(self.headers.get("Content-Length", 0))
                body = json.loads(self.rfile.read(length) or b"{}")
                fake.requests.append(("POST", self.path, body))
                if self.headers.get("Authorization") != expected:
                    status, answer = 401, {"message": "Authentication Failed"}
                else:
                    parts = self.path.strip("/").split("/")
                    status, answer = 404, {"message": "not found"}
                    if parts[:3] == ["api", "firewall", "alias_util"] and len(parts) == 5:
                        alias = fake.aliases.get(parts[4])
                        if alias is None:
                            status, answer = 200, {"status": "failed"}
                        elif parts[3] == "add":
                            alias.add(body["address"])
                            status, answer = 200, {"status": "done"}
                        elif parts[3] == "delete":
                            alias.discard(body["address"])
                            status, answer = 200, {"status": "done"}
                    elif parts == ["api", "firewall", "alias", "reconfigure"]:
                        status, answer = 200, {"status": "ok"}
                data = json.dumps(answer).encode()
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def log_message(self, *args):
                pass

        class Server(ThreadingHTTPServer):
            def handle_error(self, request, client_address):  # TLS handshake errors land here
                import sys
                fake.tls_errors.append(repr(sys.exc_info()[1]))

        self.server = Server(("127.0.0.1", 0), Handler)
        self.ca_file = None
        if mode != "http":
            self.ca_file, cert, key = make_certs(folder, mode)
            ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            ctx.load_cert_chain(cert, key)
            # Handshake in the worker thread, so a failed handshake is recorded, not fatal.
            self.server.socket = ctx.wrap_socket(self.server.socket, server_side=True,
                                                 do_handshake_on_connect=False)

            orig = Handler.setup

            def setup(handler_self):
                try:
                    handler_self.request.do_handshake()
                except (ssl.SSLError, OSError) as err:
                    fake.tls_errors.append(repr(err))
                    raise
                orig(handler_self)
            Handler.setup = setup
        scheme = "http" if mode == "http" else "https"
        self.url = f"{scheme}://127.0.0.1:{self.server.server_address[1]}"
        self.thread = threading.Thread(target=self.server.serve_forever, args=(0.05,), daemon=True)
        self.thread.start()

    def stop(self):
        self.server.shutdown()
        self.server.server_close()
