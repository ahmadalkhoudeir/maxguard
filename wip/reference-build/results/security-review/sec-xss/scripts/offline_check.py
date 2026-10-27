"""Offline guard (JON-03): does an accidental outside connection fail loudly, BEFORE
any packet or DNS query? python offline_check.py <repo> [--no-spy]

With the spy (default), the real socket functions under the guard are replaced by
recorders that never touch the network, so nothing can leave even if the guard
failed. --no-spy is for the docker --network none run.
"""

from __future__ import annotations

import os
import socket
import sys

repo = sys.argv[1]
SPY = "--no-spy" not in sys.argv
sys.path.insert(0, repo)

reached: list[tuple] = []
if SPY:
    def recorder(name):
        def fn(*args, **kwargs):
            reached.append((name, args[1:] if name in ("connect", "connect_ex", "sendto") else args[:1]))
            raise OSError(f"SPY: real {name} was reached")
        return fn
    for name in ("connect", "connect_ex", "sendto", "sendmsg"):
        setattr(socket.socket, name, recorder(name))
    for name in ("getaddrinfo", "gethostbyname", "gethostbyname_ex"):
        real = getattr(socket, name)

        def wrap(*args, _real=real, _name=name, **kwargs):
            host = args[0] if args else None
            if host in ("127.0.0.1", "localhost", "::1", None):
                return _real(*args, **kwargs)  # enable() resolves the allowed names
            reached.append((_name, args[:1]))
            raise socket.gaierror(f"SPY: real {_name} was reached")
        setattr(socket, name, wrap)

import requests  # noqa: E402

from maxguard import offline  # noqa: E402
from maxguard.ai import ollama_client  # noqa: E402

offline.enable("http://127.0.0.1:11434")
print("guard on; allowed:", offline.allowed_hosts())


def attempt(label, fn):
    before = len(reached)
    try:
        fn()
        outcome = "NO ERROR"
    except offline.OfflineViolation as e:
        outcome = f"OfflineViolation: {e}"
    except Exception as e:  # noqa: BLE001
        outcome = f"{type(e).__module__}.{type(e).__name__}: {e}"
    new = reached[before:]
    print(f"{label:58} -> {outcome[:150]}" + (f"  REAL CALLS: {new}" if new else ""))


def udp(addr):
    with socket.socket(socket.AF_INET6 if ":" in addr[0] else socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.sendto(b"x", addr)


def tcp(addr):
    with socket.socket(socket.AF_INET6 if ":" in addr[0] else socket.AF_INET) as s:
        s.connect(addr)


attempt("requests.get http://192.0.2.1/", lambda: requests.get("http://192.0.2.1/", timeout=2))
attempt("requests.get http://3221225985/ (192.0.2.1 as one integer)",
        lambda: requests.get("http://3221225985/", timeout=2))
attempt("socket.create_connection(('192.0.2.1', 80))",
        lambda: socket.create_connection(("192.0.2.1", 80), timeout=2))
attempt("raw TCP socket.connect(('192.0.2.1', 443))", lambda: tcp(("192.0.2.1", 443)))
attempt("raw TCP connect(('::ffff:192.0.2.1', 443)) IPv4-mapped", lambda: tcp(("::ffff:192.0.2.1", 443)))
attempt("raw TCP connect(('2001:db8::1', 443)) IPv6 doc range", lambda: tcp(("2001:db8::1", 443)))
attempt("UDP sendto(b'x', ('192.0.2.1', 53))", lambda: udp(("192.0.2.1", 53)))
attempt("DNS socket.getaddrinfo('example.com', 80)", lambda: socket.getaddrinfo("example.com", 80))
attempt("DNS socket.gethostbyname('example.com')", lambda: socket.gethostbyname("example.com"))

# the AI client is the guarded code path that talks to the network: point it somewhere else
os.environ["OLLAMA_HOST"] = "http://192.0.2.1:11434"
body = ollama_client.chat_request({"rule_id": "r", "title": "t", "severity": "high", "protocol": "p",
                                   "src_ip": "a", "dst_ip": "b", "dst_port": 1, "count": 1,
                                   "details": {}, "controls": [], "attack": []}, {"id": {}})
attempt("ollama_client.post_chat with OLLAMA_HOST=192.0.2.1 (after enable)",
        lambda: ollama_client.post_chat(body))
os.environ["OLLAMA_HOST"] = "http://ollama.example:11434"
attempt("ollama_client.post_chat with OLLAMA_HOST=ollama.example", lambda: ollama_client.post_chat(body))

# loopback still works (closed port -> ConnectionRefusedError from the real stack)
if not SPY:
    attempt("loopback 127.0.0.1:9 (closed port) still allowed",
            lambda: socket.create_connection(("127.0.0.1", 9), timeout=2))
print("real network functions reached for outside addresses:", reached if SPY else "(spy off)")
