"""Run Zeek on one capture file.

Fall 2026 roadmap runner with two v2.0 additions:
- `-D` (deterministic): Zeek normally picks random seeds, so connection uids
  change on every run. With -D the same capture always gives the same uids,
  which keeps finding evidence and AI citations stable (CLAUDE.md rule 2).
  Only use -D for capture files; a live sensor keeps random seeds.
- community-id logging: adds `community_id` to conn.log, the same value
  Suricata writes, so Zeek and Suricata records can be joined.
And one fix found in planning: Zeek's own "local" policy makes DNS lookups
(detect-MHR asks an outside service about file hashes), so MaxGuard loads its
own copy without them, site.zeek (CLAUDE.md rule 1).
"""

import subprocess
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent / "scripts"
SITE_POLICY = Path(__file__).parent / "site.zeek"  # Zeek's "local" without network lookups


class ZeekError(RuntimeError):
    pass


def run_zeek(pcap: Path, out_dir: Path, timeout: int = 1800) -> Path:
    """Run Zeek on one capture file and write JSON logs into out_dir."""
    out_dir.mkdir(parents=True, exist_ok=True)
    extra = sorted(str(p) for p in SCRIPTS_DIR.glob("*.zeek"))  # Jakub's scripts
    cmd = ["zeek", "-D", "-C", "-r", str(pcap.resolve()), str(SITE_POLICY),
           "LogAscii::use_json=T", "policy/protocols/conn/community-id-logging", *extra]
    try:
        res = subprocess.run(cmd, cwd=out_dir, capture_output=True,
                             text=True, timeout=timeout, check=False)
    except FileNotFoundError:
        raise ZeekError("zeek is not installed or not on PATH: run MaxGuard inside its "
                        "Docker image, or install Zeek 9.0.0") from None
    except subprocess.TimeoutExpired:
        raise ZeekError(f"Zeek took longer than {timeout} seconds; try a smaller capture") from None
    if res.returncode != 0:
        raise ZeekError(res.stderr.strip() or "zeek failed")
    if not (out_dir / "conn.log").exists():
        raise ZeekError("Zeek produced no conn.log: is this a valid capture?")
    return out_dir
