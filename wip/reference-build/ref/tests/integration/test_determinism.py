"""Determinism test (Karthik, KAR-04): the same capture always gives the same report.

CLAUDE.md rule 2 with the real tools: analyze() runs twice on every capture, in
two different temporary folders, and the two report dicts must be equal. The
folders differ on purpose, so a folder path that leaks into the report fails too.
Zeek's -D option and record IDs that ignore Suricata's random flow_id are what
make this pass (docs/ARCHITECTURE.md section 7).

The determinism test needs Zeek, so it runs inside the engine test image
(pytest -m integration). The small test of the differences() helper needs
nothing, so it is not marked and also runs with the unit tests.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from maxguard.pipeline import analyze

PCAPS = sorted((Path(__file__).resolve().parents[1] / "pcaps").glob("*.pcap"))


def differences(first: object, second: object, where: str = "report") -> list[str]:
    """Every place where two reports differ, for example
    report['events'][3]['uid']: 'CAbc' != 'CXyz'. An empty list means identical."""
    if isinstance(first, dict) and isinstance(second, dict):
        found = []
        for key in sorted(set(first) | set(second)):
            found += differences(first.get(key), second.get(key), f"{where}[{key!r}]")
        return found
    if isinstance(first, list) and isinstance(second, list) and len(first) == len(second):
        found = []
        for index, (a, b) in enumerate(zip(first, second, strict=True)):
            found += differences(a, b, f"{where}[{index}]")
        return found
    return [] if first == second else [f"{where}: {first!r} != {second!r}"]


@pytest.mark.integration
@pytest.mark.parametrize("pcap", PCAPS, ids=lambda p: p.stem)
def test_two_runs_give_the_same_report(pcap, tmp_path):
    first = analyze(pcap, tmp_path / "first", explain=False)
    second = analyze(pcap, tmp_path / "second", explain=False)

    # Show at most 10 differences: the first one usually names the culprit.
    assert first == second, "\n".join(differences(first, second)[:10])


def test_differences_names_the_value_that_changed():
    # A plain unit test of the helper above, so its messages can be trusted.
    first = {"events": [{"uid": "CAbc", "ts": 1.0}], "tools": {"zeek": True}}
    second = {"events": [{"uid": "CXyz", "ts": 1.0}], "tools": {"zeek": True}}
    assert differences(first, first) == []
    assert differences(first, second) == ["report['events'][0]['uid']: 'CAbc' != 'CXyz'"]
    assert differences({"a": [1]}, {"a": [1, 2]}) == ["report['a']: [1] != [1, 2]"]
