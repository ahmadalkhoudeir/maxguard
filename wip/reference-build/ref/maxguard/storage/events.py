"""EventStore: normalized events in hourly Parquet files, queried with DuckDB (v2.0).

Layout (UTC):  root/date=2026-10-06/hour=01/part-<sha>.parquet

- One folder per hour, so retention is "delete old folders" (prune) and a
  7-day window is a fixed number of folders.
- <sha> is a hash of the batch's event_ids: writing the same events again
  (the same capture uploaded twice) replaces the same file instead of adding
  a copy.
- The store never reads the clock: the caller says what "older than" means.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
from datetime import UTC, datetime
from pathlib import Path

import duckdb

# Column name -> DuckDB type. Same names and order as maxguard.events.normalize.EVENT_KEYS.
COLUMNS = {
    "event_id": "VARCHAR", "ts": "DOUBLE", "sensor_id": "VARCHAR", "source": "VARCHAR",
    "log": "VARCHAR", "kind": "VARCHAR", "uid": "VARCHAR", "community_id": "VARCHAR",
    "src_ip": "VARCHAR", "dst_ip": "VARCHAR", "src_port": "INTEGER", "dst_port": "INTEGER",
    "proto": "VARCHAR", "service": "VARCHAR", "bytes_out": "BIGINT", "bytes_in": "BIGINT",
    "device_mac": "VARCHAR", "summary": "VARCHAR", "ja4": "VARCHAR",
}
SECONDS_PER_HOUR = 3600
# DuckDB downloads and loads extensions on its own when a query needs one (both
# settings default to true). Parquet and JSON support are built in, so MaxGuard
# never needs a download: switch it off so nothing can go online (CLAUDE.md rule 1).
DUCKDB_CONFIG = {"autoinstall_known_extensions": False, "autoload_known_extensions": False}


def hour_key(ts: float) -> tuple[str, str]:
    """("2026-10-06", "01") for the UTC hour that contains ts."""
    moment = datetime.fromtimestamp(ts, tz=UTC)
    return moment.strftime("%Y-%m-%d"), moment.strftime("%H")


def hour_start(hour_dir: Path) -> float:
    """Epoch seconds at the start of a root/date=YYYY-MM-DD/hour=HH folder."""
    date = hour_dir.parent.name.removeprefix("date=")
    hour = int(hour_dir.name.removeprefix("hour="))
    moment = datetime.strptime(date, "%Y-%m-%d").replace(hour=hour, tzinfo=UTC)
    return moment.timestamp()


def batch_name(events: list[dict]) -> str:
    """part-<sha>.parquet, where sha depends only on which events are in the batch."""
    ids = "\n".join(sorted(e["event_id"] for e in events))
    return f"part-{hashlib.sha256(ids.encode()).hexdigest()[:16]}.parquet"


def group_by_hour(events: list[dict]) -> dict[tuple[str, str], list[dict]]:
    groups: dict[tuple[str, str], list[dict]] = {}
    for event in events:
        groups.setdefault(hour_key(event["ts"]), []).append(event)
    return groups


class EventStore:
    def __init__(self, root: Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def write(self, events: list[dict]) -> int:
        """Store events in their hour folders. Returns how many were written."""
        for (date, hour), group in sorted(group_by_hour(events).items()):
            folder = self.root / f"date={date}" / f"hour={hour}"
            folder.mkdir(parents=True, exist_ok=True)
            self._write_parquet(group, folder / batch_name(group))
        return len(events)

    def _write_parquet(self, events: list[dict], target: Path) -> None:
        # DuckDB inserts Python rows one by one slowly (about 1 ms per row, measured),
        # but loads a JSON-lines file hundreds of times faster. So: write the events
        # as JSON lines, let DuckDB convert that file to Parquet, then delete it.
        staging = target.with_suffix(".jsonl")
        partial = target.with_suffix(".partial")
        try:
            with staging.open("w", encoding="utf-8") as f:
                for event in events:
                    f.write(json.dumps({name: event[name] for name in COLUMNS}) + "\n")
            with duckdb.connect(config=DUCKDB_CONFIG) as con:
                con.execute(
                    "COPY (SELECT * FROM read_json($src, format = 'newline_delimited', "
                    "columns = $columns)) TO $dst (FORMAT parquet, COMPRESSION zstd)",
                    {"src": str(staging), "columns": COLUMNS, "dst": str(partial)},
                )
            # Readers only look at *.parquet, so they never see a half-written file.
            os.replace(partial, target)
        finally:
            staging.unlink(missing_ok=True)
            partial.unlink(missing_ok=True)

    def query(self, *, ip: str | None = None, since: float | None = None,
              until: float | None = None, limit: int = 1000) -> list[dict]:
        """Events in time order. ip matches src_ip or dst_ip; since <= ts < until."""
        if not any(self.root.glob("date=*/hour=*/*.parquet")):
            return []  # read_parquet fails on a pattern that matches no files
        where, params = [], {"files": str(self.root / "date=*" / "hour=*" / "*.parquet")}
        if ip is not None:
            where.append("(src_ip = $ip OR dst_ip = $ip)")
            params["ip"] = ip
        if since is not None:
            where.append("ts >= $since")
            params["since"] = since
        if until is not None:
            where.append("ts < $until")
            params["until"] = until
        # The column names come from COLUMNS (our constant), never from the caller;
        # every caller value goes in as a $parameter. hive_partitioning also turns the
        # folder names into "date" and "hour" columns (handy in the DuckDB shell);
        # we select only the event columns, so the result matches EVENT_KEYS.
        sql = (f"SELECT {', '.join(COLUMNS)} "
               "FROM read_parquet($files, hive_partitioning = true)")
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " ORDER BY ts, event_id LIMIT $limit"
        params["limit"] = limit
        with duckdb.connect(config=DUCKDB_CONFIG) as con:
            rows = con.execute(sql, params).fetchall()
        return [dict(zip(COLUMNS, row, strict=True)) for row in rows]

    def prune(self, *, older_than: float) -> int:
        """Delete every hour folder whose whole hour ended at or before older_than.
        Returns how many hour folders were deleted."""
        removed = 0
        for hour_dir in sorted(self.root.glob("date=*/hour=*")):
            if hour_start(hour_dir) + SECONDS_PER_HOUR <= older_than:
                shutil.rmtree(hour_dir)
                removed += 1
        for date_dir in self.root.glob("date=*"):
            if not any(date_dir.iterdir()):
                date_dir.rmdir()  # keep the tree tidy: no empty date folders
        return removed
