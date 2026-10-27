"""Add synthetic alerts (copies of the Telnet finding with another severity) to a data folder.
Usage: python add_alerts.py <repo> <data_dir> <severity>[,<severity>...]"""
import copy, sys, tempfile
from pathlib import Path
repo, data_dir, sevs = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3].split(",")
sys.path.insert(0, str(repo))
from maxguard.models import make_finding_id
from maxguard.pipeline import analyze
from maxguard.storage.state import StateStore
report = analyze(repo / "tests/fixtures/zeek/telnet", tempfile.mkdtemp(), explain=False)
base = report["findings"][0]
report["findings"] = []
for i, sev in enumerate(sevs):
    f = copy.deepcopy(base)
    f["severity"], f["dst_ip"] = sev, f"10.9.9.{i + 1}"
    f["finding_id"] = make_finding_id(f["rule_id"], f["src_ip"], f["dst_ip"], f["dst_port"])
    report["findings"].append(f)
report["input"]["sha256"] = "2" * 64
print(StateStore(data_dir / "state.db").save_analysis(report, received_at=1791400000.0 + len(sevs)))
