# Dashboard notes (Ahmad, AHM-02, AHM-03, AHM-06)

Notes for the lead from the reference build of the dashboard. They become the
"What you build" and "Expected output" parts of the AHM-02, AHM-03 and AHM-06
guides.

## Files

| File | What it is |
|---|---|
| `maxguard/web/__init__.py` | empty (step 3) |
| `maxguard/web/routes.py` | `router = APIRouter()`, every HTML page, `Jinja2Templates` |
| `maxguard/web/templates/base.html` | nav, privacy line, Analyst/Home switch, htmx + app.css + app.js |
| `maxguard/web/templates/queue.html` | alert queue with the two filters and the `#alerts` table |
| `maxguard/web/templates/_severity.html` | the severity badge (text + color; words in Home mode) |
| `maxguard/web/templates/upload.html` | upload form (`hx-post="/api/analyses"`) |
| `maxguard/web/templates/alert.html` | alert detail, Analyst and Home modes |
| `maxguard/web/templates/_status.html` | status/assignee form, also the PATCH response fragment |
| `maxguard/web/templates/timeline.html` | `/timeline?ip=` |
| `maxguard/web/templates/assets.html` | `/assets` |
| `maxguard/web/templates/error.html` | 400/404 page |
| `maxguard/web/static/app.css` | styles, 375 px layout (table rows become labelled cards) |
| `maxguard/web/static/app.js` | `EventSource("/api/stream")` -> `htmx.trigger("#alerts", "refresh")`; upload result as text |
| `tests/unit/test_web.py` | 37 tests |

## Routes

```
GET   /                             queue (?status=&severity=; "" = all)
GET   /upload                       upload form
POST  /mode                         Analyst/Home switch -> cookie mg_mode, 303 back to the page
GET   /alerts/{finding_id}          detail (404 page if missing)
PATCH /alerts/{finding_id}/status   form fields actor (first time only), status, assignee
GET   /timeline?ip=&hours=&end=     hours 1..168 (default 24); end = Unix seconds (default now)
GET   /assets                       newest analysis' assets joined with report["devices"]
GET   /favicon.ico                  204 (stops a 404 line in the log on every page)
```

## Commands and real output

```bash
./.venv/bin/pytest tests/unit/test_web.py -q -p no:cacheprovider
```
```text
.....................................                                    [100%]
37 passed in 3.11s
```

Python 3.13 (maxguard-sandbox:test image, Python 3.13.5): `37 passed in 3.41s`.
Whole unit suite: `766 passed, 1 skipped in 15.62s` (before the last 2 web tests were added).

```bash
sha256sum maxguard/web/static/htmx-2.0.11.min.js
```
```text
d6fdc75f204e6bdefa99b69bf1e6d4ac69b8a364f77929f45c13476b4000f717  maxguard/web/static/htmx-2.0.11.min.js
```

```bash
./.venv/bin/ruff check maxguard/web tests/unit/test_web.py
```
```text
All checks passed!
```

Browser check (Chromium 1194 through Playwright 1.63, uvicorn on 127.0.0.1, seeded data):

```text
queue-375: scrollWidth=375 (viewport 375)        # no sideways scrolling on a phone
alert-375 / timeline-375 / assets-375: scrollWidth=375
tab order: Skip to content, Alerts, Upload, Timeline, Devices, Analyst, Home, ← All alerts,
           172.18.0.3, 172.18.0.2, <citation chips>, actor, alert-status, assignee, Save
status form says: Saved.                          # keyboard only: type name, arrow key, Enter
upload result: Done: 1 finding. They are in the alert queue.
POP3 in queue after (no reload): High  POP3 mail retrieval in cleartext ...  New
bad upload result: Upload failed: not a .pcap/.pcapng capture or a .zip/.tar.gz of Zeek logs
console errors/warnings: []                       # no CSP violations
```

Screenshots: `screens/queue.png`, `screens/alert-analyst.png`, `screens/alert-home.png`,
`screens/timeline.png`, `screens/assets.png`, `screens/upload.png`, `screens/queue-375.png`.
The AI sentences in `alert-analyst.png` were written by hand into the stored report (no model
was run).

## Decisions worth explaining in the guides

- **Escaping.** Jinja2 autoescaping is on for `.html`; no template uses `|safe`. app.js
  writes the upload answer with `textContent`. Test: a `<script>` title, detail, AI sentence
  and assignee all come out as `&lt;script&gt;`.
- **Content-Security-Policy on every page** (`default-src 'self'; script-src 'self'; ...`):
  a second wall if escaping ever fails. htmx is configured (meta `htmx-config`) not to inject
  its indicator `<style>`, never to `eval`, never to run `<script>` from a response, and to
  swap 400 answers (form errors) into the page.
- **Referrer-Policy is `same-origin`, not `no-referrer`.** With `no-referrer`, Chromium sends
  `Origin: null` on a normal form post, and the API's cross-site check refuses it (403). Found
  with the Analyst/Home switch in the browser; a unit test pins the header.
- **The mode switch is a POST form**, not a link or JavaScript: keyboard and no-JS friendly,
  refused cross-site by the API middleware, and the `next` path is checked so it cannot
  redirect off the site.
- **Name for the audit trail.** The status form has a "Your name" field until the
  `mg_actor` cookie exists; the PATCH handler sets the cookie. Changes go through
  `StateStore.update_alert(..., at=time.time())`, and `notify_change()` refreshes open queues.
- **Home mode** shows `load_home_text()[rule_id]` headline and action, the severity as words
  ("High: fix this week"), and the device address; no rule IDs, record IDs, framework names
  or technique IDs (tested). The queue in Home mode shows the headline instead of the title.
  The status form is Analyst-only (its words, like "False positive", are jargon).
- **AI next to the rule.** Above the AI sentences the page repeats the rule's title and
  severity and says the severity comes from the rule (ARCHITECTURE section 11).
- **Times** are shown in UTC (`2026-10-06 01:31:25 UTC`): the same on every machine and in
  every screenshot.
- **Timeline links and Zeek uids.** `zeek -D` makes uids repeat across captures: the first
  connection of every lab capture is `CJKFoj4bpHEhTeaRoj`. An event links to an alert when
  its record ID, uid or Community ID is in the alert's evidence **and** it is between the
  alert's two hosts on the alert's port. Matching on uid alone linked the Telnet connection
  to "Expired certificate" (seen in the first screenshot; test
  `test_timeline_links_survive_repeated_zeek_uids`).
- **Timeline window.** `hours` (1, 6, 24, 72, 168) plus an optional `end`. The alert page
  links to `/timeline?ip=...&end=<last_seen + 1>`, so an old capture's events are visible;
  "the last 24 hours" alone would show nothing for a capture recorded last week.
- **Devices page.** A full join: a device seen only in DHCP/DNS still gets a row, sorted by
  IP number (`maxguard.inventory.ip_sort_key`).
