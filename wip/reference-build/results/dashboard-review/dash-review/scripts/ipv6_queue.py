"""Render the queue and alert page for an IPv6 version of the plain_http fixture.
Usage: python ipv6_queue.py <repo> <workdir>"""
import re, shutil, sys
from pathlib import Path
repo, work = Path(sys.argv[1]), Path(sys.argv[2])
sys.path.insert(0, str(repo))
from fastapi.testclient import TestClient
from maxguard.api.app import create_app
from maxguard.pipeline import analyze
logs = work / "logs6"
shutil.rmtree(logs, ignore_errors=True)
shutil.copytree(repo / "tests/fixtures/zeek/plain_http", logs)
for f in logs.iterdir():  # documentation prefix 2001:db8::/32 (RFC 3849)
    f.write_text(f.read_text().replace("172.18.0.3", "2001:db8::3").replace("172.18.0.2", "2001:db8::2"))
report = analyze(logs, work / "w6", explain=False)
app = create_app(work / "data6", explain=False)
app.state.state_store.save_analysis(report, received_at=1791300000.0)
c = TestClient(app, base_url="http://127.0.0.1")
f = report["findings"][0]
print("finding:", f["src_ip"], f["dst_ip"], f["dst_port"])
print("queue cell:", re.search(r'<td data-label="Source → destination" class="mono">([^<]*)</td>', c.get("/").text).group(1))
page = c.get(f"/alerts/{f['finding_id']}").text
print("alert page:", " ".join(re.search(r'<dt>Source → destination</dt>\s*<dd class="mono">(.*?)</dd>', page, re.S).group(1).split()))
