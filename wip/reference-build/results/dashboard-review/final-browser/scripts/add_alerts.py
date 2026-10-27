"""Add synthetic alerts (copies of the Telnet finding with another severity) to a data folder.
Adapted from dash-review/scripts/add_alerts.py: a third argument "octet" keeps the
destination addresses (and so the finding IDs and the input hash) of separate calls apart.
Usage: python add_alerts.py <repo> <data_dir> <severity>[,<severity>...] [octet]"""
import copy
import sys
import tempfile
from pathlib import Path

repo, data_dir, sevs = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3].split(",")
octet = int(sys.argv[4]) if len(sys.argv) > 4 else 9
sys.path.insert(0, str(repo))
from maxguard.models import make_finding_id  # noqa: E402
from maxguard.pipeline import analyze  # noqa: E402
from maxguard.storage.state import StateStore  # noqa: E402

report = analyze(repo / "tests/fixtures/zeek/telnet", tempfile.mkdtemp(), explain=False)
base = report["findings"][0]
report["findings"] = []
for i, sev in enumerate(sevs):
    f = copy.deepcopy(base)
    f["severity"], f["dst_ip"] = sev, f"10.9.{octet}.{i + 1}"
    f["finding_id"] = make_finding_id(f["rule_id"], f["src_ip"], f["dst_ip"], f["dst_port"])
    report["findings"].append(f)
report["input"]["sha256"] = f"{octet:02x}" * 32
print(StateStore(data_dir / "state.db").save_analysis(report, received_at=1791400000.0 + octet))
