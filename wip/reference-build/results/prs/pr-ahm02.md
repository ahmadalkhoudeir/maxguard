## What and why

The first dashboard pages (AHM-02): the base layout with the privacy note and the Analyst/Home switch, the alert queue with filters and live refresh, and the upload page. The files are the ones in `docs/roadmap/ahmad.md`, and this pull request also updates that guide: a browser review of the pages found ten problems (sideways scrolling on phones, keyboard focus thrown to the top of the page on every refresh, six open queue tabs freezing the browser, a log line with an impossible time crashing the queue, a stale form undoing a teammate's change, and others), and the code and the guide's AHM-02, AHM-03 and AHM-06 sections now carry the fixes together, so nobody copies the old version.

**Draft: blocked by JAI-07** (`create_app()` and the API this router plugs into are not on `main` yet). It becomes ready for review when JAI-07 merges.

Closes #<the AHM-02 issue, once `scripts/create_issues.sh` has run>
Task: AHM-02

## How I tested it

`main` has no `maxguard` package yet, so the tests ran on a full build of the roadmap up to AHM-02 (every earlier task's files, in roadmap order, exactly as the guides give them) with these files on top. The same commands run on this branch once JAI-07 is merged.

```text
$ sha256sum maxguard/web/static/htmx-2.0.11.min.js
d6fdc75f204e6bdefa99b69bf1e6d4ac69b8a364f77929f45c13476b4000f717  maxguard/web/static/htmx-2.0.11.min.js
$ ruff check .
All checks passed!
$ pytest tests/unit/test_web.py -q
..................                                                                           [100%]
18 passed in 1.48s
$ curl -s -D - -o /dev/null http://127.0.0.1:8000/ | grep -i -E '^(content-security-policy|referrer-policy|x-content-type-options):'
content-security-policy: default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self'; connect-src 'self'; form-action 'self'; base-uri 'none'; object-src 'none'; frame-ancestors 'none'
x-content-type-options: nosniff
referrer-policy: same-origin
```

Browser checks (Chromium, four fonts, 320 to 1280 px): no sideways scrolling on any page; every control reachable with Tab; focus stays put through a live refresh; eight queue tabs share one event stream and a ninth tab still loads; nothing is requested from outside the app; axe reports no accessibility violations.

## Checklist

- [x] The title has the form `type: summary (TASK-ID)` (see `docs/CONTRIBUTING.md`)
- [x] `ruff check .` and `pytest -m "not integration" -q` pass (on the reference build; see above)
- [ ] New rules have a positive and a negative test (no rules in this change)
- [x] No secrets, personal data, email addresses, or captures from a real network (CLAUDE.md rule 6)
- [x] Nothing new contacts an external service at runtime (rule 1)
- [x] Every new dependency has a row in `docs/DEPENDENCIES.md` (htmx 2.0.11 already has one; the file's SHA-256 matches)
- [ ] A contract change is labeled `contract-change` (none)
- [x] If a roadmap step was wrong, I fixed it in `docs/roadmap/`

## Notes for the reviewer

Start with `maxguard/web/routes.py` (`render()` adds the security headers to every page) and `app.js` (one shared event stream for all open queue tabs, with the browser's Web Locks API). The templates never use `|safe`: titles, addresses and names come from traffic. The guide change is large because it is regenerated as one file; the AHM-02, AHM-03 and AHM-06 code blocks are the only parts that changed.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01MBhgGwdEFhiZhjwCZ9BRy1
