"""MaxGuard's Zeek site policy makes no network lookups (Jakub, JAK-01).

Zeek's own "local" policy loads scripts that send DNS queries (CLAUDE.md rule 1).
Zeek runs as its own program, so the Python offline guard cannot catch them:
these tests make sure no MaxGuard Zeek file loads them, and that the runner
uses site.zeek instead of "local".
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from maxguard.zeek import runner

ZEEK_DIR = Path(runner.__file__).parent
NETWORK_SCRIPTS = (
    "frameworks/files/detect-MHR",              # DNS query per downloaded file's hash
    "protocols/ssh/interesting-hostnames",      # reverse DNS on SSH logins
    "frameworks/notice/extend-email/hostnames",  # reverse DNS for notice e-mails
)


def loaded(path: Path) -> list[str]:
    """The scripts a .zeek file loads with @load."""
    return [line.split()[1] for line in path.read_text().splitlines()
            if line.startswith("@load ")]


def test_no_maxguard_zeek_file_loads_a_script_that_uses_the_network():
    for path in sorted(ZEEK_DIR.rglob("*.zeek")):
        for script in loaded(path):
            assert not script.endswith(NETWORK_SCRIPTS), f"{path.name} loads {script}"
            assert script not in ("local", "site/local"), f"{path.name} loads Zeek's local"


def test_site_policy_keeps_the_logs_maxguard_reads():
    scripts = loaded(runner.SITE_POLICY)
    for needed in ("protocols/conn/known-hosts", "protocols/conn/known-services",
                   "protocols/ssl/validate-certs", "frameworks/files/hash-all-files"):
        assert needed in scripts


def test_runner_loads_site_zeek_not_local(monkeypatch, tmp_path):
    seen = {}

    def fake_run(cmd, **kwargs):
        seen["cmd"] = cmd
        (tmp_path / "conn.log").write_text("")
        return subprocess.CompletedProcess(cmd, 0, "", "")

    monkeypatch.setattr(runner.subprocess, "run", fake_run)
    runner.run_zeek(tmp_path / "x.pcap", tmp_path)
    assert str(runner.SITE_POLICY) in seen["cmd"]
    assert "local" not in seen["cmd"]
