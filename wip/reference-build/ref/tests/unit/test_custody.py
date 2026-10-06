"""Tests for the chain-of-custody log (Amory, AMO-05)."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from maxguard.custody import log as custody
from maxguard.custody.signing import generate_keypair

AT = 1791250000.0  # a fixed time: the log never reads the clock


@pytest.fixture
def keys(tmp_path) -> tuple[Path, Path]:
    return generate_keypair(tmp_path / "keys")


@pytest.fixture
def artifacts(tmp_path) -> list[Path]:
    """Three small evidence files (stand-ins for a capture and two reports)."""
    files = []
    for name, data in (("telnet.pcap", b"capture bytes"), ("report.json", b"{}"),
                       ("report.html", b"<html></html>")):
        path = tmp_path / "evidence" / name
        path.parent.mkdir(exist_ok=True)
        path.write_bytes(data)
        files.append(path)
    return files


def write_log(log_path: Path, artifacts: list[Path], private_key: Path) -> list[dict]:
    actions = ("capture_received", "report_generated", "report_exported")
    return [custody.append(log_path, action=action, artifact_path=artifact, actor="amory",
                           at=AT + i, private_key_path=private_key)
            for i, (action, artifact) in enumerate(zip(actions, artifacts, strict=True))]


@pytest.fixture
def log_path(tmp_path, artifacts, keys) -> Path:
    path = tmp_path / "custody.jsonl"
    write_log(path, artifacts, keys[0])
    return path


def read_lines(path: Path) -> list[str]:
    return path.read_text().splitlines()


def write_lines(path: Path, lines: list[str]) -> None:
    path.write_text("\n".join(lines) + "\n")


def change_entry(path: Path, position: int, field: str, value) -> None:
    lines = read_lines(path)
    entry = json.loads(lines[position - 1])
    entry[field] = value
    lines[position - 1] = json.dumps(entry, sort_keys=True)
    write_lines(path, lines)


# ---------- a good log ----------

def test_a_good_chain_verifies(log_path, keys):
    assert custody.verify(log_path, keys[1]) == (True, None, "ok")


def test_entries_link_to_each_other(log_path, artifacts):
    entries = [json.loads(line) for line in read_lines(log_path)]
    assert [e["seq"] for e in entries] == [1, 2, 3]
    assert entries[0]["prev_hash"] == "0" * 64
    assert entries[1]["prev_hash"] == entries[0]["entry_hash"]
    assert entries[2]["prev_hash"] == entries[1]["entry_hash"]

    first = entries[0]
    assert set(first) == set(custody.ALL_FIELDS)
    assert first["artifact"] == "telnet.pcap"  # the name, never the path
    assert first["sha256"] == hashlib.sha256(b"capture bytes").hexdigest()
    assert first["size"] == len(b"capture bytes")
    assert first["at"] == AT
    assert first["action"] == "capture_received"


def test_append_never_reads_the_clock(tmp_path, artifacts, keys, monkeypatch):
    def no_clock():
        raise AssertionError("the custody log must not read the clock")

    monkeypatch.setattr("time.time", no_clock)
    entry = custody.append(tmp_path / "c.jsonl", action="capture_received",
                           artifact_path=artifacts[0], actor="amory", at=AT,
                           private_key_path=keys[0])
    assert entry["at"] == AT


def test_same_inputs_give_the_same_log(tmp_path, artifacts, keys):
    # Ed25519 signatures are deterministic, so the whole file is.
    write_log(tmp_path / "a.jsonl", artifacts, keys[0])
    write_log(tmp_path / "b.jsonl", artifacts, keys[0])
    assert (tmp_path / "a.jsonl").read_bytes() == (tmp_path / "b.jsonl").read_bytes()


# ---------- tampering ----------

@pytest.mark.parametrize("field, value", [
    ("seq", 7),
    ("at", AT + 3600),
    ("action", "report_deleted"),
    ("artifact", "other.pcap"),
    ("sha256", "0" * 64),
    ("size", 1),
    ("actor", "mallory"),
    ("prev_hash", "f" * 64),
    ("entry_hash", "e" * 64),
    ("signature", "AAAA"),
])
def test_changing_any_field_fails_at_that_entry(log_path, keys, field, value):
    change_entry(log_path, 2, field, value)
    ok, bad_seq, reason = custody.verify(log_path, keys[1])
    assert (ok, bad_seq) == (False, 2)
    assert reason


def test_a_rewritten_entry_with_a_fresh_hash_fails_on_the_signature(log_path, keys):
    entry = json.loads(read_lines(log_path)[1])
    entry["actor"] = "mallory"
    change_entry(log_path, 2, "actor", "mallory")
    change_entry(log_path, 2, "entry_hash", custody.entry_hash(entry))
    ok, bad_seq, reason = custody.verify(log_path, keys[1])
    assert (ok, bad_seq) == (False, 2)
    assert "signature" in reason


def test_deleting_a_line_fails(log_path, keys):
    lines = read_lines(log_path)
    write_lines(log_path, [lines[0], lines[2]])
    ok, bad_seq, reason = custody.verify(log_path, keys[1])
    assert (ok, bad_seq) == (False, 2)
    assert "removed or moved" in reason


def test_swapping_two_lines_fails(log_path, keys):
    lines = read_lines(log_path)
    write_lines(log_path, [lines[0], lines[2], lines[1]])
    assert custody.verify(log_path, keys[1])[:2] == (False, 2)


def test_a_line_that_is_not_json_fails(log_path, keys):
    lines = read_lines(log_path)
    write_lines(log_path, [lines[0], "not json", *lines[1:]])
    assert custody.verify(log_path, keys[1]) == (False, 2, "not valid JSON")


def test_the_wrong_public_key_fails_at_the_first_entry(log_path, tmp_path):
    _, other_public = generate_keypair(tmp_path / "other-keys")
    ok, bad_seq, reason = custody.verify(log_path, other_public)
    assert (ok, bad_seq) == (False, 1)
    assert "wrong public key" in reason


def test_cutting_off_the_end_needs_the_recorded_head(log_path, keys):
    # A shorter log is still a valid chain: this is why the head is recorded elsewhere.
    recorded = custody.head(log_path)
    write_lines(log_path, read_lines(log_path)[:2])
    assert custody.verify(log_path, keys[1]) == (True, None, "ok")
    assert custody.head(log_path) != recorded
    assert recorded[0] == 3


# ---------- command line ----------

def test_command_line_verify(log_path, keys, capsys):
    assert custody.main(["verify", str(log_path), str(keys[1])]) == 0
    seq, last_hash = custody.head(log_path)
    assert capsys.readouterr().out == f"ok: 3 entries, head {last_hash}\n"

    change_entry(log_path, 3, "actor", "mallory")
    assert custody.main(["verify", str(log_path), str(keys[1])]) == 1
    assert capsys.readouterr().out.startswith("FAILED at seq 3: entry_hash does not match")
