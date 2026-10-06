"""Contract 1 (Finding), the record IDs, and Contract 2's loader (JAI-02).

These tests protect the promises other modules rely on: the original Fall 2026
fields still work, IDs never change for the same input, and mapping files fill
controls and ATT&CK techniques.
"""

import pytest

from maxguard.ids import evidence, record_id
from maxguard.mapping.loader import apply, validate
from maxguard.models import Evidence, Finding, make_finding_id

TELNET = {"ts": 1791250285.789302, "uid": "CthjcT337OAZB44O4f", "id.orig_h": "172.18.0.3",
          "id.orig_p": 55398, "id.resp_h": "172.18.0.2", "id.resp_p": 23,
          "service": "", "proto": "telnet"}


def make_finding(**changes) -> Finding:
    values = dict(rule_id="cleartext.telnet", title="Telnet session in cleartext",
                  severity="high", src_ip="172.18.0.3", dst_ip="172.18.0.2", dst_port=23,
                  protocol="telnet", first_seen=1.0, last_seen=2.0)
    values.update(changes)
    return Finding(**values)


# ---- Contract 1: Finding ----

def test_original_positional_fields_still_work():
    # Exactly how the Fall 2026 roadmap created findings: positional arguments.
    f = Finding("cleartext.telnet", "Telnet", "high", "10.0.0.1", "10.0.0.2", 23,
                "telnet", 1.0, 2.0)
    assert f.count == 1 and f.evidence == [] and f.controls == [] and f.explanation is None


def test_new_fields_have_defaults():
    f = make_finding()
    assert f.source == "zeek"
    assert f.attack == [] and f.explanation_sentences == []


def test_finding_id_is_computed_from_the_dedup_key():
    f = make_finding()
    assert f.finding_id == make_finding_id("cleartext.telnet", "172.18.0.3", "172.18.0.2", 23)
    assert len(f.finding_id) == 16
    assert make_finding(first_seen=99.0).finding_id == f.finding_id  # times are not in the key


def test_a_misspelled_severity_fails_immediately():
    with pytest.raises(ValueError, match="severity"):
        make_finding(severity="hgih")


def test_to_dict_includes_old_and_new_fields():
    d = make_finding(evidence=[Evidence("conn.log", "C1", 1.0, "abc")]).to_dict()
    assert d["evidence"][0] == {"log": "conn.log", "uid": "C1", "ts": 1.0, "record_id": "abc"}
    assert {"finding_id", "attack", "explanation_sentences", "source"} <= d.keys()


# ---- record IDs ----

def test_record_id_is_stable_and_ignores_key_order():
    shuffled = dict(reversed(list(TELNET.items())))
    assert record_id("maxguard_cleartext.log", TELNET) == record_id("maxguard_cleartext.log",
                                                                    shuffled)


def test_record_id_depends_on_the_log_name_and_content():
    assert record_id("a.log", TELNET) != record_id("b.log", TELNET)
    assert record_id("a.log", TELNET) != record_id("a.log", {**TELNET, "id.resp_p": 24})


def test_record_id_ignores_suricatas_random_flow_id():
    eve = {"timestamp": "2026-10-06T01:31:25.789302+0000", "community_id": "1:abc=",
           "event_type": "flow"}
    assert record_id("eve.json", {**eve, "flow_id": 1}) == record_id("eve.json",
                                                                    {**eve, "flow_id": 2})


def test_evidence_for_a_zeek_record():
    e = evidence("maxguard_cleartext.log", TELNET)
    assert (e.log, e.uid, e.ts) == ("maxguard_cleartext.log", "CthjcT337OAZB44O4f",
                                    1791250285.789302)
    assert e.record_id == record_id("maxguard_cleartext.log", TELNET)


def test_evidence_for_a_suricata_record_uses_the_community_id():
    eve = {"timestamp": "2026-10-06T01:31:25.789302+0000", "flow_id": 7,
           "community_id": "1:4o5Au3/nA2pOwrsX1D6xTgHOOr4=", "event_type": "flow"}
    e = evidence("eve.json", eve)
    assert e.uid == "1:4o5Au3/nA2pOwrsX1D6xTgHOOr4="
    assert e.ts == pytest.approx(1791250285.789302)


# ---- Contract 2: mapping loader ----

PCI = {"framework": "PCI DSS", "version": "4.0.1", "source": "https://example.invalid/pci",
       "mappings": {"cleartext.telnet": [
           {"control_id": "4.2.1", "title": "A title", "rationale": "A reason."}]}}
ATTACK = {"framework": "MITRE ATT&CK", "version": "v19.2", "source": "https://example.invalid/a",
          "mappings": {"cleartext.telnet": [
              {"control_id": "T1040", "title": "Network Sniffing", "rationale": "A reason.",
               "tactic": "credential-access"}]}}


def test_apply_fills_controls_and_attack_techniques():
    f = make_finding()
    apply([f], [PCI, ATTACK])
    assert [(c.framework, c.version, c.control_id) for c in f.controls] == [
        ("PCI DSS", "4.0.1", "4.2.1")]
    assert [(t.technique_id, t.tactic, t.version) for t in f.attack] == [
        ("T1040", "credential-access", "v19.2")]


def test_selecting_frameworks_never_drops_attack():
    f = make_finding()
    apply([f], [PCI, ATTACK], selected={"NIST SP 800-53"})
    assert f.controls == [] and len(f.attack) == 1


def test_validate_reports_problems():
    broken = {"framework": "MITRE ATT&CK", "version": "v19.2", "source": "x",
              "mappings": {"no.such_rule": [{"control_id": "T1040", "title": "",
                                              "rationale": "r"}]}}
    problems = validate(broken, known_rule_ids={"cleartext.telnet"})
    assert "unknown rule_id 'no.such_rule'" in problems
    assert any("missing 'title'" in p for p in problems)
    assert any("missing 'tactic'" in p for p in problems)
    assert validate(PCI, known_rule_ids={"cleartext.telnet"}) == []
