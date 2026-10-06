"""The dashboard's HTML pages (Ahmad, AHM-02, AHM-03, AHM-06).

create_app() in maxguard/api/app.py includes this router when it imports.

    GET   /                             alert queue (filters: ?status=&severity=)
    GET   /upload                       upload form (posts to /api/analyses)
    GET   /alerts/{finding_id}          one alert, Analyst or Home mode
    PATCH /alerts/{finding_id}/status   change status/assignee, returns the form again
    POST  /mode                         Analyst/Home switch (cookie mg_mode)
    GET   /timeline?ip=&hours=&end=     everything one address did (AHM-06)
    GET   /assets                       device inventory (AHM-06)

The pages read the stores only through request.app.state. Jinja2 escapes every
value; nothing from traffic or from the AI is ever marked |safe, because an
attacker writes the traffic (docs/ARCHITECTURE.md section 14).
"""

from __future__ import annotations

import ipaddress
import time
from datetime import UTC, datetime
from pathlib import Path

from fastapi import APIRouter, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates

from maxguard.ai import load_home_text
from maxguard.api.app import notify_change
from maxguard.inventory import ip_sort_key
from maxguard.models import SEVERITIES
from maxguard.storage.state import ALERT_STATUSES

router = APIRouter()
TEMPLATES = Jinja2Templates(directory=Path(__file__).resolve().parent / "templates")

MODES = ("analyst", "home")
YEAR_SECONDS = 365 * 24 * 3600
MAX_NAME_LENGTH = 100      # the same limit as "actor" in PATCH /api/alerts
TIMELINE_HOURS = {1: "Last hour", 6: "Last 6 hours", 24: "Last 24 hours", 72: "Last 3 days",
                  168: "Last 7 days"}  # the window selector: up to the 7 days events are kept
TIMELINE_LIMIT = 1000

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
    """The display name stored in the mg_actor cookie ("" when not set yet)."""
    return request.cookies.get("mg_actor", "").strip()[:MAX_NAME_LENGTH]


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
    if not actor or len(actor) > MAX_NAME_LENGTH:
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
    response.set_cookie("mg_actor", actor, max_age=YEAR_SECONDS, path="/",
                        samesite="lax", httponly=True)
    return response


# ---------- AHM-06: timeline and assets ----------

def alerts_for_ip(request: Request, ip: str) -> list[dict]:
    """Alerts where this address is the source or the destination."""
    alerts = request.app.state.state_store.list_alerts(limit=1000)
    return [a for a in alerts if ip in (a["src_ip"], a["dst_ip"])]


def evidence_links(alerts: list[dict]) -> dict[str, list[dict]]:
    """record_id, Zeek uid or Community ID -> the alerts whose evidence names it.

    A finding often cites a record that is not a timeline event (for example a
    maxguard_cleartext.log line); the connection's conn.log event shares its uid,
    so matching the uid too links the event to the alert."""
    links: dict[str, list[dict]] = {}
    for alert in alerts:
        for evidence in alert["evidence"]:
            for key in (evidence.get("record_id"), evidence.get("uid")):
                if key:
                    links.setdefault(key, []).append(alert)
    return links


def same_connection(event: dict, alert: dict) -> bool:
    """Zeek uids are not unique across captures: `zeek -D` (used for uploads, so results
    repeat) gives the first connection of every capture the same uid. So a uid match
    only counts when the event is also between the alert's two hosts, on its port."""
    return ({event["src_ip"], event["dst_ip"]} == {alert["src_ip"], alert["dst_ip"]}
            and event["dst_port"] == alert["dst_port"])


def alert_for_event(event: dict, links: dict[str, list[dict]]) -> dict | None:
    for key in (event["event_id"], event["uid"], event["community_id"]):
        for alert in links.get(key, []) if key else []:
            if same_connection(event, alert):
                return alert
    return None


@router.get("/timeline", response_class=HTMLResponse)
def timeline(request: Request, ip: str = "", hours: int = Query(24, ge=1, le=168),
             end: float | None = None):
    """Everything one address did in a time window (default: the last 24 hours).
    end (Unix seconds) moves the window back, for captures recorded earlier."""
    context = {"ip": ip, "hours": hours, "hour_choices": TIMELINE_HOURS, "end": end,
               "events": [], "alerts": []}
    if not ip:
        return render(request, "timeline.html", context)  # just the "which address?" form
    try:
        ip = str(ipaddress.ip_address(ip))  # also writes IPv6 the way Zeek does
    except ValueError:
        return error_page(request, 400, "That is not an IP address.")
    until = end if end is not None else now()
    events = request.app.state.event_store.query(ip=ip, since=until - hours * 3600,
                                                 until=until, limit=TIMELINE_LIMIT)
    alerts = alerts_for_ip(request, ip)
    links = evidence_links(alerts)
    rows = [{"event": event, "alert": alert_for_event(event, links)} for event in events]
    context.update(ip=ip, until=until, rows=rows, alerts=alerts, limit=TIMELINE_LIMIT)
    return render(request, "timeline.html", context)


def join_devices(assets: list[dict], devices: list[dict]) -> list[dict]:
    """Each asset plus mac, host_name and dns_names from the device table (JAK-08).

    A full join: a device seen only in DHCP or DNS (for example a phone that
    asked for an address and did nothing else yet) is still a device on the
    network, so it gets a row too. Sorted by IP address, like both inputs."""
    by_ip = {device["ip"]: device for device in devices}
    rows = {asset["ip"]: {**asset, "mac": "", "host_name": "", "dns_names": []}
            for asset in assets}
    for ip, device in by_ip.items():
        row = rows.setdefault(ip, {"ip": ip, "first_seen": device["first_seen"],
                                   "services": [], "software": [], "finding_count": 0})
        row.update(mac=device["mac"], host_name=device["host_name"],
                   dns_names=device["dns_names"])
    return [rows[ip] for ip in sorted(rows, key=ip_sort_key)]


@router.get("/assets", response_class=HTMLResponse)
def assets(request: Request):
    store = request.app.state.state_store
    newest = store.list_analyses(limit=1)
    analysis = newest[0] if newest else None
    report = store.get_analysis(analysis["analysis_id"]) if analysis else {}
    rows = join_devices(report.get("assets", []), report.get("devices", []))
    return render(request, "assets.html", {"analysis": analysis, "rows": rows})


@router.get("/favicon.ico", include_in_schema=False)
def favicon() -> Response:
    """Browsers ask for this on every page; answer "nothing" instead of a 404 log line."""
    return Response(status_code=204)
