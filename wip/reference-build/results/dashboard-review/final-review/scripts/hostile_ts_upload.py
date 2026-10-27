"""Upload the Telnet fixture logs as a zip with one hostile ts in maxguard_cleartext.log,
then fetch the dashboard pages. Usage (from a build folder):
    python hostile_ts_upload.py <ts literal as written in the JSON log, e.g. 1e400>"""
import io, json, sys, tempfile, zipfile
from pathlib import Path
from fastapi.testclient import TestClient
from maxguard.api.app import create_app

literal = sys.argv[1]
fixture = Path("tests/fixtures/zeek/telnet")
buf = io.BytesIO()
with zipfile.ZipFile(buf, "w") as z:
    for f in sorted(fixture.iterdir()):
        text = f.read_text()
        if f.name == "maxguard_cleartext.log":
            rec = json.loads(text.splitlines()[0])
            rec["ts"] = "@@TS@@"
            text = json.dumps(rec).replace('"@@TS@@"', literal) + "\n"
        z.writestr(f"telnet/{f.name}", text)
app = create_app(tempfile.mkdtemp(), explain=False)
c = TestClient(app, base_url="http://127.0.0.1", raise_server_exceptions=False)
r = c.post("/api/analyses", files={"file": ("logs.zip", buf.getvalue(), "application/zip")})
print(f"ts={literal}: upload", r.status_code, r.text[:200])
alerts = app.state.state_store.list_alerts()
if not alerts:
    sys.exit("no alert stored")
a = alerts[0]
print("stored last_seen:", repr(a["last_seen"]), "| evidence ts:", [e.get("ts") for e in a["evidence"]])
paths = ["/", f"/alerts/{a['finding_id']}", "/api/alerts", f"/api/alerts/{a['finding_id']}"]
if Path("maxguard/web/templates/timeline.html").exists():
    paths += [f"/timeline?ip={a['src_ip']}", "/assets"]
for mode in ("analyst", "home"):
    c.cookies.set("mg_mode", mode)
    for p in paths:
        resp = c.get(p)
        print(f"  {mode:7} GET {p}: {resp.status_code}")
c.cookies.set("mg_mode", "analyst")
strict = TestClient(app, base_url="http://127.0.0.1")
try:
    strict.get(f"/alerts/{a['finding_id']}")
except Exception as e:
    import traceback
    tb = traceback.extract_tb(e.__traceback__)
    frames = [f"{fr.filename.split('/')[-1]}:{fr.lineno}" for fr in tb[-3:]]
    print("  exception on the alert page:", type(e).__name__, e, "| last frames", frames)
