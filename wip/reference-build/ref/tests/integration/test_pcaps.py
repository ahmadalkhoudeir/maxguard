"""Integration tests (Karthik, KAR-03): the real pipeline on every lab capture.

Each tests/expected/<capture>.json says which findings its capture must give.
The test runs maxguard.pipeline.analyze() on the capture (real Zeek, plus real
Suricata when it is installed) and compares. Unit tests use saved logs, so
only these tests notice when the way MaxGuard *runs* the tools breaks.

They need Zeek, so they run inside the engine test image:
    docker run --rm --network none maxguard:test pytest -m integration -q
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from maxguard.pipeline import analyze

TESTS = Path(__file__).resolve().parents[1]
PCAPS = TESTS / "pcaps"
EXPECTED_FILES = sorted((TESTS / "expected").glob("*.json"))


def load(expected_file: Path) -> dict:
    return json.loads(expected_file.read_text())


def count_by_rule_and_port(findings: list[dict]) -> dict[tuple[str, int], int]:
    """(rule_id, dst_port) -> total count. Adds up counts in case several findings
    (for example from different client addresses) share a rule and a port."""
    counts: dict[tuple[str, int], int] = {}
    for finding in findings:
        key = (finding["rule_id"], finding["dst_port"])
        counts[key] = counts.get(key, 0) + finding["count"]
    return counts


@pytest.mark.integration
def test_every_capture_has_an_expected_file():
    # A capture without an expected file would never be tested.
    captures = sorted(p.name for p in PCAPS.glob("*.pcap"))
    assert captures == sorted(load(f)["capture"] for f in EXPECTED_FILES)


@pytest.mark.integration
@pytest.mark.parametrize("expected_file", EXPECTED_FILES, ids=lambda p: p.stem)
def test_capture_gives_the_expected_findings(expected_file, tmp_path):
    spec = load(expected_file)
    report = analyze(PCAPS / spec["capture"], tmp_path, explain=False)

    assert report["tools"]["zeek"] is True  # a capture always goes through Zeek
    counts = count_by_rule_and_port(report["findings"])
    for want in spec["expected"]:
        got = counts.get((want["rule_id"], want["dst_port"]), 0)
        assert got >= want["min_count"], f"missing {want}; found {counts}"
    found_rules = {rule_id for rule_id, _port in counts}
    for rule_id in spec.get("must_not_contain", []):
        assert rule_id not in found_rules, f"{rule_id} fired on {spec['capture']}"
    if spec.get("expect_no_findings", False):
        assert report["findings"] == []


# The sandbox image used in planning had no Suricata, so this check is its own
# test: there it shows as "skipped" with the reason below. The engine image has
# Suricata, so in CI it runs (and CI's "suricata -V" step fails if it is missing).
@pytest.mark.integration
@pytest.mark.skipif(shutil.which("suricata") is None,
                    reason="suricata is not installed here; the engine image has it")
def test_zeek_and_suricata_both_ran(tmp_path):
    report = analyze(PCAPS / "tls_weak_version.pcap", tmp_path, explain=False)

    assert report["tools"] == {"zeek": True, "suricata": True}
    # Suricata ran with MaxGuard's settings: its TLS event carries a JA4, and the
    # same Community ID as Zeek's event for that connection, so the two can be joined.
    [suricata_tls] = [e for e in report["events"]
                      if e["source"] == "suricata" and e["kind"] == "tls"]
    [zeek_tls] = [e for e in report["events"] if e["source"] == "zeek" and e["kind"] == "tls"]
    assert suricata_tls["ja4"] != ""
    assert zeek_tls["community_id"] != ""
    assert suricata_tls["community_id"] == zeek_tls["community_id"]
