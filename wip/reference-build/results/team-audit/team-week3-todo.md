# What each person must do to reach Week 3 (checked October 27, 2026)

How this was checked: every teammate branch on GitHub was exported and compared file by file
with the code in that person's guide, then `ruff` and `pytest` were run on it. Every guide's
own commands were re-run today on a clean build; all of them still give the guide's output.

## Where we are

- Nothing has merged to `main` since October 14 except planning docs. There are no open
  pull requests.
- Week 0 is finished only for Ahmad. Fiona's row is in, but her header pull request is
  missing. Jaiden's row was pushed straight to `main` and is wrong. Jakub, Jonattan, Ali,
  Amory and Karthik have no row.
- Only two people have pushed code: Jaiden (five commits, mostly empty files) and Karthik
  (one commit, 13 of 14 captures empty).
- The roadmap needs 11 review-and-merge rounds to reach AHM-02 (the W3 dashboard). At one
  round per working day, AHM-02 lands Tuesday, November 10, not Friday, October 30.

## The order things must merge in

```
R1  JAI-01, KAR-01, ALI-01, and the TEAM.md rows (Jaiden's fix and Fiona's header first)
R2  JAI-02, JAK-01, JAK-02
R3  KAR-02, JON-01
R4  FIO-01
R5  FIO-02
R6  JAK-03
R7  JAI-03, JAK-04, AMO-01
R8  FIO-03 (before ALI-02), JAI-04, JAI-05, JAI-06, JON-02, ALI-02
R9  JON-03, FIO-04, KAR-03, ALI-03
R10 JAI-07, KAR-04, AMO-02
R11 AHM-02
```

Zero-slack path: JAI-01 + KAR-01 → JAK-01 + JAK-02 → KAR-02 → FIO-01 → FIO-02 → JAK-03 →
JAI-03 → JON-02 → JON-03 → JAI-07 → AHM-02. A day lost anywhere on it is a day lost at the end.

A realistic target for Friday, October 30: every Week 0 row merged; JAI-01, JAI-02, KAR-01
and ALI-01 merged; every other W1–W3 task open as a draft pull request with its code in
place; JAK-01 and JAK-02 merged within hours of JAI-01 and KAR-01.

## Everyone, before anything else

1. GitHub → Settings → Emails: tick **Keep my email addresses private**, copy the
   `...@users.noreply.github.com` address, and run
   `git config --global user.email "<that address>"`. Six of eight people are committing
   with a school, Gmail or laptop-hostname address (CLAUDE.md rule 6). Jaiden's and Ahmad's
   school addresses are already in `main`'s history; stopping new ones is the fix.
2. Your TEAM.md row pull request (guide section 0.9). Jaiden's fix and Fiona's header merge
   first; the other five merge one at a time, each after a `git merge main` (section 0.9
   has the conflict steps).
3. Reply to the pinned "Week 0 check-in" in Discussions.
4. Prepare every task you are blocked on as a **draft** pull request now: branch from
   `main`, paste the guide's files exactly, push, `gh pr create --draft`. When the task it
   needs merges, `git merge main`, run the guide's test step, and mark it ready. All the
   guide code was re-run today and passes; what costs time is the review queue, not the
   typing.

## Jaiden (critical path; Ahmad reviews)

Status: JAI-01 exists on a branch literally named `maxguard/__init__.py`, with `ci.yml` and
`test_package.py` as 0-byte files, two edited files and no final newlines. JAI-02 (the three
contracts) exists nowhere, yet his later branches import it. JAI-03's `normalize.py` is in a
doubled folder (`maxguard/maxguard/events/`) with a relative import; every other JAI-03,
JAI-04, JAI-05 and JAI-06 file is 0 bytes. All four branches are stacked and 12 commits
behind `main`.

This week, in this order:

1. Email privacy and `user.email` (above). In VS Code, turn on **Insert Final Newline**.
2. **JAI-01** (target: Wednesday). Keep a backup, rebuild the guide's branch from today's
   `main`, repair the six files, test, push, open the pull request:
   ```bash
   cd ~/projects/maxguard && git status            # must be clean
   git fetch origin --prune && git branch --no-track backup/jaiden-storage origin/jaiden/storage
   git switch -C jaiden/restructure origin/main && git cherry-pick 2e33504
   git checkout cee8da0 -- .github/workflows/ci.yml tests/unit/test_package.py
   printf '%s\n' '"""MaxGuard command line interface (`maxguard` / `python -m cli.main`)."""' > cli/__init__.py
   perl -0pi -e 's/from importlib import import_module\n//; s/^pytest = import_module\("pytest"\)$/import pytest/m' tests/conftest.py
   for f in maxguard/__init__.py pyproject.toml tests/conftest.py tests/unit/test_package.py .github/workflows/ci.yml; do printf '\n' >> "$f"; done
   python3.11 -m venv .venv && source .venv/bin/activate && pip install --upgrade pip && pip install -e ".[dev]"
   ruff check .                      # All checks passed!
   pytest -m "not integration" -q    # 1 passed
   git add -A && git commit --amend --reset-author -m "chore: restructure repo, add pyproject and CI (JAI-01)"
   git push -u origin jaiden/restructure
   ```
   Pull request title `chore: restructure repo, add pyproject and CI (JAI-01)`, reviewer
   Ahmad. After the merge, delete the odd branch:
   `git push origin --delete maxguard/__init__.py`.
3. **JAI-02** (target: Wednesday, right after JAI-01 merges): branch `jaiden/contracts-v2`,
   paste guide steps 2–7, `pytest tests/unit/test_contracts.py -q` → `13 passed`,
   `pytest -m "not integration" -q` → `14 passed`. Label `contract-change`; Ahmad approves.
4. **TEAM.md fix** (can go up while JAI-01 is in review): branch `jaiden/week0-team-row`,
   replace his line with
   `| Jaiden Winborne | Co-lead; Architecture and Release Lead | JWinborne1 | Architecture, API, storage, releases |`
   (the current line has three cells and says `JWinborne12`).
5. **JAI-03, JAI-06, JAI-04, JAI-05, JAI-07**: start each only when its "Needs first" tasks
   are merged, from a fresh `main`. Recover `normalize.py` from the backup branch into
   `maxguard/events/` with `from maxguard.ids import ...`; everything else is pasted from the
   guide (the files on his branches are empty). JAI-06 needs only JAI-03. JAI-07's guide
   section changed after his October 12 base, so use the guide as it is on `main`.
6. While waiting on others: **JAI-08** (needs only JAI-01).

## Karthik (Jaiden reviews)

Status: no TEAM.md row. KAR-01's branch is missing 14 of its 35 files (13 scenario scripts
and `SOURCES.md`), and 13 of the 14 captures are 24-byte files with no packets. Root cause,
reproduced in Docker: the client container could not find `/scenarios/ftp.py`, exited with
code 2, and `--abort-on-container-exit` stopped `tcpdump` before it recorded anything. His
`telnet.pcap` is a real but different recording, and committing re-recorded captures breaks
nine later unit tests that hard-code values from the reference captures.

This week, in this order (target: KAR-01 merged by Wednesday, it blocks 23 W1–W3 tasks):

1. `user.email` to the noreply address; TEAM.md row pull request
   (`| Karthik Nair | Test and CI Engineer | Karthiknair91 | Testing |`, reviewer Jaiden).
2. **KAR-01**: take the reference lab files and captures, which exist only on the
   save-point branch, then prove the lab works, then commit once:
   ```bash
   cd ~/projects/maxguard && git fetch origin && git checkout karthik/traffic-lab && git pull
   git archive origin/claude/happy-newton-h26wx7 wip/reference-build/ref/lab wip/reference-build/ref/tests/pcaps | tar -x -f - --strip-components=3
   git show origin/claude/happy-newton-h26wx7:wip/reference-build/docgen/snippets/pcaps_SOURCES.md > tests/pcaps/SOURCES.md
   shasum -a 256 tests/pcaps/*.pcap | cut -c1-16      # each value is in SOURCES.md (telnet deb2874b1e5c2b87)
   cd lab && docker compose build && cd ..            # then the guide's Step 6 loop
   find lab/captures -name '*.pcap' -size -100c        # must print nothing
   # do NOT run Step 7's "cp lab/captures/*.pcap tests/pcaps/": keep the reference captures
   git add lab tests/pcaps && git status              # nothing from lab/captures/
   git reset --soft $(git merge-base HEAD origin/main) && git commit -m "test: traffic lab and the 14 synthetic test captures (KAR-01)"
   git log -1 --format='%an <%ae>'                     # the noreply address
   git push --force-with-lease
   ```
   Pull request title `test: traffic lab and the 14 synthetic test captures (KAR-01)`,
   reviewer Jaiden. Say in the body that `ruff` and `pytest` cannot run on `main` until
   JAI-01 is merged.
3. **KAR-02** after KAR-01, JAI-01, JAK-01 and JAK-02 merge (`14 passed`, 14 × `identical`).
   **KAR-03** after KAR-02, JAI-04 and JAI-05 (`57 passed`; `15 passed, 340 deselected` in
   the engine image). **KAR-04** after KAR-03.

## Fiona (Jaiden reviews; she reviews Jakub)

Status: her row is in `main`, but the header pull request her guide asks for is missing, and
her commits use a Gmail address. No FIO branch exists. FIO-01 and FIO-02 have zero slack.

1. `user.email`; branch `fiona/week0-team-header`; add `| Name | Role | GitHub | Module |`
   and `|---|---|---|---|` at the top of `docs/TEAM.md`; pull request to Jaiden. This and
   Jaiden's fix merge before the other rows.
2. Draft pull requests today for **FIO-01** (`fiona/zeek-runner-adapters`), **FIO-02**
   (`fiona/tls-cert-rules`), **FIO-03** (`fiona/attack-mapping`) and **FIO-04**
   (`fiona/cli`), each with the guide's files pasted exactly.
3. When the prerequisites merge: FIO-01 → `16 passed`; FIO-02 → `60 passed` (expect an
   add/add conflict on `maxguard/rules/__init__.py` after `git merge main`: keep yours with
   `git checkout --ours maxguard/rules/__init__.py`); FIO-03 → `36 passed, 1 skipped`;
   FIO-04 → `9 passed`. FIO-03 must merge before Ali's ALI-02 and ALI-03 (a hidden
   dependency the roadmap does not list).
4. Review Jakub's pull requests the same day they go up: JAK-01, JAK-02 and JAK-03 are on
   the zero-slack path.

## Jakub (Fiona reviews)

Status: nothing on GitHub, no row. JAK-01 and JAK-02 are round 2 of the zero-slack path and
need only Docker, not Python.

1. `user.email`; row `| Jakub Kania | Protocol Coverage Engineer | SXafir-byte | Sensor |`,
   reviewer Fiona.
2. Draft pull requests today for **JAK-01** (`jakub/zeek-scripts`) and **JAK-02**
   (`jakub/suricata-config`). The moment JAI-01 and KAR-01 merge, `git merge main`, run
   the Docker steps (JAK-01 steps 5–7, JAK-02 steps 4–5), paste the output, mark ready,
   and ask Fiona for a same-day review. The guide's exact values appear only with the
   reference captures.
3. Drafts for **JAK-03** (`jakub/cleartext-rules`, `47 passed`; same `rules/__init__.py`
   conflict as Fiona, keep yours) and **JAK-04** (`jakub/inventory`, `24 passed`).

## Jonattan (Jaiden reviews; he reviews Ali)

Status: nothing on GitHub, no row. JON-02 and JON-03 are on the zero-slack path (JAI-07
needs JON-03).

1. `user.email`; row `| Jonattan Escalante | Offline AI Engineer | MeliorExi | AI |`,
   reviewer Jaiden.
2. Drafts for **JON-01** (`jonattan/citations`, needs JAI-02, `8 passed`), **JON-02**
   (`jonattan/ollama-client`, `14 passed`) and **JON-03** (`jonattan/offline-guard`,
   `13 passed`). Do not hold JON-02 for its step 5 (the real model run): that step needs
   FIO-04 and can go in as a comment afterwards.
3. Review Ali's Week 0 and ALI-01 pull requests promptly.

## Ali (Jonattan reviews)

Status: nothing on GitHub, no row. ALI-01 has no prerequisites and can merge this week.

1. `user.email`; row `| Ali Al-Kheder | AI Model Evaluation Engineer | al-kheder | AI evaluation |`,
   reviewer Jonattan.
2. **ALI-01** today: `docs/model-eval/README.md` from the guide, check every license at its
   primary source, add the "Checked on" column, post the shortlist in Discussions → Ideas,
   open the pull request to Jonattan. Docs only, so say in the body that `ruff` and the
   tests work after JAI-01.
3. Drafts for **ALI-02** (`ali/eval-set`) and **ALI-03** (`ali/benchmark`). Both need
   FIO-03 as well as the listed tasks: generate the eval set only after FIO-03 is merged,
   or the committed file differs.

## Amory (Ahmad reviews)

Status: the branch `amory/week0-team-row` exists but has no commits beyond `main`, so the
row was never committed or pushed. No AMO branch.

1. `user.email`; on that branch add
   `| Amory B. | Compliance Mapping Analyst | gettalife | Mapping and reports |`, commit,
   push, pull request to Ahmad.
2. **AMO-02** reading can start today: download PCI DSS v4.0.1 (keep the PDF outside the
   repository) and write the rows for `cleartext.telnet` first, with requirement number,
   exact title and page, in a file outside the repository.
3. Draft for **AMO-01** (`amory/nist-mapping`, `30 passed`). After it merges, paste the
   PCI rows in; AMO-02's step 5 check needs FIO-04 (not listed in the roadmap).

## Ahmad

- Reviews that only you can do: every JAI-* and AMO-* pull request, sign-off on the rules
  (FIO-02, JAK-03) and mapping files (AMO-01, FIO-03), and the `contract-change` approval
  on JAI-02. JAI-01 and JAI-02 unblock everyone: review them the day they open.
- AHM-01 leftovers: `ASSIGN=1 bash scripts/create_issues.sh` (labels, milestones, 69
  issues, board), squash-only merges with automatic branch deletion, and the
  `main-protection` ruleset right after JAI-01 merges.
- Roadmap fixes to make (small, docs only): KAR-01 step 7 must say "commit the reference
  captures" and step 6 needs the empty-capture guard; add FIO-03 to ALI-03's "Needs first"
  and FIO-04 to AMO-02's; give JON-03 the `critical-path` label.
- Decision: the reference captures live only on the save-point branch. Either keep that
  branch until KAR-01 merges, or publish them somewhere stable first.
