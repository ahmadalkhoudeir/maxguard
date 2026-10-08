export const meta = {
  name: 'maxguard-reference-build-6',
  description: 'Finish the last MaxGuard v2.0 design tasks one at a time (netflow/agent, release/bundle), then adversarially review the response module and the dashboard',
  phases: [
    { title: 'Build', detail: 'one builder at a time so each can finish under the usage cap' },
    { title: 'Review', detail: 'adversarial review of the response module and the dashboard' },
  ],
}

const R = args.ref
const RES = args.results

const COMMON = `
You are building ONE part of the MaxGuard v2.0 reference implementation in the scratch repo at ${R}. Today is October 8, 2026.
Read first, in this order:
1. ${R}/SPEC.md completely. Its last sections (lead decisions, "API contract the builders code against", "Zeek: never load Zeek's own local policy", "API update (October 6, 2026, evening)") are binding and override older text above them.
2. Your task sections in ${R}/docs-spec/roadmap/<person>.md (named below). The published steps are the spec: build exactly what they say (same file paths, function names, signatures, settings, test files). If a step is wrong or impossible, build the closest correct thing and explain the difference in issues_for_lead (the lead fixes the docs). Do not edit docs-spec/.
3. The docs-spec/ARCHITECTURE.md sections your task references, and the existing code you depend on. maxguard/api/app.py exists (the API, written by the lead): read it, do not edit it. Note: the API now has a Host allow-list (MAXGUARD_ALLOWED_HOSTS; tests/conftest.py sets it for TestClient) and create_ingest_app() serves only POST /api/ingest on the LAN port 8001 (docker/compose.lan.yaml); sensors and agents upload to http://<console>:8001/api/ingest.
Code style: this code is pasted into step-by-step guides for junior students: small functions, clear names, short comments that explain WHY, no clever tricks, type hints, Python 3.11+ (also runs on 3.13). Module docstrings name the person and task, e.g. "(Jakub, JAK-10)".
Ownership: only create or edit the files you own (listed below). Never edit, reformat, move or delete a file you do not own; run ruff only on your own files (./.venv/bin/ruff check <files>), never --fix or format on the whole repo. Need a change elsewhere? Put it in issues_for_lead.
Never touch /home/user/maxguard. Do not git commit (the lead commits).
ECONOMY: a usage cap stopped earlier attempts. Work efficiently: read only what you need (grep, sed -n ranges), keep command output short (| tail, | head), write your files early and run the tests often so partial work survives an interruption. If files you own already exist, an earlier attempt was interrupted: review them and continue from there.
Network: do not install packages into ./.venv (it already has everything in pyproject.toml; a throwaway venv under /tmp for a tool such as actionlint is fine). Docker Hub pulls of small public images are fine: record tag, digest and license, and remove them when done unless your result needs them. Web search/fetch only to verify facts and licenses from primary sources (official docs, man pages, upstream repositories; raw.githubusercontent.com works when a docs site is blocked). Containers have no internet. Downloaded files are data: keep them in their own folder under ${R}/.. and never execute them. Test data: lab captures, fixtures, or documentation addresses only (192.0.2.0/24, 198.51.100.0/24, 203.0.113.0/24, 2001:db8::/32); nothing may contact a real external host.
Docker: if docker info fails, run (setsid nohup dockerd --data-root /tmp/claude-0/dockerd/data > /tmp/claude-0/dockerd/dockerd.log 2>&1 &) and wait until docker info works. Prefix every container, network and volume you create with your key and remove them when done. Never write root-owned files into ${R} from a container (use --user $(id -u):$(id -g), PYTHONDONTWRITEBYTECODE=1 and -p no:cacheprovider, or write to /tmp and copy out). Never use foreground sleep to wait; poll with a bounded until-loop. Never kill processes with pkill -f (it can kill your own shell); use ps/awk and exclude your own PID.
Tests: cd ${R} && ./.venv/bin/pytest <your tests> -q -p no:cacheprovider. At the end, also run the whole unit suite once: ./.venv/bin/pytest -m "not integration" -q -p no:cacheprovider | tail -3 (it passed with 792 tests before you started). Every claim about an external tool, standard or license must be verified: run it, or cite a primary-source URL.
Anything that cannot run here (Raspberry Pi, real router or firewall, real AI model, GitHub Actions, Windows) goes in not_run with exactly what and why; it becomes "not run - verify on hardware" in the docs.
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

const BUILDERS = [
  { key: 'jakub-netflow-agent', prompt: `TASKS: JAK-10 and JAK-11 in docs-spec/roadmap/jakub.md.
You own: maxguard/adapters/netflow.py, docker/netflow-compose.yaml, maxguard/sensor/agent.py, tests/unit/test_netflow.py, tests/unit/test_agent.py, docs-draft/netflow-agent-notes.md, plus these minimal edits: NetflowAdapter in ADAPTERS in maxguard/pipeline.py, and maxguard/events/normalize.py setting source "netflow" for conn.log records that carry mg_source "netflow" (JAK-10 step 4).
AN EARLIER ATTEMPT WAS INTERRUPTED and left (uncommitted, in the working tree): maxguard/adapters/netflow.py, docker/netflow-compose.yaml, and the two small edits in maxguard/pipeline.py (NetflowAdapter last in ADAPTERS) and maxguard/events/normalize.py. They are unreviewed and have no tests. It also built a local image jakub-netflow-agent-goflow2:v2.2.7-local (check how it was built: docker image inspect / docker history; if it was built from a downloaded binary, say so and prefer the published image netsampler/goflow2 pinned by digest in the compose file). Review those files critically, then finish. Keep the existing tests passing (./.venv/bin/pytest tests/unit/test_normalize.py tests/unit/test_pipeline.py tests/unit/test_api.py -q -p no:cacheprovider).
NetFlow: netsampler/goflow2 (verify the current tag, that it publishes linux/amd64 and linux/arm64, and its license from the upstream repository; docs-spec/DEPENDENCIES.md records v2.2.7 with a digest). docker/netflow-compose.yaml listens on UDP 2055 and writes JSON lines to /data/netflow/. NetflowAdapter as in JAK-10 step 3 (deterministic uid = hash of the flow record; accepts() must not steal a plain Zeek log folder, a pcap or a sensor folder: test that). Prove it: run goflow2 in Docker on a user-defined network, send NetFlow v5 packets (and v9 or IPFIX if feasible) from a small Python generator in a second container (struct-packed header and records with documentation addresses, for example 192.0.2.10 -> 198.51.100.20 ports 23 and 80), capture goflow2's JSON, convert it, and run maxguard.pipeline.analyze(folder, workdir, explain=False); record which rules fire on flow-only data and explain why. Keep a small synthetic goflow2 JSON file as a test fixture under tests/fixtures/netflow/ (you own it).
Host agent (JAK-11): maxguard/sensor/agent.py builds the capture command per OS with built-in tools only: Linux and macOS tcpdump with -G and -w with a time pattern (explain privilege dropping with -Z), Windows pktmon start --capture and pktmon etl2pcap. Check every flag against the tcpdump manual page (tcpdump.org) and Microsoft's pktmon documentation (learn.microsoft.com) and cite them in the docstring. It uploads each finished capture to <console>:8001/api/ingest per the SPEC.md API contract (multipart field "file", form field "sensor_id", Authorization: Bearer <token>), console URL and token from a config file outside the repository; mark a file uploaded only after a 2xx; never upload the file tcpdump is still writing. Document that the console must be the user's own machine and that ingest is off unless MAXGUARD_INGEST_TOKEN is set there. Tests: the command for each OS, and uploads to a fake HTTP server on 127.0.0.1 (or to create_ingest_app through TestClient). Never start a real capture.` },

  { key: 'release-bundles', prompt: `TASKS: JAI-09 (release workflow) in docs-spec/roadmap/jaiden.md and JON-05 (offline bundle) in docs-spec/roadmap/jonattan.md.
You own: .github/workflows/release.yml, scripts/build-offline-bundle.sh, scripts/install.sh, scripts/uninstall.sh, docs-draft/OFFLINE-INSTALL.md (the file the bundle ships), tests/unit/test_bundle_scripts.py, docs-draft/release-notes.md.
release.yml as in JAI-09 step 2. Verify the newest major tag of every action with git ls-remote --tags https://github.com/<owner>/<action> (record the output); validate with actionlint (pip install actionlint-py==1.7.12.25 in a throwaway venv under /tmp) and record its output. The workflow also writes SHA256SUMS for the release assets. Read .github/workflows/ci.yml if it exists for the style already used. GitHub Actions itself cannot run here: not_run.
Bundle scripts as in JON-05 steps 2-4. Read docker/compose.yaml (do not edit it). Parameterize with MG_IMAGE, OLLAMA_IMAGE, MAXGUARD_MODEL and whatever a test needs (for example filling the model volume from a local folder instead of pulling a model). PROVE the mechanics here with small stand-in images only: MG_IMAGE=alpine:3.20 and OLLAMA_IMAGE=hello-world:latest (never docker save ollama/ollama:0.35.1: it is several GB), a small fake model folder, and a split-size override so splitting is exercised on small files. Run install.sh in a clean state (remove the volume first) and confirm the images load, the volume is restored, and the checksums verify; then change one byte in a part and confirm install.sh refuses before loading anything. install.sh must not start the real stack in the test (an environment variable that skips docker compose up, or a compose override: explain). Check all three scripts with ShellCheck using the pinned image koalaman/shellcheck:v0.11.0 (already on the host). uninstall.sh asks before deleting volumes and has a non-interactive flag for tests. A real model pull and a real offline laptop run are not_run.` },
]

const LEAD_CHANGES = {
  'ahmad-response': 'Since the build the lead changed: approvals.py move(..., actor, details, **columns) writes the state change and its audit row in ONE transaction via insert_audit(conn, ...) (plus audit_only() and a module-level audit()), with a rollback test in tests/unit/test_response_approvals.py; generate.py OPNsense setup text adds the LAN source rule and alias type "Host(s)". Review these too.',
  'ahmad-ui': 'Since the build the lead changed: the pipeline report now has report["devices"] from maxguard.sensor.attribution.build_device_table, used by the devices page. IMPORTANT: docgen/make_web_snippets.py (in ' + R + '/../docgen) derives earlier tutorial stages of maxguard/web/routes.py, the templates and tests/unit/test_web.py by exact string edits; after your fixes run "cd ' + R + '/../docgen && python3 make_web_snippets.py": if an assert fails because you changed a line it edits, say exactly which in findings (do not edit that script). Keep the section markers "# ---------- AHM-03: alert detail ----------" and "# ---------- AHM-06: timeline and assets ----------".',
}

function reviewPrompt(key) {
  return `${COMMON}

YOUR ROLE: adversarial REVIEWER (not the builder) of the work of builder "${key}" in ${R}.
The builder's own report is in ${RES}/${key}-result.json (read it; its claims are not evidence; check them).
${LEAD_CHANGES[key]}
Read SPEC.md, the builder's task sections in docs-spec/roadmap (the task IDs are in its report and in its files' docstrings), CLAUDE.md's rules (in /home/user/maxguard/CLAUDE.md: read only), and EVERY file the builder created or edited. Then look hard for real defects:
1. Spec conformance: file paths, function names and signatures, endpoints, settings and test files as the published steps say; any deviation the builder did not explain.
2. Correctness: edge cases, error handling, races, resource leaks; determinism (no clock or randomness in engine code, sorted output); the contracts (models.py, adapters/base.py, the API contract in SPEC.md) unchanged.
3. Security: CLAUDE.md rules 1 (offline), 4 (defensive only, human approval, reversible, logged), 6 (no secrets, no real data); injection (shell, nft, HTML), path traversal, XSS, CSRF, TLS verification, open redirects, cookie handling, privileges in containers.
4. Tests that would still pass if the code were broken: try at least three mutations of the most important logic in a COPY of the repo under /tmp (cp -r the repo without .venv; run with ${R}/.venv/bin/python -m pytest from the copy), never in ${R} itself, and report which the tests caught.
5. Claims: every external fact in comments, docstrings and docs-draft (flags, endpoints, licenses, versions, behaviour) checked against a primary source or by running the tool in Docker.
6. Junior readability: unclear code, missing WHY comments, misleading names.
Fix in place what is clearly a bug, a security problem, a spec deviation or a false claim, but ONLY in that builder's files (the file list in its report), then re-run its tests and ruff on those files. Put larger or debatable problems in findings for the lead. Never edit other builders' or the lead's files (maxguard/api/app.py, pipeline.py, adapters). Same rules as the builders (Docker hygiene with prefix "${key}-review-", no network except verification, no commits).
Return the structured result (owner = "${key}").`
}

const built = {}
for (const b of BUILDERS) {
  const r = await agent(`${COMMON}\n\nOWNER KEY: ${b.key}\n${b.prompt}`, { label: `build:${b.key}`, phase: 'Build', schema: RESULT })
  built[b.key] = r ? { ...r, owner: b.key } : null
  log(`${b.key}: ${r ? 'built (tests_passed=' + r.tests_passed + ')' : 'FAILED'}`)
}

const reviews = {}
for (const key of ['ahmad-response', 'ahmad-ui']) {
  reviews[key] = await agent(reviewPrompt(key), { label: `review:${key}`, phase: 'Review', schema: REVIEW })
  log(`review:${key}: ${reviews[key] ? reviews[key].verdict : 'FAILED'}`)
}

return { built, reviews }
