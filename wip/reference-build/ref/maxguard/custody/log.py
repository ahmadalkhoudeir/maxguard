"""Chain-of-custody log (Amory, AMO-05).

An append-only JSON Lines file that records what happened to evidence, for
example "capture_received", "report_generated" or "report_exported". Each line
is one entry:

    seq         1, 2, 3, ... in the order the entries were written
    at          when it happened, in Unix seconds (passed in: never read from the clock)
    action      what happened
    artifact    the file's name (not its path, which differs between machines)
    sha256      the file's SHA-256 at that moment
    size        the file's size in bytes
    actor       who did it
    prev_hash   the entry_hash of the entry before (64 zeros for the first entry)
    entry_hash  SHA-256 of this entry as canonical JSON, without entry_hash and signature
    signature   Ed25519 signature of entry_hash (base64), made with the custody key

Why both a hash chain and a signature:
- The chain shows that no entry was edited, removed or moved: each entry pins
  the hash of the one before it.
- The signature shows that this MaxGuard installation wrote the entries. Without
  it, someone who changed a line could simply recompute every hash after it.

What the chain cannot show: that entries were cut off at the END. A shorter log
is still a valid chain. So `verify` prints the last entry's hash ("head"): write
it into the report or the case notes, and compare it later.

Verify a log from the command line:
    python -m maxguard.custody.log verify custody.jsonl custody_ed25519_public.pem
"""

from __future__ import annotations

import argparse
import base64
import binascii
import hashlib
import json
import os
import sys
import threading
from pathlib import Path

from maxguard.custody.signing import sign
from maxguard.custody.signing import verify as signature_ok
from maxguard.ids import canonical_json

GENESIS_HASH = "0" * 64  # the "entry before" the first entry
HASHED_FIELDS = ("seq", "at", "action", "artifact", "sha256", "size", "actor", "prev_hash")
ALL_FIELDS = (*HASHED_FIELDS, "entry_hash", "signature")

# Two threads appending at once could both take the same seq. The API runs
# analyses in worker threads, so appends inside one process take turns.
# Only one program (the console) should write to a log.
_append_lock = threading.Lock()


def append(log_path: Path, *, action: str, artifact_path: Path, actor: str, at: float,
           private_key_path: Path) -> dict:
    """Add one signed entry for artifact_path to the log and return it."""
    log_path = Path(log_path)
    with _append_lock:
        last = last_entry(log_path)
        entry = {
            "seq": last["seq"] + 1 if last else 1,
            "at": at,
            "action": action,
            "artifact": Path(artifact_path).name,
            "sha256": file_sha256(artifact_path),
            "size": Path(artifact_path).stat().st_size,
            "actor": actor,
            "prev_hash": last["entry_hash"] if last else GENESIS_HASH,
        }
        entry["entry_hash"] = entry_hash(entry)
        signature = sign(entry["entry_hash"].encode("ascii"), private_key_path)
        entry["signature"] = base64.b64encode(signature).decode("ascii")
        write_line(log_path, entry)
    return entry


def entry_hash(entry: dict) -> str:
    """SHA-256 of the hashed fields in one fixed text form (sorted keys, no spaces)."""
    hashed = {field: entry[field] for field in HASHED_FIELDS}
    return hashlib.sha256(canonical_json(hashed).encode("utf-8")).hexdigest()


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def last_entry(log_path: Path) -> dict | None:
    if not log_path.exists():
        return None
    lines = log_path.read_text(encoding="utf-8").splitlines()
    return json.loads(lines[-1]) if lines else None


def write_line(log_path: Path, entry: dict) -> None:
    """Append one line and make sure it is on the disk before returning."""
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, sort_keys=True) + "\n")
        f.flush()
        os.fsync(f.fileno())  # a power cut right after append() must not lose the entry


def verify(log_path: Path, public_key_path: Path) -> tuple[bool, int | None, str]:
    """Check every entry in order.

    Returns (True, None, "ok"), or (False, first_bad_seq, reason) where
    first_bad_seq is the position (1, 2, 3, ...) of the first entry that fails."""
    previous = GENESIS_HASH
    lines = Path(log_path).read_text(encoding="utf-8").splitlines()
    for position, line in enumerate(lines, start=1):
        problem = check_entry(line, position, previous, public_key_path)
        if problem:
            return False, position, problem
        previous = json.loads(line)["entry_hash"]
    return True, None, "ok"


def check_entry(line: str, position: int, previous: str, public_key_path: Path) -> str | None:
    """Why this line is not a good entry, or None if it is."""
    try:
        entry = json.loads(line)
    except json.JSONDecodeError:
        return "not valid JSON"
    if not isinstance(entry, dict) or set(entry) != set(ALL_FIELDS):
        return "missing or unexpected fields"
    if entry["seq"] != position:
        return f"seq is {entry['seq']!r}, expected {position}: an entry was removed or moved"
    if entry["prev_hash"] != previous:
        return "prev_hash does not match the entry before: an entry was removed, moved or changed"
    if entry_hash(entry) != entry["entry_hash"]:
        return "entry_hash does not match the entry: the entry was changed after it was written"
    try:
        signature = base64.b64decode(entry["signature"], validate=True)
    except (binascii.Error, TypeError):
        return "signature is not valid base64"
    if not signature_ok(entry["entry_hash"].encode("ascii"), signature, public_key_path):
        return "bad signature: the entry was forged, or this is the wrong public key"
    return None


def head(log_path: Path) -> tuple[int, str]:
    """(seq, entry_hash) of the last entry: record it elsewhere to detect a cut-off log."""
    last = last_entry(Path(log_path))
    return (last["seq"], last["entry_hash"]) if last else (0, GENESIS_HASH)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m maxguard.custody.log",
                                     description="Check a MaxGuard chain-of-custody log.")
    commands = parser.add_subparsers(dest="command", required=True)
    check = commands.add_parser("verify", help="check every entry's hash chain and signature")
    check.add_argument("log", type=Path, help="the custody log (JSON Lines)")
    check.add_argument("public_key", type=Path, help="the custody public key (PEM)")
    args = parser.parse_args(argv)

    ok, bad_seq, reason = verify(args.log, args.public_key)
    if not ok:
        print(f"FAILED at seq {bad_seq}: {reason}")
        return 1
    seq, last_hash = head(args.log)
    noun = "entry" if seq == 1 else "entries"
    print(f"ok: {seq} {noun}, head {last_hash}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
