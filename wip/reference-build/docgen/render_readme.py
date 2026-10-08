"""Render docs/roadmap/README.md from the task plan. Usage: python render_readme.py OUT_DIR"""

from __future__ import annotations

import sys
from pathlib import Path

from plan_common import MILESTONES, OWNERS
from render import OWNER_ORDER, STATUS_LABEL, task_link
from taskplan import TASKS

BY_ID = {t["id"]: t for t in TASKS}
REAL = [t for t in TASKS if not t["id"].endswith("-00")]

HEADER = """# MaxGuard v2.0 — Roadmap

This folder is the team's build plan for MaxGuard v2.0. It replaces the Fall
2026 roadmap (kept for history in `docs/archive/ROADMAP_fall2026_original.md`).
The locked decisions behind it are in `docs/PROJECT_DECISIONS.md`, the design is
in `docs/ARCHITECTURE.md`, and the hardware lab is in `docs/HARDWARE.md`.

| File | Who |
|---|---|
"""

HOW_TO_USE = """
## How to use this roadmap

1. **Start with Week 0** at the top of your own file. Everyone does it, even if
   you already have the tools: it ends with your first merged pull request.
2. **Do your tasks in order.** Each task has an ID such as `JAI-02`. The same ID
   starts the title of its GitHub issue (created by `scripts/create_issues.sh`;
   see `docs/ISSUES.md`), so you can find, assign, and close it on the project
   board. Before you start a task, check **Needs first**: if one of those tasks
   is not merged yet, say so in your issue, help with it, or start your next
   unblocked task.
3. **Every task has the same parts:** goal, prerequisites, exact steps, the code
   or the specification, the commands to run with their expected output, how to
   test it, "what you just did and why", and a pull request checklist.
4. **Four kinds of task.** *Code, tested*: the complete code is in the task and
   was run with its tests during planning, in roadmap order, on a copy of the
   repository holding only the files of the tasks before it — copy it exactly.
   *Code, written*: written in planning, but part of it needs a machine planning
   did not have (the step says which). *Design*: the steps give the files,
   interfaces and tests, and you write the code. *Process*: setup, review,
   testing, or release work with no code.
5. **Milestones are due before the Friday review.** The meeting is for showing
   and reviewing work, not for doing it. If you will miss a date, say so in your
   issue by Wednesday.
6. **Stuck for more than a day?** Post the exact command and the exact error in
   GitHub Discussions (category *Q&A*) and tag your help person (table below).
   Quick chat can stay in Microsoft Teams, but answers others might need go in
   Discussions so they can be searched.
7. **Steps marked "not run — verify on hardware"** (or "not run in planning")
   could not be run while this plan was written. When you run them, fix the
   document in your pull request if anything differs.

### Help people

| Person | Ask first | Then |
|---|---|---|
| Ahmad | Jaiden | — |
| Jaiden | Ahmad | — |
| Fiona | Jaiden | Ahmad |
| Jakub | Fiona | Jaiden |
| Jonattan | Jaiden | Ali |
| Ali | Jonattan | Jaiden |
| Amory | Ahmad (frameworks) | Jonattan (GitHub) |
| Karthik | Jaiden | Fiona |
"""

PHASES = """
## Phases and Friday checkpoints

Dates follow the CCSU academic calendar as published in October 2026 (Fall 2026
in full; some Spring 2027 dates were inferred, marked below — confirm at
https://www.ccsu.edu/calendar). Milestone names match the GitHub milestones made
by `scripts/create_issues.sh`.

### Fall 2026 — `v2.0-alpha`

| Week | Friday | Milestone | What must work at the review |
|---|---|---|---|
| W0 | **Oct 9** | `W0 Onboarding and contracts` | Everyone has one merged pull request. GitHub is set up, the repository is restructured, CI runs, the three contracts (v2.0 versions) are merged, and the traffic lab has recorded its 14 captures. |
| W1 | **Oct 16** | `W1 Building blocks` | MaxGuard's Zeek scripts and Suricata settings, the fixtures, both adapters, all 13 rules, the event normalizer, the asset inventory, the citation check, the NIST SP 800-53 mapping file, and the engine image are merged, each with tests. |
| W2 | **Oct 23** | `W2 First end-to-end demo` | **Demo:** `maxguard analyze` on `telnet.pcap` (in the engine image) prints a Telnet finding mapped to NIST SP 800-53 with ATT&CK techniques; on a laptop with Ollama, the same finding gets an explanation whose every sentence cites record IDs. Integration tests run on every lab capture. |
| W3 | **Oct 30** | `W3 API and alert queue` | Upload a capture in the browser; the alert queue shows its findings; storage keeps them; CI runs the integration tests in the engine image; PCI DSS rows are merged. |
| W4 | **Nov 6** | `W4 Full offline report` | Alert detail page with Analyst and Home modes; Suricata runs in the pipeline; JSON, CSV and HTML reports; **a full report is produced with the network unplugged** (the original Fall 2026 gate); the default models are proposed. |
| W5 | **Nov 13** | `W5 Alpha feature freeze` | All alpha features merged; CISA CPG 2.0 and CJIS v6.1 rows merged; the security review is done. After this date: bug fixes only. |
| W6 | **Nov 20** | `W6 Release candidate` | `v2.0-alpha-rc1` is tagged with the offline bundle and handed to an outside tester. |
| W7 | Nov 27 | — | Thanksgiving recess (no classes Nov 25–29; no meeting). Only fixes for the tester's issues. |
| W8 | **Dec 4** | `W8 v2.0-alpha` | `v2.0-alpha` released; the acceptance test below passes; presentation delivered; the hardware lab is built if the parts have arrived. |

Final exams run December 7–13. Winter break (December 14 – January 19) has no
planned work; anything done then is optional.

### Spring 2027 — `v2.0`

Spring classes start Wednesday, January 20, 2027.

| Week | Friday | Milestone | What must work at the review |
|---|---|---|---|
| S1–S4 | Jan 22 – **Feb 12** | `S1-S4 Live sensor` | The Raspberry Pi sensor runs Zeek and Suricata on the mirror port and its logs reach the console every 15 minutes; device attribution; IP timeline and device pages; chain-of-custody log; the live end-to-end check passes. |
| S5–S8 | Feb 19 – **Mar 12** | `S5-S8 Respond` | Blocking with a human in the loop: generated rules, preview before you block (7 days of stored events), approvals with audit and revert, the OPNsense connector; signed intel bundles; the JA4 watchlist; prompt-injection tests and the model re-evaluation. Residence halls close at 5 p.m. on Mar 12: meet early or online. |
| — | Mar 19 | — | Spring break (inferred from residence-hall dates: no meeting). |
| — | Mar 26 | — | Possibly a CCSU recess (Good Friday; not confirmed): no milestone. |
| S9–S11 | Apr 2 – **Apr 16** | `S9-S11 Detect more` | Decoys on their own IP address, per-device baselines, NetFlow/IPFIX input. |
| S12 | **Apr 23** | `S12 v2.0 feature freeze` | The host agent; every v2.0 feature merged. Bug fixes only after this date. |
| S13 | **Apr 30** | `S13 v2.0 release candidate` | `v2.0-rc1` tagged and handed to an outside tester. |
| S14 | **May 7** | `S14 v2.0` | `v2.0` released; the v2.0 acceptance test passes. Final exams start May 10. |
"""

ACCEPTANCE = """
## Acceptance test for `v2.0-alpha` (Friday, December 4)

Run by someone who did not build the release, on a machine that has never run
MaxGuard. Ahmad records each result (AHM-05).

1. On a clean machine with only Docker installed, download every file of the
   GitHub Release (the offline bundle) into one empty folder.
2. Verify the checksums (`sha256sum -c SHA256SUMS` on Linux,
   `shasum -a 256 -c SHA256SUMS` on macOS): every part prints `OK`.
3. Nothing to reassemble or unpack: `install.sh` joins the parts itself.
4. **Disconnect the network** (Wi-Fi off, cable out). Check that
   `ping -c 1 1.1.1.1` fails.
5. Run `bash install.sh`. It finishes without errors.
6. Open http://127.0.0.1:8000. The dashboard loads and shows the privacy note.
7. Upload `sample-telnet.pcap` from the bundle. The alert queue shows a
   `cleartext.telnet` alert mapped to controls in all four frameworks, with
   ATT&CK techniques and a local AI explanation whose sentences cite record IDs.
8. Upload `sample-telnet-zeek-logs.tar.gz`. A report appears (the log-import path works).
9. Download the JSON, CSV, and HTML reports. All three open and contain the same findings.
10. Upload `sample-clean-tls13.pcap`. It produces zero findings.

The `v2.0` acceptance test (May 7, AHM-09) adds: the live sensor on the
reference lab, a blocked IP address with preview, approval and revert, a
verified intel bundle, and the chain-of-custody check.

## Labels used on issues

| Label | Meaning |
|---|---|
| `owner:<name>` | Who does it (`owner:ahmad`, `owner:jaiden`, ...) |
| `phase:alpha`, `phase:spring` | Which release it belongs to |
| `type:task`, `type:bug`, `type:question`, `type:docs` | Kind of issue |
| `area:engine`, `area:ai`, `area:mapping`, `area:ui`, `area:api`, `area:storage`, `area:sensor`, `area:response`, `area:testing`, `area:release`, `area:program` | Part of the system |
| `critical-path` | A delay here delays the next demo or release |
| `contract-change` | Changes a contract: needs Jaiden's review and the Security Lead's approval |
| `blocked` | Waiting on another task (say which in a comment) |
| `needs-hardware` | Contains steps marked "not run — verify on hardware" |
"""


def node(task: dict) -> str:
    short = task["title"].split(":")[0]
    if len(short) > 34:
        short = short[:32].rstrip() + "…"
    short = short.replace('"', "'")
    return f'  {task["id"].replace("-", "")}["{task["id"]}<br/>{short}"]'


def reaches(start: str, goal: str, skip_edge: tuple[str, str]) -> bool:
    """True if goal depends on start through some path that does not use skip_edge."""
    stack, seen = [goal], set()
    while stack:
        current = stack.pop()
        for dep in BY_ID[current]["depends"]:
            if (dep, current) == skip_edge or dep in seen:
                continue
            if dep == start:
                return True
            seen.add(dep)
            stack.append(dep)
    return False


def reduced_edges(tasks: list[dict], ids: set[str]) -> list[tuple[str, str]]:
    """Direct links only: drop A -> C when A already reaches C through another task."""
    edges = []
    for t in tasks:
        for dep in t["depends"]:
            if dep in ids and not reaches(dep, t["id"], (dep, t["id"])):
                edges.append((dep, t["id"]))
    return edges


def blocked_by_graph() -> str:
    """Mermaid graph of the alpha tasks up to the Week 4 milestone, one box per week."""
    weeks = ["W0", "W1", "W2", "W3", "W4"]
    tasks = [t for t in REAL if t["milestone"] in weeks]
    ids = {t["id"] for t in tasks}
    edges = reduced_edges(tasks, ids)
    lines = ["```mermaid", "flowchart TB"]
    for week in weeks:
        lines.append(f'  subgraph {week}["{MILESTONES[week][0]}"]')
        lines += ["  " + node(t) for t in tasks if t["milestone"] == week]
        lines.append("  end")
    for dep, task_id in edges:
        lines.append(f'  {dep.replace("-", "")} --> {task_id.replace("-", "")}')
    critical = [t["id"].replace("-", "") for t in tasks if "critical-path" in t["all_labels"]]
    lines.append("  classDef critical stroke-width:3px")
    lines.append(f"  class {','.join(critical)} critical")
    lines.append("```")
    return "\n".join(lines)


def longest_chain(target: str) -> list[str]:
    memo: dict[str, list[str]] = {}

    def chain(task_id: str) -> list[str]:
        if task_id not in memo:
            deps = BY_ID[task_id]["depends"]
            best = max((chain(d) for d in deps), key=len, default=[])
            memo[task_id] = best + [task_id]
        return memo[task_id]

    return chain(target)


def tasks_by_week() -> str:
    lines = ["| Due | Task | Owner | Title | Kind |", "|---|---|---|---|---|"]
    for task in REAL:
        owner = OWNERS[task["owner"]]["first"]
        lines.append(f"| {task['milestone']} | {task_link(task)} | {owner} | {task['title']} | "
                     f"{STATUS_LABEL[task['status']]} |")
    return "\n".join(lines)


def main(out_dir: str) -> None:
    files = "\n".join(
        f"| [{o}.md]({o}.md) | {OWNERS[o]['first']} — {OWNERS[o]['role']}; {OWNERS[o]['module']} |"
        for o in OWNER_ORDER)
    demo_chain = " → ".join(longest_chain("FIO-04"))
    blocked = f"""
## Who is blocked by whom

The graph shows the tasks up to the Week 4 milestone; an arrow means "must be
merged before". To keep it readable it draws only direct links (if A is needed
by B and B by C, there is no extra arrow from A to C). Thick boxes are on the
critical path. Every task's **Needs first** line in its person file is the full
list, including spring.

{blocked_by_graph()}

The longest chain to the Week 2 demo is **{demo_chain}**. If any of these slips,
the demo slips, so these pull requests are reviewed first (within one day).

How the team avoids waiting:

- Everyone codes against the contracts in `docs/ARCHITECTURE.md` section 5 from
  day one; the code is already in JAI-02.
- The test fixtures (`tests/fixtures/zeek/*`) are real Zeek 9.0.0 and Suricata
  output, so rules, the normalizer, the inventory, and the AI client are tested
  without Docker or a capture.
- Ahmad builds the pages against stores filled from fixtures, so the dashboard
  does not wait for real uploads.

## All tasks by due date

{tasks_by_week()}
"""
    text = HEADER + files + "\n" + HOW_TO_USE + PHASES + blocked + ACCEPTANCE
    Path(out_dir, "README.md").write_text(text.rstrip("\n") + "\n")
    print("wrote", Path(out_dir, "README.md"))


if __name__ == "__main__":
    main(sys.argv[1])
