"""Stable IDs for log records (v2.0).

record_id(log, rec) hashes the log name plus the record's content, so the same
record always gets the same ID, on every machine, in every run. The AI cites
these IDs, the event index uses them as event_id, and the dashboard links
evidence back to the raw record with them.
"""

from __future__ import annotations

import hashlib
import json

from maxguard.models import Evidence


def canonical_json(rec: dict) -> str:
    """One fixed text form of a record: sorted keys, no extra spaces."""
    return json.dumps(rec, sort_keys=True, separators=(",", ":"), default=str)


# Fields that change from run to run even for the same capture. Suricata picks
# a random flow_id each run, so it is left out of the hash.
VOLATILE_KEYS = frozenset({"flow_id"})


def record_id(log: str, rec: dict) -> str:
    """16 hex characters identifying one record in one log."""
    stable = {k: v for k, v in rec.items() if k not in VOLATILE_KEYS}
    data = f"{log}\n{canonical_json(stable)}".encode()
    return hashlib.sha256(data).hexdigest()[:16]


def evidence(log: str, rec: dict) -> Evidence:
    """Build the Evidence for a Zeek record or a Suricata eve.json record."""
    # Zeek records have a uid. Suricata records are linked by community_id,
    # which Zeek also logs, so the two tools' records can be joined.
    uid = rec.get("uid") or rec.get("community_id") or ""
    ts = rec.get("ts")
    if ts is None:  # Suricata uses an ISO timestamp string instead of epoch "ts"
        ts = iso_to_epoch(rec["timestamp"])
    return Evidence(log=log, uid=uid, ts=float(ts), record_id=record_id(log, rec))


def iso_to_epoch(value: str) -> float:
    """Convert Suricata's '2026-10-06T01:02:03.456789+0000' to epoch seconds."""
    from datetime import datetime

    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f%z").timestamp()
