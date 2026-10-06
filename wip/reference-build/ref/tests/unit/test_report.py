"""Tests for maxguard.report: JSON, CSV and HTML exports of a report dict."""

import csv
import io
import json
from pathlib import Path

from maxguard.models import Control, Evidence, Finding, Sentence
from maxguard.pipeline import analyze
from maxguard.report import CSV_COLUMNS, to_csv, to_html, to_json

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "zeek"

NIST_SC8 = Control("NIST SP 800-53", "Rev. 5 (Release 5.2.0)", "SC-8",
                   "Transmission Confidentiality and Integrity", "Sent in readable form.")
TEST_ROW = Control("PCI DSS", "4.0.1", "TEST-1", "Made-up row for tests", "Not a real control.")


def finding(title="Telnet session in cleartext", severity="high", dst_port=23,
            controls=(), sentences=()) -> Finding:
    """A small Finding built through Contract 1, so the tests follow the real shape."""
    return Finding(
        rule_id="cleartext.telnet", title=title, severity=severity,
        src_ip="10.0.0.5", dst_ip="10.0.0.9", dst_port=dst_port, protocol="telnet",
        first_seen=1791250285.789302, last_seen=1791250285.789302,
        evidence=[Evidence("maxguard_cleartext.log", "C1", 1791250285.789302,
                           "aab5e36795eaa77e")],
        controls=list(controls), explanation_sentences=list(sentences),
    )


def make_report(*findings: Finding, ai_status: str = "disabled") -> dict:
    """A report dict with the maxguard.report/2 keys the exporters read."""
    return {
        "schema": "maxguard.report/2",
        "input": {"name": "telnet.pcap", "sha256": "ab" * 32, "adapter": "pcap"},
        "tools": {"zeek": True, "suricata": False},
        "frameworks": [],
        "findings": [f.to_dict() for f in findings],
        "assets": [],
        "events": [],
        "ai": {"status": ai_status, "model": None, "explained": 0, "dropped_sentences": 0},
    }


def csv_data_rows(text: str) -> list[dict]:
    return list(csv.DictReader(io.StringIO(text)))


# ---------------------------------------------------------------- JSON

def test_json_round_trips():
    report = make_report(finding(controls=[NIST_SC8]))
    assert json.loads(to_json(report)) == report


def test_json_text_does_not_depend_on_key_order():
    # Same content, keys inserted in a different order -> the same text.
    report = make_report(finding())
    reordered = dict(reversed(list(report.items())))
    assert to_json(reordered) == to_json(report)


# ---------------------------------------------------------------- CSV

def test_csv_header_is_the_column_list():
    header = to_csv(make_report()).splitlines()[0]
    assert header.split(",") == CSV_COLUMNS


def test_csv_has_one_row_per_control():
    rows = csv_data_rows(to_csv(make_report(finding(controls=[NIST_SC8, TEST_ROW]))))
    assert [r["control_id"] for r in rows] == ["SC-8", "TEST-1"]
    assert rows[0]["framework"] == "NIST SP 800-53"
    assert rows[0]["control_title"] == "Transmission Confidentiality and Integrity"


def test_csv_keeps_a_finding_without_controls():
    rows = csv_data_rows(to_csv(make_report(finding())))
    assert len(rows) == 1
    assert rows[0]["rule_id"] == "cleartext.telnet"
    assert rows[0]["framework"] == rows[0]["control_id"] == ""


def test_csv_times_are_utc_and_evidence_ids_are_listed():
    row = csv_data_rows(to_csv(make_report(finding())))[0]
    assert row["first_seen"] == "2026-10-06T01:31:25Z"
    assert row["evidence_record_ids"] == "aab5e36795eaa77e"


def test_csv_stops_spreadsheet_formulas():
    row = csv_data_rows(to_csv(make_report(finding(title="=HYPERLINK(\"x\")"))))[0]
    assert row["title"] == "'=HYPERLINK(\"x\")"


# ---------------------------------------------------------------- HTML

def test_html_escapes_every_value():
    evil = finding(
        title="<script>alert(1)</script>",
        controls=[Control("NIST SP 800-53", "v", "<b>X</b>", "<i>t</i>", "r")],
        sentences=[Sentence("<img src=x onerror=alert(1)>", ["aab5e36795eaa77e"])],
    )
    page = to_html(make_report(evil, ai_status="ok"))
    assert "<script" not in page
    assert "<img" not in page
    assert "<b>X</b>" not in page
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in page


def test_html_loads_nothing_from_outside():
    page = to_html(make_report(finding(controls=[NIST_SC8])))
    for forbidden in ("<script", "<link", "<img", "<iframe", "src=", "@import", "url("):
        assert forbidden not in page
    assert "Content-Security-Policy" in page


def test_html_totals_by_severity():
    page = to_html(make_report(finding(), finding(severity="medium", dst_port=24),
                               finding(severity="medium", dst_port=25)))
    assert '<td class="sev sev-high">high</td><td>1</td>' in page
    assert '<td class="sev sev-medium">medium</td><td>2</td>' in page
    assert '<td class="sev sev-critical">critical</td><td>0</td>' in page
    assert "<tr><th>Total</th><th>3</th></tr>" in page


def test_html_lists_ten_findings_most_severe_first():
    findings = [finding(title=f"Low {i:02d}", severity="low", dst_port=i) for i in range(11)]
    findings.append(finding(title="The high one", severity="high", dst_port=99))
    page = to_html(make_report(*findings))
    assert page.index("The high one") < page.index("Low 00")
    assert "Low 08" in page
    assert "Low 09" not in page  # 1 high + Low 00..08 = the top 10


def test_html_names_affected_frameworks_only():
    page = to_html(make_report(finding(controls=[NIST_SC8])))
    assert "<td>NIST SP 800-53</td><td>Rev. 5 (Release 5.2.0)</td><td>1</td><td>SC-8</td>" in page
    assert "PCI DSS" not in page


def test_html_shows_ai_sentences_with_their_record_ids():
    cited = finding(sentences=[Sentence("Telnet sent the login in cleartext.",
                                        ["aab5e36795eaa77e"])])
    page = to_html(make_report(cited, ai_status="ok"))
    assert "Telnet sent the login in cleartext." in page
    assert "[evidence: <code>aab5e36795eaa77e</code>]" in page


def test_html_explains_when_ai_was_off():
    page = to_html(make_report(finding(), ai_status="unavailable"))
    assert "could not be reached" in page


def test_html_is_the_same_every_time():
    report = make_report(finding(controls=[NIST_SC8]))
    assert to_html(report) == to_html(json.loads(to_json(report)))


# ---------------------------------------------------------------- real pipeline output

def test_exports_for_the_telnet_fixture(tmp_path):
    report = analyze(FIXTURES / "telnet", tmp_path, explain=False)
    rows = csv_data_rows(to_csv(report))
    assert {r["rule_id"] for r in rows} == {"cleartext.telnet"}
    assert "SC-8" in {r["control_id"] for r in rows}
    page = to_html(report)
    assert "Telnet session in cleartext" in page
    assert json.loads(to_json(report))["schema"] == "maxguard.report/2"
