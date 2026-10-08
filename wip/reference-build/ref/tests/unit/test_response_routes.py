"""Tests for the /api/response routes (Ahmad, AHM-08).

The whole app from maxguard/api/app.py, with TestClient, and the fake OPNsense
server from test_opnsense.py (never a real firewall).
"""

import time

import pytest
from fastapi.testclient import TestClient
from test_opnsense import KEY, SECRET, FakeOPNsense

from maxguard.api.app import create_app
from maxguard.events.normalize import EVENT_KEYS

BAD = "203.0.113.7"


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.delenv("MAXGUARD_OPNSENSE_URL", raising=False)
    monkeypatch.delenv("MAXGUARD_OFFLINE", raising=False)
    return TestClient(create_app(tmp_path / "data", explain=False))


@pytest.fixture
def firewall(tmp_path, monkeypatch):
    """A fake OPNsense, configured the way a user would: URL, CA file, key file."""
    fake = FakeOPNsense(tmp_path)
    monkeypatch.setenv("MAXGUARD_OPNSENSE_URL", fake.url)
    monkeypatch.setenv("MAXGUARD_OPNSENSE_CA", str(fake.ca_file))
    key_dir = tmp_path / "data" / "opnsense"
    key_dir.mkdir(parents=True)
    (key_dir / "apikey.txt").write_text(f"key={KEY}\nsecret={SECRET}\n")
    yield fake
    fake.stop()


def propose(client, ip=BAD, direction="both") -> dict:
    response = client.post("/api/response/proposals",
                           json={"actor": "ahmad", "ip": ip, "direction": direction})
    assert response.status_code == 200, response.text
    return response.json()


def step(client, proposal_id: int, name: str, **body):
    return client.post(f"/api/response/proposals/{proposal_id}/{name}",
                       json={"actor": "ahmad", **body})


def response_audit(client) -> list[dict]:
    rows = client.get("/api/audit").json()
    return [row for row in reversed(rows) if row["action"].startswith("response.")]


def test_manual_workflow(client):
    proposal = propose(client)
    pid = proposal["proposal_id"]
    assert proposal["rules"]["nftables"]["block"]       # the commands are shown at once
    assert step(client, pid, "preview").json()["preview"]["connections"] == 0
    assert step(client, pid, "approve", confirm_ip=BAD).json()["state"] == "approved"
    applied = step(client, pid, "apply").json()
    assert applied["state"] == "applied" and applied["method"] == "manual"
    assert step(client, pid, "revert").json()["state"] == "reverted"
    assert [row["action"] for row in response_audit(client)] == [
        "response.proposed", "response.previewed", "response.approved",
        "response.applied", "response.reverted"]
    assert {row["target"] for row in response_audit(client)} == {str(pid)}


def test_approval_without_the_typed_ip_fails(client):
    pid = propose(client)["proposal_id"]
    step(client, pid, "preview")
    assert step(client, pid, "approve").status_code == 400                  # missing
    assert step(client, pid, "approve", confirm_ip="203.0.113.8").status_code == 400
    assert client.post(f"/api/response/proposals/{pid}/approve",
                       json={"confirm_ip": BAD}).status_code == 422          # no actor
    assert client.get(f"/api/response/proposals/{pid}").json()["state"] == "previewed"
    refused = [r for r in response_audit(client) if r["action"] == "response.approve_refused"]
    assert len(refused) == 2


@pytest.mark.parametrize("ip", ["1.2.3.4; rm -rf /", "127.0.0.1", "::1", "224.0.0.251",
                                "0.0.0.0", "fe80::1", "2001:db8::1%$(id)"])
def test_bad_addresses_are_refused(client, ip):
    response = client.post("/api/response/proposals",
                           json={"actor": "ahmad", "ip": ip, "direction": "both"})
    assert response.status_code == 400
    assert client.get("/api/response/proposals").json() == []


def test_unknown_direction_is_refused(client):
    response = client.post("/api/response/proposals",
                           json={"actor": "ahmad", "ip": BAD, "direction": "sideways"})
    assert response.status_code == 400


def test_missing_proposal_and_wrong_order(client):
    assert client.get("/api/response/proposals/42").status_code == 404
    assert step(client, 42, "approve", confirm_ip=BAD).status_code == 404
    pid = propose(client)["proposal_id"]
    assert step(client, pid, "approve", confirm_ip=BAD).status_code == 409   # no preview yet
    assert step(client, pid, "revert").status_code == 409                    # not applied


def test_reject(client):
    pid = propose(client)["proposal_id"]
    assert step(client, pid, "reject", reason="our own VPN").json()["state"] == "rejected"
    assert step(client, pid, "preview").status_code == 409


def test_preview_counts_events_from_the_event_store(client):
    now = time.time()
    event = dict.fromkeys(EVENT_KEYS, "")
    event.update(event_id="ev1", ts=now - 3600, sensor_id="pcap", source="zeek",
                 log="conn.log", kind="conn", community_id="1:x=", src_ip=BAD,
                 dst_ip="192.168.1.20", src_port=40000, dst_port=22, proto="tcp",
                 service="ssh", bytes_out=1, bytes_in=1)
    client.app.state.event_store.write([event])
    pid = propose(client, direction="inbound")["proposal_id"]
    summary = step(client, pid, "preview").json()["preview"]
    assert summary["connections"] == 1 and summary["devices"] == ["192.168.1.20"]


def test_cross_site_requests_are_refused(client):
    response = client.post("/api/response/proposals",
                           json={"actor": "x", "ip": BAD, "direction": "both"},
                           headers={"Sec-Fetch-Site": "cross-site"})
    assert response.status_code == 403


def test_opnsense_apply_and_revert(client, firewall):
    pid = propose(client, direction="both")["proposal_id"]
    step(client, pid, "preview")
    step(client, pid, "approve", confirm_ip=BAD)
    applied = step(client, pid, "apply")
    assert applied.status_code == 200, applied.text
    assert applied.json()["method"] == "enforcer"
    assert firewall.aliases == {"maxguard_block_in": {BAD}, "maxguard_block_out": {BAD}}
    assert firewall.reconfigures == 2
    assert step(client, pid, "revert").json()["state"] == "reverted"
    assert firewall.aliases == {"maxguard_block_in": set(), "maxguard_block_out": set()}
    assert [row["action"] for row in response_audit(client)][-2:] == [
        "response.applied", "response.reverted"]


def test_firewall_error_is_502_and_nothing_changes(client, firewall):
    firewall.aliases = {}  # the user has not created the aliases on the firewall
    pid = propose(client)["proposal_id"]
    step(client, pid, "preview")
    step(client, pid, "approve", confirm_ip=BAD)
    response = step(client, pid, "apply")
    assert response.status_code == 502
    assert client.get(f"/api/response/proposals/{pid}").json()["state"] == "approved"
    assert response_audit(client)[-1]["action"] == "response.apply_failed"


def test_a_second_open_proposal_for_the_same_address_is_409(client):
    propose(client)
    response = client.post("/api/response/proposals",
                           json={"actor": "fiona", "ip": BAD, "direction": "inbound"})
    assert response.status_code == 409
    assert len(client.get("/api/response/proposals").json()) == 1
