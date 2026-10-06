## What and why

<!-- One or two sentences: what this pull request changes and why. -->

Closes #<!-- issue number -->
Task: <!-- the task ID, for example FIO-01 -->

## How I tested it

<!-- Paste the exact commands you ran and their real output: ruff, pytest, and the
     task's own commands. Remove anything from a real network first. -->

```text

```

## Checklist

- [ ] The title has the form `type: summary (TASK-ID)` (see `docs/CONTRIBUTING.md`)
- [ ] `ruff check .` and `pytest -m "not integration" -q` pass
- [ ] New rules have a positive and a negative test
- [ ] No secrets, personal data, email addresses, or captures from a real network (CLAUDE.md rule 6)
- [ ] Nothing new contacts an external service at runtime (rule 1)
- [ ] Every new dependency has a row in `docs/DEPENDENCIES.md`
- [ ] A contract change is labeled `contract-change` (Jaiden reviews, Ahmad approves)
- [ ] If a roadmap step was wrong, I fixed it in `docs/roadmap/`

## Notes for the reviewer

<!-- What to look at first, and anything you are unsure about. -->
