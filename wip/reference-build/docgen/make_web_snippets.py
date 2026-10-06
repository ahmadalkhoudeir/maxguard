"""Derive the AHM-02 and AHM-03 versions of the dashboard files from the final
(AHM-06) files in ../ref, so the guides can show each stage. Re-run after any
change to the final files; every edit is asserted, so a drift fails loudly."""

from __future__ import annotations

import re
from pathlib import Path

REF = Path(__file__).resolve().parent.parent / "ref"
OUT = Path(__file__).resolve().parent / "snippets"


def sub(text: str, old: str, new: str, count: int = 1) -> str:
    assert text.count(old) == count, (old[:80], text.count(old))
    return text.replace(old, new)


def cut(text: str, start: str, end: str) -> str:
    """Remove from `start` (included) up to `end` (kept)."""
    a = text.index(start)
    b = text.index(end, a)
    return text[:a] + text[b:]


def routes() -> tuple[str, str]:
    final = (REF / "maxguard/web/routes.py").read_text()
    # ---- AHM-03 version: everything but the timeline and the devices page
    v2 = sub(final, '"""The dashboard\'s HTML pages (Ahmad, AHM-02, AHM-03, AHM-06).',
             '"""The dashboard\'s HTML pages (Ahmad, AHM-02, AHM-03).')
    v2 = re.sub(r"    GET   /timeline\?ip=.*\n    GET   /assets .*\n", "", v2)
    v2 = sub(v2, "import ipaddress\n", "")
    v2 = sub(v2, "from fastapi import APIRouter, Query, Request\n",
             "from fastapi import APIRouter, Request\n")
    v2 = sub(v2, "from maxguard.inventory import ip_sort_key\n", "")
    v2 = re.sub(r"TIMELINE_HOURS = \{.*?\n.*?\n(TIMELINE_LIMIT = 1000\n)", "", v2, flags=re.S)
    v2 = cut(v2, "# ---------- AHM-06: timeline and assets ----------",
             '@router.get("/favicon.ico"')
    # ---- AHM-02 version: the queue, the upload page and the mode switch
    v1 = sub(v2, '"""The dashboard\'s HTML pages (Ahmad, AHM-02, AHM-03).',
             '"""The dashboard\'s HTML pages (Ahmad, AHM-02).')
    v1 = re.sub(r"    GET   /alerts/\{finding_id\} .*\n    PATCH /alerts/.*\n", "", v1)
    v1 = sub(v1, "import time\n", "")
    v1 = sub(v1, "from maxguard.ai import load_home_text\n", "")
    v1 = sub(v1, "from maxguard.api.app import notify_change\n", "")
    v1 = re.sub(r"MAX_NAME_LENGTH = 100 .*\n", "", v1)
    v1 = cut(v1, "def now() -> float:", "def utc_time(")
    v1 = cut(v1, "def actor_of(request: Request) -> str:", "def render(")
    v1 = sub(v1, '        "statuses": ALERT_STATUSES, "home_text": load_home_text(),\n',
             '        "statuses": ALERT_STATUSES,\n')
    v1 = cut(v1, "# ---------- AHM-03: alert detail ----------", '@router.get("/favicon.ico"')
    return v1, v2


def templates() -> dict[str, str]:
    t = REF / "maxguard/web/templates"
    base = sub((t / "base.html").read_text(),
               '      <a href="/timeline">Timeline</a>\n      <a href="/assets">Devices</a>\n', "")
    queue = (t / "queue.html").read_text()
    queue = sub(queue, '      {% set home = home_text.get(alert.rule_id) %}\n', "")
    queue = sub(queue, '{% if mode == "home" and home %}{{ home.headline }}{% else %}'
                       '{{ alert.title }}{% endif %}', "{{ alert.title }}")
    alert = (t / "alert.html").read_text()
    alert = re.sub(r'<a href="/timeline\?ip=\{\{ alert\.(src|dst)_ip \| urlencode \}\}'
                   r'&amp;end=\{\{ \(alert\.last_seen \+ 1\) \| int \}\}">'
                   r'\{\{ alert\.(src|dst)_ip \}\}</a>', r"{{ alert.\1_ip }}", alert)
    assert "/timeline" not in alert
    return {"web_base_v1.html": base, "web_queue_v1.html": queue, "web_alert_v1.html": alert}


def tests() -> tuple[str, str]:
    final = (REF / "tests/unit/test_web.py").read_text()
    v2 = sub(final, '"""Tests for the dashboard pages (Ahmad, AHM-02, AHM-03, AHM-06).',
             '"""Tests for the dashboard pages (Ahmad, AHM-02, AHM-03).')
    v2 = sub(v2, "from maxguard.sensor.attribution import build_device_table\n", "")
    v2 = sub(v2, '@pytest.mark.parametrize("path", ["/", "/upload", "/timeline", "/assets"])',
             '@pytest.mark.parametrize("path", ["/", "/upload"])')
    v2 = sub(v2, '    for path in ("/", f"/alerts/{finding[\'finding_id\']}", "/timeline?ip=172.18.0.3"):',
             '    for path in ("/", f"/alerts/{finding[\'finding_id\']}"):')
    v2 = sub(v2, '    pages = ["/", "/upload", "/assets", "/timeline?ip=172.18.0.3",\n'
                 '             f"/alerts/{telnet_id(telnet_report)}"]',
             '    pages = ["/", "/upload", f"/alerts/{telnet_id(telnet_report)}"]')
    a = v2.index("# ---------- AHM-06: timeline and assets ----------")
    v2 = v2[:a].rstrip("\n") + "\n"
    v1 = sub(v2, '"""Tests for the dashboard pages (Ahmad, AHM-02, AHM-03).',
             '"""Tests for the dashboard pages (Ahmad, AHM-02).')
    v1 = sub(v1, "from maxguard.web import routes\n", "")
    v1 = sub(v1, '    for path in ("/", f"/alerts/{finding[\'finding_id\']}"):',
             '    for path in ("/",):  # the alert page comes in AHM-03')
    v1 = sub(v1, '    pages = ["/", "/upload", f"/alerts/{telnet_id(telnet_report)}"]',
             '    pages = ["/", "/upload"]')
    a = v1.index("# ---------- AHM-03: alert detail ----------")
    v1 = v1[:a].rstrip("\n") + "\n"
    return v1, v2


def main() -> None:
    r1, r2 = routes()
    (OUT / "web_routes_v1.py").write_text(r1)
    (OUT / "web_routes_v2.py").write_text(r2)
    for name, text in templates().items():
        (OUT / name).write_text(text)
    t1, t2 = tests()
    (OUT / "test_web_v1.py").write_text(t1)
    (OUT / "test_web_v2.py").write_text(t2)
    print("wrote the AHM-02 and AHM-03 dashboard snippets")


if __name__ == "__main__":
    main()
