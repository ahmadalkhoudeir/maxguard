"""Tests for the OPNsense enforcer (Ahmad, AHM-08).

Never a real firewall: FakeOPNsense is a small HTTPS server on 127.0.0.1 that
answers the three alias endpoints the way OPNsense's AliasUtilController and
AliasController do. Its certificate comes from a test CA made here, so the tests
also prove that TLS verification is on. test_response_routes.py reuses it.
"""

from __future__ import annotations

import base64
import datetime
import ipaddress
import json
import socket
import ssl
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID

from maxguard import offline
from maxguard.offline import OfflineViolation
from maxguard.response.enforcers.base import EnforcerError
from maxguard.response.enforcers.opnsense import OPNsenseEnforcer, from_env, read_api_key

KEY = "test-key"
SECRET = "test-secret=="          # real secrets are base64 and may end in "="
FIREWALL_NAME = "fw.home.arpa"    # home.arpa is reserved for home networks (RFC 8375)


# ---------- a test certificate authority and server certificate ----------

def name(common_name: str) -> x509.Name:
    return x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, common_name)])


def make_certificates(folder: Path) -> tuple[Path, Path, Path]:
    """Returns (ca_file, server_cert_file, server_key_file)."""
    now = datetime.datetime.now(datetime.UTC)
    ca_key = ec.generate_private_key(ec.SECP256R1())
    ca_cert = (
        x509.CertificateBuilder().subject_name(name("MaxGuard test CA"))
        .issuer_name(name("MaxGuard test CA")).public_key(ca_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - datetime.timedelta(minutes=5))
        .not_valid_after(now + datetime.timedelta(days=1))
        .add_extension(x509.BasicConstraints(ca=True, path_length=0), critical=True)
        .add_extension(x509.KeyUsage(digital_signature=False, content_commitment=False,
                                     key_encipherment=False, data_encipherment=False,
                                     key_agreement=False, key_cert_sign=True, crl_sign=True,
                                     encipher_only=False, decipher_only=False), critical=True)
        .add_extension(x509.SubjectKeyIdentifier.from_public_key(ca_key.public_key()),
                       critical=False)
        .sign(ca_key, hashes.SHA256()))
    server_key = ec.generate_private_key(ec.SECP256R1())
    server_cert = (
        x509.CertificateBuilder().subject_name(name(FIREWALL_NAME))
        .issuer_name(ca_cert.subject).public_key(server_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - datetime.timedelta(minutes=5))
        .not_valid_after(now + datetime.timedelta(days=1))
        .add_extension(x509.SubjectAlternativeName([
            x509.DNSName(FIREWALL_NAME), x509.IPAddress(ipaddress.ip_address("127.0.0.1"))]),
            critical=False)
        .add_extension(x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH]), critical=False)
        .add_extension(x509.AuthorityKeyIdentifier.from_issuer_public_key(ca_key.public_key()),
                       critical=False)
        .sign(ca_key, hashes.SHA256()))
    ca_file, cert_file, key_file = folder / "ca.pem", folder / "server.pem", folder / "key.pem"
    ca_file.write_bytes(ca_cert.public_bytes(serialization.Encoding.PEM))
    cert_file.write_bytes(server_cert.public_bytes(serialization.Encoding.PEM))
    key_file.write_bytes(server_key.private_bytes(serialization.Encoding.PEM,
                                                  serialization.PrivateFormat.PKCS8,
                                                  serialization.NoEncryption()))
    return ca_file, cert_file, key_file


# ---------- the fake firewall ----------

class FakeOPNsense:
    """Remembers the alias contents and every request it was sent."""

    def __init__(self, folder: Path):
        self.aliases: dict[str, set[str]] = {"maxguard_block_in": set(),
                                             "maxguard_block_out": set()}
        self.requests: list[tuple[str, dict]] = []
        self.reconfigures = 0
        self.redirects: dict[str, str] = {}  # path -> where to send the client instead
        self.ca_file, cert_file, key_file = make_certificates(folder)
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(cert_file, key_file)
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), self.handler_class())
        self.server.socket = context.wrap_socket(self.server.socket, server_side=True)
        self.port = self.server.server_address[1]
        self.url = f"https://127.0.0.1:{self.port}"
        # A short poll interval makes stop() quick (the default waits up to 0.5 s).
        self.thread = threading.Thread(target=self.server.serve_forever, args=(0.05,),
                                       daemon=True)
        self.thread.start()

    def stop(self) -> None:
        self.server.shutdown()
        self.server.server_close()

    def answer(self, path: str, body: dict) -> tuple[int, dict]:
        """What OPNsense would answer (see AliasUtilController.php / AliasController.php)."""
        self.requests.append((path, body))
        parts = path.strip("/").split("/")
        if parts[:3] == ["api", "firewall", "alias_util"] and len(parts) == 5:
            action, alias = parts[3], parts[4]
            if alias not in self.aliases or "address" not in body:
                return 200, {"status": "failed"}
            if action == "add":
                self.aliases[alias].add(body["address"])
                return 200, {"status": "done"}
            if action == "delete":
                self.aliases[alias].discard(body["address"])
                return 200, {"status": "done"}
        if parts == ["api", "firewall", "alias", "reconfigure"]:
            self.reconfigures += 1
            return 200, {"status": "ok"}
        return 404, {"message": "not found"}

    def handler_class(self):
        fake = self
        expected = "Basic " + base64.b64encode(f"{KEY}:{SECRET}".encode()).decode()

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):  # noqa: N802 (the name http.server expects)
                length = int(self.headers.get("Content-Length", 0))
                body = json.loads(self.rfile.read(length) or b"{}")
                if self.path in fake.redirects:
                    fake.requests.append((self.path, body))
                    self.send_response(307)
                    self.send_header("Location", fake.redirects[self.path])
                    self.send_header("Content-Length", "0")
                    self.end_headers()
                    return
                if self.headers.get("Authorization") != expected:
                    status, answer = 401, {"message": "Authentication Failed"}
                else:
                    status, answer = fake.answer(self.path, body)
                data = json.dumps(answer).encode()
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def log_message(self, *args):  # keep the test output quiet
                pass

        return Handler


@pytest.fixture
def firewall(tmp_path):
    fake = FakeOPNsense(tmp_path)
    yield fake
    fake.stop()


def enforcer(fake: FakeOPNsense, alias: str = "maxguard_block_in", **kwargs):
    options = {"ca_file": str(fake.ca_file), **kwargs}
    return OPNsenseEnforcer(fake.url, KEY, SECRET, alias=alias, **options)


# ---------- tests ----------

def test_add_apply_remove(firewall):
    client = enforcer(firewall)
    client.add("203.0.113.7")
    client.apply()
    assert firewall.aliases["maxguard_block_in"] == {"203.0.113.7"}
    assert firewall.reconfigures == 1
    client.remove("203.0.113.7")
    client.apply()
    assert firewall.aliases["maxguard_block_in"] == set()
    assert [path for path, _ in firewall.requests] == [
        "/api/firewall/alias_util/add/maxguard_block_in",
        "/api/firewall/alias/reconfigure",
        "/api/firewall/alias_util/delete/maxguard_block_in",
        "/api/firewall/alias/reconfigure",
    ]


def test_ipv6_is_sent_in_its_short_lower_case_form(firewall):
    # OPNsense's addAction refuses characters outside [0-9a-f:./_] (no upper case).
    enforcer(firewall, alias="maxguard_block_out").add("2001:DB8:0:0:0:0:0:7")
    assert firewall.aliases["maxguard_block_out"] == {"2001:db8::7"}


def test_tls_is_verified(firewall):
    # Without the firewall's CA file the certificate is not trusted: refused.
    client = OPNsenseEnforcer(firewall.url, KEY, SECRET, alias="maxguard_block_in")
    with pytest.raises(EnforcerError, match="CERTIFICATE_VERIFY_FAILED|certificate verify"):
        client.add("203.0.113.7")
    assert firewall.requests == []


def test_plain_http_is_refused():
    with pytest.raises(ValueError, match="https"):
        OPNsenseEnforcer("http://127.0.0.1:8443", KEY, SECRET, alias="maxguard_block_in")


def test_bad_alias_name_is_refused():
    with pytest.raises(ValueError):
        OPNsenseEnforcer("https://127.0.0.1", KEY, SECRET, alias="x/../../core")


def test_wrong_secret_is_an_error(firewall):
    client = OPNsenseEnforcer(firewall.url, KEY, "wrong", alias="maxguard_block_in",
                              ca_file=str(firewall.ca_file))
    with pytest.raises(EnforcerError, match="401"):
        client.add("203.0.113.7")
    assert firewall.aliases["maxguard_block_in"] == set()


def test_redirects_are_not_followed(firewall):
    # A redirect could send the request (and the API key) somewhere else: refuse it.
    firewall.redirects["/api/firewall/alias_util/add/maxguard_block_in"] = (
        firewall.url + "/api/firewall/alias_util/add/maxguard_block_out")
    with pytest.raises(EnforcerError, match="307"):
        enforcer(firewall).add("203.0.113.7")
    assert len(firewall.requests) == 1
    assert firewall.aliases["maxguard_block_out"] == set()


def test_unknown_alias_is_an_error(firewall):
    with pytest.raises(EnforcerError, match="failed"):
        enforcer(firewall, alias="not_there").add("203.0.113.7")


@pytest.mark.parametrize("text", ["1.2.3.4; rm -rf /", "127.0.0.1", "2001:db8::1%$(id)"])
def test_hostile_input_never_reaches_the_firewall(firewall, text):
    with pytest.raises(ValueError):
        enforcer(firewall).add(text)
    assert firewall.requests == []


def test_unreachable_firewall_is_an_error(tmp_path):
    with socket.socket() as probe:  # a port with nothing listening
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]
    client = OPNsenseEnforcer(f"https://127.0.0.1:{port}", KEY, SECRET,
                              alias="maxguard_block_in")
    with pytest.raises(EnforcerError, match="not reachable"):
        client.add("203.0.113.7")


def test_read_api_key(tmp_path):
    key_file = tmp_path / "apikey.txt"
    key_file.write_text(f"key={KEY}\nsecret={SECRET}\n")
    assert read_api_key(key_file) == (KEY, SECRET)
    key_file.write_text(f"key={KEY}\n")
    with pytest.raises(EnforcerError, match="secret"):
        read_api_key(key_file)


def test_from_env(tmp_path, monkeypatch, firewall):
    monkeypatch.delenv("MAXGUARD_OPNSENSE_URL", raising=False)
    assert from_env(tmp_path, "maxguard_block_in") is None  # not configured: manual steps

    monkeypatch.setenv("MAXGUARD_OPNSENSE_URL", firewall.url)
    monkeypatch.setenv("MAXGUARD_OPNSENSE_CA", str(firewall.ca_file))
    with pytest.raises(EnforcerError, match="apikey.txt"):
        from_env(tmp_path, "maxguard_block_in")              # the key file is missing

    (tmp_path / "opnsense").mkdir()
    (tmp_path / "opnsense" / "apikey.txt").write_text(f"key={KEY}\nsecret={SECRET}\n")
    from_env(tmp_path, "maxguard_block_in").add("198.51.100.20")
    assert firewall.aliases["maxguard_block_in"] == {"198.51.100.20"}


# ---------- with the offline guard on ----------

@pytest.fixture
def firewall_name(monkeypatch):
    """Make fw.home.arpa resolve to 127.0.0.1 (as a home router's DNS would)."""
    real_getaddrinfo = socket.getaddrinfo

    def fake_getaddrinfo(host, *args, **kwargs):
        if host == FIREWALL_NAME:
            host = "127.0.0.1"
        return real_getaddrinfo(host, *args, **kwargs)

    monkeypatch.setattr(socket, "getaddrinfo", fake_getaddrinfo)
    yield
    offline.disable()  # before monkeypatch puts the real getaddrinfo back


def test_works_with_the_guard_on_when_the_firewall_is_allowed(firewall, firewall_name):
    # The same as MAXGUARD_OFFLINE=1 with MAXGUARD_OFFLINE_ALLOW=fw.home.arpa
    offline.enable("http://127.0.0.1:11434", extra_allowed=[FIREWALL_NAME])
    client = OPNsenseEnforcer(f"https://{FIREWALL_NAME}:{firewall.port}", KEY, SECRET,
                              alias="maxguard_block_in", ca_file=str(firewall.ca_file))
    client.add("203.0.113.7")  # only the firewall is contacted, never 203.0.113.7
    client.apply()
    assert firewall.aliases["maxguard_block_in"] == {"203.0.113.7"}


def test_guard_stops_a_firewall_that_is_not_allowed(firewall, firewall_name):
    offline.enable("http://127.0.0.1:11434")  # MAXGUARD_OFFLINE_ALLOW not set
    client = OPNsenseEnforcer(f"https://{FIREWALL_NAME}:{firewall.port}", KEY, SECRET,
                              alias="maxguard_block_in", ca_file=str(firewall.ca_file))
    with pytest.raises(EnforcerError, match="MAXGUARD_OFFLINE_ALLOW") as caught:
        client.add("203.0.113.7")
    assert isinstance(caught.value.__cause__, OfflineViolation)
    assert firewall.requests == []
