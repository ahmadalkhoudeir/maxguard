"""JA4 watchlist rule (Jakub, proposed for v2.0 spring).

Suricata (checked on 7.0.10 and 8.0.7) writes a JA4 fingerprint of every TLS
client hello into eve.json ("event_type": "tls", field tls.ja4) when
maxguard-suricata.yaml turns it on. JA4 (TLS client fingerprinting) is
BSD-3-Clause; MaxGuard uses only JA4, no other JA4+ method (CLAUDE.md rule 7).

The rule compares each fingerprint with maxguard/intel/ja4_watchlist.yaml, a
list of {ja4, label, source} entries. We ship that list EMPTY: copying a
third-party fingerprint database with an unknown license into the repo is not
allowed, so every entry must come from our own captures or a source whose
license we have checked (write it in "source").

JAK-09 adds this module to maxguard/rules/__init__.py, which turns the rule on
(a new rule ID needs the Security Lead's approval).
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import yaml

from maxguard.adapters.base import read_log
from maxguard.ids import evidence
from maxguard.models import Finding
from maxguard.rules.base import rule

RULE_ID = "tls.ja4_watchlist"
WATCHLIST_PATH = Path(__file__).resolve().parent.parent / "intel" / "ja4_watchlist.yaml"
ENTRY_KEYS = ("ja4", "label", "source")


class WatchlistError(ValueError):
    """The watchlist file has a mistake (the message says which entry and what)."""


def looks_like_ja4(text: str) -> bool:
    """True for the JA4 shape 'a_b_c': 10 characters, then two 12-character hex hashes.

    Example from the JA4 spec: t13d1516h2_8daaf6152771_e5627efa2ab1
    This catches copy-paste mistakes in the watchlist (a JA3 hash, a JA4H, ...).
    """
    parts = text.split("_")
    if len(parts) != 3 or len(parts[0]) != 10:
        return False
    return all(len(p) == 12 and all(c in "0123456789abcdef" for c in p) for p in parts[1:])


def checked_ja4(entry: object, where: str) -> str:
    """Return the entry's JA4 (lower case) or raise WatchlistError saying what is wrong."""
    if not isinstance(entry, dict):
        raise WatchlistError(f"{where}: expected keys {ENTRY_KEYS}")
    missing = [key for key in ENTRY_KEYS if not str(entry.get(key) or "").strip()]
    if missing:
        raise WatchlistError(f"{where}: missing {missing}")
    ja4 = str(entry["ja4"]).strip().lower()  # Suricata writes JA4 in lower case
    if not looks_like_ja4(ja4):
        raise WatchlistError(f"{where}: {ja4!r} is not a JA4 fingerprint")
    return ja4


def load_watchlist(path: Path = WATCHLIST_PATH) -> dict[str, dict]:
    """Read the watchlist file into {ja4: entry}. Raises WatchlistError on a bad entry,
    so a typo in the file stops the analysis instead of silently matching nothing."""
    entries = yaml.safe_load(path.read_text()) or []  # a file with only comments -> None
    if not isinstance(entries, list):
        raise WatchlistError(f"{path.name}: expected a list of entries")
    watchlist: dict[str, dict] = {}
    for i, entry in enumerate(entries):
        watchlist[checked_ja4(entry, f"{path.name} entry {i}")] = entry
    return watchlist


def tls_events(log_dir: Path) -> Iterator[dict]:
    """Yield eve.json TLS events that carry a JA4 fingerprint."""
    for rec in read_log(log_dir, "eve.json"):
        if rec.get("event_type") == "tls" and (rec.get("tls") or {}).get("ja4"):
            yield rec


def watchlist_finding(rec: dict, entry: dict) -> Finding:
    ev = evidence("eve.json", rec)  # its ts is the eve timestamp as epoch seconds
    tls = rec["tls"]
    return Finding(rule_id=RULE_ID, title=f"TLS client matches JA4 watchlist: {entry['label']}",
                   severity="high", src_ip=rec["src_ip"], dst_ip=rec["dest_ip"],
                   dst_port=int(rec["dest_port"]), protocol="tls",
                   first_seen=ev.ts, last_seen=ev.ts, source="suricata",
                   details={"ja4": tls["ja4"], "label": entry["label"],
                            "watchlist_source": entry["source"], "sni": tls.get("sni")},
                   evidence=[ev])


@rule(RULE_ID)
def ja4_watchlist(log_dir: Path, watchlist_path: Path = WATCHLIST_PATH) -> list[Finding]:
    """One finding per TLS event whose JA4 is on the watchlist (merged per src/dst/port)."""
    watchlist = load_watchlist(watchlist_path)
    if not watchlist:  # the shipped list is empty: nothing to compare
        return []
    return [watchlist_finding(rec, watchlist[rec["tls"]["ja4"]])
            for rec in tls_events(log_dir) if rec["tls"]["ja4"] in watchlist]
