"""Tests for the decoy service and rule decoy.contact (Fiona, FIO-06).

The decoy listens on 127.0.0.1 with port 0 (the system picks a free port), so
the tests need no root, no Docker and no network.
"""

from __future__ import annotations

import asyncio
import json
import socket

import pytest

from maxguard.decoy import service
from maxguard.ids import record_id
from maxguard.rules.base import RULES, merge

# Importing the module registers decoy.contact. It is not in maxguard/rules/__init__.py
# yet, because a new rule ID needs the Security Lead's approval.
from maxguard.rules.decoy import decoy_contact

FIXED_TS = 1791250284.5  # the tests pass a fixed clock, so decoy.log is predictable
LINE = {"ts": FIXED_TS, "service": "telnet", "src_ip": "192.0.2.10", "src_port": 50000,
        "dst_ip": "192.0.2.250", "dst_port": 23, "first_bytes_hex": "726f6f740d0a"}


@pytest.fixture
def connects(monkeypatch):
    """Record every outgoing connection made in this process (the test client's too)."""
    made: list[tuple] = []
    real_connect, real_connect_ex = socket.socket.connect, socket.socket.connect_ex

    def connect(sock, address):
        made.append(tuple(address[:2]))
        return real_connect(sock, address)

    def connect_ex(sock, address):
        made.append(tuple(address[:2]))
        return real_connect_ex(sock, address)

    monkeypatch.setattr(socket.socket, "connect", connect)
    monkeypatch.setattr(socket.socket, "connect_ex", connect_ex)
    return made


async def talk(port: int, send: bytes, *, close_early: bool = False) -> bytes:
    """Connect like an attacker would: read the banner, send something, read the answer."""
    reader, writer = await asyncio.open_connection("127.0.0.1", port)
    if close_early:
        writer.close()
        return b""
    if send:
        writer.write(send)
        await writer.drain()
    answer = await reader.read()  # until the decoy closes the connection
    writer.close()
    return answer


async def run_decoys(log_path, clients: list[tuple[str, bytes]]) -> list[bytes]:
    servers = await service.start({"telnet": 0, "ftp": 0, "http": 0}, log_path,
                                  host="127.0.0.1", timeout=0.3, clock=lambda: FIXED_TS)
    ports = {name: srv.sockets[0].getsockname()[1]
             for name, srv in zip(sorted(["telnet", "ftp", "http"]), servers, strict=True)}
    try:
        return [await talk(ports[name], data) for name, data in clients]
    finally:
        for srv in servers:
            srv.close()
            await srv.wait_closed()


def read_lines(path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines()]


def test_service_logs_a_connection_and_never_connects_out(tmp_path, connects):
    log_path = tmp_path / "decoy.log"
    answers = asyncio.run(run_decoys(log_path, [("telnet", b"root\r\n")]))

    assert answers == [b"login: "]
    [line] = read_lines(log_path)
    assert line["ts"] == FIXED_TS
    assert line["service"] == "telnet"
    assert line["src_ip"] == "127.0.0.1" and line["dst_ip"] == "127.0.0.1"
    assert isinstance(line["src_port"], int) and isinstance(line["dst_port"], int)
    assert bytes.fromhex(line["first_bytes_hex"]) == b"root\r\n"
    # The only connection in this process is the test's own, to the decoy.
    assert connects == [("127.0.0.1", line["dst_port"])]


def test_each_service_has_its_banner(tmp_path):
    answers = asyncio.run(run_decoys(tmp_path / "decoy.log", [
        ("ftp", b"USER admin\r\n"), ("http", b"GET / HTTP/1.1\r\nHost: printer\r\n\r\n")]))
    assert answers[0] == b"220 FTP server ready\r\n"
    assert answers[1].startswith(b"HTTP/1.1 200 OK")
    assert b"<title>Printer admin</title>" in answers[1]


def test_only_the_first_64_bytes_are_logged(tmp_path):
    log_path = tmp_path / "decoy.log"
    asyncio.run(run_decoys(log_path, [("http", b"A" * 5000)]))
    [line] = read_lines(log_path)
    assert bytes.fromhex(line["first_bytes_hex"]) == b"A" * 64


def test_silent_client_is_logged_after_the_timeout(tmp_path):
    log_path = tmp_path / "decoy.log"
    asyncio.run(run_decoys(log_path, [("ftp", b"")]))  # connects, sends nothing
    [line] = read_lines(log_path)
    assert line["first_bytes_hex"] == ""


def test_garbage_and_early_close_do_not_stop_the_decoy(tmp_path):
    log_path = tmp_path / "decoy.log"

    async def scenario():
        servers = await service.start({"telnet": 0}, log_path, host="127.0.0.1",
                                      timeout=0.3, clock=lambda: FIXED_TS)
        port = servers[0].sockets[0].getsockname()[1]
        await talk(port, bytes(range(256)) * 8)  # binary garbage, not valid Telnet
        await talk(port, b"", close_early=True)  # hangs up before the banner is read
        answer = await talk(port, b"admin\r\n")  # the decoy still answers afterwards
        servers[0].close()
        await servers[0].wait_closed()
        return answer

    assert asyncio.run(scenario()) == b"login: "
    assert len(read_lines(log_path)) == 3


def test_parse_ports():
    assert service.parse_ports("telnet=2323, http=8080") == {"telnet": 2323, "http": 8080}
    with pytest.raises(ValueError):
        service.parse_ports("ssh=22")
    with pytest.raises(ValueError):
        service.parse_ports("ftp=21x")


def test_rule_turns_a_decoy_log_line_into_one_finding(tmp_path):
    (tmp_path / "decoy.log").write_text(json.dumps(LINE) + "\n")
    [finding] = decoy_contact(tmp_path)
    assert finding.rule_id == "decoy.contact"
    assert finding.severity == "critical"
    assert finding.source == "decoy"
    assert (finding.src_ip, finding.dst_ip, finding.dst_port) == ("192.0.2.10", "192.0.2.250", 23)
    assert finding.protocol == "telnet"
    assert finding.first_seen == finding.last_seen == FIXED_TS
    # The evidence ID is the hash of the decoy.log line, so the AI can cite it.
    assert finding.evidence[0].log == "decoy.log"
    assert finding.evidence[0].record_id == record_id("decoy.log", LINE)


def test_repeated_contacts_merge_into_one_finding(tmp_path):
    second = {**LINE, "ts": FIXED_TS + 60, "src_port": 50001}
    (tmp_path / "decoy.log").write_text(json.dumps(LINE) + "\n" + json.dumps(second) + "\n")
    [finding] = merge(decoy_contact(tmp_path))
    assert finding.count == 2
    assert (finding.first_seen, finding.last_seen) == (FIXED_TS, FIXED_TS + 60)


def test_no_decoy_log_means_no_findings(tmp_path):
    assert decoy_contact(tmp_path) == []


def test_rule_registers_when_imported():
    assert RULES["decoy.contact"] is decoy_contact


def test_service_end_to_end_with_the_rule(tmp_path):
    asyncio.run(run_decoys(tmp_path / "decoy.log", [("http", b"GET / HTTP/1.1\r\n\r\n")]))
    [finding] = decoy_contact(tmp_path)
    assert finding.protocol == "http" and finding.src_ip == "127.0.0.1"
