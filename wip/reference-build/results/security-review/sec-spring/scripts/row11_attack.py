"""AHM-04 row 11: tamper with a chain-of-custody log (maxguard.custody.log, private ALL build).

Throwaway keys and synthetic evidence files are made at run time.
Usage: row11_attack.py REPO OUT
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(sys.argv[1]).resolve()
WORK = Path(sys.argv[2]).resolve()
sys.path.insert(0, str(REPO))

from maxguard.custody import log as custody  # noqa: E402
from maxguard.custody.signing import generate_keypair  # noqa: E402

AT = 1791250000.0


def cli(log_path: Path, pub: Path) -> str:
    out = subprocess.run([sys.executable, "-m", "maxguard.custody.log", "verify", str(log_path), str(pub)],
                         cwd=REPO, capture_output=True, text=True,
                         env={"PYTHONDONTWRITEBYTECODE": "1", "PATH": "/usr/bin:/bin"})
    return f"exit {out.returncode}: {(out.stdout + out.stderr).strip()}"


def main():
    WORK.mkdir(parents=True, exist_ok=True)
    priv, pub = generate_keypair(WORK / "keys")
    evidence = WORK / "evidence"
    evidence.mkdir()
    log_path = WORK / "custody.jsonl"
    for i, action in enumerate(("capture_received", "report_generated", "report_exported",
                                "capture_received", "report_generated")):
        artifact = evidence / f"item{i + 1}.bin"
        artifact.write_bytes(f"synthetic evidence {i + 1}".encode())
        custody.append(log_path, action=action, artifact_path=artifact, actor="amory", at=AT + i,
                       private_key_path=priv)
    original = log_path.read_text()
    lines = original.splitlines()
    print("== the untouched log (5 entries)")
    print("  " + cli(log_path, pub))
    recorded_head = custody.head(log_path)

    def run(label, text):
        path = WORK / "tampered.jsonl"
        path.write_text(text)
        print(f"  [{label}] {cli(path, pub)}")

    print("== one byte changed in the middle entry (seq 3)")
    third = lines[2]
    i = third.index('"actor": "amory"') + len('"actor": "a')
    run("actor 'amory' -> 'aMory'", "\n".join(lines[:2] + [third[:i] + "M" + third[i + 1:]] + lines[3:]) + "\n")
    i = third.index('"sha256": "') + len('"sha256": "') + 10
    run("one hex digit of sha256", "\n".join(lines[:2] + [third[:i] + ("0" if third[i] != "0" else "1")
                                                           + third[i + 1:]] + lines[3:]) + "\n")
    i = third.index('"signature": "') + len('"signature": "') + 40
    run("one character in the middle of the signature",
        "\n".join(lines[:2] + [third[:i] + ("A" if third[i] != "A" else "B") + third[i + 1:]] + lines[3:]) + "\n")
    i = third.index('"prev_hash": "') + len('"prev_hash": "') + 5
    run("one hex digit of prev_hash",
        "\n".join(lines[:2] + [third[:i] + ("0" if third[i] != "0" else "1") + third[i + 1:]] + lines[3:]) + "\n")

    print("== exhaustive: every single-byte change of entry 3 (each position x every printable ASCII byte)")
    original3 = json.loads(third)
    passed, same_meaning, total = [], 0, 0
    previous = lines[1] and json.loads(lines[1])["entry_hash"]
    for pos in range(len(third)):
        for code in range(32, 127):
            ch = chr(code)
            if ch == third[pos]:
                continue
            total += 1
            changed = third[:pos] + ch + third[pos + 1:]
            if custody.check_entry(changed, 3, previous, pub) is None:
                # entry 4 must still chain to it: prev_hash of entry 4 == entry_hash of entry 3
                if json.loads(changed)["entry_hash"] != json.loads(lines[3])["prev_hash"]:
                    continue
                meaning = json.loads(changed) == original3 and all(
                    type(json.loads(changed)[k]) is type(original3[k]) for k in original3)
                same_meaning += meaning
                passed.append((pos, third[pos], ch, meaning))
    print(f"  {total} single-byte variants of entry 3 tried; {len(passed)} pass verify; "
          f"{same_meaning} of those parse to exactly the same values")
    for pos, old, new, meaning in passed[:12]:
        context = third[max(0, pos - 12):pos + 6]
        print(f"    pos {pos}: {old!r} -> {new!r} in ...{context}...  same values: {meaning}")
    if passed:
        pos, old, new, _ = passed[0]
        variant = "\n".join(lines[:2] + [third[:pos] + new + third[pos + 1:]] + lines[3:]) + "\n"
        run(f"CLI on the first passing variant (pos {pos})", variant)

    print("== duplicate key inserted in entry 3 (more than one byte)")
    dup = third.replace('{"action"', '{"actor": "mallory", "action"', 1)
    run('entry 3 starts with "actor": "mallory" before the real "actor"',
        "\n".join(lines[:2] + [dup] + lines[3:]) + "\n")
    print(f"    Python json.loads keeps: {json.loads(dup)['actor']!r}; raw line shows both: "
          f"{dup[:40]}...")

    print("== an entry removed (entry 3 of 5)")
    run("entry 3 deleted", "\n".join(lines[:2] + lines[3:]) + "\n")
    print("== the last entry cut off")
    run("entry 5 deleted", "\n".join(lines[:4]) + "\n")
    print(f"    head recorded before the cut: seq {recorded_head[0]}, {recorded_head[1]}")
    run("entry 5 cut in the middle of its line", "\n".join(lines[:4] + [lines[4][:len(lines[4]) // 2]]) + "\n")
    run("every entry deleted (empty file)", "")
    print("== other tampering")
    run("entries 2 and 3 swapped", "\n".join([lines[0], lines[2], lines[1]] + lines[3:]) + "\n")
    forged = json.loads(lines[4])
    forged.update(seq=6, prev_hash=forged["entry_hash"], action="report_deleted", at=AT + 9)
    forged["entry_hash"] = custody.entry_hash(forged)
    run("forged 6th entry appended (correct hashes, old signature)",
        original + json.dumps(forged, sort_keys=True) + "\n")
    _, other_pub = generate_keypair(WORK / "other")
    print(f"  [right log, wrong public key] {cli(log_path, other_pub)}")


if __name__ == "__main__":
    main()
