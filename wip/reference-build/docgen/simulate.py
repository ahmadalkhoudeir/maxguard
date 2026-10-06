"""Replay the roadmap task by task and record real command output.

For every task, in roadmap order, build a fresh copy of the repository that
contains ONLY the files created by that task and the tasks before it, then run
the task's commands and save their output. A command that fails unexpectedly
means the roadmap order is wrong (for example a test imports a module that a
later task creates), and the run stops with a clear message.

Usage:  python simulate.py [TASK_ID ...]     (no ids = all tasks)
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRATCH = HERE.parent
REF = SCRATCH / "ref"
SNIPPETS = HERE / "snippets"
OUT = HERE / "outputs"
WORK = HERE / "work"
DEPS313 = SCRATCH / "deps313"
VENV_BIN = REF / ".venv" / "bin"
SHOWN_ROOT = "~/projects/maxguard"

sys.path.insert(0, str(HERE))
from taskplan import TASKS  # noqa: E402


def source_of(entry):
    """(repo_path, source_path_or_None) for one files entry."""
    if isinstance(entry, str):
        return entry, REF / entry
    path, src = entry
    if src is None:
        return path, None
    if src.startswith("snip:"):
        return path, SNIPPETS / src[5:]
    return path, REF / src


def build_repo(upto_index: int) -> Path:
    repo = WORK / "repo"
    if repo.exists():
        shutil.rmtree(repo)
    repo.mkdir(parents=True)
    for task in TASKS[: upto_index + 1]:
        for entry in task.get("files", []):
            path, src = source_of(entry)
            target = repo / path
            if src is None:
                if target.is_dir():
                    shutil.rmtree(target)
                else:
                    target.unlink(missing_ok=True)
                continue
            if not src.exists():
                raise FileNotFoundError(f"{task['id']}: source missing: {src}")
            target.parent.mkdir(parents=True, exist_ok=True)
            if src.is_dir():
                if target.exists():
                    shutil.rmtree(target)
                shutil.copytree(src, target, ignore=shutil.ignore_patterns("__pycache__"))
            else:
                shutil.copy2(src, target)
    return repo


def clean_output(text: str, repo: Path) -> str:
    text = text.replace(str(repo), SHOWN_ROOT)
    text = text.replace(str(VENV_BIN.parent), "~/projects/maxguard/.venv")
    text = re.sub(r"/tmp/pytest-of-[^/\s]+/pytest-\d+", "/tmp/pytest-of-you/pytest-0", text)
    lines = text.rstrip("\n").splitlines()
    if len(lines) > 60:
        lines = lines[:30] + ["..."] + lines[-25:]
    return "\n".join(lines)


def run_command(cmd: dict, repo: Path) -> tuple[int, str]:
    env = dict(os.environ)
    env["PATH"] = f"{VENV_BIN}:{env['PATH']}"
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env.pop("MAXGUARD_MAPPINGS_DIR", None)
    env["COLUMNS"] = "100"
    run = cmd.get("run", cmd["show"])
    kind = cmd.get("env", "venv")
    if kind == "zeek":
        run = ("docker run --rm --network none -v {repo}:/src -v {deps}:/deps:ro "
               "-e PYTHONPATH=/deps:/src -e PYTHONDONTWRITEBYTECODE=1 -w /src "
               "zeek/zeek:9.0.0 sh -c {cmd}").format(
                   repo=repo, deps=DEPS313, cmd=shlex_quote(run))
    cwd = repo / cmd.get("cwd", ".")
    # stderr goes into the same pipe, so the lines keep the order a terminal shows.
    res = subprocess.run(run, shell=True, cwd=cwd, env=env, stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT, text=True, timeout=cmd.get("timeout", 900))
    return res.returncode, clean_output(res.stdout, repo)


def shlex_quote(s: str) -> str:
    import shlex
    return shlex.quote(s)


def main(ids: list[str]) -> int:
    OUT.mkdir(exist_ok=True)
    summary = {}
    failures = 0
    for index, task in enumerate(TASKS):
        if ids and task["id"] not in ids:
            continue
        commands = [c for c in task.get("commands", []) if c.get("env") != "none"]
        if not commands:
            continue
        repo = build_repo(index)
        for cmd in commands:
            code, text = run_command(cmd, repo)
            expected = cmd.get("expect_code", 0)
            ok = code == expected
            (OUT / task["id"]).mkdir(exist_ok=True)
            (OUT / task["id"] / f"{cmd['id']}.txt").write_text(text + "\n")
            summary[f"{task['id']}/{cmd['id']}"] = {"code": code, "ok": ok}
            mark = "ok " if ok else "FAIL"
            print(f"[{mark}] {task['id']} {cmd['id']}: exit {code} (expected {expected})")
            if not ok:
                failures += 1
                print("      " + text.replace("\n", "\n      ")[-3000:])
    (OUT / "summary.json").write_text(json.dumps(summary, indent=1, sort_keys=True))
    print(f"{failures} failing command(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
