"""AHM-04 row 7: LAN ingest (token compare, shipper https + ca_file, agent config mode).

Everything runs on 127.0.0.1 with a throwaway token made at run time and the
synthetic telnet fixture logs from tests/fixtures/zeek/telnet.
"""
from __future__ import annotations

import io
import os
import secrets
import shutil
import socket
import sqlite3
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import fakefw  # noqa: E402

REPO = Path(sys.argv[1]).resolve()
WORK = Path(sys.argv[2]).resolve()
sys.path.insert(0, str(REPO))
PY = sys.executable


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def token_timing():
    print("== 1. constant-time token check (in process, maxguard.api.app.check_ingest_token)")
    import hmac
    import timeit

    from fastapi import HTTPException

    from maxguard.api import app as api
    token = secrets.token_urlsafe(32)

    class Req:
        def __init__(self, given):
            self.headers = {"authorization": f"Bearer {given}"}
            self.app = type("A", (), {"state": type("S", (), {"ingest_token": token})()})()

    def attempt(given):
        try:
            api.check_ingest_token(Req(given))
            return 200
        except HTTPException as err:
            return err.status_code

    wrong_first = ("A" if token[0] != "A" else "B") + token[1:]
    wrong_last = token[:-1] + ("A" if token[-1] != "A" else "B")
    print(f"  right token -> {attempt(token)}; first char wrong -> {attempt(wrong_first)}; "
          f"last char wrong -> {attempt(wrong_last)}; shorter -> {attempt(token[:10])}; "
          f"'Basic' scheme -> {attempt(token) if False else 'n/a'}")
    # The comparison itself: hmac.compare_digest over 43-byte values.
    a = token.encode()
    for label, b in (("0 matching leading bytes", wrong_first.encode()),
                     ("42 matching leading bytes", wrong_last.encode())):
        best = min(timeit.repeat(lambda: hmac.compare_digest(b, a), number=200_000, repeat=7))
        print(f"  compare_digest, {label}: best of 7 x 200k = {best * 1e9 / 200_000:.1f} ns/call")
    naive = {}
    for label, b in (("0 matching leading bytes", wrong_first.encode()),
                     ("42 matching leading bytes", wrong_last.encode())):
        naive[label] = min(timeit.repeat(lambda: b == a, number=200_000, repeat=7))
    print("  (for contrast, plain ==: " + ", ".join(
        f"{k} {v * 1e9 / 200_000:.1f} ns" for k, v in naive.items()) + ")")


def make_interval(data_dir: Path) -> str:
    """One finished interval folder (1 h ago, UTC) holding the synthetic telnet logs."""
    start = (int(time.time()) // 900) * 900 - 3600
    name = datetime.fromtimestamp(start, UTC).strftime("%Y-%m-%d-%H%M")
    folder = data_dir / "zeek" / name
    folder.mkdir(parents=True)
    for log in ("conn.log", "maxguard_cleartext.log"):
        shutil.copy(REPO / "tests/fixtures/zeek/telnet" / log, folder / log)
    return name


def run_shipper(data_dir: Path, toml: str) -> str:
    (data_dir / "shipper.toml").write_text(toml)
    env = {k: v for k, v in os.environ.items() if k.lower() not in ("https_proxy", "http_proxy")}
    env.update({"PYTHONDONTWRITEBYTECODE": "1", "PYTHONPATH": str(REPO)})
    out = subprocess.run([PY, "-m", "maxguard.sensor.shipper", "--data", str(data_dir), "--once",
                          "--interval-minutes", "15"], cwd=REPO, env=env, capture_output=True,
                         text=True, timeout=300)
    lines = [line.split(" ", 2)[-1] for line in (out.stdout + out.stderr).splitlines()]
    return " | ".join(lines)


def shipper_tls():
    print("== 2. shipper -> the real ingest app served over TLS by uvicorn (private CA)")
    tls = WORK / "tls"
    ca_file, cert, key = fakefw.make_certs(tls, "privateca")
    token = secrets.token_urlsafe(32)
    port = free_port()
    console_data = WORK / "console-data"
    env = {k: v for k, v in os.environ.items()
           if not k.startswith("MAXGUARD_") and k.lower() not in ("https_proxy", "http_proxy")}
    env.update({"PYTHONDONTWRITEBYTECODE": "1", "MAXGUARD_DATA_DIR": str(console_data),
                "MAXGUARD_INGEST_TOKEN": token, "MAXGUARD_ALLOWED_HOSTS": "127.0.0.1,localhost",
                "MAXGUARD_OFFLINE": "1", "OLLAMA_HOST": "http://127.0.0.1:9"})
    log = open(WORK / "ingest-tls.log", "w")
    proc = subprocess.Popen([PY, "-m", "uvicorn", "maxguard.api.app:create_ingest_app", "--factory",
                             "--host", "127.0.0.1", "--port", str(port),
                             "--ssl-keyfile", str(key), "--ssl-certfile", str(cert),
                             "--log-level", "warning"], cwd=REPO, env=env, stdout=log,
                            stderr=subprocess.STDOUT)
    try:
        for _ in range(100):
            try:
                socket.create_connection(("127.0.0.1", port), 0.2).close()
                break
            except OSError:
                time.sleep(0.1)
        base = f'token = "{token}"\nsensor_id = "lab-sensor"\n'
        cases = [
            ("https + ca_file", f'console_url = "https://127.0.0.1:{port}"\n{base}ca_file = "{ca_file}"\n'),
            ("https, no ca_file", f'console_url = "https://127.0.0.1:{port}"\n{base}'),
            ("https + ca_file, name not in cert (localhost)",
             f'console_url = "https://localhost:{port}"\n{base}ca_file = "{ca_file}"\n'),
            ("http:// to the TLS port", f'console_url = "http://127.0.0.1:{port}"\n{base}'),
            ("https + ca_file, wrong token",
             f'console_url = "https://127.0.0.1:{port}"\ntoken = "{secrets.token_urlsafe(32)}"\n'
             f'sensor_id = "lab-sensor"\nca_file = "{ca_file}"\n'),
        ]
        for label, toml in cases:
            data_dir = WORK / ("sensor-" + label.split(",")[0].replace(" ", "").replace("+", "_")
                               + str(cases.index((label, toml))))
            name = make_interval(data_dir)
            result = run_shipper(data_dir, toml)
            shipped = (data_dir / "zeek" / name / ".shipped").exists()
            print(f"  [{label}] shipper says: {result[-260:]}")
            print(f"     .shipped marker written: {shipped}")
        with sqlite3.connect(console_data / "state.db") as db:
            rows = db.execute("SELECT count(*), group_concat(input_name) FROM analyses").fetchone()
            alerts = db.execute("SELECT rule_id, count FROM alerts").fetchall() \
                if "count" in [c[1] for c in db.execute("PRAGMA table_info(alerts)")] else \
                db.execute("SELECT rule_id FROM alerts").fetchall()
        print(f"  console state.db: analyses={rows[0]} ({rows[1]}); alerts={alerts}")
    finally:
        proc.terminate()
        proc.wait(10)
        log.close()
    return ca_file, cert, key


def agent_config():
    print("== 3. host agent: config file permissions (maxguard.sensor.agent.load_config)")
    from maxguard.sensor import agent
    folder = WORK / "agent"
    folder.mkdir(exist_ok=True)
    text = (f'console_url = "http://127.0.0.1:8001"\ntoken = "{secrets.token_urlsafe(32)}"\n'
            f'spool_dir = "{folder / "spool"}"\ncapture_user = "nobody"\n')
    for mode in (0o600, 0o400, 0o700, 0o640, 0o604, 0o644, 0o660, 0o610, 0o601, 0o666):
        path = folder / f"agent-{mode:o}.toml"
        path.write_text(text)
        path.chmod(mode)
        try:
            agent.load_config(path)
            result = "accepted"
        except ValueError as err:
            result = f"refused: {err}"
        print(f"  mode {mode:04o}: {result.replace(str(folder), '<dir>')}")
    link = folder / "link.toml"
    link.symlink_to(folder / "agent-644.toml")
    try:
        agent.load_config(link)
        print("  symlink -> 0644 file: accepted")
    except ValueError as err:
        print(f"  symlink -> 0644 file: refused: {str(err).replace(str(folder), '<dir>')}")
    other = folder / "owned-by-uid-12345.toml"
    other.write_text(text)
    other.chmod(0o600)
    os.chown(other, 12345, 12345)
    try:
        agent.load_config(other)
        print("  0600 file owned by another account (uid 12345), loaded by root: accepted")
    except ValueError as err:
        print(f"  0600 file owned by uid 12345: refused: {err}")
    env = {k: v for k, v in os.environ.items()}
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    out = subprocess.run([PY, "-m", "maxguard.sensor.agent", "--config", str(folder / "agent-644.toml"),
                          "--upload-only"], cwd=REPO, env=env, capture_output=True, text=True)
    print(f"  CLI with the 0644 file: exit {out.returncode}; last line: "
          f"{(out.stderr or out.stdout).strip().splitlines()[-1].replace(str(folder), '<dir>')}")
    print("  Windows branch (platform.system() == 'Windows'), 0644 file:")
    import platform
    real = platform.system
    platform.system = lambda: "Windows"
    try:
        agent.check_private(folder / "agent-644.toml")
        print("    check_private returned without error (no check on Windows)")
    finally:
        platform.system = real


def agent_tls(ca_file, cert, key):
    print("== 4. host agent -> TLS ingest app with a private CA (no ca_file setting exists)")
    from maxguard.sensor import agent
    token = secrets.token_urlsafe(32)
    port = free_port()
    env = {k: v for k, v in os.environ.items()
           if not k.startswith("MAXGUARD_") and k.lower() not in ("https_proxy", "http_proxy")}
    env.update({"PYTHONDONTWRITEBYTECODE": "1", "MAXGUARD_DATA_DIR": str(WORK / "console-data2"),
                "MAXGUARD_INGEST_TOKEN": token, "MAXGUARD_ALLOWED_HOSTS": "127.0.0.1",
                "MAXGUARD_OFFLINE": "1", "OLLAMA_HOST": "http://127.0.0.1:9"})
    log = open(WORK / "ingest-tls2.log", "w")
    proc = subprocess.Popen([PY, "-m", "uvicorn", "maxguard.api.app:create_ingest_app", "--factory",
                             "--host", "127.0.0.1", "--port", str(port), "--ssl-keyfile", str(key),
                             "--ssl-certfile", str(cert), "--log-level", "warning"], cwd=REPO,
                            env=env, stdout=log, stderr=subprocess.STDOUT)
    try:
        for _ in range(100):
            try:
                socket.create_connection(("127.0.0.1", port), 0.2).close()
                break
            except OSError:
                time.sleep(0.1)
        spool = WORK / "agent-spool"
        spool.mkdir(exist_ok=True)
        cap = spool / "capture-20261027-100000.pcap"
        shutil.copy(REPO / "tests/pcaps/telnet.pcap", cap)
        config = agent.AgentConfig(console_url=f"https://127.0.0.1:{port}", token=token,
                                   spool_dir=spool, capture_user="nobody")
        os.environ["REQUESTS_CA_BUNDLE"] = str(ca_file)  # a user might try this; trust_env=False
        status = agent.upload(cap, config)
        print(f"  agent.upload over https with REQUESTS_CA_BUNDLE set to the CA: status={status}")
        del os.environ["REQUESTS_CA_BUNDLE"]
    finally:
        proc.terminate()
        proc.wait(10)
        log.close()


def replay():
    print("== 5. replay of one captured ingest request (plain HTTP ingest app)")
    import requests
    token = secrets.token_urlsafe(32)
    port = free_port()
    data_dir = WORK / "console-replay"
    env = {k: v for k, v in os.environ.items()
           if not k.startswith("MAXGUARD_") and k.lower() not in ("https_proxy", "http_proxy")}
    env.update({"PYTHONDONTWRITEBYTECODE": "1", "MAXGUARD_DATA_DIR": str(data_dir),
                "MAXGUARD_INGEST_TOKEN": token, "MAXGUARD_ALLOWED_HOSTS": "127.0.0.1",
                "MAXGUARD_OFFLINE": "1", "OLLAMA_HOST": "http://127.0.0.1:9"})
    log = open(WORK / "ingest-replay.log", "w")
    proc = subprocess.Popen([PY, "-m", "uvicorn", "maxguard.api.app:create_ingest_app", "--factory",
                             "--host", "127.0.0.1", "--port", str(port), "--log-level", "warning"],
                            cwd=REPO, env=env, stdout=log, stderr=subprocess.STDOUT)
    try:
        for _ in range(100):
            try:
                socket.create_connection(("127.0.0.1", port), 0.2).close()
                break
            except OSError:
                time.sleep(0.1)
        from maxguard.sensor.shipper import pack_folder
        folder_root = WORK / "replay-sensor"
        name = make_interval(folder_root)
        archive = pack_folder(folder_root / "zeek" / name)
        s = requests.Session()
        s.trust_env = False
        for attempt in (1, 2):
            r = s.post(f"http://127.0.0.1:{port}/api/ingest",
                       headers={"Authorization": f"Bearer {token}"},
                       data={"sensor_id": "lab-sensor"},
                       files={"file": (f"{name}.tar.gz", io.BytesIO(archive), "application/gzip")},
                       timeout=120)
            print(f"  send #{attempt} of the same request: HTTP {r.status_code} {r.text[:120]}")
        with sqlite3.connect(data_dir / "state.db") as db:
            cols = [c[1] for c in db.execute("PRAGMA table_info(alerts)")]
            print(f"  alerts table columns: {cols}")
            print(f"  analyses rows: {db.execute('SELECT count(*) FROM analyses').fetchone()[0]}; "
                  f"alerts: {db.execute('SELECT * FROM alerts').fetchall()[:3]}")
    finally:
        proc.terminate()
        proc.wait(10)
        log.close()


if __name__ == "__main__":
    WORK.mkdir(parents=True, exist_ok=True)
    token_timing()
    ca_file, cert, key = shipper_tls()
    agent_config()
    agent_tls(ca_file, cert, key)
    replay()
