"""Tests for per-device baselines and rule baseline.new_service (Fiona, FIO-07).

The lab fixtures in tests/fixtures/zeek/ all come from one client (172.18.0.3)
talking to one server (172.18.0.2), each capture on a different service. So the
"learning period" here is the plain_http and clean_tls13 captures, and the
telnet capture is the device trying something new.
"""

from __future__ import annotations

import json
import random
from pathlib import Path

import pytest

from maxguard.events.normalize import normalize
from maxguard.rules.base import RULES, run_all
from maxguard.rules.baseline import (
    STATEFUL_RULES,
    build_baseline,
    new_service,
    run_stateful,
    stateful_rule,
)

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "zeek"
CLIENT, SERVER = "172.18.0.3", "172.18.0.2"
# Every lab capture was made after this moment, so all their events count as "after learning".
LEARNING_ENDS = 1791250000.0


def events_of(*captures: str) -> list[dict]:
    events: list[dict] = []
    for capture in captures:
        events.extend(normalize(FIXTURES / capture, sensor_id="pcap"))
    return events


@pytest.fixture
def baseline() -> dict:
    return build_baseline(events_of("plain_http", "clean_tls13"))


def test_baseline_lists_services_and_peers(baseline):
    assert baseline == {CLIENT: {"peers": 1, "services": [[80, "tcp", "http"],
                                                          [4436, "tcp", "ssl"]]}}


def test_same_events_always_build_the_same_baseline():
    events = events_of("plain_http", "clean_tls13", "_handmade/dns_dhcp", "ftp")
    shuffled = list(events)
    random.Random(7).shuffle(shuffled)  # a different order must not matter
    first, second = build_baseline(events), build_baseline(shuffled)
    assert json.dumps(first) == json.dumps(second)  # byte for byte, key order included


def test_baseline_survives_a_json_round_trip(baseline):
    # The baseline is stored as JSON between runs; the rule must work on the loaded copy.
    stored = json.loads(json.dumps(baseline))
    assert stored == baseline
    context = {"baseline": stored, "learning_ends": LEARNING_ENDS}
    assert new_service(FIXTURES / "plain_http", context) == []


def test_several_devices_and_ftp_data_left_out():
    baseline = build_baseline(events_of("_handmade/dns_dhcp", "ftp"))
    assert baseline["192.168.56.50"] == {"peers": 1, "services": [[53, "udp", "dns"]]}
    # ftp-data ports change on every transfer, so only the control port 21 is learned.
    assert baseline[CLIENT]["services"] == [[21, "tcp", "ftp"]]
    assert list(baseline) == sorted(baseline)


def test_a_new_port_is_found(baseline):
    context = {"baseline": baseline, "learning_ends": LEARNING_ENDS}
    [finding] = new_service(FIXTURES / "telnet", context)
    assert finding.rule_id == "baseline.new_service"
    assert finding.severity == "medium"
    assert (finding.src_ip, finding.dst_ip, finding.dst_port) == (CLIENT, SERVER, 23)
    assert finding.protocol == "tcp"  # Zeek has no Telnet analyzer, so service is ""
    [ev] = finding.evidence
    [conn] = [e for e in normalize(FIXTURES / "telnet", "pcap") if e["log"] == "conn.log"]
    assert ev.log == "conn.log" and ev.record_id == conn["event_id"]


def test_a_known_service_is_not_found(baseline):
    context = {"baseline": baseline, "learning_ends": LEARNING_ENDS}
    assert new_service(FIXTURES / "plain_http", context) == []
    assert new_service(FIXTURES / "clean_tls13", context) == []


def test_nothing_is_found_during_the_learning_period(baseline):
    # The telnet capture happened before this "end of learning": it is still learning.
    context = {"baseline": baseline, "learning_ends": 1791260000.0}
    assert new_service(FIXTURES / "telnet", context) == []


def test_unknown_devices_are_skipped():
    context = {"baseline": {"192.0.2.99": {"peers": 1, "services": [[80, "tcp", "http"]]}},
               "learning_ends": LEARNING_ENDS}
    assert new_service(FIXTURES / "telnet", context) == []


def test_same_logs_and_context_give_the_same_findings(baseline):
    context = {"baseline": baseline, "learning_ends": LEARNING_ENDS}
    first = [f.to_dict() for f in run_stateful(FIXTURES / "telnet", context)]
    second = [f.to_dict() for f in run_stateful(FIXTURES / "telnet", context)]
    assert first == second and len(first) == 1


def test_stateful_registry_is_separate_from_run_all():
    assert STATEFUL_RULES["baseline.new_service"] is new_service
    assert "baseline.new_service" not in RULES
    # run_all() is unchanged: on the telnet capture it still finds only cleartext.telnet.
    assert {f.rule_id for f in run_all(FIXTURES / "telnet")} == {"cleartext.telnet"}


def test_duplicate_rule_ids_are_refused():
    with pytest.raises(ValueError):
        stateful_rule("baseline.new_service")(new_service)
    with pytest.raises(ValueError):
        stateful_rule("cleartext.telnet")(new_service)  # taken in the normal registry
