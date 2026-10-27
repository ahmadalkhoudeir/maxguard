"""Save an IPv6 version of the plain_http fixture into a running server's data folder.
Usage: python add_ipv6.py <repo> <data_dir> <workdir>"""
import shutil, sys, tempfile
from pathlib import Path
repo, data_dir, work = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
sys.path.insert(0, str(repo))
from maxguard.pipeline import analyze
from maxguard.storage.state import StateStore
logs = work / "logs6"
shutil.rmtree(logs, ignore_errors=True)
shutil.copytree(repo / "tests/fixtures/zeek/plain_http", logs)
for f in logs.iterdir():  # documentation prefix 2001:db8::/32 (RFC 3849)
    f.write_text(f.read_text().replace("172.18.0.3", "2001:db8:1234:5678:9abc:def0:1234:5678")
                 .replace("172.18.0.2", "2001:db8:abcd:ef01:2345:6789:abcd:ef02"))
report = analyze(logs, tempfile.mkdtemp(dir=work), explain=False)
store = StateStore(data_dir / "state.db")
print(store.save_analysis(report, received_at=1791300005.0), report["findings"][0]["finding_id"])
