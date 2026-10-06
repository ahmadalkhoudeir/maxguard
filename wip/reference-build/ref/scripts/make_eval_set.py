"""Build the AI evaluation set from the Zeek fixture logs (Ali).

One eval item = one finding, exactly as the pipeline hands it to the AI (rules
run, mapping files applied), plus the raw log records it cites, keyed by
record_id. scripts/benchmark_models.py asks every model about the same items,
so the models are compared on the same questions.

The output is deterministic: the same fixtures always give a byte-identical
eval_set.json. Run this again whenever a rule, a mapping file or a fixture
changes, and commit the new file (tests/unit/test_benchmark.py fails until you do).

Run from the repository root:
    python -m scripts.make_eval_set
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import maxguard.rules  # noqa: F401  (importing registers every rule)
from maxguard.events.lookup import records_for
from maxguard.mapping.loader import apply, load_all
from maxguard.models import Finding
from maxguard.rules.base import run_all

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURES_DIR = REPO_ROOT / "tests" / "fixtures" / "zeek"
MAPPINGS_DIR = REPO_ROOT / "mappings"
EVAL_SET_PATH = REPO_ROOT / "tests" / "fixtures" / "ai_eval" / "eval_set.json"
SCHEMA = "maxguard.eval_set/1"

# clean_tls13 is the "nothing wrong" capture: it has no finding to explain.
SKIPPED_FIXTURES = {"clean_tls13"}
# No lab capture contains RDP. This hand-made fixture is real Zeek 9.0.0 output
# (see its README), so adding it gives one item for every Fall 2026 rule.
EXTRA_FIXTURES = ["_handmade/rdp"]


def fixture_names(fixtures_dir: Path = FIXTURES_DIR) -> list[str]:
    """The lab capture folders (sorted, so the order never changes), then the extras.

    Folders starting with "_" hold hand-made extras; some are in Zeek's TSV
    format, which the rules cannot read directly, so only EXTRA_FIXTURES are used.
    """
    names = sorted(
        p.name
        for p in fixtures_dir.iterdir()
        if p.is_dir() and not p.name.startswith("_") and p.name not in SKIPPED_FIXTURES
    )
    return names + [name for name in EXTRA_FIXTURES if (fixtures_dir / name).is_dir()]


def findings_for(log_dir: Path, frameworks: list[dict]) -> list[Finding]:
    """Rules plus mappings, the same two steps maxguard.pipeline.analyze() does."""
    findings = run_all(log_dir)
    apply(findings, frameworks)
    return sorted(findings, key=lambda f: f.finding_id)  # a fixed order


def eval_item(fixture: str, finding: Finding, log_dir: Path) -> dict:
    """One finding plus its evidence records, in the shape explain() takes."""
    record_ids = {e.record_id for e in finding.evidence}
    # records_for() is what production uses: it re-hashes every record with
    # maxguard.ids.record_id and keeps the ones the finding cites.
    records = records_for(log_dir, record_ids)
    missing = record_ids - set(records)
    if missing:
        # The model would be asked about evidence it cannot see: stop loudly.
        raise ValueError(f"{fixture}: evidence records not found: {sorted(missing)}")
    return {
        "item_id": f"{fixture}/{finding.finding_id}",
        "fixture": fixture,
        "finding": finding.to_dict(),
        "records": records,
    }


def build_eval_set(fixtures_dir: Path = FIXTURES_DIR,
                   mappings_dir: Path = MAPPINGS_DIR) -> dict:
    """Every finding of every fixture, as eval items. Reads no clock: no "created at"."""
    frameworks = load_all(mappings_dir) if mappings_dir.is_dir() else []
    items = []
    for fixture in fixture_names(fixtures_dir):
        log_dir = fixtures_dir / fixture
        for finding in findings_for(log_dir, frameworks):
            items.append(eval_item(fixture, finding, log_dir))
    return {"schema": SCHEMA, "items": items}


def to_json(eval_set: dict) -> str:
    """Sorted keys and fixed indentation, so the file only changes when the data does."""
    return json.dumps(eval_set, indent=1, sort_keys=True) + "\n"


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Build the AI evaluation set.")
    parser.add_argument("--out", type=Path, default=EVAL_SET_PATH, help="where to write it")
    args = parser.parse_args(argv)

    eval_set = build_eval_set()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(to_json(eval_set))
    rule_ids = sorted({item["finding"]["rule_id"] for item in eval_set["items"]})
    print(f"wrote {len(eval_set['items'])} items ({len(rule_ids)} rules) to {args.out}")


if __name__ == "__main__":
    main()
