"""Tests for the API (Jaiden, JAI-07).

Uploads use a zip of the Zeek log fixture tests/fixtures/zeek/telnet: it goes
through ZeekLogAdapter, so these tests need no Zeek. The integration test
tests/integration/test_api_upload.py uploads a real capture.
"""

from __future__ import annotations

import io
import re
import threading
import zipfile
from pathlib import Path

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from maxguard.api import app as api_app
from maxguard.api.app import (
    create_app,
    create_ingest_app,
    display_name,
    notify_change,
    optional_module,
    save_upload,
    suffix_for,
)

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures" / "zeek"
TOKEN = "t" * 43  # a test value with the length of secrets.token_urlsafe(32)


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    """Every test starts with the settings off, whatever the shell has set."""
    for name in ("MAXGUARD_INGEST_TOKEN", "MAXGUARD_MAX_UPLOAD_MB", "MAXGUARD_KEEP_UPLOADS",
                 "MAXGUARD_OFFLINE", "MAXGUARD_DATA_DIR"):
        monkeypatch.delenv(name, raising=False)


@pytest.fixture
def data_dir(tmp_path) -> Path:
    return tmp_path / "data"


@pytest.fixture
def client(data_dir) -> TestClient:
    return TestClient(create_app(data_dir, explain=False))


def zipped_fixture(name: str = "telnet") -> bytes:
    """The fixture folder as a .zip in memory, with the logs at the top level."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        for log in sorted((FIXTURES / name).iterdir()):
            archive.write(log, arcname=log.name)
    return buffer.getvalue()


def upload(client: TestClient, data: bytes, filename: str = "telnet.zip", **kwargs):
    return client.post("/api/analyses", files={"file": (filename, data)}, **kwargs)


def uploaded_files(data_dir: Path) -> list[Path]:
    return sorted((data_dir / "uploads").iterdir())


# ---------- uploads ----------

def test_upload_creates_the_telnet_alert(client):
    response = upload(client, zipped_fixture())
    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"analysis_id", "findings"}
    assert body["findings"] == 1

    [alert] = client.get("/api/alerts").json()
    assert alert["rule_id"] == "cleartext.telnet"
    assert alert["status"] == "new"
    assert alert["count"] == 1
    assert alert["analysis_id"] == body["analysis_id"]

    [analysis] = client.get("/api/analyses").json()
    assert analysis["input_name"] == "telnet.zip"  # the name the person knows
    report = client.get(f"/api/analyses/{body['analysis_id']}").json()
    assert report["schema"] == "maxguard.report/2"
    assert "events" not in report  # events live in the event store


def test_the_same_file_twice_is_not_counted_twice(client):
    data = zipped_fixture()
    upload(client, data)
    upload(client, data)
    [alert] = client.get("/api/alerts").json()
    assert alert["count"] == 1
    assert len(client.get("/api/analyses").json()) == 2  # both uploads are on record


def test_upload_is_stored_under_a_generated_name_and_deleted(client, data_dir):
    response = upload(client, zipped_fixture(), filename="../../evil.zip")
    assert response.status_code == 200
    assert uploaded_files(data_dir) == []  # deleted after the analysis
    assert not (data_dir.parent / "evil.zip").exists()
    assert client.get("/api/analyses").json()[0]["input_name"] == "evil.zip"


def test_keep_uploads_keeps_the_file_under_our_name(monkeypatch, data_dir):
    monkeypatch.setenv("MAXGUARD_KEEP_UPLOADS", "1")
    client = TestClient(create_app(data_dir, explain=False))
    upload(client, zipped_fixture(), filename="../../evil.zip")
    [kept] = uploaded_files(data_dir)
    assert re.fullmatch(r"[0-9a-f]{32}\.zip", kept.name)


def test_unsupported_file_is_refused(client, data_dir):
    response = upload(client, b"just some text", filename="notes.txt")
    assert response.status_code == 400
    assert "not a .pcap/.pcapng capture" in response.json()["detail"]
    assert uploaded_files(data_dir) == []


def test_broken_archive_is_refused(client, data_dir):
    response = upload(client, b"PK\x03\x04 this is not really a zip", filename="logs.zip")
    assert response.status_code == 400
    assert uploaded_files(data_dir) == []


def test_upload_without_a_file_field_is_refused(client):
    response = client.post("/api/analyses", files={"wrong_name": ("a.zip", b"PK")})
    assert response.status_code == 400


def test_too_large_upload_is_refused(monkeypatch, data_dir):
    monkeypatch.setenv("MAXGUARD_MAX_UPLOAD_MB", "1")
    client = TestClient(create_app(data_dir, explain=False))
    response = upload(client, b"\0" * (2 * 1024 * 1024), filename="big.pcap")
    assert response.status_code == 413
    assert "MAXGUARD_MAX_UPLOAD_MB" in response.json()["detail"]
    assert not (data_dir / "uploads").exists() or uploaded_files(data_dir) == []


def test_save_upload_stops_at_the_limit_and_removes_the_partial_file(data_dir):
    # A client can leave out Content-Length; then only the copy loop sees the size.
    app = create_app(data_dir, explain=False)
    app.state.max_upload_bytes = 10
    folder = data_dir / "uploads"
    folder.mkdir()
    with pytest.raises(HTTPException) as caught:
        save_upload(io.BytesIO(b"x" * 11), folder, app)
    assert caught.value.status_code == 413
    assert list(folder.iterdir()) == []


def test_bad_upload_size_setting_fails_at_start(monkeypatch, data_dir):
    monkeypatch.setenv("MAXGUARD_MAX_UPLOAD_MB", "lots")
    with pytest.raises(ValueError, match="MAXGUARD_MAX_UPLOAD_MB"):
        create_app(data_dir, explain=False)


# ---------- alerts, audit, events, assets ----------

def test_patch_changes_status_and_writes_the_audit_trail(client):
    upload(client, zipped_fixture())
    [alert] = client.get("/api/alerts").json()
    url = f"/api/alerts/{alert['finding_id']}"

    response = client.patch(url, json={"actor": "ahmad", "status": "investigating",
                                       "assignee": "fiona"})
    assert response.status_code == 200
    assert response.json()["status"] == "investigating"
    assert client.get(url).json()["assignee"] == "fiona"

    [entry] = client.get("/api/audit").json()
    assert entry["actor"] == "ahmad"
    assert entry["action"] == "alert.update"
    assert entry["target"] == alert["finding_id"]
    assert entry["details"]["status"] == {"from": "new", "to": "investigating"}


def test_patch_errors(client):
    upload(client, zipped_fixture())
    [alert] = client.get("/api/alerts").json()
    url = f"/api/alerts/{alert['finding_id']}"
    assert client.patch("/api/alerts/0000000000000000",
                        json={"actor": "ahmad", "status": "resolved"}).status_code == 404
    assert client.patch(url, json={"actor": "ahmad", "status": "fixed"}).status_code == 400
    assert client.patch(url, json={"status": "resolved"}).status_code == 422  # no actor


def test_alert_filters(client):
    upload(client, zipped_fixture())
    assert len(client.get("/api/alerts", params={"severity": "high"}).json()) == 1
    assert client.get("/api/alerts", params={"severity": "low"}).json() == []
    assert client.get("/api/alerts", params={"status": "new"}).json()[0]["status"] == "new"
    assert client.get("/api/alerts", params={"status": "bogus"}).status_code == 400
    assert client.get("/api/alerts", params={"limit": 0}).status_code == 422


def test_unknown_ids_are_404(client):
    assert client.get("/api/alerts/0000000000000000").status_code == 404
    assert client.get("/api/analyses/0000000000000000").status_code == 404


def test_events_and_assets(client):
    assert client.get("/api/events").json() == []
    assert client.get("/api/assets").json() == []
    upload(client, zipped_fixture())

    events = client.get("/api/events").json()
    assert len(events) == 1
    assert events[0]["dst_port"] == 23
    assert events[0]["sensor_id"] == "import"  # uploaded Zeek logs
    assert client.get("/api/events", params={"ip": "172.18.0.3"}).json() == events
    assert client.get("/api/events", params={"ip": "192.0.2.99"}).json() == []
    assert client.get("/api/events", params={"ip": "not-an-ip"}).status_code == 400

    ips = [asset["ip"] for asset in client.get("/api/assets").json()]
    assert ips == ["172.18.0.2", "172.18.0.3"]


# ---------- ingest ----------

def test_ingest_is_off_without_a_token(client):
    response = client.post("/api/ingest", files={"file": ("x.zip", zipped_fixture())})
    assert response.status_code == 404


def test_ingest_needs_the_right_token(monkeypatch, data_dir):
    monkeypatch.setenv("MAXGUARD_INGEST_TOKEN", TOKEN)
    client = TestClient(create_app(data_dir, explain=False))
    files = {"file": ("2026-10-06-1400.tar.gz", zipped_fixture())}

    missing = client.post("/api/ingest", files=files)
    assert missing.status_code == 401
    assert missing.headers["www-authenticate"] == "Bearer"
    wrong = client.post("/api/ingest", files=files, headers={"Authorization": "Bearer nope"})
    assert wrong.status_code == 401
    assert client.get("/api/alerts").json() == []  # nothing was stored

    right = client.post("/api/ingest", files=files, data={"sensor_id": "lab-sensor"},
                        headers={"Authorization": f"Bearer {TOKEN}"})
    assert right.status_code == 200
    assert right.json()["findings"] == 1
    assert {e["sensor_id"] for e in client.get("/api/events").json()} == {"lab-sensor"}


def test_ingest_refuses_a_bad_sensor_name(monkeypatch, data_dir):
    monkeypatch.setenv("MAXGUARD_INGEST_TOKEN", TOKEN)
    client = TestClient(create_app(data_dir, explain=False))
    response = client.post("/api/ingest", files={"file": ("x.zip", zipped_fixture())},
                           data={"sensor_id": "../etc"},
                           headers={"Authorization": f"Bearer {TOKEN}"})
    assert response.status_code == 400


def test_short_ingest_token_is_refused_at_start(monkeypatch, data_dir):
    monkeypatch.setenv("MAXGUARD_INGEST_TOKEN", "secret")
    with pytest.raises(ValueError, match="at least 32 characters"):
        create_app(data_dir, explain=False)


def test_the_ingest_app_serves_only_ingest(monkeypatch, data_dir):
    # The port published on the LAN (docker/compose.lan.yaml): nothing to read there.
    monkeypatch.setenv("MAXGUARD_INGEST_TOKEN", TOKEN)
    lan = TestClient(create_ingest_app(data_dir, explain=False))
    for path in ("/api/alerts", "/api/events", "/api/audit", "/", "/docs", "/openapi.json"):
        assert lan.get(path).status_code == 404, path
    assert list(lan.app.openapi()["paths"]) == ["/api/ingest"]  # its only route

    sent = lan.post("/api/ingest", files={"file": ("2026-10-06-1400.tar.gz", zipped_fixture())},
                    data={"sensor_id": "lab-sensor"},
                    headers={"Authorization": f"Bearer {TOKEN}"})
    assert sent.status_code == 200
    # The dashboard's app reads the same data folder.
    console = TestClient(create_app(data_dir, explain=False))
    assert [a["rule_id"] for a in console.get("/api/alerts").json()] == ["cleartext.telnet"]


def test_the_ingest_app_needs_a_token(data_dir):
    with pytest.raises(ValueError, match="MAXGUARD_INGEST_TOKEN"):
        create_ingest_app(data_dir, explain=False)


# ---------- cross-site requests ----------

def test_another_website_cannot_upload(client):
    data = zipped_fixture()
    other = upload(client, data, headers={"Origin": "http://evil.example"})
    assert other.status_code == 403
    fetch_metadata = upload(client, data, headers={"Sec-Fetch-Site": "cross-site"})
    assert fetch_metadata.status_code == 403
    other_port = upload(client, data, headers={"Sec-Fetch-Site": "same-site"})
    assert other_port.status_code == 403
    sandboxed = upload(client, data, headers={"Origin": "null"})
    assert sandboxed.status_code == 403
    same_site = upload(client, data, headers={"Origin": "http://testserver"})
    assert same_site.status_code == 200


# ---------- DNS rebinding: only this machine's names ----------

def test_a_request_for_an_unknown_host_name_is_refused(data_dir):
    # What a DNS-rebinding page sends: its own name, now pointing at 127.0.0.1.
    client = TestClient(create_app(data_dir, explain=False),
                        base_url="http://rebind.example:8000")
    response = client.get("/api/alerts")
    assert response.status_code == 400
    assert response.text == "Invalid host header"


@pytest.mark.parametrize("host", ["127.0.0.1:8000", "localhost:8000", "[::1]:8000", "localhost"])
def test_this_machine_is_allowed_by_default(data_dir, monkeypatch, host):
    monkeypatch.delenv("MAXGUARD_ALLOWED_HOSTS")
    client = TestClient(create_app(data_dir, explain=False), base_url=f"http://{host}")
    assert client.get("/api/alerts").status_code == 200


def test_the_consoles_lan_address_can_be_added(data_dir, monkeypatch):
    monkeypatch.setenv("MAXGUARD_ALLOWED_HOSTS", "localhost, 192.168.50.20")
    app = create_app(data_dir, explain=False)
    assert TestClient(app, base_url="http://192.168.50.20:8000").get(
        "/api/alerts").status_code == 200
    assert TestClient(app, base_url="http://192.168.50.21:8000").get(
        "/api/alerts").status_code == 400


@pytest.mark.parametrize("value", ["http://192.168.50.20", "192.168.50.20:8000", "*", " , "])
def test_a_wrong_allowed_hosts_setting_stops_the_app(data_dir, monkeypatch, value):
    monkeypatch.setenv("MAXGUARD_ALLOWED_HOSTS", value)
    with pytest.raises(ValueError, match="MAXGUARD_ALLOWED_HOSTS"):
        create_app(data_dir, explain=False)


# ---------- live updates ----------

def test_stream_sends_alerts_changed(client):
    app = client.app
    app.state.keepalive_seconds = 0.5  # instead of 15 s, so the test sees one
    timer = threading.Timer(1.2, notify_change, args=[app])
    timer.start()
    with client.stream("GET", "/api/stream", params={"max_events": 2}) as response:
        assert response.headers["content-type"].startswith("text/event-stream")
        text = "".join(response.iter_text())
    timer.join()
    assert text.startswith("event: alerts-changed\ndata: 0\n\n")  # sent at once
    assert ": keep-alive\n\n" in text
    assert text.endswith("event: alerts-changed\ndata: 1\n\n")    # after the change


# ---------- small helpers and the app itself ----------

def test_display_name_keeps_only_a_safe_last_part():
    assert display_name("C:\\captures\\..\\shop.pcap") == "shop.pcap"
    assert display_name("../../etc/passwd") == "passwd"
    assert display_name("<script>.pcap") == "_script_.pcap"
    assert display_name(None) == "upload"
    assert display_name("..") == "upload"


def test_suffix_comes_from_the_first_bytes():
    assert suffix_for(b"\xd4\xc3\xb2\xa1rest") == ".pcap"
    assert suffix_for(b"\x0a\x0d\x0d\x0arest") == ".pcap"  # pcapng
    assert suffix_for(b"PK\x03\x04rest") == ".zip"
    assert suffix_for(b"\x1f\x8brest") == ".tar.gz"
    assert suffix_for(b"hello") == ""


def test_optional_modules_that_do_not_exist_are_skipped():
    assert optional_module("maxguard.no_such_module") is None
    assert optional_module("maxguard.no_such_package.routes") is None


def test_static_files_are_served(monkeypatch, data_dir, tmp_path):
    # The dashboard's files (AHM-02) live in maxguard/web/static; a stand-in folder
    # shows the mount works before they exist.
    static = tmp_path / "static"
    static.mkdir()
    (static / "hello.txt").write_text("hello")
    monkeypatch.setattr(api_app, "STATIC_DIR", static)
    client = TestClient(create_app(data_dir, explain=False))
    assert client.get("/static/hello.txt").text == "hello"
    assert client.get("/static/missing.txt").status_code == 404


def test_openapi_page_shows_the_upload_field(client):
    schema = client.get("/openapi.json").json()
    body = schema["paths"]["/api/analyses"]["post"]["requestBody"]
    assert "file" in body["content"]["multipart/form-data"]["schema"]["properties"]
    assert "sensor_id" in str(schema["paths"]["/api/ingest"]["post"]["requestBody"])


def test_data_dir_defaults_to_the_environment(monkeypatch, tmp_path):
    monkeypatch.setenv("MAXGUARD_DATA_DIR", str(tmp_path / "from-env"))
    app = create_app(explain=False)
    assert app.state.data_dir == tmp_path / "from-env"
    assert (tmp_path / "from-env" / "state.db").exists()
