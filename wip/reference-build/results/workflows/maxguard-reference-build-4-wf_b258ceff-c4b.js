export const meta = {
  name: 'maxguard-reference-build-4',
  description: 'Build the six remaining MaxGuard v2.0 design tasks; adversarial review of the response module, live sensor and dashboard',
  phases: [
    { title: 'Build', detail: 'live sensor (continue), response, decoys/baselines, netflow/agent, release/bundle, dashboard' },
    { title: 'Review', detail: 'adversarial review of the security-critical builds' },
  ],
}

const R = args.ref

const COMMON = `
You are building ONE part of the MaxGuard v2.0 reference implementation in the scratch repo at ${R}. Today is October 6, 2026.
Read first, in this order:
1. ${R}/SPEC.md completely. Its last sections ("Lead decisions after the planning docs", "API contract the builders code against", "Zeek: never load Zeek's own local policy") are binding and override older text above them.
2. Your task sections in ${R}/docs-spec/roadmap/<person>.md (named below). The published steps are the spec: build exactly what they say (same file paths, function names, signatures, settings, test files). If a step is wrong or impossible, build the closest correct thing and explain the difference in issues_for_lead (the lead fixes the docs). Do not edit docs-spec/.
3. The docs-spec/ARCHITECTURE.md sections your task references, and the existing code you depend on. maxguard/api/app.py exists (the API, written by the lead): read it, do not edit it. The integration tests (tests/integration/) and expected results exist too.
Code style: this code is pasted into step-by-step guides for junior students: small functions, clear names, short comments that explain WHY, no clever tricks, type hints, Python 3.11+ (also runs on 3.13). Module docstrings name the person and task, e.g. "(Ahmad, AHM-07)".
Ownership: only create or edit the files you own (listed below). Other builders and reviewers work in the same repo at the same time: never edit, reformat, move or delete a file you do not own; run ruff only on your own files (./.venv/bin/ruff check <files>), never --fix or format on the whole repo. Need a change elsewhere? Put it in issues_for_lead. If a test of yours fails because of another module that is being written right now, wait a little and re-run, or report it.
Never touch /home/user/maxguard. Do not git commit (the lead commits).
Network: do not install packages into ./.venv (it already has everything in pyproject.toml; a throwaway venv under /tmp for a tool such as actionlint or playwright is fine). Docker Hub pulls of small public images are fine: record tag, digest and license, and remove them when done unless your result needs them (disk: about 12 GB free; never docker save a big image). Web search/fetch only to verify facts and licenses from primary sources (official docs, man pages, upstream repositories; raw.githubusercontent.com works when a docs site is blocked). Containers have no internet. Test data: lab captures, fixtures, or documentation addresses only (192.0.2.0/24, 198.51.100.0/24, 203.0.113.0/24, 2001:db8::/32); nothing may contact a real external host.
Docker: if docker info fails, the sandbox restarted: run (setsid nohup dockerd --data-root /tmp/claude-0/dockerd/data > /tmp/claude-0/dockerd/dockerd.log 2>&1 &) and wait until docker info works. Prefix every container, network and volume you create with your key (for example "jakub-live-") and remove them when done. Never write root-owned files into ${R} from a container (use --user $(id -u):$(id -g), PYTHONDONTWRITEBYTECODE=1 and -p no:cacheprovider, or write to /tmp and copy out). Never use foreground sleep to wait; poll with a bounded until-loop.
Tests: cd ${R} && ./.venv/bin/pytest <your tests> -q. Every claim about an external tool, standard or license must be verified: run it, or cite a primary-source URL.
Anything that cannot run here (Raspberry Pi, real router or firewall, real AI model, GitHub Actions) goes in not_run with exactly what and why; it becomes "not run - verify on hardware" in the docs.
Time box: when one problem resists about three serious attempts, stop, record what you tried and saw, and move on.
Record the commands you ran and their real output (trimmed): they become the "expected output" sections of the guides.
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

const REVIEW = {
  type: 'object',
  properties: {
    owner: { type: 'string' },
    verdict: { type: 'string', enum: ['good', 'fixed', 'needs-lead'] },
    fixed: { type: 'array', items: { type: 'object', properties: {
      file: { type: 'string' }, problem: { type: 'string' }, fix: { type: 'string' } }, required: ['file', 'problem', 'fix'] } },
    findings: { type: 'array', items: { type: 'object', properties: {
      severity: { type: 'string', enum: ['blocker', 'major', 'minor'] }, file: { type: 'string' },
      problem: { type: 'string' }, suggestion: { type: 'string' } }, required: ['severity', 'file', 'problem', 'suggestion'] } },
    mutations: { type: 'array', items: { type: 'string' }, description: 'mutations tried and whether the tests caught them' },
    verified_facts: { type: 'array', items: { type: 'string' } },
    commands: { type: 'array', items: { type: 'object', properties: {
      command: { type: 'string' }, output: { type: 'string' } }, required: ['command', 'output'] } },
    tests_passed: { type: 'boolean' },
  },
  required: ['owner', 'verdict', 'fixed', 'findings', 'mutations', 'verified_facts', 'commands', 'tests_passed'],
}

const REVIEWED = new Set(['jakub-live', 'ahmad-response', 'ahmad-ui'])

const BUILDERS = [
  { key: 'jakub-live', prompt: `TASKS: JAK-07 in docs-spec/roadmap/jakub.md (live sensor) and the three open questions at the end of docs-spec/ARCHITECTURE.md section 4 (see also docs-spec/HARDWARE.md section 11.3).
You own: maxguard/zeek/scripts/live/rotate.zeek, maxguard/suricata/maxguard-suricata-live.yaml, docker/sensor-compose.yaml, maxguard/adapters/live.py, maxguard/sensor/shipper.py, tests/unit/test_live_adapter.py, tests/unit/test_shipper.py, docs-draft/live-sensor-notes.md.
YOU ARE CONTINUING AN INTERRUPTED ATTEMPT. An earlier builder for this same task was stopped by a usage limit after doing most of the work. Its files above already exist (untracked) and its scratch folder is ${R}/../jakub-live (its containers were removed). What it established (re-check anything you rely on):
1. The 0-packet mystery: jasonish/suricata:7.0.17 ships the ET Open rule set (53,021 rules in /var/lib/suricata/rules/suricata.rules); loading it took about 50 s on this 4-core machine, and Suricata captures nothing until loading finishes, so the 18-20 s planning tests stopped before capture began (with -S /dev/null, capture started after 0.7 s: 241 packets in 20 s). jasonish/suricata:8.0.7 ships no rules file and starts in about a second; the HARDWARE.md 11.3 smoke command (-i eth0, 60 s, NET_ADMIN NET_RAW SYS_NICE) captured 738 packets here. The lead already put this into HARDWARE.md 11.3.
2. Rotation: Zeek with Log::default_rotation_interval and Log::rotation_format_func writes /data/zeek/<YYYY-MM-DD-HHMM>/ folders (tested with 1 minute); Suricata 8's eve rotation wrote one eve-YYYY-MM-DD-HHMM.json per interval in /data/spool/suricata.
3. End to end: the sensor compose stack ran with a 1-minute interval and the shipper sent a finished folder to the console's POST /api/ingest (HTTP 200).
4. Zeek's own local policy makes DNS lookups. The lead fixed it (SPEC.md last section): docker/sensor-compose.yaml loads maxguard/zeek/site.zeek instead of local, and the detect-MHR workaround was removed from rotate.zeek. Keep it that way; tests/unit/test_zeek_site.py must pass.
5. From NetworkManager's own source (raw.githubusercontent.com/NetworkManager/NetworkManager): ipv4.method and ipv6.method "disabled", ethernet.accept-all-mac-addresses (promiscuous mode, since 1.32), ethtool option names feature-gro / feature-lro.
Remaining work: (a) review and finish every file above against JAK-07's steps (fix anything wrong; the shipper reads the clock only in its main loop); (b) re-run the end-to-end proof once with the final files and record the real outputs: rotated folders, eve files, the shipper's log line with HTTP 200, and the alert in the console's /api/alerts with the sensor's sensor_id (start the console with ./.venv/bin/uvicorn maxguard.api.app:create_app --factory on 127.0.0.1 with MAXGUARD_INGEST_TOKEN set (at least 32 characters) and a data dir under /tmp; the AI will report itself unavailable, which is fine); (c) write docs-draft/live-sensor-notes.md: the capture port with no IP address and the nmcli commands for Raspberry Pi OS Trixie, the compose file, the rotation answers, the 0-packet cause, the site.zeek fix, and every Pi step you could not run; (d) in issues_for_lead give the exact line that adds LiveSensorAdapter to ADAPTERS in maxguard/pipeline.py, where in the order, and how accepts() tells a sensor data folder from a plain Zeek log folder (do not edit pipeline.py yourself); (e) remove every container, network and volume prefixed jakub-live when done.` },

  { key: 'ahmad-response', prompt: `TASKS: AHM-07 and AHM-08 in docs-spec/roadmap/ahmad.md, with docs-spec/ARCHITECTURE.md section 13.
You own: maxguard/response/__init__.py, maxguard/response/generate.py, maxguard/response/preview.py, maxguard/response/approvals.py, maxguard/response/routes.py, maxguard/response/enforcers/__init__.py, maxguard/response/enforcers/base.py, maxguard/response/enforcers/opnsense.py, tests/unit/test_response_generate.py, tests/unit/test_response_preview.py, tests/unit/test_response_approvals.py, tests/unit/test_response_routes.py, tests/unit/test_opnsense.py, docs-draft/response-notes.md.
CLAUDE.md rule 4 is the heart of this task: blocking applies only to networks the user owns or administers, always needs explicit human approval, is reversible, and is logged; no hack-back; nothing is ever sent toward the blocked address.
- generate.py rules_for(ip, direction): as in AHM-07 step 2. Verify the nftables syntax for real with nft -c -f <file> in a container that has nft (nicolaka/netshoot:v0.15 probably does; --network none plus the capabilities nft needs; record), and the iptables syntax as far as possible (iptables-restore --test, or explain).
- preview.py: as in AHM-07 step 4 (window_end passed in, never the clock; deterministic order).
- approvals.py: as in AHM-08 step 2. States proposed -> approved -> applied -> reverted (add rejected if you think it is needed; explain). Approve needs actor and confirm_ip equal to the proposal's IP. Every change is audited with StateStore.add_audit (actor, action "response.<step>", target = proposal id). Times are passed in by the caller.
- routes.py: APIRouter as in AHM-08 step 3. Routes read the stores from request.app.state (SPEC.md API contract) and may read the clock (time.time()) like the API does. Test with TestClient(create_app(tmp_path, explain=False)) from maxguard/api/app.py (it includes your router when maxguard/response/routes.py imports); the API refuses cross-site changes (Origin or Sec-Fetch-Site), so plain TestClient calls work.
- enforcers: base.py Enforcer protocol (add(ip), remove(ip), apply()); opnsense.py client for the alias API. Verify the exact endpoints and request formats from the OPNsense documentation (docs.opnsense.org API reference, or the OPNsense source on GitHub) and cite them. requests with HTTP basic auth (key and secret from a file in the data folder, never in the repository), TLS verification on by default with a CA bundle option, short timeouts. Read maxguard/offline.py: document adding the firewall to MAXGUARD_OFFLINE_ALLOW and test that the enforcer works with the guard on and the firewall allowed. Tests use a fake OPNsense server (http.server in a thread on 127.0.0.1), never a real firewall.
- Tests include hostile input such as "1.2.3.4; rm -rf /", IPv6, refusal of loopback/multicast/unspecified/link-local, approval with a missing or wrong typed IP, an audit row for every step, and revert removing the address.` },

  { key: 'fiona-spring', prompt: `TASKS: FIO-06 and FIO-07 in docs-spec/roadmap/fiona.md, with docs-spec/ARCHITECTURE.md section 5 (STATEFUL_RULES).
You own: maxguard/decoy/__init__.py, maxguard/decoy/service.py, maxguard/decoy/__main__.py (optional), maxguard/rules/decoy.py, maxguard/rules/baseline.py, docker/decoy-compose.yaml, tests/unit/test_decoy.py, tests/unit/test_baseline.py, docs-draft/decoy-baseline-notes.md.
Decoys follow CLAUDE.md rule 5: own IP address, only answers, never initiates a connection, never on a capture interface. service.py as in FIO-06 step 2 (asyncio; configurable ports; the banners; decoy.log JSON lines with ts, src_ip, src_port, dst_ip, dst_port and the first 64 bytes as hex; a short timeout; cap the bytes read; survive garbage input). Rule decoy.contact (critical) reads decoy.log from the log folder; Finding fields per Contract 1 (maxguard/models.py) with evidence record IDs (maxguard/ids.py) so the AI can cite them. Do not register it in maxguard/rules/__init__.py (the rule ID needs approval): show how a test imports it.
docker/decoy-compose.yaml: its own LAN address on a macvlan network, the parent interface as a variable with a documented default; validate with docker compose -f docker/decoy-compose.yaml config. Also prove the decoy in Docker: run it in a container on a user-defined bridge network (macvlan needs a real NIC: explain), connect from another container (nc or curl in nicolaka/netshoot:v0.15), copy out decoy.log, and run the rule on it. Record outputs.
Baselines: FIO-07 steps 2-4. The STATEFUL_RULES registry and the @stateful_rule decorator live in maxguard/rules/baseline.py (do not edit maxguard/rules/base.py; if you think they belong there, say so in issues_for_lead). Rule functions take (log_dir, context); the baseline and the end of the learning period come in through context; never read the clock or the disk implicitly. Baseline input is a list of normalized events (EVENT_KEYS in maxguard/events/normalize.py). Deterministic: sorted, JSON-serializable output (so it can be stored), same events -> same baseline. Tests with fixtures in tests/fixtures/zeek/.` },

  { key: 'jakub-netflow-agent', prompt: `TASKS: JAK-10 and JAK-11 in docs-spec/roadmap/jakub.md.
You own: maxguard/adapters/netflow.py, docker/netflow-compose.yaml, maxguard/sensor/agent.py, tests/unit/test_netflow.py, tests/unit/test_agent.py, docs-draft/netflow-agent-notes.md, plus these minimal edits (you are the only builder allowed to touch these two files): add NetflowAdapter to ADAPTERS in maxguard/pipeline.py, and make maxguard/events/normalize.py set source "netflow" for conn.log records that carry mg_source "netflow" (JAK-10 step 4). Keep both edits as small as possible, keep the existing tests passing (./.venv/bin/pytest tests/unit/test_normalize.py tests/unit/test_pipeline.py tests/unit/test_api.py -q), and list them in files.
NetFlow: netsampler/goflow2 (verify the current tag, that it publishes linux/amd64 and linux/arm64, and its license from the upstream repository). docker/netflow-compose.yaml listens on UDP 2055 and writes JSON lines to /data/netflow/. NetflowAdapter as in JAK-10 step 3 (deterministic uid = hash of the flow record). Prove it: run goflow2 in Docker on a user-defined network, send NetFlow v5 packets (and v9 or IPFIX if feasible) from a small Python generator in a second container (struct-packed header and records with documentation addresses, for example 192.0.2.10 -> 198.51.100.20 ports 23 and 80), capture goflow2's JSON, convert it, and run maxguard.pipeline.analyze(folder, workdir, explain=False); record which rules fire on flow-only data and explain why.
Host agent (JAK-11): maxguard/sensor/agent.py builds the capture command per OS with built-in tools only: Linux and macOS tcpdump with -G and -w with a time pattern (explain privilege dropping with -Z), Windows pktmon start --capture and pktmon etl2pcap. Check every flag against the tcpdump manual page (tcpdump.org) and Microsoft's pktmon documentation (learn.microsoft.com) and cite them in the docstring. It uploads each finished capture to <console>/api/ingest per the SPEC.md API contract (multipart field "file", form field "sensor_id", Authorization: Bearer <token>), console URL and token from a config file outside the repository; mark a file uploaded only after a 2xx. Document that the console must be the user's own machine and that ingest is off unless MAXGUARD_INGEST_TOKEN is set there. Tests: the command for each OS, and uploads to a fake HTTP server on 127.0.0.1. Never start a real capture.` },

  { key: 'release-bundles', prompt: `TASKS: JAI-09 (release workflow) in docs-spec/roadmap/jaiden.md and JON-05 (offline bundle) in docs-spec/roadmap/jonattan.md.
You own: .github/workflows/release.yml, scripts/build-offline-bundle.sh, scripts/install.sh, scripts/uninstall.sh, docs-draft/OFFLINE-INSTALL.md (the file the bundle ships), tests/unit/test_bundle_scripts.py, docs-draft/release-notes.md.
release.yml as in JAI-09 step 2. Verify the newest major tag of every action with git ls-remote --tags https://github.com/<owner>/<action> (record the output); validate with actionlint (pip install actionlint-py in a throwaway venv under /tmp) and record its output. The workflow also writes SHA256SUMS for the release assets. GitHub Actions itself cannot run here: not_run.
Bundle scripts as in JON-05 steps 2-4. Read docker/compose.yaml (do not edit it). Parameterize with MG_IMAGE, OLLAMA_IMAGE, MAXGUARD_MODEL and whatever a test needs (for example filling the model volume from a local folder instead of pulling a model). PROVE the mechanics here with small stand-in images only: MG_IMAGE=alpine:3.20 and OLLAMA_IMAGE=hello-world:latest (never docker save ollama/ollama:0.35.1: it is several GB), a small fake model folder, and a split-size override so splitting is exercised on small files. Run install.sh in a clean state (remove the volume first) and confirm the images load, the volume is restored, and the checksums verify; then change one byte in a part and confirm install.sh refuses before loading anything. install.sh must not start the real stack in the test (an environment variable that skips docker compose up, or a compose override: explain). shellcheck all three scripts (koalaman/shellcheck:stable is on the host). uninstall.sh asks before deleting volumes and has a non-interactive flag for tests. A real model pull and a real offline laptop run are not_run.` },

  { key: 'ahmad-ui', prompt: `TASKS: AHM-02, AHM-03 and AHM-06 in docs-spec/roadmap/ahmad.md (the dashboard), with docs-spec/ARCHITECTURE.md sections 10 and 11.
You own: maxguard/web/__init__.py, maxguard/web/routes.py, maxguard/web/templates/*.html, maxguard/web/static/app.css, maxguard/web/static/app.js, tests/unit/test_web.py, screens/*.png, docs-draft/dashboard-notes.md.
maxguard/api/app.py exists (read it, do not edit it): create_app(data_dir=None, *, explain=True) includes maxguard.web.routes.router and mounts /static. It refuses changing requests (POST/PUT/PATCH/DELETE) whose Origin does not match Host or whose Sec-Fetch-Site is cross-site or same-site, so the dashboard's own htmx requests (same origin) work. htmx is vendored at maxguard/web/static/htmx-2.0.11.min.js (0BSD): check its sha256 matches AHM-02 step 2 in a test; never a CDN.
Follow the steps exactly: pages, element IDs such as ev-<record_id>, the cookies mg_mode and mg_actor, the hx attributes, the 30 s fallback refresh, the AI-unavailable banner with ai.reason, Home-mode text from maxguard.ai.load_home_text(), severity as text and color. Escape everything: AI text and anything from traffic is never |safe (prompt injection and XSS). Keyboard accessible; works at 375 px.
Tests with TestClient(create_app(tmp_path, explain=False)) and data saved through StateStore.save_analysis() and EventStore.write() from fixture reports (build one with maxguard.pipeline.analyze on tests/fixtures/zeek/telnet and others with explain=False, then add AI sentences by hand where a test needs them). The response module (maxguard/response/) may be written at the same time by another builder; create_app imports its router when it exists.
Screenshots: run uvicorn on 127.0.0.1 with a seeded data folder and take PNGs with Playwright and Chromium (preinstalled: PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers; executablePath /opt/pw-browsers/chromium if needed; install the playwright Python package into a throwaway venv under /tmp, or use node playwright if present) of: the queue, alert detail in Analyst mode, alert detail in Home mode, the timeline, the assets page, the upload page, and the queue at 375 px. Save them to screens/ and report the paths.` },
]

function reviewPrompt(key, built) {
  return `${COMMON}

YOUR ROLE: adversarial REVIEWER (not the builder) of the work of builder "${key}" in ${R}.
The builder's own report (its claims are not evidence; check them):
${JSON.stringify(built, null, 1).slice(0, 20000)}

Read SPEC.md, the builder's task sections in docs-spec/roadmap (the task IDs are in its report and in its files' docstrings), CLAUDE.md's rules, and EVERY file the builder created or edited. Then look hard for real defects:
1. Spec conformance: file paths, function names and signatures, endpoints, settings and test files as the published steps say; any deviation the builder did not explain.
2. Correctness: edge cases, error handling, races, resource leaks; determinism (no clock or randomness in engine code, sorted output); the contracts (models.py, adapters/base.py, the API contract in SPEC.md) unchanged.
3. Security: CLAUDE.md rules 1 (offline: nothing contacts anything; Zeek never loads local), 4 (defensive only, human approval, reversible, logged), 5 (passive sensors, decoys only answer), 6 (no secrets, no real data); injection, path traversal, XSS, TLS verification, privileges in containers.
4. Tests that would still pass if the code were broken: try at least three mutations of the most important logic in a COPY of the repo under /tmp (cp -r the repo without .venv; run with ${R}/.venv/bin/python -m pytest from the copy), never in ${R} itself, and report which the tests caught.
5. Claims: every external fact in comments, docstrings and docs-draft (flags, endpoints, licenses, versions, behaviour) checked against a primary source or by running the tool in Docker.
6. Junior readability: unclear code, missing WHY comments, misleading names.
Fix in place what is clearly a bug, a security problem, a spec deviation or a false claim, but ONLY in that builder's files (the file list in its report), then re-run its tests and ruff on those files. Put larger or debatable problems in findings for the lead. Never edit other builders' or the lead's files. Same rules as the builders (Docker hygiene with prefix "${key}-review-", no network except verification, no commits).
Return the structured result (owner = "${key}").`
}

const results = await pipeline(
  BUILDERS,
  (b) => agent(`${COMMON}\n\nOWNER KEY: ${b.key}\n${b.prompt}`, { label: `build:${b.key}`, phase: 'Build', schema: RESULT })
    .then(r => r ? { ...r, owner: b.key } : null),
  (built, b) => (built && REVIEWED.has(b.key))
    ? agent(reviewPrompt(b.key, built), { label: `review:${b.key}`, phase: 'Review', schema: REVIEW })
        .then(rv => ({ key: b.key, built, review: rv }))
    : { key: b.key, built, review: null },
)

const ok = results.filter(Boolean)
log(`built: ${ok.filter(r => r.built).map(r => r.key).join(', ') || 'none'}; reviewed: ${ok.filter(r => r.review).map(r => r.key).join(', ') || 'none'}`)
return ok
