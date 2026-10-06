"""Integration test for the API (Jaiden, JAI-07): a real capture through Zeek.

Runs inside the engine test image (pytest -m integration), where Zeek is installed.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from maxguard.api.app import create_app

PCAPS = Path(__file__).resolve().parent.parent / "pcaps"

pytestmark = pytest.mark.integration


def test_uploading_a_real_capture_creates_the_alert(tmp_path):
    client = TestClient(create_app(tmp_path / "data", explain=False))
    with (PCAPS / "telnet.pcap").open("rb") as capture:
        response = client.post("/api/analyses", files={"file": ("telnet.pcap", capture)})
    assert response.status_code == 200, response.text

    [alert] = client.get("/api/alerts").json()
    assert alert["rule_id"] == "cleartext.telnet"
    assert alert["dst_port"] == 23

    report = client.get(f"/api/analyses/{response.json()['analysis_id']}").json()
    assert report["tools"]["zeek"] is True
    assert report["input"]["name"] == "telnet.pcap"

    events = client.get("/api/events").json()
    assert events
    assert {event["sensor_id"] for event in events} == {"pcap"}
    assert list((tmp_path / "data" / "uploads").iterdir()) == []  # deleted afterwards
