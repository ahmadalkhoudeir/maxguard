"""Build the repository as it looks right after one roadmap task, into any folder.

Same rules as simulate.build_repo (roadmap order, each task's files only), but the
destination is chosen by the caller, so several builds can exist side by side.

Usage:  python build_stage.py TASK_ID DEST_DIR      (DEST_DIR must not exist yet)
        python build_stage.py ALL DEST_DIR           (every task)
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from simulate import source_of  # noqa: E402
from taskplan import TASKS  # noqa: E402


def build(task_id: str, dest: Path) -> list[str]:
    ids = [t["id"] for t in TASKS]
    upto = len(TASKS) - 1 if task_id == "ALL" else ids.index(task_id)
    if dest.exists():
        raise SystemExit(f"{dest} already exists; pick a new folder")
    dest.mkdir(parents=True)
    for task in TASKS[: upto + 1]:
        for entry in task.get("files", []):
            path, src = source_of(entry)
            target = dest / path
            if src is None:
                if target.is_dir():
                    shutil.rmtree(target)
                else:
                    target.unlink(missing_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            if src.is_dir():
                if target.exists():
                    shutil.rmtree(target)
                shutil.copytree(src, target, ignore=shutil.ignore_patterns("__pycache__"))
            else:
                shutil.copy2(src, target)
    return ids[: upto + 1]


if __name__ == "__main__":
    done = build(sys.argv[1], Path(sys.argv[2]).resolve())
    print(f"built {sys.argv[2]} with {len(done)} tasks, last {done[-1]}")
