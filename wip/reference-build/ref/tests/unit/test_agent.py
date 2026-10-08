"""Tests for the host agent (Jakub, JAK-11).

No test starts a capture: the commands are only built and compared. Uploads go
to a fake HTTP server on 127.0.0.1 and to the real ingest app through TestClient.
"""

from __future__ import annotations

import os
import shutil
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

from maxguard.sensor import agent
from maxguard.sensor.agent import AgentConfig

TOKEN = "test-token-" + "x" * 32  # made up; the API wants at least 32 characters
FLOW_FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "netflow" / "goflow2.json"


def make_config(spool: Path, **changes) -> AgentConfig:
    settings = {"console_url": "http://127.0.0.1:8001", "token": TOKEN, "spool_dir": spool,
                "sensor_id": "laptop", "interface": "eth0", "rotate_seconds": 900,
                "capture_user": "alex"}
    settings.update(changes)
    return AgentConfig(**settings)


def make_captures(spool: Path, *names: str) -> None:
    spool.mkdir(parents=True, exist_ok=True)
    for name in names:
        (spool / name).write_bytes(b"\xd4\xc3\xb2\xa1" + b"\0" * 20)  # a pcap header


# ---------- capture commands ----------

@pytest.mark.parametrize("system", ["Linux", "Darwin"])
def test_tcpdump_command(system, tmp_path):
    command = agent.capture_command(system, make_config(tmp_path), now=0)
    assert command == ["tcpdump", "-i", "eth0", "-n", "-G", "900",
                       "-w", str(tmp_path / "capture-%Y%m%d-%H%M%S.pcap"), "-Z", "alex"]


def test_tcpdump_without_interface_uses_its_default(tmp_path):
    command = agent.tcpdump_command(make_config(tmp_path, interface=""))
    assert "-i" not in command


def test_tcpdump_needs_a_user_to_drop_root_to(tmp_path):
    with pytest.raises(ValueError, match="capture_user"):
        agent.tcpdump_command(make_config(tmp_path, capture_user=""))


def test_percent_in_the_spool_folder_is_not_a_time_pattern(tmp_path):
    # tcpdump runs the whole -w name through strftime: "%d" in a folder name
    # would become the day of the month unless it is written "%%d".
    command = agent.tcpdump_command(make_config(tmp_path / "100%done"))
    assert command[command.index("-w") + 1] == str(
        tmp_path / "100%%done" / "capture-%Y%m%d-%H%M%S.pcap")


def test_tcpdump_names_files_in_utc():
    assert agent.capture_env()["TZ"] == "UTC"


def test_windows_commands(tmp_path):
    now = 1791295200.0  # 2026-10-06 14:00:00 UTC
    etl = tmp_path / "capture-20261006-140000.etl"
    assert agent.capture_command("Windows", make_config(tmp_path), now) == [
        "pktmon", "start", "--capture", "--comp", "nics", "--pkt-size", "0",
        "--file-name", str(etl)]
    assert agent.pktmon_stop_command() == ["pktmon", "stop"]
    assert agent.pktmon_convert_command(etl) == [
        "pktmon", "etl2pcap", str(etl), "--out", str(tmp_path / "capture-20261006-140000.pcapng")]


def test_unknown_system_is_refused(tmp_path):
    with pytest.raises(ValueError, match="no built-in capture tool"):
        agent.capture_command("Plan9", make_config(tmp_path), now=0)


# ---------- config file ----------

CONFIG_TEXT = f"""
console_url = "http://192.0.2.20:8001/"
token = "{TOKEN}"
spool_dir = "SPOOL"
sensor_id = "laptop"
capture_user = "alex"
"""


@pytest.mark.skipif(os.name == "nt", reason="mode bits are POSIX only")
def test_load_config(tmp_path):
    path = tmp_path / "agent.toml"
    path.write_text(CONFIG_TEXT.replace("SPOOL", str(tmp_path / "spool")))
    path.chmod(0o600)
    config = agent.load_config(path)
    assert config.console_url == "http://192.0.2.20:8001"  # trailing / removed
    assert (config.sensor_id, config.rotate_seconds, config.interface) == ("laptop", 900, "")


@pytest.mark.skipif(os.name == "nt", reason="mode bits are POSIX only")
def test_config_readable_by_others_is_refused(tmp_path):
    path = tmp_path / "agent.toml"
    path.write_text(CONFIG_TEXT.replace("SPOOL", str(tmp_path)))
    path.chmod(0o644)
    with pytest.raises(ValueError, match="chmod 600"):
        agent.load_config(path)


@pytest.mark.parametrize("change, message", [
    ({"sensor_id": "my laptop"}, "sensor_id"),
    ({"console_url": "192.0.2.20:8001"}, "http"),
    ({"token": ""}, "token"),
    ({"rotate_seconds": 5}, "rotate_seconds"),
])
def test_bad_settings_are_refused(tmp_path, change, message):
    with pytest.raises(ValueError, match=message):
        agent.check_config(make_config(tmp_path, **change))


# ---------- which files are finished ----------

def test_newest_file_is_not_finished_while_capturing(tmp_path):
    make_captures(tmp_path, "capture-20261006-141500.pcap", "capture-20261006-140000.pcap",
                  "capture-20261006-143000.pcap")
    (tmp_path / "capture-20261006-144500.etl").write_bytes(b"")  # pktmon still writing
    running = agent.finished_files(tmp_path, capture_running=True)
    assert [p.name for p in running] == ["capture-20261006-140000.pcap",
                                         "capture-20261006-141500.pcap"]
    stopped = agent.finished_files(tmp_path, capture_running=False)
    assert len(stopped) == 3


# ---------- uploads to a fake console on 127.0.0.1 ----------

class FakeConsole(BaseHTTPRequestHandler):
    status = 200
    requests: list[dict] = []

    def do_POST(self):
        body = self.rfile.read(int(self.headers["Content-Length"]))
        FakeConsole.requests.append({"path": self.path, "auth": self.headers["Authorization"],
                                     "type": self.headers["Content-Type"], "body": body})
        self.send_response(FakeConsole.status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"analysis_id": "a1", "findings": 0}')

    def log_message(self, *args):  # keep test output quiet
        pass


@pytest.fixture
def console():
    """A fake console on 127.0.0.1 (a free port). Yields its URL."""
    FakeConsole.status, FakeConsole.requests = 200, []
    server = ThreadingHTTPServer(("127.0.0.1", 0), FakeConsole)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_port}"
    server.shutdown()
    server.server_close()


def test_upload_sends_file_sensor_id_and_token(tmp_path, console):
    spool = tmp_path / "spool"
    make_captures(spool, "capture-20261006-140000.pcap", "capture-20261006-141500.pcap")
    config = make_config(spool, console_url=console)
    assert agent.upload_finished(config, capture_running=True) == 1
    sent = FakeConsole.requests[0]
    assert sent["path"] == "/api/ingest"
    assert sent["auth"] == f"Bearer {TOKEN}"
    assert sent["type"].startswith("multipart/form-data")
    assert b'name="sensor_id"\r\n\r\nlaptop' in sent["body"]
    assert b'name="file"; filename="capture-20261006-140000.pcap"' in sent["body"]
    # Uploaded after the 2xx; the file tcpdump is still writing was not touched.
    assert (spool / "uploaded" / "capture-20261006-140000.pcap").exists()
    assert (spool / "capture-20261006-141500.pcap").exists()
    assert len(FakeConsole.requests) == 1


def test_failed_upload_keeps_the_file(tmp_path, console):
    spool = tmp_path / "spool"
    make_captures(spool, "capture-20261006-140000.pcap", "capture-20261006-141500.pcap")
    FakeConsole.status = 401  # wrong token
    config = make_config(spool, console_url=console)
    assert agent.upload_finished(config, capture_running=False) == 0
    assert len(FakeConsole.requests) == 1  # stopped at the oldest file, keeps the order
    assert sorted(p.name for p in spool.glob("*.pcap")) == [
        "capture-20261006-140000.pcap", "capture-20261006-141500.pcap"]


@pytest.mark.parametrize("status", [400, 413, 422])
def test_refused_file_moves_to_rejected(tmp_path, console, status):
    """400 not a capture, 413 too large, 422 Zeek failed on it: the same next time."""
    spool = tmp_path / "spool"
    make_captures(spool, "capture-20261006-140000.pcap")
    FakeConsole.status = status
    agent.upload_finished(make_config(spool, console_url=console), capture_running=False)
    assert (spool / "rejected" / "capture-20261006-140000.pcap").exists()


def test_console_down_keeps_the_file(tmp_path, console):
    spool = tmp_path / "spool"
    make_captures(spool, "capture-20261006-140000.pcap")
    closed_port = make_config(spool, console_url="http://127.0.0.1:9")  # nothing listens
    assert agent.upload_finished(closed_port, capture_running=False) == 0
    assert (spool / "capture-20261006-140000.pcap").exists()


def test_upload_ignores_proxy_settings_and_netrc(tmp_path, console, monkeypatch):
    # A proxy variable must not reroute the captures, and a ~/.netrc entry for
    # the console must not replace the Bearer token with a password.
    home = tmp_path / "home"
    home.mkdir()
    (home / ".netrc").write_text("machine 127.0.0.1 login someone password not-the-token\n")
    (home / ".netrc").chmod(0o600)
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("NETRC", str(home / ".netrc"))
    for name in ("HTTP_PROXY", "http_proxy", "ALL_PROXY", "all_proxy"):
        monkeypatch.setenv(name, "http://127.0.0.1:9")  # nothing listens there
    for name in ("NO_PROXY", "no_proxy"):
        monkeypatch.delenv(name, raising=False)
    spool = tmp_path / "spool"
    make_captures(spool, "capture-20261006-140000.pcap")
    assert agent.upload_finished(make_config(spool, console_url=console),
                                 capture_running=False) == 1
    assert FakeConsole.requests[0]["auth"] == f"Bearer {TOKEN}"


def test_spool_folder_the_agent_creates_goes_to_capture_user(tmp_path, monkeypatch):
    # sudo: the agent is root, but tcpdump -Z writes as capture_user.
    given = []
    monkeypatch.setattr(agent.os, "geteuid", lambda: 0, raising=False)
    monkeypatch.setattr(agent.shutil, "chown", lambda path, user: given.append((path, user)))
    config = make_config(tmp_path / "spool")
    agent.prepare_spool(config, "Linux")
    assert config.spool_dir.is_dir() and given == [(config.spool_dir, "alex")]
    agent.prepare_spool(config, "Linux")  # it exists now: left alone
    assert len(given) == 1


def test_only_the_newest_uploaded_files_are_kept(tmp_path):
    folder = tmp_path / "uploaded"
    make_captures(folder, *[f"capture-20261006-14{m:02d}00.pcap" for m in range(0, 60, 10)])
    agent.prune_uploaded(folder, keep=2)
    assert sorted(p.name for p in folder.iterdir()) == [
        "capture-20261006-144000.pcap", "capture-20261006-145000.pcap"]


# ---------- the real ingest app ----------

# The agent passes timeout= like any requests call; TestClient warns that it ignores it.
@pytest.mark.filterwarnings("ignore:You should not use the 'timeout' argument")
def test_upload_to_the_real_ingest_app(tmp_path, monkeypatch):
    """The agent's request, answered by create_ingest_app (no network: TestClient).

    The console recognises a file by its content, not its name, so a goflow2 flow
    file stands in for a capture here (a real capture would need Zeek)."""
    from fastapi.testclient import TestClient

    from maxguard.api.app import create_ingest_app

    monkeypatch.setenv("MAXGUARD_INGEST_TOKEN", TOKEN)
    client = TestClient(create_ingest_app(tmp_path / "data", explain=False))
    spool = tmp_path / "spool"
    spool.mkdir()
    shutil.copy(FLOW_FIXTURE, spool / "capture-20261006-140000.pcap")
    config = make_config(spool, console_url="http://testserver")
    assert agent.upload_finished(config, capture_running=False, session=client) == 1
    assert agent.upload(spool / "uploaded" / "capture-20261006-140000.pcap",
                        make_config(spool, console_url="http://testserver", token="wrong"),
                        session=client) == 401
