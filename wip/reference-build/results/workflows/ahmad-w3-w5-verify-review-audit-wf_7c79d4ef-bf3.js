export const meta = {
  name: 'ahmad-w3-w5-verify-review-audit',
  description: 'Verify AHM-02/03 in a browser, run the AHM-04 security pre-review, and audit each teammate branch for W0-W3',
  phases: [
    { title: 'Dashboard checks', detail: 'manual guide steps in Chromium + correctness/a11y review, then verify findings' },
    { title: 'Security review', detail: 'attack every threat row of ARCHITECTURE section 14, verify failures, write the doc' },
    { title: 'Team audit', detail: 'compare every teammate branch with the roadmap, exact fixes to reach W3' },
  ],
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
- Be exact: every claim must come from a command you ran or a file:line you read. Quote real output. If you could not run something, say so plainly.
`

// ---------------- Track A: dashboard (AHM-02, AHM-03) ----------------
const CHECKS_SCHEMA = {
  type: 'object',
  properties: {
    checks: { type: 'array', items: { type: 'object', properties: {
      task: { type: 'string' }, step: { type: 'string' }, what: { type: 'string' },
      method: { type: 'string' }, expected: { type: 'string' }, observed: { type: 'string' },
      pass: { type: 'boolean' } }, required: ['task', 'step', 'what', 'method', 'observed', 'pass'] } },
    screenshots: { type: 'array', items: { type: 'string' } },
    findings: { type: 'array', items: { type: 'object', properties: {
      id: { type: 'string' }, severity: { type: 'string', enum: ['high', 'medium', 'low'] },
      title: { type: 'string' }, repro: { type: 'string' }, evidence: { type: 'string' },
      fix: { type: 'string' }, files: { type: 'array', items: { type: 'string' } } },
      required: ['id', 'severity', 'title', 'repro', 'evidence', 'fix'] } },
    notes: { type: 'string' },
  },
  required: ['checks', 'findings'],
}
const VERDICTS_SCHEMA = {
  type: 'object',
  properties: { verdicts: { type: 'array', items: { type: 'object', properties: {
    id: { type: 'string' }, confirmed: { type: 'boolean' }, reason: { type: 'string' },
    output: { type: 'string' } }, required: ['id', 'confirmed', 'reason'] } } },
  required: ['verdicts'],
}

const manualPrompt = `${CTX}
Your label: dash-manual. You verify Ahmad's two dashboard tasks the way a careful human reviewer would, in a real browser.

Read the AHM-02 and AHM-03 sections of /home/user/maxguard/docs/roadmap/ahmad.md (search for "### AHM-02" and "### AHM-03"), especially AHM-02 steps 7-8, AHM-03 step 6, and both pull request checklists.

1. Build two private copies: AHM-02 and AHM-03 (build_stage.py). For each, start the server the way AHM-02 step 7 says (uvicorn maxguard.api.app:create_app --factory --host 127.0.0.1 --port <free port>), from the build folder with the venv on PATH. Read maxguard/api/app.py and maxguard/config* (or wherever settings live) first to learn the data-folder and allowed-hosts settings; keep data inside your own folder.
2. AHM-02 step 7: run the guide's curl header check and compare with its expected output line by line.
3. AHM-02 step 8 with Playwright (Chromium): open the queue in tab A; in tab B upload tests/fixtures/zeek/telnet as a .zip (zip the folder's files the way a user would) on the Upload page; confirm the Telnet alert appears in tab A WITHOUT a reload (measure how long it takes). Then at a 375 px wide viewport, for every page (queue, upload, alert detail, an error page such as an unknown alert id), check document.documentElement.scrollWidth <= 375 (no sideways scrolling). With the keyboard only (Tab, Shift+Tab, Enter, Space, arrow keys), confirm every link, button, select and input is reachable and usable, and that focus is visible. Confirm nothing is loaded from outside the app (record every request URL the page makes).
4. AHM-03 step 6 on the AHM-03 copy: open the Telnet alert in Analyst mode and in Home mode; change its status and assignee with the keyboard only; confirm the change shows in the audit trail (find where the audit trail is stored or shown by reading the code). Check the Home view has a headline, the severity in plain words and one action, with no jargon. The AI explanation needs Ollama, which is not installed: first record what the page shows without it (it must degrade gracefully, never crash). Then read the JON-02 client code to learn which URL it calls, start a tiny fake Ollama HTTP server of your own on 127.0.0.1 that returns a well-formed reply citing real record IDs of this finding, and confirm each AI sentence is followed by links to the records it cites. Also try a fake reply whose sentence cites a record ID that is NOT in the finding, and confirm the sentence is dropped (CLAUDE.md rule 3).
5. Checklist items: grep the templates for "|safe" and Markup( and confirm none is applied to traffic or AI text; run ruff check . and the full unit suite (pytest -m "not integration" -q) in both copies and quote the last lines.
Save screenshots (PNG) of: the queue with the Telnet alert, the upload page, the alert in Analyst mode, the alert in Home mode, and the queue at 375 px, in ${SP}/agentwork/dash-manual/. Return every check with pass/fail and real observed output, the screenshot paths, and findings ONLY for real problems you reproduced (each with exact repro steps). Stop every server you started before you finish.`

const reviewPrompt = `${CTX}
Your label: dash-review. Review Ahmad's dashboard code for correctness and accessibility bugs (security is reviewed separately, but report any XSS/CSRF you happen to confirm). Code under review, in ${SP}/stages/AHM-03: maxguard/web/routes.py, maxguard/web/templates/*.html, maxguard/web/static/app.js, maxguard/web/static/app.css, tests/unit/test_web.py; and the parts of maxguard/api/ and maxguard/storage/ these pages call. The guide text is the AHM-02 and AHM-03 sections of /home/user/maxguard/docs/roadmap/ahmad.md: its claims ("What to notice" paragraphs, checklist) must be true of the code.
Look for: filters and sorting that return wrong rows; pagination or count bugs; live refresh that duplicates or loses rows, or stops after an error; status/assignee form edge cases (empty assignee, very long input, unknown status, concurrent change); wrong HTTP status codes; unhandled exceptions on odd input (bad alert id, unknown query parameter values, missing AI text); templates that break with missing fields; form controls without labels; missing aria-live for live updates; focus lost after an htmx swap; color-only severity cues; text in the guide that does not match the code.
For every suspected bug, build your own copy (build_stage.py AHM-03 ...) and PROVE it with a failing test or a command whose output shows the problem. Report only bugs you reproduced, with the exact repro and a minimal fix (a unified diff against the file). If you find nothing real, return an empty findings list; do not pad. Put each check you did (even passing ones) in checks.`

function verifyPrompt(label, findings, extra) {
  return `${CTX}
Your label: ${label}. You are an independent skeptic. Below are findings another reviewer reported. For EACH one, try to REFUTE it: rebuild a private copy (build_stage.py), rerun the repro exactly, read the code paths, and check whether the behavior is actually wrong per the guide, ARCHITECTURE.md, or CLAUDE.md. Mark confirmed=true only if you reproduced the problem yourself and it is a real defect (not intended behavior, not a test artifact). Default to confirmed=false when uncertain. Quote the output you got. ${extra || ''}

Findings:
${JSON.stringify(findings, null, 1)}`
}

const trackA = async () => {
  const [manual, review] = await parallel([
    () => agent(manualPrompt, { label: 'dash-manual', phase: 'Dashboard checks', schema: CHECKS_SCHEMA }),
    () => agent(reviewPrompt, { label: 'dash-review', phase: 'Dashboard checks', schema: CHECKS_SCHEMA }),
  ])
  const all = [...((manual && manual.findings) || []), ...((review && review.findings) || [])]
  let verdicts = []
  if (all.length) {
    const v = await agent(verifyPrompt('dash-verify', all), { label: 'dash-verify', phase: 'Dashboard checks', schema: VERDICTS_SCHEMA })
    verdicts = (v && v.verdicts) || []
  } else {
    log('Dashboard: no findings to verify')
  }
  return { manual, review, verdicts }
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
  { key: 'archives', rows: '1', prompt: `Your label: sec-archives. Your row: 1 (malicious archive: zip bomb, path traversal; adapters/zeeklogs.py). Attacks to try at least: a zip whose members declare a small size but expand past the limit (craft it; do not actually write 4 GiB to disk: lower the limit through any setting or monkeypatch in a test harness, or use a highly compressible stream and check the code refuses before extracting, and explain which), a zip whose member names are absolute or contain ../, a tar with ../../x, an absolute path, a symlink and a hard link pointing outside, a device file (if you cannot create one without root, build the TarInfo in Python). Also check the same defenses on the API upload path (whatever function the API uses to unpack uploads) and on any other place that extracts archives in the alpha.` },
  { key: 'api', rows: '2, 6, 12', prompt: `Your label: sec-api. Your rows: 2 (huge or fake upload; magic-number type check; generated storage name; ingest off by default; ingest token checked before the body is read), 6 (dashboard published on 127.0.0.1 only; separate ingest-only app on the LAN; read docker/compose.yaml and docker/compose.lan.yaml), 12 (CSRF: Sec-Fetch-Site cross-site/same-site refused, Origin must match Host; DNS rebinding: Host outside MAXGUARD_ALLOWED_HOSTS refused). Start the API from your own AHM-04 build and attack it with curl/Python: an upload over the size limit with and without a Content-Length header, a chunked upload that grows past the limit, a .zip that is really a text file, a file name like ../../evil.zip or with NUL bytes, an ingest request with no token, a wrong token, a correct token but ingest disabled, a huge body with a wrong token (confirm the body is not read: time it or watch memory), POST/PATCH/DELETE with Sec-Fetch-Site: cross-site, with Origin: http://evil.example and Host 127.0.0.1, with Origin: null, with no Origin and no Sec-Fetch-Site (decide what the code does and whether that matches the table), Host: evil.example on GET and POST. Check the error pages and static files also carry the security headers.` },
  { key: 'xss', rows: '3, 4, 5', prompt: `Your label: sec-xss. Your rows: 3 (XSS: Jinja2 autoescaping, no |safe on traffic or AI text, CSP on every page, HTML export escapes and carries a no-script CSP), 4 (CSV formula injection: =, +, -, @, tab, CR/LF get a leading quote; report.py), 5 (prompt injection: evidence passed as JSON, model fills two fields only, every sentence must cite this finding's records, severity always shown; find which of these exist in the ALPHA (JON-02 client, JON-01 validator, JON-03 offline guard) versus later (JON-06 tests are Spring)). Attacks: make synthetic Zeek logs (copy tests/fixtures/zeek/telnet or http fixtures into your folder) whose HTTP host, user agent, URI, Telnet user name, or certificate subject contain <script>alert(1)</script>, "><img src=x onerror=alert(1)>, javascript: URLs and {{7*7}}; run them through the pipeline (python -m maxguard.cli or the API upload) and load every dashboard page and the HTML report in Chromium with Playwright: confirm no dialog fires, no injected element exists in the DOM, and the CSP header/meta is present. Export CSV and check each dangerous prefix including a value that starts with a tab or a CR. For prompt injection, use a fake Ollama server on 127.0.0.1 (read the client to learn the URL) that tries to: add a third field, change severity, cite a record that is not in the finding, cite no record, and return HTML; confirm each is refused or dropped. Also confirm the offline guard (JON-03) makes an accidental outside connection fail loudly: try a request to a non-local address from inside the guarded code path with --network none semantics simulated (do NOT actually reach the internet; a connection to a TEST-NET address like 192.0.2.1 that the guard must refuse before connecting is fine).` },
  { key: 'spring', rows: '7, 8, 9, 10, 11', prompt: `Your label: sec-spring. Your rows: 7 (LAN ingest: port 8001 plain HTTP is a known open item; check the token is compared in constant time (hmac.compare_digest or similar), the shipper accepts https with ca_file, and the agent refuses a config file other users can read), 8 (sensor passivity: capture interface without IP, Zeek/Suricata only listen, decoys on their own IP: check docker/sensor-compose.yaml, the sensor code, docs/HARDWARE.md, and that no code path sends packets on the capture interface), 9 (response module: preview before approve, IP typed again, one-step state changes, audit row for every step and refusal, undo shown, strict address parsing refusing scope IDs, integers, special/reserved/loopback/multicast/own-console addresses, only the user's own firewall over verified HTTPS, response API never on the LAN port), 10 (tampered intel bundle: member list from headers, regular files only, no duplicates, size limits, signature checked before trusting the manifest, allowed paths only, hashes checked in memory and on disk, atomic switch of the current link, rollback refused), 11 (custody log: chain of hashes, Ed25519 signature per entry, verify names the first bad entry, cut-off end detection via the printed head hash). These are Spring 2027 features: use your own build of ALL and set in_alpha=false. Attack each: approve without preview, approve with a mistyped IP, block 127.0.0.1, ::1, 0.0.0.0, 224.0.0.1, fe80::1%eth0, 3232235777 (an integer), 010.1.1.1, the console's own address; an OPNsense connector pointed at http:// or at a self-signed https without the CA (use a local fake server); a bundle with a bad signature, a valid signature over a manifest listing ../x, a duplicate member, a symlink member, an extra file not in the manifest, a member whose hash differs, an older version (rollback); a custody log with one byte changed in the middle, an entry removed, and the last entry cut off.` },
  { key: 'repo', rows: '13, 14, 15, 16, 17 + step 2', prompt: `Your label: sec-repo. Your rows: 13 (secrets: .gitignore and .dockerignore exclude key files; scan the whole git history of /home/user/maxguard (read-only, all branches: git -C /home/user/maxguard log --all -p) and the ALL build for secrets, private keys, tokens, email addresses, and real captures (CLAUDE.md rule 6); report every hit with branch/commit/path but NEVER copy a secret value into your output: redact it), 14 (offline bundle: scripts/install.sh uses sha256sum -c --strict, refuses unlisted files before loading anything; try an extra file, a changed byte, and a malformed SHA256SUMS line against a tiny fake bundle; SHA256SUMS not signed is a known open item), 15 (release workflow .github/workflows/release.yml: least privilege per job, every action pinned to a full commit SHA, persist-credentials: false, tag name only through env vars; also check the CI workflow(s) the same way), 16 (dependencies: pinned minimum versions in pyproject.toml, htmx SHA-256 d6fdc75f204e6bdefa99b69bf1e6d4ac69b8a364f77929f45c13476b4000f717, every dependency licensed in docs/DEPENDENCIES.md: compare pyproject dependencies and every image/vendored file against that table), 17 (privacy: uploads deleted after analysis (prove it by uploading and listing the data folder), events kept 7 days with prune() still not called: confirm whether anything calls prune()).
Also AHM-04 step 2: (a) make a fresh venv in your folder, pip install pip-audit, and run it on the exact installed set of ${SP}/ref/.venv (pip freeze it into a requirements file and run pip-audit -r on it, add --vulnerability-service osv if PyPI is unreachable); quote the result. (b) For Zeek (pinned 9.0.0), Suricata (engine 7.0.10 via Debian 13, sensor 8.0.7) and Ollama (0.35.1), list every newer release up to today (2026-10-27) and any security fix or CVE in them, with the release-note URL. Use https://api.github.com/repos/zeek/zeek/releases, https://api.github.com/repos/OISF/suricata/tags (and suricata.io release posts if reachable), https://api.github.com/repos/ollama/ollama/releases with curl, plus WebSearch/WebFetch if available; say which sources you could not reach. Put the dependency and upstream results in 'extra' as Markdown with links.` },
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
  const rowsResults = ok.map(x => ({ group: x.group, rows: x.rows, findings: x.findings, extra: x.extra }))
  const verdicts = ok.flatMap(x => x.verdicts)
  const doc = await agent(secFinal(rowsResults, verdicts), { label: 'sec-writer', phase: 'Security review' })
  return { groups: ok, doc }
}

// ---------------- Track C: team audit to reach W3 ----------------
const AUDIT_SCHEMA = {
  type: 'object',
  properties: {
    people: { type: 'array', items: { type: 'object', properties: {
      person: { type: 'string' },
      tasks: { type: 'array', items: { type: 'object', properties: {
        id: { type: 'string' }, due: { type: 'string' },
        status: { type: 'string', enum: ['merged', 'pr-open', 'branch-matches-guide', 'branch-partial', 'branch-broken', 'not-started', 'blocked'] },
        branch: { type: 'string' }, problems: { type: 'array', items: { type: 'string' } },
        fix_steps: { type: 'array', items: { type: 'string' } }, blocked_by: { type: 'array', items: { type: 'string' } } },
        required: ['id', 'status', 'problems', 'fix_steps'] } },
      summary: { type: 'string' } }, required: ['person', 'tasks', 'summary'] } },
    notes: { type: 'string' },
  },
  required: ['people'],
}

const AUDIT_INTRO = `${CTX}
You audit teammates' work against the roadmap so the Security Lead (Ahmad) can tell each person exactly what to do to reach Week 3 (W3 is due Friday, October 30, 2026). Today is Tuesday, October 27, 2026. Nothing has been merged to main since October 14 except planning docs; there are no open pull requests. The remote branches were fetched today; list them with git -C /home/user/maxguard branch -r and inspect them read-only.
How to compare: a task's expected files and their exact expected content are what build_stage.py produces for that task: build the stage for the task (and for the task just before it in TASKS order when you need to know which files the task changes) and byte-compare each expected file with the branch's version (git -C /home/user/maxguard show origin/<branch>:<path>). Empty __init__.py files are correct when the stage's file is also empty; any other 0-byte file where the stage has content is a real problem. Note wrong paths (for example a doubled maxguard/maxguard/ folder), missing files, extra files, files from another task, and content differences (summarize each difference in one line; show a few diff lines when it helps). Where possible, export the branch into your folder and run ruff check . and pytest -m "not integration" -q there; if they cannot pass because an earlier task is missing, say which task.
For fix_steps, write exact commands a junior student can paste, in order (branch names from the guide, git commands, which guide step to redo). Use the branch names and PR titles the guides specify. Keep each person's steps short and concrete.
`

const AUDIT_GROUPS = [
  { key: 'jaiden', prompt: `Your label: audit-jaiden. Audit Jaiden (GitHub JWinborne1), who owns the critical path: JAI-00 (Week 0 onboarding), JAI-01, JAI-02, JAI-03, JAI-04, JAI-05, JAI-06, JAI-07 (read /home/user/maxguard/docs/roadmap/jaiden.md). His branches: origin/maxguard/__init__.py (JAI-01; note the odd branch name), origin/jaiden/restructure, origin/jaiden/event-schema (JAI-03), origin/jaiden/storage (JAI-06), origin/jaiden/docker-image (has a JAI-05 commit). Walk every commit on each branch (git log --stat origin/main..origin/<branch>), map it to a task, and compare with the stage files. Find out whether the branches are stacked on each other, whether JAI-02 (the three contracts) and JAI-04 exist anywhere, and what is missing for each of JAI-01..JAI-07. Also check his docs/TEAM.md row on main (git show origin/main:docs/TEAM.md) against the header order and his GitHub name JWinborne1. Give the shortest safe sequence to get JAI-01 and JAI-02 merged first (they unblock everyone), then the rest, including how to clean up the empty/wrong files without losing his work.` },
  { key: 'karthik', prompt: `Your label: audit-karthik. Audit Karthik (GitHub Karthiknair91): KAR-00, KAR-01 (traffic lab and the 14 test captures; due W0), KAR-02 (W1), KAR-03 (W2), KAR-04 (W3) (read /home/user/maxguard/docs/roadmap/karthik.md). His branch: origin/karthik/traffic-lab. Compare every file with the KAR-01 stage. The captures in his branch were reported to be header-only (24-byte pcap files): verify the size of each capture, and find the root cause by reading the lab files (compose, scripts) in his branch versus the guide's, and the guide's expected output (packet counts). If useful, actually run the guide's lab in Docker from the GUIDE's files in your own folder (it uses python:3.11-slim-bookworm and nicolaka/netshoot:v0.15; pull them) to see what a correct run produces, and if you can, run his version too to reproduce the empty captures. Give exact fix steps. Note which later tasks KAR-01 blocks (JAK-01, JAK-02, KAR-02 and everything after).` },
  { key: 'others', prompt: `Your label: audit-others. Audit the other five teammates and Week 0 for everyone. People and GitHub names: Fiona (flau0306), Jakub (SXafir-byte), Jonattan (MeliorExi), Ali (al-kheder), Amory (gettalife); also report Week 0 status for Ahmad (ahmadalkhoudeir), Jaiden (JWinborne1) and Karthik (Karthiknair91). Week 0 is done when the person has a merged pull request adding their row to docs/TEAM.md (see section 0.9 of each guide). Check git -C /home/user/maxguard log origin/main -- docs/TEAM.md and the file itself (who has a row; is each row correct in column order and GitHub name). Amory has a branch origin/amory/week0-team-row: check whether it has any commits beyond main. For each of the five, list their tasks due W0-W3 from /home/user/maxguard/docs/roadmap/<name>.md and ${SP}/docgen/taskplan.py (with the 'depends' field), say which are blocked and by which unmerged task, and which they can start TODAY even though nothing is merged (for example ALI-01 has no dependencies; process tasks like AMO-02 can begin reading the official document; anyone can prepare a branch and run the guide's code on top of a stage build to be ready). Give each person their concrete next steps in order. Also produce, in notes, one merge order for every W0-W3 task (a topological order using 'depends') showing the critical path to AHM-02, and estimate how many review-and-merge rounds it needs.` },
]

const trackC = async () => {
  const res = await parallel(AUDIT_GROUPS.map(g => () =>
    agent(AUDIT_INTRO + g.prompt, { label: 'audit-' + g.key, phase: 'Team audit', schema: AUDIT_SCHEMA })))
  return res.filter(Boolean)
}

const [A, B, C] = await parallel([trackA, trackB, trackC].map(f => () => f()))
return { dashboard: A, security: B, team: C }
