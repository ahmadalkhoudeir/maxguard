export const meta = {
  name: 'dashboard-fix-verify',
  description: 'Re-test the five dashboard fixes in Chromium with four fonts, axe, keyboard and many tabs, plus an adversarial review of the diff',
  phases: [
    { title: 'Re-test', detail: 'browser checks of F1-F5 on fixed AHM-02/AHM-03 builds, axe scan, regression of the original checks' },
    { title: 'Review diff', detail: 'adversarial review of the fix diff' },
    { title: 'Verify', detail: 'independent re-check of anything reported broken' },
  ],
}

const SP = '/tmp/claude-0/-home-user-maxguard/d28fe4b6-2c9f-5cd0-8e7f-d2be65aa4c01/scratchpad'
const CTX = `
Setup:
- Write ONLY inside ${SP}/agentwork/<your-label>/ (create it). Do not modify anything else: not ${SP}/fix, not ${SP}/ref, not ${SP}/docgen, not /home/user/maxguard.
- FIXED code: the dashboard fix is in the git worktree ${SP}/fix/ref (branch dashboard-fixes; see git -C ${SP}/fix/ref diff for exactly what changed: app.css, app.js, queue.html, _status.html, alert.html, tests/unit/test_web.py). Build private copies of the FIXED project at a roadmap stage with: python3 ${SP}/fix/docgen/build_stage.py AHM-02 <new empty folder>  (or AHM-03). These include the fix.
- ORIGINAL (unfixed) builds for comparison, READ-ONLY: ${SP}/stages/AHM-02 and ${SP}/stages/AHM-03 (copy them before running a server that writes data).
- Python 3.11 venv with all dependencies: ${SP}/ref/.venv/bin (uvicorn, pytest, ruff). Start a server from a build folder: cd <build>; MAXGUARD_DATA_DIR=<your folder>/data-<n> ${SP}/ref/.venv/bin/uvicorn maxguard.api.app:create_app --factory --host 127.0.0.1 --port <free port> (pick free ports with python3 -c 'import socket;s=socket.socket();s.bind(("127.0.0.1",0));print(s.getsockname()[1])'; other checks run at the same time on this machine). Upload tests/fixtures/zeek/telnet as a .zip (zip the folder's files) through the Upload page or POST /api/analyses to get the Telnet alert. Read maxguard/api/app.py for settings if needed.
- Node + Playwright: require('playwright') works anywhere; chromium.launch() needs no options; never run "playwright install". The axe checker is installed: require('${SP}/tools/node/node_modules/@axe-core/playwright') (AxeBuilder, axe-core 4.14.0).
- Fonts installed: DejaVu Sans (old default), Liberation Sans (Arial metrics, like Windows), Roboto (Android), Noto Sans (now the system-ui default). To test one font, inject a style such as html, body, input, button, select, label { font-family: "Liberation Sans" !important } with page.addStyleTag after load and re-measure.
- Quote real output. Stop every server you start. Report only problems you reproduced.
`
const RESULT_SCHEMA = {
  type: 'object',
  properties: {
    checks: { type: 'array', items: { type: 'object', properties: {
      id: { type: 'string' }, what: { type: 'string' }, method: { type: 'string' },
      observed: { type: 'string' }, pass: { type: 'boolean' } }, required: ['id', 'what', 'observed', 'pass'] } },
    findings: { type: 'array', items: { type: 'object', properties: {
      id: { type: 'string' }, severity: { type: 'string', enum: ['high', 'medium', 'low'] }, title: { type: 'string' },
      repro: { type: 'string' }, evidence: { type: 'string' }, fix: { type: 'string' } },
      required: ['id', 'severity', 'title', 'repro', 'evidence', 'fix'] } },
    measurements: { type: 'string' },
  },
  required: ['checks', 'findings'],
}

phase('Re-test')
const retest = agent(`${CTX}
Your label: fix-retest. Five problems were found in Ahmad's dashboard (AHM-02/AHM-03) and fixed. Prove each fix works in Chromium on FIXED builds of AHM-02 and AHM-03, and show the same check fails on the ORIGINAL builds (so the test really detects the bug):
F1 phone width: for every page (/, /upload, and on AHM-03 also /alerts/<telnet id>, /alerts/0000000000000000 (404), /?status=bogus (400)), in Analyst and Home mode (cookie mg_mode=home), at viewport widths 320, 360, 375, 390 and 414, with each of the four fonts, record document.documentElement.scrollWidth and any element whose right edge passes the viewport. Pass = no sideways scrolling anywhere. Also check the status form on the alert page still looks right (screenshot at 375 px).
F2 focus through refresh: Tab to the Telnet alert link in the queue, then (a) change the alert from another client (PATCH /api/alerts/<id> with JSON {"actor":"x","assignee":"Someone"}) and (b) wait for the 30 s poll with no change; after each refresh document.activeElement must still be the alert link, and the next Tab must go to the next control, not to "Skip to content".
F3 focus after Save (AHM-03, Analyst mode): keyboard only, fill the name, change status with arrow keys, type an assignee, Tab to Save, press Enter: after "Saved." focus must be on the Save button.
F4 many tabs: in ONE browser context open the queue in 8 tabs. Count the open /api/stream connections (use page.on('request') across pages, or the server log, or ss -tnp on the server port). Pass = exactly 1 stream for all 8 tabs, a 9th tab with /upload loads in under 2 s, a filter change in tab 5 answers, and after a PATCH every one of the 8 queue tabs shows the new assignee within 3 s without reloading. Then close the tab that holds the stream: another tab must open a new stream within a few seconds, and a second PATCH must again reach all remaining tabs. Also test the fallback: in a context where an init script deletes navigator.locks (Object.defineProperty(navigator,'locks',{value:undefined})), each tab opens its own stream and live refresh still works in a single tab, with no console errors. Collect console errors from every page in every test.
F5 title: in Home mode the <title> of the Telnet alert page is the Home headline; in Analyst mode it is the rule title.
Also run axe (AxeBuilder, default rules plus wcag2a, wcag2aa, wcag21aa tags) on every page of the FIXED AHM-03 build in both modes at 1280 px and 375 px, and on the ORIGINAL build the same way; list every violation (id, impact, number of nodes, page) for both, and say which are new in the fixed build (there should be none). Finally re-run the original regression checks on the fixed builds: the guide's curl header check (AHM-02 step 7), nothing loads from outside the app (record request URLs), every control reachable with Tab, ruff check . and pytest -m "not integration" -q (quote the last line) in both fixed builds.
Put exact numbers in 'measurements' (a compact table per check) so the guide text can quote them. Save screenshots in your folder.`, { label: 'fix-retest', phase: 'Re-test', schema: RESULT_SCHEMA })

const review = agent(`${CTX}
Your label: fix-review. Adversarially review the dashboard fix: git -C ${SP}/fix/ref diff (read the whole changed files too, not only the diff). Try to break it:
- app.js: the Web Locks + BroadcastChannel design (one tab holds the "maxguard-stream" lock and the only EventSource; it calls refresh itself and posts to the others; others refresh on message; fallback without navigator.locks or BroadcastChannel). Think about: page navigation away and back (bfcache), a tab frozen or discarded by the browser, two browser windows, a tab whose stream errors and reconnects, the lock holder being a tab that later navigates to /upload, private windows, http://localhost vs http://127.0.0.1 (different origins: does each get its own lock? is that fine?), secure-context rules for navigator.locks, CSP (script-src 'self', connect-src 'self'), htmx.trigger when #alerts is mid-swap, duplicate refreshes, memory/connection leaks, and the server's /api/stream contract (read alert_events in maxguard/api/app.py: it sends one alerts-changed immediately on connect). Prove any problem with a Playwright script on a fixed build.
- queue.html id="alert-{{ alert.finding_id }}": are finding_id values always valid, unique ids on the page? Could traffic control them (escaping, duplicates)? Does htmx really restore focus by id with hx-select="#alerts" and outerHTML swap (read the vendored htmx-2.0.11.min.js)?
- _status.html id="status-save": unique on the page? Does focus return after the PATCH swap?
- alert.html title expression: what if home is missing, mode is something else, the headline contains quotes or HTML (it is autoescaped in <title>?), or the page is the AHM-03 version (no AHM-06 context)?
- app.css grid-template-columns: minmax(0, 1fr) on .status-form and #upload-form: any side effect on the status form, long labels, long assignee names, or wide screens?
- tests: do the new assertions really fail on the original code (run them against ${SP}/stages/AHM-03 copies)? Are they too weak?
Report only problems you reproduced, each with a minimal fix (diff). If the fix is sound, say so plainly with the checks you did.`, { label: 'fix-review', phase: 'Review diff', schema: RESULT_SCHEMA })

const [r1, r2] = await Promise.all([retest, review])
const findings = [...((r1 && r1.findings) || []), ...((r2 && r2.findings) || [])]
let verdicts = null
if (findings.length) {
  phase('Verify')
  verdicts = await agent(`${CTX}
Your label: fix-verify. Independently try to REFUTE each finding below about the dashboard fix: rebuild fixed copies, rerun the repro exactly, and decide whether it is a real defect of the FIXED code (not a test artifact, not a problem that also exists unchanged in the original and is out of scope). Default to confirmed=false when unsure. Quote your output.
Findings: ${JSON.stringify(findings, null, 1)}`, { label: 'fix-verify', phase: 'Verify', schema: {
    type: 'object', properties: { verdicts: { type: 'array', items: { type: 'object', properties: {
      id: { type: 'string' }, confirmed: { type: 'boolean' }, reason: { type: 'string' }, output: { type: 'string' } },
      required: ['id', 'confirmed', 'reason'] } } }, required: ['verdicts'] } })
}
return { retest: r1, review: r2, verdicts }
