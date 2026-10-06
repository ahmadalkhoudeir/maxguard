"""Rule registry (Fall 2026 roadmap, unchanged behavior).

A rule is a function that takes a folder of logs and returns Finding objects.
Rules never read the clock, the network, or random numbers, so the same logs
always produce the same findings (CLAUDE.md rule 2).
"""

from collections.abc import Callable
from pathlib import Path

from maxguard.models import Finding

RULES: dict[str, Callable[[Path], list[Finding]]] = {}
MAX_EVIDENCE = 5


def rule(rule_id: str):
    def wrap(fn):
        if rule_id in RULES:
            raise ValueError(f"duplicate rule_id {rule_id!r}")
        RULES[rule_id] = fn
        return fn

    return wrap


def merge(findings: list[Finding]) -> list[Finding]:
    """Collapse duplicates per Contract 1: one Finding per (rule_id, src, dst, port).

    The first Finding for each key is kept and updated in place; at most
    MAX_EVIDENCE evidence records are kept, in the order the logs listed them.
    """
    out: dict[tuple, Finding] = {}
    for f in findings:
        key = (f.rule_id, f.src_ip, f.dst_ip, f.dst_port)
        if key in out:
            g = out[key]
            g.count += f.count
            g.first_seen = min(g.first_seen, f.first_seen)
            g.last_seen = max(g.last_seen, f.last_seen)
            room = max(0, MAX_EVIDENCE - len(g.evidence))
            g.evidence.extend(f.evidence[:room])
        else:
            del f.evidence[MAX_EVIDENCE:]
            out[key] = f
    return list(out.values())


def run_all(log_dir: Path) -> list[Finding]:
    """Run every registered rule in rule_id order and merge the results."""
    found: list[Finding] = []
    for rule_id in sorted(RULES):
        found.extend(RULES[rule_id](log_dir))
    return merge(found)
