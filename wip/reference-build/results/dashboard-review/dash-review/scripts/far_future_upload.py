"""Upload a zip of the Telnet fixture logs whose one record has ts=1e12, then open the queue."""
import io, json, sys, zipfile, tempfile
from pathlib import Path
from fastapi.testclient import TestClient
from maxguard.api.app import create_app

fixture = Path("tests/fixtures/zeek/telnet")
buf = io.BytesIO()
with zipfile.ZipFile(buf, "w") as z:
    for f in sorted(fixture.iterdir()):
        text = f.read_text()
        if f.name == "maxguard_cleartext.log":
            rec = json.loads(text.splitlines()[0]); rec["ts"] = 1e12
            text = json.dumps(rec) + "\n"
        z.writestr(f"telnet/{f.name}", text)
app = create_app(tempfile.mkdtemp(), explain=False)
c = TestClient(app, base_url="http://127.0.0.1", raise_server_exceptions=False)
r = c.post("/api/analyses", files={"file": ("logs.zip", buf.getvalue(), "application/zip")})
print("upload:", r.status_code, r.text[:300])
print("GET / :", c.get("/").status_code)
fid = app.state.state_store.list_alerts()[0]["finding_id"]
print(f"GET /alerts/{fid} :", c.get(f"/alerts/{fid}").status_code)
print("GET /api/alerts :", c.get("/api/alerts").status_code)
try:
    TestClient(app, base_url="http://127.0.0.1").get("/")
except Exception as e:
    import traceback; tb = traceback.extract_tb(e.__traceback__)
    print("exception:", type(e).__name__, e, "| raised in", tb[-1].filename.split("maxguard/")[-1], tb[-1].lineno, tb[-1].name)
