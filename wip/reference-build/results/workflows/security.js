export const meta = {
  name: 'ahm04-security-prereview',
  description: 'AHM-04 pre-review: attack threat rows 2-17 of ARCHITECTURE section 14, verify failures, write docs/security-review-alpha.md (row 1 already done)',
  phases: [{ title: 'Security review', detail: 'four reviewers, a verifier per reviewer with findings, then the writer' }],
}
const SP = '/tmp/claude-0/-home-user-maxguard/d28fe4b6-2c9f-5cd0-8e7f-d2be65aa4c01/scratchpad'
const CTX = `
Shared setup (read carefully):
- Scratchpad: ${SP}. Write ONLY inside ${SP}/agentwork/<your-label>/ (create it). Never write anywhere else.
- The MaxGuard roadmap guides are in /home/user/maxguard/docs/roadmap/*.md and the design in /home/user/maxguard/docs/ARCHITECTURE.md. Treat /home/user/maxguard as READ-ONLY: no checkout, commit, push, fetch, branch, or file edits there. Use only read-only git (git -C /home/user/maxguard log/show/ls-tree/diff/cat-file). To run a branch's code, export it: git -C /home/user/maxguard archive origin/<branch> | tar -x -C <your folder>.
- Full builds of the project as it looks right after a roadmap task already exist and are READ-ONLY: ${SP}/stages/AHM-02, ${SP}/stages/AHM-03, ${SP}/stages/AHM-04 (the alpha state) and ${SP}/stages/ALL (every task, including Spring 2027 features). If you need to run a server, write files, or change anything, build your own copy first: python3 ${SP}/docgen/build_stage.py <TASK_ID|ALL> <new empty folder> (for example ${SP}/agentwork/<label>/repo). Any task ID works (for example JAI-01, KAR-01). The list of tasks with their files, owners and dependencies is in ${SP}/docgen/taskplan.py (TASKS); simulate.py's source_of() maps each files entry to its source.
- Python: ${SP}/ref/.venv/bin (Python 3.11 with every dependency, ruff, pytest, uvicorn). Run tests from the build folder: ${SP}/ref/.venv/bin/python -m pytest -q -p no:cacheprovider ... (pyproject sets pythonpath=["."], so maxguard imports from the current folder). Set PYTHONDONTWRITEBYTECODE=1.
- Docker works and the image zeek/zeek:9.0.0 is pulled. To run MaxGuard inside it the way the roadmap simulation does: docker run --rm --network none -v <repo>:/src -v ${SP}/deps313:/deps:ro -e PYTHONPATH=/deps:/src -e PYTHONDONTWRITEBYTECODE=1 -w /src zeek/zeek:9.0.0 sh -c '<command>' (python3 is the interpreter there).
- Node with Playwright is available: require('playwright') works from any folder and chromium.launch() needs no options. Do not run "playwright install".
- Safety (CLAUDE.md rules 4-6): attack only processes you start yourself on 127.0.0.1 inside this container, with synthetic data. Never contact or scan any outside host. Never create real secrets in files you keep; generate throwaway tokens at runtime.
- Installed tools (approved by the project lead today; do not install, pull or download anything else): pip-audit 2.10.1, bandit 1.9.4 and actionlint 1.7.12 in ${SP}/tools/secvenv/bin; Docker images koalaman/shellcheck:v0.11.0, zricethezav/gitleaks:v8.30.1, zeek/zeek:9.0.0, python:3.11-slim-bookworm, nicolaka/netshoot:v0.15, jasonish/suricata:7.0.10 and jasonish/suricata:8.0.7; the axe checker at ${SP}/tools/node/node_modules/@axe-core/playwright; fonts DejaVu Sans, Liberation Sans, Roboto and Noto Sans.
- Be exact: every claim must come from a command you ran or a file:line you read. Quote real output. If you could not run something, say so plainly.
`

const VERDICTS_SCHEMA = {
  type: 'object',
  properties: { verdicts: { type: 'array', items: { type: 'object', properties: {
    id: { type: 'string' }, confirmed: { type: 'boolean' }, reason: { type: 'string' },
    output: { type: 'string' } }, required: ['id', 'confirmed', 'reason'] } } },
  required: ['verdicts'],
}

function verifyPrompt(label, findings, extra) {
  return `${CTX}
Your label: ${label}. You are an independent skeptic. Below are findings another reviewer reported. For EACH one, try to REFUTE it: rebuild a private copy (build_stage.py), rerun the repro exactly, read the code paths, and check whether the behavior is actually wrong per the guide, ARCHITECTURE.md, or CLAUDE.md. Mark confirmed=true only if you reproduced the problem yourself and it is a real defect (not intended behavior, not a test artifact). Default to confirmed=false when uncertain. Quote the output you got. ${extra || ''}

Findings:
${JSON.stringify(findings, null, 1)}`
}

// ---------------- Track B: AHM-04 security pre-review ----------------
const ROWS_SCHEMA = {
  type: 'object',
  properties: {
    rows: { type: 'array', items: { type: 'object', properties: {
      row: { type: 'integer' }, threat: { type: 'string' }, in_alpha: { type: 'boolean' },
      defense: { type: 'string' }, code_refs: { type: 'array', items: { type: 'string' } },
      tests: { type: 'array', items: { type: 'string' } }, attacks: { type: 'string' },
      commands: { type: 'array', items: { type: 'string' } }, observed: { type: 'string' },
      result: { type: 'string', enum: ['PASS', 'FAIL', 'PARTIAL', 'OPEN-ITEM'] }, notes: { type: 'string' } },
      required: ['row', 'threat', 'in_alpha', 'defense', 'code_refs', 'attacks', 'commands', 'observed', 'result'] } },
    findings: { type: 'array', items: { type: 'object', properties: {
      id: { type: 'string' }, row: { type: 'integer' }, severity: { type: 'string', enum: ['critical', 'high', 'medium', 'low'] },
      title: { type: 'string' }, repro: { type: 'string' }, evidence: { type: 'string' }, fix: { type: 'string' },
      files: { type: 'array', items: { type: 'string' } }, owner_task: { type: 'string' } },
      required: ['id', 'row', 'severity', 'title', 'repro', 'evidence', 'fix'] } },
    extra: { type: 'string' },
  },
  required: ['rows', 'findings'],
}

const SEC_INTRO = `${CTX}
You are doing part of AHM-04, "Security review of the alpha" (read its section in /home/user/maxguard/docs/roadmap/ahmad.md). The threat table is in /home/user/maxguard/docs/ARCHITECTURE.md section 14 ("## 14. Security design"); number its rows 1-17 from the top (row 1 = zip bomb / archive, row 17 = privacy). The alpha is the state ${SP}/stages/AHM-04 (every Fall 2026 task up to AHM-04). Spring 2027 features (sensor, agent, response module, intel bundles, custody log) exist only in ${SP}/stages/ALL: test those there and set in_alpha=false.
For each row you own: (1) find the code that defends it (file:line) and the tests that prove it (test file::name) and run those tests; (2) try the attack yourself where it is safe, on your own private build, against servers you start on 127.0.0.1; (3) record exactly what you ran and what happened; (4) set result: PASS (defense works as the table says), FAIL (attack succeeded or the table's claim is false), PARTIAL (works but a stated part is missing), OPEN-ITEM (the table itself already lists it as open/not done; say what remains). Every FAIL/PARTIAL also goes in findings with a repro, evidence, minimal fix (diff if code), and the roadmap task that owns the code (for example JAI-07). Do not report style issues. Do not pad.
`

const SEC_GROUPS = [
  { key: 'api', rows: '2, 6, 12', prompt: `Your label: sec-api. Your rows: 2 (huge or fake upload; magic-number type check; generated storage name; ingest off by default; ingest token checked before the body is read), 6 (dashboard published on 127.0.0.1 only; separate ingest-only app on the LAN; read docker/compose.yaml and docker/compose.lan.yaml), 12 (CSRF: Sec-Fetch-Site cross-site/same-site refused, Origin must match Host; DNS rebinding: Host outside MAXGUARD_ALLOWED_HOSTS refused). Start the API from your own AHM-04 build and attack it with curl/Python: an upload over the size limit with and without a Content-Length header, a chunked upload that grows past the limit, a .zip that is really a text file, a file name like ../../evil.zip or with NUL bytes, an ingest request with no token, a wrong token, a correct token but ingest disabled, a huge body with a wrong token (confirm the body is not read: time it or watch memory), POST/PATCH/DELETE with Sec-Fetch-Site: cross-site, with Origin: http://evil.example and Host 127.0.0.1, with Origin: null, with no Origin and no Sec-Fetch-Site (decide what the code does and whether that matches the table), Host: evil.example on GET and POST. Check the error pages and static files also carry the security headers.` },
  { key: 'xss', rows: '3, 4, 5', prompt: `Your label: sec-xss. Your rows: 3 (XSS: Jinja2 autoescaping, no |safe on traffic or AI text, CSP on every page, HTML export escapes and carries a no-script CSP), 4 (CSV formula injection: =, +, -, @, tab, CR/LF get a leading quote; report.py), 5 (prompt injection: evidence passed as JSON, model fills two fields only, every sentence must cite this finding's records, severity always shown; find which of these exist in the ALPHA (JON-02 client, JON-01 validator, JON-03 offline guard) versus later (JON-06 tests are Spring)). Attacks: make synthetic Zeek logs (copy tests/fixtures/zeek/telnet or http fixtures into your folder) whose HTTP host, user agent, URI, Telnet user name, or certificate subject contain <script>alert(1)</script>, "><img src=x onerror=alert(1)>, javascript: URLs and {{7*7}}; run them through the pipeline (python -m maxguard.cli or the API upload) and load every dashboard page and the HTML report in Chromium with Playwright: confirm no dialog fires, no injected element exists in the DOM, and the CSP header/meta is present. Export CSV and check each dangerous prefix including a value that starts with a tab or a CR. For prompt injection, use a fake Ollama server on 127.0.0.1 (read the client to learn the URL) that tries to: add a third field, change severity, cite a record that is not in the finding, cite no record, and return HTML; confirm each is refused or dropped. Also confirm the offline guard (JON-03) makes an accidental outside connection fail loudly: try a request to a non-local address from inside the guarded code path with --network none semantics simulated (do NOT actually reach the internet; a connection to a TEST-NET address like 192.0.2.1 that the guard must refuse before connecting is fine).` },
  { key: 'spring', rows: '7, 8, 9, 10, 11', prompt: `Your label: sec-spring. Your rows: 7 (LAN ingest: port 8001 plain HTTP is a known open item; check the token is compared in constant time (hmac.compare_digest or similar), the shipper accepts https with ca_file, and the agent refuses a config file other users can read), 8 (sensor passivity: capture interface without IP, Zeek/Suricata only listen, decoys on their own IP: check docker/sensor-compose.yaml, the sensor code, docs/HARDWARE.md, and that no code path sends packets on the capture interface), 9 (response module: preview before approve, IP typed again, one-step state changes, audit row for every step and refusal, undo shown, strict address parsing refusing scope IDs, integers, special/reserved/loopback/multicast/own-console addresses, only the user's own firewall over verified HTTPS, response API never on the LAN port), 10 (tampered intel bundle: member list from headers, regular files only, no duplicates, size limits, signature checked before trusting the manifest, allowed paths only, hashes checked in memory and on disk, atomic switch of the current link, rollback refused), 11 (custody log: chain of hashes, Ed25519 signature per entry, verify names the first bad entry, cut-off end detection via the printed head hash). These are Spring 2027 features: use your own build of ALL and set in_alpha=false. Attack each: approve without preview, approve with a mistyped IP, block 127.0.0.1, ::1, 0.0.0.0, 224.0.0.1, fe80::1%eth0, 3232235777 (an integer), 010.1.1.1, the console's own address; an OPNsense connector pointed at http:// or at a self-signed https without the CA (use a local fake server); a bundle with a bad signature, a valid signature over a manifest listing ../x, a duplicate member, a symlink member, an extra file not in the manifest, a member whose hash differs, an older version (rollback); a custody log with one byte changed in the middle, an entry removed, and the last entry cut off.` },
  { key: 'repo', rows: '13, 14, 15, 16, 17 + step 2', prompt: `Your label: sec-repo. Your rows: 13 (secrets: .gitignore and .dockerignore exclude key files; scan the whole git history of /home/user/maxguard (read-only, all branches: git -C /home/user/maxguard log --all -p) and the ALL build for secrets, private keys, tokens, email addresses, and real captures (CLAUDE.md rule 6); report every hit with branch/commit/path but NEVER copy a secret value into your output: redact it), 14 (offline bundle: scripts/install.sh uses sha256sum -c --strict, refuses unlisted files before loading anything; try an extra file, a changed byte, and a malformed SHA256SUMS line against a tiny fake bundle; SHA256SUMS not signed is a known open item), 15 (release workflow .github/workflows/release.yml: least privilege per job, every action pinned to a full commit SHA, persist-credentials: false, tag name only through env vars; also check the CI workflow(s) the same way), 16 (dependencies: pinned minimum versions in pyproject.toml, htmx SHA-256 d6fdc75f204e6bdefa99b69bf1e6d4ac69b8a364f77929f45c13476b4000f717, every dependency licensed in docs/DEPENDENCIES.md: compare pyproject dependencies and every image/vendored file against that table), 17 (privacy: uploads deleted after analysis (prove it by uploading and listing the data folder), events kept 7 days with prune() still not called: confirm whether anything calls prune()).
Also AHM-04 step 2: (a) run the installed ${SP}/tools/secvenv/bin/pip-audit on the exact installed set of ${SP}/ref/.venv (pip freeze it into a requirements file and run pip-audit -r on it, add --vulnerability-service osv if PyPI is unreachable); quote the result. Also run ${SP}/tools/secvenv/bin/bandit -r maxguard -q on the ALL build and say which findings matter (most will be expected, for example subprocess use); run the gitleaks image over the repository (docker run --rm -v /home/user/maxguard:/repo:ro zricethezav/gitleaks:v8.30.1 git /repo --redact --no-banner, and the same with detect on the ALL build), ShellCheck (koalaman/shellcheck:v0.11.0) on every shell script in the ALL build, and actionlint on its workflows. (b) For Zeek (pinned 9.0.0), Suricata (engine 7.0.10 via Debian 13, sensor 8.0.7) and Ollama (0.35.1), list every newer release up to today (2026-10-27) and any security fix or CVE in them, with the release-note URL. Use https://api.github.com/repos/zeek/zeek/releases, https://api.github.com/repos/OISF/suricata/tags (and suricata.io release posts if reachable), https://api.github.com/repos/ollama/ollama/releases with curl, plus WebSearch/WebFetch if available; say which sources you could not reach. Put the dependency and upstream results in 'extra' as Markdown with links.` },
]

function secFinal(rowsResults, verdicts) {
  return `${CTX}
Your label: sec-writer. Write the AHM-04 deliverable docs/security-review-alpha.md for the MaxGuard repository, as a file at ${SP}/agentwork/sec-writer/security-review-alpha.md. Read the AHM-04 section of /home/user/maxguard/docs/roadmap/ahmad.md and section 14 of /home/user/maxguard/docs/ARCHITECTURE.md first.

Facts to use (from reviewers who ran every check; findings were independently re-tested, and only confirmed ones count as failures):
ROW RESULTS: ${JSON.stringify(rowsResults)}
VERIFIER VERDICTS (confirmed=false means the finding did NOT hold up; then the row's result must not be FAIL because of it): ${JSON.stringify(verdicts)}

Write it for a junior student, in plain, direct English that sounds like a person wrote it (short sentences, no filler, no "delve", no "robust", no marketing tone). Structure:
1. Title "# Security review of the alpha (AHM-04)" and a short status paragraph: this is a pre-review done on October 27, 2026 against the roadmap's reference build (the code in the task guides, built in roadmap order up to AHM-04, which is what the team will merge, since "code, tested" tasks are copied exactly); the alpha is not merged yet; before the W5 review (Friday, November 13, 2026) Ahmad re-runs each "How checked" command on main and updates the Result column.
2. One table with one row per threat, all 17 rows in section 14 order: # | Threat | Defense (code and test) | How checked | Result | Issue. Result is one of Pass, Fail, Partial, Open item, each with a few words. In Fall alpha scope? Mark Spring-only rows "Spring 2027 (checked early on the full build)". The Issue column says "to open: <short title> (owner TASK-ID)" for each confirmed failure or partial, else "—".
3. "Confirmed problems" section: for each confirmed finding, what is wrong, how to reproduce, the fix, and which task's guide must change.
4. "Dependencies" (pip-audit result) and "Upstream tools" (Zeek, Suricata, Ollama releases since our pins and their security fixes, with links). Include only facts the reviewers reported with sources; if a source was unreachable, say so.
5. "Open items that need a decision" (for example plain-HTTP port 8001, unsigned SHA256SUMS, prune() never called, the engine's Suricata 7.0 being end-of-life) with a one-line recommendation each.
6. "How to re-run this review on main": exact commands, grouped by row.
7. "References" in APA 7 style for every outside source you cite (OWASP cheat sheets, Python tarfile docs, release notes), with URLs.
Keep commands exact and copyable. Use real numbers from the results. Do not invent anything. Return the full Markdown text of the file as your final answer as well.`
}

const trackB = async () => {
  const results = await pipeline(
    SEC_GROUPS,
    g => agent(SEC_INTRO + g.prompt, { label: 'sec-' + g.key, phase: 'Security review', schema: ROWS_SCHEMA }),
    async (r, g) => {
      if (!r) return { group: g.key, rows: [], findings: [], verdicts: [], extra: '' }
      const fs = r.findings || []
      let verdicts = []
      if (fs.length) {
        const v = await agent(verifyPrompt('sec-verify-' + g.key, fs, 'These are security findings from the AHM-04 review; use the same safety rules.'),
          { label: 'sec-verify-' + g.key, phase: 'Security review', schema: VERDICTS_SCHEMA })
        verdicts = (v && v.verdicts) || []
      }
      return { group: g.key, rows: r.rows || [], findings: fs, verdicts, extra: r.extra || '' }
    },
  )
  const ok = results.filter(Boolean)
  const rowsResults = [args.archives, ...ok.map(x => ({ group: x.group, rows: x.rows, findings: x.findings, extra: x.extra }))]
  const verdicts = ok.flatMap(x => x.verdicts)
  const doc = await agent(secFinal(rowsResults, verdicts), { label: 'sec-writer', phase: 'Security review' })
  return { groups: ok, doc }
}

const B = await trackB()
return { security: B }
