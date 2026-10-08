    {
        "id": "AHM-02", "owner": "ahmad", "milestone": "W3",
        "title": "Dashboard: layout, alert queue, and upload page",
        "labels": ["area:ui", "critical-path"],
        "depends": ["JAI-07"],
        "goal": (
            "Build the first dashboard pages with FastAPI, Jinja2 and htmx: a base layout with the "
            "privacy note and the Analyst/Home switch, the alert queue (severity, title, source → "
            "destination:port, count, status, assignee, last seen) with filters and live refresh, "
            "and an upload page."
        ),
        "prereq": "JAI-07 (the API and `create_app`) is merged. Read `docs/ARCHITECTURE.md` "
                  "sections 10 and 14 first.",
        "steps": [
            start_step("ahmad/dashboard-queue"),
            "Vendor htmx (one file, 0BSD license) from the npm registry and check it is the exact "
            "file the team reviewed:\n\n@@RUN htmx@@\n\nOn macOS use `shasum -a 256` instead of "
            "`sha256sum`. htmx already has a row in `docs/DEPENDENCIES.md`.",
            "Create `maxguard/web/__init__.py` (one line):\n\n@@FILE maxguard/web/__init__.py@@\n\n"
            "and `maxguard/web/routes.py`:\n\n@@FILE maxguard/web/routes.py@@\n\n"
            "`create_app()` includes this router as soon as the module exists. What to notice: "
            "`render()` adds three headers to every page. The **Content-Security-Policy** tells "
            "the browser to load and run nothing that does not come from this computer, a second "
            "wall in case some text ever slipped past escaping. **Referrer-Policy** is "
            "`same-origin`, not `no-referrer`: with `no-referrer`, Chrome sends `Origin: null` "
            "on form posts, and the API's cross-site check refuses those (found in a real "
            "browser, not by a unit test). The Analyst/Home switch is a small `POST` form, so it "
            "works with the keyboard and without JavaScript, and `safe_next()` keeps its "
            "redirect on this site.",
            "Create the templates in `maxguard/web/templates/`. The layout, `base.html` (the "
            "`htmx-config` tag keeps htmx inside the CSP: no inline styles, no `eval`, no scripts "
            "from responses, only this site):\n\n@@FILE maxguard/web/templates/base.html@@\n\n"
            "The severity badge `_severity.html` (the word *and* a color, never color alone) and "
            "the error page `error.html`:\n\n@@FILE maxguard/web/templates/_severity.html@@\n\n"
            "@@FILE maxguard/web/templates/error.html@@\n\n"
            "The queue, `queue.html`:\n\n@@FILE maxguard/web/templates/queue.html@@\n\n"
            "and the upload page, `upload.html`:\n\n@@FILE maxguard/web/templates/upload.html@@\n\n"
            "No template uses `|safe`: titles, addresses and names come from network traffic, "
            "which an attacker writes. The queue links each alert to its detail page, which "
            "arrives in AHM-03.",
            "Create `maxguard/web/static/app.css` (it already holds the styles for the pages of "
            "AHM-03 and AHM-06):\n\n@@FILE maxguard/web/static/app.css@@\n\n"
            "and `maxguard/web/static/app.js`, the only script besides htmx:\n\n"
            "@@FILE maxguard/web/static/app.js@@\n\n"
            "The live refresh: the server sends `alerts-changed` on `/api/stream`, and the table "
            "reloads itself; `hx-trigger=\"refresh, every 30s\"` is the fallback. The upload "
            "answer is written with `textContent`, never `innerHTML`, because an error message "
            "can contain a file name.",
            "Create the tests `tests/unit/test_web.py`:\n\n@@FILE tests/unit/test_web.py@@\n\n"
            "Run them:\n\n@@RUN tests@@",
            "Start the server and check the headers every page sends:\n\n@@RUN headers@@",
            "Open http://127.0.0.1:8000, upload `tests/fixtures/zeek/telnet` as a `.zip` on the "
            "Upload page, and watch the alert appear in the queue in another tab without "
            "reloading. Then check the pages in a 375-pixel-wide window (your browser's device "
            "toolbar) and with the keyboard only (Tab, Enter, arrow keys). In planning, Chromium "
            "at 375 px showed no sideways scrolling, and every control was reachable with Tab.",
            pr_step("feat: dashboard layout, alert queue and upload page (AHM-02)", "JWinborne1"),
        ],
        "files": ["maxguard/web/__init__.py", ("maxguard/web/routes.py", "snip:web_routes_v1.py"),
                  ("maxguard/web/templates/base.html", "snip:web_base_v1.html"),
                  "maxguard/web/templates/_severity.html", "maxguard/web/templates/error.html",
                  ("maxguard/web/templates/queue.html", "snip:web_queue_v1.html"),
                  "maxguard/web/templates/upload.html", "maxguard/web/static/app.css",
                  "maxguard/web/static/app.js", "maxguard/web/static/htmx-2.0.11.min.js",
                  ("tests/unit/test_web.py", "snip:test_web_v1.py")],
        "commands": [
            {"id": "htmx", "show": (
                "mkdir -p maxguard/web/static\n"
                "curl -sSL https://registry.npmjs.org/htmx.org/-/htmx.org-2.0.11.tgz -o /tmp/htmx.tgz\n"
                "tar -xzOf /tmp/htmx.tgz package/dist/htmx.min.js > maxguard/web/static/htmx-2.0.11.min.js\n"
                "sha256sum maxguard/web/static/htmx-2.0.11.min.js")},
            {"id": "tests", "show": "pytest tests/unit/test_web.py -q"},
            {"id": "headers",
             "show": ("# terminal 1:\n"
                      "uvicorn maxguard.api.app:create_app --factory --host 127.0.0.1 --port 8000\n"
                      "# terminal 2:\n"
                      "curl -s -D - -o /dev/null http://127.0.0.1:8000/ | grep -i -E "
                      "'^(content-security-policy|referrer-policy|x-content-type-options):'"),
             "run": ("(uvicorn maxguard.api.app:create_app --factory --host 127.0.0.1 --port 18000 "
                     "> /tmp/ahm02-uvicorn.log 2>&1 & echo $! > /tmp/ahm02-uvicorn.pid)\n"
                     "for i in $(seq 1 50); do curl -s -o /dev/null http://127.0.0.1:18000/docs "
                     "&& break; sleep 0.2; done\n"
                     "curl -s -D - -o /dev/null http://127.0.0.1:18000/ | grep -i -E "
                     "'^(content-security-policy|referrer-policy|x-content-type-options):'\n"
                     "kill $(cat /tmp/ahm02-uvicorn.pid)")},
        ],
        "test": (
            "`pytest tests/unit/test_web.py -q` passes. Uploading the Telnet fixture logs on "
            "http://127.0.0.1:8000/upload makes the Telnet alert appear in the queue in another "
            "tab without reloading the page."
        ),
        "why": (
            "Server-rendered pages with htmx keep the whole dashboard in Python and one small, "
            "vendored JavaScript file, so it works offline and every dependency is accounted for. "
            "Escaping everything matters because alert titles and hosts come from network traffic, "
            "which an attacker controls (`docs/ARCHITECTURE.md` section 14)."
        ),
        "checklist": checklist(extra=["The htmx file's SHA-256 matches",
                                      "Nothing loads from outside the app",
                                      "Usable with the keyboard and at 375 px"]),
    },
    {
        "id": "AHM-03", "owner": "ahmad", "milestone": "W4",
        "title": "Alert detail page with Analyst and Home modes",
        "labels": ["area:ui", "critical-path"],
        "depends": ["AHM-02", "JON-02", "JON-04"],
        "goal": (
            "Show one alert in full. Analyst mode: evidence records, controls grouped by framework "
            "(with version), ATT&CK techniques, and the AI's sentences, each followed by links to "
            "the records it cites, plus the status and assignee form. Home mode: the headline, "
            "the severity in plain words, and one action, with no jargon."
        ),
        "prereq": "AHM-02, JON-02 (AI sentences) and JON-04 (Home text) are merged.",
        "steps": [
            start_step("ahmad/alert-detail"),
            "Extend `maxguard/web/routes.py` with the alert page and the status form (the new "
            "parts are under `# ---------- AHM-03`; the queue now passes the Home text "
            "too):\n\n@@FILE maxguard/web/routes.py@@\n\n"
            "`update_alert()` needs `at=now()`: the stores never read the clock, the web layer "
            "does, in one place (`now()`), so tests can replace it. After a change, "
            "`notify_change()` makes every open queue refresh itself.",
            "Create `maxguard/web/templates/alert.html`:\n\n"
            "@@FILE maxguard/web/templates/alert.html@@\n\n"
            "and the status form fragment `_status.html`, which the `PATCH` answer replaces "
            "in place:\n\n@@FILE maxguard/web/templates/_status.html@@\n\n"
            "Each evidence row has `id=\"ev-<record_id>\"`, and every AI sentence is followed by "
            "links to the rows it cites: that is how an analyst checks the AI instead of trusting "
            "it (CLAUDE.md rule 3). Above the sentences the page repeats the rule's title and "
            "severity and says the severity comes from the rule. In Home mode the page shows the "
            "headline and action from `load_home_text()`, the severity in words (\"High: fix "
            "this week\") and the device's address, and no rule, record, framework or technique "
            "IDs. The status form appears in Analyst mode only: its words, such as \"False "
            "positive\", are jargon.",
            "In Home mode the queue shows the Home headline instead of the rule title. Update "
            "`maxguard/web/templates/queue.html`:\n\n"
            "@@FILE maxguard/web/templates/queue.html@@",
            "Add the AHM-03 tests to `tests/unit/test_web.py` (the new section is "
            "`# ---------- AHM-03`):\n\n@@FILE tests/unit/test_web.py@@\n\nRun them:\n\n"
            "@@RUN tests@@",
            "Open an alert in both modes and change its status with the keyboard only. Then ask "
            "someone who is not technical to read the Home view of the Telnet alert and say what "
            "they would do.",
            pr_step("feat: alert detail with Analyst and Home modes (AHM-03)", "JWinborne1"),
        ],
        "files": [("maxguard/web/routes.py", "snip:web_routes_v2.py"),
                  ("maxguard/web/templates/alert.html", "snip:web_alert_v1.html"),
                  "maxguard/web/templates/_status.html", "maxguard/web/templates/queue.html",
                  ("tests/unit/test_web.py", "snip:test_web_v2.py")],
        "commands": [
            {"id": "tests", "show": "pytest tests/unit/test_web.py -q"},
        ],
        "test": "The tests pass, and a non-technical friend can read the Home view of the Telnet "
                "alert and say what to do.",
        "why": (
            "The citation links are how an analyst checks the AI instead of trusting it: every "
            "sentence leads to the exact record behind it (CLAUDE.md rule 3). Home mode exists "
            "because most small-network owners are not analysts; the same alert, in plain words, "
            "with one action, is what makes them act."
        ),
        "checklist": checklist(extra=["No `|safe` on traffic or AI text",
                                      "Status changes appear in the audit trail"]),
    },
    {
        "id": "AHM-06", "owner": "ahmad", "milestone": "S4",
        "title": "IP timeline and device inventory pages",
        "labels": ["area:ui"],
        "depends": ["AHM-03", "JAK-08", "JAI-07", "JAK-07"],
        "goal": (
            "Add `/timeline?ip=` (everything one address did, in time order, with links to the "
            "alerts that involve it) and `/assets` (the device inventory with MAC addresses and "
            "names from device attribution)."
        ),
        "prereq": "AHM-03 and JAK-08 (device attribution) are merged.",
        "steps": [
            start_step("ahmad/timeline-devices"),
            "The device table (JAK-08) must travel in the report: the log folder is deleted "
            "after an upload, so the dashboard cannot rebuild it later. In "
            "`maxguard/pipeline.py`, import `build_device_table` next to `build_inventory` and "
            "add a `devices` key after `assets` (a new optional report key, so nothing that "
            "reads reports breaks; tell Jaiden in the pull request):\n\n"
            "@@FILE maxguard/pipeline.py@@\n\n"
            "Update `tests/unit/test_pipeline.py`: the report's key list gains `devices`, and a "
            "new test checks the DHCP fixture's laptop:\n\n@@FILE tests/unit/test_pipeline.py@@",
            "Add the timeline and the devices page to `maxguard/web/routes.py` (the new section "
            "is `# ---------- AHM-06`):\n\n@@FILE maxguard/web/routes.py@@\n\n"
            "Two traps this code avoids. First, Zeek uids are not unique across captures: "
            "`zeek -D`, used for uploads so results repeat, gives the first connection of "
            "*every* capture the same uid, so linking an event to an alert by uid alone linked "
            "the Telnet connection to \"Expired certificate\". An event links to an alert only "
            "when its record ID, uid or Community ID is in the alert's evidence **and** it is "
            "between the alert's two hosts on the alert's port. Second, a finding often cites a "
            "record that is not a timeline event (a `maxguard_cleartext.log` line, for "
            "example); the connection's `conn.log` event shares its uid, which is why the uid "
            "is matched too. The window is 1, 6, 24, 72 or 168 hours; the optional `end` "
            "(Unix seconds) moves it back, so the alert page can link to the time of an old "
            "capture. The devices page is a full join: a phone seen only in DHCP still gets a "
            "row.",
            "Create `maxguard/web/templates/timeline.html` and `assets.html`:\n\n"
            "@@FILE maxguard/web/templates/timeline.html@@\n\n"
            "@@FILE maxguard/web/templates/assets.html@@",
            "Add Timeline and Devices to the navigation in `base.html`, and link the alert "
            "page's addresses to their timelines in `alert.html`:\n\n"
            "@@FILE maxguard/web/templates/base.html@@\n\n"
            "@@FILE maxguard/web/templates/alert.html@@",
            "Add the AHM-06 tests to `tests/unit/test_web.py` (the new section is "
            "`# ---------- AHM-06`). They never depend on the real clock: they replace "
            "`routes.now` or pass `end=`:\n\n@@FILE tests/unit/test_web.py@@\n\n"
            "Run the dashboard and pipeline tests:\n\n@@RUN tests@@",
            "Check both pages at 375 px and with the keyboard only.",
            pr_step("feat: IP timeline and device inventory pages (AHM-06)", "JWinborne1"),
        ],
        "files": [("maxguard/pipeline.py", "snip:pipeline_v4.py"), "tests/unit/test_pipeline.py",
                  "maxguard/web/routes.py", "maxguard/web/templates/timeline.html",
                  "maxguard/web/templates/assets.html", "maxguard/web/templates/base.html",
                  "maxguard/web/templates/alert.html", "tests/unit/test_web.py"],
        "commands": [
            {"id": "tests", "show": "pytest tests/unit/test_web.py tests/unit/test_pipeline.py -q"},
        ],
        "test": "The new tests pass and the pages work at 375 px.",
        "why": (
            "Alerts say *what* happened; the timeline says *what else that device did*, which is "
            "how an analyst decides whether an alert is a one-off or part of something bigger."
        ),
        "checklist": checklist(extra=["Timeline links check hosts and port, not the uid alone"]),
    },
