"""TLS and certificate rule tests (Fiona, FIO-02): positive and negative for each rule.

tests/fixtures/zeek/<capture>/ holds the Zeek 9.0.0 logs of the lab capture
tests/pcaps/<capture>.pcap. Each capture shows exactly one weakness.
"""

from pathlib import Path

import pytest

import maxguard.rules  # noqa: F401  (importing registers every rule)
from maxguard.adapters.base import read_log
from maxguard.ids import record_id
from maxguard.rules.base import RULES

REPO = Path(__file__).resolve().parents[2]
FIXTURES = REPO / "tests" / "fixtures" / "zeek"

# capture folder -> the one rule it must trigger
EXPECTED = {
    "tls_weak_version": "tls.weak_version",
    "tls_weak_cipher": "tls.weak_cipher",
    "cert_expired": "cert.expired",
    "cert_self_signed": "cert.self_signed",
    "cert_weak_key": "cert.weak_key",
    "cert_sha1": "cert.sha1_signature",
}

# rule -> a capture that ALMOST matches it but must not trigger it
NEAR_MISS = {
    "tls.weak_version": "clean_tls13",  # TLSv13
    "tls.weak_cipher": "tls_weak_version",  # old version, but a strong cipher
    "cert.expired": "cert_self_signed",  # bad certificate, but not expired
    "cert.self_signed": "cert_expired",  # signed by the lab CA, not by itself
    "cert.weak_key": "cert_sha1",
    "cert.sha1_signature": "cert_weak_key",
}

TLS_AND_CERT_RULES = set(EXPECTED.values())


def test_the_six_tls_and_certificate_rules_are_registered():
    assert TLS_AND_CERT_RULES <= set(RULES)


def test_every_rule_has_a_near_miss_test():
    # A new rule must come with a negative test, not only a positive one.
    assert set(NEAR_MISS) == TLS_AND_CERT_RULES


@pytest.mark.parametrize(("capture", "rule_id"), sorted(EXPECTED.items()))
def test_rule_fires_on_its_capture(capture, rule_id):
    findings = RULES[rule_id](FIXTURES / capture)

    assert len(findings) >= 1
    for finding in findings:
        assert finding.rule_id == rule_id
        assert finding.protocol == "tls"
        assert finding.evidence, "every finding needs evidence the AI can cite"


@pytest.mark.parametrize(("capture", "rule_id"), sorted(EXPECTED.items()))
def test_evidence_points_at_real_log_records(capture, rule_id):
    # The AI cites evidence by record_id, so each one must name a record that
    # really is in that log file (ssl.log, and x509.log for certificate rules).
    log_dir = FIXTURES / capture
    for finding in RULES[rule_id](log_dir):
        for ev in finding.evidence:
            ids_in_log = {record_id(ev.log, rec) for rec in read_log(log_dir, ev.log)}
            assert ev.record_id in ids_in_log


@pytest.mark.parametrize(("rule_id", "capture"), sorted(NEAR_MISS.items()))
def test_rule_is_silent_on_near_miss(rule_id, capture):
    assert RULES[rule_id](FIXTURES / capture) == []


@pytest.mark.parametrize("rule_id", sorted(TLS_AND_CERT_RULES))
def test_rule_is_silent_on_clean_tls13(rule_id):
    assert RULES[rule_id](FIXTURES / "clean_tls13") == []


def test_certificate_findings_cite_both_the_session_and_the_certificate():
    [finding] = RULES["cert.expired"](FIXTURES / "cert_expired")
    assert [ev.log for ev in finding.evidence] == ["ssl.log", "x509.log"]


def test_expired_means_expired_when_seen_not_today():
    # cert.expired compares with the capture time, so the result never depends
    # on the day the analysis runs (CLAUDE.md rule 2).
    [finding] = RULES["cert.expired"](FIXTURES / "cert_expired")
    assert finding.details["not_valid_after"] < finding.first_seen
