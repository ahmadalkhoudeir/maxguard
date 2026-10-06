"""Fake Telnet, FTP and printer web services (Fiona, FIO-06).

Nothing legitimate on the network has a reason to contact these services, so
every connection is worth an alert. For each connection the decoy:

1. sends a fake banner (Telnet and FTP speak first; HTTP answers a request),
2. reads at most READ_LIMIT bytes, waiting at most `timeout` seconds,
3. writes one JSON line to decoy.log and closes the connection.

Safety (CLAUDE.md rule 5): the decoy only answers. This module never opens a
connection, never resolves a name and never sends anything except its banner
to the client that connected. It runs in its own container with its own IP
address, never on the sensor's capture interface.
"""

from __future__ import annotations

import asyncio
import functools
import json
import time
from collections.abc import Callable
from pathlib import Path

DEFAULT_PORTS = {"telnet": 23, "ftp": 21, "http": 80}
DEFAULT_TIMEOUT = 5.0  # seconds; a slow or silent client cannot keep a connection open
READ_LIMIT = 1024  # bytes; we never buffer more than this from one client
LOGGED_BYTES = 64  # bytes of what the client sent that go into decoy.log (as hex)

PRINTER_PAGE = (
    b"<!doctype html><html><head><title>Printer admin</title></head>"
    b"<body><h1>Printer admin</h1><form method=post>"
    b"<input name=user><input name=pass type=password><button>Log in</button>"
    b"</form></body></html>"
)
HTTP_RESPONSE = (
    b"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n"
    b"Content-Length: " + str(len(PRINTER_PAGE)).encode() + b"\r\n"
    b"Connection: close\r\n\r\n" + PRINTER_PAGE
)
# Sent as soon as a client connects (these protocols make the server speak first).
GREETINGS = {"telnet": b"login: ", "ftp": b"220 FTP server ready\r\n"}
# Sent after the client has said something (HTTP waits for the request).
REPLIES = {"http": HTTP_RESPONSE}


def parse_ports(text: str) -> dict[str, int]:
    """Turn "telnet=23,ftp=21,http=80" into {"telnet": 23, "ftp": 21, "http": 80}."""
    ports: dict[str, int] = {}
    for item in text.split(","):
        name, _, port = item.strip().partition("=")
        if name not in GREETINGS and name not in REPLIES:
            raise ValueError(f"unknown decoy service {name!r} (use telnet, ftp or http)")
        if not port.isdigit() or not 0 <= int(port) <= 65535:
            raise ValueError(f"bad port for {name}: {port!r}")
        ports[name] = int(port)
    return ports


def contact_record(service: str, peer: tuple, local: tuple, data: bytes, ts: float) -> dict:
    """The decoy.log line for one connection."""
    return {
        "ts": ts,
        "service": service,
        "src_ip": peer[0],
        "src_port": peer[1],
        "dst_ip": local[0],
        "dst_port": local[1],
        "first_bytes_hex": data[:LOGGED_BYTES].hex(),
    }


def append_line(log_path: Path, record: dict) -> None:
    # asyncio runs one handler at a time, so lines from two clients never mix.
    with log_path.open("a") as f:
        f.write(json.dumps(record, sort_keys=True) + "\n")


async def read_some(reader: asyncio.StreamReader, timeout: float) -> bytes:
    """Whatever the client sends first, capped at READ_LIMIT bytes; b"" if it stays silent."""
    try:
        return await asyncio.wait_for(reader.read(READ_LIMIT), timeout)
    except (TimeoutError, OSError):  # silent client, or it reset the connection
        return b""


async def send(writer: asyncio.StreamWriter, data: bytes) -> None:
    """Send data; a client that already left is not an error for a decoy."""
    try:
        writer.write(data)
        await writer.drain()
    except OSError:
        pass


async def close(writer: asyncio.StreamWriter) -> None:
    writer.close()
    try:
        await writer.wait_closed()
    except OSError:
        pass


async def handle(service: str, reader: asyncio.StreamReader, writer: asyncio.StreamWriter,
                 *, log_path: Path, timeout: float, clock: Callable[[], float]) -> None:
    """Answer one connection, log it, close it."""
    ts = clock()  # the time the client connected
    # (ip, port). IPv6 adds two more fields, which we drop. None if the client already left.
    peer = (writer.get_extra_info("peername") or ("", 0))[:2]
    local = (writer.get_extra_info("sockname") or ("", 0))[:2]
    data = b""
    try:
        if service in GREETINGS:
            await send(writer, GREETINGS[service])
        data = await read_some(reader, timeout)
        if service in REPLIES and data:
            await send(writer, REPLIES[service])
    finally:
        # Log even if something above failed: the contact itself is the evidence.
        append_line(log_path, contact_record(service, peer, local, data, ts))
        await close(writer)


async def start(ports: dict[str, int], log_path: Path, *, host: str = "0.0.0.0",
                timeout: float = DEFAULT_TIMEOUT,
                clock: Callable[[], float] = time.time) -> list[asyncio.Server]:
    """Start one listener per service. Port 0 picks a free port (used by the tests)."""
    servers = []
    for service, port in sorted(ports.items()):
        # partial() fixes everything except (reader, writer), which asyncio passes in.
        on_connect = functools.partial(handle, service, log_path=log_path, timeout=timeout,
                                       clock=clock)
        servers.append(await asyncio.start_server(on_connect, host, port))
    return servers


async def serve_forever(ports: dict[str, int], log_path: Path, *, host: str = "0.0.0.0",
                        timeout: float = DEFAULT_TIMEOUT) -> None:
    servers = await start(ports, log_path, host=host, timeout=timeout)
    for service, server in zip(sorted(ports), servers, strict=True):  # start() sorts too
        for sock in server.sockets:
            address, port = sock.getsockname()[:2]
            print(f"decoy {service} listening on {address}:{port}", flush=True)
    await asyncio.gather(*(server.serve_forever() for server in servers))
