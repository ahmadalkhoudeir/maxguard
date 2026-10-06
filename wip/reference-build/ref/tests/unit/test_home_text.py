"""Tests for maxguard/ai/home_text.yaml (Home mode text, written by people)."""

import pytest

import maxguard.rules  # noqa: F401  (importing registers every rule)
from maxguard.ai import load_home_text
from maxguard.rules.base import RULES

FALL_2026_RULE_IDS = {
    "cleartext.ftp", "cleartext.telnet", "cleartext.http", "cleartext.http_alt",
    "cleartext.pop3", "cleartext.imap", "rdp.standard_security",
    "tls.weak_version", "tls.weak_cipher",
    "cert.expired", "cert.self_signed", "cert.weak_key", "cert.sha1_signature",
}
HOME_TEXT = load_home_text()


def test_every_fall_2026_rule_has_home_text():
    assert FALL_2026_RULE_IDS <= set(HOME_TEXT)


def test_no_entry_for_a_rule_that_does_not_exist():
    # Catches typos such as "cert.sha1" instead of "cert.sha1_signature".
    assert set(HOME_TEXT) <= set(RULES)


@pytest.mark.parametrize("rule_id", sorted(HOME_TEXT))
def test_entry_has_exactly_a_headline_and_an_action(rule_id):
    entry = HOME_TEXT[rule_id]
    assert set(entry) == {"headline", "action"}
    for text in entry.values():
        assert isinstance(text, str) and text.strip()
        assert text.endswith(".")  # full sentences
        assert len(text) <= 120  # short enough for a phone screen card
