"""CSV formula-injection checks on maxguard.report.to_csv.

python csv_checks.py <repo> <end-to-end csv file>
"""

from __future__ import annotations

import csv
import io
import sys
from pathlib import Path

repo, e2e = Path(sys.argv[1]), Path(sys.argv[2])
sys.path.insert(0, str(repo))

from maxguard.models import Control, Evidence, Finding  # noqa: E402
from maxguard.report import CSV_COLUMNS, FORMULA_STARTS, to_csv  # noqa: E402

print("FORMULA_STARTS =", FORMULA_STARTS)
PREFIXES = {"=": "=1+1", "+": "+1+1", "-": "-1+1", "@": "@SUM(1,1)", "tab": "\t=1+1",
            "CR": "\r=1+1", "LF": "\n=1+1", "CRLF": "\r\n=1+1"}
results = []


def report_with(**fields) -> dict:
    f = Finding(rule_id="cleartext.telnet", title="t", severity="high", src_ip="10.0.0.5",
                dst_ip="10.0.0.9", dst_port=23, protocol="telnet", first_seen=1.0, last_seen=1.0,
                evidence=[Evidence("x.log", "C1", 1.0, "aab5e36795eaa77e")],
                controls=[Control("PCI DSS", "4.0.1", "T-1", "t", "r")])
    d = f.to_dict()
    for key, value in fields.items():
        if key.startswith("control_"):
            d["controls"][0][key[len("control_"):]] = value
        else:
            d[key] = value
    return {"findings": [d]}


# 1) every dangerous prefix in every text column that can be set
columns = {"title": "title", "src_ip": "src_ip", "dst_ip": "dst_ip", "rule_id": "rule_id",
           "protocol": "protocol", "finding_id": "finding_id", "severity": "severity",
           "framework": "control_framework", "control_id": "control_control_id",
           "control_title": "control_title", "rationale": "control_rationale",
           "version": "control_version"}
for column, key in columns.items():
    for name, value in PREFIXES.items():
        row = next(csv.DictReader(io.StringIO(to_csv(report_with(**{key: value})))))
        ok = row[column] == "'" + value
        results.append(ok)
        if not ok:
            print(f"FAIL {column} {name}: {row[column]!r}")
print(f"prefix matrix: {sum(results)}/{len(results)} cells got the leading quote "
      f"({len(columns)} columns x {len(PREFIXES)} prefixes)")

# numbers: a negative port or count is quoted too
row = next(csv.DictReader(io.StringIO(to_csv(report_with(dst_port=-1, count=-5)))))
print("negative numbers:", repr(row["dst_port"]), repr(row["count"]))

# 2) a cell cannot be split into a new cell: the csv module quotes , " CR LF
text = to_csv(report_with(title='a,=1+1', src_ip='x"=1+1'))
line = text.splitlines()[1]
print("comma/quote in a value stay in one cell:", line[:80])
row = next(csv.DictReader(io.StringIO(text)))
print("   parsed back:", repr(row["title"]), repr(row["src_ip"]))

# 3) values that do NOT start with a listed character are left alone
for value in (" =1+1", " =1+1", "＝1+1", "|calc", "%0A=1+1"):
    row = next(csv.DictReader(io.StringIO(to_csv(report_with(title=value)))))
    print("not prefixed:", repr(value), "->", repr(row["title"]))

# 4) the end-to-end CSV written by `maxguard analyze --format csv` on the hostile logs
rows = list(csv.DictReader(e2e.open(newline="")))
starts = {c: [r[c][:1] for r in rows] for c in CSV_COLUMNS}
bad = [(c, r[c]) for r in rows for c in CSV_COLUMNS if r[c][:1] in "=+-@\t\r\n"]
print(f"end-to-end CSV: {len(rows)} rows; cells starting with a formula character: {bad}")
title = next(r["title"] for r in rows if r["rule_id"] == "tls.weak_cipher")
print("   weak-cipher title cell:", repr(title))

# 5) the same file read with ';' as the separator (spreadsheets in locales whose list
#    separator is ';' split CSV lines on ';'). Simulation only: no spreadsheet app here.
semi = [cell for line in csv.reader(e2e.open(newline=""), delimiter=";") for cell in line]
formula_cells = [c for c in semi if c[:1] in "=+-@"]
print("   read with delimiter ';' -> cells starting with = + - @:", formula_cells)
