"""CLI tests (Fiona): `maxguard analyze` on a fixture log folder, and exit codes.

These call cli.main.main([...]) directly instead of starting a new process:
same code path, much faster. A fixture *log folder* goes through
ZeekLogAdapter, so no Zeek is needed, and --no-ai means no Ollama is needed.
"""

import json
from pathlib import Path

import pytest

from cli import main as cli
from maxguard.zeek.runner import ZeekError

REPO = Path(__file__).resolve().parents[2]
TELNET_LOGS = REPO / "tests" / "fixtures" / "zeek" / "telnet"


def test_analyze_log_folder_writes_json_report(tmp_path, capsys):
    out = tmp_path / "report.json"

    code = cli.main(["analyze", str(TELNET_LOGS), "--no-ai", "-o", str(out)])

    assert code == cli.EXIT_OK
    report = json.loads(out.read_text())
    assert report["schema"] == "maxguard.report/2"
    assert report["input"]["adapter"] == "zeek-logs"
    assert report["ai"]["status"] == "disabled"
    assert [f["rule_id"] for f in report["findings"]] == ["cleartext.telnet"]
    # mappings/attack.yaml is applied: Telnet passwords can be sniffed.
    assert "T1040" in [t["technique_id"] for t in report["findings"][0]["attack"]]
    assert "1 finding(s)" in capsys.readouterr().err


def test_without_output_file_the_report_goes_to_stdout(capsys):
    code = cli.main(["analyze", str(TELNET_LOGS), "--no-ai"])

    assert code == cli.EXIT_OK
    report = json.loads(capsys.readouterr().out)
    assert report["findings"][0]["rule_id"] == "cleartext.telnet"


def test_same_input_gives_byte_identical_reports(tmp_path):
    first, second = tmp_path / "first.json", tmp_path / "second.json"
    cli.main(["analyze", str(TELNET_LOGS), "--no-ai", "-o", str(first)])
    cli.main(["analyze", str(TELNET_LOGS), "--no-ai", "-o", str(second)])
    assert first.read_bytes() == second.read_bytes()


def test_frameworks_option_keeps_only_those_controls(tmp_path):
    out = tmp_path / "report.json"

    cli.main(["analyze", str(TELNET_LOGS), "--no-ai", "-o", str(out),
              "--frameworks", "NIST SP 800-53"])

    finding = json.loads(out.read_text())["findings"][0]
    assert finding["controls"], "NIST maps cleartext.telnet"
    assert {c["framework"] for c in finding["controls"]} == {"NIST SP 800-53"}
    assert finding["attack"], "ATT&CK techniques are always added"


# ---- exit codes ------------------------------------------------------------

def test_text_file_is_bad_input(tmp_path, capsys):
    notes = tmp_path / "notes.txt"
    notes.write_text("hello\n")

    assert cli.main(["analyze", str(notes), "--no-ai"]) == cli.EXIT_BAD_INPUT
    assert "not a pcap/pcapng file" in capsys.readouterr().err


def test_missing_input_is_bad_input(tmp_path):
    missing = tmp_path / "missing.pcap"
    assert cli.main(["analyze", str(missing), "--no-ai"]) == cli.EXIT_BAD_INPUT


def test_unknown_framework_is_bad_input(capsys):
    code = cli.main(["analyze", str(TELNET_LOGS), "--no-ai", "--frameworks", "PCI-DSS"])

    assert code == cli.EXIT_BAD_INPUT
    assert "unknown framework(s): PCI-DSS" in capsys.readouterr().err


def test_wrong_option_exits_with_2():
    with pytest.raises(SystemExit) as stop:  # argparse exits by itself
        cli.main(["analyze", str(TELNET_LOGS), "--colour"])
    assert stop.value.code == cli.EXIT_BAD_INPUT


def test_zeek_failure_exits_with_3(monkeypatch, tmp_path, capsys):
    def zeek_fails(*args, **kwargs):
        raise ZeekError("problem with trace file")

    monkeypatch.setattr(cli, "analyze", zeek_fails)
    capture = tmp_path / "broken.pcap"
    capture.write_bytes(b"\xd4\xc3\xb2\xa1 not really a capture")

    assert cli.main(["analyze", str(capture), "--no-ai"]) == cli.EXIT_ZEEK_ERROR
    assert "Zeek failed: problem with trace file" in capsys.readouterr().err
