"""Suricata runner tests (Jakub, JAK-05). No real Suricata is needed.

A tiny fake `suricata` program is put first on the PATH. It writes the files
the real one writes, so the tests check what MaxGuard does with them.
"""

import os
import stat
from pathlib import Path

import pytest

from maxguard.suricata import runner

FAKE_SURICATA = """#!/bin/sh
# Fake suricata: find the folder after -l and write what Suricata would write.
while [ $# -gt 0 ]; do
  if [ "$1" = "-l" ]; then out="$2"; fi
  shift
done
echo '{"event_type":"flow"}' > "$out/eve.json"
for extra in fast.log stats.log suricata.log; do echo x > "$out/$extra"; done
exit ${FAKE_EXIT:-0}
"""


@pytest.fixture
def fake_suricata(tmp_path, monkeypatch):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    program = bin_dir / "suricata"
    program.write_text(FAKE_SURICATA)
    program.chmod(program.stat().st_mode | stat.S_IEXEC)
    monkeypatch.setenv("PATH", f"{bin_dir}{os.pathsep}{os.environ['PATH']}")
    return program


def test_without_suricata_nothing_happens(tmp_path, monkeypatch):
    monkeypatch.setenv("PATH", str(tmp_path / "empty"))  # no suricata anywhere

    assert runner.run_suricata_if_available(Path("x.pcap"), tmp_path) is None
    assert list(tmp_path.iterdir()) == []


def test_eve_json_is_written_and_the_other_files_removed(tmp_path, fake_suricata):
    log_dir = tmp_path / "logs"

    eve = runner.run_suricata_if_available(Path("capture.pcap"), log_dir)

    assert eve == log_dir / "eve.json"
    assert sorted(p.name for p in log_dir.iterdir()) == ["eve.json"]


def test_a_failing_suricata_raises(tmp_path, fake_suricata, monkeypatch):
    monkeypatch.setenv("FAKE_EXIT", "1")

    with pytest.raises(runner.SuricataError):
        runner.run_suricata(Path("capture.pcap"), tmp_path / "logs")
