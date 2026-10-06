"""Generate docs/ISSUES.md and scripts/create_issues.sh from the task plan.

Usage: python gen_issues.py REPO_ROOT
"""

from __future__ import annotations

import sys
from pathlib import Path

from plan_common import LABELS, MILESTONES, OWNERS, PROJECT_TITLE, REPO
from render import slug, task_heading
from taskplan import TASKS


def issue_title(task: dict) -> str:
    return f"{task['id']}: {task['title']}"


def anchor(task: dict) -> str:
    return task.get("anchor") or slug(task_heading(task))


def one_line(text: str) -> str:
    return " ".join(text.split())


def check_field(value: str, what: str) -> str:
    if "|" in value or "\n" in value:
        raise ValueError(f"{what} contains '|' or a newline: {value!r}")
    return value


def issues_md() -> str:
    lines = [
        "# Issues, labels, milestones, and the project board",
        "",
        "Every task in `docs/roadmap/` becomes one GitHub issue, so the team can assign,",
        "track, and close work on the project board. `scripts/create_issues.sh` creates",
        "them (its data rows were generated from the roadmap; keep them in step when a",
        "task changes), together with the labels, the milestones, and the project",
        f"**{PROJECT_TITLE}**. Ahmad runs it once in Week 0 (task AHM-01 in",
        "`docs/roadmap/ahmad.md`).",
        "",
        "## Running the script",
        "",
        "You need the GitHub CLI (`gh`) logged in with an account that can write to the",
        "repository, plus the `project` permission for the board:",
        "",
        "```bash",
        "gh auth login",
        "gh auth refresh -s project",
        "DRY_RUN=1 bash scripts/create_issues.sh    # prints every change, makes none",
        "bash scripts/create_issues.sh              # creates what is missing",
        "```",
        "",
        "What it does, in order:",
        "",
        "1. Creates or updates every label below (`gh label create --force`).",
        "2. Creates each milestone that does not exist yet, with its due date (GitHub's",
        "   REST API through `gh api`; `gh` has no milestone command).",
        f"3. Finds or creates the project **{PROJECT_TITLE}** and links it to the repository.",
        "4. Creates each issue whose exact title does not exist yet (open or closed), with",
        "   its labels and milestone, and adds it to the project.",
        "",
        "It is safe to run again: everything that already exists is skipped (labels are",
        "updated in place). It makes one change at a time and waits one second after",
        "each, as GitHub asks scripts to do, and it retries when GitHub reports a rate",
        "limit. Set `ASSIGN=1` to also assign each issue to its owner; GitHub can only",
        "assign people who already accepted the invitation to the repository.",
        "",
        "The script was tested in planning against a stand-in for `gh` that records the",
        "calls without contacting GitHub, including a second run and a rate-limit retry.",
        "It was **not run against the real repository** (not run — run it in AHM-01).",
        "",
        "## Labels",
        "",
        "| Label | Color | Meaning |",
        "|---|---|---|",
    ]
    for name, (color, desc) in LABELS.items():
        lines.append(f"| `{name}` | `#{color}` | {desc} |")
    lines += ["", "## Milestones", "", "| Milestone | Due | What it means |", "|---|---|---|"]
    for title, due, desc in MILESTONES.values():
        lines.append(f"| `{title}` | {due} | {desc} |")
    lines += ["", f"## The {len(TASKS)} issues", "",
              "| Issue title | Owner | Milestone | Labels | Needs first |", "|---|---|---|---|---|"]
    for task in TASKS:
        link = f"[{issue_title(task)}](roadmap/{task['owner']}.md#{anchor(task)})"
        labels = " ".join(f"`{x}`" for x in task["all_labels"])
        deps = ", ".join(task["depends"]) or "—"
        lines.append(f"| {link} | {OWNERS[task['owner']]['first']} | "
                     f"`{MILESTONES[task['milestone']][0]}` | {labels} | {deps} |")
    lines += ["", "Bugs and questions use the forms in `.github/ISSUE_TEMPLATE/`; questions",
              "belong in GitHub Discussions first."]
    return "\n".join(lines) + "\n"


SCRIPT_HEAD = r'''#!/usr/bin/env bash
# Create the MaxGuard v2.0 labels, milestones, project board and roadmap issues.
#
# The data at the bottom was generated from the roadmap in docs/roadmap/ during
# planning (October 6, 2026); docs/ISSUES.md lists the same rows. When a task is
# added or changed in the roadmap, update its row here as well: one line per
# issue, fields separated by "|" (title|labels|milestone|owner|link|goal|needs).
#
# Usage (from the repository root, with gh logged in):
#   gh auth refresh -s project                 # once: the project board needs it
#   DRY_RUN=1 bash scripts/create_issues.sh    # print every change, make none
#   bash scripts/create_issues.sh              # create what is missing
#   ASSIGN=1 bash scripts/create_issues.sh     # also assign issues to their owners
#
# Safe to run again: existing milestones, issues and the project are skipped,
# labels are updated in place. One change at a time with a pause after each,
# and a retry with back-off when GitHub reports a rate limit
# (https://docs.github.com/en/rest/using-the-rest-api/best-practices-for-using-the-rest-api).
set -euo pipefail

REPO="${REPO:-__REPO__}"
OWNER="${REPO%%/*}"
PROJECT_TITLE="${PROJECT_TITLE:-__PROJECT__}"
DRY_RUN="${DRY_RUN:-0}"
ASSIGN="${ASSIGN:-0}"
PAUSE="${PAUSE:-1}"   # seconds to wait after each change

# Print a change; run it unless DRY_RUN=1. Retries up to 3 times on a rate limit.
run() {
  if [[ "$DRY_RUN" == 1 ]]; then
    printf 'would run:'; printf ' %q' "$@"; printf '\n'
    return 0
  fi
  local attempt=1 wait=60 out
  while true; do
    if out=$("$@" 2>&1); then
      printf '%s\n' "$out"
      sleep "$PAUSE"
      return 0
    fi
    if [[ "$out" == *"rate limit"* && $attempt -lt 4 ]]; then
      echo "rate limited; waiting ${wait}s (attempt $attempt of 3)" >&2
      sleep "${RETRY_WAIT:-$wait}"
      wait=$((wait * 2))
      attempt=$((attempt + 1))
    else
      printf '%s\n' "$out" >&2
      return 1
    fi
  done
}

if ! gh auth status >/dev/null 2>&1; then
  echo "gh is not logged in: run 'gh auth login' first" >&2
  exit 4
fi

echo "== labels"
while IFS='|' read -r name color description; do
  [[ -z "$name" ]] && continue
  run gh label create "$name" --repo "$REPO" --color "$color" --description "$description" --force
done <<'LABELS'
'''

SCRIPT_MIDDLE = r'''LABELS

echo "== milestones"
existing_milestones=$(gh api "repos/$REPO/milestones?state=all&per_page=100" --paginate --jq '.[].title')
while IFS='|' read -r title due description; do
  [[ -z "$title" ]] && continue
  if grep -Fxq -- "$title" <<<"$existing_milestones"; then
    echo "milestone exists: $title"
    continue
  fi
  run gh api "repos/$REPO/milestones" -f title="$title" -f due_on="${due}T23:59:59Z" \
    -f description="$description" >/dev/null
done <<'MILESTONES'
'''

SCRIPT_PROJECT = r'''MILESTONES

echo "== project"
project=$(gh project list --owner "$OWNER" --format json \
  --jq ".projects[] | select(.title==\"$PROJECT_TITLE\") | .number" | head -n 1)
if [[ -z "$project" ]]; then
  if [[ "$DRY_RUN" == 1 ]]; then
    run gh project create --owner "$OWNER" --title "$PROJECT_TITLE"
    project="(new)"
  else
    project=$(gh project create --owner "$OWNER" --title "$PROJECT_TITLE" --format json --jq .number)
    sleep "$PAUSE"
    run gh project link "$project" --owner "$OWNER" --repo "${REPO#*/}" >/dev/null
  fi
fi
echo "project number: $project"

echo "== issues"
existing_issues=$(gh issue list --repo "$REPO" --state all --limit 1000 --json title --jq '.[].title')
body_file=$(mktemp)
trap 'rm -f "$body_file"' EXIT
created=0
skipped=0
while IFS='|' read -r title labels milestone assignee doc goal needs; do
  [[ -z "$title" ]] && continue
  if grep -Fxq -- "$title" <<<"$existing_issues"; then
    skipped=$((skipped + 1))
    continue
  fi
  # shellcheck disable=SC2016  # the backticks are Markdown code in the issue body, not a command
  printf '%s\n\n**Task:** https://github.com/%s/blob/main/%s\n\n**Needs first:** %s\n\nThe task lists the exact steps and the pull request checklist. Close this issue from the pull request with `Closes #<this number>`.\n' \
    "$goal" "$REPO" "$doc" "$needs" >"$body_file"
  assign=()
  [[ "$ASSIGN" == 1 ]] && assign=(--assignee "$assignee")
  create=(gh issue create --repo "$REPO" --title "$title" --body-file "$body_file"
          --label "$labels" --milestone "$milestone" ${assign[@]+"${assign[@]}"})
  if [[ "$DRY_RUN" == 1 ]]; then
    run "${create[@]}"
  else
    url=$(run "${create[@]}")
    echo "$url"
    run gh project item-add "$project" --owner "$OWNER" --url "$url" >/dev/null
  fi
  created=$((created + 1))
done <<'ISSUES'
'''

SCRIPT_TAIL = r'''ISSUES

echo "done: $created issue(s) to create or created, $skipped already existed"
'''


def script() -> str:
    labels = "\n".join(f"{check_field(n, 'label')}|{c}|{check_field(d, 'label description')}"
                       for n, (c, d) in LABELS.items())
    milestones = "\n".join(f"{check_field(t, 'milestone')}|{due}|{check_field(d, 'milestone description')}"
                           for t, due, d in MILESTONES.values())
    issue_rows = []
    for task in TASKS:
        doc = f"docs/roadmap/{task['owner']}.md#{anchor(task)}"
        fields = [issue_title(task), ",".join(task["all_labels"]), MILESTONES[task["milestone"]][0],
                  OWNERS[task["owner"]]["handle"], doc, one_line(task["goal"]),
                  ", ".join(task["depends"]) or "nothing"]
        issue_rows.append("|".join(check_field(f, f"{task['id']} field") for f in fields))
    head = SCRIPT_HEAD.replace("__REPO__", REPO).replace("__PROJECT__", PROJECT_TITLE)
    return (head + labels + "\n" + SCRIPT_MIDDLE + milestones + "\n" + SCRIPT_PROJECT
            + "\n".join(issue_rows) + "\n" + SCRIPT_TAIL)


def main(root: str) -> None:
    base = Path(root)
    (base / "docs").mkdir(parents=True, exist_ok=True)
    (base / "scripts").mkdir(parents=True, exist_ok=True)
    (base / "docs" / "ISSUES.md").write_text(issues_md())
    target = base / "scripts" / "create_issues.sh"
    target.write_text(script())
    target.chmod(0o755)
    print("wrote", base / "docs" / "ISSUES.md", "and", target)


if __name__ == "__main__":
    main(sys.argv[1])
