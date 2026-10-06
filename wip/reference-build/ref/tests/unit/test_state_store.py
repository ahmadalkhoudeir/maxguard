"""Tests for maxguard.storage.state.StateStore (SQLite: analyses, alerts, audit)."""

import copy
import sqlite3
import time
from pathlib import Path

import pytest

import maxguard.rules  # noqa: F401  (importing registers every rule)
from maxguard.events.normalize import normalize
from maxguard.rules.base import run_all
from maxguard.storage.state import ALERT_STATUSES, StateStore

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "zeek"


def make_report(capture: str) -> dict:
    """A report dict shaped like pipeline.analyze() output, built from a fixture."""
    log_dir = FIXTURES / capture
    return {
        "schema": "maxguard.report/2",
        "input": {"name": f"{capture}.pcap", "sha256": "ab" * 32, "adapter": "pcap"},
        "tools": {"zeek": True, "suricata": True},
        "frameworks": [],
        "findings": [f.to_dict() for f in run_all(log_dir)],
        "assets": [],
        "events": normalize(log_dir, sensor_id="pcap"),
        "ai": {"status": "disabled", "model": None, "explained": 0, "dropped_sentences": 0},
    }


@pytest.fixture
def store(tmp_path) -> StateStore:
    return StateStore(tmp_path / "data" / "state.db")


def only_alert(store: StateStore) -> dict:
    [alert] = store.list_alerts()
    return alert


def test_database_uses_wal_and_has_the_tables(store):
    conn = sqlite3.connect(store.path)
    assert conn.execute("PRAGMA journal_mode").fetchone()[0] == "wal"
    tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert {"analyses", "alerts", "audit"} <= tables
    conn.close()


def test_saving_a_report_creates_new_alerts(store):
    report = make_report("telnet")
    analysis_id = store.save_analysis(report, received_at=1000.0)

    alert = only_alert(store)
    finding = report["findings"][0]
    assert alert["finding_id"] == finding["finding_id"]
    assert alert["rule_id"] == "cleartext.telnet"
    assert alert["status"] == "new" and alert["assignee"] == ""
    assert alert["analysis_id"] == analysis_id
    assert alert["first_received_at"] == alert["last_received_at"] == 1000.0
    assert alert["evidence"] == finding["evidence"]  # the full finding is kept
    assert store.get_alert(finding["finding_id"]) == alert


def test_reupload_updates_the_same_alert(store):
    report = make_report("telnet")
    first_id = store.save_analysis(report, received_at=1000.0)
    store.update_alert(report["findings"][0]["finding_id"], actor="amory", at=1100.0,
                       status="investigating", assignee="amory")

    later = copy.deepcopy(report)  # a NEW capture showing the same problem over a wider time
    later["input"]["sha256"] = "cd" * 32
    later["findings"][0]["first_seen"] -= 60
    later["findings"][0]["last_seen"] += 60
    second_id = store.save_analysis(later, received_at=2000.0)

    alert = only_alert(store)
    old = report["findings"][0]
    assert second_id != first_id
    assert alert["count"] == 2
    assert alert["first_seen"] == old["first_seen"] - 60
    assert alert["last_seen"] == old["last_seen"] + 60
    assert (alert["status"], alert["assignee"]) == ("investigating", "amory")  # kept
    assert alert["first_received_at"] == 1000.0 and alert["last_received_at"] == 2000.0
    assert alert["analysis_id"] == second_id  # the latest analysis that reported it


def test_saving_the_same_report_at_the_same_time_twice_counts_once(store):
    report = make_report("ftp")
    assert store.save_analysis(report, received_at=1000.0) == store.save_analysis(
        report, received_at=1000.0)
    assert only_alert(store)["count"] == 1
    assert len(store.list_analyses()) == 1


def test_stored_analysis_has_no_events(store):
    report = make_report("plain_http")
    analysis_id = store.save_analysis(report, received_at=1000.0)

    stored = store.get_analysis(analysis_id)

    assert "events" not in stored  # events live in the EventStore
    assert stored["findings"] == report["findings"]
    assert store.get_analysis("0000000000000000") is None
    [row] = store.list_analyses()
    assert row == {"analysis_id": analysis_id, "received_at": 1000.0,
                   "input_name": "plain_http.pcap", "input_sha256": "ab" * 32,
                   "finding_count": 1}


def test_list_alerts_filters_and_sorts_most_severe_first(store):
    for i, capture in enumerate(["plain_http", "telnet", "cert_self_signed", "ftp"]):
        store.save_analysis(make_report(capture), received_at=1000.0 + i)

    alerts = store.list_alerts()
    ranks = [("critical", "high", "medium", "low", "info").index(a["severity"]) for a in alerts]
    assert ranks == sorted(ranks)
    assert {a["rule_id"] for a in store.list_alerts(severity="high")} == {
        "cleartext.telnet", "cleartext.ftp"}
    assert store.list_alerts(status="resolved") == []
    assert len(store.list_alerts(limit=2)) == 2


def test_bad_filters_are_rejected(store):
    with pytest.raises(ValueError):
        store.list_alerts(status="done")
    with pytest.raises(ValueError):
        store.list_alerts(severity="urgent")


def test_update_alert_changes_status_and_writes_audit(store):
    report = make_report("imap")
    store.save_analysis(report, received_at=1000.0)
    finding_id = report["findings"][0]["finding_id"]

    alert = store.update_alert(finding_id, actor="ahmad", at=1500.0, status="resolved")

    assert alert["status"] == "resolved"
    [entry] = store.list_audit()
    assert entry["actor"] == "ahmad" and entry["at"] == 1500.0
    assert entry["action"] == "alert.update" and entry["target"] == finding_id
    assert entry["details"] == {"status": {"from": "new", "to": "resolved"}}


def test_update_without_a_real_change_writes_no_audit(store):
    report = make_report("imap")
    store.save_analysis(report, received_at=1000.0)
    finding_id = report["findings"][0]["finding_id"]

    store.update_alert(finding_id, actor="ahmad", at=1500.0, status="new")

    assert store.list_audit() == []


def test_update_alert_validates_input(store):
    report = make_report("imap")
    store.save_analysis(report, received_at=1000.0)
    with pytest.raises(ValueError):
        store.update_alert(report["findings"][0]["finding_id"], actor="x", at=1.0,
                           status="closed")
    with pytest.raises(KeyError):
        store.update_alert("0000000000000000", actor="x", at=1.0, status="resolved")
    assert ALERT_STATUSES == ("new", "investigating", "resolved", "false_positive")


def test_audit_is_listed_newest_first(store):
    first = store.add_audit(actor="system", action="analysis.saved", target="a1",
                            details={"findings": 1}, at=10.0)
    second = store.add_audit(actor="fiona", action="block.approved", target="10.0.0.5",
                             details={}, at=20.0)
    assert second > first
    assert [e["audit_id"] for e in store.list_audit()] == [second, first]
    assert store.list_audit(limit=1)[0]["details"] == {}


def test_data_survives_reopening(store):
    store.save_analysis(make_report("pop3"), received_at=1000.0)
    reopened = StateStore(store.path)  # "CREATE TABLE IF NOT EXISTS": safe to run again
    assert len(reopened.list_alerts()) == 1


def test_store_never_reads_the_clock(store, monkeypatch):
    def no_clock():
        raise AssertionError("StateStore must not read the clock")

    monkeypatch.setattr(time, "time", no_clock)
    monkeypatch.setattr(time, "time_ns", no_clock)
    report = make_report("telnet")
    store.save_analysis(report, received_at=1000.0)
    store.update_alert(report["findings"][0]["finding_id"], actor="x", at=1001.0,
                       assignee="jaiden")
    store.add_audit(actor="x", action="test", target="t", details={}, at=1002.0)
    assert len(store.list_audit()) == 2
