"""Upload a zip of the Telnet fixture logs whose one record has ts=1e12, then open the pages.
Adapted from dash-review/scripts/far_future_upload.py: the build is an argument (it goes on
sys.path), and /alerts/<id> is only asked for on builds that have it.
Usage: python far_future_upload.py <build>"""
import io
import json
import sys
import tempfile
import zipfile
from pathlib import Path

build = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(build))
from fastapi.testclient import TestClient  # noqa: E402

from maxguard.api.app import create_app  # noqa: E402

fixture = build / "tests/fixtures/zeek/telnet"
buf = io.BytesIO()
with zipfile.ZipFile(buf, "w") as z:
    for f in sorted(fixture.iterdir()):
        text = f.read_text()
        if f.name == "maxguard_cleartext.log":
            rec = json.loads(text.splitlines()[0])
            rec["ts"] = 1e12
            text = json.dumps(rec) + "\n"
        z.writestr(f"telnet/{f.name}", text)
app = create_app(tempfile.mkdtemp(), explain=False)
c = TestClient(app, base_url="http://127.0.0.1", raise_server_exceptions=False)
r = c.post("/api/analyses", files={"file": ("logs.zip", buf.getvalue(), "application/zip")})
print("upload:", r.status_code, r.text[:300])
q = c.get("/")
print("GET / :", q.status_code, "| shows '(not a valid time)':", "(not a valid time)" in q.text)
fid = app.state.state_store.list_alerts()[0]["finding_id"]
if (build / "maxguard/web/templates/alert.html").exists():
    d = c.get(f"/alerts/{fid}")
    print(f"GET /alerts/{fid} :", d.status_code, "| shows '(not a valid time)':",
          d.text.count("(not a valid time)"), "times")
print("GET /api/alerts :", c.get("/api/alerts").status_code)
try:
    TestClient(app, base_url="http://127.0.0.1").get("/")
    print("GET / with server exceptions raised: no exception")
except Exception as e:  # noqa: BLE001
    import traceback
    tb = traceback.extract_tb(e.__traceback__)
    print("exception:", type(e).__name__, e, "| raised in",
          tb[-1].filename.split("maxguard/")[-1], tb[-1].lineno, tb[-1].name)
