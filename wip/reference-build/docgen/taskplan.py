"""The whole roadmap in one ordered list: TASKS (merge order, used by simulate.py)."""

import plan_ahmad
import plan_ali
import plan_amory
import plan_fiona
import plan_jaiden
import plan_jakub
import plan_jonattan
import plan_karthik
from plan_common import MILESTONES, OWNERS

PREFIX = {"ahmad": "AHM", "jaiden": "JAI", "fiona": "FIO", "jakub": "JAK",
          "jonattan": "JON", "ali": "ALI", "amory": "AMO", "karthik": "KAR"}

# The order tasks are expected to merge in. Every task's prerequisites come
# before it, which simulate.py proves by running each task's tests on a copy of
# the repository that holds only the files of the tasks up to that point.
ORDER = """
AHM-01 JAI-01 JAI-02 KAR-01
JAK-01 JAK-02 KAR-02 FIO-01 FIO-02 JAK-03 JAI-03 JAK-04 JON-01 AMO-01 JAI-04 ALI-01
JAI-05 FIO-03 FIO-04 JON-02 ALI-02 KAR-03
JAI-06 JAI-07 JON-03 AMO-02 ALI-03 KAR-04 AHM-02
JAK-05 AMO-03 FIO-05 JON-04 AHM-03 ALI-04
JAI-08 AMO-04 AHM-04
JON-05 JAI-09 KAR-05
JAI-10 JAK-06 AHM-05
JAK-07 JAK-08 AMO-05 AHM-06 KAR-06
JAI-11 JAK-09 AHM-07 AHM-08 JON-06 ALI-05
FIO-06 FIO-07 JAK-10
JAK-11
JAI-12
AHM-09
""".split()


def onboarding_task(owner: str) -> dict:
    person = OWNERS[owner]
    return {
        "id": f"{PREFIX[owner]}-00", "owner": owner, "milestone": "W0",
        "title": f"Week 0 onboarding ({person['first']})",
        "labels": ["area:program"], "status": "process", "depends": [],
        "goal": "Install the tools, clone the repository, merge your first pull request, "
                "and post in the Week 0 check-in.",
        "prereq": "None.", "steps": [], "files": [], "commands": [],
        "test": "", "why": "", "checklist": [],
        "anchor": "week-0--onboarding-due-friday-october-9-2026",
    }


def _all_plan_tasks() -> dict[str, dict]:
    tasks = {}
    for module in (plan_ahmad, plan_jaiden, plan_fiona, plan_jakub, plan_jonattan, plan_ali,
                   plan_amory, plan_karthik):
        for task in module.TASKS:
            if task["id"] in tasks:
                raise ValueError(f"duplicate task id {task['id']}")
            tasks[task["id"]] = task
    return tasks


def _finish(task: dict) -> dict:
    task.setdefault("status", "tested")
    task.setdefault("hardware", False)
    task.setdefault("files", [])
    task.setdefault("commands", [])
    phase = "phase:alpha" if task["milestone"].startswith("W") else "phase:spring"
    labels = ["type:task", phase, f"owner:{task['owner']}", *task.get("labels", [])]
    if task["hardware"]:
        labels.append("needs-hardware")
    task["all_labels"] = list(dict.fromkeys(labels))
    return task


def build() -> list[dict]:
    tasks = _all_plan_tasks()
    missing = sorted(set(tasks) - set(ORDER))
    unknown = sorted(set(ORDER) - set(tasks))
    if missing or unknown:
        raise ValueError(f"ORDER is missing {missing} / has unknown {unknown}")
    for task in tasks.values():
        if task["milestone"] not in MILESTONES:
            raise ValueError(f"{task['id']}: unknown milestone {task['milestone']}")
        for dep in task["depends"]:
            if dep not in tasks:
                raise ValueError(f"{task['id']} depends on unknown {dep}")
    # Stable topological sort: keep ORDER, but never put a task before a prerequisite.
    ordered_ids: list[str] = []
    waiting = list(ORDER)
    while waiting:
        for task_id in waiting:
            if all(dep in ordered_ids for dep in tasks[task_id]["depends"]):
                ordered_ids.append(task_id)
                waiting.remove(task_id)
                break
        else:
            raise ValueError(f"dependency cycle among {waiting}")
    milestones = list(MILESTONES)
    for task_id in ordered_ids:
        task = tasks[task_id]
        for dep in task["depends"]:
            if milestones.index(tasks[dep]["milestone"]) > milestones.index(task["milestone"]):
                raise ValueError(f"{task_id} ({task['milestone']}) depends on {dep}, "
                                 f"due later ({tasks[dep]['milestone']})")
    ordered = [_finish(tasks[i]) for i in ordered_ids]
    onboarding = [_finish(onboarding_task(owner)) for owner in OWNERS]
    return onboarding + ordered


TASKS = build()
