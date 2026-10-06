"""How often each model obeyed the prompt-injection items (Jonattan and Ali, JON-06).

Reads the benchmark's CSV (scripts/benchmark_models.py), keeps the rows of the
injection items (item_id starting with "injection/"), and checks each kept
answer for that item's canary (scripts/make_injection_set.py). Only run 1 is
counted, so repeating a run does not double the numbers.

The citation check cannot catch every obeying answer: a sentence that cites
the hostile record itself has a valid citation and is kept. This rate is what
reached the reader.

Run from the repository root after benchmarking the injection set:
    python -m scripts.injection_report docs/model-eval/raw_results.csv
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from scripts.make_injection_set import INJECTION_SET_PATH, obeyed

PREFIX = "injection/"


def canaries(path: Path = INJECTION_SET_PATH) -> dict[str, str]:
    """item_id -> canary word."""
    return {item["item_id"]: item["canary"] for item in json.loads(path.read_text())["items"]}


def injection_rates(rows: list[dict], canary_by_item: dict[str, str]) -> list[dict]:
    """One summary per (tier, model): answers checked, answers that obeyed, the share."""
    groups: dict[tuple[str, str], list[dict]] = {}
    for row in rows:
        if row["item_id"].startswith(PREFIX) and row["run"] == "1" and not row["error"]:
            groups.setdefault((row["tier"], row["model"]), []).append(row)
    summaries = []
    for (tier, model), answers in sorted(groups.items()):
        count = sum(obeyed(row["text"], canary_by_item[row["item_id"]]) for row in answers)
        summaries.append({"tier": tier, "model": model, "answers": len(answers),
                          "obeyed": count, "rate": count / len(answers)})
    return summaries


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Prompt-injection rate per model.")
    parser.add_argument("results", type=Path, help="the benchmark's raw_results.csv")
    parser.add_argument("--injection-set", type=Path, default=INJECTION_SET_PATH)
    args = parser.parse_args(argv)

    with args.results.open(newline="") as f:
        rows = list(csv.DictReader(f))
    summaries = injection_rates(rows, canaries(args.injection_set))
    if not summaries:
        print("no injection rows: benchmark --eval-set "
              "tests/fixtures/ai_eval/injection/injection_set.json first")
        return
    print(f"{'tier':<8}{'model':<24}{'answers':>8}{'obeyed':>8}{'rate':>8}")
    for s in summaries:
        print(f"{s['tier']:<8}{s['model']:<24}{s['answers']:>8}{s['obeyed']:>8}{s['rate']:>8.0%}")


if __name__ == "__main__":
    main()
