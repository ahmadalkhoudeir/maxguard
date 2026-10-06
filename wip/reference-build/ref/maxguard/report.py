"""Report export (Amory): turn a report dict into JSON, CSV or HTML text.

The input is the dict that maxguard.pipeline.analyze() returns (schema
"maxguard.report/2"). Each function returns a string; the caller decides
where to save it. Nothing here reads the clock, so the same report always
gives exactly the same file (CLAUDE.md rule 2). Standard library only, so
exports work on an offline machine.
"""

from __future__ import annotations

import csv
import html
import io
import json
from datetime import UTC, datetime

from maxguard.models import SEVERITIES

TOP_FINDINGS = 10  # how many findings the HTML page lists in its table

# ---------------------------------------------------------------- JSON


def to_json(report: dict) -> str:
    """The whole report as JSON. Sorted keys make two exports easy to diff."""
    return json.dumps(report, sort_keys=True, indent=2) + "\n"


# ---------------------------------------------------------------- CSV

CSV_COLUMNS = [
    "finding_id", "rule_id", "severity", "title",
    "src_ip", "dst_ip", "dst_port", "protocol",
    "count", "first_seen", "last_seen",
    "framework", "version", "control_id", "control_title", "rationale",
    "evidence_record_ids",
]

# A spreadsheet app runs a cell that starts with one of these as a formula.
# Titles and hosts can come from network traffic, so an attacker could plant
# "=HYPERLINK(...)". OWASP's advice: put a single quote in front of such cells.
# https://owasp.org/www-community/attacks/CSV_Injection
FORMULA_STARTS = ("=", "+", "-", "@", "\t", "\r", "\n")


def to_csv(report: dict) -> str:
    """One row per finding per control, for spreadsheets and auditors.

    A finding with no controls still gets one row (with empty control
    columns), so no finding ever disappears from the export.
    """
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=CSV_COLUMNS)
    writer.writeheader()
    for finding in report.get("findings", []):
        for row in csv_rows(finding):
            writer.writerow({column: safe_cell(row[column]) for column in CSV_COLUMNS})
    return out.getvalue()


def csv_rows(finding: dict) -> list[dict]:
    """The CSV rows for one finding: one per control, or one with no control."""
    base = {
        "finding_id": finding["finding_id"],
        "rule_id": finding["rule_id"],
        "severity": finding["severity"],
        "title": finding["title"],
        "src_ip": finding["src_ip"],
        "dst_ip": finding["dst_ip"],
        "dst_port": finding["dst_port"],
        "protocol": finding["protocol"],
        "count": finding["count"],
        "first_seen": iso_utc(finding["first_seen"]),
        "last_seen": iso_utc(finding["last_seen"]),
        "evidence_record_ids": " ".join(evidence_ids(finding)),
    }
    controls = finding.get("controls") or [None]  # [None] -> one row, empty columns
    return [{**base, **control_columns(control)} for control in controls]


def control_columns(control: dict | None) -> dict:
    """The five control columns of a CSV row ("" when there is no control)."""
    if control is None:
        return {"framework": "", "version": "", "control_id": "",
                "control_title": "", "rationale": ""}
    return {
        "framework": control["framework"],
        "version": control["version"],
        "control_id": control["control_id"],
        "control_title": control["title"],
        "rationale": control["rationale"],
    }


def safe_cell(value: object) -> str:
    """Text for one CSV cell, made safe to open in a spreadsheet app."""
    text = "" if value is None else str(value)
    if text.startswith(FORMULA_STARTS):
        return "'" + text
    return text


# ---------------------------------------------------------------- helpers


def iso_utc(ts: float) -> str:
    """Epoch seconds -> '2026-10-06T01:02:03Z'. Converts a stored time; never reads the clock."""
    return datetime.fromtimestamp(float(ts), tz=UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def evidence_ids(finding: dict) -> list[str]:
    """The record IDs of a finding's evidence, in order."""
    return [ev["record_id"] for ev in finding.get("evidence", []) if ev.get("record_id")]


def by_severity(findings: list[dict]) -> list[dict]:
    """Most severe first. The sort is stable, so ties keep the report's order."""
    return sorted(findings, key=lambda f: SEVERITIES.index(f["severity"]))


def esc(value: object) -> str:
    """HTML-escape any value. Every piece of report data goes through this,
    because titles, hosts and AI sentences can contain text from the network."""
    return html.escape("" if value is None else str(value), quote=True)


# ---------------------------------------------------------------- HTML

# The page loads nothing from outside: no fonts, no scripts, no images.
# The CSP line below makes the browser enforce that, even if a later edit
# adds a link by mistake. Only the inline <style> block is allowed.
CSP = "default-src 'none'; style-src 'unsafe-inline'"

STYLE = """
body { font-family: system-ui, sans-serif; margin: 0; color: #1a1a1a; background: #fff; }
main { max-width: 960px; margin: 0 auto; padding: 16px; }
table { border-collapse: collapse; width: 100%; margin: 8px 0 16px; }
th, td { border: 1px solid #ccc; padding: 4px 8px; text-align: left; vertical-align: top; }
th { background: #f2f2f2; }
code { font-size: 0.9em; overflow-wrap: anywhere; }
.sev { font-weight: bold; text-transform: uppercase; }
.sev-critical { color: #8b0000; } .sev-high { color: #b22222; }
.sev-medium { color: #a0522d; } .sev-low { color: #2f4f4f; } .sev-info { color: #555; }
.note { color: #555; }
"""


def to_html(report: dict) -> str:
    """A standalone HTML page: totals, top findings, frameworks, AI sentences."""
    findings = by_severity(report.get("findings", []))
    sections = [
        html_head(report),
        html_summary(report, findings),
        html_severity_totals(findings),
        html_top_findings(findings),
        html_frameworks(findings),
        html_ai(report, findings),
        "</main>\n</body>\n</html>\n",
    ]
    return "\n".join(sections)


def html_head(report: dict) -> str:
    name = report.get("input", {}).get("name", "")
    return (
        "<!doctype html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        f"<meta http-equiv=\"Content-Security-Policy\" content=\"{CSP}\">\n"
        f"<title>MaxGuard report: {esc(name)}</title>\n"
        f"<style>{STYLE}</style>\n</head>\n<body>\n<main>\n"
        "<h1>MaxGuard report</h1>"
    )


def html_summary(report: dict, findings: list[dict]) -> str:
    source = report.get("input", {})
    tools = report.get("tools", {})
    rows = [
        ("Input", source.get("name", "")),
        ("SHA-256", source.get("sha256") or "(folder of logs, not hashed)"),
        ("Input type", source.get("adapter", "")),
        ("Zeek ran in this analysis", "yes" if tools.get("zeek") else "no"),
        ("Suricata output used", "yes" if tools.get("suricata") else "no"),
        ("Findings", len(findings)),
    ]
    cells = "\n".join(f"<tr><th>{esc(label)}</th><td>{esc(value)}</td></tr>"
                      for label, value in rows)
    return f"<h2>Summary</h2>\n<table>\n{cells}\n</table>"


def html_severity_totals(findings: list[dict]) -> str:
    """Number of findings per severity, every severity listed even when 0."""
    rows = []
    for severity in SEVERITIES:
        total = sum(1 for f in findings if f["severity"] == severity)
        rows.append(f"<tr><td class=\"sev sev-{esc(severity)}\">{esc(severity)}</td>"
                    f"<td>{total}</td></tr>")
    rows.append(f"<tr><th>Total</th><th>{len(findings)}</th></tr>")
    body = "\n".join(rows)
    return ("<h2>Findings by severity</h2>\n<table>\n"
            f"<tr><th>Severity</th><th>Findings</th></tr>\n{body}\n</table>")


def html_top_findings(findings: list[dict]) -> str:
    title = f"<h2>Top findings (most severe first, up to {TOP_FINDINGS})</h2>"
    if not findings:
        return f"{title}\n<p>No findings.</p>"
    header = ("<tr><th>#</th><th>Severity</th><th>Finding</th><th>Source</th>"
              "<th>Destination</th><th>Port</th><th>Count</th><th>Controls</th></tr>")
    rows = [html_finding_row(i, f) for i, f in enumerate(findings[:TOP_FINDINGS], start=1)]
    body = "\n".join(rows)
    return f"{title}\n<table>\n{header}\n{body}\n</table>"


def html_finding_row(number: int, f: dict) -> str:
    controls = "<br>".join(esc(line) for line in controls_by_framework(f)) or "none mapped"
    return (
        f"<tr><td>{number}</td>"
        f"<td class=\"sev sev-{esc(f['severity'])}\">{esc(f['severity'])}</td>"
        f"<td>{esc(f['title'])}<br><code>{esc(f['rule_id'])} {esc(f['finding_id'])}</code></td>"
        f"<td><code>{esc(f['src_ip'])}</code></td><td><code>{esc(f['dst_ip'])}</code></td>"
        f"<td>{esc(f['dst_port'])}/{esc(f['protocol'])}</td><td>{esc(f['count'])}</td>"
        f"<td>{controls}</td></tr>"
    )


def controls_by_framework(finding: dict) -> list[str]:
    """['NIST SP 800-53: SC-8, SC-8(1)', ...], frameworks in the order they appear."""
    ids: dict[str, list[str]] = {}
    for control in finding.get("controls", []):
        ids.setdefault(control["framework"], []).append(control["control_id"])
    return [f"{framework}: {', '.join(control_ids)}" for framework, control_ids in ids.items()]


def frameworks_affected(findings: list[dict]) -> dict[tuple[str, str], dict]:
    """(framework, version) -> {"controls": [...], "findings": n} for frameworks with hits."""
    affected: dict[tuple[str, str], dict] = {}
    for f in findings:
        hit_here: set[tuple[str, str]] = set()
        for control in f.get("controls", []):
            key = (control["framework"], control["version"])
            entry = affected.setdefault(key, {"controls": [], "findings": 0})
            if control["control_id"] not in entry["controls"]:
                entry["controls"].append(control["control_id"])
            hit_here.add(key)
        for key in hit_here:  # count each finding once per framework
            affected[key]["findings"] += 1
    return affected


def html_frameworks(findings: list[dict]) -> str:
    title = "<h2>Frameworks affected</h2>"
    # A framework with no rows here is NOT a pass: its mapping file may simply
    # have no checked rows yet. Say so, so nobody reads silence as compliance.
    note = ("<p class=\"note\">A framework that is not listed has no mapped controls for "
            "these findings. That does not mean the network meets that framework.</p>")
    affected = frameworks_affected(findings)
    if not affected:
        return f"{title}\n<p>No mapped controls.</p>\n{note}"
    rows = [
        f"<tr><td>{esc(framework)}</td><td>{esc(version)}</td><td>{entry['findings']}</td>"
        f"<td>{esc(', '.join(entry['controls']))}</td></tr>"
        for (framework, version), entry in affected.items()
    ]
    header = "<tr><th>Framework</th><th>Version</th><th>Findings</th><th>Controls</th></tr>"
    body = "\n".join(rows)
    return f"{title}\n<table>\n{header}\n{body}\n</table>\n{note}"


AI_STATUS_TEXT = {
    "ok": "Sentences from the local AI, each with the evidence records it cites. "
          "Sentences without valid citations were removed before this report was made.",
    "unavailable": "The local AI could not be reached, so there are no AI explanations.",
    "disabled": "AI explanations were turned off for this analysis.",
}


def html_ai(report: dict, findings: list[dict]) -> str:
    ai = report.get("ai", {})
    status = ai.get("status", "disabled")
    stats = (f"Model: <code>{esc(ai.get('model') or 'none')}</code>. "
             f"Findings explained: {esc(ai.get('explained', 0))}. "
             f"Sentences removed for bad citations: {esc(ai.get('dropped_sentences', 0))}.")
    lines = [
        "<h2>AI explanations</h2>",
        f"<p class=\"note\">{esc(AI_STATUS_TEXT.get(status, status))}</p>",
        f"<p class=\"note\">{stats}</p>",
    ]
    for f in findings:
        if f.get("explanation_sentences"):
            lines.append(html_ai_finding(f))
    return "\n".join(lines)


def html_ai_finding(f: dict) -> str:
    """One finding's AI sentences, each followed by the record IDs it cites."""
    items = []
    for sentence in f["explanation_sentences"]:
        cited = ", ".join(sentence.get("evidence_ids", []))
        items.append(f"<li>{esc(sentence['text'])} "
                     f"<span class=\"note\">[evidence: <code>{esc(cited)}</code>]</span></li>")
    body = "\n".join(items)
    return (f"<h3>{esc(f['title'])} <code>{esc(f['finding_id'])}</code></h3>\n"
            f"<ul>\n{body}\n</ul>")
