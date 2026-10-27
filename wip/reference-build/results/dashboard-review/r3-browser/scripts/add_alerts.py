"""Add synthetic alerts (copies of the Telnet finding) to a data folder.
Usage: python add_alerts.py <repo> <data_dir> <severity>[,<severity>...] [count-per-severity]
Each alert gets its own destination address, so its own finding_id."""
import copy, sys, tempfile
from pathlib import Path
repo, data_dir, sevs = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3].split(",")
per = int(sys.argv[4]) if len(sys.argv) > 4 else 1
sys.path.insert(0, str(repo))
from maxguard.models import make_finding_id
from maxguard.pipeline import analyze
from maxguard.storage.state import StateStore
report = analyze(repo / "tests/fixtures/zeek/telnet", tempfile.mkdtemp(), explain=False)
base = report["findings"][0]
report["findings"] = []
n = 0
for sev in sevs:
    for _ in range(per):
        n += 1
        f = copy.deepcopy(base)
        f["severity"], f["dst_ip"] = sev, f"10.{50 + n // 60000}.{(n // 250) % 240}.{n % 250 + 1}"
        f["finding_id"] = make_finding_id(f["rule_id"], f["src_ip"], f["dst_ip"], f["dst_port"])
        report["findings"].append(f)
report["input"]["sha256"] = f"{len(report['findings']):064x}"
store = StateStore(Path(data_dir) / "state.db")
print(store.save_analysis(report, received_at=1791400000.0 + n), "added", n)
