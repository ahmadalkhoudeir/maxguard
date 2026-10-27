"""Server-side cases for the stale-form logic in PATCH /alerts/{id}/status.
Run from a build folder: PYTHONPATH=. python stale_cases.py"""
import re, tempfile
from pathlib import Path
from fastapi.testclient import TestClient
from maxguard.api.app import create_app
from maxguard.pipeline import analyze

app = create_app(tempfile.mkdtemp(), explain=False)
store = app.state.state_store
for i, name in enumerate(["telnet", "ftp"]):
    store.save_analysis(analyze(Path("tests/fixtures/zeek") / name, tempfile.mkdtemp(), explain=False),
                        received_at=1791300000.0 + i)
a, b = [x["finding_id"] for x in store.list_alerts()]
c = TestClient(app, base_url="http://127.0.0.1")

def reset(fid=a, status="new", assignee=""):
    store.update_alert(fid, actor="setup", at=1.0, status=status, assignee=assignee)

def patch(data=None, files=None, fid=a, cookie="Ahmad"):
    c.cookies.set("mg_actor", cookie) if cookie else c.cookies.clear()
    r = c.patch(f"/alerts/{fid}/status", data=data, files=files)
    alert = store.get_alert(fid)
    msg = re.search(r'class="message"[^>]*>([^<]*)<', r.text)
    hidden = re.findall(r'name="(shown_\w+)" value="([^"]*)"', r.text)
    return f"{r.status_code} {msg.group(1) if msg else ''!r} -> stored {alert['status']}/{alert['assignee'] or '-'} | form hidden {hidden}"

reset()
print("old client, no hidden fields, status=resolved:     ", patch({"status": "resolved", "assignee": ""}))
reset(); reset(b, status="investigating")
print("hidden fields of alert B (investigating) sent to A:", patch({"status": "investigating", "shown_status": "investigating",
                                                                      "assignee": "", "shown_assignee": ""}))
reset(status="investigating")
print("shown_status with spaces ' new ', status new:       ", patch({"status": "new", "shown_status": " new ", "assignee": "", "shown_assignee": ""}))
reset(assignee="Fiona")
print("assignee cleared on purpose:                       ", patch({"status": "new", "shown_status": "new", "assignee": "", "shown_assignee": "Fiona"}))
reset(assignee="Bob")  # another analyst set Bob after this form was opened (it showed "")
print("stale assignee, only the status changed:           ", patch({"status": "resolved", "shown_status": "new", "assignee": "", "shown_assignee": ""}))
reset(status="investigating")  # changed meanwhile; this person keeps "new" (what they saw)
print("status equal to shown, changed meanwhile:          ", patch({"status": "new", "shown_status": "new", "assignee": "", "shown_assignee": ""}))
reset()
print("shown_status sent as a file upload:                ", patch({"status": "new", "assignee": "", "shown_assignee": ""},
                                                                    files={"shown_status": ("x.txt", b"new", "text/plain")}))
reset()
print("shown_assignee sent as a file upload:              ", patch({"status": "new", "shown_status": "new", "assignee": ""},
                                                                    files={"shown_assignee": ("x.txt", b"", "text/plain")}))
reset()
print("no name yet (400):                                 ", patch({"actor": "   ", "status": "resolved", "shown_status": "new",
                                                                      "assignee": "Ali", "shown_assignee": ""}, cookie=None))
print("retry with a name, same choices:                   ", patch({"actor": "Ahmad", "status": "resolved", "shown_status": "new",
                                                                      "assignee": "Ali", "shown_assignee": ""}, cookie=None))
print("audit (newest first):", [(r["actor"], r["details"]) for r in store.list_audit(limit=3)])
