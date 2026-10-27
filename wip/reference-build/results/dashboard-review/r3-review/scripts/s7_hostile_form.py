"""Hostile and odd clients against PATCH /alerts/{id}/status and the alert page.
Run: python s7_hostile_form.py <build>"""
import re, sys, tempfile
from pathlib import Path
repo = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(repo))
from fastapi.testclient import TestClient
from maxguard.api.app import create_app
from maxguard.pipeline import analyze

app = create_app(tempfile.mkdtemp(), explain=False)
store = app.state.state_store
store.save_analysis(analyze(repo / "tests/fixtures/zeek/telnet", tempfile.mkdtemp(), explain=False),
                    received_at=1791300000.0)
fid = store.list_alerts()[0]["finding_id"]
c = TestClient(app, base_url="http://127.0.0.1")
c.cookies.set("mg_actor", "Ahmad")


def show(label, r):
    a = store.get_alert(fid)
    msg = re.search(r'class="message"[^>]*>([^<]*)<', r.text)
    audit = store.list_audit(limit=1)
    print(f"{label}\n   -> {r.status_code} {msg.group(1) if msg else ''!r}; stored status={a['status']!r} "
          f"assignee={a['assignee']!r}; newest audit={audit[0]['details'] if audit else None}")


def reset(status="new", assignee=""):
    store.update_alert(fid, actor="setup", at=1.0, status=status, assignee=assignee)


reset(status="investigating")
r = c.patch(f"/alerts/{fid}/status", data=[("status", "new"), ("shown_status", "investigating"),
                                           ("shown_status", "new"), ("assignee", ""), ("shown_assignee", "")])
show("1. shown_status sent twice (investigating, new), status=new, stored=investigating", r)

reset(status="investigating")
r = c.patch(f"/alerts/{fid}/status", data=[("status", "new"), ("shown_status", "new"),
                                           ("shown_status", "investigating"), ("assignee", ""), ("shown_assignee", "")])
show("2. shown_status sent twice (new, investigating), status=new, stored=investigating", r)

reset()
r = c.patch(f"/alerts/{fid}/status", data={"status": "resolved", "assignee": "", "shown_assignee": ""},
            files={"shown_status": ("x.txt", b"new", "text/plain")})
show("3. shown_status as a file part, status=resolved", r)

reset()
r = c.patch(f"/alerts/{fid}/status", data={"status": "new", "shown_status": "new", "shown_assignee": ""},
            files={"assignee": ("x.txt", b"Mallory", "text/plain")})
show("4. assignee as a file part (text_field on an UploadFile)", r)

reset(assignee="Fiona")
r = c.patch(f"/alerts/{fid}/status", data={"status": "new", "shown_status": "new", "assignee": "Fiona"},
            files={"shown_assignee": ("x.txt", b"Fiona", "text/plain")})
show("5. shown_assignee as a file part, assignee unchanged (Fiona)", r)

# an assignee longer than the form's 100 characters, set through the JSON API's own 100 limit? no:
# the API caps at 100 too, so set it through the store (a future importer, an older version)
long_name = "L" * 120
reset(assignee=long_name)
page = c.get(f"/alerts/{fid}").text
hidden = re.search(r'name="shown_assignee" value="([^"]*)"', page).group(1)
box = re.search(r'id="assignee"[^>]*value="([^"]*)"', page).group(1)
print(f"6. stored assignee of 120 chars: hidden field holds {len(hidden)} chars, text box {len(box)} chars")
r = c.patch(f"/alerts/{fid}/status", data={"status": "investigating", "shown_status": "new",
                                           "assignee": long_name, "shown_assignee": long_name})
show("   status-only save (the browser sends the 120-char value back unchanged)", r)

reset()
r = c.patch(f"/alerts/{fid}/status", data={"status": "new", "shown_status": "new",
                                           "assignee": "Ann\x00Lee", "shown_assignee": ""})
show("7. assignee with a NUL byte", r)

reset()
r = c.patch(f"/alerts/{fid}/status", data={"status": "new", "shown_status": "new",
                                           "assignee": " Ann", "shown_assignee": ""})
show("8. assignee with U+2028 LINE SEPARATOR", r)

# title escaping: a title that tries to close <title>
report = analyze(repo / "tests/fixtures/zeek/ftp", tempfile.mkdtemp(), explain=False)
report["findings"][0]["title"] = '</title><script>alert(1)</script><title>'
store.save_analysis(report, received_at=1791300001.0)
fid2 = report["findings"][0]["finding_id"]
page = c.get(f"/alerts/{fid2}").text
print("9. <title> with a hostile alert title:", re.search(r"<title>.*?</title>", page, re.S).group(0)[:120])
print("   raw '</title>' in page:", "</title><script>" in page)
