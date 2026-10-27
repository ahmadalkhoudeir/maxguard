"""More than QUEUE_LIMIT alerts of mixed severity: what does the caption claim, and
what is the real order of the rows? Run: python s6_caption.py <build>"""
import copy, re, sys, tempfile
from pathlib import Path
repo = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(repo))
from fastapi.testclient import TestClient
from maxguard.api.app import create_app
from maxguard.models import make_finding_id
from maxguard.pipeline import analyze

app = create_app(tempfile.mkdtemp(), explain=False)
store = app.state.state_store
report = analyze(repo / "tests/fixtures/zeek/telnet", tempfile.mkdtemp(), explain=False)
base = report["findings"][0]
report["findings"] = []
n = 0
# 50 of each severity; last_seen goes UP with n, so the newest alerts are the info ones
for sev in ("critical", "high", "medium", "low", "info"):  # the newest alert is an info one
    for _ in range(50):
        n += 1
        f = copy.deepcopy(base)
        f["severity"], f["dst_ip"] = sev, f"10.0.{n // 250}.{n % 250 + 1}"
        f["last_seen"] = f["first_seen"] = 1791300000.0 + n
        f["finding_id"] = make_finding_id(f["rule_id"], f["src_ip"], f["dst_ip"], f["dst_port"])
        report["findings"].append(f)
report["input"]["sha256"] = f"{n:064x}"
store.save_analysis(report, received_at=1791400000.0)
client = TestClient(app, base_url="http://127.0.0.1")
for path in ("/", "/?status=new", "/?status=new&severity=critical", "/?status=new&severity=low"):
    page = client.get(path).text
    caption = re.search(r"<caption>(.*?)</caption>", page, re.S).group(1)
    sevs = re.findall(r'<span class="sev sev-(\w+)">', page)
    seen = re.findall(r'<td data-label="Last seen">([^<]*)</td>', page)
    print(f"{path}: rows={len(sevs)} first severities={sevs[:3]} last={sevs[-2:]}")
    print(f"   caption: {caption!r}")
    print(f"   last seen of row 1 / row 2 / last row: {seen[0]} / {seen[1]} / {seen[-1]}")
    print(f"   sorted most-recent-first? {seen == sorted(seen, reverse=True)}; "
          f"most-severe-first? {sevs == sorted(sevs, key=['critical','high','medium','low','info'].index)}")
