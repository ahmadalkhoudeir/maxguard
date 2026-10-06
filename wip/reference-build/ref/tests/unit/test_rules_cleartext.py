"""Cleartext and RDP rule tests (Jakub, JAK-02): positive and negative for each rule.

RDP has no lab capture: tests/fixtures/zeek/_handmade/rdp/ has a synthetic
capture and its real Zeek output (one "RDP" and one "HYBRID" connection).
"""

import json
import re
from pathlib import Path

import pytest

import maxguard.rules  # noqa: F401  (importing registers every rule)
from maxguard.adapters.base import read_log
from maxguard.ids import record_id
from maxguard.rules.base import RULES, run_all

REPO = Path(__file__).resolve().parents[2]
FIXTURES = REPO / "tests" / "fixtures" / "zeek"
RDP_DIR = FIXTURES / "_handmade" / "rdp"

EXPECTED = {
    "ftp": "cleartext.ftp",
    "telnet": "cleartext.telnet",
    "plain_http": "cleartext.http",
    "plain_http_alt": "cleartext.http_alt",
    "pop3": "cleartext.pop3",
    "imap": "cleartext.imap",
}

NEAR_MISS = {
    "cleartext.ftp": "plain_http",  # cleartext, but not FTP
    "cleartext.telnet": "pop3",  # same maxguard_cleartext.log, other protocol
    "cleartext.pop3": "imap",
    "cleartext.imap": "telnet",
    "cleartext.http": "plain_http_alt",  # HTTP, but on port 8080
    "cleartext.http_alt": "plain_http",  # HTTP, but on port 80
}

CLEARTEXT_RULES = {*EXPECTED.values(), "rdp.standard_security"}


def write_log(log_dir: Path, log_name: str, records: list[dict]) -> Path:
    """Write records as a Zeek JSON log (one object per line) and return the folder."""
    (log_dir / log_name).write_text("".join(json.dumps(rec) + "\n" for rec in records))
    return log_dir


def rdp_record(security_protocol: str) -> dict:
    """The rdp.log record from the hand-made capture with this security_protocol."""
    for rec in read_log(RDP_DIR, "rdp.log"):
        if rec["security_protocol"] == security_protocol:
            return rec
    raise AssertionError(f"no {security_protocol} record in {RDP_DIR / 'rdp.log'}")


def test_the_seven_cleartext_and_rdp_rules_are_registered():
    assert CLEARTEXT_RULES <= set(RULES)


@pytest.mark.parametrize(("capture", "rule_id"), sorted(EXPECTED.items()))
def test_rule_fires_on_its_capture(capture, rule_id):
    findings = RULES[rule_id](FIXTURES / capture)

    assert len(findings) >= 1
    for finding in findings:
        assert finding.rule_id == rule_id
        assert finding.evidence, "every finding needs evidence the AI can cite"


@pytest.mark.parametrize(("capture", "rule_id"), sorted(EXPECTED.items()))
def test_evidence_points_at_real_log_records(capture, rule_id):
    log_dir = FIXTURES / capture
    for finding in RULES[rule_id](log_dir):
        for ev in finding.evidence:
            ids_in_log = {record_id(ev.log, rec) for rec in read_log(log_dir, ev.log)}
            assert ev.record_id in ids_in_log


@pytest.mark.parametrize(("rule_id", "capture"), sorted(NEAR_MISS.items()))
def test_rule_is_silent_on_near_miss(rule_id, capture):
    assert RULES[rule_id](FIXTURES / capture) == []


@pytest.mark.parametrize("rule_id", sorted(CLEARTEXT_RULES))
def test_rule_is_silent_on_clean_tls13(rule_id):
    assert RULES[rule_id](FIXTURES / "clean_tls13") == []


def test_ftp_password_is_never_in_the_finding():
    # Zeek writes "<hidden>" instead of the FTP password; the finding keeps only
    # the user name and command, so a report never shows a password.
    [finding] = RULES["cleartext.ftp"](FIXTURES / "ftp")
    assert "password" not in finding.details


def test_rdp_standard_security_fires_for_security_protocol_rdp(tmp_path):
    log_dir = write_log(tmp_path, "rdp.log", [rdp_record("RDP")])

    [finding] = RULES["rdp.standard_security"](log_dir)

    assert (finding.dst_ip, finding.dst_port) == ("192.168.56.30", 3389)
    assert finding.details == {"security_protocol": "RDP"}
    assert [ev.log for ev in finding.evidence] == ["rdp.log"]


def test_rdp_standard_security_is_silent_for_hybrid(tmp_path):
    # HYBRID = CredSSP / Network Level Authentication: the secure choice.
    log_dir = write_log(tmp_path, "rdp.log", [rdp_record("HYBRID")])
    assert RULES["rdp.standard_security"](log_dir) == []


def test_rdp_fixture_folder_flags_only_the_old_server():
    found = [(f.rule_id, f.dst_ip) for f in run_all(RDP_DIR)]
    assert found == [("rdp.standard_security", "192.168.56.30")]


# Telnet, POP3 and IMAP have no Zeek log of their own, so cleartext.zeek writes
# maxguard_cleartext.log and the rules trust every line of it. The script, not
# the Python rule, decides what counts as cleartext (ports 23/110/143, the server
# sent data, and no TLS was seen). Zeek's service set holds upper-case names such
# as "SSL", so the script compares lower-case; tests/integration checks it with Zeek.

def cleartext_script_protocols() -> set[str]:
    """Protocol names in cleartext.zeek's port table, e.g. [23/tcp] = "telnet"."""
    script = (REPO / "maxguard" / "zeek" / "scripts" / "cleartext.zeek").read_text()
    return set(re.findall(r'\[\d+/tcp\]\s*=\s*"(\w+)"', script))


def test_script_and_rules_use_the_same_protocol_names():
    # If the script wrote "pop" instead of "pop3", cleartext.pop3 would silently
    # never fire. Each rule filters maxguard_cleartext.log on one of these names.
    assert cleartext_script_protocols() == {"telnet", "pop3", "imap"}
    for proto in ("telnet", "pop3", "imap"):
        assert f"cleartext.{proto}" in RULES


def test_script_ignores_case_when_checking_for_tls():
    script = (REPO / "maxguard" / "zeek" / "scripts" / "cleartext.zeek").read_text()
    assert "to_lower(svc)" in script
