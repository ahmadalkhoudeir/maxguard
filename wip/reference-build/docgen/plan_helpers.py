"""Steps and checklist items that every task repeats, written once."""

COMMON_CHECKS = [
    "`ruff check .` prints `All checks passed!`",
    "`pytest -m \"not integration\" -q` passes on your laptop",
    "The pull request title has the form `type: summary (TASK-ID)` and the body says "
    "`Closes #<issue number>`",
    "No secrets, passwords, email addresses, personal data, or captures from a real network "
    "(CLAUDE.md rule 6)",
    "Any new dependency has a row in `docs/DEPENDENCIES.md` with its license",
    "CI is green and your reviewer approved",
]


def start_step(branch: str) -> str:
    return (
        "Update `main` and create your branch for this task (one branch per task):\n\n"
        "```bash\ncd ~/projects/maxguard\nsource .venv/bin/activate\n"
        f"git checkout main && git pull\ngit checkout -b {branch}\n```\n\n"
        "If `source .venv/bin/activate` fails, you have not made the virtual environment "
        "yet: do Week 0 section 0.11 first."
    )


def pr_step(title: str, reviewer: str) -> str:
    return (
        "Commit, push, and open the pull request:\n\n"
        "```bash\ngit add -A\n"
        "git status          # only this task's files: nothing from .venv/, data/ or lab/captures/\n"
        f"git commit -m \"{title}\"\ngit push -u origin HEAD\n```\n\n"
        "`HEAD` means \"the branch I am on\", so you do not have to retype its name. Open the "
        "repository on github.com: a yellow bar shows your branch with a **Compare & pull "
        f"request** button. Click it, keep the title `{title}`, fill in the template (paste the "
        "real output of the commands above under **How I tested it**), write "
        f"`Closes #<issue number>` (this task's issue), and pick **@{reviewer}** under "
        "**Reviewers**. Click **Create pull request**, then fix anything CI or the reviewer finds "
        "with new commits on the same branch."
    )


def checklist(extra: list[str] | None = None) -> list[str]:
    return COMMON_CHECKS + list(extra or [])
