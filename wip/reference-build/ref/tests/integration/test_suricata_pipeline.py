"""Suricata runs next to Zeek in the pipeline (Jakub, JAK-05).

Once JAK-05 is merged, analyze() runs Suricata on every capture whenever Suricata
is installed. The engine image has it, so CI runs this test. Where Suricata is
missing (a laptop, or the Zeek-only image used in planning) the test shows as
"skipped" with the reason, never silently passed, and CI's "suricata -V" step
fails if the engine image ever loses Suricata.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from maxguard.pipeline import analyze

PCAPS = Path(__file__).resolve().parents[1] / "pcaps"


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
