export const meta = {
  name: 'dashboard-round3-verify',
  description: 'Verify the complete dashboard fix (round 3) in Chromium against the original builds, with an adversarial review of the full diff and an independent re-check of anything reported',
  phases: [
    { title: 'Browser', detail: 'every fix proven on fixed AHM-02/AHM-03 builds, each shown failing on the original' },
    { title: 'Review', detail: 'adversarial review of the complete diff' },
    { title: 'Verify', detail: 'independent re-check of findings' },
  ],
}

const SP = '/tmp/claude-0/-home-user-maxguard/d28fe4b6-2c9f-5cd0-8e7f-d2be65aa4c01/scratchpad'
const CTX = `
Setup:
- Write ONLY inside ${SP}/agentwork/<your-label>/ (create it). Do not modify ${SP}/fix3, ${SP}/fix2, ${SP}/fix, ${SP}/ref, ${SP}/docgen, ${SP}/stages or /home/user/maxguard.
- FINAL fixed code: git worktree ${SP}/fix3/ref (branch dashboard-fixes-3); "git -C ${SP}/fix3/ref diff" is the complete change against the original (app.css, app.js, base.html, queue.html, _status.html, alert.html, routes.py, tests/unit/test_web.py). Build private copies of the FIXED project at a roadmap stage: python3 ${SP}/fix3/docgen/build_stage.py AHM-02 <new empty folder> (or AHM-03, or AHM-06 for the full dashboard with timeline links).
- ORIGINAL builds for comparison, READ-ONLY: ${SP}/stages/AHM-02, ${SP}/stages/AHM-03, ${SP}/stages/ALL (copy before running a server that writes data).
- Python 3.11 venv: ${SP}/ref/.venv/bin (uvicorn, pytest, ruff). Start a server from a build folder: cd <build>; MAXGUARD_DATA_DIR=<your folder>/data-<n> ${SP}/ref/.venv/bin/uvicorn maxguard.api.app:create_app --factory --host 127.0.0.1 --port <free port> (pick free ports with python3 -c 'import socket;s=socket.socket();s.bind(("127.0.0.1",0));print(s.getsockname()[1])'; other jobs share this 4-core machine, so allow for slowness and never treat a timeout under load as a defect without a retry). Get the Telnet alert by uploading tests/fixtures/zeek/telnet as a .zip. Helper scripts from earlier reviewers you may copy and adapt: ${SP}/agentwork/dash-review/scripts/ (add_alerts.py adds synthetic alerts of chosen severities; far_future_upload.py; pw_*.js), ${SP}/agentwork/fix-review/scripts/ (t5_back_stale.js, t6_bfcache_pending.js, t7_stream_502.js, t8_midswap.js and others for the shared stream), ${SP}/agentwork/final-review/scripts/ (pw_filter_race.js, pw_restore.js, pw_history.js, pw_upload_focus.js, pw_status.js, pw_home_widths.js, queue_limit.py, hostile_ts_upload.py, pw_newline_assignee.js, pw_name400.js).
- Node + Playwright: require('playwright') works anywhere; chromium.launch() needs no options; never run "playwright install". For back/forward-cache tests launch with channel 'chromium' and ignoreDefaultArgs ['--disable-back-forward-cache'] (the default launch disables bfcache). The axe checker: require('${SP}/tools/node/node_modules/@axe-core/playwright') (axe-core 4.14.0).
- Fonts installed: DejaVu Sans, Liberation Sans, Roboto, Noto Sans. IMPORTANT: page.addStyleTag is refused by the dashboard's CSP (style-src 'self') and silently leaves the default font. Inject a test font through CSSOM instead: await page.evaluate(f => { const s = new CSSStyleSheet(); s.replaceSync('html, body, input, button, select, label, .stack td::before { font-family: "' + f + '" !important }'); document.adoptedStyleSheets = [...document.adoptedStyleSheets, s]; }, font) and confirm getComputedStyle(document.body).fontFamily changed.
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
      regression: { type: 'boolean' }, repro: { type: 'string' }, evidence: { type: 'string' }, fix: { type: 'string' } },
      required: ['id', 'severity', 'title', 'regression', 'repro', 'evidence', 'fix'] } },
    measurements: { type: 'string' },
  },
  required: ['checks', 'findings'],
}

phase('Browser')
const browser = agent(`${CTX}
Your label: r3-browser. Prove every part of the final dashboard fix in Chromium on FIXED builds and show the ORIGINAL fails the same check (fill 'original' and 'fixed' for each). Checks:
1 Width: every page (/, /upload; on AHM-03 also /alerts/<telnet id>, /alerts/0000000000000000, /?status=bogus; on AHM-06 also /timeline?ip=172.18.0.3 and /assets), both modes, at 320, 375, 414, 701, 768 and 1280 px, with the four fonts (CSSOM injection), with alerts of all five severities in the queue (add_alerts.py), with an assignee like firstname.lastname@example-company.com and a 40-character actor name without spaces, and with Ollama absent (the AI-unavailable banner). Pass = document.documentElement.scrollWidth equals the viewport width everywhere.
2 Focus through a live refresh (PATCH from another client while an alert link has focus) and after Save (keyboard only): focus stays where it was.
3 Shared stream: 8 queue tabs in one context use exactly one /api/stream; a 9th tab (/upload) loads; one PATCH reaches all 8 tabs within 3 s; closing the holder hands over; a second PATCH reaches all. Then the four cases fixed in round 3: (a) Back after Save or after Upload with two queue tabs open shows the new state within 2 s, not after 30 s; (b) a queue page parked in bfcache (full chromium with bfcache on) does not end up holding the lock while a new tab gets no stream; (c) a stub answering 502 on the stream port during a restart: after the server returns, live refresh works again within about 10 s; (d) two PATCHes 200 ms apart while a slow (800 ms) table answer is in flight: both changes show without waiting for the poll. Fallback: navigator.locks deleted by an init script → one stream per tab, still works.
4 Filter race: trigger a refresh, 100 ms later choose Severity = Medium while every table answer takes 800 ms (route delay): the table ends filtered and the address matches.
5 Back/Forward: choose status, then severity, press Back: selects, rows and address agree, and it is a full page load (document changed); then the Analyst/Home switch keeps the filter. Back while the server is unreachable shows the browser's own error, not a half page.
6 Status form: (a) two analysts: Fiona sets Investigating while Ahmad's page still shows New; Ahmad saves only an assignee → status stays Investigating, audit shows only his assignee change; (b) Chrome form restore after Back cannot undo Fiona's change (autocomplete off); (c) a name of only spaces is refused by the browser before any request; (d) server stopped → "No answer from the MaxGuard server: the change may not be saved. Reload the page to check."; (e) an assignee set through the JSON API with a line break is not "changed" by a status-only save.
7 Impossible times: upload a zip of the Telnet logs with ts=1e12, then 1e400 (inf): every page (queue, alert in both modes, timeline on AHM-06) answers 200, the alert page's timeline links carry no end= for those, and the time shows as "(not a valid time)".
8 Queue limit: 201 alerts → 200 rows and the caption 'The 200 most severe alerts, most recent first. More alerts match and are not shown: choose a status and a severity to see them.'; with both filters set the caption ends 'are not shown.'; 3 alerts → '3 alerts, most severe first'.
9 Upload focus: after an upload, focus is on Analyze; if the person moved to another link during the upload, focus stays there.
10 Home title, aside landmark, and axe (default rules plus wcag2a/wcag2aa/wcag21aa) on every page of the fixed AHM-06 build in both modes at 1280 and 375 px: list every violation for fixed and original; pass = none in the fixed build.
11 Regression: AHM-02 step 7 curl header check matches the guide; no request leaves 127.0.0.1; every control reachable with Tab in DOM order; ruff check . and pytest -m "not integration" -q in the fixed AHM-02, AHM-03 and AHM-06 builds (quote the last line).
Report compact numbers in 'measurements' (widths, fonts, timings, counts) and save screenshots of the Home queue at 375 px with five severities, the upload page at 320 px, and the alert page with the AI banner at 320 px.`, { label: 'r3-browser', phase: 'Browser', schema: RESULT_SCHEMA })

const review = agent(`${CTX}
Your label: r3-review. Adversarially review the COMPLETE final change: git -C ${SP}/fix3/ref diff, and read every changed file whole. Earlier reviewers already fixed: the shared-stream catch-up, bfcache lock and 502 cases; the filter race; inf timestamps; autocomplete=off; refreshOnHistoryMiss; upload focus guard; the 'no answer' wording; overflow-wrap and badge wrapping; the caption; text_field for line breaks; the actor pattern. Your job is what is still wrong after all that. Attack: app.js as a whole (the two lock requests in join(): can a tab end up with two streams, or none, after pagehide/pageshow cycles, or when ifAvailable grants the lock while a queued request from the same tab is pending? the 'again' flag with hx-sync replace; the beforeOnLoad re-targeting when #alerts is absent or when the filter answer is a 400 page; refresh() when #alerts is missing (an error page swapped in?); memory and listener leaks over many refreshes), routes.py (timeline_end types, text_field on non-strings, QUEUE_LIMIT+1 with filters, stale-form logic against a hostile client sending shown_status as a file part or a list), templates (the caption grammar for 1 row, the aside inside the header order for screen readers, title escaping), CSS (overflow-wrap: anywhere on .stack td can break IDs and hashes mid-string: is that acceptable for record IDs in the alert page's evidence table? check what it does to the mono columns), tests (mutation-test the new assertions: can each listed fix be reverted without a test failing? list the ones that are only string checks). Prove every problem on a fixed build with a test or Playwright script, mark regression=true when the original did not have it, and give a minimal fix (diff). If a part is sound, say what you checked.`, { label: 'r3-review', phase: 'Review', schema: RESULT_SCHEMA })

const [b, r] = await Promise.all([browser, review])
const findings = [...((b && b.findings) || []), ...((r && r.findings) || [])]
let verdicts = null
if (findings.length) {
  phase('Verify')
  verdicts = await agent(`${CTX}
Your label: r3-verify. Independently try to REFUTE each finding below about the final dashboard fix: rebuild fixed copies, rerun each repro exactly, and decide whether it is a real defect of the fixed code (not a test artifact, not slowness from other jobs, not an unchanged problem outside this change's scope). Default to confirmed=false when unsure. Quote your output.
Findings: ${JSON.stringify(findings, null, 1)}`, { label: 'r3-verify', phase: 'Verify', schema: {
    type: 'object', properties: { verdicts: { type: 'array', items: { type: 'object', properties: {
      id: { type: 'string' }, confirmed: { type: 'boolean' }, reason: { type: 'string' }, output: { type: 'string' } },
      required: ['id', 'confirmed', 'reason'] } } }, required: ['verdicts'] } })
}
return { browser: b, review: r, verdicts }
