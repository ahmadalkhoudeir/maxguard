"""Tests for the dashboard pages (Ahmad, AHM-02).

Reports come from maxguard.pipeline.analyze on the Zeek log fixtures (no Zeek,
no AI) and are saved through the stores, exactly as the upload endpoint does.
"""

from __future__ import annotations

import copy
import hashlib
import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from maxguard.api.app import STATIC_DIR, create_app
from maxguard.pipeline import analyze

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures" / "zeek"
HTMX_SHA256 = "d6fdc75f204e6bdefa99b69bf1e6d4ac69b8a364f77929f45c13476b4000f717"
RECEIVED_AT = 1791300000.0  # a fixed "upload time" (Oct 2026), so tests never read the clock
HOSTILE = "<script>alert('xss')</script>"


@pytest.fixture(scope="module")
def telnet_report(tmp_path_factory) -> dict:
    return analyze(FIXTURES / "telnet", tmp_path_factory.mktemp("telnet"), explain=False)


@pytest.fixture(scope="module")
def ftp_report(tmp_path_factory) -> dict:
    return analyze(FIXTURES / "ftp", tmp_path_factory.mktemp("ftp"), explain=False)


@pytest.fixture
def app(tmp_path):
    return create_app(tmp_path / "data", explain=False)


@pytest.fixture
def client(app) -> TestClient:
    return TestClient(app)


def save(app, report: dict, received_at: float = RECEIVED_AT) -> str:
    """Store a report the way POST /api/analyses does."""
    analysis_id = app.state.state_store.save_analysis(report, received_at=received_at)
    app.state.event_store.write(report.get("events", []))
    return analysis_id


def with_ai_sentences(report: dict) -> dict:
    """A copy of the report with one AI sentence per finding, citing its evidence."""
    report = copy.deepcopy(report)
    for finding in report["findings"]:
        ids = [e["record_id"] for e in finding["evidence"]]
        finding["explanation_sentences"] = [
            {"text": "A device logged in with Telnet, so the session was readable.",
             "evidence_ids": ids}]
        finding["explanation"] = finding["explanation_sentences"][0]["text"]
    report["ai"] = {"status": "ok", "model": "qwen3:4b", "explained": len(report["findings"]),
                    "dropped_sentences": 0, "reason": None}
    return report


def telnet_id(report: dict) -> str:
    return report["findings"][0]["finding_id"]


# ---------- AHM-02: layout, queue, upload ----------

def test_htmx_file_is_the_reviewed_one():
    data = (STATIC_DIR / "htmx-2.0.11.min.js").read_bytes()
    assert hashlib.sha256(data).hexdigest() == HTMX_SHA256


@pytest.mark.parametrize("path", ["/", "/upload"])
def test_pages_return_200_with_the_layout(client, path):
    page = client.get(path)
    assert page.status_code == 200
    assert "Your data never leaves this computer." in page.text
    assert '<script src="/static/htmx-2.0.11.min.js"' in page.text
    assert 'href="/static/app.css"' in page.text
    csp = page.headers["content-security-policy"]
    assert "default-src 'self'" in csp and "script-src 'self';" in csp
    assert "unsafe" not in csp  # no inline scripts, no eval: a second wall behind escaping
    # not "no-referrer": Chrome then sends "Origin: null" on form posts, which the API refuses
    assert page.headers["referrer-policy"] == "same-origin"


def test_static_files_are_served(client):
    assert client.get("/static/app.js").status_code == 200
    assert client.get("/static/app.css").status_code == 200


def test_queue_lists_the_telnet_alert(app, client, telnet_report):
    save(app, telnet_report)
    page = client.get("/")
    assert "Telnet session in cleartext" in page.text
    assert f'href="/alerts/{telnet_id(telnet_report)}"' in page.text
    assert "172.18.0.3 → 172.18.0.2:23" in page.text
    # severity as text and color: the word is in the badge with the color class
    assert '<span class="sev sev-high">High</span>' in page.text


def test_queue_has_the_htmx_wiring(client):
    page = client.get("/")
    assert 'hx-trigger="refresh, every 30s"' in page.text
    assert page.text.count('hx-get="/" hx-target="#alerts" hx-select="#alerts"') == 2
    assert 'new EventSource("/api/stream")' in client.get("/static/app.js").text


def test_queue_filters(app, client, telnet_report, ftp_report):
    save(app, telnet_report)
    save(app, ftp_report, received_at=RECEIVED_AT + 1)
    app.state.state_store.update_alert(telnet_id(telnet_report), actor="test",
                                       at=RECEIVED_AT + 2, status="resolved")
    resolved = client.get("/?status=resolved&severity=").text
    assert "Telnet session in cleartext" in resolved
    assert "FTP" not in resolved.split('id="alerts"')[1]
    new = client.get("/", params={"status": "new"}).text
    assert "Telnet session in cleartext" not in new
    low = client.get("/", params={"severity": "low"}).text
    assert "No alerts match these filters" in low


def test_unknown_filter_value_is_a_400_page(client):
    page = client.get("/?status=bogus")
    assert page.status_code == 400
    assert "status must be one of" in page.text


def test_hostile_values_are_escaped(app, client, telnet_report):
    report = with_ai_sentences(telnet_report)
    finding = report["findings"][0]
    finding["title"] = HOSTILE
    finding["details"] = {"user": HOSTILE}
    finding["explanation_sentences"][0]["text"] = HOSTILE
    save(app, report)
    app.state.state_store.update_alert(finding["finding_id"], actor="test",
                                       at=RECEIVED_AT, assignee=HOSTILE)
    for path in ("/",):  # the alert page comes in AHM-03
        page = client.get(path).text
        assert HOSTILE not in page
        assert "&lt;script&gt;" in page


@pytest.mark.parametrize("mode", ["analyst", "home"])
def test_no_page_loads_anything_from_outside(app, client, telnet_report, mode):
    save(app, with_ai_sentences(telnet_report))
    client.cookies.set("mg_mode", mode)
    pages = ["/", "/upload"]
    for path in pages:
        for url in re.findall(r'(?:src|href|action|hx-[a-z]+)="([^"]*)"', client.get(path).text):
            assert not url.startswith(("http:", "https:", "//")), (path, url)


def test_mode_switch_sets_the_cookie(client):
    answer = client.post("/mode", data={"mode": "home", "next": "/assets"},
                         follow_redirects=False)
    assert answer.status_code == 303
    assert answer.headers["location"] == "/assets"
    cookie = answer.headers["set-cookie"].lower()
    assert "mg_mode=home" in cookie and "httponly" in cookie and "samesite=lax" in cookie


# Browsers read /\evil.example like //evil.example: another website.
@pytest.mark.parametrize("next_path", ["//evil.example/", "/\\evil.example/",
                                       "https://evil.example/", "javascript:alert(1)"])
def test_mode_switch_never_redirects_off_site(client, next_path):
    answer = client.post("/mode", data={"mode": "home", "next": next_path},
                         follow_redirects=False)
    assert answer.headers["location"] == "/"


def test_cross_site_mode_switch_is_refused(client):
    answer = client.post("/mode", data={"mode": "home"},
                         headers={"Sec-Fetch-Site": "cross-site"})
    assert answer.status_code == 403


def test_upload_page_posts_to_the_api(client):
    page = client.get("/upload").text
    assert 'hx-post="/api/analyses"' in page
    assert 'hx-encoding="multipart/form-data"' in page
    assert 'href="/"' in page
