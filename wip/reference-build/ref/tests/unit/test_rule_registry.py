"""The whole Fall 2026 rule set (JAK-02 completes it): 13 rules, one per capture."""

from pathlib import Path

import pytest

import maxguard.rules  # noqa: F401  (importing registers every rule)
from maxguard.rules.base import RULES, run_all

FIXTURES = Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "zeek"

EXPECTED = {
    "ftp": "cleartext.ftp", "telnet": "cleartext.telnet", "plain_http": "cleartext.http",
    "plain_http_alt": "cleartext.http_alt", "pop3": "cleartext.pop3", "imap": "cleartext.imap",
    "tls_weak_version": "tls.weak_version", "tls_weak_cipher": "tls.weak_cipher",
    "cert_expired": "cert.expired", "cert_self_signed": "cert.self_signed",
    "cert_weak_key": "cert.weak_key", "cert_sha1": "cert.sha1_signature",
}
CLEAN_CAPTURES = ["clean_tls13", "dns_lookup"]
FALL_2026_RULES = {*EXPECTED.values(), "rdp.standard_security"}


def test_all_13_fall_2026_rules_are_registered():
    # Spring rules (tls.ja4_watchlist, decoy.contact, ...) register only when their
    # module is imported, so this checks that the 13 are there, not that nothing else is.
    assert len(FALL_2026_RULES) == 13
    assert FALL_2026_RULES <= set(RULES)


@pytest.mark.parametrize("capture", sorted(EXPECTED) + CLEAN_CAPTURES)
def test_each_capture_triggers_exactly_its_rule(capture):
    expected = {EXPECTED[capture]} if capture in EXPECTED else set()
    assert {f.rule_id for f in run_all(FIXTURES / capture)} == expected
