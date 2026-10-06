"""Tests for maxguard.events.lookup.records_for (evidence record_id -> raw record)."""

from pathlib import Path

import maxguard.rules  # noqa: F401  (importing registers every rule)
from maxguard.adapters.base import read_log
from maxguard.events.lookup import log_names, records_for
from maxguard.ids import record_id
from maxguard.rules.base import run_all

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "zeek"


def test_finds_the_evidence_records_of_a_finding():
    log_dir = FIXTURES / "cert_expired"
    [finding] = run_all(log_dir)
    wanted = {ev.record_id for ev in finding.evidence}

    records = records_for(log_dir, wanted)

    assert set(records) == wanted
    assert sorted(rec["_log"] for rec in records.values()) == ["ssl.log", "x509.log"]
    for rid, rec in records.items():
        raw = {k: v for k, v in rec.items() if k != "_log"}
        assert record_id(rec["_log"], raw) == rid  # "_log" is added after hashing


def test_finds_suricata_records_too():
    log_dir = FIXTURES / "tls_weak_version"
    tls = next(r for r in read_log(log_dir, "eve.json") if r["event_type"] == "tls")
    rid = record_id("eve.json", tls)

    records = records_for(log_dir, {rid})

    assert records[rid]["_log"] == "eve.json"
    assert records[rid]["tls"]["ja4"] == "t10d230600_44099cda8a52_242d16716555"


def test_unknown_ids_are_left_out():
    log_dir = FIXTURES / "telnet"
    rec = next(read_log(log_dir, "maxguard_cleartext.log"))
    rid = record_id("maxguard_cleartext.log", rec)

    records = records_for(log_dir, {rid, "0000000000000000"})

    assert list(records) == [rid]


def test_no_ids_and_empty_folder_give_empty_result(tmp_path):
    assert records_for(FIXTURES / "telnet", set()) == {}
    assert records_for(tmp_path, {"0000000000000000"}) == {}


def test_log_names_are_sorted_with_eve_json_last():
    assert log_names(FIXTURES / "telnet") == [
        "conn.log", "known_hosts.log", "maxguard_cleartext.log", "eve.json"]
