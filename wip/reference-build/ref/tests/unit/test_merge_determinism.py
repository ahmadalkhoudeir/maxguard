"""merge() and determinism tests (Fiona).

merge(): many findings for the same (rule_id, src, dst, port) become one, with
a count and at most MAX_EVIDENCE evidence records (Contract 1).

Determinism (CLAUDE.md rule 2): the same logs must always give the same
findings, finding_ids and evidence record_ids, or AI citations and alert
de-duplication break.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

import maxguard.rules  # noqa: F401  (importing registers every rule)
from maxguard.adapters.zeeklogs import ZeekLogAdapter
from maxguard.models import Evidence, Finding, make_finding_id
from maxguard.rules.base import MAX_EVIDENCE, merge, run_all

REPO = Path(__file__).resolve().parents[2]
FIXTURES = REPO / "tests" / "fixtures" / "zeek"


def telnet_finding(ts: float, record: str, dst_port: int = 23) -> Finding:
    """One finding as a rule would make it: one connection, one evidence record."""
    return Finding(rule_id="cleartext.telnet", title="Telnet session in cleartext",
                   severity="high", src_ip="192.168.56.50", dst_ip="192.168.56.30",
                   dst_port=dst_port, protocol="telnet", first_seen=ts, last_seen=ts,
                   evidence=[Evidence(log="maxguard_cleartext.log", uid=f"C{record}",
                                      ts=ts, record_id=record)])


# ---- merge() ---------------------------------------------------------------

def test_duplicates_collapse_into_one_finding_with_a_count():
    findings = [telnet_finding(200.0, "r1"), telnet_finding(100.0, "r2"),
                telnet_finding(300.0, "r3")]

    merged = merge(findings)

    assert len(merged) == 1
    assert merged[0].count == 3
    assert (merged[0].first_seen, merged[0].last_seen) == (100.0, 300.0)
    assert [ev.record_id for ev in merged[0].evidence] == ["r1", "r2", "r3"]


def test_finding_id_depends_only_on_rule_hosts_and_port():
    a, b = telnet_finding(100.0, "r1"), telnet_finding(999.0, "r2")
    assert a.finding_id == b.finding_id
    assert a.finding_id == make_finding_id("cleartext.telnet", "192.168.56.50",
                                           "192.168.56.30", 23)


def test_a_different_port_is_a_different_finding():
    merged = merge([telnet_finding(100.0, "r1", dst_port=23),
                    telnet_finding(200.0, "r2", dst_port=2323)])

    assert [(f.dst_port, f.count) for f in merged] == [(23, 1), (2323, 1)]
    assert merged[0].finding_id != merged[1].finding_id


def test_evidence_is_capped_at_five_but_count_is_not():
    findings = [telnet_finding(100.0 + i, f"r{i}") for i in range(7)]

    merged = merge(findings)

    assert MAX_EVIDENCE == 5
    assert merged[0].count == 7  # every connection is counted...
    # ...but only the first five records are kept, so reports stay small.
    assert [ev.record_id for ev in merged[0].evidence] == ["r0", "r1", "r2", "r3", "r4"]


def test_merge_keeps_the_order_findings_first_appeared_in():
    other = telnet_finding(50.0, "x1", dst_port=2323)
    merged = merge([telnet_finding(100.0, "r1"), other, telnet_finding(200.0, "r2")])
    assert [f.dst_port for f in merged] == [23, 2323]


# ---- determinism -----------------------------------------------------------

def json_fixture_dirs() -> list[Path]:
    """Every fixture folder of JSON logs: the lab captures and the hand-made ones."""
    folders = [p for p in FIXTURES.iterdir() if p.is_dir() and not p.name.startswith("_")]
    handmade = [p for p in (FIXTURES / "_handmade").iterdir()
                if p.is_dir() and not p.name.startswith("tsv_")]  # TSV needs the adapter first
    return sorted(folders + handmade)


def tsv_fixture_dirs() -> list[Path]:
    return sorted((FIXTURES / "_handmade").glob("tsv_*"))


def findings_as_dicts(log_dir: Path) -> list[dict]:
    return [f.to_dict() for f in run_all(log_dir)]


@pytest.mark.parametrize("log_dir", json_fixture_dirs(), ids=lambda p: p.name)
def test_run_all_twice_gives_identical_findings(log_dir):
    assert findings_as_dicts(log_dir) == findings_as_dicts(log_dir)


@pytest.mark.parametrize("tsv_dir", tsv_fixture_dirs(), ids=lambda p: p.name)
def test_tsv_import_twice_gives_identical_findings(tsv_dir, tmp_path):
    first = ZeekLogAdapter().to_zeek_logs(tsv_dir, tmp_path / "first")
    second = ZeekLogAdapter().to_zeek_logs(tsv_dir, tmp_path / "second")
    assert findings_as_dicts(first) == findings_as_dicts(second)


# Python gives each run a random "hash seed", which changes the order of a set.
# Two runs inside one test share the seed, so a rule that loops over a set
# would still pass the test above. Separate processes with different seeds
# catch that.
PRINT_ALL_FINDINGS = """
import json, sys
from pathlib import Path
import maxguard.rules
from maxguard.rules.base import run_all
out = {d: [f.to_dict() for f in run_all(Path(d))] for d in sys.argv[1:]}
print(json.dumps(out, sort_keys=True))
"""


def findings_in_new_process(hash_seed: str) -> dict:
    env = {**os.environ, "PYTHONHASHSEED": hash_seed}
    folders = [str(p) for p in json_fixture_dirs()]
    result = subprocess.run([sys.executable, "-c", PRINT_ALL_FINDINGS, *folders],
                            cwd=REPO, env=env, capture_output=True, text=True, check=True)
    return json.loads(result.stdout)


def test_findings_do_not_depend_on_the_hash_seed():
    first = findings_in_new_process("1")
    assert any(first.values()), "the fixtures should produce some findings"
    assert first == findings_in_new_process("2")
