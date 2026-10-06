"""Rule decoy.contact (Fiona, FIO-06, proposed for v2.0 spring).

Each line of decoy.log (written by maxguard/decoy/service.py) records one
connection to a decoy. Nothing legitimate has a reason to contact a decoy, so
every line becomes a critical finding. The evidence is the decoy.log line
itself (its record_id), so the AI can cite it.

Not yet in maxguard/rules/__init__.py: the rule ID needs the Security Lead's
approval first. Until then it registers only when imported, for example in a test:
    from maxguard.rules.decoy import decoy_contact
"""

from __future__ import annotations

from pathlib import Path

from maxguard.adapters.base import read_log
from maxguard.ids import evidence
from maxguard.models import Finding
from maxguard.rules.base import rule

RULE_ID = "decoy.contact"
LOG_NAME = "decoy.log"


def contact_finding(rec: dict) -> Finding:
    ev = evidence(LOG_NAME, rec)  # uid is "": the decoy is not a Zeek connection
    return Finding(rule_id=RULE_ID, title="Someone contacted a decoy", severity="critical",
                   src_ip=rec["src_ip"], dst_ip=rec["dst_ip"], dst_port=int(rec["dst_port"]),
                   protocol=rec.get("service") or "tcp", first_seen=ev.ts, last_seen=ev.ts,
                   source="decoy",
                   details={"service": rec.get("service"),
                            "first_bytes_hex": rec.get("first_bytes_hex", "")},
                   evidence=[ev])


@rule(RULE_ID)
def decoy_contact(log_dir: Path) -> list[Finding]:
    """One finding per decoy.log line (merge() then counts repeats per src/dst/port)."""
    return [contact_finding(rec) for rec in read_log(log_dir, LOG_NAME)]
