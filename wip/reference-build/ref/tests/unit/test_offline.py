"""Tests for maxguard.offline.

No test here can reach the internet. Before the guard is enabled, the "real"
socket functions are swapped for recorders, so if the guard ever let a call
through, the recorder would get it, not the network. Blocked addresses come
from the documentation ranges (192.0.2.0/24, RFC 5737), which nothing uses.
"""

import ipaddress
import socket
from types import SimpleNamespace

import pytest

from maxguard import offline
from maxguard.offline import OfflineViolation


@pytest.fixture
def net(monkeypatch):
    """Fake network: records every call and answers DNS from a small table."""
    net = SimpleNamespace(calls=[], dns={"localhost": "127.0.0.1", "ollama": "172.20.0.5",
                                         "fw.home.arpa": "192.168.1.1"})

    def fake_getaddrinfo(host, port, *args, **kwargs):
        net.calls.append(("getaddrinfo", host))
        ip = net.dns.get(host, host)
        try:
            ipaddress.ip_address(ip)
        except ValueError:
            raise socket.gaierror(socket.EAI_NONAME, "Name or service not known") from None
        family = socket.AF_INET6 if ":" in ip else socket.AF_INET
        return [(family, socket.SOCK_STREAM, 6, "", (ip, port or 0))]

    def fake_gethostbyname(host):
        net.calls.append(("gethostbyname", host))
        return net.dns[host]

    def fake_connect(sock, address):
        net.calls.append(("connect", address))

    def fake_connect_ex(sock, address):
        net.calls.append(("connect_ex", address))
        return 0

    def fake_sendto(sock, data, *args):
        net.calls.append(("sendto", args[-1]))
        return len(data)

    def fake_sendmsg(sock, buffers, *args):
        net.calls.append(("sendmsg", args[2] if len(args) >= 3 else None))
        return 0

    monkeypatch.setattr(socket, "getaddrinfo", fake_getaddrinfo)
    monkeypatch.setattr(socket, "gethostbyname", fake_gethostbyname)
    monkeypatch.setattr(socket.socket, "connect", fake_connect)
    monkeypatch.setattr(socket.socket, "connect_ex", fake_connect_ex)
    monkeypatch.setattr(socket.socket, "sendto", fake_sendto)
    monkeypatch.setattr(socket.socket, "sendmsg", fake_sendmsg, raising=False)
    yield net
    offline.disable()  # runs before monkeypatch puts the real functions back


def sent(net) -> list:
    """Calls that would have put a packet on the wire."""
    return [c for c in net.calls if c[0] != "getaddrinfo"]


# ---- blocked ---------------------------------------------------------------

def test_tcp_connect_to_the_internet_is_blocked(net):
    offline.enable("http://127.0.0.1:11434")
    with socket.socket() as s:
        with pytest.raises(OfflineViolation, match="192.0.2.1:443"):
            s.connect(("192.0.2.1", 443))
        with pytest.raises(OfflineViolation):
            s.connect_ex(("192.0.2.1", 443))
    assert sent(net) == []


def test_create_connection_fails_at_the_dns_step(net):
    offline.enable("http://127.0.0.1:11434")
    with pytest.raises(OfflineViolation, match="address lookup"):
        socket.create_connection(("192.0.2.1", 443), timeout=2)
    assert ("getaddrinfo", "192.0.2.1") not in net.calls  # the resolver was never asked
    assert sent(net) == []


def test_udp_sendto_is_blocked(net):
    # Fall 2026 bug: only connect() was guarded, so UDP still got out.
    offline.enable("http://127.0.0.1:11434")
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        with pytest.raises(OfflineViolation):
            s.sendto(b"x", ("192.0.2.1", 53))
        with pytest.raises(OfflineViolation):
            s.sendto(b"x", 0, ("192.0.2.1", 53))  # the form with flags
    assert sent(net) == []


@pytest.mark.skipif(not hasattr(socket.socket, "sendmsg"), reason="no sendmsg on Windows")
def test_udp_sendmsg_is_blocked(net):
    offline.enable("http://127.0.0.1:11434")
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    with pytest.raises(OfflineViolation):
        s.sendmsg([b"x"], [], 0, ("192.0.2.1", 53))
    s.close()
    assert sent(net) == []


def test_dns_lookup_of_unknown_name_is_blocked(net):
    # Fall 2026 bug: lookups were not guarded, so DNS queries still got out.
    offline.enable("http://127.0.0.1:11434")
    with pytest.raises(OfflineViolation, match="example.com"):
        socket.getaddrinfo("example.com", 443)
    with pytest.raises(OfflineViolation):
        socket.gethostbyname("example.com")
    assert ("getaddrinfo", "example.com") not in net.calls


# ---- allowed ---------------------------------------------------------------

def test_this_machine_is_allowed(net):
    offline.enable("http://127.0.0.1:11434")
    with socket.socket() as s:
        s.connect(("127.0.0.1", 11434))
        s.connect(("localhost", 8000))
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.sendto(b"x", ("127.0.0.53", 53))  # any 127.x.x.x is this machine
    assert len(sent(net)) == 3


def test_ollama_host_and_its_ip_are_allowed(net):
    offline.enable("http://ollama:11434")
    assert socket.getaddrinfo("ollama", 11434)[0][4][0] == "172.20.0.5"
    with socket.socket() as s:
        s.connect(("172.20.0.5", 11434))
    assert ("connect", ("172.20.0.5", 11434)) in net.calls


def test_new_ip_of_an_allowed_name_is_learned(net):
    offline.enable("http://ollama:11434")
    net.dns["ollama"] = "172.20.0.9"  # the Ollama container restarted with a new IP
    socket.getaddrinfo("ollama", 11434)
    with socket.socket() as s:
        s.connect(("172.20.0.9", 11434))
    assert ("connect", ("172.20.0.9", 11434)) in net.calls


def test_extra_allowlist_for_the_users_own_firewall(net):
    offline.enable("http://127.0.0.1:11434", extra_allowed=["fw.home.arpa"])
    with socket.socket() as s:
        s.connect(("192.168.1.1", 443))
        with pytest.raises(OfflineViolation):
            s.connect(("192.168.1.2", 443))  # same network, but not on the list
    assert sent(net) == [("connect", ("192.168.1.1", 443))]


@pytest.mark.skipif(not hasattr(socket, "AF_UNIX"), reason="no Unix sockets on this OS")
def test_unix_sockets_are_not_checked(net):
    offline.enable("http://127.0.0.1:11434")
    with socket.socket(socket.AF_UNIX) as s:
        s.connect("/run/example.sock")
    assert net.calls[-1] == ("connect", "/run/example.sock")


# ---- on and off ------------------------------------------------------------

def test_disable_puts_the_original_functions_back(net):
    fake = socket.getaddrinfo
    offline.enable("http://127.0.0.1:11434")
    assert socket.getaddrinfo is not fake
    offline.disable()
    assert socket.getaddrinfo is fake
    assert not offline.is_enabled()


def test_enable_from_env(net, monkeypatch):
    monkeypatch.delenv("MAXGUARD_OFFLINE", raising=False)
    assert offline.enable_from_env() is False
    assert not offline.is_enabled()

    monkeypatch.setenv("MAXGUARD_OFFLINE", "1")
    monkeypatch.setenv("OLLAMA_HOST", "ollama:11434")
    monkeypatch.setenv("MAXGUARD_OFFLINE_ALLOW", "fw.home.arpa, 10.9.9.9")
    assert offline.enable_from_env() is True
    allowed = offline.allowed_hosts()
    for host in ("ollama", "172.20.0.5", "fw.home.arpa", "192.168.1.1", "10.9.9.9"):
        assert host in allowed


def test_real_socket_to_closed_local_port_is_refused_not_blocked():
    # No fakes: a real TCP connect to this machine. "Connection refused" is the
    # normal answer from a closed port; the guard must not get in the way.
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]  # a free port; closing it leaves nothing listening
    offline.enable("http://127.0.0.1:11434")
    try:
        with pytest.raises(ConnectionRefusedError):
            socket.create_connection(("127.0.0.1", port), timeout=2)
    finally:
        offline.disable()
