export const meta = {
  name: 'team-w0-w3-audit',
  description: 'Audit every teammate branch against the roadmap and give each person exact steps to reach Week 3',
  phases: [{ title: 'Team audit', detail: 'Jaiden, Karthik, and everyone else' }],
}
const SP = '/tmp/claude-0/-home-user-maxguard/d28fe4b6-2c9f-5cd0-8e7f-d2be65aa4c01/scratchpad'
const CTX = `
Shared setup (read carefully):
- Scratchpad: ${SP}. Write ONLY inside ${SP}/agentwork/<your-label>/ (create it). Never write anywhere else.
- The MaxGuard roadmap guides are in /home/user/maxguard/docs/roadmap/*.md and the design in /home/user/maxguard/docs/ARCHITECTURE.md. Treat /home/user/maxguard as READ-ONLY: no checkout, commit, push, fetch, branch, or file edits there. Use only read-only git (git -C /home/user/maxguard log/show/ls-tree/diff/cat-file). To run a branch's code, export it: git -C /home/user/maxguard archive origin/<branch> | tar -x -C <your folder>.
- Full builds of the project as it looks right after a roadmap task already exist and are READ-ONLY: ${SP}/stages/AHM-02, ${SP}/stages/AHM-03, ${SP}/stages/AHM-04 (the alpha state) and ${SP}/stages/ALL (every task, including Spring 2027 features). If you need to run a server, write files, or change anything, build your own copy first: python3 ${SP}/docgen/build_stage.py <TASK_ID|ALL> <new empty folder> (for example ${SP}/agentwork/<label>/repo). Any task ID works (for example JAI-01, KAR-01). The list of tasks with their files, owners and dependencies is in ${SP}/docgen/taskplan.py (TASKS); simulate.py's source_of() maps each files entry to its source.
- Python: ${SP}/ref/.venv/bin (Python 3.11 with every dependency, ruff, pytest, uvicorn). Run tests from the build folder: ${SP}/ref/.venv/bin/python -m pytest -q -p no:cacheprovider ... (pyproject sets pythonpath=["."], so maxguard imports from the current folder). Set PYTHONDONTWRITEBYTECODE=1.
- Docker works and the image zeek/zeek:9.0.0 is pulled. To run MaxGuard inside it the way the roadmap simulation does: docker run --rm --network none -v <repo>:/src -v ${SP}/deps313:/deps:ro -e PYTHONPATH=/deps:/src -e PYTHONDONTWRITEBYTECODE=1 -w /src zeek/zeek:9.0.0 sh -c '<command>' (python3 is the interpreter there).
- Node with Playwright is available: require('playwright') works from any folder and chromium.launch() needs no options. Do not run "playwright install".
- Safety (CLAUDE.md rules 4-6): attack only processes you start yourself on 127.0.0.1 inside this container, with synthetic data. Never contact or scan any outside host. Never create real secrets in files you keep; generate throwaway tokens at runtime.
- Installed tools (approved by the project lead today; do not install, pull or download anything else): pip-audit 2.10.1, bandit 1.9.4 and actionlint 1.7.12 in ${SP}/tools/secvenv/bin; Docker images koalaman/shellcheck:v0.11.0, zricethezav/gitleaks:v8.30.1, zeek/zeek:9.0.0, python:3.11-slim-bookworm, nicolaka/netshoot:v0.15, jasonish/suricata:7.0.10 and jasonish/suricata:8.0.7; the axe checker at ${SP}/tools/node/node_modules/@axe-core/playwright; fonts DejaVu Sans, Liberation Sans, Roboto and Noto Sans.
- Be exact: every claim must come from a command you ran or a file:line you read. Quote real output. If you could not run something, say so plainly.
`

// ---------------- Track C: team audit to reach W3 ----------------
const AUDIT_SCHEMA = {
  type: 'object',
  properties: {
    people: { type: 'array', items: { type: 'object', properties: {
      person: { type: 'string' },
      tasks: { type: 'array', items: { type: 'object', properties: {
        id: { type: 'string' }, due: { type: 'string' },
        status: { type: 'string', enum: ['merged', 'pr-open', 'branch-matches-guide', 'branch-partial', 'branch-broken', 'not-started', 'blocked'] },
        branch: { type: 'string' }, problems: { type: 'array', items: { type: 'string' } },
        fix_steps: { type: 'array', items: { type: 'string' } }, blocked_by: { type: 'array', items: { type: 'string' } } },
        required: ['id', 'status', 'problems', 'fix_steps'] } },
      summary: { type: 'string' } }, required: ['person', 'tasks', 'summary'] } },
    notes: { type: 'string' },
  },
  required: ['people'],
}

const AUDIT_INTRO = `${CTX}
You audit teammates' work against the roadmap so the Security Lead (Ahmad) can tell each person exactly what to do to reach Week 3 (W3 is due Friday, October 30, 2026). Today is Tuesday, October 27, 2026. Nothing has been merged to main since October 14 except planning docs; there are no open pull requests. The remote branches were fetched today; list them with git -C /home/user/maxguard branch -r and inspect them read-only.
How to compare: a task's expected files and their exact expected content are what build_stage.py produces for that task: build the stage for the task (and for the task just before it in TASKS order when you need to know which files the task changes) and byte-compare each expected file with the branch's version (git -C /home/user/maxguard show origin/<branch>:<path>). Empty __init__.py files are correct when the stage's file is also empty; any other 0-byte file where the stage has content is a real problem. Note wrong paths (for example a doubled maxguard/maxguard/ folder), missing files, extra files, files from another task, and content differences (summarize each difference in one line; show a few diff lines when it helps). Where possible, export the branch into your folder and run ruff check . and pytest -m "not integration" -q there; if they cannot pass because an earlier task is missing, say which task.
For fix_steps, write exact commands a junior student can paste, in order (branch names from the guide, git commands, which guide step to redo). Use the branch names and PR titles the guides specify. Keep each person's steps short and concrete.
`

const AUDIT_GROUPS = [
  { key: 'jaiden', prompt: `Your label: audit-jaiden. Audit Jaiden (GitHub JWinborne1), who owns the critical path: JAI-00 (Week 0 onboarding), JAI-01, JAI-02, JAI-03, JAI-04, JAI-05, JAI-06, JAI-07 (read /home/user/maxguard/docs/roadmap/jaiden.md). His branches: origin/maxguard/__init__.py (JAI-01; note the odd branch name), origin/jaiden/restructure, origin/jaiden/event-schema (JAI-03), origin/jaiden/storage (JAI-06), origin/jaiden/docker-image (has a JAI-05 commit). Walk every commit on each branch (git log --stat origin/main..origin/<branch>), map it to a task, and compare with the stage files. Find out whether the branches are stacked on each other, whether JAI-02 (the three contracts) and JAI-04 exist anywhere, and what is missing for each of JAI-01..JAI-07. Also check his docs/TEAM.md row on main (git show origin/main:docs/TEAM.md) against the header order and his GitHub name JWinborne1. Give the shortest safe sequence to get JAI-01 and JAI-02 merged first (they unblock everyone), then the rest, including how to clean up the empty/wrong files without losing his work.` },
  { key: 'karthik', prompt: `Your label: audit-karthik. Audit Karthik (GitHub Karthiknair91): KAR-00, KAR-01 (traffic lab and the 14 test captures; due W0), KAR-02 (W1), KAR-03 (W2), KAR-04 (W3) (read /home/user/maxguard/docs/roadmap/karthik.md). His branch: origin/karthik/traffic-lab. Compare every file with the KAR-01 stage. The captures in his branch were reported to be header-only (24-byte pcap files): verify the size of each capture, and find the root cause by reading the lab files (compose, scripts) in his branch versus the guide's, and the guide's expected output (packet counts). If useful, actually run the guide's lab in Docker from the GUIDE's files in your own folder (it uses python:3.11-slim-bookworm and nicolaka/netshoot:v0.15, which are already pulled) to see what a correct run produces, and if you can, run his version too to reproduce the empty captures. Give exact fix steps. Note which later tasks KAR-01 blocks (JAK-01, JAK-02, KAR-02 and everything after).` },
  { key: 'others', prompt: `Your label: audit-others. Audit the other five teammates and Week 0 for everyone. People and GitHub names: Fiona (flau0306), Jakub (SXafir-byte), Jonattan (MeliorExi), Ali (al-kheder), Amory (gettalife); also report Week 0 status for Ahmad (ahmadalkhoudeir), Jaiden (JWinborne1) and Karthik (Karthiknair91). Week 0 is done when the person has a merged pull request adding their row to docs/TEAM.md (see section 0.9 of each guide). Check git -C /home/user/maxguard log origin/main -- docs/TEAM.md and the file itself (who has a row; is each row correct in column order and GitHub name). Amory has a branch origin/amory/week0-team-row: check whether it has any commits beyond main. For each of the five, list their tasks due W0-W3 from /home/user/maxguard/docs/roadmap/<name>.md and ${SP}/docgen/taskplan.py (with the 'depends' field), say which are blocked and by which unmerged task, and which they can start TODAY even though nothing is merged (for example ALI-01 has no dependencies; process tasks like AMO-02 can begin reading the official document; anyone can prepare a branch and run the guide's code on top of a stage build to be ready). Give each person their concrete next steps in order. Also produce, in notes, one merge order for every W0-W3 task (a topological order using 'depends') showing the critical path to AHM-02, and estimate how many review-and-merge rounds it needs.` },
]

const trackC = async () => {
  const res = await parallel(AUDIT_GROUPS.map(g => () =>
    agent(AUDIT_INTRO + g.prompt, { label: 'audit-' + g.key, phase: 'Team audit', schema: AUDIT_SCHEMA })))
  return res.filter(Boolean)
}

const team = await trackC()
return { team }
