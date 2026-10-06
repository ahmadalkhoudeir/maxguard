"""Find the raw log records behind evidence record_ids (v2.0).

A finding only stores record_ids (see maxguard.ids). When the AI explains a
finding it must see the actual records, so this module scans the log folder,
recomputes each record's ID and keeps the ones that were asked for.
"""

from __future__ import annotations

from pathlib import Path

from maxguard.adapters.base import read_log
from maxguard.ids import record_id


def log_names(log_dir: Path) -> list[str]:
    """Every Zeek *.log plus Suricata's eve.json, in a fixed (sorted) order."""
    names = sorted(p.name for p in log_dir.glob("*.log"))
    if (log_dir / "eve.json").exists():
        names.append("eve.json")
    return names


def records_for(log_dir: Path, record_ids: set[str]) -> dict[str, dict]:
    """Map each requested record_id to its raw record, with a "_log" key added
    (e.g. "ssl.log") so the reader knows where it came from. IDs that are not
    found are simply missing from the result."""
    log_dir = Path(log_dir)
    wanted = set(record_ids)
    found: dict[str, dict] = {}
    for log_name in log_names(log_dir):
        if len(found) == len(wanted):
            break  # everything found: no need to read the remaining logs
        for rec in read_log(log_dir, log_name):
            rid = record_id(log_name, rec)  # hash the record before adding "_log"
            if rid in wanted:
                found[rid] = {**rec, "_log": log_name}
    return found
