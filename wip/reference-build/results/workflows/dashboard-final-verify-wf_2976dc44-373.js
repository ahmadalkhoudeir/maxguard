export const meta = {
  name: 'dashboard-final-verify',
  description: 'Final browser verification of all dashboard fixes (F1-F5 plus the review round) on fixed AHM-02/AHM-03 builds, and an adversarial review of the full diff',
  phases: [
    { title: 'Browser', detail: 'every fix proven in Chromium against fixed and original builds, axe, regression' },
    { title: 'Review', detail: 'adversarial review of the complete diff' },
    { title: 'Verify', detail: 'independent re-check of anything reported broken' },
  ],
}

const SP = '/tmp/claude-0/-home-user-maxguard/d28fe4b6-2c9f-5cd0-8e7f-d2be65aa4c01/scratchpad'
const CTX = `
Setup:
- Write ONLY inside ${SP}/agentwork/<your-label>/ (create it). Do not modify ${SP}/fix2, ${SP}/fix, ${SP}/ref, ${SP}/docgen, ${SP}/stages or /home/user/maxguard.
- FINAL fixed code: git worktree ${SP}/fix2/ref (branch dashboard-fixes-2); "git -C ${SP}/fix2/ref diff" shows every change against the original (app.css, app.js, base.html, queue.html, _status.html, alert.html, routes.py, tests/unit/test_web.py). Build private copies of the FIXED project: python3 ${SP}/fix2/docgen/build_stage.py AHM-02 <new empty folder> (or AHM-03).
- ORIGINAL builds for comparison, READ-ONLY: ${SP}/stages/AHM-02 and ${SP}/stages/AHM-03 (copy before running a server that writes data).
- Python 3.11 venv: ${SP}/ref/.venv/bin (uvicorn, pytest, ruff). Start a server from a build folder: cd <build>; MAXGUARD_DATA_DIR=<your folder>/data-<n> ${SP}/ref/.venv/bin/uvicorn maxguard.api.app:create_app --factory --host 127.0.0.1 --port <free port> (pick free ports with python3 -c 'import socket;s=socket.socket();s.bind(("127.0.0.1",0));print(s.getsockname()[1])'; other checks run on this machine at the same time, so allow for some slowness). Get the Telnet alert by uploading tests/fixtures/zeek/telnet as a .zip. Useful helper scripts from an earlier reviewer (read them, copy and adapt into your folder): ${SP}/agentwork/dash-review/scripts/ (add_alerts.py adds synthetic alerts of chosen severities to a data folder; far_future_upload.py uploads a log with ts=1e12; pw_*.js are Playwright checks for focus, tabs, widths, server-down, history and the two-analyst case).
- Node + Playwright: require('playwright') works anywhere; chromium.launch() needs no options; never run "playwright install". The axe checker: require('${SP}/tools/node/node_modules/@axe-core/playwright') (axe-core 4.14.0). Fonts installed: DejaVu Sans, Liberation Sans, Roboto, Noto Sans (inject html, body, input, button, select, label { font-family: "<font>" !important } with page.addStyleTag to test one).
- Installed tools are approved; do not install or download anything. Quote real output. Stop every server you start. Report only problems you reproduced.
`
const RESULT_SCHEMA = {
  type: 'object',
  properties: {
    checks: { type: 'array', items: { type: 'object', properties: {
      id: { type: 'string' }, what: { type: 'string' }, method: { type: 'string' },
      original: { type: 'string' }, fixed: { type: 'string' }, pass: { type: 'boolean' } },
      required: ['id', 'what', 'fixed', 'pass'] } },
    findings: { type: 'array', items: { type: 'object', properties: {
      id: { type: 'string' }, severity: { type: 'string', enum: ['high', 'medium', 'low'] }, title: { type: 'string' },
      repro: { type: 'string' }, evidence: { type: 'string' }, fix: { type: 'string' } },
      required: ['id', 'severity', 'title', 'repro', 'evidence', 'fix'] } },
    measurements: { type: 'string' },
  },
  required: ['checks', 'findings'],
}

phase('Browser')
const browser = agent(`${CTX}
Your label: final-browser. Prove every dashboard fix in Chromium on FIXED builds (AHM-02 and AHM-03), and for each one show the ORIGINAL build fails the same check (fill both 'original' and 'fixed'). Checks:
1 Phone width: every page (/, /upload, and on AHM-03 /alerts/<telnet id>, /alerts/0000000000000000, /?status=bogus) in Analyst and Home mode at 320 and 375 px, with each of the four fonts; also the queue in Home mode with many alerts of every severity (critical, high, medium, low; use add_alerts.py), whose badges have the longest words. Pass = document.documentElement.scrollWidth equals the viewport width everywhere.
2 Focus through a live refresh: Tab to an alert link, change that alert from another client (PATCH /api/alerts/<id> JSON {"actor":"x","assignee":"Someone"}); focus must stay on the link.
3 Focus after Save on the alert page (keyboard only): focus on the Save button afterwards.
4 Many tabs: 8 queue tabs in one context use exactly ONE /api/stream; a 9th tab with /upload loads in under 2 s; one PATCH reaches all 8 tabs within 3 s; closing the stream's tab hands the stream to another tab and a second PATCH still reaches all remaining tabs. Collect console errors.
5 Home title: Home-mode <title> of the Telnet alert is the Home headline; Analyst-mode title is the rule title.
6 Impossible time: upload a zip of the Telnet logs whose maxguard_cleartext.log record has ts=1e12 (far_future_upload.py does it with TestClient; also do it through the real server): / and /alerts/<id> answer 200 and show "(not a valid time)".
7 Queue limit: with 201 alerts in the store (add_alerts.py), the queue shows 200 rows and the caption "The 200 most severe alerts. More alerts match: use the filters to see them."; with 3 alerts the caption is "3 alerts, most severe first".
8 Two analysts: Ahmad sets the Telnet alert to Investigating in tab A while tab B already has the alert page open (still showing New); in tab B type an assignee and Save without touching the status: the stored status must stay Investigating, the assignee must change, and the audit trail must show only the assignee change for B.
9 Two quick changes: two PATCHes 200 ms apart to different alerts; both changes appear in an open queue within 3 s without a reload.
10 Back button: choose a status filter, then a severity filter, press Back: the select boxes and the rows must match the address.
11 Upload focus: after an upload finishes, focus is on the Analyze button.
12 Mode switch keeps filters: choose a severity filter on the queue (the address changes without a page load), then switch to Home: the filter must still be applied.
13 Server down: open the alert page, stop the server, change the status and Save: the form must say "Not saved: the MaxGuard server could not be reached." (never "Saved."); start it again and confirm the store was not changed.
14 axe (default rules plus tags wcag2a, wcag2aa, wcag21aa) on every page of the FIXED AHM-03 build in both modes at 1280 and 375 px, and on the ORIGINAL the same way: list every violation (id, impact, nodes, page) for both; pass = nothing new and nothing serious or critical in the fixed build.
15 Regression on both fixed builds: the AHM-02 step 7 curl header check matches the guide's three lines; no request leaves 127.0.0.1 (record request URLs); every control reachable with Tab; ruff check . and pytest -m "not integration" -q (quote the last line).
Put compact numbers per check in 'measurements' so the guide text can quote them (fonts and widths tested, times, counts). Save screenshots of the Home queue at 375 px with all severities and of the upload page at 320 px in your folder.`, { label: 'final-browser', phase: 'Browser', schema: RESULT_SCHEMA })

const review = agent(`${CTX}
Your label: final-review. Adversarially review the COMPLETE dashboard change: git -C ${SP}/fix2/ref diff (read the whole changed files). Try hard to break each part and prove any problem with a test or a Playwright script on a fixed build:
- routes.py change_status: the stale-form logic (shown_status / shown_assignee). Cases: first save with no hidden fields (old clients), hidden fields from a different alert, values with surrounding spaces, assignee cleared on purpose (""), status chosen equal to what was shown but another analyst changed it meanwhile, a hostile client sending shown_status as a file upload, a name not yet given (400 path) followed by a retry, two saves in a row from the same form after the swap (are the hidden fields refreshed from the server's answer?).
- routes.py utc_time: every input type the store can return (int, float, None, very large, negative, NaN, inf, a string); can the fallback text itself break a page or the CSV/JSON paths?
- routes.py QUEUE_LIMIT: off-by-one, filters, Home mode, the caption grammar, list_alerts' own default limit.
- queue.html hx-sync="this:replace": interaction with hx-trigger every 30s and the filter selects (they target #alerts with their own requests); can a filter answer be overwritten by an older refresh?
- base.html historyCacheSize 0: what htmx does on Back/Forward now (read the vendored htmx-2.0.11.min.js), whether a full reload happens, and whether any page breaks.
- app.js: the Web Locks + BroadcastChannel stream (navigation, bfcache, two windows, localhost vs 127.0.0.1, fallback), the mode switch setting next from location (can it become an open redirect? check safe_next in routes.py), statusNotSaved (which events fire for 400 vs 500 vs network errors under the htmx-config responseHandling; can it show "Not saved" after a real save?), focus after upload.
- CSS: minmax(0, 1fr) and white-space: normal side effects at wide and narrow widths.
- Tests: do the new assertions fail on the original code and pass on the fixed one (run them on copies)? Is anything important untested?
Report only problems you reproduced, each with a minimal fix (diff). If a part is sound, say what you checked.`, { label: 'final-review', phase: 'Review', schema: RESULT_SCHEMA })

const [b, r] = await Promise.all([browser, review])
const findings = [...((b && b.findings) || []), ...((r && r.findings) || [])]
let verdicts = null
if (findings.length) {
  phase('Verify')
  verdicts = await agent(`${CTX}
Your label: final-verify. Independently try to REFUTE each finding below about the FINAL dashboard fix: rebuild fixed copies, rerun each repro exactly, and decide whether it is a real defect of the fixed code (not a test artifact, not slowness from other jobs running on this machine, not an unchanged problem outside this change's scope). Default to confirmed=false when unsure. Quote your output.
Findings: ${JSON.stringify(findings, null, 1)}`, { label: 'final-verify', phase: 'Verify', schema: {
    type: 'object', properties: { verdicts: { type: 'array', items: { type: 'object', properties: {
      id: { type: 'string' }, confirmed: { type: 'boolean' }, reason: { type: 'string' }, output: { type: 'string' } },
      required: ['id', 'confirmed', 'reason'] } } }, required: ['verdicts'] } })
}
return { browser: b, review: r, verdicts }
