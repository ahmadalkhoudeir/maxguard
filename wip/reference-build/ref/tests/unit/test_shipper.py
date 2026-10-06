"""Shipper tests (Jakub, JAK-07): the right file with the right header, retries after a
failure, never twice, and 7-day retention.

The console is faked with Python's http.server in a thread on 127.0.0.1, so the
shipper's real HTTP code runs, and nothing leaves this computer. Every function
gets `now` from the test, so which folders are ready is exact.
"""

import io
import re
import socket
import tarfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

from maxguard.adapters.live import folder_start
from maxguard.sensor.shipper import (
    SHIPPED_MARKER,
    ConfigError,
    is_shipped,
    load_config,
    main,
    pack_folder,
    prune,
    run_once,
)

TOKEN = "fake-token-for-tests-0123456789abcdef"   # not a secret: only the fake console knows it
FOLDERS = ("2026-10-06-1400", "2026-10-06-1415", "2026-10-06-1430")
# 14:46 UTC: 14:00 and 14:15 are complete; 14:30 ended at 14:45 and is still settling.
NOW = folder_start("2026-10-06-1430") + 15 * 60 + 60
DAY = 86400


class FakeConsole:
    """Stands in for the console's POST /api/ingest. Answers with the codes in
    `statuses` first (one per request), then 200, and records every request."""

    def __init__(self) -> None:
        self.statuses: list[int] = []
        self.requests: list[dict] = []
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), self.handler_class())
        # poll_interval: how often serve_forever() checks for shutdown (fast teardown).
        self.thread = threading.Thread(target=self.server.serve_forever,
                                       kwargs={"poll_interval": 0.05}, daemon=True)

    @property
    def url(self) -> str:
        return f"http://127.0.0.1:{self.server.server_port}"

    def handler_class(self):
        console = self

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                body = self.rfile.read(int(self.headers["Content-Length"]))
                console.requests.append({"path": self.path, "headers": self.headers,
                                         "body": body})
                status = console.statuses.pop(0) if console.statuses else 200
                reply = b'{"analysis_id": "test", "findings": 1}'
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(reply)))
                self.end_headers()
                self.wfile.write(reply)

            def log_message(self, *args):  # keep the test output quiet
                pass

        return Handler


@pytest.fixture
def console():
    fake = FakeConsole()
    fake.thread.start()
    yield fake
    fake.server.shutdown()
    fake.server.server_close()


def unused_port() -> int:
    """A port on 127.0.0.1 where nothing listens: connecting is refused at once."""
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def write_config(data_dir: Path, url: str, sensor_id: str = "lab-sensor") -> None:
    (data_dir / "shipper.toml").write_text(
        "# test settings\n"
        f'console_url = "{url}"\n'
        f'token = "{TOKEN}"\n'
        f'sensor_id = "{sensor_id}"\n')


def make_sensor(data_dir: Path, folders=FOLDERS) -> Path:
    """Interval folders with one conn.log line each, and one Suricata minute file
    for the 14:15 interval (written in minute 14:20)."""
    for name in folders:
        folder = data_dir / "zeek" / name
        folder.mkdir(parents=True)
        (folder / "conn.log").write_text(f'{{"folder": "{name}"}}\n')
    spool = data_dir / "spool" / "suricata"
    spool.mkdir(parents=True)
    (spool / "eve-2026-10-06-1420.json").write_text('{"event_type": "tls"}\n')
    return data_dir


def parse_form(request: dict) -> dict[str, tuple[str | None, bytes]]:
    """multipart/form-data body -> {field name: (file name or None, value bytes)}."""
    boundary = request["headers"]["Content-Type"].split("boundary=")[1].encode()
    fields = {}
    for part in request["body"].split(b"--" + boundary)[1:-1]:
        head, _, value = part.removeprefix(b"\r\n").partition(b"\r\n\r\n")
        disposition = head.decode().splitlines()[0]
        name = re.search(r'; name="([^"]*)"', disposition).group(1)
        file_name = re.search(r'; filename="([^"]*)"', disposition)
        fields[name] = (file_name.group(1) if file_name else None, value.removesuffix(b"\r\n"))
    return fields


def tar_members(data: bytes) -> dict[str, bytes]:
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tar:
        return {m.name: tar.extractfile(m).read() for m in tar.getmembers()}


# ---- shipping -------------------------------------------------------------------------

def test_ships_the_right_file_with_the_right_header(tmp_path, console):
    data = make_sensor(tmp_path, folders=("2026-10-06-1415", "2026-10-06-1430"))
    write_config(data, console.url)

    result = run_once(data, 15, NOW)

    assert result["shipped"] == ["2026-10-06-1415"]
    [request] = console.requests
    assert request["path"] == "/api/ingest"
    assert request["headers"]["Authorization"] == f"Bearer {TOKEN}"
    form = parse_form(request)
    assert form["sensor_id"] == (None, b"lab-sensor")
    file_name, archive = form["file"]
    assert file_name == "2026-10-06-1415.tar.gz"
    assert tar_members(archive) == {
        "2026-10-06-1415/conn.log": b'{"folder": "2026-10-06-1415"}\n',
        "2026-10-06-1415/eve.json": b'{"event_type": "tls"}\n',   # merged before shipping
    }
    assert is_shipped(data / "zeek" / "2026-10-06-1415")


def test_the_folder_still_being_written_is_not_shipped(tmp_path, console):
    data = make_sensor(tmp_path)
    write_config(data, console.url)
    run_once(data, 15, NOW)
    assert not is_shipped(data / "zeek" / "2026-10-06-1430")
    # Two minutes later it has settled, and the next round ships it.
    assert run_once(data, 15, NOW + 120)["shipped"] == ["2026-10-06-1430"]


def test_never_ships_a_folder_twice(tmp_path, console):
    data = make_sensor(tmp_path)
    write_config(data, console.url)
    assert run_once(data, 15, NOW)["shipped"] == ["2026-10-06-1400", "2026-10-06-1415"]
    assert run_once(data, 15, NOW + 30)["shipped"] == []
    assert len(console.requests) == 2


def test_retries_after_the_console_answers_with_an_error(tmp_path, console):
    data = make_sensor(tmp_path, folders=("2026-10-06-1415",))
    write_config(data, console.url)
    console.statuses = [500]

    assert run_once(data, 15, NOW)["shipped"] == []
    assert not is_shipped(data / "zeek" / "2026-10-06-1415")

    assert run_once(data, 15, NOW + 60)["shipped"] == ["2026-10-06-1415"]
    assert len(console.requests) == 2
    # The same folder packs to the same bytes, so the console sees the same upload.
    assert parse_form(console.requests[0])["file"] == parse_form(console.requests[1])["file"]


def test_retries_when_the_console_cannot_be_reached(tmp_path, console):
    data = make_sensor(tmp_path, folders=("2026-10-06-1415",))
    write_config(data, f"http://127.0.0.1:{unused_port()}")
    assert run_once(data, 15, NOW)["shipped"] == []      # refused: no crash, not marked

    write_config(data, console.url)                      # the console is back
    assert run_once(data, 15, NOW + 60)["shipped"] == ["2026-10-06-1415"]


def test_stops_at_the_first_failure_and_keeps_the_order(tmp_path, console):
    data = make_sensor(tmp_path)
    write_config(data, console.url)
    console.statuses = [503]
    assert run_once(data, 15, NOW)["shipped"] == []
    assert len(console.requests) == 1                    # 14:15 was not even tried
    assert run_once(data, 15, NOW + 30)["shipped"] == ["2026-10-06-1400", "2026-10-06-1415"]


def test_a_proxy_setting_is_ignored(tmp_path, console, monkeypatch):
    for name in ("http_proxy", "HTTP_PROXY", "https_proxy", "HTTPS_PROXY", "all_proxy"):
        monkeypatch.setenv(name, f"http://127.0.0.1:{unused_port()}")
    monkeypatch.delenv("no_proxy", raising=False)
    monkeypatch.delenv("NO_PROXY", raising=False)
    data = make_sensor(tmp_path, folders=("2026-10-06-1415",))
    write_config(data, console.url)
    assert run_once(data, 15, NOW)["shipped"] == ["2026-10-06-1415"]


def test_without_a_config_file_nothing_is_shipped(tmp_path, console, caplog):
    data = make_sensor(tmp_path)
    assert run_once(data, 15, NOW)["shipped"] == []
    assert console.requests == []
    assert "shipper.toml not found" in caplog.text


def test_a_bad_config_file_is_reported_not_fatal(tmp_path, console, caplog):
    data = make_sensor(tmp_path)
    write_config(data, console.url, sensor_id="lab sensor!")
    assert run_once(data, 15, NOW)["shipped"] == []
    assert "sensor_id must be" in caplog.text


def test_main_runs_one_round(tmp_path, console):
    data = make_sensor(tmp_path, folders=("2026-10-06-1415",))
    write_config(data, console.url)
    assert main(["--data", str(data), "--interval-minutes", "15", "--once"]) == 0
    assert len(console.requests) == 1   # the real clock is long past 14:17 on Oct 6, 2026


# ---- settings ---------------------------------------------------------------------

def test_load_config_reads_the_settings(tmp_path):
    (tmp_path / "shipper.toml").write_text(
        f'console_url = "http://192.0.2.10:8001/"\ntoken = "{TOKEN}"\nsensor_id = "sensor-01"\n')
    config = load_config(tmp_path / "shipper.toml")
    assert config.console_url == "http://192.0.2.10:8001"   # trailing slash removed
    assert (config.token, config.sensor_id, config.ca_file) == (TOKEN, "sensor-01", None)


@pytest.mark.parametrize(("line", "message"), [
    ('console_url = "192.0.2.10:8001"', "console_url must start with"),
    ('token = ""', "token is empty"),
    ('sensor_id = "../etc"', "sensor_id must be"),
])
def test_load_config_refuses_wrong_settings(tmp_path, line, message):
    settings = {"console_url": '"http://192.0.2.10:8001"', "token": f'"{TOKEN}"',
                "sensor_id": '"sensor-01"'}
    key = line.split(" = ")[0]
    settings[key] = line.split(" = ")[1]
    (tmp_path / "shipper.toml").write_text(
        "".join(f"{k} = {v}\n" for k, v in settings.items()))
    with pytest.raises(ConfigError, match=message):
        load_config(tmp_path / "shipper.toml")


# ---- packing and retention ------------------------------------------------------------

def test_pack_folder_is_repeatable_and_leaves_out_hidden_files(tmp_path):
    folder = make_sensor(tmp_path) / "zeek" / "2026-10-06-1415"
    (folder / SHIPPED_MARKER).write_text("1\n")
    (folder / ".eve-abc.partial").write_text("half written\n")
    first = pack_folder(folder)
    assert pack_folder(folder) == first
    assert list(tar_members(first)) == ["2026-10-06-1415/conn.log"]


def test_prune_deletes_only_shipped_folders_older_than_7_days(tmp_path):
    data = make_sensor(tmp_path, folders=("2026-09-28-1400", "2026-09-28-1415",
                                          "2026-10-06-1400"))
    for name in ("2026-09-28-1400", "2026-10-06-1400"):
        (data / "zeek" / name / SHIPPED_MARKER).write_text("1\n")
    old_part = data / "spool" / "suricata" / "eve-2026-09-28-1401.json"
    old_part.write_text("{}\n")

    deleted = prune(data, now=NOW)

    assert deleted == ["2026-09-28-1400", "eve-2026-09-28-1401.json"]
    assert sorted(p.name for p in (data / "zeek").iterdir()) == [
        "2026-09-28-1415",   # never shipped: kept
        "2026-10-06-1400",   # shipped, but only today
    ]
    assert (data / "spool" / "suricata" / "eve-2026-10-06-1420.json").exists()


def test_prune_keeps_a_folder_until_it_is_older_than_7_days(tmp_path):
    data = make_sensor(tmp_path, folders=("2026-10-06-1400",))
    (data / "zeek" / "2026-10-06-1400" / SHIPPED_MARKER).write_text("1\n")
    start = folder_start("2026-10-06-1400")
    assert prune(data, now=start + 7 * DAY) == []
    assert prune(data, now=start + 7 * DAY + 1) == ["2026-10-06-1400"]
