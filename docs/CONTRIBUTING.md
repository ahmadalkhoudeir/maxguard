# Contributing to MaxGuard

This page says how code gets from your laptop into `main`: branch names, commit
messages, pull requests, and reviews. It applies to everyone, including the
leads. If something here disagrees with `CLAUDE.md` or
`docs/PROJECT_DECISIONS.md`, those files win; tell Jaiden so this page can be fixed.

New to Git or GitHub? Do **Week 0** at the top of your file in `docs/roadmap/`
first: it walks through every command on this page once.

## The rules that are never broken

From `CLAUDE.md` (read the full list there):

1. **Offline at runtime.** No code that calls an external service.
2. **Deterministic detection.** Rules never read the clock, random numbers, or the network.
3. **The AI cites evidence** and never creates, hides, or re-rates an alert.
4. **Defensive only.** Blocking needs human approval, is reversible, and is logged.
5. **Sensors never transmit.**
6. **Public repository:** no secrets, API keys, passwords, personal data, email
   addresses, real captures from anyone's network, or details of anyone's home network.
7. **JA4 only** from the JA4+ family; every new dependency is recorded in `docs/DEPENDENCIES.md`.
8. **Exact control IDs and framework versions** in every compliance mapping.

A pull request that breaks one of these is not merged, however good the rest is.

## The workflow, start to finish

```text
issue (e.g. FIO-01) → branch → small commits → push → pull request → review + CI → squash and merge
```

1. **Pick up your issue** on the project board (the issues are created from
   `docs/roadmap/` by `scripts/create_issues.sh`). Assign yourself and move it to
   *In progress*.
2. **Branch from an up-to-date `main`:**

   ```bash
   git checkout main && git pull
   git checkout -b fiona/zeek-runner
   ```

3. **Commit in small steps** (see "Commit messages").
4. **Before you push, run the same checks CI runs:**

   ```bash
   ruff check .
   pytest -m "not integration" -q
   ```

   Both must pass. Integration tests need Zeek, so they run inside the engine
   image; CI runs them for you on every pull request (see `docs/roadmap/karthik.md`
   to run them yourself).
5. **Push and open a pull request** (`gh pr create` or the link Git prints).
   Fill in the template, link the issue with `Closes #<number>`, and request
   your reviewer.
6. **Address review comments** with new commits on the same branch. Do not
   force-push a branch someone is reviewing.
7. **Merge** with **Squash and merge** once it is approved and CI is green, then
   delete the branch.

## Branch names

`<yourname>/<short-task>`, all lower case, words joined with hyphens.

| Good | Why it is good |
|---|---|
| `fiona/zeek-runner` | owner and task are obvious |
| `jakub/cleartext-rules` | |
| `amory/pci-telnet-rows` | |
| `karthik/fix-tls-expected-results` | a bug fix says what it fixes |

| Avoid | Problem |
|---|---|
| `patch-1`, `test`, `my-branch` | nobody can tell what it is |
| `Fiona/ZeekRunner` | capital letters break on some systems |
| reusing an old branch for a new task | one branch = one task = one pull request |

## Commit messages

Use a short type, a colon, and a summary in the imperative mood ("add", not
"added"), at most 72 characters. This follows the
[Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) style.

```text
feat: add Zeek runner with deterministic seeds
fix: ignore case when checking for STARTTLS in cleartext.zeek
docs: explain the TSV import in ARCHITECTURE.md
test: add negative case for cleartext.imap
```

| Type | Use it for |
|---|---|
| `feat` | new behavior a user or another module can use |
| `fix` | a bug fix |
| `docs` | documentation only |
| `test` | tests or test data only |
| `refactor` | code change that does not change behavior |
| `ci` | GitHub Actions and other automation |
| `chore` | everything else (dependencies, tooling) |

If the change needs explaining, leave a blank line after the summary and write
*why* in the body. Because pull requests are squash-merged, the **pull request
title** becomes the one commit on `main`, so give it the same form and add the
task ID: `feat: Zeek runner and adapters (FIO-01)`.

## Pull requests

- **One task per pull request.** Small pull requests get reviewed the same day;
  1,000-line ones wait a week. If a task is big, split it by feature (for
  example, TLS rules in one pull request and certificate rules in another).
  Tests always go in the same pull request as the code they test.
- **Fill in the template** (`.github/pull_request_template.md`): what changed,
  why, how you tested it (paste the real output), and the checklist.
- **Draft pull requests are welcome.** Open one early (`gh pr create --draft`) to
  get feedback; mark it *Ready for review* when it is.
- **Pull requests marked with `contract-change`** (any change to
  `maxguard/models.py`, `maxguard/adapters/base.py`, the mapping schema, the
  report schema, or the event schema) need Jaiden's review **and** Ahmad's approval.
- **New dependencies:** explain why in the pull request and add a row to
  `docs/DEPENDENCIES.md` with the license. GPL-licensed Python libraries are not
  accepted, because importing them into our Apache-2.0 code would change what
  users may do with MaxGuard (separate programs such as Suricata are fine); ask
  first if unsure.

## Reviews

**What you need to merge:** one approving review and all CI checks green. The
`main` branch is protected so that this is enforced (Jaiden sets the ruleset in JAI-01).

**Who reviews:**

| Change | Reviewer |
|---|---|
| Most code | your help person from `docs/roadmap/README.md`, or the module owner |
| Detection rules and their severities | Fiona, and Ahmad signs off (Security Lead) |
| Mapping files (`mappings/*.yaml`) | Ahmad (compliance accuracy) |
| Contracts and schemas | Jaiden and Ahmad |
| Response module (blocking) | Ahmad and one more person |
| CI and release workflows | Jaiden |

**As a reviewer:**

1. Review within **two days** (critical-path pull requests within one day).
2. Pull the branch and run it if the change is not obvious:
   `gh pr checkout <number>`, then the commands from the pull request.
3. Check, in this order:
   - Does it do what the task asks? Do the tests prove it, including a negative case?
   - The never-broken rules above (secrets, captures, network calls, clock reads in rules).
   - Would a teammate understand it in six months? Clear names, small functions,
     comments that explain *why*.
4. Be specific and kind: suggest the change ("rename `x` to `record_count`"),
   explain why, and use GitHub's **suggestion** feature for small fixes.
5. Use **Request changes** only for things that must change before merging;
   use **Comment** for ideas. Approve when it is good enough, not perfect.

**As an author:** reply to every comment (a fix commit or a short answer), then
re-request review. Never resolve a reviewer's thread without answering it.

## Tests and test data

- Every code change comes with tests; every rule has a positive and a negative test.
- Unit tests live in `tests/unit/`, need no Docker or network, and run in seconds.
- Integration tests live in `tests/integration/`, are marked `@pytest.mark.integration`,
  and run inside the engine image (Zeek and Suricata).
- Captures in `tests/pcaps/` are **synthetic** (made by `lab/`) or publicly
  licensed. Each needs a line in `tests/pcaps/SOURCES.md`: no source line, no merge.
  Keep each capture under 1 MB.
- Never commit a capture from a real network, including your own home.

## If you commit a secret by mistake

1. Tell Ahmad immediately (Teams direct message, not a public channel).
2. Revoke or change the secret right away. Deleting the commit is not enough:
   the repository is public and copies may already exist.
3. Then remove it from the branch with a new commit and ask Jaiden whether the
   history needs cleaning.

## Reporting a security problem in MaxGuard

Do not open a public issue for a vulnerability. Use GitHub's **Security → Report a
vulnerability** (private reporting) or message Ahmad directly.

## When the roadmap is wrong

The steps in `docs/roadmap/` were written before the code existed, and some
could not be run during planning (they say so). If a step does not work as
written, fix the step in the same pull request as your code and say so in the
pull request description, or open an issue with the `type:docs` label. The next
person will hit the same problem.

## Questions

Ask in **GitHub Discussions** (category *Q&A*) with the exact command and output.
Microsoft Teams is for meetings and quick chat; anything others may need to find
again belongs in Discussions.
