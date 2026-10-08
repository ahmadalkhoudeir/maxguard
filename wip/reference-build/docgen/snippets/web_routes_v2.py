"""The dashboard's HTML pages (Ahmad, AHM-02, AHM-03).

create_app() in maxguard/api/app.py includes this router when it imports.

    GET   /                             alert queue (filters: ?status=&severity=)
    GET   /upload                       upload form (posts to /api/analyses)
    GET   /alerts/{finding_id}          one alert, Analyst or Home mode
    PATCH /alerts/{finding_id}/status   change status/assignee, returns the form again
    POST  /mode                         Analyst/Home switch (cookie mg_mode)

The pages read the stores only through request.app.state. Jinja2 escapes every
value; nothing from traffic or from the AI is ever marked |safe, because an
attacker writes the traffic (docs/ARCHITECTURE.md section 14).
"""

from __future__ import annotations

import time
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import quote, unquote

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates

from maxguard.ai import load_home_text
from maxguard.api.app import notify_change
from maxguard.models import SEVERITIES
from maxguard.storage.state import ALERT_STATUSES

router = APIRouter()
TEMPLATES = Jinja2Templates(directory=Path(__file__).resolve().parent / "templates")

MODES = ("analyst", "home")
YEAR_SECONDS = 365 * 24 * 3600
MAX_NAME_LENGTH = 100      # the same limit as "actor" in PATCH /api/alerts

# Home mode: the severity in plain words (no jargon), and color is never the only signal.
SEVERITY_WORDS = {
    "critical": "Critical: fix this today",
    "high": "High: fix this week",
    "medium": "Medium: fix this month",
    "low": "Low: fix when you can",
    "info": "Info: nothing to fix, good to know",
}
STATUS_LABELS = {"new": "New", "investigating": "Investigating", "resolved": "Resolved",
                 "false_positive": "False positive"}

# Sent with every page. The dashboard needs nothing from outside this computer, so the
# browser is told to refuse anything else, even if some text ever slipped past escaping.
SECURITY_HEADERS = {
    "Content-Security-Policy": (
        "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self'; "
        "connect-src 'self'; form-action 'self'; base-uri 'none'; object-src 'none'; "
        "frame-ancestors 'none'"),
    "X-Content-Type-Options": "nosniff",
    # "same-origin", not "no-referrer": with no-referrer, Chrome sends "Origin: null" on
    # form posts, and the API's cross-site check (rightly) refuses those.
    "Referrer-Policy": "same-origin",
}


# ---------- small helpers ----------

def now() -> float:
    """The clock, in one place (the web layer may read it; the engine never does)."""
    return time.time()


def utc_time(ts: float | None) -> str:
    """Unix seconds -> "2026-10-06 14:03:22 UTC" (the same on every machine)."""
    if ts is None:
        return ""
    return datetime.fromtimestamp(ts, tz=UTC).strftime("%Y-%m-%d %H:%M:%S UTC")


TEMPLATES.env.filters["utc_time"] = utc_time


def mode_of(request: Request) -> str:
    """"home" or "analyst" (the default) from the mg_mode cookie."""
    return "home" if request.cookies.get("mg_mode") == "home" else "analyst"


def actor_of(request: Request) -> str:
    """The display name stored in the mg_actor cookie ("" when not set yet or not valid)."""
    name = unquote(request.cookies.get("mg_actor", "")).strip()
    return name if valid_name(name) else ""


def valid_name(name: str) -> bool:
    """1 to 100 printable characters. A line break or another control character
    could fake an extra line in the audit trail, so it is refused."""
    return 0 < len(name) <= MAX_NAME_LENGTH and name.isprintable()


def render(request: Request, name: str, context: dict, status_code: int = 200) -> HTMLResponse:
    """Render a template with the values every page needs, plus the security headers."""
    full = {"mode": mode_of(request), "severities": SEVERITIES,
            "severity_words": SEVERITY_WORDS, "status_labels": STATUS_LABELS, **context}
    response = TEMPLATES.TemplateResponse(request, name, full, status_code=status_code)
    response.headers.update(SECURITY_HEADERS)
    return response


def error_page(request: Request, status_code: int, message: str) -> HTMLResponse:
    return render(request, "error.html", {"message": message}, status_code=status_code)


def empty_to_none(value: str | None) -> str | None:
    """A filter <select> sends "" for "All"."""
    return value or None


def safe_next(path: str) -> str:
    """Only a path on this site: "//evil.example" or "https://..." would be an open redirect."""
    if path.startswith("/") and not path.startswith("//") and "\\" not in path:
        return path
    return "/"


# ---------- AHM-02: queue, upload, mode switch ----------

@router.get("/", response_class=HTMLResponse)
def queue(request: Request, status: str | None = None, severity: str | None = None):
    status, severity = empty_to_none(status), empty_to_none(severity)
    try:
        alerts = request.app.state.state_store.list_alerts(status=status, severity=severity)
    except ValueError as err:  # unknown status or severity in the URL
        return error_page(request, 400, str(err))
    return render(request, "queue.html", {
        "alerts": alerts, "status": status or "", "severity": severity or "",
        "statuses": ALERT_STATUSES, "home_text": load_home_text(),
    })


@router.get("/upload", response_class=HTMLResponse)
def upload_page(request: Request):
    return render(request, "upload.html", {})


@router.post("/mode")
async def switch_mode(request: Request):
    """The Analyst/Home switch: a plain form, so it works with the keyboard and without
    JavaScript. The cookie is only a display preference, not a security setting."""
    form = await request.form()
    mode = form.get("mode")
    response = RedirectResponse(safe_next(str(form.get("next", "/"))), status_code=303)
    if mode in MODES:
        response.set_cookie("mg_mode", mode, max_age=YEAR_SECONDS, path="/",
                            samesite="lax", httponly=True)
    return response


# ---------- AHM-03: alert detail ----------

def controls_by_framework(controls: list[dict]) -> list[dict]:
    """[{"framework", "version", "controls": [...]}, ...] in the order they first appear."""
    groups: dict[tuple[str, str], list[dict]] = {}
    for control in controls:
        groups.setdefault((control["framework"], control["version"]), []).append(control)
    return [{"framework": framework, "version": version, "controls": items}
            for (framework, version), items in groups.items()]


def ai_status(request: Request, alert: dict) -> dict:
    """The "ai" part of the report that last updated this alert."""
    report = request.app.state.state_store.get_analysis(alert["analysis_id"]) or {}
    return report.get("ai") or {"status": "disabled", "reason": None}


def status_context(alert: dict, actor: str, message: str = "") -> dict:
    return {"alert": alert, "actor": actor, "statuses": ALERT_STATUSES, "message": message}


@router.get("/alerts/{finding_id}", response_class=HTMLResponse)
def alert_detail(request: Request, finding_id: str):
    alert = request.app.state.state_store.get_alert(finding_id)
    if alert is None:
        return error_page(request, 404, "No alert with this ID. It may have been removed.")
    return render(request, "alert.html", {
        **status_context(alert, actor_of(request)),
        "groups": controls_by_framework(alert["controls"]),
        "ai": ai_status(request, alert),
        "home": load_home_text().get(alert["rule_id"]),
    })


@router.patch("/alerts/{finding_id}/status", response_class=HTMLResponse)
async def change_status(request: Request, finding_id: str):
    """Called by the htmx form on the alert page; returns the form again (a fragment).
    The first time, the form also sends the person's display name ("actor"), which
    is stored in the mg_actor cookie so the page does not ask again."""
    form = await request.form()
    actor = actor_of(request) or str(form.get("actor", "")).strip()
    store = request.app.state.state_store
    alert = store.get_alert(finding_id)
    if alert is None:
        return error_page(request, 404, "No alert with this ID.")
    if not valid_name(actor):
        return render(request, "_status.html", status_context(
            alert, "", f"Type your name (1 to {MAX_NAME_LENGTH} characters) first."), 400)
    try:
        alert = store.update_alert(
            finding_id, actor=actor, at=now(),
            status=empty_to_none(str(form.get("status", ""))),
            assignee=str(form.get("assignee", "")).strip()[:MAX_NAME_LENGTH])
    except ValueError as err:  # unknown status
        return render(request, "_status.html", status_context(alert, actor, str(err)), 400)
    notify_change(request.app)  # open queues refresh themselves
    response = render(request, "_status.html", status_context(alert, actor, "Saved."))
    # Percent-encoded ("Jos%C3%A9"): a cookie value may only hold plain ASCII
    # (RFC 6265 section 4.1.1), and names such as "José" or "Łukasz" are not.
    response.set_cookie("mg_actor", quote(actor, safe=""), max_age=YEAR_SECONDS, path="/",
                        samesite="lax", httponly=True)
    return response


@router.get("/favicon.ico", include_in_schema=False)
def favicon() -> Response:
    """Browsers ask for this on every page; answer "nothing" instead of a 404 log line."""
    return Response(status_code=204)
