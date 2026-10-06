"""StateStore: analyses, alerts and the audit trail in one SQLite file (v2.0).

- WAL mode: the dashboard can keep reading while an upload is being saved.
- An alert is a finding plus what people did with it (status, assignee).
  Alerts are keyed by finding_id, so a new capture that shows the same problem
  updates the existing alert (count, first/last seen) instead of adding a copy.
- Uploading the very same file again (same SHA-256) refreshes the alert's
  details but does not add to its count: the traffic was already counted.
- A "resolved" alert that comes back with newer evidence (last_seen moves
  forward) is reopened as "new", and the reopen is written to the audit table:
  a problem that was fixed and returned must be seen again. "false_positive"
  and "investigating" are never changed by an upload.
- The store never reads the clock: every time is passed in by the caller.
  That keeps tests exact and leaves "what time is it" to the API.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from maxguard.ids import canonical_json
from maxguard.models import SEVERITIES

ALERT_STATUSES = ("new", "investigating", "resolved", "false_positive")

SCHEMA = """
CREATE TABLE IF NOT EXISTS analyses (
    analysis_id   TEXT PRIMARY KEY,
    received_at   REAL NOT NULL,
    input_name    TEXT NOT NULL,
    input_sha256  TEXT NOT NULL,
    finding_count INTEGER NOT NULL,
    report_json   TEXT NOT NULL      -- the report minus "events" (those go to the EventStore)
);
CREATE TABLE IF NOT EXISTS alerts (
    finding_id        TEXT PRIMARY KEY,
    rule_id           TEXT NOT NULL,
    severity          TEXT NOT NULL,
    severity_rank     INTEGER NOT NULL,  -- position in SEVERITIES: 0 = critical
    first_seen        REAL NOT NULL,
    last_seen         REAL NOT NULL,
    count             INTEGER NOT NULL,
    status            TEXT NOT NULL DEFAULT 'new',
    assignee          TEXT NOT NULL DEFAULT '',
    analysis_id       TEXT NOT NULL,     -- the latest analysis that reported it
    first_received_at REAL NOT NULL,
    last_received_at  REAL NOT NULL,
    finding_json      TEXT NOT NULL      -- Finding.to_dict() from that latest analysis
);
CREATE TABLE IF NOT EXISTS audit (
    audit_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    at           REAL NOT NULL,
    actor        TEXT NOT NULL,
    action       TEXT NOT NULL,
    target       TEXT NOT NULL,
    details_json TEXT NOT NULL
);
"""

# status, assignee and first_received_at are not in the UPDATE part, so a
# re-upload keeps them (reopening is done separately, see reopen_if_back()).
# min()/max() widen the time range the alert covers. :repeat is 1 when this
# exact file was analysed before, so its findings are not counted twice.
UPSERT_ALERT = """
INSERT INTO alerts (finding_id, rule_id, severity, severity_rank, first_seen, last_seen,
                    count, analysis_id, first_received_at, last_received_at, finding_json)
VALUES (:finding_id, :rule_id, :severity, :severity_rank, :first_seen, :last_seen,
        :count, :analysis_id, :received_at, :received_at, :finding_json)
ON CONFLICT (finding_id) DO UPDATE SET
    count            = alerts.count + (CASE WHEN :repeat THEN 0 ELSE excluded.count END),
    first_seen       = min(alerts.first_seen, excluded.first_seen),
    last_seen        = max(alerts.last_seen, excluded.last_seen),
    severity         = excluded.severity,
    severity_rank    = excluded.severity_rank,
    analysis_id      = excluded.analysis_id,
    last_received_at = excluded.last_received_at,
    finding_json     = excluded.finding_json
"""

# Columns that override the values inside finding_json when an alert is read.
ALERT_COLUMNS = ("severity", "first_seen", "last_seen", "count", "status", "assignee",
                 "analysis_id", "first_received_at", "last_received_at")


def make_analysis_id(report: dict, received_at: float) -> str:
    """Same report received at the same moment -> same ID (so a retry is not saved twice)."""
    data = f"{received_at!r}\n{canonical_json(report)}".encode()
    return hashlib.sha256(data).hexdigest()[:16]


def alert_params(finding: dict, analysis_id: str, received_at: float,
                 repeat: bool = False) -> dict:
    """The named values UPSERT_ALERT needs for one finding dict."""
    return {
        "repeat": int(repeat),
        "finding_id": finding["finding_id"],
        "rule_id": finding["rule_id"],
        "severity": finding["severity"],
        "severity_rank": SEVERITIES.index(finding["severity"]),
        "first_seen": finding["first_seen"],
        "last_seen": finding["last_seen"],
        "count": finding["count"],
        "analysis_id": analysis_id,
        "received_at": received_at,
        "finding_json": json.dumps(finding, sort_keys=True),
    }


def row_to_alert(row: sqlite3.Row) -> dict:
    """The stored finding, with the merged/updated values from the columns on top."""
    alert = json.loads(row["finding_json"])
    for column in ALERT_COLUMNS:
        alert[column] = row[column]
    return alert


def check_status(status: str) -> None:
    if status not in ALERT_STATUSES:
        raise ValueError(f"status must be one of {ALERT_STATUSES}, got {status!r}")


def check_severity(severity: str) -> None:
    if severity not in SEVERITIES:
        raise ValueError(f"severity must be one of {SEVERITIES}, got {severity!r}")


def insert_audit(conn: sqlite3.Connection, *, actor: str, action: str, target: str,
                 details: dict, at: float) -> int:
    cur = conn.execute(
        "INSERT INTO audit (at, actor, action, target, details_json) VALUES (?, ?, ?, ?, ?)",
        (at, actor, action, target, json.dumps(details, sort_keys=True)),
    )
    return cur.lastrowid


def reopen_if_back(conn: sqlite3.Connection, finding: dict, analysis_id: str,
                   received_at: float) -> None:
    """Reopen a resolved alert when this finding brings newer evidence, and audit it."""
    row = conn.execute("SELECT status, last_seen FROM alerts WHERE finding_id = ?",
                       (finding["finding_id"],)).fetchone()
    if row is None or row["status"] != "resolved" or finding["last_seen"] <= row["last_seen"]:
        return
    conn.execute("UPDATE alerts SET status = 'new' WHERE finding_id = ?",
                 (finding["finding_id"],))
    insert_audit(conn, actor="maxguard", action="alert.reopen", target=finding["finding_id"],
                 details={"status": {"from": "resolved", "to": "new"},
                          "analysis_id": analysis_id, "last_seen": finding["last_seen"]},
                 at=received_at)


class StateStore:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            # WAL is stored in the database file, so setting it once is enough.
            conn.execute("PRAGMA journal_mode=WAL")
            conn.executescript(SCHEMA)

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        """A fresh connection per call: the API serves requests from several threads,
        and one sqlite3 connection must not be shared between threads."""
        conn = sqlite3.connect(self.path, timeout=5.0)  # wait up to 5 s for a lock
        conn.row_factory = sqlite3.Row
        try:
            with conn:  # commit if the block succeeds, roll back if it raises
                yield conn
        finally:
            conn.close()

    # ---------- analyses ----------

    def save_analysis(self, report: dict, *, received_at: float) -> str:
        """Store one pipeline report and merge its findings into the alerts."""
        analysis_id = make_analysis_id(report, received_at)
        stored = {key: value for key, value in report.items() if key != "events"}
        sha = report["input"]["sha256"]  # "" for a folder of logs (no single file to hash)
        with self._connect() as conn:
            repeat = bool(sha) and conn.execute(
                "SELECT 1 FROM analyses WHERE input_sha256 = ?", (sha,)).fetchone() is not None
            cur = conn.execute(
                "INSERT OR IGNORE INTO analyses VALUES (?, ?, ?, ?, ?, ?)",
                (analysis_id, received_at, report["input"]["name"], sha,
                 len(report["findings"]), json.dumps(stored, sort_keys=True)),
            )
            if cur.rowcount == 0:
                return analysis_id  # saved before: do not count its findings twice
            for finding in report["findings"]:
                reopen_if_back(conn, finding, analysis_id, received_at)
                conn.execute(UPSERT_ALERT,
                             alert_params(finding, analysis_id, received_at, repeat))
        return analysis_id

    def get_analysis(self, analysis_id: str) -> dict | None:
        """The stored report (without "events"), or None."""
        with self._connect() as conn:
            row = conn.execute("SELECT report_json FROM analyses WHERE analysis_id = ?",
                               (analysis_id,)).fetchone()
        return json.loads(row["report_json"]) if row else None

    def list_analyses(self, limit: int = 50) -> list[dict]:
        """Newest first: analysis_id, received_at, input_name, input_sha256, finding_count."""
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT analysis_id, received_at, input_name, input_sha256, finding_count "
                "FROM analyses ORDER BY received_at DESC, analysis_id LIMIT ?", (limit,),
            ).fetchall()
        return [dict(row) for row in rows]

    # ---------- alerts ----------

    def list_alerts(self, *, status: str | None = None, severity: str | None = None,
                    limit: int = 200) -> list[dict]:
        """Most severe first, then most recently seen."""
        where, params = [], []
        if status is not None:
            check_status(status)
            where.append("status = ?")
            params.append(status)
        if severity is not None:
            check_severity(severity)
            where.append("severity = ?")
            params.append(severity)
        sql = "SELECT * FROM alerts"
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " ORDER BY severity_rank, last_seen DESC, finding_id LIMIT ?"
        params.append(limit)
        with self._connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        return [row_to_alert(row) for row in rows]

    def get_alert(self, finding_id: str) -> dict | None:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM alerts WHERE finding_id = ?",
                               (finding_id,)).fetchone()
        return row_to_alert(row) if row else None

    def update_alert(self, finding_id: str, *, actor: str, at: float,
                     status: str | None = None, assignee: str | None = None) -> dict:
        """Change status and/or assignee (None = leave as is; assignee "" = nobody).
        Every real change is written to the audit table in the same transaction.
        Raises KeyError for an unknown finding_id, ValueError for an unknown status."""
        if status is not None:
            check_status(status)
        with self._connect() as conn:
            row = conn.execute("SELECT status, assignee FROM alerts WHERE finding_id = ?",
                               (finding_id,)).fetchone()
            if row is None:
                raise KeyError(finding_id)
            new_status = row["status"] if status is None else status
            new_assignee = row["assignee"] if assignee is None else assignee
            changes = {}
            if new_status != row["status"]:
                changes["status"] = {"from": row["status"], "to": new_status}
            if new_assignee != row["assignee"]:
                changes["assignee"] = {"from": row["assignee"], "to": new_assignee}
            if changes:
                conn.execute("UPDATE alerts SET status = ?, assignee = ? WHERE finding_id = ?",
                             (new_status, new_assignee, finding_id))
                insert_audit(conn, actor=actor, action="alert.update", target=finding_id,
                             details=changes, at=at)
        return self.get_alert(finding_id)

    # ---------- audit ----------

    def add_audit(self, *, actor: str, action: str, target: str, details: dict,
                  at: float) -> int:
        """Append one audit row and return its audit_id."""
        with self._connect() as conn:
            return insert_audit(conn, actor=actor, action=action, target=target,
                                details=details, at=at)

    def list_audit(self, limit: int = 200) -> list[dict]:
        """Newest first."""
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM audit ORDER BY audit_id DESC LIMIT ?",
                                (limit,)).fetchall()
        return [{"audit_id": row["audit_id"], "at": row["at"], "actor": row["actor"],
                 "action": row["action"], "target": row["target"],
                 "details": json.loads(row["details_json"])} for row in rows]
