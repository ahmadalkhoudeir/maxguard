"""Offline guard: make any accidental internet access fail loudly (CLAUDE.md rule 1).

When enabled, Python code in this process may only talk to:
- this machine (127.0.0.1, ::1, localhost, any loopback address),
- the local Ollama server (its host name and the IPs it resolves to),
- hosts the caller lists explicitly (for example the user's own firewall).

It wraps the four socket methods that send to an address we choose (connect,
connect_ex, sendto, sendmsg), so TCP and UDP are both covered, and the
functions that look up host names, so no DNS query for an unknown name is made.
The Fall 2026 version only wrapped connect/connect_ex, so UDP packets and DNS
lookups still got out.

This is a guard against mistakes inside MaxGuard's own Python code, not a
sandbox: programs started as subprocesses are not covered. The Docker network
setup (Ollama on an internal-only network) is the outer wall.
"""

from __future__ import annotations

import ipaddress
import os
import socket
from collections.abc import Iterable
from urllib.parse import urlparse

ALWAYS_ALLOWED = ("127.0.0.1", "::1", "localhost")
INTERNET_FAMILIES = (socket.AF_INET, socket.AF_INET6)

# Socket methods that send to an address we pass in. sendmsg does not exist on
# Windows, so only the methods this Python has are wrapped.
SOCKET_METHODS = [m for m in ("connect", "connect_ex", "sendto", "sendmsg")
                  if hasattr(socket.socket, m)]
LOOKUP_FUNCTIONS = ("getaddrinfo", "gethostbyname", "gethostbyname_ex")

_allowed: set[str] = set()  # lower-case host names and IP addresses
_original_methods: dict[str, object] = {}
_original_lookups: dict[str, object] = {}


class OfflineViolation(RuntimeError):
    """Raised instead of letting a connection or DNS lookup leave the machine."""


def enable(ollama_url: str, extra_allowed: Iterable[str] = ()) -> None:
    """Turn the guard on. extra_allowed: more hosts the user owns, e.g. a firewall."""
    disable()  # start clean if enable() is called twice
    hosts = {*ALWAYS_ALLOWED, *extra_allowed}
    ollama_host = host_of(ollama_url)
    if ollama_host:
        hosts.add(ollama_host)
    for host in hosts:
        _allowed.add(clean(host))
        _allowed.update(resolve(host))  # the real lookup: nothing is wrapped yet
    wrap_socket_methods()
    wrap_lookups()


def disable() -> None:
    """Put the original socket functions back (used by tests)."""
    for name, original in _original_methods.items():
        setattr(socket.socket, name, original)
    for name, original in _original_lookups.items():
        setattr(socket, name, original)
    _original_methods.clear()
    _original_lookups.clear()
    _allowed.clear()


def is_enabled() -> bool:
    return bool(_original_lookups)


def allowed_hosts() -> list[str]:
    return sorted(_allowed)


def enable_from_env() -> bool:
    """Turn the guard on when MAXGUARD_OFFLINE=1. Returns True if it is on.

    MAXGUARD_OFFLINE_ALLOW may list extra user-owned hosts, comma-separated.
    """
    if os.environ.get("MAXGUARD_OFFLINE") != "1":
        return False
    from maxguard.ai.ollama_client import ollama_url  # one place reads OLLAMA_HOST

    extra = [h.strip() for h in os.environ.get("MAXGUARD_OFFLINE_ALLOW", "").split(",")]
    enable(ollama_url(), [h for h in extra if h])
    return True


# ---- helpers -------------------------------------------------------------

def host_of(url: str) -> str | None:
    """'http://ollama:11434' -> 'ollama'. Also accepts 'ollama:11434'."""
    if "://" not in url:
        url = "http://" + url
    return urlparse(url).hostname


def clean(host: str | bytes) -> str:
    """One spelling per host: text, lower case, no trailing dot."""
    if isinstance(host, bytes):
        host = host.decode("ascii", errors="replace")
    return host.lower().rstrip(".")


def resolve(host: str) -> set[str]:
    """IP addresses for a name, looked up once while enabling the guard."""
    try:
        results = socket.getaddrinfo(host, None)
    except socket.gaierror:
        return set()  # not resolvable yet (e.g. the Ollama container is starting)
    return {clean(info[4][0]) for info in results}


def is_local_ip(host: str) -> bool:
    """True for loopback (127.x.x.x, ::1) and 'any address' (0.0.0.0, ::)."""
    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        return False  # a host name, not an IP address
    return ip.is_loopback or ip.is_unspecified


def is_allowed(host: str | bytes | None) -> bool:
    if host is None:  # getaddrinfo(None, port) means "this machine", e.g. for a server
        return True
    name = clean(host)
    return name in _allowed or is_local_ip(name)


def check_address(sock: socket.socket, address: object) -> None:
    # Only internet sockets are checked. Unix sockets and other families stay
    # on this machine, and their addresses are not (host, port) pairs.
    if sock.family not in INTERNET_FAMILIES:
        return
    host, port = address[0], address[1]
    if not is_allowed(host):
        raise OfflineViolation(f"OFFLINE MODE: blocked network access to {host}:{port}. "
                               f"Allowed hosts: {', '.join(allowed_hosts())}")


def check_lookup(host: str | bytes | None) -> None:
    if not is_allowed(host):
        raise OfflineViolation(f"OFFLINE MODE: blocked address lookup of {host!r}. "
                               f"Allowed hosts: {', '.join(allowed_hosts())}")


# ---- wrapped socket methods ---------------------------------------------

def guarded_connect(self, address):
    check_address(self, address)
    return _original_methods["connect"](self, address)


def guarded_connect_ex(self, address):
    check_address(self, address)
    return _original_methods["connect_ex"](self, address)


def guarded_sendto(self, data, *args):
    # sendto(data, address) or sendto(data, flags, address): address is last.
    if args:
        check_address(self, args[-1])
    return _original_methods["sendto"](self, data, *args)


def guarded_sendmsg(self, buffers, *args):
    # sendmsg(buffers, ancdata, flags, address): the address is optional, 4th.
    if len(args) >= 3:
        check_address(self, args[2])
    return _original_methods["sendmsg"](self, buffers, *args)


GUARDED_METHODS = {"connect": guarded_connect, "connect_ex": guarded_connect_ex,
                   "sendto": guarded_sendto, "sendmsg": guarded_sendmsg}


def wrap_socket_methods() -> None:
    for name in SOCKET_METHODS:
        _original_methods[name] = getattr(socket.socket, name)
        setattr(socket.socket, name, GUARDED_METHODS[name])


# ---- wrapped name lookups -----------------------------------------------

def guarded_getaddrinfo(host, *args, **kwargs):
    check_lookup(host)
    results = _original_lookups["getaddrinfo"](host, *args, **kwargs)
    # An allowed name (e.g. the "ollama" container) can get a new IP after a
    # restart. The name is trusted, so the addresses it points to now are too.
    _allowed.update(clean(info[4][0]) for info in results)
    return results


def guarded_gethostbyname(host):
    check_lookup(host)
    ip = _original_lookups["gethostbyname"](host)
    _allowed.add(clean(ip))  # same reason as in guarded_getaddrinfo
    return ip


def guarded_gethostbyname_ex(host):
    check_lookup(host)
    name, aliases, ips = _original_lookups["gethostbyname_ex"](host)
    _allowed.update(clean(ip) for ip in ips)
    return name, aliases, ips


GUARDED_LOOKUPS = {"getaddrinfo": guarded_getaddrinfo,
                   "gethostbyname": guarded_gethostbyname,
                   "gethostbyname_ex": guarded_gethostbyname_ex}


def wrap_lookups() -> None:
    for name in LOOKUP_FUNCTIONS:
        _original_lookups[name] = getattr(socket, name)
        setattr(socket, name, GUARDED_LOOKUPS[name])
