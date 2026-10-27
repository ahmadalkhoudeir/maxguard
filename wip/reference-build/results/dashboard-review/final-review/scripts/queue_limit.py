"""QUEUE_LIMIT boundary and caption. Run from a build folder with PYTHONPATH=."""
import re, subprocess, sys, tempfile
from pathlib import Path
from fastapi.testclient import TestClient
from maxguard.api.app import create_app

W = Path(sys.argv[1])
def queue(data, **params):
    c = TestClient(create_app(data, explain=False), base_url="http://127.0.0.1")
    page = c.get("/", params=params).text
    cap = re.search(r"<caption>(.*?)</caption>", page, re.S)
    return page.count('<a id="alert-'), cap.group(1) if cap else None

for n in (200, 201):
    data = tempfile.mkdtemp()
    subprocess.run([sys.executable, str(W / "scripts/add_alerts.py"), ".", data, "low", str(n)], check=True,
                   capture_output=True)
    rows, cap = queue(data)
    print(f"{n} alerts, no filter: {rows} rows | caption: {cap!r}")
    if n == 201:
        rows, cap = queue(data, status="new", severity="low")
        print(f"{n} alerts, status=new & severity=low (the narrowest filters): {rows} rows | caption: {cap!r}")
        for mode in ("home",):
            c = TestClient(create_app(data, explain=False), base_url="http://127.0.0.1")
            c.cookies.set("mg_mode", mode)
            print(f"  {mode} mode caption:", re.search(r"<caption>(.*?)</caption>", c.get("/").text, re.S).group(1))
