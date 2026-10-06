"""The dashboard's HTML pages (Ahmad, AHM-02).

create_app() in maxguard/api/app.py includes this router when it imports.

    GET   /                             alert queue (filters: ?status=&severity=)
    GET   /upload                       upload form (posts to /api/analyses)
    POST  /mode                         Analyst/Home switch (cookie mg_mode)

The pages read the stores only through request.app.state. Jinja2 escapes every
value; nothing from traffic or from the AI is ever marked |safe, because an
attacker writes the traffic (docs/ARCHITECTURE.md section 14).
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates

from maxguard.models import SEVERITIES
from maxguard.storage.state import ALERT_STATUSES

router = APIRouter()
TEMPLATES = Jinja2Templates(directory=Path(__file__).resolve().parent / "templates")

MODES = ("analyst", "home")
YEAR_SECONDS = 365 * 24 * 3600

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

def utc_time(ts: float | None) -> str:
    """Unix seconds -> "2026-10-06 14:03:22 UTC" (the same on every machine)."""
    if ts is None:
        return ""
    return datetime.fromtimestamp(ts, tz=UTC).strftime("%Y-%m-%d %H:%M:%S UTC")


TEMPLATES.env.filters["utc_time"] = utc_time


def mode_of(request: Request) -> str:
    """"home" or "analyst" (the default) from the mg_mode cookie."""
    return "home" if request.cookies.get("mg_mode") == "home" else "analyst"


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
        "statuses": ALERT_STATUSES,
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


@router.get("/favicon.ico", include_in_schema=False)
def favicon() -> Response:
    """Browsers ask for this on every page; answer "nothing" instead of a 404 log line."""
    return Response(status_code=204)
