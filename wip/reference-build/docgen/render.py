"""Render docs/roadmap/*.md from the task plan, the reference files and the simulation outputs.

Usage: python render.py OUT_DIR
Fails loudly when a placeholder cannot be filled (a missing file or output).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from plan_common import MILESTONES, OWNERS, WEEK_TEXT
from simulate import OUT, REF, SNIPPETS, source_of
from taskplan import PREFIX, TASKS

HERE = Path(__file__).resolve().parent
WEEK0_TEMPLATE = Path("/tmp/claude-0/drafts/week0_template.md")

LANG = {".py": "python", ".yaml": "yaml", ".yml": "yaml", ".toml": "toml", ".md": "markdown",
        ".sh": "bash", ".json": "json", ".zeek": "zeek", ".rules": "text", ".ini": "ini",
        ".txt": "text"}
STATUS_LABEL = {"tested": "code, tested", "written": "code, written", "design": "design",
                "process": "process"}
OWNER_ORDER = ["ahmad", "jaiden", "fiona", "jakub", "jonattan", "ali", "amory", "karthik"]


def slug(heading: str) -> str:
    """GitHub's heading anchor: lower case, drop punctuation, spaces become hyphens."""
    text = heading.strip().lower()
    text = re.sub(r"[^\w\- ]", "", text)
    return text.replace(" ", "-")


def task_heading(task: dict) -> str:
    return f"{task['id']}: {task['title']}"


def task_link(task: dict, from_owner: str | None = None) -> str:
    anchor = task.get("anchor") or slug(task_heading(task))
    target = "" if from_owner == task["owner"] else f"{task['owner']}.md"
    return f"[{task['id']}]({target}#{anchor})"


def fence_for(text: str) -> str:
    return "````" if "```" in text else "```"


def code_block(text: str, lang: str) -> str:
    fence = fence_for(text)
    return f"{fence}{lang}\n{text.rstrip(chr(10))}\n{fence}"


def lang_for(path: str) -> str:
    name = Path(path).name
    if name in ("Dockerfile",) or name.endswith("Dockerfile"):
        return "dockerfile"
    if name in (".gitignore", ".dockerignore"):
        return "text"
    return LANG.get(Path(path).suffix, "text")


class SourceMap:
    """Which source file a repository path has at a given point in the roadmap."""

    def __init__(self):
        self.files: dict[str, Path] = {}
        self.dirs: dict[str, Path] = {}

    def add(self, entry) -> None:
        path, src = source_of(entry)
        if src is None:
            self.files.pop(path, None)
            return
        if src.is_dir():
            self.dirs[path] = src
        else:
            self.files[path] = src

    def find(self, path: str) -> Path:
        if path in self.files:
            return self.files[path]
        for folder, src in sorted(self.dirs.items(), key=lambda kv: -len(kv[0])):
            if path.startswith(folder + "/"):
                candidate = src / path[len(folder) + 1:]
                if candidate.is_file():
                    return candidate
        raise FileNotFoundError(f"no source for {path}")


def command_text(cmd: dict) -> str:
    return code_block(cmd["show"], "bash")


def output_text(task: dict, cmd: dict) -> str:
    if cmd.get("env") == "none":
        if "output" in cmd:
            return cmd["output"]
        if "output_file" in cmd:
            return (HERE / cmd["output_file"]).read_text().rstrip("\n")
        raise ValueError(f"{task['id']}/{cmd['id']}: no output for a command that is not run")
    path = OUT / task["id"] / f"{cmd['id']}.txt"
    if not path.exists():
        raise FileNotFoundError(f"missing simulation output {path}")
    return path.read_text().rstrip("\n")


def has_output(cmd: dict) -> bool:
    return cmd.get("env") != "none" or "output" in cmd or "output_file" in cmd


def run_block(task: dict, cmd: dict) -> str:
    parts = [command_text(cmd)]
    if has_output(cmd):
        label = cmd.get("label") or ("Expected output" if cmd.get("env") != "none"
                                     else "Expected output (not run in planning)")
        out = output_text(task, cmd)
        parts.append(f"{label}:\n\n" + code_block(out if out else "(no output)", "text"))
    if cmd.get("note"):
        parts.append(f"*{cmd['note']}*")
    return "\n\n".join(parts)


def fill(text: str, task: dict, sources: SourceMap) -> str:
    commands = {c["id"]: c for c in task["commands"]}

    def file_repl(m):
        path = m.group(1)
        return code_block(sources.find(path).read_text(), lang_for(path))

    def run_repl(m):
        return run_block(task, commands[m.group(1)])

    def cmd_repl(m):
        return command_text(commands[m.group(1)])

    def out_repl(m):
        return code_block(output_text(task, commands[m.group(1)]), "text")

    text = re.sub(r"@@FILE ([^@]+)@@", file_repl, text)
    text = re.sub(r"@@RUN ([\w-]+)@@", run_repl, text)
    text = re.sub(r"@@CMD ([\w-]+)@@", cmd_repl, text)
    text = re.sub(r"@@OUT ([\w-]+)@@", out_repl, text)
    if "@@" in text:
        raise ValueError(f"{task['id']}: unfilled placeholder in {text[:200]!r}")
    return text


def banners(task: dict) -> list[str]:
    out = []
    if task["status"] == "design":
        out.append(
            "> **Design task.** The code for this task was not written during planning. The "
            "steps give the files, the interfaces and the tests to write; the code is yours. "
            "Ask in GitHub Discussions when something is unclear, and update this section in "
            "your pull request with what you built.")
    if task["status"] == "written":
        out.append(
            "> **Written, not fully run.** The files in this task were written during planning, "
            "but part of them could not be run there (each such step says why). Your run is the "
            "first real one: if anything differs, fix this file in your pull request.")
    if task["hardware"]:
        out.append(
            "> **Needs hardware.** Steps that use the Raspberry Pi, the switch or other devices "
            "were not run during planning; they are marked *not run — verify on hardware*.")
    return out


def render_task(task: dict, sources: SourceMap, by_id: dict) -> str:
    owner = task["owner"]
    deps = ", ".join(task_link(by_id[d], owner) for d in task["depends"]) or "none"
    labels = " ".join(f"`{label}`" for label in task["all_labels"])
    milestone_title = MILESTONES[task["milestone"]][0]
    lines = [
        f"### {task_heading(task)}",
        "",
        f"**Due:** {WEEK_TEXT[task['milestone']]} · **Milestone:** `{milestone_title}` · "
        f"**Needs first:** {deps} · **Kind:** {STATUS_LABEL[task['status']]}",
        "",
        f"**Issue labels:** {labels}",
        "",
    ]
    for banner in banners(task):
        lines += [banner, ""]
    lines += ["#### Goal", "", fill(task["goal"], task, sources), "",
              "#### Prerequisites", "", fill(task["prereq"], task, sources), "",
              "#### Steps", ""]
    for n, step in enumerate(task["steps"], start=1):
        lines += [f"**Step {n}.** " + fill(step, task, sources), ""]
    if task.get("test"):
        lines += ["#### How to test", "", fill(task["test"], task, sources), ""]
    if task.get("why"):
        lines += ["#### What you just did and why", "", fill(task["why"], task, sources), ""]
    if task.get("checklist"):
        lines += ["#### Pull request checklist", ""]
        lines += [f"- [ ] {item}" for item in task["checklist"]]
        lines.append("")
    return "\n".join(lines)


def week0(owner: str, first_task: dict) -> str:
    p = OWNERS[owner]
    text = WEEK0_TEMPLATE.read_text()
    values = {
        "NAME": p["name"], "ROLE": p["role"], "HANDLE": p["handle"], "MODULE": p["module"],
        "BRANCH": f"{owner}/week0-team-row", "FIRST": p["first"],
        "REVIEWER_HANDLE": p["reviewer"], "EXAMPLE_TASK": first_task["id"],
    }
    if owner == "fiona":
        values["BRANCH"] = "fiona/week0-team-header"
        old = ("You will add your row to `docs/TEAM.md`. Every task in this roadmap uses the\n"
               "same six steps, so learn them now.")
        new = ("Your row is already in `docs/TEAM.md`, but the file has no table header, so "
               "GitHub does not show it as a table. You will add the header. Every task in this "
               "roadmap uses the same six steps, so learn them now.")
        assert old in text
        text = text.replace(old, new)
        old2 = ("2. **Make the change.** Run `code .`, open `docs/TEAM.md`, and add this line at\n"
                "   the end (keep the `|` characters):\n\n```markdown\n"
                "| {{NAME}} | {{ROLE}} | {{HANDLE}} | {{MODULE}} |\n```")
        new2 = ("2. **Make the change.** Run `code .`, open `docs/TEAM.md`, and add these two\n"
                "   lines at the very top (keep the `|` characters):\n\n```markdown\n"
                "| Name | Role | GitHub | Module |\n|---|---|---|---|\n```")
        assert old2 in text
        text = text.replace(old2, new2)
        text = text.replace('git commit -m "docs: add {{FIRST}} to TEAM.md"',
                            'git commit -m "docs: add a table header to TEAM.md"')
        text = text.replace('--title "docs: add {{FIRST}} to TEAM.md"',
                            '--title "docs: add a table header to TEAM.md"')
    if owner == "jaiden":
        text = text.replace("(Jaiden does it inside JAI-01)", "(you do it inside JAI-01)")
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", value)
    if "{{" in text:
        raise ValueError(f"unfilled Week 0 placeholder for {owner}")
    return text.strip("\n")


def person_file(owner: str, by_id: dict, sources_at: dict) -> str:
    p = OWNERS[owner]
    mine = [t for t in TASKS if t["owner"] == owner]
    real = [t for t in mine if not t["id"].endswith("-00")]
    helper = p["help"]
    lines = [
        f"# {p['first']}: {p['role']}",
        "",
        f"**{p['name']}** (@{p['handle']}) · Module: {p['module']} · Reviewer for your pull "
        f"requests: @{p['reviewer']} ({p['reviewer_first']}) · Ask first when stuck: {helper}",
        "",
        "This is your part of the MaxGuard v2.0 roadmap. Read "
        "[the roadmap overview](README.md) once, then work top to bottom: Week 0 first, then "
        "your tasks in order. Each task's ID is also the start of its GitHub issue's title.",
        "",
        "## Your tasks",
        "",
        "| Task | Due | Title | Needs first | Kind |",
        "|---|---|---|---|---|",
    ]
    for task in mine:
        deps = ", ".join(task_link(by_id[d], owner) for d in task["depends"]) or "—"
        lines.append(f"| {task_link(task, owner)} | {task['milestone']} | {task['title']} | {deps} | "
                     f"{STATUS_LABEL[task['status']]} |")
    lines += [
        "",
        "**Kind:** *code, tested* — the complete code below was run with its tests during "
        "planning; copy it exactly, then improve it in a later pull request if you like. "
        "*code, written* — written in planning, but part of it needs a machine planning did not "
        "have. *design* — you write the code from the steps. *process* — no code: setup, "
        "review, testing or release work.",
        "",
        week0(owner, real[0]),
        "",
    ]
    fall = [t for t in real if t["milestone"].startswith("W")]
    spring = [t for t in real if t["milestone"].startswith("S")]
    if fall:
        lines += ["## Fall 2026: v2.0-alpha", ""]
        lines += [render_task(t, sources_at[t["id"]], by_id) for t in fall]
    if spring:
        lines += ["## Spring 2027: v2.0", ""]
        lines += [render_task(t, sources_at[t["id"]], by_id) for t in spring]
    return "\n".join(lines).rstrip("\n") + "\n"


def sources_by_task() -> dict:
    """The SourceMap as it stands right after each task (in merge order)."""
    current = SourceMap()
    result = {}
    for task in TASKS:
        for entry in task["files"]:
            current.add(entry)
        snapshot = SourceMap()
        snapshot.files = dict(current.files)
        snapshot.dirs = dict(current.dirs)
        result[task["id"]] = snapshot
    return result


def main(out_dir: str) -> None:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    by_id = {t["id"]: t for t in TASKS}
    sources_at = sources_by_task()
    for owner in OWNER_ORDER:
        (out / f"{owner}.md").write_text(person_file(owner, by_id, sources_at))
        print("wrote", out / f"{owner}.md")


if __name__ == "__main__":
    main(sys.argv[1])
