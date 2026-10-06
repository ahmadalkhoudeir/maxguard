"""Contract 2 loader: applies mappings/*.yaml to findings.

The YAML schema is the Fall 2026 one (framework, version, source, mappings ->
rule_id -> list of {control_id, title, rationale}). v2.0 adds two optional row
keys: `tactic` (used only by the ATT&CK file) and `verified` (where in the
source document the row was checked, e.g. "p. 112").

The file whose framework is "MITRE ATT&CK" fills Finding.attack; every other
file fills Finding.controls.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from maxguard.models import Control, Finding, Technique

ATTACK = "MITRE ATT&CK"
REQUIRED_TOP = ("framework", "version", "source", "mappings")
REQUIRED_ROW = ("control_id", "title", "rationale")


def load_all(mapping_dir: Path) -> list[dict]:
    """Load every mapping file, sorted by file name so the order never changes."""
    return [yaml.safe_load(p.read_text()) for p in sorted(mapping_dir.glob("*.yaml"))]


def validate(fw: dict, known_rule_ids: set[str]) -> list[str]:
    """Return a list of problems in one mapping file (empty list means valid)."""
    problems = [f"missing top-level key {k!r}" for k in REQUIRED_TOP if k not in fw]
    for rule_id, rows in (fw.get("mappings") or {}).items():
        if rule_id not in known_rule_ids:
            problems.append(f"unknown rule_id {rule_id!r}")
        for i, row in enumerate(rows or []):
            for k in REQUIRED_ROW:
                if not str(row.get(k, "")).strip():
                    problems.append(f"{rule_id}[{i}] missing {k!r}")
            if fw.get("framework") == ATTACK and not row.get("tactic"):
                problems.append(f"{rule_id}[{i}] missing 'tactic' (required for ATT&CK)")
    return problems


def apply(findings: list[Finding], frameworks: list[dict], selected: set[str] | None = None):
    """Attach controls (and ATT&CK techniques) to each finding, in place."""
    for fw in frameworks:
        is_attack = fw["framework"] == ATTACK
        if selected and not is_attack and fw["framework"] not in selected:
            continue
        for f in findings:
            for row in fw["mappings"].get(f.rule_id, []):
                if is_attack:
                    f.attack.append(
                        Technique(row["control_id"], row["title"], row["tactic"], fw["version"])
                    )
                else:
                    f.controls.append(
                        Control(fw["framework"], fw["version"], row["control_id"],
                                row["title"], row["rationale"])
                    )
    return findings
