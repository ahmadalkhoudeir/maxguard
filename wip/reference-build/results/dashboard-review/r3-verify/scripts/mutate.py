"""Mutation test of tests/unit/test_web.py: revert one fix at a time (keeping any string
the tests grep for) and see whether the suite notices. Run: python mutate.py <build>"""
import shutil, subprocess, sys
from pathlib import Path

BUILD = Path(sys.argv[1]).resolve()
OUT = Path(__file__).resolve().parent.parent / "mut"
PY = "/tmp/claude-0/-home-user-maxguard/d28fe4b6-2c9f-5cd0-8e7f-d2be65aa4c01/scratchpad/ref/.venv/bin/python"
JS, CSS = "maxguard/web/static/app.js", "maxguard/web/static/app.css"
T = "maxguard/web/templates/"
MUTATIONS = [
    # (name, file, old, new, what is reverted)
    ("lock-holder-no-stream", JS, "return hold();", "return null;",
     "the tab that wins the lock never opens the stream"),
    ("lock-no-relay", JS, 'channel.postMessage("alerts-changed");', '/* channel.postMessage("alerts-changed") */;',
     "the holder stops relaying changes to other tabs"),
    ("bfcache-no-abort", JS, "waiting.abort();", ";",
     "a bfcached page stays in line for the lock (event.persisted string kept)"),
    ("bfcache-no-rejoin", JS, "if (event.persisted && waiting) {\n      join();", "if (event.persisted && waiting) {\n      void 0;",
     "a restored page never rejoins the line"),
    ("stream-502-no-retry", JS, "setTimeout(openStream, 5000);", ";",
     "a 502 on the stream is never retried"),
    ("catchup-refresh-removed", JS, "      refresh();\n      waiting = new AbortController();", "      waiting = new AbortController();",
     "a non-holder tab no longer catches up once"),
    ("again-flag-broken", JS, "again = true;\n      return;", "return;",
     "a refresh during load/settle is dropped instead of remembered"),
    ("filter-race-retarget-removed", JS, 'event.detail.target = document.getElementById("alerts");', ";",
     "the filter answer is no longer re-targeted"),
    ("upload-focus-removed", JS, 'form.querySelector("button").focus();', ";",
     "focus is not given back after an upload"),
    ("mode-switch-broken", JS, "modeSwitch.elements.next.value = location.pathname + location.search;",
     "void (location.pathname + location.search);", "the mode switch loses the filters again"),
    ("not-saved-handler-dead", JS, 'if (!form || form.id !== "status-form") {', "if (true) {",
     "the Not saved message is never shown (wording string kept)"),
    ("sev-nowrap-back", CSS, "  font-size: 0.85rem;\n}", "  font-size: 0.85rem;\n  white-space: nowrap;\n}",
     "severity badges cannot wrap again"),
    ("autocomplete-off-removed", T + "_status.html", ' autocomplete="off"', "",
     "the status form autocompletes again"),
    ("actor-pattern-removed", T + "_status.html", '\n         pattern=".*\\S.*" title="Your name, not only spaces"', "",
     "a name of only spaces passes the browser check again"),
    ("hx-sync-removed", T + "queue.html", ' hx-sync="this:replace"', ' hx-sync="this:drop"',
     "a newer refresh no longer replaces a running one (string check will catch this one)"),
    # the ones that should be caught by real assertions:
    ("text-field-no-linebreaks", "maxguard/web/routes.py", 'return str(value).replace("\\r", "").replace("\\n", "").strip()',
     "return str(value).strip()", "line breaks are compared literally again"),
    ("stale-status-logic-removed", "maxguard/web/routes.py", 'if "shown_status" in form and status == form["shown_status"]:\n        status = None',
     "pass", "a stale form overwrites someone else's status again"),
    ("stale-assignee-logic-removed", "maxguard/web/routes.py", 'if "shown_assignee" in form and assignee == text_field(form["shown_assignee"]):\n        assignee = None',
     "pass", "a stale form overwrites someone else's assignee again"),
    ("queue-limit-plus-one-removed", "maxguard/web/routes.py", "limit=QUEUE_LIMIT + 1)", "limit=QUEUE_LIMIT)",
     "the page never says more alerts match"),
    ("timeline-end-no-range-check", "maxguard/web/routes.py", "return end if 0 <= end <= LAST_TIME else None", "return end",
     "end= for 1e12 is written again"),
    ("utc-time-no-guard", "maxguard/web/routes.py", "    try:\n        return datetime.fromtimestamp(ts, tz=UTC).strftime(\"%Y-%m-%d %H:%M:%S UTC\")\n    except (TypeError, ValueError, OverflowError, OSError):\n        return f\"{ts!r} (not a valid time)\"",
     "    return datetime.fromtimestamp(ts, tz=UTC).strftime(\"%Y-%m-%d %H:%M:%S UTC\")", "an impossible time breaks the page again"),
    ("home-title-removed", T + "alert.html", '{% block title %}{{ home.headline if mode == "home" and home else alert.title }}{% endblock %}',
     "{% block title %}{{ alert.title }}{% endblock %}", "the tab title shows jargon in Home mode again"),
    ("aside-removed", T + "base.html", '<aside aria-label="Privacy"><p class="privacy">Your data never leaves this computer.</p></aside>',
     '<p class="privacy">Your data never leaves this computer.</p>', "the privacy line is no longer a landmark"),
]


def run(name, file, old, new, what):
    dest = OUT / name
    shutil.rmtree(dest, ignore_errors=True)
    shutil.copytree(BUILD, dest, ignore=shutil.ignore_patterns("lab", "docs", "__pycache__", ".venv"))
    path = dest / file
    text = path.read_text()
    assert text.count(old) == 1, (name, text.count(old))
    path.write_text(text.replace(old, new))
    proc = subprocess.run([PY, "-m", "pytest", "tests/unit/test_web.py", "-q", "-p", "no:cacheprovider",
                           "-x", "--no-header"], cwd=dest, capture_output=True, text=True,
                          env={"PATH": "/usr/bin:/bin", "PYTHONDONTWRITEBYTECODE": "1", "HOME": "/root"})
    failed = [line.split(" ")[1] for line in proc.stdout.splitlines() if line.startswith("FAILED")]
    verdict = "CAUGHT by " + ", ".join(failed) if proc.returncode else "NOT CAUGHT (suite passes)"
    shutil.rmtree(dest, ignore_errors=True)
    print(f"{name:34} {verdict:60} <- {what}", flush=True)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for m in MUTATIONS:
        run(*m)
