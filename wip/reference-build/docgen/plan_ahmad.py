"""Ahmad's tasks: GitHub setup, dashboard pages, security review, response module, acceptance."""

from plan_helpers import checklist, pr_step, start_step

TASKS = [
    {
        "id": "AHM-01", "owner": "ahmad", "milestone": "W0",
        "title": "Set up GitHub for the team: access, Discussions, labels, milestones, issues",
        "labels": ["area:program", "critical-path"], "status": "process",
        "depends": [],
        "goal": (
            "Make the repository ready for eight people as early in Week 0 as possible: everyone has write "
            "access, Discussions is on with a pinned \"Week 0 check-in\", private vulnerability "
            "reporting is on, and every roadmap task exists as an issue with its labels and "
            "milestone on the project board."
        ),
        "prereq": "The planning pull request (it adds `scripts/create_issues.sh` and the "
                  "templates) is merged. You need admin rights on the repository.",
        "steps": [
            "**Access.** On github.com: **Settings → Collaborators → Add people**, and invite "
            "each teammate by the GitHub name in `docs/TEAM.md` with the **Write** role.",
            "**Discussions.** **Settings → General → Features**: tick **Discussions**. GitHub "
            "creates the categories the team uses (*Announcements*, *Q&A*, *Ideas*, *General*). "
            "Then open **Discussions → New discussion → General**, title `Week 0 check-in`, body: "
            "\"Reply with the output of `git --version`, `python3.11 --version`, `docker --version`, "
            "and the first line of your `http.log` from Week 0 step 0.8.\" Open it and click "
            "**Pin discussion**.",
            "**Security reports.** In **Settings**, open the page in the *Security* part of the "
            "sidebar (named *Code security* or *Advanced Security*, depending on the account) and "
            "**Enable** **Private vulnerability reporting**, so outsiders can report a problem "
            "without a public issue. *Not run in planning — verify on github.com.*",
            "**Labels, milestones, issues, and the project.** The GitHub CLI needs the `project` "
            "permission for the board:\n\n```bash\ngh auth refresh -s project\n```\n\n"
            "Preview what the script will do (it changes nothing in this mode):\n\n@@RUN dry@@\n\n"
            "Then run it for real (*not run in planning*; it is safe to run again, it skips what "
            "already exists):\n\n```bash\nbash scripts/create_issues.sh\n```",
            "Check the result: **Issues** lists every task (title starts with its ID, such as "
            "`JAI-01`), each with an `owner:` label and a milestone, and **Projects → MaxGuard "
            "v2.0 Roadmap** shows them all. Assign each issue to its owner once they accept the "
            "invitation (GitHub can only assign collaborators).",
            "Post in **Announcements**: the link to `docs/roadmap/README.md` and \"Start with "
            "Week 0 in your own file\".",
        ],
        "files": [], "commands": [
            {"id": "dry", "env": "none", "show": "DRY_RUN=1 bash scripts/create_issues.sh | head -n 25",
             "output_file": "outputs/_static/create_issues_dry_run.txt",
             "label": "Expected output (recorded in planning)",
             "note": "Recorded in planning with a stand-in for `gh` that only prints the calls."},
        ],
        "test": "Every teammate can open the pinned discussion, sees their issues with "
                "`owner:<name>`, and has write access (they can push a branch).",
        "why": (
            "Issues, labels, and milestones made by a script are consistent and complete; made by "
            "hand, 69 of them would not be. The board then shows at a glance who is blocked and "
            "what is late, which is what the Friday review needs. Discussions keeps answers "
            "searchable for the next person with the same problem."
        ),
        "checklist": [
            "All seven teammates accepted the invitation",
            "The `Week 0 check-in` discussion is pinned",
            "Private vulnerability reporting is on",
            "Every roadmap task has an issue, a milestone and its labels",
        ],
    },
    {
        "id": "AHM-02", "owner": "ahmad", "milestone": "W3",
        "title": "Dashboard: layout, alert queue, and upload page",
        "labels": ["area:ui", "critical-path"], "status": "design",
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
            "`sha256sum`. Add a row for htmx to `docs/DEPENDENCIES.md` if it is not there.",
            "Create `maxguard/web/__init__.py` (empty) and `maxguard/web/routes.py` with "
            "`router = APIRouter()`. `create_app()` already includes this router when the module "
            "exists. Read stores only through `request.app.state.state_store` and "
            "`request.app.state.event_store`; templates come from `maxguard/web/templates/` with "
            "`Jinja2Templates` (autoescaping is on by default for `.html`).",
            "`templates/base.html`: a `<nav>` (Alerts, Upload; Timeline and Devices come in "
            "AHM-06), the line **\"Your data never leaves this computer.\"**, the Analyst/Home "
            "switch stored in a cookie `mg_mode`, `<script src=\"/static/htmx-2.0.11.min.js\">` "
            "(never a CDN), and `/static/app.css`.",
            "`GET /` → `templates/queue.html`: the alert table from "
            "`state_store.list_alerts(status=..., severity=...)`; the two filters are `<select>`s "
            "with `hx-get=\"/\" hx-target=\"#alerts\" hx-select=\"#alerts\"`. Severity is shown as "
            "text *and* color, never color alone.",
            "Live refresh: `static/app.js` opens `new EventSource(\"/api/stream\")` and on each "
            "`alerts-changed` message calls `htmx.trigger(\"#alerts\", \"refresh\")`; the table "
            "also has `hx-trigger=\"refresh, every 30s\"` as a fallback.",
            "`GET /upload` → a form that posts the file to `/api/analyses` "
            "(`hx-post`, `hx-encoding=\"multipart/form-data\"`) and then links to the queue.",
            "Tests `tests/unit/test_web.py` with `TestClient(create_app(tmp_path, explain=False))` "
            "and alerts saved through `StateStore.save_analysis()` from a fixture report: the "
            "pages return 200, the queue lists the Telnet alert, the filters work, a value with "
            "`<script>` in it is shown escaped, and no page loads anything from outside "
            "(no `http://` or `https://` in any `src` or `href` except links in text).",
            "Check the pages on a 375-pixel-wide window and with the keyboard only.",
            pr_step("feat: dashboard layout, alert queue and upload page (AHM-02)", "JWinborne1"),
        ],
        "files": [], "commands": [
            {"id": "htmx", "show": (
                "mkdir -p maxguard/web/static\n"
                "curl -sSL https://registry.npmjs.org/htmx.org/-/htmx.org-2.0.11.tgz -o /tmp/htmx.tgz\n"
                "tar -xzOf /tmp/htmx.tgz package/dist/htmx.min.js > maxguard/web/static/htmx-2.0.11.min.js\n"
                "sha256sum maxguard/web/static/htmx-2.0.11.min.js")},
            {"id": "tests", "env": "none", "show": "pytest tests/unit/test_web.py -q"},
        ],
        "test": (
            "`pytest tests/unit/test_web.py -q` passes. With `docker compose -f docker/compose.yaml "
            "-f docker/compose.dev.yaml up --build`, uploading `tests/pcaps/telnet.pcap` on "
            "http://127.0.0.1:8000/upload makes the Telnet alert appear in the queue without "
            "reloading the page."
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
        "labels": ["area:ui", "critical-path"], "status": "design",
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
            "`GET /alerts/{finding_id}` → `templates/alert.html` from "
            "`state_store.get_alert(finding_id)` (404 page if missing).",
            "Analyst mode: an evidence table (`record_id`, log, uid, time) where each row has "
            "`id=\"ev-<record_id>\"`; controls grouped by framework, showing the version next to "
            "each framework name; techniques with their tactic; then the AI sentences, each "
            "followed by small links `#ev-<record_id>` (the citation chips).",
            "If the stored report's `ai.status` is `unavailable`, show a clear banner with "
            "`ai.reason` (for example \"model 'qwen3:4b' not found: run ollama pull qwen3:4b\").",
            "Home mode (cookie `mg_mode=home`): the headline and action from "
            "`maxguard.ai.load_home_text()[rule_id]`, the severity as words (\"High: fix this "
            "week\"), and no IDs or framework names.",
            "Status and assignee: a small form that sends `hx-patch` to an HTML endpoint "
            "`/alerts/{finding_id}/status`, which calls "
            "`state_store.update_alert(finding_id, actor=<name from the mg_actor cookie>, "
            "at=time.time(), status=..., assignee=...)` and returns the updated fragment. The page "
            "asks for a display name once and stores it in `mg_actor`.",
            "AI text and everything from traffic is plain text in the templates: never `|safe`.",
            "Tests in `tests/unit/test_web.py`: both modes render, the citation links point to "
            "existing evidence rows, a status change is saved and appears in `list_audit()`, and "
            "the banner shows when the AI was unavailable.",
            pr_step("feat: alert detail with Analyst and Home modes (AHM-03)", "JWinborne1"),
        ],
        "files": [], "commands": [
            {"id": "tests", "env": "none", "show": "pytest tests/unit/test_web.py -q"},
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
        "id": "AHM-04", "owner": "ahmad", "milestone": "W5",
        "title": "Security review of the alpha",
        "labels": ["area:program"], "status": "process",
        "depends": ["AHM-03", "JON-03", "AMO-03"],
        "goal": (
            "Before the feature freeze, walk through every threat in `docs/ARCHITECTURE.md` "
            "section 14 against the real code and record, for each, how it is defended and how "
            "you checked."
        ),
        "prereq": "The alpha features are merged (AHM-03, JON-03, AMO-03 at least).",
        "steps": [
            "For each row of the threat table, find the code and the test that defend it, and try "
            "the attack yourself where it is safe: a zip whose files unpack to more than 4 GiB, a "
            "file named `../../x` inside a tar, an HTTP host name containing `<script>` in a "
            "capture, a CSV cell starting with `=`, the dashboard from another machine on the LAN.",
            "Run `pip-audit` (or GitHub's Dependabot alerts) on the installed packages and check "
            "Zeek's, Suricata's and Ollama's release notes for security fixes since our pinned "
            "versions.",
            "Write `docs/security-review-alpha.md`: one row per threat with *defense*, *how "
            "checked*, *result*, and an issue link for anything that failed (label `type:bug` and "
            "`critical-path` if it blocks the release).",
        ],
        "files": [], "commands": [],
        "test": "Every threat has a result, and every failure has an issue with an owner.",
        "why": (
            "A security tool with a security hole is worse than no tool. Checking the defenses "
            "against the running code, not against the design document, is the Security Lead's "
            "job before the alpha goes to an outside tester."
        ),
        "checklist": ["Every threat in section 14 has a result",
                      "Every failure has an issue"],
    },
    {
        "id": "AHM-05", "owner": "ahmad", "milestone": "W8",
        "title": "Alpha acceptance test and presentation",
        "labels": ["area:program", "critical-path"], "status": "process",
        "depends": ["JAI-10", "KAR-05"],
        "goal": (
            "Run the `v2.0-alpha` acceptance test with someone who did not build the release, "
            "record each result, and give the end-of-semester presentation."
        ),
        "prereq": "JAI-10 has tagged `v2.0-alpha`.",
        "steps": [
            "Follow the acceptance test in `docs/roadmap/README.md` with the tester; write the "
            "result of each step in the findings log.",
            "Prepare the presentation: the problem, the architecture (section 1 diagram), a live "
            "demo of upload → alert → explanation with citations → Home mode, what is next in "
            "spring, and what each person built.",
        ],
        "files": [], "commands": [],
        "test": "All ten acceptance steps pass, or the failures are documented with issues.",
        "why": "A release is done when someone else can install and use it, not when the code is merged.",
        "checklist": ["Acceptance results recorded", "Presentation delivered"],
    },
    {
        "id": "AHM-06", "owner": "ahmad", "milestone": "S4",
        "title": "IP timeline and device inventory pages",
        "labels": ["area:ui"], "status": "design",
        "depends": ["AHM-03", "JAK-08", "JAI-07"],
        "goal": (
            "Add `/timeline?ip=` (everything one address did, in time order, with the ATT&CK "
            "techniques of findings that involve it) and `/assets` (the device inventory with MAC "
            "addresses and names from device attribution)."
        ),
        "prereq": "AHM-03 and JAK-08 (device attribution) are merged.",
        "steps": [
            start_step("ahmad/timeline-devices"),
            "`GET /timeline?ip=<address>`: validate the address with `ipaddress.ip_address` (400 "
            "if invalid); events from `event_store.query(ip=..., since=..., until=...)` (default "
            "the last 24 hours, with a selector up to 7 days); each row shows time, kind, summary, "
            "and a link to the alert if a finding cites that event.",
            "`GET /assets`: the inventory of the latest analysis joined with the device table "
            "(MAC, host name, DNS names); each IP links to its timeline.",
            "Tests in `tests/unit/test_web.py` with events written through `EventStore.write()`.",
            pr_step("feat: IP timeline and device inventory pages (AHM-06)", "JWinborne1"),
        ],
        "files": [], "commands": [], "test": "The new tests pass and the pages work at 375 px.",
        "why": (
            "Alerts say *what* happened; the timeline says *what else that device did*, which is "
            "how an analyst decides whether an alert is a one-off or part of something bigger."
        ),
        "checklist": checklist(),
    },
    {
        "id": "AHM-07", "owner": "ahmad", "milestone": "S8",
        "title": "Response: block proposals, generated rules, and preview before you block",
        "labels": ["area:response"],
        "depends": ["JAI-06", "JAI-07"],
        "goal": (
            "Let an analyst propose blocking one IP address and see, before anything happens, the "
            "exact firewall commands (with their undo commands) and what the block would have "
            "stopped in the last 7 days (`docs/ARCHITECTURE.md` section 13)."
        ),
        "prereq": "JAI-06 and JAI-07 are merged.",
        "steps": [
            start_step("ahmad/response-generate"),
            "Create `maxguard/response/__init__.py` (one line):\n\n"
            "@@FILE maxguard/response/__init__.py@@\n\n"
            "and `maxguard/response/generate.py`:\n\n@@FILE maxguard/response/generate.py@@\n\n"
            "Four things to notice. `parse_ip()` is the only way an address gets into a "
            "command, and `ipaddress.ip_address()` alone is not enough: it accepts "
            "`2001:db8::1%$(id)` (an IPv6 *scope*, which can hold shell syntax) and plain "
            "integers (`16909060` means `1.2.3.4`), so those are refused too. An nftables set "
            "holds one address family, and a block has a direction, so there are four sets, "
            "created once by `NFT_SETUP`. *Direction* means who starts the connection: "
            "`inbound` blocks connections the address starts, `outbound` blocks connections "
            "your devices start toward it; the rules match conntrack's *original* direction, "
            "so an inbound block still lets your own connections to that address work. And "
            "each `nft` command is one quoted argument, so the shell never reads the braces.",
            "Check the generated commands for real. `nicolaka/netshoot:v0.15` has `nft` and "
            "`iptables`; `--network none` gives the container only its own loopback, so "
            "nothing can leave it. The setup file is loaded twice to show that running it "
            "again never doubles the rules:\n\n@@RUN nft@@",
            "Create `maxguard/response/preview.py`:\n\n@@FILE maxguard/response/preview.py@@\n\n"
            "`window_end` comes from the caller, never from the clock, so the same events "
            "always give the same preview. One connection seen in `conn.log`, `ssl.log` and "
            "`eve.json` counts once (by `community_id`).",
            "Create the tests `tests/unit/test_response_generate.py`:\n\n"
            "@@FILE tests/unit/test_response_generate.py@@\n\n"
            "and `tests/unit/test_response_preview.py`:\n\n"
            "@@FILE tests/unit/test_response_preview.py@@\n\nRun them:\n\n@@RUN tests@@",
            pr_step("feat: block proposals with generated rules and preview (AHM-07)", "JWinborne1"),
        ],
        "files": ["maxguard/response/__init__.py", "maxguard/response/generate.py",
                  "maxguard/response/preview.py", "tests/unit/test_response_generate.py",
                  "tests/unit/test_response_preview.py"],
        "commands": [
            {"id": "nft", "show": (
                "mkdir -p data/nft-check\n"
                "python - <<'EOF'\n"
                "from pathlib import Path\n"
                "from maxguard.response.generate import NFT_SETUP, rules_for\n"
                "Path(\"data/nft-check/maxguard-setup.nft\").write_text(NFT_SETUP)\n"
                "r = rules_for(\"203.0.113.7\", \"both\")\n"
                "commands = (r[\"nftables\"][\"block\"] + r[\"iptables\"][\"block\"]\n"
                "            + [\"nft list set inet maxguard maxguard_block_in_v4 | grep elements\",\n"
                "               \"iptables -S | grep maxguard\"]\n"
                "            + r[\"nftables\"][\"undo\"] + r[\"iptables\"][\"undo\"]\n"
                "            + ['echo \"rules left: $(iptables -S | grep -c maxguard)\"'])\n"
                "# The container runs as root, so sudo is not needed there.\n"
                "Path(\"data/nft-check/run.sh\").write_text(\"\\n\".join(commands).replace(\"sudo \", \"\") + \"\\n\")\n"
                "EOF\n"
                "docker run --rm --network none --cap-add NET_ADMIN --cap-add NET_RAW \\\n"
                "  -v \"$PWD/data/nft-check:/w:ro\" nicolaka/netshoot:v0.15 sh -c '\n"
                "  nft -c -f /w/maxguard-setup.nft && echo \"syntax check: ok\"\n"
                "  nft -f /w/maxguard-setup.nft && nft -f /w/maxguard-setup.nft\n"
                "  echo \"drop rules in input after loading twice: $(nft list chain inet maxguard input | grep -c drop)\"\n"
                "  bash -e /w/run.sh'"),
             "note": ("`nicolaka/netshoot` is for testing only, never shipped "
                      "(`docs/DEPENDENCIES.md`). Not checked here: the older iptables-legacy "
                      "backend, and a real router forwarding traffic (the `forward` chain loads, "
                      "but no routed packets went through it).")},
            {"id": "tests", "show": ("pytest tests/unit/test_response_generate.py "
                                     "tests/unit/test_response_preview.py -q")},
        ],
        "test": "The tests pass, and the nftables commands pass `nft -c`.",
        "why": (
            "Blocking the wrong address can cut off a printer, a phone, or the whole office. "
            "Showing exactly what would have been blocked last week, and the undo command before "
            "the block, is how MaxGuard keeps blocking safe and reversible (CLAUDE.md rule 4)."
        ),
        "checklist": checklist(extra=["A hostile input test exists"]),
    },
    {
        "id": "AHM-08", "owner": "ahmad", "milestone": "S8",
        "title": "Response: approvals, audit, revert, and the OPNsense connector",
        "labels": ["area:response"], "hardware": True,
        "depends": ["AHM-07", "JON-03"],
        "goal": (
            "Add the approval workflow (propose → preview → approve with the IP typed again → "
            "applied → reverted, every step audited) and the first `Enforcer`, which applies an "
            "approved block on an OPNsense firewall through its API."
        ),
        "prereq": ("AHM-07 is merged. For the last step you need an OPNsense test firewall in a "
                   "VM, never a real one."),
        "steps": [
            start_step("ahmad/response-approvals"),
            "Create `maxguard/response/approvals.py`:\n\n"
            "@@FILE maxguard/response/approvals.py@@\n\n"
            "The steps are `proposed → previewed → approved → applied → reverted`, and a "
            "proposed or previewed block can be `rejected`. Approve is allowed only after a "
            "preview, needs the person's name and the IP address typed again, and a refused "
            "approval is audited too. Each check and state change is **one** SQL `UPDATE ... "
            "WHERE state IN (...)`, so two people clicking at the same moment cannot both "
            "approve. The proposals table is created here with `CREATE TABLE IF NOT EXISTS`, so "
            "`storage/state.py` does not change. Each state change and its audit row are "
            "written in **one** transaction (`insert_audit(conn, ...)` from `storage/state.py`), "
            "so a crash can never leave a block without its record; the last test proves it by "
            "making the audit write fail.",
            "Create the enforcer interface `maxguard/response/enforcers/__init__.py` and "
            "`maxguard/response/enforcers/base.py`:\n\n"
            "@@FILE maxguard/response/enforcers/__init__.py@@\n\n"
            "@@FILE maxguard/response/enforcers/base.py@@\n\n"
            "and the OPNsense client `maxguard/response/enforcers/opnsense.py`:\n\n"
            "@@FILE maxguard/response/enforcers/opnsense.py@@\n\n"
            "The endpoints come from OPNsense's own source code (`opnsense/core`, commit "
            "`1177021c22d6dedb63ff9bffd6300e789a8822e2`, October 6, 2026): `POST "
            "/api/firewall/alias_util/add/<alias>` and `.../delete/<alias>` with "
            "`{\"address\": ip}` (`AliasUtilController.php`; they change the live `pf` table at "
            "once through `pfctl -t <alias> -T add`) and `POST /api/firewall/alias/reconfigure` "
            "(`AliasController.php`, the \"Apply\" step). The key file has `key=` and `secret=` "
            "lines and is sent with HTTP basic auth (OPNsense's API how-to, `api.rst`). The "
            "client accepts only `https://`, always verifies the certificate (your CA file or "
            "the system's), uses short timeouts, follows no redirects, and ignores proxy "
            "settings (`trust_env = False`): the request goes straight to your firewall, and "
            "never toward the blocked address.",
            "Create `maxguard/response/routes.py`, the API under `/api/response`:\n\n"
            "@@FILE maxguard/response/routes.py@@\n\n"
            "`create_app()` (JAI-07) includes this router automatically now that the module "
            "exists. It is part of the dashboard's app on `127.0.0.1` only, never the "
            "ingest-only app that sensors reach. Errors: 400 bad input or a wrong typed IP, 404 "
            "no such proposal, 409 a step that is not allowed now, 502 the firewall refused or "
            "could not be reached.",
            "Create the tests `tests/unit/test_response_approvals.py`:\n\n"
            "@@FILE tests/unit/test_response_approvals.py@@\n\n"
            "`tests/unit/test_opnsense.py` (a fake OPNsense: `http.server` on `127.0.0.1` "
            "wrapped in TLS with a throwaway test CA, so the tests also prove that an untrusted "
            "certificate is refused):\n\n@@FILE tests/unit/test_opnsense.py@@\n\n"
            "and `tests/unit/test_response_routes.py`:\n\n"
            "@@FILE tests/unit/test_response_routes.py@@\n\nRun them:\n\n@@RUN tests@@",
            "Walk through the whole workflow against the API. Start the server in one terminal, "
            "then run the rest in a second one:\n\n@@RUN session@@",
            "**On an OPNsense test VM** (*not run — verify on hardware*; never a real "
            "firewall):\n\n"
            "1. **Firewall > Aliases**: create `maxguard_block_in` and `maxguard_block_out`, "
            "type *Host(s)*, empty.\n"
            "2. **Firewall > Rules > WAN**: a *Block* rule with source `maxguard_block_in`. "
            "**Firewall > Rules > LAN**: a *Block* rule with source `maxguard_block_in` (a "
            "device on your own network) and one with destination `maxguard_block_out`. Apply.\n"
            "3. **System > Access > Users**: a user `maxguard` with only the privileges "
            "*Diagnostics: PF Table IP addresses* and *Firewall: Alias: Edit* (OPNsense's "
            "`ACL.xml`). In its API keys section click **+**; the browser downloads the key "
            "file once.\n"
            "4. On the MaxGuard machine, keep the key in the data folder (never in the "
            "repository) and point MaxGuard at the firewall:\n\n"
            "```bash\n"
            "mkdir -p data/opnsense\n"
            "mv ~/Downloads/<the downloaded key file>.txt data/opnsense/apikey.txt\n"
            "chmod 600 data/opnsense/apikey.txt\n"
            "export MAXGUARD_OPNSENSE_URL=https://fw.home.arpa      # your test firewall\n"
            "export MAXGUARD_OPNSENSE_CA=$PWD/data/opnsense/ca.pem  # if it uses its own CA\n"
            "export MAXGUARD_OFFLINE_ALLOW=fw.home.arpa             # with MAXGUARD_OFFLINE=1\n"
            "```\n\n"
            "5. Repeat the walk-through: `apply` now adds the address to the alias (check "
            "**Firewall > Diagnostics > Aliases**), and `revert` removes it. Without "
            "`MAXGUARD_OFFLINE_ALLOW`, apply answers 502 with the hint to add the firewall "
            "there.",
            pr_step("feat: approvals, audit and OPNsense enforcer (AHM-08)", "JWinborne1"),
        ],
        "files": ["maxguard/response/approvals.py", "maxguard/response/enforcers/__init__.py",
                  "maxguard/response/enforcers/base.py", "maxguard/response/enforcers/opnsense.py",
                  "maxguard/response/routes.py", "tests/unit/test_response_approvals.py",
                  "tests/unit/test_opnsense.py", "tests/unit/test_response_routes.py"],
        "commands": [
            {"id": "tests", "show": ("pytest tests/unit/test_response_approvals.py "
                                     "tests/unit/test_opnsense.py tests/unit/test_response_routes.py -q")},
            {"id": "session", "show": '# terminal 1:\nuvicorn maxguard.api.app:create_app --factory --host 127.0.0.1 --port 8000\n# terminal 2:\npython -c "import shutil; shutil.make_archive(\'data/telnet\', \'zip\', \'tests/fixtures/zeek/telnet\')"\ncurl -s -F file=@data/telnet.zip http://127.0.0.1:8000/api/analyses; echo\npython - <<\'EOF\'\nimport requests\n\nB = "http://127.0.0.1:8000/api/response/proposals"\n\n\ndef step(path, **body):\n    """POST one step and print the answer in one line."""\n    answer = requests.post(B + path, json=body, timeout=60)\n    data = answer.json()\n    print(answer.status_code, data.get("detail") or f"proposal {data[\'proposal_id\']}: {data[\'state\']}")\n    return data\n\n\nstep("", actor="ahmad", ip="1.2.3.4; rm -rf /", direction="both")\np = step("", actor="ahmad", ip="172.18.0.3", direction="both", reason="Telnet client")\nprint("\\n".join(p["rules"]["nftables"]["block"] + p["rules"]["nftables"]["undo"]))\nseen = step("/1/preview", actor="ahmad")["preview"]\nprint("preview:", seen["connections"], "connection(s), devices", seen["devices"],\n      "ports", [s["port"] for s in seen["services"]])\nstep("/1/approve", actor="fiona")                          # the IP was not typed again\nstep("/1/approve", actor="fiona", confirm_ip="172.18.0.3")\nstep("/1/apply", actor="fiona")                            # no firewall connector: by hand\nstep("/1/revert", actor="ahmad")\nfor row in reversed(requests.get("http://127.0.0.1:8000/api/audit", timeout=10).json()):\n    print(row["actor"], row["action"], row["target"])\nEOF', "run": '(uvicorn maxguard.api.app:create_app --factory --host 127.0.0.1 --port 18000 > /tmp/ahm08-uvicorn.log 2>&1 & echo $! > /tmp/ahm08-uvicorn.pid)\nfor i in $(seq 1 50); do curl -s -o /dev/null http://127.0.0.1:18000/docs && break; sleep 0.2; done\npython -c "import shutil; shutil.make_archive(\'data/telnet\', \'zip\', \'tests/fixtures/zeek/telnet\')"\ncurl -s -F file=@data/telnet.zip http://127.0.0.1:18000/api/analyses; echo\npython - <<\'EOF\'\nimport requests\n\nB = "http://127.0.0.1:18000/api/response/proposals"\n\n\ndef step(path, **body):\n    """POST one step and print the answer in one line."""\n    answer = requests.post(B + path, json=body, timeout=60)\n    data = answer.json()\n    print(answer.status_code, data.get("detail") or f"proposal {data[\'proposal_id\']}: {data[\'state\']}")\n    return data\n\n\nstep("", actor="ahmad", ip="1.2.3.4; rm -rf /", direction="both")\np = step("", actor="ahmad", ip="172.18.0.3", direction="both", reason="Telnet client")\nprint("\\n".join(p["rules"]["nftables"]["block"] + p["rules"]["nftables"]["undo"]))\nseen = step("/1/preview", actor="ahmad")["preview"]\nprint("preview:", seen["connections"], "connection(s), devices", seen["devices"],\n      "ports", [s["port"] for s in seen["services"]])\nstep("/1/approve", actor="fiona")                          # the IP was not typed again\nstep("/1/approve", actor="fiona", confirm_ip="172.18.0.3")\nstep("/1/apply", actor="fiona")                            # no firewall connector: by hand\nstep("/1/revert", actor="ahmad")\nfor row in reversed(requests.get("http://127.0.0.1:18000/api/audit", timeout=10).json()):\n    print(row["actor"], row["action"], row["target"])\nEOF\nkill $(cat /tmp/ahm08-uvicorn.pid)',
             "note": ("The analysis ID depends on the moment of the upload, so yours differs. "
                      "The preview counts only the 7 days before now: the fixture's traffic is "
                      "from October 6, 2026, so on a later date your preview shows 0 "
                      "connections. `apply` records a block made by hand because no firewall "
                      "connector is configured.")},
        ],
        "test": "The tests pass, and on a test OPNsense VM an approved block and its revert work.",
        "why": (
            "Typing the address again is a deliberate speed bump: it makes the person read what "
            "they are about to block. The audit trail and revert make every block accountable "
            "and reversible, and testing against a fake server means no test can ever change a "
            "real firewall."
        ),
        "checklist": checklist(extra=["No test talks to a real firewall",
                                      "The API key is read from the data folder"]),
    },
    {
        "id": "AHM-09", "owner": "ahmad", "milestone": "S14",
        "title": "v2.0 acceptance test",
        "labels": ["area:program", "critical-path"], "status": "process",
        "depends": ["JAI-12"],
        "goal": (
            "Run the `v2.0` acceptance test: the alpha test plus the live sensor on the reference "
            "lab, a blocked IP with preview and approval, a verified intel bundle, and the "
            "chain-of-custody check."
        ),
        "prereq": "JAI-12 has tagged `v2.0`.",
        "steps": [
            "Follow the v2.0 acceptance test in `docs/roadmap/README.md` with someone who did not "
            "build the release, and record each result.",
        ],
        "files": [], "commands": [],
        "test": "Every step passes or has an issue.",
        "why": "The same rule as the alpha: done means someone else can use it.",
        "checklist": ["Acceptance results recorded"],
    },
]
