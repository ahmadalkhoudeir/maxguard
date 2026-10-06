"""The pipeline (Jaiden, JAI-03): picking an adapter and producing the report dict.

These tests use the Zeek-log adapter on fixture folders, so they need no Zeek.
tests/integration/ runs real captures through Zeek inside the engine image.
"""

import zipfile
from pathlib import Path

import pytest

from maxguard.pipeline import MappingsNotFound, UnsupportedInput, analyze, pick_adapter

FIXTURES = Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "zeek"


def test_text_file_is_unsupported_input(tmp_path):
    path = tmp_path / "notes.txt"
    path.write_text("hello\n")
    with pytest.raises(UnsupportedInput):
        pick_adapter(path)


def test_zip_of_logs_is_analyzed(tmp_path):
    archive = tmp_path / "telnet_logs.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        for log in sorted((FIXTURES / "telnet").glob("*.log")):
            zf.write(log, arcname=log.name)

    report = analyze(archive, tmp_path / "work", explain=False)

    assert report["input"]["adapter"] == "zeek-logs"
    assert [f["rule_id"] for f in report["findings"]] == ["cleartext.telnet"]


def test_report_has_every_section(tmp_path):
    report = analyze(FIXTURES / "telnet", tmp_path, explain=False)
    assert report["schema"] == "maxguard.report/2"
    assert set(report) == {"schema", "input", "tools", "frameworks", "findings", "assets",
                           "events", "ai"}
    assert report["ai"]["status"] == "disabled"


def test_findings_are_mapped_to_controls(tmp_path):
    [finding] = analyze(FIXTURES / "telnet", tmp_path, explain=False)["findings"]
    assert any(c["framework"] == "NIST SP 800-53" for c in finding["controls"])


def test_same_input_gives_the_same_report(tmp_path):
    first = analyze(FIXTURES / "cert_expired", tmp_path / "a", explain=False)
    second = analyze(FIXTURES / "cert_expired", tmp_path / "b", explain=False)
    assert first == second  # no clock, no randomness (CLAUDE.md rule 2)


def test_missing_mapping_files_fail_loudly(tmp_path, monkeypatch):
    monkeypatch.setenv("MAXGUARD_MAPPINGS_DIR", str(tmp_path / "nothing-here"))
    with pytest.raises(MappingsNotFound):
        analyze(FIXTURES / "telnet", tmp_path / "work", explain=False)
