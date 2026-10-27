"""AHM-04 row 9: attack the response module of a private ALL build on 127.0.0.1.

Starts the real console app (uvicorn create_app) and, for the ingest check, the
real ingest app, each on a free 127.0.0.1 port, with a fresh data folder per
scenario. Only synthetic addresses (RFC 5737 / RFC 3849) are proposed; nothing
is ever sent toward a proposed address (manual mode writes text only; the
enforcer talks only to the fake firewall in fakefw.py on 127.0.0.1).
"""
from __future__ import annotations

import concurrent.futures
import json
import os
import secrets
import socket
import subprocess
import sys
import threading
import time
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import fakefw  # noqa: E402

REPO = Path(sys.argv[1]).resolve()
WORK = Path(sys.argv[2]).resolve()
PY = sys.executable
BAD = "203.0.113.7"


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class Server:
    def __init__(self, name: str, factory: str, extra_env: dict):
        self.data = WORK / name / "data"
        self.data.mkdir(parents=True, exist_ok=True)
        self.port = free_port()
        env = {k: v for k, v in os.environ.items()
               if not k.startswith("MAXGUARD_") and k.lower() not in ("https_proxy", "http_proxy")}
        env.update({"PYTHONDONTWRITEBYTECODE": "1", "MAXGUARD_DATA_DIR": str(self.data),
                    "MAXGUARD_OFFLINE": "1", "OLLAMA_HOST": "http://127.0.0.1:9"})
        env.update(extra_env)
        self.log = open(WORK / name / "server.log", "w")
        self.proc = subprocess.Popen(
            [PY, "-m", "uvicorn", factory, "--factory", "--host", "127.0.0.1",
             "--port", str(self.port), "--log-level", "warning"],
            cwd=REPO, env=env, stdout=self.log, stderr=subprocess.STDOUT)
        self.base = f"http://127.0.0.1:{self.port}"
        self.http = requests.Session()
        self.http.trust_env = False
        for _ in range(100):
            try:
                self.http.get(self.base + "/api/ingest", timeout=1)
                break
            except requests.ConnectionError:
                time.sleep(0.1)

    def call(self, method, path, body=None, headers=None):
        r = self.http.request(method, self.base + path, json=body, headers=headers, timeout=60)
        try:
            data = r.json()
        except ValueError:
            data = r.text
        return r.status_code, data

    def audit(self):
        rows = self.call("GET", "/api/audit?limit=1000")[1]
        return [(r["action"], r["target"], r["details"]) for r in reversed(rows)
                if r["action"].startswith("response.")]

    def stop(self):
        self.proc.terminate()
        self.proc.wait(10)
        self.log.close()


def show(label, result):
    status, data = result
    text = json.dumps(data, sort_keys=True) if not isinstance(data, str) else data
    print(f"  {label}: HTTP {status} {text[:300]}")
    return status, data


def propose(s, ip=BAD, direction="both"):
    return s.call("POST", "/api/response/proposals",
                  {"actor": "reviewer", "ip": ip, "direction": direction})


def step(s, pid, name, **body):
    return s.call("POST", f"/api/response/proposals/{pid}/{name}", {"actor": "reviewer", **body})


def approved_proposal(s, ip=BAD):
    pid = propose(s, ip)[1]["proposal_id"]
    step(s, pid, "preview")
    status, data = step(s, pid, "approve", confirm_ip=ip)
    assert status == 200, data
    return pid


def scenario_manual():
    print("== Scenario A: manual mode (no firewall connector)")
    s = Server("A-manual", "maxguard.api.app:create_app", {})
    try:
        status, p = show("propose 203.0.113.7 both", propose(s))
        pid = p["proposal_id"]
        before = len(s.audit())
        show("approve WITHOUT preview (right IP)", step(s, pid, "approve", confirm_ip=BAD))
        after = s.audit()
        print(f"  audit rows before/after the refused approve: {before}/{len(after)}; "
              f"last row: {after[-1][:2]}")
        show("approve with a stray click (no confirm_ip)", step(s, pid, "approve"))
        print(f"  audit after missing-IP approve (state proposed): {s.audit()[-1]}")
        show("preview", step(s, pid, "preview"))
        show("approve with mistyped IP 203.0.113.8", step(s, pid, "approve", confirm_ip="203.0.113.8"))
        show("approve with 203.0.113.07 (leading zero)", step(s, pid, "approve", confirm_ip="203.0.113.07"))
        show("approve with confirm_ip as JSON integer 3405803783",
             step(s, pid, "approve", confirm_ip=3405803783))
        show("approve with whitespace-only actor",
             s.call("POST", f"/api/response/proposals/{pid}/approve",
                    {"actor": "   ", "confirm_ip": BAD}))
        print(f"  audit rows now: {[a[0] for a in s.audit()]}")
        show("approve with the right IP", step(s, pid, "approve", confirm_ip=BAD))
        status, p = s.call("GET", f"/api/response/proposals/{pid}")
        undo = {k: bool(v.get("undo")) for k, v in p["rules"].items() if isinstance(v, dict)}
        print(f"  GET proposal: state={p['state']} preview kept={p['preview'] is not None} "
              f"undo present per method={undo}")
        print(f"  nftables undo: {p['rules']['nftables']['undo']}")
        # 20 apply clicks at once: exactly one may change the state.
        with concurrent.futures.ThreadPoolExecutor(20) as pool:
            codes = list(pool.map(lambda _: step(s, pid, "apply")[0], range(20)))
        print(f"  20 parallel apply requests -> status counts {sorted(set((c, codes.count(c)) for c in codes))}")
        applied_rows = [a for a in s.audit() if a[0] == "response.applied"]
        print(f"  response.applied audit rows: {len(applied_rows)}")
        show("revert", step(s, pid, "revert"))
        show("revert again", step(s, pid, "revert"))
        show("apply after revert", step(s, pid, "apply"))
        show("reject a reverted proposal", step(s, pid, "reject"))
        print(f"  audit rows for proposal {pid}: {[a[0] for a in s.audit() if a[1] == str(pid)]}")

        print("  -- second proposal: race 20 parallel approvals")
        pid2 = propose(s, "198.51.100.9")[1]["proposal_id"]
        step(s, pid2, "preview")
        with concurrent.futures.ThreadPoolExecutor(20) as pool:
            codes = list(pool.map(lambda _: step(s, pid2, "approve", confirm_ip="198.51.100.9")[0],
                                  range(20)))
        print(f"  20 parallel approvals -> status counts {sorted(set((c, codes.count(c)) for c in codes))}; "
              f"approved rows: {sum(1 for a in s.audit() if a[0]=='response.approved' and a[1]==str(pid2))}")

        print("  -- addresses that must be refused")
        n_props = len(s.call("GET", "/api/response/proposals")[1])
        n_audit = len(s.audit())
        for ip in ["127.0.0.1", "::1", "0.0.0.0", "224.0.0.1", "fe80::1%eth0", 3232235777,
                   "3232235777", "010.1.1.1", "::ffff:127.0.0.1", "255.255.255.255",
                   "2001:db8::1%eth0", "ff02::1", "169.254.1.1", "0x7f.0.0.1", "127.1",
                   "203.0.113.7/32", " 203.0.113.7", "203.0.113.7\n"]:
            status, data = propose(s, ip)
            detail = data.get("detail") if isinstance(data, dict) else data
            if isinstance(detail, list):
                detail = detail[0].get("msg")
            print(f"  propose {ip!r}: HTTP {status} {str(detail)[:110]}")
        print(f"  proposals before/after: {n_props}/{len(s.call('GET', '/api/response/proposals')[1])}; "
              f"audit rows before/after: {n_audit}/{len(s.audit())}")
        print("  -- addresses that are accepted")
        for ip in ["192.0.2.2", "172.17.0.1", "240.0.0.1", "192.168.1.1", "::127.0.0.1"]:
            status, data = propose(s, ip)
            print(f"  propose {ip!r}: HTTP {status} "
                  f"{data.get('state') if isinstance(data, dict) and 'state' in data else data}")
        status, data = propose(s, "192.0.2.2")
        print(f"  second open proposal for 192.0.2.2: HTTP {status} {data}")
        print(f"  audit row for that 409? last row: {s.audit()[-1][:2]}")
    finally:
        s.stop()


def write_key(server_data: Path):
    (server_data / "opnsense").mkdir(parents=True, exist_ok=True)
    (server_data / "opnsense" / "apikey.txt").write_text(
        f"key={fakefw.KEY}\nsecret={fakefw.SECRET}\n")


class DummyProxy:
    """Counts connections: proves the enforcer does not go through HTTPS_PROXY."""

    def __init__(self):
        self.sock = socket.socket()
        self.sock.bind(("127.0.0.1", 0))
        self.sock.listen(5)
        self.port = self.sock.getsockname()[1]
        self.connections = 0
        threading.Thread(target=self.loop, daemon=True).start()

    def loop(self):
        while True:
            try:
                conn, _ = self.sock.accept()
            except OSError:
                return
            self.connections += 1
            conn.close()


def firewall_scenario(name, mode, *, give_ca, key=True, url_override=None):
    print(f"== Scenario {name}: OPNsense connector, fake firewall mode={mode}, CA given={give_ca}")
    fw = fakefw.FakeFirewall(WORK / name / "fw", mode)
    proxy = DummyProxy()
    env = {"MAXGUARD_OPNSENSE_URL": url_override or fw.url,
           "MAXGUARD_OFFLINE_ALLOW": "127.0.0.1",
           "HTTPS_PROXY": f"http://127.0.0.1:{proxy.port}",
           "HTTP_PROXY": f"http://127.0.0.1:{proxy.port}", "NO_PROXY": "", "no_proxy": ""}
    if give_ca and fw.ca_file:
        env["MAXGUARD_OPNSENSE_CA"] = str(fw.ca_file)
    s = Server(name, "maxguard.api.app:create_app", env)
    try:
        if key:
            write_key(s.data)
        print(f"  MAXGUARD_OPNSENSE_URL={env['MAXGUARD_OPNSENSE_URL']}")
        pid = approved_proposal(s)
        status, data = show("apply", step(s, pid, "apply"))
        state = s.call("GET", f"/api/response/proposals/{pid}")[1]["state"]
        print(f"  state after apply: {state}")
        print(f"  fake firewall: API requests received={len(fw.requests)} {fw.requests[:3]}; "
              f"TLS handshake errors={len(fw.tls_errors)} {fw.tls_errors[:1]}")
        print(f"  aliases on the fake firewall: {fw.aliases}")
        print(f"  dummy HTTPS_PROXY connections: {proxy.connections}")
        print(f"  last response.* audit row: {s.audit()[-1]}")
        if state == "applied":
            show("revert", step(s, pid, "revert"))
            print(f"  aliases after revert: {fw.aliases}; last audit: {s.audit()[-1][:2]}")
    finally:
        s.stop()
        fw.stop()


def scenario_ingest_port():
    print("== Scenario H: the response API on the LAN ingest app (create_ingest_app)")
    token = secrets.token_urlsafe(32)  # throwaway, never stored
    s = Server("H-ingest", "maxguard.api.app:create_ingest_app",
               {"MAXGUARD_INGEST_TOKEN": token})
    try:
        auth = {"Authorization": f"Bearer {token}"}
        show("POST /api/response/proposals (no token)",
             s.call("POST", "/api/response/proposals", {"actor": "x", "ip": BAD}))
        show("POST /api/response/proposals (with token)",
             s.call("POST", "/api/response/proposals", {"actor": "x", "ip": BAD}, headers=auth))
        show("GET /api/response/proposals (with token)",
             s.call("GET", "/api/response/proposals", headers=auth))
        show("POST /api/response/proposals/1/approve (with token)",
             s.call("POST", "/api/response/proposals/1/approve",
                    {"actor": "x", "confirm_ip": BAD}, headers=auth))
        show("GET /openapi.json", s.call("GET", "/openapi.json"))
    finally:
        s.stop()


if __name__ == "__main__":
    which = sys.argv[3:] or ["A", "B", "C", "D", "E", "F", "G", "H"]
    if "A" in which:
        scenario_manual()
    if "B" in which:
        firewall_scenario("B-http", "http", give_ca=False)
    if "C" in which:
        firewall_scenario("C-selfsigned-noCA", "selfsigned", give_ca=False)
    if "D" in which:
        firewall_scenario("D-privateCA-noCA", "privateca", give_ca=False)
    if "E" in which:
        firewall_scenario("E-privateCA-withCA", "privateca", give_ca=True)
    if "F" in which:
        firewall_scenario("F-wrongname-withCA", "wrongname", give_ca=True)
    if "G" in which:
        firewall_scenario("G-nokeyfile", "privateca", give_ca=True, key=False)
    if "H" in which:
        scenario_ingest_port()
