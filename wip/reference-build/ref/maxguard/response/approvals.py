"""Block proposals and their approval workflow (Ahmad, AHM-08).

CLAUDE.md rule 4: a block always needs explicit human approval, is reversible,
and is logged. The steps (docs/ARCHITECTURE.md section 13):

    proposed -> previewed -> approved -> applied -> reverted
    proposed or previewed -> rejected

- Approve only after a preview: the person must have seen what the block stops.
- Approve needs the person's name and the IP address typed again (confirm_ip),
  so a block is never approved by a stray click.
- Every step, and every refused approval, writes a row to the audit table
  (action "response.<step>", target = the proposal id). A state change and its
  audit row are written in ONE transaction (storage.state.insert_audit), so a
  crash can never leave a change without its audit row.
- Times are passed in by the caller (the API reads the clock, this module never does).

Proposals live in their own table in state.db, created here with
CREATE TABLE IF NOT EXISTS, so storage/state.py does not change.
"""

from __future__ import annotations

import ipaddress
import json
import sqlite3
from collections.abc import Iterator, Sequence
from contextlib import contextmanager

from maxguard.response.enforcers.base import Enforcer
from maxguard.response.generate import check_direction, parse_ip, rules_for
from maxguard.storage.state import StateStore, insert_audit

STATES = ("proposed", "previewed", "approved", "applied", "reverted", "rejected")

SCHEMA = """
CREATE TABLE IF NOT EXISTS response_proposals (
    proposal_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    ip           TEXT NOT NULL,
    direction    TEXT NOT NULL,
    reason       TEXT NOT NULL,
    finding_id   TEXT,
    state        TEXT NOT NULL,
    created_by   TEXT NOT NULL,
    created_at   REAL NOT NULL,
    updated_at   REAL NOT NULL,
    approved_by  TEXT,
    method       TEXT,      -- how it was applied: "manual" or "enforcer"
    preview_json TEXT       -- the last preview the person saw
);
"""


class WrongState(Exception):
    """This step is not allowed from the proposal's current state (the API answers 409)."""


class ProposalStore:
    def __init__(self, state_store: StateStore):
        self.state_store = state_store
        with self._connect() as conn:
            conn.executescript(SCHEMA)

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        # A new connection per call, like StateStore: the API uses several threads.
        conn = sqlite3.connect(self.state_store.path, timeout=5.0)
        conn.row_factory = sqlite3.Row
        try:
            with conn:  # commit on success, roll back on an exception
                yield conn
        finally:
            conn.close()

    # ---------- reading ----------

    def get(self, proposal_id: int) -> dict:
        """One proposal with its generated commands. KeyError if it does not exist."""
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM response_proposals WHERE proposal_id = ?",
                               (proposal_id,)).fetchone()
        if row is None:
            raise KeyError(proposal_id)
        return row_to_proposal(row)

    def list_proposals(self, limit: int = 200) -> list[dict]:
        """Newest first."""
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM response_proposals "
                                "ORDER BY proposal_id DESC LIMIT ?", (limit,)).fetchall()
        return [row_to_proposal(row) for row in rows]

    # ---------- the steps ----------

    def propose(self, *, ip: str, direction: str, actor: str, at: float, reason: str = "",
                finding_id: str | None = None) -> dict:
        address = str(parse_ip(ip))  # ValueError for anything that is not a plain address
        check_direction(direction)
        with self._connect() as conn:  # the proposal and its audit row: one transaction
            cur = conn.execute(
                "INSERT INTO response_proposals (ip, direction, reason, finding_id, state, "
                "created_by, created_at, updated_at) VALUES (?, ?, ?, ?, 'proposed', ?, ?, ?)",
                (address, direction, reason, finding_id, actor, at, at))
            proposal_id = cur.lastrowid
            audit(conn, actor, "proposed", proposal_id, at,
                  {"ip": address, "direction": direction, "finding_id": finding_id})
        return self.get(proposal_id)

    def record_preview(self, proposal_id: int, *, actor: str, preview: dict,
                       at: float) -> dict:
        """Keep the preview the person saw. A previewed proposal may be previewed again."""
        self.move(proposal_id, ("proposed", "previewed"), "previewed", at, actor,
                  {"connections": preview["connections"], "devices": len(preview["devices"]),
                   "window_end": preview["window_end"]},
                  preview_json=json.dumps(preview, sort_keys=True))
        return self.get(proposal_id)

    def approve(self, proposal_id: int, *, actor: str, confirm_ip: str, at: float) -> dict:
        """The person types the address again; a missing or different address is refused."""
        proposal = self.get(proposal_id)
        if not actor.strip():
            raise ValueError("enter your name to approve a block")
        if not same_address(confirm_ip, proposal["ip"]):
            self.audit_only(actor, "approve_refused", proposal_id, at,
                            {"reason": "typed IP does not match"})
            raise ValueError("the IP address you typed does not match the proposal")
        self.move(proposal_id, ("previewed",), "approved", at, actor, {"ip": proposal["ip"]},
                  approved_by=actor)
        return self.get(proposal_id)

    def mark_applied(self, proposal_id: int, *, actor: str, at: float,
                     enforcers: Sequence[Enforcer] = ()) -> dict:
        """Apply an approved block: by the enforcers if given, else the person ran the
        commands by hand and says so. If an enforcer fails, the state stays 'approved'."""
        proposal = self.require_state(proposal_id, "approved")
        method = "enforcer" if enforcers else "manual"
        try:
            for enforcer in enforcers:
                enforcer.add(proposal["ip"])
                enforcer.apply()
        except Exception as err:
            self.audit_only(actor, "apply_failed", proposal_id, at, {"error": str(err)})
            raise
        self.move(proposal_id, ("approved",), "applied", at, actor,
                  {"ip": proposal["ip"], "method": method}, method=method)
        return self.get(proposal_id)

    def revert(self, proposal_id: int, *, actor: str, at: float,
               enforcers: Sequence[Enforcer] = ()) -> dict:
        """Undo the block the same way it was applied."""
        proposal = self.require_state(proposal_id, "applied")
        if proposal["method"] == "enforcer":
            if not enforcers:
                raise ValueError("this block was applied by the firewall connector, "
                                 "which is not configured now")
            try:
                for enforcer in enforcers:
                    enforcer.remove(proposal["ip"])
                    enforcer.apply()
            except Exception as err:
                self.audit_only(actor, "revert_failed", proposal_id, at, {"error": str(err)})
                raise
        self.move(proposal_id, ("applied",), "reverted", at, actor,
                  {"ip": proposal["ip"], "method": proposal["method"]})
        return self.get(proposal_id)

    def reject(self, proposal_id: int, *, actor: str, at: float, reason: str = "") -> dict:
        self.move(proposal_id, ("proposed", "previewed"), "rejected", at, actor,
                  {"reason": reason})
        return self.get(proposal_id)

    # ---------- helpers ----------

    def require_state(self, proposal_id: int, state: str) -> dict:
        proposal = self.get(proposal_id)
        if proposal["state"] != state:
            raise WrongState(f"proposal {proposal_id} is {proposal['state']}, not {state}")
        return proposal

    def move(self, proposal_id: int, allowed: tuple[str, ...], new_state: str, at: float,
             actor: str, details: dict, **columns: str) -> None:
        """Change the state only if it is still one of `allowed`, and audit it.

        The check and the change are one UPDATE, so two people clicking at the same
        moment cannot both approve (or both revert) the same proposal. The audit row
        (action "response.<new_state>") is written in the same transaction."""
        self.get(proposal_id)  # KeyError first, so a missing proposal is a 404, not a 409
        sets = "".join(f", {name} = ?" for name in columns)  # names come from our code only
        placeholders = ", ".join("?" for _ in allowed)
        with self._connect() as conn:
            cur = conn.execute(
                f"UPDATE response_proposals SET state = ?, updated_at = ?{sets} "
                f"WHERE proposal_id = ? AND state IN ({placeholders})",
                (new_state, at, *columns.values(), proposal_id, *allowed))
            if cur.rowcount == 1:
                audit(conn, actor, new_state, proposal_id, at, details)
        if cur.rowcount == 0:
            state = self.get(proposal_id)["state"]
            raise WrongState(f"proposal {proposal_id} is {state}; cannot become {new_state}")

    def audit_only(self, actor: str, step: str, proposal_id: int, at: float,
                   details: dict) -> None:
        """Audit a refused or failed step, which changes nothing else."""
        with self._connect() as conn:
            audit(conn, actor, step, proposal_id, at, details)


def audit(conn: sqlite3.Connection, actor: str, step: str, proposal_id: int, at: float,
          details: dict) -> None:
    """One audit row (action "response.<step>"), inside the caller's transaction."""
    insert_audit(conn, actor=actor, action=f"response.{step}", target=str(proposal_id),
                 details=details, at=at)


def same_address(typed: str | None, expected: str) -> bool:
    """'2001:DB8::7' and '2001:db8::7' are the same address; '' or 'abc' never match."""
    try:
        return str(ipaddress.ip_address((typed or "").strip())) == expected
    except ValueError:
        return False


def row_to_proposal(row: sqlite3.Row) -> dict:
    proposal = {key: row[key] for key in row.keys() if key != "preview_json"}
    proposal["preview"] = json.loads(row["preview_json"]) if row["preview_json"] else None
    proposal["rules"] = rules_for(row["ip"], row["direction"])  # commands + undo, always shown
    return proposal
