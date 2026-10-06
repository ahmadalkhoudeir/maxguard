"""Alerts across several uploads: repeats are not double counted, fixes that come back reopen."""

from copy import deepcopy

from maxguard.storage.state import StateStore


def report(sha: str, last_seen: float, count: int = 1) -> dict:
    finding = {"finding_id": "f1", "rule_id": "cleartext.telnet", "severity": "high",
               "first_seen": last_seen - 1, "last_seen": last_seen, "count": count,
               "title": "Telnet session in cleartext", "evidence": []}
    return {"schema": "maxguard.report/2", "input": {"name": "x.pcap", "sha256": sha,
            "adapter": "pcap"}, "findings": [finding], "events": []}


def test_same_file_uploaded_twice_is_not_counted_twice(tmp_path):
    store = StateStore(tmp_path / "state.db")
    store.save_analysis(report("aaaa", 100.0, count=3), received_at=1000.0)
    store.save_analysis(report("aaaa", 100.0, count=3), received_at=2000.0)  # same file, later

    alert = store.get_alert("f1")
    assert alert["count"] == 3
    assert alert["last_received_at"] == 2000.0
    assert len(store.list_analyses()) == 2  # both uploads are still on record


def test_different_files_add_up(tmp_path):
    store = StateStore(tmp_path / "state.db")
    store.save_analysis(report("aaaa", 100.0, count=3), received_at=1000.0)
    store.save_analysis(report("bbbb", 200.0, count=2), received_at=2000.0)
    assert store.get_alert("f1")["count"] == 5


def test_resolved_alert_reopens_when_new_evidence_arrives(tmp_path):
    store = StateStore(tmp_path / "state.db")
    store.save_analysis(report("aaaa", 100.0), received_at=1000.0)
    store.update_alert("f1", actor="ahmad", at=1100.0, status="resolved")

    store.save_analysis(report("bbbb", 200.0), received_at=2000.0)  # newer traffic

    assert store.get_alert("f1")["status"] == "new"
    newest = store.list_audit()[0]
    assert (newest["action"], newest["actor"], newest["at"]) == ("alert.reopen", "maxguard", 2000.0)


def test_resolved_alert_stays_resolved_for_old_evidence(tmp_path):
    store = StateStore(tmp_path / "state.db")
    store.save_analysis(report("aaaa", 100.0), received_at=1000.0)
    store.update_alert("f1", actor="ahmad", at=1100.0, status="resolved")

    store.save_analysis(report("cccc", 100.0), received_at=2000.0)  # nothing newer

    assert store.get_alert("f1")["status"] == "resolved"


def test_false_positive_is_never_reopened(tmp_path):
    store = StateStore(tmp_path / "state.db")
    store.save_analysis(report("aaaa", 100.0), received_at=1000.0)
    store.update_alert("f1", actor="ahmad", at=1100.0, status="false_positive")
    store.save_analysis(deepcopy(report("bbbb", 300.0)), received_at=2000.0)
    assert store.get_alert("f1")["status"] == "false_positive"
