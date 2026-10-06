# MaxGuard v2.0 reference implementation — shared spec for builders

This scratch repo is the *reference implementation* behind the team's planning
docs. Every code block that later appears in `docs/roadmap/<person>.md` is
copied from here, so it must be correct, tested, small, and readable by a junior
student (clear names, short functions, comments only where they explain *why*).

## Hard rules (from CLAUDE.md)
1. Offline at runtime: no network calls except to the local Ollama host and an
   explicitly configured user-owned firewall (enforcers). Tests never use the network.
2. Determinism: rules never read the clock, random numbers, or the network. Same
   logs -> same findings, same finding_id, same evidence record_ids. The report
   dict produced by pipeline.analyze has NO wall-clock timestamps.
3. AI sentences must cite Evidence.record_id values; validated in code.
4. Blocking: human approval, reversible, logged. Only the user's own network.
5. Sensors never inject packets. Decoys run on their own IP and only answer.
6. No secrets, personal data, emails, or real captures in the repo.
7. JA4 only (from Suricata). No other JA4+ methods.
8. Compliance rows cite exact control ID + framework version (PROJECT_DECISIONS §8):
   PCI DSS "4.0.1"; NIST SP 800-53 "Rev. 5 (Release 5.2.0)"; CISA CPG "2.0";
   CJIS "6.1"; MITRE ATT&CK "v19.x" (exact point release recorded in the file).
   Never invent control IDs: only use IDs you have verified from a primary source,
   otherwise leave a clearly marked TODO for Amory.

## Python and tooling
- Code must run on Python 3.11 (developer laptops, CI) AND 3.13 (inside the
  zeek/zeek:9.0.0 image, Debian 13). Use `from __future__ import annotations`
  where you use `X | None` in signatures inside dataclasses on 3.11 (fine either way).
- Style: ruff defaults, line length 100. `ruff check .` must pass.
- Tests: pytest. Unit tests in tests/unit/ (no Docker, no network, < 1 s each).
  Integration tests in tests/integration/ (need Zeek; run inside the engine image).

## Pinned tool versions (verified Oct 6, 2026)
- Zeek 9.0.0 (`zeek/zeek:9.0.0`, amd64+arm64; `lts` currently = 9.0.0).
- Suricata 7.0.10 (Debian 13 package `suricata` 1:7.0.10-1+deb13uX inside the engine
  image; `jasonish/suricata:7.0.10` image, AlmaLinux, amd64+arm64, for the live
  sensor and for testing). JA4 works on 7.0.10 and 8.0.7 with maxguard-suricata.yaml.
- Ollama image `ollama/ollama:0.35.1` (newest stable on Docker Hub, 2026-10-02, amd64+arm64;
  pulled here). The model registry is blocked in this sandbox, so no model was ever run here:
  mark model-dependent output "not run".
- htmx 2.0.11 (0BSD) vendored at maxguard/web/static/htmx-2.0.11.min.js
  (sha256 d6fdc75f204e6bdefa99b69bf1e6d4ac69b8a364f77929f45c13476b4000f717).
- Python deps (latest verified): pyyaml 6.0.3, requests 2.34.2, fastapi 0.142.2,
  starlette 1.7.0, uvicorn 0.54.0, jinja2 3.1.6, python-multipart 0.0.32,
  duckdb 1.5.6, cryptography 50.0.2, pytest 9.1.1, ruff 0.16.10, httpx 0.28.1.

## Verified facts about the tools (do not "fix" these)
- `zeek -D` makes uids deterministic for capture files. Runner uses -D plus
  `policy/protocols/conn/community-id-logging`. Live sensors must NOT use -D.
- Suricata flow_id is random per run; ids.record_id() ignores it. Suricata and Zeek
  produce the same community_id (`1:...=`) for the same connection; eve.json records
  are linked by community_id (Evidence.uid = community_id for eve records).
- Zeek 9 x509.log has NO uid/id.* fields; link via ssl.log cert_chain_fps[0] == x509 fingerprint.
- Zeek 9 ssl.log versions: "TLSv10", "TLSv11", "TLSv12", "TLSv13". ftp.log hides
  passwords as "<hidden>". Telnet/POP3/IMAP have no dedicated log -> maxguard_cleartext.log.
- cryptography >= 44 refuses SHA-1 signatures; the lab makes its SHA-1 cert with
  the openssl CLI (present in python:3.11-slim-bookworm, OpenSSL 3.0.22).
- OpenSSL 3.0.22 in python:3.11-slim-bookworm has no 3DES; the weak-cipher lab
  scenario uses NULL-SHA256 (Zeek: TLS_RSA_WITH_NULL_SHA256).
- A file named http.py in the scenarios folder shadows Python's http package;
  lab scenarios are named plain_http.py / plain_http_alt.py.

## Repository layout (target)
```
maxguard/
  models.py        Contract 1 (DONE)          ids.py   record/finding IDs (DONE)
  adapters/base.py Contract 3 (DONE)  pcap.py (DONE)  zeeklogs.py (DONE)
           live.py (Jakub, spring)  netflow.py (Jakub, spring)
  zeek/runner.py (DONE)  zeek/scripts/cleartext.zeek, inventory.zeek (DONE)
  suricata/runner.py, maxguard-suricata.yaml, rules/maxguard.rules (DONE)
  rules/base.py (DONE) tls.py cleartext.py certs.py (DONE)
        ja4.py (Jakub)  decoy.py, baseline.py (Fiona, spring)
  mapping/loader.py Contract 2 (DONE)
  events/normalize.py, events/lookup.py (Jaiden)
  storage/state.py (SQLite), storage/events.py (Parquet+DuckDB) (Jaiden)
  inventory.py (Jakub)
  ai/ollama_client.py, ai/citations.py, ai/home_text.yaml (Jonattan)
  offline.py (Jonattan)
  report.py (Amory)   custody/log.py (Amory)   custody/signing.py (Jaiden)
  intel/bundle.py (Jaiden, spring)
  api/app.py (Jaiden)  web/routes.py, web/templates/, web/static/ (Ahmad)
  response/generate.py, response/preview.py, response/approvals.py,
  response/enforcers/opnsense.py (Ahmad)
  sensor/attribution.py (Jakub)  sensor/agent.py (Jakub, spring)
  pipeline.py (core, DONE by lead; owners may add hooks)
cli/main.py (Fiona)
mappings/*.yaml (Amory; attack.yaml by Fiona)
lab/ (Karthik, DONE: compose.yaml, server/, client/scenarios/)
tests/unit, tests/integration, tests/pcaps, tests/expected, tests/fixtures
docker/Dockerfile, docker/compose.yaml, docker/compose.dev.yaml (Jaiden)
.github/workflows/ci.yml (Jaiden; integration job by Karthik)
scripts/ (benchmark_models.py: Ali; build-offline-bundle.sh, install.sh: Jonattan)
pyproject.toml (Jaiden)
```

## Lead decisions after wave 1 (binding for waves 2-3)
- Ollama pin: ollama/ollama:0.35.1 everywhere (compose, bundle, docs).
- /api/chat body also sends "think": false (thinking models such as qwen3 otherwise reason first).
- report["ai"] gains "reason": str | None (why the AI was unavailable, e.g. "model 'qwen3:4b' not
  found: run ollama pull qwen3:4b"). Shown by the dashboard.
- sensor_id: "pcap" for pcap uploads, "import" for Zeek-log uploads, the sensor name for live.
- create_app(data_dir: Path | None = None, *, explain: bool = True): data_dir defaults to
  env MAXGUARD_DATA_DIR or "data" (uvicorn --factory calls it with no arguments).
- StateStore.update_alert(finding_id, *, actor, at, status=None, assignee=None) — `at` is required
  (stores never read the clock). KeyError -> 404, ValueError -> 400 in the API.
  StateStore.get_analysis(analysis_id) and StateStore.list_analyses(limit=50) exist.
- Identical file uploaded again (same input sha256): a new analysis row is stored and the alert's
  details refresh, but its count does NOT grow (DONE in storage/state.py by the lead).
- Alert recurrence (DONE in storage/state.py by the lead): when a re-upload brings NEW evidence for a finding (its last_seen increases)
  and the alert is "resolved", it reopens to "new" and the reopen is audited; "false_positive"
  stays suppressed; "investigating" stays. (Security choice: a fixed problem that comes back
  must be seen again.)
- Mapping files stay in the repo-root folder mappings/ (easy for Amory to edit on github.com).
  pipeline finds them via env MAXGUARD_MAPPINGS_DIR, else the repo-root mappings/ folder; the
  Dockerfile copies mappings/ to /opt/maxguard/mappings and sets MAXGUARD_MAPPINGS_DIR. If the
  folder has no *.yaml files, analyze() raises an error instead of silently mapping nothing.
  Do NOT install mappings as a top-level Python package.
- Ruff: pyproject [tool.ruff] line-length = 100, [tool.ruff.lint] select = ["E", "F", "I", "B", "UP"].
  (A user-level ruff config exists in this sandbox; the project config overrides it.)
- Tests run as `pytest` (pyproject sets [tool.pytest.ini_options] pythonpath = ["."]).
- Live sensor Suricata image: jasonish/suricata:7.0.17 (newest 7.0.x, security fixes; parses
  untrusted traffic all day). Fixtures/tests stay on 7.0.10 output (same eve format, and 7.0.10 is
  the Debian 13 base version inside the engine image).
- Raspberry Pi OS is now based on Debian 13 "Trixie" (64-bit Lite). Capture port via NetworkManager:
  ipv4.method disabled, ipv6.method disabled (NOT ignore: ignore keeps an fe80:: link-local
  address), ethernet.accept-all-mac-addresses true, ethtool.feature-gro off, ethtool.feature-lro off.
  Sensor data on a USB SSD at /data; docker.service gets RequiresMountsFor=/data.
- Live sensor batching: EventStore.write once per 5-15 minutes (each Parquet file has ~3 KB
  overhead); measured ~60 B/event zstd on x86 synthetic data (verify on hardware).
- Honesty about isolation: only the ollama container is network-isolated (internal network). The
  engine container has a route via the ui network; its Python code is guarded by maxguard.offline
  (MAXGUARD_OFFLINE=1, extra hosts via MAXGUARD_OFFLINE_ALLOW), and Zeek/Suricata reading files
  make no connections. Never write that the engine container is isolated.

## Report dict (output of maxguard.pipeline.analyze) — schema "maxguard.report/2"
```python
{
  "schema": "maxguard.report/2",
  "input": {"name": "telnet.pcap", "sha256": "<hex>", "adapter": "pcap"},
  "tools": {"zeek": True, "suricata": True | False},   # whether each ran
  "frameworks": [{"framework": ..., "version": ..., "source": ...}, ...],
  "findings": [Finding.to_dict(), ...],   # sorted by SEVERITY order, rule_id, src, dst, port
  "assets": [ {...} ],                    # maxguard.inventory.build(log_dir, findings)
  "events": [ {...} ],                    # normalized events (see below); pipeline returns them
  "ai": {"status": "ok" | "unavailable" | "disabled", "model": str | None,
         "explained": int, "dropped_sentences": int, "reason": str | None},
}
```
No timestamps of "now" anywhere in this dict.

## Common event schema (maxguard.events.normalize.normalize(log_dir, sensor_id) -> list[dict])
One dict per source record, keys exactly:
| key | type | meaning |
|---|---|---|
| event_id | str | = ids.record_id(log, rec) |
| ts | float | epoch seconds |
| sensor_id | str | "pcap" for uploads, else sensor name |
| source | str | "zeek" or "suricata" (later "netflow", "agent", "decoy") |
| log | str | "conn.log", "dns.log", "http.log", "ssl.log", "dhcp.log", "eve.json" |
| kind | str | "conn", "dns", "http", "tls", "dhcp", "alert", "flow" |
| uid | str | Zeek uid or "" |
| community_id | str | community id or "" |
| src_ip, dst_ip | str | |
| src_port, dst_port | int or None | |
| proto | str | "tcp", "udp", "icmp", "" |
| service | str | Zeek service / Suricata app_proto / "" |
| bytes_out, bytes_in | int | orig/resp bytes (0 if unknown) |
| device_mac | str | MAC if known (dhcp), else "" |
| summary | str | short human text, e.g. "GET server:8080/" or "TLSv10 port4431.lab.invalid ja4=t10d..." |
| ja4 | str | JA4 from Suricata tls events, else "" |

Normalizer reads: conn.log, dns.log, http.log, ssl.log, dhcp.log, and eve.json
event types alert, tls, dns, dhcp (eve "flow" events are skipped because Zeek
conn.log already covers flows; eve "tls" kept because it carries ja4).
Output sorted by (ts, log, event_id) for determinism.

`maxguard.events.lookup.records_for(log_dir, record_ids: set[str]) -> dict[str, dict]`
returns the raw records (with "_log" key added) for the given record_ids; used by
the AI to show evidence to the model.

## Storage interfaces (Jaiden)
```python
class StateStore:            # maxguard/storage/state.py, SQLite WAL, path e.g. data/state.db
    def __init__(self, path: Path): ...
    def save_analysis(self, report: dict, *, received_at: float) -> str: ...  # returns analysis_id
    def list_alerts(self, *, status: str | None = None, severity: str | None = None,
                    limit: int = 200) -> list[dict]: ...
    def get_alert(self, finding_id: str) -> dict | None: ...
    def update_alert(self, finding_id: str, *, actor: str, status: str | None = None,
                     assignee: str | None = None) -> dict: ...
    def add_audit(self, *, actor: str, action: str, target: str, details: dict,
                  at: float) -> int: ...
    def list_audit(self, limit: int = 200) -> list[dict]: ...
ALERT_STATUSES = ("new", "investigating", "resolved", "false_positive")
# An alert = a finding row + status + assignee + analysis_id + first_received_at.
# Re-uploading the same capture updates count/last_seen of the same finding_id
# (dedup across analyses by finding_id).

class EventStore:            # maxguard/storage/events.py, hourly Parquet under root/
    def __init__(self, root: Path): ...
    def write(self, events: list[dict]) -> int: ...      # partition date=YYYY-MM-DD/hour=HH
    def query(self, *, ip: str | None = None, since: float | None = None,
              until: float | None = None, limit: int = 1000) -> list[dict]: ...
    def prune(self, *, older_than: float) -> int: ...   # deletes whole hour partitions
```

## API (Jaiden: maxguard/api/app.py) — FastAPI, JSON under /api
- `create_app(data_dir: Path, *, explain: bool = True) -> FastAPI`
- POST /api/analyses (multipart file) -> runs pipeline in a temp dir, saves to stores,
  returns {"analysis_id", "findings": n}
- GET /api/alerts?status=&severity= ; GET /api/alerts/{finding_id} ;
  PATCH /api/alerts/{finding_id} json {"status"?, "assignee"?, "actor"}
- GET /api/events?ip=&since=&until=&limit= (timeline)
- GET /api/assets
- GET /api/audit
- GET /api/stream  (server-sent events: "alerts-changed" whenever alerts change)
- The app stores its stores on `app.state.state_store` (StateStore), `app.state.event_store`
  (EventStore), and `app.state.data_dir` (Path), so other routers can reach them via `request.app.state`.
- For each optional router module that exists — `maxguard.web.routes` (Ahmad, HTML pages),
  `maxguard.response.routes` (Ahmad, block proposals/preview/approval JSON under /api/response) —
  the app does `app.include_router(module.router)`. It mounts /static from maxguard/web/static.
- The app binds to 127.0.0.1 by default (compose publishes 127.0.0.1:8000).

## AI (Jonattan)
- `maxguard/ai/citations.py`: `validate(raw: dict, allowed_ids: set[str]) -> tuple[list[Sentence], int]`
  keeps sentences with >= 1 evidence id where ALL ids are in allowed_ids and text non-empty;
  returns (kept, dropped_count).
- `maxguard/ai/ollama_client.py`: POST {OLLAMA_HOST}/api/chat with
  `"format": <JSON schema {"sentences":[{"text":str,"evidence_ids":[str]}]}>`,
  `"options": {"temperature": 0, "seed": 42}`, `"stream": False`.
  `explain(finding: dict, records: dict[str, dict]) -> tuple[list[Sentence], int]`
  `explain_all(findings: list[Finding], log_dir: Path, *, limit: int = 20) -> dict` (ai status dict)
  Explains per finding (never cache across findings), highest severity first, up to limit.
  Sets finding.explanation_sentences and finding.explanation (" ".join texts) or None.
  On connection error -> status "unavailable", findings keep explanation None.
- `maxguard/offline.py`: guard that blocks connect/connect_ex/sendto/sendmsg to
  non-allowed IPs AND blocks getaddrinfo for non-allowed hostnames.
- `maxguard/ai/home_text.yaml`: per rule_id {headline, action} plain-language text for Home mode
  (static, human-written, not AI).

## Shared fixtures (already generated, do not regenerate unless needed)
- tests/pcaps/<capture>.pcap — 14 synthetic lab captures (telnet, ftp, plain_http, plain_http_alt,
  pop3, imap, tls_weak_version, tls_weak_cipher, cert_expired, cert_weak_key, cert_sha1,
  cert_self_signed, clean_tls13). Each triggers exactly one rule (clean_tls13: none).
  Verified: Zeek 9.0.0 + rules give the same findings, finding_ids and record_ids on two runs.
- tests/fixtures/zeek/<capture>/ — Zeek 9.0.0 JSON logs (made with -D + community-id
  + cleartext.zeek + inventory.zeek) plus eve.json from Suricata 7.0.10 with
  maxguard-suricata.yaml. Use these for fast unit tests (no Docker needed).
- No capture has DNS, DHCP or RDP traffic yet; hand-write small fixture lines for those
  (field names must match Zeek 9 / Suricata 7 — check the Zeek docs or generate them).

## Rule ID registry (final; new IDs need Security Lead approval — flag them)
Fall 2026: cleartext.ftp, cleartext.telnet, cleartext.http, cleartext.http_alt, cleartext.pop3,
cleartext.imap, rdp.standard_security, tls.weak_version, tls.weak_cipher, cert.expired,
cert.self_signed, cert.weak_key, cert.sha1_signature.
Proposed v2.0 additions (spring): tls.ja4_watchlist (Jakub), decoy.contact (Fiona),
baseline.new_service (Fiona).

## Test harness in this sandbox
- Host venv: ./.venv (Python 3.11) with all Python deps. Run `./.venv/bin/pytest tests/unit -q`.
- Docker daemon is running. Images present: zeek/zeek:9.0.0, jasonish/suricata:7.0.10,
  jasonish/suricata:8.0.7, python:3.11-slim-bookworm, nicolaka/netshoot:v0.15,
  ollama/ollama:0.35.1 (large: never `docker save` it), lab-server, lab-client,
  maxguard-sandbox:test (Zeek 9.0.0 + Python 3.13 venv at /opt/venv with MaxGuard's
  dependencies and pytest; NO Suricata; built in planning as a stand-in for the engine test image).
- Python 3.13 deps for the Zeek image: ../deps313 (mount at /deps, PYTHONPATH=/deps).
  Example: `docker run --rm --network none -v $PWD:/src -v $(realpath ../deps313):/deps:ro
  -e PYTHONPATH=/deps -w /src zeek/zeek:9.0.0 python3 -m pytest tests/integration -q`
  (inside Zeek image there is no Suricata; Suricata output is tested from eve.json
  fixtures produced with the jasonish/suricata:7.0.10 container).
- Containers have NO internet. Do not try apt-get. Docker builds that need pip must
  use ../ccr-build.sh <context> <tag> [Dockerfile] (sandbox-only helper; never document it).
- Lab captures: lab/captures/*.pcap (14 synthetic captures). Regenerate one with:
  `cd lab && CAPTURE=x SCENARIO=x docker compose up --no-build --abort-on-container-exit --exit-code-from client; docker compose down`
- Never write outside this ref/ folder except your own temp dirs. Never touch
  /home/user/maxguard (the real repo).

## Lead decisions after the planning docs (binding for the build of the remaining tasks)

The team's planning documents are published. Read-only copies are in `docs-spec/`:
`docs-spec/ARCHITECTURE.md` and `docs-spec/roadmap/<person>.md`. Each remaining task is
specified there as a **Design task** with its task ID (for example `JAI-07` in
`docs-spec/roadmap/jaiden.md`). BUILD EXACTLY WHAT THE TASK'S STEPS SAY: the same file
paths, function names, signatures, endpoints, settings and test files. If the spec is wrong
or impossible, build the closest correct thing and explain the difference in
`issues_for_lead` (the lead will fix the docs). Do not edit `docs-spec/`.

- Task IDs (use them in docstrings, e.g. "(Karthik, KAR-03)"): see each person's file.
- Live sensor Suricata: `jasonish/suricata:8.0.7` (OISF ended the 7.0 branch in July 2026).
  The local `jasonish/suricata:8.0.7` tag may be the arm64 variant: pull the amd64 one with
  `docker pull --platform linux/amd64 jasonish/suricata:8.0.7` before running it here.
  Suricata containers need `--cap-add NET_ADMIN --cap-add NET_RAW --cap-add SYS_NICE`
  (Suricata user guide, packet capture). Fixtures stay on 7.0.10 output.
- Live shipping interval: 15 minutes by default (one folder per interval), as in
  ARCHITECTURE.md section 4.
- Tests that use FastAPI's TestClient need `httpx2` (installed in ./.venv; pyproject dev extra).
- DuckDB: always `duckdb.connect(config=maxguard.storage.events.DUCKDB_CONFIG)` (no extension
  auto-install; CLAUDE.md rule 1).
- The API is `maxguard/api/app.py` with `create_app(data_dir=None, *, explain=True)` exactly as
  in ARCHITECTURE.md section 10 (the lead writes it; other tasks may import it once it exists,
  and must not edit it — report what you need).
- Already tested files that the published docs embed must not change unless a real bug needs
  it; if you change one, list it in `files` and explain in `issues_for_lead`.
- Test data uses only lab/fixture data or documentation addresses (192.0.2.0/24,
  198.51.100.0/24, 203.0.113.0/24). Nothing ever contacts a real external host.
- Ollama: never pull or run a model (registry blocked). For tests use fake servers.
- Docker images you may use: everything already on the host, plus small public images you pull
  yourself (record the exact tag and license). Disk is limited (about 12 GB free): never
  `docker save` a large image; remove what you pulled when done unless the docs need it.

### API contract the builders code against (the lead writes maxguard/api/app.py)

- `POST /api/analyses`: multipart/form-data, one field `file`. 200 -> `{"analysis_id": str, "findings": int}`.
  400 unsupported file, 413 too large (`MAXGUARD_MAX_UPLOAD_MB`, default 1024).
- `POST /api/ingest`: the same, plus an optional form field `sensor_id` (1-64 characters from
  `A-Z a-z 0-9 . _ -`; default `sensor`; anything else -> 400) and the header
  `Authorization: Bearer <token>`. 404 unless the console sets `MAXGUARD_INGEST_TOKEN`; 401 on a
  missing or wrong token. The sensor name becomes `sensor_id` in every event
  (`pipeline.analyze(..., sensor_id=...)`, a new optional keyword).
- `GET /api/alerts?status=&severity=&limit=` -> JSON list of alerts (Finding.to_dict() keys plus
  status, assignee, count, first_seen, last_seen, analysis_id, first_received_at, last_received_at;
  times are Unix seconds). `GET /api/alerts/{finding_id}` -> one alert (404).
  `PATCH /api/alerts/{finding_id}` JSON `{"actor": str, "status"?: str, "assignee"?: str}`.
- `GET /api/events?ip=&since=&until=&limit=` -> list of events (EVENT_KEYS). `GET /api/assets` -> list
  (assets of the newest analysis). `GET /api/audit?limit=` -> list, newest first.
  `GET /api/analyses` -> list; `GET /api/analyses/{analysis_id}` -> stored report (404).
- `GET /api/stream?max_events=N` -> `text/event-stream`: `event: alerts-changed` + `data: <counter>`
  whenever alerts change, `: keep-alive` every 15 s.
- Routers: `create_app()` includes `maxguard.web.routes.router` and `maxguard.response.routes.router`
  when they import, and mounts `/static` from `maxguard/web/static/`. Routers read the stores from
  `request.app.state.state_store` / `request.app.state.event_store` / `request.app.state.data_dir`.
  To tell open dashboards that alerts changed, call `maxguard.api.app.notify_change(request.app)`.

### Zeek: never load Zeek's own `local` policy (found during the build, binding)

Zeek 9.0.0's `share/zeek/site/local.zeek` loads three scripts that make DNS lookups of their own:
`frameworks/files/detect-MHR` (asks Team Cymru about the SHA-1 of every downloaded executable/PDF),
`protocols/ssh/interesting-hostnames` and `frameworks/notice/extend-email/hostnames` (reverse DNS).
Zeek is a separate program, so the Python offline guard cannot stop it (CLAUDE.md rules 1 and 5).
MaxGuard therefore loads `maxguard/zeek/site.zeek` (a copy of local.zeek without those three) wherever
it used `local`: `maxguard/zeek/runner.py`, `scripts/make_fixtures.sh`, the sensor compose file, and every
documented command. The fixtures did not change (checked). `tests/unit/test_zeek_site.py` fails if any
MaxGuard `.zeek` file loads `local` or one of the three scripts. Do not load `local` anywhere.

## API update (October 6, 2026, evening): Host allow-list and the ingest-only app

- The API answers only requests whose Host header is in MAXGUARD_ALLOWED_HOSTS
  (default "localhost,127.0.0.1,[::1]"); anything else gets 400 "Invalid host
  header" (Starlette TrustedHostMiddleware, against DNS rebinding).
  tests/conftest.py has an autouse fixture that adds "testserver", so
  TestClient(create_app(...)) works in every test. uvicorn on 127.0.0.1 works.
- create_ingest_app(data_dir=None, *, explain=True) serves only POST /api/ingest
  (no /docs), for the LAN port (docker/compose.lan.yaml, port 8001). The full
  app, create_app(), stays on 127.0.0.1 and still includes /api/ingest.
  The dashboard and the response module are never reachable from the LAN.
- The dashboard learns about data ingested by the other process at its next
  refresh (the 30 s fallback), because GET /api/stream counts changes per process.
- The live sensor (JAK-07) is built: maxguard/adapters/live.py is in ADAPTERS.
