export const meta = {
  name: 'maxguard-reference-build',
  description: 'Build and test the MaxGuard v2.0 reference implementation module by module in the scratch repo',
  phases: [
    { title: 'Wave 1', detail: 'independent core modules' },
    { title: 'Wave 2', detail: 'API, UI, response, custody, integration tests' },
    { title: 'Wave 3', detail: 'spring features' },
    { title: 'Integrate', detail: 'full test run and cross-module fixes' },
  ],
}

const R = args.ref
const COMMON = `
You are building ONE part of the MaxGuard v2.0 *reference implementation* in the scratch repo at ${R}.
FIRST read ${R}/SPEC.md completely, then read the existing code you depend on (maxguard/models.py, ids.py,
adapters/, rules/, mapping/loader.py, pipeline.py). Follow SPEC.md exactly (interfaces, names, schemas).
This code will be pasted into step-by-step guides for junior students, so: small functions, clear names,
short comments that explain WHY, no clever tricks, type hints, Python 3.11+ compatible (also runs on 3.13).
Only create/edit the files you own (listed below). If you need a change in a file you do not own, do NOT edit it:
report it in issues_for_lead. Never touch /home/user/maxguard. Never use the network except: PyPI via the
host venv already exists (do not install new packages unless truly needed; if you do, report it), Docker Hub
image pulls, and web search for verifying facts/licenses. Containers have no internet.
Use the host venv: cd ${R} && ./.venv/bin/pytest <your tests> -q ; ./.venv/bin/ruff check <your files>.
Every claim about external tools/standards/licenses must be verified (run it, or cite a primary source URL).
If something cannot be run here, say exactly what and why in not_run (it will be marked "not run - verify on hardware").
Do not git commit (the lead commits). Keep a precise record of commands you ran and their real output
(trimmed) — these become the "expected output" sections of the guides.
Return the structured result.`

const RESULT = {
  type: 'object',
  properties: {
    owner: { type: 'string' },
    files: { type: 'array', items: { type: 'string' }, description: 'paths relative to repo root you created or edited' },
    commands: { type: 'array', items: { type: 'object', properties: {
      command: { type: 'string' }, output: { type: 'string' } }, required: ['command', 'output'] } },
    tests_passed: { type: 'boolean' },
    verified_facts: { type: 'array', items: { type: 'string' }, description: 'facts verified, with source URL or how verified' },
    not_run: { type: 'array', items: { type: 'string' } },
    issues_for_lead: { type: 'array', items: { type: 'string' } },
    doc_notes: { type: 'string', description: 'what a junior needs to know: why decisions, gotchas, explanations' },
  },
  required: ['owner', 'files', 'commands', 'tests_passed', 'verified_facts', 'not_run', 'issues_for_lead', 'doc_notes'],
}

const WAVE1 = [
  { key: 'jaiden-data', prompt: `You own: maxguard/events/normalize.py, maxguard/events/lookup.py, maxguard/storage/state.py,
maxguard/storage/events.py, maxguard/storage/__init__.py, maxguard/events/__init__.py, tests/unit/test_normalize.py,
tests/unit/test_lookup.py, tests/unit/test_state_store.py, tests/unit/test_event_store.py, plus any tests/fixtures/zeek/_handmade/* you need.
Implement the common event schema normalizer exactly as SPEC.md says (deterministic ordering; handle TSV-converted
string values by converting numbers; handle absent logs; eve.json kinds alert/tls/dns/dhcp; skip eve flow).
Hand-write small Zeek 9 dns.log and dhcp.log fixture lines (verify field names against Zeek 9 docs: docs.zeek.org scripts/base/protocols/dns/main.zeek and dhcp/main.zeek; cite).
StateStore: SQLite in WAL mode, schema created on init, alerts deduplicated by finding_id across analyses
(re-upload increases count, widens first/last seen, keeps status/assignee), audit table, ALERT_STATUSES validation,
all times passed in by the caller (never time.time() inside). EventStore: DuckDB writes hourly Parquet partitions
root/date=YYYY-MM-DD/hour=HH/part-<sha>.parquet (UTC), query with read_parquet(hive_partitioning) filters by ip
(src or dst), since/until, ordered by ts,event_id; prune deletes whole hour folders older than a cutoff.
Test everything with the fixtures in tests/fixtures/zeek/*. Also measure: how many bytes per event in Parquet for
the fixtures (report it; it is needed for 7-day retention sizing on a Pi).` },
  { key: 'jonattan-ai', prompt: `You own: maxguard/ai/__init__.py, maxguard/ai/citations.py, maxguard/ai/ollama_client.py,
maxguard/ai/home_text.yaml, maxguard/offline.py, tests/unit/test_citations.py, tests/unit/test_ollama_client.py,
tests/unit/test_offline.py, tests/unit/test_home_text.py.
Implement per SPEC.md AI section. The prompt must give the model the finding facts and the evidence records keyed by
record_id (use maxguard.events.lookup.records_for once it exists; until then accept a records dict argument and in
explain_all import lookup lazily). Use Ollama /api/chat with format=JSON schema, temperature 0, seed 42, stream false.
Config via env OLLAMA_HOST (default http://127.0.0.1:11434) and MAXGUARD_MODEL (default: leave a clearly named
placeholder constant that Ali's evaluation replaces; pick qwen3:4b as the temporary default and say so).
Fix the two bugs found in the Fall 2026 roadmap code: (1) never reuse one finding's explanation for another finding;
(2) the offline guard must also block UDP sendto/sendmsg and DNS lookups via socket.getaddrinfo for non-allowed hosts
(allowed: 127.0.0.1, ::1, localhost, and the Ollama host + its resolved IPs; plus an explicit extra allowlist argument
for user-owned firewalls). Write home_text.yaml with a plain-language headline and one clear action for each of the
13 Fall 2026 rule_ids (8th-grade reading level, no jargon, accurate).
Verify against the real Ollama server API shape: start the container ollama/ollama:0.12.6 (docker run -d --network
none? it needs a port: use docker network or run your test client inside the same container network), call /api/version
and /api/chat with a model that is not present and record the exact error JSON, so the client's error handling is
tested against reality. Also check Docker Hub (https://hub.docker.com/v2/repositories/ollama/ollama/tags) for the newest
stable (non-rc) Ollama version and whether it supports the JSON-schema "format" field (cite Ollama docs/blog).
No model can be pulled in this sandbox (registry blocked): mark real model output as not run.` },
  { key: 'jakub-inventory', prompt: `You own: maxguard/inventory.py, maxguard/rules/ja4.py, maxguard/intel/ja4_watchlist.yaml,
maxguard/intel/__init__.py, maxguard/sensor/__init__.py, maxguard/sensor/attribution.py, tests/unit/test_inventory.py,
tests/unit/test_ja4_rule.py, tests/unit/test_attribution.py, and you MAY add a DNS scenario to the lab:
lab/server/services.py (add a tiny UDP DNS responder on port 53 answering every A query with 10.99.0.7 — stdlib only),
lab/client/scenarios/dns_lookup.py, then rebuild the lab images with ../ccr-build.sh (server: ../ccr-build.sh lab/server lab-server;
client: ../ccr-build.sh lab/client lab-client), record tests/pcaps/dns_lookup.pcap with the lab compose command in SPEC.md,
and generate tests/fixtures/zeek/dns_lookup/ the same way the other fixtures were made (Zeek 9.0.0 -D + community-id +
maxguard/zeek/scripts/*.zeek, plus eve.json from jasonish/suricata:7.0.10 with maxguard/suricata/maxguard-suricata.yaml).
inventory.build(log_dir, findings) -> list of asset dicts per IP: ip, first_seen, services (sorted "port/service"),
software (sorted "name version"), finding_count; deterministic order by IP. Note known_hosts/known_services come from
inventory.zeek (ALL_HOSTS).
rules/ja4.py: rule id tls.ja4_watchlist (severity high) reading eve.json tls events' tls.ja4 and matching against
ja4_watchlist.yaml entries {ja4, label, source} — ship the file with an empty list plus a commented example, because
we must not copy third-party JA4 databases with unknown licenses. Do NOT import it from rules/__init__.py (the lead
decides when it ships); test it by importing directly with a temporary watchlist.
sensor/attribution.py: build a device table from dhcp.log (mac, host_name, assigned_addr) and dns.log (which IP asked
for which names), deterministic. Tests with fixtures.` },
  { key: 'amory-report', prompt: `You own: maxguard/report.py, mappings/pci_dss_4_0_1.yaml, mappings/nist_800_53_r5.yaml,
mappings/cisa_cpg_2_0.yaml, mappings/cjis_6_1.yaml, mappings/schema.md, tests/unit/test_report.py, tests/unit/test_mappings.py.
report.py: to_json(report)->str (sorted keys, indent 2), to_csv(report)->str (one row per finding per control; findings
without controls get one row with empty control columns), to_html(report)->str (standalone page, all values HTML-escaped,
totals by severity, top 10 findings, frameworks affected, the AI sentences with their cited record IDs, NO external
resources/fonts/scripts). Standard library only.
Mapping files: Contract 2 schema. Versions exactly: PCI DSS "4.0.1", NIST SP 800-53 "Rev. 5 (Release 5.2.0)",
CISA CPG "2.0", CJIS "6.1". Sources: primary URLs. IMPORTANT accuracy rule: only include rows whose control ID and
title you verified from a primary source you could actually read (try csrc.nist.gov / NIST CPRT for NIST titles via
web fetch; PCI SSC document library; cisa.gov CPG 2.0; le.fbi.gov CJIS 6.1). Start with cleartext.telnet (the demo
finding) in PCI and NIST. Each row: control_id, title (exact), rationale (your one plain sentence), verified (where
you checked it, e.g. URL + section). If you cannot verify a framework's IDs, ship that file with "mappings: {}" and a
YAML comment explaining that Amory fills it during the Wave 2 task — never guess IDs. mappings/schema.md explains every
field for a non-programmer. test_mappings.py: every YAML loads, has required keys, every rule_id exists in the rule
registry (import maxguard.rules; RULES), versions match the locked table, and validate() from mapping/loader.py returns no problems.` },
  { key: 'fiona-engine', prompt: `You own: cli/main.py, cli/__init__.py, mappings/attack.yaml, tests/unit/test_rules.py,
tests/unit/test_adapters.py, tests/unit/test_merge_determinism.py, tests/unit/test_cli.py, tests/fixtures/zeek/_handmade/rdp/* (you may create).
CLI (python -m cli.main / console script "maxguard"): "maxguard analyze INPUT [-o report.json] [--no-ai] [--offline]
[--frameworks 'PCI DSS,NIST SP 800-53'] [--format json|csv|html]" calling maxguard.pipeline.analyze; --offline enables
maxguard.offline guard before analysis (import lazily; it is being written in parallel); csv/html use maxguard.report
(also parallel; import lazily). Exit codes: 0 ok, 2 bad input (UnsupportedInput), 3 Zeek error.
mappings/attack.yaml (framework "MITRE ATT&CK", version: the exact current Enterprise point release you can verify
(v19.x; search attack.mitre.org versions/changelogs; cite), source URL). Map each of the 13 Fall 2026 rule_ids to the
ATT&CK technique(s) an attacker would use against that weakness, e.g. cleartext credentials -> T1040 Network Sniffing;
verify every technique ID, name, and tactic shortname against attack.mitre.org (via search results if the site is blocked)
and cite; include the "tactic" key; rationale one sentence. If you cannot verify a technique, leave it out.
Tests: positive and negative test for EVERY rule using tests/fixtures/zeek/<capture>/ (each capture triggers exactly one
rule; clean_tls13 none) + a handmade rdp.log fixture (Zeek 9 rdp.log field names — verify, cite) with security_protocol
RDP (positive) and HYBRID (negative); IMAP with service "imap,ssl" negative case via handmade maxguard_cleartext line is
not possible (script skips it) so test the Zeek script logic by reading cleartext.zeek and documenting it instead;
pcap magic accept/reject (pcap, pcapng, txt); TSV conversion of a 3-line conn.log; merge(): duplicates collapse, count,
evidence capped at 5; determinism: run_all twice on every fixture dir gives identical to_dict() output.
CLI test: run with a fixture *log folder* (ZeekLogAdapter path) and --no-ai, check exit code and JSON written.` },
  { key: 'jaiden-platform', prompt: `You own: pyproject.toml, docker/Dockerfile, docker/compose.yaml, docker/compose.dev.yaml,
docker/entrypoint.sh (optional), .github/workflows/ci.yml, maxguard/custody/__init__.py, maxguard/custody/signing.py,
tests/unit/test_signing.py, tests/conftest.py (shared fixtures helper: e.g. FIXTURES path, a fixture_dir(name) helper),
.dockerignore.
pyproject.toml: name maxguard, version 2.0.0a0, requires-python >=3.11, [build-system] setuptools, runtime deps from
SPEC.md with sensible lower bounds, optional dev deps (pytest, ruff, httpx), console script maxguard = "cli.main:main",
package data (zeek/scripts/*.zeek, suricata/*.yaml, suricata/rules/*, ai/*.yaml, intel/*.yaml, web/templates/**, web/static/**),
ruff config (line-length 100), pytest config (testpaths tests, markers: integration).
docker/Dockerfile: FROM zeek/zeek:9.0.0; apt-get install --no-install-recommends python3-venv suricata ca-certificates;
venv at /opt/venv; pip install the package; run as a non-root user; EXPOSE 8000; CMD uvicorn "maxguard.api.app:create_app"
with --factory on 0.0.0.0:8000 and data dir /data (volume). The engine must not need the internet at runtime.
docker/compose.yaml: services maxguard (ports "127.0.0.1:8000:8000", volume maxguard-data:/data, env OLLAMA_HOST=http://ollama:11434,
MAXGUARD_OFFLINE=1, networks ui+ai) and ollama (image ollama/ollama pinned, volume maxguard-ollama-models with fixed name,
network ai internal:true). compose.dev.yaml: build from source and mount the repo.
Verify what you can: "docker compose -f docker/compose.yaml config" must succeed; lint the Dockerfile with
"docker build --check" if supported; you cannot apt-get here (Debian mirrors are blocked) so the real image build is
not run — instead build a SANDBOX-ONLY equivalent to prove the Python side installs and starts: a temporary Dockerfile
FROM zeek/zeek:9.0.0 that skips apt (no suricata) and installs the package with pip from ../deps313-style wheels or
via ../ccr-build.sh, then run "maxguard --help" or python -c "import maxguard.pipeline" inside it. Do not document the
sandbox-only variant. Also verify the zeek/zeek:9.0.0 image's default user and paths.
.github/workflows/ci.yml: job "test" (ubuntu-latest, Python 3.11, pip install -e .[dev], ruff check ., pytest -m "not integration" -q)
and job "integration" (docker build -f docker/Dockerfile -t maxguard:ci .; docker run --rm --network none ... pytest -m integration -q
inside the image; note the image must contain pytest: build a test stage or install pytest before going offline).
Pin GitHub Actions to current major versions (verify: actions/checkout, actions/setup-python latest major as of Oct 2026).
Validate the workflow YAML with actionlint if you can get it (pip install actionlint-py into a temp venv) — report result.
custody/signing.py: Ed25519 with the cryptography library: generate_keypair(dir) writing private key 0600 + public key PEM,
sign(data: bytes, private_key_path) -> bytes, verify(data, signature, public_key_path) -> bool, key files never inside the repo
(document data dir). Tests.` },
  { key: 'ali-eval', prompt: `You own: scripts/benchmark_models.py, scripts/make_eval_set.py, tests/fixtures/ai_eval/eval_set.json,
tests/unit/test_benchmark.py, docs-draft/model-eval-template.md (a draft the lead will move into the docs).
make_eval_set.py builds the evaluation set from the real fixtures: for each fixture dir in tests/fixtures/zeek/ (except
clean_tls13) run the rules (maxguard.rules.base.run_all) and the mapping loader with mappings/ if present, and store each
finding dict together with its evidence records (record_id -> raw record, found by scanning the fixture logs with
maxguard.ids.record_id) — deterministic output, committed as eval_set.json.
benchmark_models.py: for each model tag given on the command line, warm up, then for each eval item call the PRODUCTION
explain() from maxguard.ai.ollama_client (being written in parallel: import it, do not copy it; until it exists, write
against the SPEC.md signature explain(finding: dict, records: dict) -> (sentences, dropped)). Record per item: seconds,
sentences kept, sentences dropped by the citation validator, and an automatic "unsupported detail" check: every IP address,
port number, hostname, TLS version, and cipher string mentioned in the text must appear in the finding or its cited
records (regex-based; explain the regexes). Write docs/model-eval/raw_results.csv and print a per-model summary
(median seconds, drop rate, unsupported-detail count). Two hardware tiers: a --tier pi|laptop flag that only labels results.
Run the benchmark twice and compare outputs to check determinism (temperature 0, seed 42).
Shortlist (verify each model's license from a primary source — the model card/license file; ollama.com and huggingface.co are
blocked here, use web search results that quote the license or GitHub repos): Pi tier <= 4B: qwen3:4b, llama3.2:3b, phi4-mini,
gemma3:4b; laptop tier <= 8B: qwen3:8b, llama3.1:8b, granite3.3:8b (or newest granite if verified). For each: license name,
whether redistribution in our offline bundle is allowed and what attribution/notice it requires, source URL.
Unit-test the benchmark logic with a fake explain function (no network). No model can be pulled here: mark real runs as not run.` },
]

const WAVE2 = [
  { key: 'jaiden-api', prompt: `You own: maxguard/api/__init__.py, maxguard/api/app.py, tests/unit/test_api.py, tests/integration/test_api_upload.py.
Implement the FastAPI app exactly per SPEC.md (create_app(data_dir, explain=True), app.state stores, routers included if
present, /static mount, endpoints, SSE /api/stream using an asyncio-friendly approach: StreamingResponse with
text/event-stream that emits "alerts-changed" when a version counter in app.state changes; include a heartbeat comment
line every 15 s; make it testable by allowing a max_events query param for tests). Upload handling: save to a temp dir
inside data_dir/uploads with a safe generated filename (never trust the client filename for paths), run
pipeline.analyze(explain=app setting), EventStore.write(report["events"]), StateStore.save_analysis(report, received_at=time.time())
(the API layer is allowed to read the clock; the engine is not), bump the version counter, delete the upload unless
MAXGUARD_KEEP_UPLOADS=1. Limit upload size (MAXGUARD_MAX_UPLOAD_MB default 1024). Reject unsupported files with 400.
Machine ingest for sensors and host agents on the LAN: add POST /api/ingest (same behavior as /api/analyses) that is
DISABLED (404) unless env MAXGUARD_INGEST_TOKEN is set, and then requires "Authorization: Bearer <token>" compared with
hmac.compare_digest (401 otherwise). /api/analyses stays token-free because the dashboard on 127.0.0.1 uses it. Document in
the module docstring that publishing the ingest port on the LAN is an explicit, optional user choice (CLAUDE.md rule 1).
The report "ai" dict now has a "reason" key (None or why the AI was unavailable); keep it when saving/returning.
StateStore already handles identical re-uploads (same sha256: no double count) and reopens resolved alerts that come back —
do not re-implement that; just call save_analysis.
Unit tests with TestClient monkeypatching pipeline.analyze to return a report built from fixtures (run_all on a fixture dir).
Integration test (marked integration) that uploads tests/pcaps/telnet.pcap for real: run it inside the zeek/zeek:9.0.0
container per SPEC.md harness (deps in ../deps313) and record output. Also start uvicorn inside the Zeek container
(--network none is fine; curl from inside the container) and record a real curl of /api/alerts after an upload.` },
  { key: 'ahmad-ui', prompt: `You own: maxguard/web/__init__.py, maxguard/web/routes.py, maxguard/web/templates/*.html,
maxguard/web/static/app.css, maxguard/web/static/app.js, tests/unit/test_web.py. htmx is already vendored at
maxguard/web/static/htmx-2.0.11.min.js (0BSD) — reference it locally, never a CDN.
Pages (Jinja2 server-rendered, htmx for partial updates, no build step): base.html (nav, mode toggle Analyst/Home stored in a
cookie "mg_mode", privacy note "Your data never leaves this computer."), / alert queue (table: severity, title, src -> dst:port,
count, status, assignee, last seen; filters by status/severity via hx-get; refreshes when the SSE /api/stream says
"alerts-changed" using a tiny app.js with EventSource that calls htmx.trigger; fallback hx-trigger every 30s),
/alerts/{finding_id} detail (Analyst mode: evidence table with record_id, log, uid, ts; controls grouped by framework with
version; ATT&CK techniques; AI sentences each followed by citation chips linking to the evidence rows; status/assignee form
using hx-patch or hx-post to an HTML endpoint that calls StateStore.update_alert and returns the updated fragment.
Home mode: headline + one action from maxguard/ai/home_text.yaml, severity in plain words, no jargon),
/upload (form posting the file to /api/analyses via a normal form or hx-post with hx-encoding multipart),
/timeline?ip= (events from EventStore.query, ordered by time, with ATT&CK techniques of findings involving that IP),
/assets (latest analysis assets). When the stored report's ai.status is "unavailable", show a clear banner with ai.reason
(for example "model 'qwen3:4b' not found: run ollama pull qwen3:4b"). Escape everything (Jinja2 autoescape on); AI text and
anything from network traffic must never be marked |safe (prompt-injection / XSS). Keyboard accessible, color is never the only
signal (severity text + color), works at 375px width. Reach stores via request.app.state.
Tests with TestClient using create_app(tmp_path, explain=False) and data saved via StateStore/EventStore from fixtures:
pages return 200, contain expected elements, mode toggle changes content, status update works and writes audit.
Take screenshots of the queue, detail (both modes) and timeline pages with Playwright + Chromium (preinstalled:
PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers; launch with executablePath '/opt/pw-browsers/chromium' if needed; python
playwright may need pip install into a temp venv) by running uvicorn on 127.0.0.1 with a seeded data dir; save PNGs to
${R}/screens/ and report the paths.` },
  { key: 'ahmad-response', prompt: `You own: maxguard/response/__init__.py, maxguard/response/generate.py, maxguard/response/preview.py,
maxguard/response/approvals.py, maxguard/response/routes.py, maxguard/response/enforcers/__init__.py,
maxguard/response/enforcers/base.py, maxguard/response/enforcers/opnsense.py, tests/unit/test_response_*.py.
CLAUDE.md rule 4: blocking only on the user's own network, explicit human approval, reversible, logged; no hack-back.
generate.py: given a validated IP (ipaddress module; reject anything else to prevent injection) and direction
(inbound|outbound|both) produce: nftables commands (add rule + matching delete/undo command using a named set
"maxguard_block" so undo is simple), iptables commands (with undo), OPNsense manual steps (Firewall > Aliases), and
plain-English steps for a home router. Verify nftables syntax for real: run nft --check in a container if any image has
nft (e.g. nicolaka/netshoot has nft? check) — record. 
preview.py: given a proposed block and EventStore, look back 7 days (window end passed in, never read the clock) and
return what would have been blocked: number of connections, internal devices affected, services/ports, first/last seen,
top 10 sample events (event_id, ts, summary) — deterministic ordering.
approvals.py: proposal lifecycle stored via StateStore (add the tables you need via a small helper that runs CREATE TABLE IF
NOT EXISTS on the same SQLite file; do not edit state.py — if you need a StateStore change report it): propose -> approve
(requires actor name and typed confirmation of the IP) -> applied (manual or enforcer) -> reverted; every step audited with
StateStore.add_audit.
enforcers/opnsense.py: OPNsense REST API client: add/remove an address to a firewall alias (POST /api/firewall/alias_util/add/{alias}
and /delete/{alias}, verify the exact endpoints and request body from OPNsense docs and cite), then apply
(/api/firewall/alias/reconfigure — verify). Uses requests with HTTP basic auth key/secret from a config file outside the repo,
TLS verification on by default with a CA path option. The offline guard must allow ONLY this configured firewall host.
Test with a fake OPNsense HTTP server (http.server in a thread on 127.0.0.1) — never a real firewall.
routes.py: APIRouter under /api/response: POST /proposals, GET /proposals, POST /proposals/{id}/preview,
POST /proposals/{id}/approve, POST /proposals/{id}/revert; HTML fragments optional. Tests with TestClient.` },
  { key: 'amory-custody', prompt: `You own: maxguard/custody/log.py, tests/unit/test_custody.py.
Tamper-evident chain of custody using maxguard/custody/signing.py (written by Jaiden in wave 1 — read it).
append(log_path, *, action, artifact_path, actor, at, private_key_path) -> dict entry: seq, at (passed in), action
("capture_received", "report_generated", "report_exported", ...), artifact name, artifact sha256, size, actor, prev_hash,
entry_hash = sha256 of canonical JSON of the entry without entry_hash/signature, signature = Ed25519 over entry_hash (base64).
verify(log_path, public_key_path) -> (ok: bool, first_bad_seq: int | None, reason: str). JSON Lines file.
Tests: good chain verifies; editing any field, deleting a line, reordering lines, or a wrong key all fail with the right seq.
Also write a tiny CLI entry in the same module: python -m maxguard.custody.log verify <log> <pubkey>.` },
  { key: 'karthik-tests', prompt: `You own: tests/expected/*.json, tests/integration/test_pcaps.py, tests/integration/test_determinism.py,
tests/integration/__init__.py (if needed), tests/pcaps/SOURCES.md, lab/README.md, docs-draft/test-results.md.
Expected-result files for every capture in tests/pcaps/ (format from the Fall 2026 roadmap: capture, expected [{rule_id,
dst_port, min_count}], must_not_contain) — clean_tls13 expects zero findings (add "expect_no_findings": true and test it).
test_pcaps.py: parametrized over expected files, runs maxguard.pipeline.analyze(..., explain=False), mark integration.
test_determinism.py: runs analyze twice on each capture and asserts the full report dicts (minus nothing) are identical.
Run the integration tests for real inside zeek/zeek:9.0.0 per SPEC.md (deps in ../deps313, --network none) and record the
output. SOURCES.md: every capture is synthetic from lab/ (scenario, date, tool versions) — no third-party captures.
lab/README.md: how to run the lab, list of scenarios and which rule each triggers, the gotchas (SHA-1 via openssl CLI,
no 3DES so NULL-SHA256, http.py name shadowing, lab CA so each capture triggers one rule).
docs-draft/test-results.md: a Wireshark-style cross-check table. tshark is not installed on the host; try the image
cincan/tshark or any tshark image on Docker Hub (check it exists and its license/maintainer) to count sessions per capture
with display filters (telnet, ftp, http.request, pop, imap, tls.handshake.type == 2 && tls.handshake.version <= 0x0302)
and compare with MaxGuard's counts. If no image works, mark not run.` },
]

const WAVE3 = [
  { key: 'jakub-live', prompt: `You own: maxguard/adapters/live.py, maxguard/zeek/scripts/live/rotate.zeek (if needed),
docker/sensor-compose.yaml, maxguard/suricata/maxguard-suricata-live.yaml, tests/unit/test_live_adapter.py,
maxguard/sensor/shipper.py, tests/unit/test_shipper.py, docs-draft/live-sensor-notes.md.
Live sensor for the Pi (ARM64) and x86: Zeek 9.0.0 (zeek/zeek:9.0.0, NO -D in live mode) listening on the capture
interface with network_mode host, cap_add NET_RAW and NET_ADMIN, writing JSON logs that rotate every hour into
/data/zeek/<YYYY-MM-DD-HH>/ (find the correct Zeek 9 way to rotate without zeekctl: Log::default_rotation_interval and
a rotation postprocessor or Log::rotation_format_func — verify in Zeek docs and by running it); Suricata 7.0.17
(jasonish/suricata:7.0.17 — the lead pinned this newer 7.0.x for security fixes; fixtures stay on 7.0.10 output) with
af-packet on the same interface writing eve.json rotated hourly (verify the eve "rotate-interval" option for 7.0.x).
KNOWN PROBLEM to solve first: the lead ran Zeek live with 'docker run --network container:<web> --cap-add NET_RAW
--cap-add NET_ADMIN zeek/zeek:9.0.0 timeout 20 zeek -i eth0 -C LogAscii::use_json=T local' and it captured 449 packets,
but Suricata in the same setup saw 0 packets, both with '--entrypoint timeout ... suricata --af-packet=eth0 -k none',
with '--pcap=eth0', and via the image's own entrypoint ('jasonish/suricata:7.0.17 -i eth0 -k none', stopped after 18 s).
Find out why (config? capture mode? threads? the entrypoint dropping to the suricata user? timing?) and produce a
VERIFIED one-minute live Suricata command for docs/HARDWARE.md section 11.3 (Pi: --network host, capture iface eth0),
with its real output. The live config must use MaxGuard's eve settings (community-id, JA4 on, types as in
maxguard-suricata.yaml).
Batching for EventStore writes: 5-15 minutes (see SPEC lead decisions). The sensor ships each COMPLETED hour folder
(Zeek logs + that hour's eve.json) to the console as a .tar.gz via POST /api/ingest with "Authorization: Bearer <token>"
(Jaiden's API; ZeekLogAdapter already accepts .tar.gz) — write that small shipper as maxguard/sensor/shipper.py with tests
against a fake HTTP server. Both containers are passive: never transmit (CLAUDE.md rule 5) — document that the
capture interface has no IP address and how to set that on Raspberry Pi OS.
LiveSensorAdapter (Contract 3 unchanged): accepts a sensor data folder; to_zeek_logs returns the newest COMPLETED hour
folder (ignore the current hour), merging the Suricata eve.json for that hour into it.
PROVE live capture works here: create a docker network, run a container that generates traffic (python http.server +
curl/urllib loop) and run zeek -i eth0 in a container sharing its network namespace (network_mode container:<name>) with a
1-minute rotation interval for the test; show that rotated JSON logs appear and contain the traffic. Same for Suricata
af-packet. Record exact commands/output. Raspberry Pi specific steps are not runnable here: list them as not run.` },
  { key: 'jakub-netflow-agent', prompt: `You own: maxguard/adapters/netflow.py, maxguard/sensor/agent.py, docker/netflow-compose.yaml,
tests/unit/test_netflow.py, tests/unit/test_agent.py, docs-draft/netflow-agent-notes.md.
NetFlow/IPFIX: use goflow2 (netsampler/goflow2 on Docker Hub — verify image, version, license BSD-3?) as the collector writing
JSON lines; NetflowAdapter (Contract 3) converts goflow2 records into conn.log-style JSON records in a log dir (fields ts, uid
= deterministic hash of the flow record, id.orig_h, id.orig_p, id.resp_h, id.resp_p, proto, orig_bytes, resp_bytes,
duration, mg_source "netflow") so the existing rules and normalizer can read them (payload-based rules simply find nothing).
PROVE it: run goflow2 in Docker, send real NetFlow v5 (and if feasible v9/IPFIX) packets to it from a small Python generator
(struct-packed v5 header + records, all fake RFC 5737 addresses), capture its JSON output, convert, and run normalize/rules.
Record commands/output.
Host agent (sensor/agent.py): for one machine; builds the capture command per OS without third-party capture drivers:
Linux/macOS tcpdump with -G rotation; Windows pktmon (built in: "pktmon start --capture --pkt-size 0 -f file.etl" then
"pktmon etl2pcap") — verify these commands/flags from Microsoft docs and tcpdump man page and cite; then uploads each
finished capture to the console API POST /api/ingest with requests and "Authorization: Bearer <token>" (console URL and
token from a config file outside the repo; document that the console must be the user's own machine and that the ingest
endpoint is disabled unless MAXGUARD_INGEST_TOKEN is set on the console). Test with a fake server; never run captures on
this host. You own maxguard/sensor/agent.py (not shipper.py, which belongs to the live-sensor task).` },
  { key: 'fiona-spring', prompt: `You own: maxguard/decoy/__init__.py, maxguard/decoy/service.py, maxguard/rules/decoy.py,
maxguard/rules/baseline.py, docker/decoy-compose.yaml, tests/unit/test_decoy.py, tests/unit/test_baseline.py, docs-draft/decoy-baseline-notes.md.
Decoys (CLAUDE.md rule 5: own IP, only answers, never initiates): decoy/service.py runs asyncio TCP listeners on
configured ports with fake banners (telnet "login:", FTP "220", HTTP 200 page "Printer admin"), logs every connection as a
JSON line in decoy.log (ts, src_ip, src_port, dst_ip, dst_port, first 64 bytes as hex), closes after a short timeout, never
connects anywhere. docker/decoy-compose.yaml gives it its own LAN IP with a macvlan network (document parent interface
config; verify macvlan compose syntax with docker compose config). rules/decoy.py: rule decoy.contact (critical) reading
decoy.log. Prove it in Docker: run the decoy in a container network, connect from another container, run the rule on the
produced log.
Baselines: rules/baseline.py — deterministic. build_baseline(events: list[dict]) -> dict per device IP: set of
(dst_port, proto, service) seen and peers count. A stateful rule baseline.new_service: given a baseline (input, never read
from disk implicitly) and a log dir, flag a device using a (dst_port, proto, service) not in its baseline after the learning
period. Design a small registry STATEFUL_RULES with a @stateful_rule decorator taking (log_dir, context) so it does not
change Contract 3 or run_all. Do NOT import these from rules/__init__.py (spring feature). Tests with fixtures.` },
  { key: 'jaiden-spring', prompt: `You own: maxguard/intel/bundle.py, .github/workflows/release.yml, tests/unit/test_intel_bundle.py,
docs-draft/release-notes.md.
Signed offline intel bundles delivered on USB: build_bundle(src_dir, out_path, private_key_path, *, version) creates a
tar.gz containing manifest.json (version, files with sha256 and size, created_by) and manifest.sig (Ed25519 over the
manifest bytes, using maxguard.custody.signing). verify_bundle(path, public_key_path) checks the signature BEFORE extracting
anything, then every file hash, and rejects absolute paths, "..", symlinks, device files, and files not in the manifest
(extract with tarfile filter="data"). install_bundle(path, public_key_path, dest_dir) installs atomically (temp dir + rename)
and keeps the previous version for rollback. Allowed content: suricata rules (*.rules), ja4 watchlist, mapping YAML updates.
Tests: good bundle installs; tampered file, tampered manifest, wrong key, path traversal entry, extra file all rejected.
release.yml: on tags v*, build and push multi-arch (linux/amd64, linux/arm64) image to ghcr.io/ahmadalkhoudeir/maxguard
with docker/setup-qemu-action, docker/setup-buildx-action, docker/login-action (GITHUB_TOKEN), docker/build-push-action;
permissions packages: write, contents: write; also generate SHA256SUMS and attach to the GitHub Release. Pin actions to
current majors (verify). Validate with actionlint (pip install actionlint-py in a temp venv) and report.` },
  { key: 'jonattan-bundle', prompt: `You own: scripts/build-offline-bundle.sh, scripts/install.sh, scripts/uninstall.sh,
docs-draft/offline-install-notes.md, tests/unit/test_bundle_scripts.py (shellcheck-like checks via bash -n).
Offline bundle for v2.0 (adapt the Fall 2026 roadmap's scripts to the new compose file docker/compose.yaml and the API on
port 8000): images.tar (docker save of the MaxGuard image and the pinned Ollama image), models.tar.gz (the Ollama model
volume maxguard-ollama-models), compose.yaml, install.sh, OFFLINE-INSTALL.md, SHA256SUMS (sha256sum, with a macOS
"shasum -a 256" note), split into < 2 GiB parts. install.sh verifies checksums before loading anything.
Make the scripts parameterizable by env vars (MG_IMAGE, OLLAMA_IMAGE, MAXGUARD_MODEL) so they can be tested here:
PROVE the mechanics by running build-offline-bundle.sh with MG_IMAGE=python:3.11-slim-bookworm (stand-in) and
OLLAMA_IMAGE=ollama/ollama:0.12.6 and a fake small model directory placed into the volume (since models cannot be pulled
here), then run install.sh in a clean state (remove the volume first) and confirm images load, volume is restored and
checksums verify; then tamper one part and confirm install refuses. Run shellcheck if obtainable (pip install shellcheck-py
in a temp venv) and fix warnings. Record outputs. Real model pull is not run.` },
  { key: 'jakub-ja4-integrate', prompt: `You own nothing new except tests/integration/test_suricata_eve.py and docs-draft/suricata-notes.md.
Verify Suricata integration end to end with the real jasonish/suricata:7.0.10 image: for every capture in tests/pcaps run
Suricata with maxguard/suricata/maxguard-suricata.yaml and -S maxguard/suricata/rules/maxguard.rules, confirm eve.json has
community_id on every event, JA4 on every TLS client hello event (list them per capture), and that
maxguard.events.normalize produces events with ja4 filled for those. Also run Suricata 8.0.7 (jasonish/suricata:8.0.7) with
the same config and report any config warnings/differences. Write a pytest integration test that, given a directory of
eve.json files, checks those properties (it runs against tests/fixtures/zeek/*/eve.json in CI). Document the 7.0 vs 8.0
differences and the Debian 13 package (1:7.0.10-1+deb13uX) note.` },
]

async function runWave(name, tasks) {
  phase(name)
  const results = await parallel(tasks.map(t => () =>
    agent(`${COMMON}\n\nOWNER/TASK: ${t.key}\n${t.prompt}`, { label: t.key, phase: name, schema: RESULT })
      .then(r => r ? { ...r, owner: t.key } : null)))
  const ok = results.filter(Boolean)
  log(`${name}: ${ok.length}/${tasks.length} returned; tests passed: ${ok.filter(r => r.tests_passed).map(r => r.owner).join(', ')}`)
  return ok
}

const w1 = await runWave('Wave 1', WAVE1)
const w2 = await runWave('Wave 2', WAVE2)
const w3 = await runWave('Wave 3', WAVE3)

phase('Integrate')
const issues = [...w1, ...w2, ...w3].flatMap(r => (r.issues_for_lead || []).map(i => `[${r.owner}] ${i}`))
const integ = await agent(`${COMMON}

OWNER/TASK: integrator. You may edit ANY file in ${R} now (but keep each module's design; make minimal fixes).
All modules have been built by separate builders. Your job:
1. Read every issue below and resolve the ones that are real (cross-module mismatches, missing hooks, pyproject deps,
   rules/__init__ imports, pipeline integration). Do not ship spring features in rules/__init__.py.
2. Run ./.venv/bin/ruff check . and fix everything.
3. Run ./.venv/bin/pytest -m "not integration" -q (all unit tests) and make it pass.
4. Run the integration tests inside zeek/zeek:9.0.0 per SPEC.md (deps in ../deps313; rebuild ../deps313 with pip --target for
   python 3.13 manylinux if new deps were added) with --network none, twice, and make them pass.
5. Run the full pipeline via the CLI inside the Zeek container on tests/pcaps/telnet.pcap with --no-ai and save the report
   to ${R}/screens/telnet-report.json; also produce CSV and HTML exports.
6. Start the API (uvicorn) inside the Zeek container, upload telnet.pcap and tls_weak_version.pcap with curl, fetch
   /api/alerts and the HTML queue page; record outputs.
7. Write ${R}/INTEGRATION.md summarizing: final file list per owner, all test commands with their final real output,
   remaining known gaps, everything not run and why.
Issues reported by builders:\n${issues.join('\n') || '(none)'}`, { label: 'integrator', phase: 'Integrate', schema: RESULT })

return { wave1: w1, wave2: w2, wave3: w3, integrator: integ }
