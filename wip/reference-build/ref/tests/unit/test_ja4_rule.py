"""Tests for the tls.ja4_watchlist rule.

The rule is not in maxguard/rules/__init__.py yet, so it is imported directly,
and every test writes its own temporary watchlist instead of editing the
shipped (empty) one.
"""

import re
from pathlib import Path

import pytest
import yaml

from maxguard.adapters.base import read_log
from maxguard.ids import record_id
from maxguard.rules import ja4
from maxguard.rules.base import RULES

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "zeek"
# The Python lab client's JA4 in clean_tls13/eve.json (Suricata 7.0.10).
LAB_JA4 = "t13d041000_16476d049b0b_78f1d400d464"


def write_watchlist(tmp_path: Path, entries) -> Path:
    path = tmp_path / "ja4_watchlist.yaml"
    path.write_text(yaml.safe_dump(entries))
    return path


def lab_entry(ja4_value: str = LAB_JA4) -> dict:
    return {"ja4": ja4_value, "label": "Lab Python client", "source": "MaxGuard lab capture"}


def test_matching_ja4_gives_one_high_finding(tmp_path):
    watchlist = write_watchlist(tmp_path, [lab_entry()])
    [f] = ja4.ja4_watchlist(FIXTURES / "clean_tls13", watchlist_path=watchlist)
    assert (f.rule_id, f.severity, f.source) == ("tls.ja4_watchlist", "high", "suricata")
    assert (f.src_ip, f.dst_ip, f.dst_port, f.protocol) == ("172.18.0.3", "172.18.0.2", 4436, "tls")
    assert f.title == "TLS client matches JA4 watchlist: Lab Python client"
    assert f.details == {"ja4": LAB_JA4, "label": "Lab Python client",
                         "watchlist_source": "MaxGuard lab capture",
                         "sni": "port4436.lab.invalid"}


def test_evidence_points_at_the_eve_tls_record(tmp_path):
    watchlist = write_watchlist(tmp_path, [lab_entry()])
    [f] = ja4.ja4_watchlist(FIXTURES / "clean_tls13", watchlist_path=watchlist)
    [tls_rec] = [r for r in read_log(FIXTURES / "clean_tls13", "eve.json")
                 if r["event_type"] == "tls"]
    [ev] = f.evidence
    assert ev.log == "eve.json"
    assert ev.uid == tls_rec["community_id"]  # links to Zeek's conn.log community_id
    assert ev.record_id == record_id("eve.json", tls_rec)
    assert f.first_seen == f.last_seen == ev.ts


def test_same_logs_same_finding_id_and_record_ids(tmp_path):
    watchlist = write_watchlist(tmp_path, [lab_entry()])
    first = ja4.ja4_watchlist(FIXTURES / "clean_tls13", watchlist_path=watchlist)
    again = ja4.ja4_watchlist(FIXTURES / "clean_tls13", watchlist_path=watchlist)
    assert [f.to_dict() for f in first] == [f.to_dict() for f in again]


def test_other_fingerprints_do_not_match(tmp_path):
    watchlist = write_watchlist(tmp_path, [lab_entry()])
    # cert_expired's client used TLS 1.2, so its JA4 is different
    assert ja4.ja4_watchlist(FIXTURES / "cert_expired", watchlist_path=watchlist) == []


def test_no_eve_json_means_no_findings(tmp_path):
    watchlist = write_watchlist(tmp_path, [lab_entry()])
    assert ja4.ja4_watchlist(FIXTURES / "telnet" / "missing", watchlist_path=watchlist) == []


def test_shipped_watchlist_is_empty_and_valid():
    assert ja4.load_watchlist() == {}
    assert ja4.ja4_watchlist(FIXTURES / "clean_tls13") == []


def test_rule_is_registered_under_its_id():
    assert RULES["tls.ja4_watchlist"] is ja4.ja4_watchlist


def test_upper_case_entry_still_matches(tmp_path):
    watchlist = write_watchlist(tmp_path, [lab_entry(LAB_JA4.upper())])
    assert len(ja4.ja4_watchlist(FIXTURES / "clean_tls13", watchlist_path=watchlist)) == 1


@pytest.mark.parametrize("entries, message", [
    ({"ja4": LAB_JA4}, "expected a list"),
    ([{"ja4": LAB_JA4, "label": "x"}], "missing ['source']"),
    (["t13d041000_16476d049b0b_78f1d400d464"], "expected keys"),
    ([lab_entry("0123456789abcdef0123456789abcdef")], "is not a JA4"),  # JA3-sized MD5
])
def test_bad_watchlist_entries_are_rejected(tmp_path, entries, message):
    watchlist = write_watchlist(tmp_path, entries)
    with pytest.raises(ja4.WatchlistError, match=re.escape(message)):
        ja4.load_watchlist(watchlist)


@pytest.mark.parametrize("text, ok", [
    ("t13d1516h2_8daaf6152771_e5627efa2ab1", True),  # example from the JA4 spec
    (LAB_JA4, True),
    ("t13d1516h2_8daaf6152771", False),  # only two parts
    ("t13d1516h2_8daaf615277_e5627efa2ab1", False),  # 11-character hash
    ("t13d1516h2_8daaf615277z_e5627efa2ab1", False),  # not hex
])
def test_looks_like_ja4(text, ok):
    assert ja4.looks_like_ja4(text) is ok
