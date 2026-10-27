## What and why

The alert detail page (AHM-03). Analyst mode shows the evidence records, the controls grouped by framework with its version, the ATT&CK techniques, the AI's sentences each followed by links to the records it cites, and the status and assignee form. Home mode shows the headline, the severity in plain words and one action, with no jargon, even in the page title. Status changes land in the audit trail.

**Draft, stacked on the AHM-02 pull request: blocked by AHM-02, JON-02 (the AI sentences) and JON-04 (the Home text).**

Closes #<the AHM-03 issue, once `scripts/create_issues.sh` has run>
Task: AHM-03

## How I tested it

On a full build of the roadmap up to AHM-03 (every earlier task's files, in roadmap order) with these files on top:

```text
$ ruff check .
All checks passed!
$ pytest tests/unit/test_web.py -q
.......................................                                                      [100%]
39 passed in 2.87s
```

Browser checks (Chromium): status and assignee changed with the keyboard only, and focus stays on Save; a form opened before a teammate's change saves only the field the person changed; with the server stopped the form says the change may not be saved; a fake local Ollama whose sentence cites a record outside the finding has that sentence dropped (CLAUDE.md rule 3); hostile text in a title, a detail, an AI sentence or a name is shown as text; the Home view reads without jargon at 320 px.

## Checklist

- [x] The title has the form `type: summary (TASK-ID)` (see `docs/CONTRIBUTING.md`)
- [x] `ruff check .` and `pytest -m "not integration" -q` pass (on the reference build; see above)
- [ ] New rules have a positive and a negative test (no rules in this change)
- [x] No secrets, personal data, email addresses, or captures from a real network (CLAUDE.md rule 6)
- [x] Nothing new contacts an external service at runtime (rule 1)
- [x] Every new dependency has a row in `docs/DEPENDENCIES.md` (none added)
- [ ] A contract change is labeled `contract-change` (none)
- [x] If a roadmap step was wrong, I fixed it in `docs/roadmap/` (in the AHM-02 pull request)

## Notes for the reviewer

`change_status()` in `routes.py` checks the person's name before anything is saved and saves only the fields the form changed (`shown_status`, `shown_assignee`). No `|safe` anywhere: AI text and anything from traffic is escaped.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01MBhgGwdEFhiZhjwCZ9BRy1
