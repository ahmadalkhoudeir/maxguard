"""MaxGuard's JSON API (Jaiden, JAI-07).

The dashboard, the live sensor and the host agent all talk to MaxGuard through
this app. docs/ARCHITECTURE.md section 10 lists the endpoints.

- The API is the only part of MaxGuard that reads the clock and writes to the
  stores. The engine (maxguard.pipeline) never does either, so the same input
  always gives the same report.
- Uploads are saved under a name we generate, never the client's file name
  (which could contain "../"), and the file type is decided by its first bytes.
- One analysis runs at a time: Zeek and Suricata already use every CPU core,
  so two at once on a Raspberry Pi only makes both slower.
- POST /api/ingest is how sensors and host agents on the LAN send data. It is
  OFF unless MAXGUARD_INGEST_TOKEN is set, and every request must carry that
  token. The dashboard and the rest of the API are published on 127.0.0.1 only.
  Sensors reach a second app, create_ingest_app(), which serves nothing but
  POST /api/ingest on its own port; publishing that port on the LAN is an
  explicit, optional choice of the user (CLAUDE.md rule 1: nothing leaves or
  enters the machine by default).
- Browsers refuse to let other websites read this API, but they do let another
  website *send* a form to it. Requests that change something are therefore
  refused when the browser says they come from another site (cross-site
  request forgery, OWASP CSRF Prevention Cheat Sheet).
- A website can also make its own name point to 127.0.0.1 after the page has
  loaded (DNS rebinding); the browser then treats this API as part of that
  website. The API therefore answers only requests whose Host header names this
  machine, or an address listed in MAXGUARD_ALLOWED_HOSTS.

Start it with:  uvicorn maxguard.api.app:create_app --factory --port 8000
Ingest only:    uvicorn maxguard.api.app:create_ingest_app --factory --port 8001
"""

from __future__ import annotations

import asyncio
import hmac
import importlib
import importlib.util
import ipaddress
import os
import re
import secrets
import tarfile
import tempfile
import threading
import time
import zipfile
from collections.abc import AsyncIterator
from pathlib import Path
from typing import BinaryIO
from urllib.parse import urlparse

from fastapi import APIRouter, FastAPI, HTTPException, Query, Request
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from starlette.datastructures import FormData, UploadFile
from starlette.middleware.trustedhost import TrustedHostMiddleware

from maxguard import __version__, offline
from maxguard.adapters.pcap import PCAP_MAGIC
from maxguard.adapters.zeeklogs import ArchiveTooLarge
from maxguard.pipeline import UnsupportedInput, analyze
from maxguard.storage.events import EventStore
from maxguard.storage.state import StateStore
from maxguard.suricata.runner import SuricataError
from maxguard.zeek.runner import ZeekError

STATIC_DIR = Path(__file__).resolve().parent.parent / "web" / "static"
OPTIONAL_ROUTERS = ("maxguard.web.routes", "maxguard.response.routes")

DEFAULT_MAX_UPLOAD_MB = 1024
MIB = 1024 * 1024
CHUNK_BYTES = MIB              # copy uploads in 1 MiB blocks: never the whole file in memory
FORM_OVERHEAD_BYTES = 64 * 1024  # room for the multipart headers around the file
MIN_TOKEN_LENGTH = 32          # secrets.token_urlsafe(32) gives 43 characters
DEFAULT_ALLOWED_HOSTS = "localhost,127.0.0.1,[::1]"  # this machine only

DEFAULT_SENSOR_ID = "sensor"
MAX_FORM_FIELDS = 5             # one file plus a few text fields; Starlette allows 1000
SENSOR_ID_PATTERN = re.compile(r"[A-Za-z0-9._-]{1,64}")
ZIP_MAGIC = b"PK\x03\x04"
GZIP_MAGIC = b"\x1f\x8b"

KEEPALIVE_SECONDS = 15.0   # a comment line now and then stops proxies closing the stream
POLL_SECONDS = 0.5         # how often the stream checks the change counter
CHANGING_METHODS = {"POST", "PUT", "PATCH", "DELETE"}

# The file field, written out for the OpenAPI page (/docs): the upload endpoints
# read the form themselves (see check_ingest_token), so FastAPI cannot see it.
FILE_FIELD = {"type": "string", "format": "binary",
              "description": "a .pcap/.pcapng capture, or a .zip/.tar.gz of Zeek logs"}
UPLOAD_FORM = {"requestBody": {"required": True, "content": {"multipart/form-data": {
    "schema": {"type": "object", "required": ["file"], "properties": {"file": FILE_FIELD}}}}}}
INGEST_FORM = {"requestBody": {"required": True, "content": {"multipart/form-data": {
    "schema": {"type": "object", "required": ["file"], "properties": {
        "file": FILE_FIELD,
        "sensor_id": {"type": "string", "default": DEFAULT_SENSOR_ID,
                      "description": "1-64 characters: letters, digits, '.', '_', '-'"},
    }}}}}}

router = APIRouter()
ingest_router = APIRouter()  # also served alone by create_ingest_app()


# ---------- the app ----------

def create_app(data_dir: str | Path | None = None, *, explain: bool = True) -> FastAPI:
    """Build the app. uvicorn --factory calls it with no arguments.

    data_dir defaults to $MAXGUARD_DATA_DIR, then "data". explain=False skips the AI
    (tests, and machines without Ollama)."""
    app = new_app(data_dir, explain)
    app.include_router(router)
    app.include_router(ingest_router)
    for module_name in OPTIONAL_ROUTERS:
        module = optional_module(module_name)
        if module is not None:
            app.include_router(module.router)
    if STATIC_DIR.is_dir():
        app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    return app


def create_ingest_app(data_dir: str | Path | None = None, *, explain: bool = True) -> FastAPI:
    """Only POST /api/ingest: the app for the port that sensors and agents reach over
    the LAN (docker/compose.lan.yaml). The dashboard and the rest of the API stay on
    127.0.0.1, so nobody on the LAN can read alerts or approve a block.

    Both apps share the data folder. The dashboard shows ingested data at its next
    refresh: GET /api/stream only hears about changes made in its own process."""
    app = new_app(data_dir, explain, docs=False)  # no /docs page on the LAN
    if app.state.ingest_token is None:
        raise ValueError("the ingest app needs MAXGUARD_INGEST_TOKEN (at least 32 characters)")
    app.include_router(ingest_router)
    return app


def new_app(data_dir: str | Path | None, explain: bool, *, docs: bool = True) -> FastAPI:
    """What both apps share: settings and stores on app.state, and the two checks
    that run before any route (unknown host names, cross-site changes)."""
    offline.enable_from_env()  # MAXGUARD_OFFLINE=1 (set in docker/compose.yaml)

    folder = Path(data_dir or os.environ.get("MAXGUARD_DATA_DIR", "data"))
    folder.mkdir(parents=True, exist_ok=True)

    no_docs = {} if docs else {"docs_url": None, "redoc_url": None, "openapi_url": None}
    app = FastAPI(title="MaxGuard", version=__version__,
                  description="Offline network security checks. See docs/ARCHITECTURE.md.",
                  **no_docs)
    app.state.data_dir = folder
    app.state.state_store = StateStore(folder / "state.db")
    app.state.event_store = EventStore(folder / "events")
    app.state.explain = explain
    app.state.max_upload_bytes = max_upload_bytes()
    app.state.keep_uploads = os.environ.get("MAXGUARD_KEEP_UPLOADS") == "1"
    app.state.ingest_token = ingest_token()
    app.state.analysis_lock = threading.Lock()
    app.state.changes = 0      # goes up by one whenever alerts change (see notify_change)
    app.state.keepalive_seconds = KEEPALIVE_SECONDS

    app.middleware("http")(refuse_cross_site_changes)
    # Added last, so it runs first: a request for an unknown host name stops here.
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=allowed_hosts(),
                       www_redirect=False)
    return app


def allowed_hosts() -> list[str]:
    """MAXGUARD_ALLOWED_HOSTS: the names and addresses this console may be reached by,
    comma-separated, without http:// or a port. Default: this machine only. Add the
    console's LAN address (for example 192.168.50.20) when sensors or agents send to it."""
    text = os.environ.get("MAXGUARD_ALLOWED_HOSTS", DEFAULT_ALLOWED_HOSTS)
    hosts = [host.strip().lower() for host in text.split(",") if host.strip()]
    if not hosts:
        raise ValueError("MAXGUARD_ALLOWED_HOSTS is empty: the console would answer no one")
    for host in hosts:
        # "*" would switch the check off; "/" or a port can never match a Host header.
        if "*" in host or "/" in host or (":" in host and not host.startswith("[")):
            raise ValueError("MAXGUARD_ALLOWED_HOSTS: write names or addresses only, "
                             f"without http:// or a port, got {host!r}")
    return hosts


def max_upload_bytes() -> int:
    """MAXGUARD_MAX_UPLOAD_MB (default 1024) in bytes; 1 MB here means 1 MiB."""
    text = os.environ.get("MAXGUARD_MAX_UPLOAD_MB", str(DEFAULT_MAX_UPLOAD_MB))
    if not text.isdigit() or int(text) < 1:
        raise ValueError(
            f"MAXGUARD_MAX_UPLOAD_MB must be a whole number of megabytes, got {text!r}")
    return int(text) * MIB


def ingest_token() -> str | None:
    """The sensor token, or None when ingest is off. A short token is refused at start-up."""
    token = os.environ.get("MAXGUARD_INGEST_TOKEN", "")
    if not token:
        return None
    if len(token) < MIN_TOKEN_LENGTH:
        raise ValueError(
            f"MAXGUARD_INGEST_TOKEN must be at least {MIN_TOKEN_LENGTH} characters; make one with: "
            'python -c "import secrets; print(secrets.token_urlsafe(32))"')
    return token


def optional_module(name: str):
    """Import a module that may not exist yet (the dashboard and the response
    module arrive in later tasks). A module that exists but fails to import still
    raises, so a real bug in it is never hidden."""
    try:
        spec = importlib.util.find_spec(name)
    except ModuleNotFoundError:  # its parent package does not exist either
        return None
    return importlib.import_module(name) if spec else None


def notify_change(app: FastAPI) -> None:
    """Tell open dashboards that alerts changed: /api/stream sends alerts-changed.
    Two threads doing += at the same moment can lose one increment; that is fine,
    because the number still changes, and a change is all the stream looks for."""
    app.state.changes += 1


# ---------- cross-site request check ----------

def is_cross_site(request: Request) -> bool:
    """True when the browser says another website (another origin) started this request.

    Sec-Fetch-Site is set by every browser since 2023 and cannot be set by a page's
    scripts. "same-site" is refused too: another program on 127.0.0.1 with a different
    port counts as the same site. Older browsers send only Origin; "null" never matches."""
    if request.headers.get("sec-fetch-site") in ("cross-site", "same-site"):
        return True
    origin = request.headers.get("origin")
    if origin is None:
        return False  # curl, sensors, agents and tests send no Origin header
    return urlparse(origin).netloc != request.headers.get("host", "")


async def refuse_cross_site_changes(request: Request, call_next):
    if request.method in CHANGING_METHODS and is_cross_site(request):
        return JSONResponse({"detail": "cross-site request refused"}, status_code=403)
    return await call_next(request)


# ---------- uploads and ingest ----------

@router.post("/api/analyses", openapi_extra=UPLOAD_FORM)
async def upload_analysis(request: Request) -> dict:
    """Analyze one uploaded capture or zipped log folder (the dashboard's upload page)."""
    check_content_length(request)
    async with request.form(max_files=1, max_fields=MAX_FORM_FIELDS) as form:
        upload = form_file(form)
        return await run_in_threadpool(receive, request.app, upload, sensor_id=None)


@ingest_router.post("/api/ingest", openapi_extra=INGEST_FORM)
async def ingest(request: Request) -> dict:
    """The same as an upload, for sensors and host agents on the LAN."""
    # Both checks come before the body is read, so a stranger without the token
    # cannot make the console store anything.
    check_ingest_token(request)
    check_content_length(request)
    async with request.form(max_files=1, max_fields=MAX_FORM_FIELDS) as form:
        upload = form_file(form)
        sensor_id = check_sensor_id(form.get("sensor_id", DEFAULT_SENSOR_ID))
        return await run_in_threadpool(receive, request.app, upload, sensor_id=sensor_id)


def check_ingest_token(request: Request) -> None:
    token = request.app.state.ingest_token
    if token is None:
        raise HTTPException(404, "Not Found")  # ingest is off: look like any missing page
    scheme, _, given = request.headers.get("authorization", "").partition(" ")
    # compare_digest takes the same time however many characters match, so the
    # answer time does not help anyone guess the token one character at a time.
    if scheme.lower() != "bearer" or not hmac.compare_digest(given.encode(), token.encode()):
        raise HTTPException(401, "missing or wrong token", headers={"WWW-Authenticate": "Bearer"})


def check_content_length(request: Request) -> None:
    """Refuse an upload that announces itself as too large before reading it."""
    length = request.headers.get("content-length", "")
    if length.isdigit() and int(length) > request.app.state.max_upload_bytes + FORM_OVERHEAD_BYTES:
        raise HTTPException(413, too_large_message(request.app))


def too_large_message(app: FastAPI) -> str:
    return f"file larger than {app.state.max_upload_bytes // MIB} MB (MAXGUARD_MAX_UPLOAD_MB)"


def form_file(form: FormData) -> UploadFile:
    upload = form.get("file")
    if not isinstance(upload, UploadFile):
        raise HTTPException(400, "send the file in a multipart form field named 'file'")
    return upload


def check_sensor_id(value) -> str:
    if not isinstance(value, str) or not SENSOR_ID_PATTERN.fullmatch(value):
        raise HTTPException(400, "sensor_id: 1-64 characters, letters, digits, '.', '_' or '-'")
    return value


def receive(app: FastAPI, upload: UploadFile, *, sensor_id: str | None) -> dict:
    """Save the upload, analyze it, store the results, tell the dashboards.
    Runs in a worker thread: analyze() takes seconds and must not block the server."""
    uploads = app.state.data_dir / "uploads"
    uploads.mkdir(exist_ok=True)
    path = save_upload(upload.file, uploads, app)
    try:
        with app.state.analysis_lock:
            report = run_pipeline(app, path, sensor_id)
    finally:
        if not app.state.keep_uploads:
            path.unlink(missing_ok=True)
    # The generated name is in the report; show the person the name they know.
    # It is only ever displayed, never used as a path.
    report["input"]["name"] = display_name(upload.filename)
    analysis_id = app.state.state_store.save_analysis(report, received_at=time.time())
    app.state.event_store.write(report["events"])
    notify_change(app)
    return {"analysis_id": analysis_id, "findings": len(report["findings"])}


def save_upload(source: BinaryIO, folder: Path, app: FastAPI) -> Path:
    """Copy the upload to folder/<random name><suffix>, in blocks, up to the size limit.

    The suffix comes from the file's first bytes (its "magic number"), because the
    adapters recognise archives by suffix, and the client's file name cannot be trusted."""
    first = source.read(CHUNK_BYTES)
    path = folder / (secrets.token_hex(16) + suffix_for(first))
    size = 0
    with path.open("wb") as out:
        block = first
        while block:
            size += len(block)
            if size > app.state.max_upload_bytes:
                out.close()
                path.unlink()
                raise HTTPException(413, too_large_message(app))
            out.write(block)
            block = source.read(CHUNK_BYTES)
    return path


def suffix_for(head: bytes) -> str:
    if head[:4] in PCAP_MAGIC:
        return ".pcap"
    if head.startswith(ZIP_MAGIC):
        return ".zip"
    if head.startswith(GZIP_MAGIC):
        return ".tar.gz"  # a gzip file that is not a tar archive fails later with 400
    return ""  # unknown: the pipeline refuses it (400)


def display_name(filename: str | None) -> str:
    """'C:\\captures\\..\\shop.pcap' -> 'shop.pcap': last part only, safe characters only."""
    last = (filename or "").replace("\\", "/").rsplit("/", 1)[-1]
    cleaned = re.sub(r"[^A-Za-z0-9._ -]", "_", last).strip(" .")
    return cleaned[:100] or "upload"


def run_pipeline(app: FastAPI, path: Path, sensor_id: str | None) -> dict:
    """analyze() in a temporary work folder inside the data folder, errors -> HTTP codes."""
    work = app.state.data_dir / "work"
    work.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=work) as workdir:
        try:
            return analyze(path, workdir, explain=app.state.explain, sensor_id=sensor_id)
        except UnsupportedInput:
            raise HTTPException(
                400, "not a .pcap/.pcapng capture or a .zip/.tar.gz of Zeek logs") from None
        except ArchiveTooLarge as err:
            raise HTTPException(413, str(err)) from None
        except (zipfile.BadZipFile, tarfile.TarError, EOFError) as err:
            raise HTTPException(400, f"not a valid archive: {err}") from None
        except (ZeekError, SuricataError) as err:
            raise HTTPException(422, str(err)) from None


# ---------- reading ----------

@router.get("/api/analyses")
def list_analyses(request: Request, limit: int = Query(50, ge=1, le=1000)) -> list[dict]:
    return request.app.state.state_store.list_analyses(limit=limit)


@router.get("/api/analyses/{analysis_id}")
def get_analysis(request: Request, analysis_id: str) -> dict:
    report = request.app.state.state_store.get_analysis(analysis_id)
    if report is None:
        raise HTTPException(404, f"no analysis {analysis_id}")
    return report


@router.get("/api/alerts")
def list_alerts(request: Request, status: str | None = None, severity: str | None = None,
                limit: int = Query(200, ge=1, le=1000)) -> list[dict]:
    """The alert queue, most severe first."""
    try:
        return request.app.state.state_store.list_alerts(status=status, severity=severity,
                                                         limit=limit)
    except ValueError as err:  # unknown status or severity
        raise HTTPException(400, str(err)) from None


@router.get("/api/alerts/{finding_id}")
def get_alert(request: Request, finding_id: str) -> dict:
    alert = request.app.state.state_store.get_alert(finding_id)
    if alert is None:
        raise HTTPException(404, f"no alert {finding_id}")
    return alert


class AlertUpdate(BaseModel):
    actor: str = Field(min_length=1, max_length=100)  # who made the change (audit trail)
    status: str | None = None
    assignee: str | None = Field(default=None, max_length=100)


@router.patch("/api/alerts/{finding_id}")
def update_alert(request: Request, finding_id: str, change: AlertUpdate) -> dict:
    """Change an alert's status and/or assignee; StateStore writes the audit row."""
    try:
        alert = request.app.state.state_store.update_alert(
            finding_id, actor=change.actor, at=time.time(),
            status=change.status, assignee=change.assignee)
    except KeyError:
        raise HTTPException(404, f"no alert {finding_id}") from None
    except ValueError as err:  # unknown status
        raise HTTPException(400, str(err)) from None
    notify_change(request.app)
    return alert


@router.get("/api/events")
def list_events(request: Request, ip: str | None = None, since: float | None = None,
                until: float | None = None,
                limit: int = Query(1000, ge=1, le=10000)) -> list[dict]:
    """Timeline events in time order; ip matches the source or the destination."""
    if ip is not None:
        try:
            ip = str(ipaddress.ip_address(ip))  # also writes IPv6 the way Zeek does
        except ValueError:
            raise HTTPException(400, f"not an IP address: {ip!r}") from None
    return request.app.state.event_store.query(ip=ip, since=since, until=until, limit=limit)


@router.get("/api/assets")
def list_assets(request: Request) -> list[dict]:
    """The asset inventory of the newest analysis."""
    store = request.app.state.state_store
    newest = store.list_analyses(limit=1)
    if not newest:
        return []
    return store.get_analysis(newest[0]["analysis_id"])["assets"]


@router.get("/api/audit")
def list_audit(request: Request, limit: int = Query(200, ge=1, le=1000)) -> list[dict]:
    return request.app.state.state_store.list_audit(limit=limit)


# ---------- live updates ----------

@router.get("/api/stream")
async def stream(request: Request, max_events: int | None = Query(None, ge=1)):
    """Server-sent events: alerts-changed when alerts change, a comment line in between.

    The first event is sent at once: a dashboard that reconnects may have missed a
    change, so it refreshes once to catch up. max_events ends the stream after that
    many events (tests use it; browsers never send it)."""
    return StreamingResponse(alert_events(request.app, max_events),
                             media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache",
                                      "X-Accel-Buffering": "no"})  # nginx: do not buffer


async def alert_events(app: FastAPI, max_events: int | None) -> AsyncIterator[str]:
    sent = 0
    last = None
    quiet = 0.0
    while max_events is None or sent < max_events:
        if app.state.changes != last:
            last = app.state.changes
            sent += 1
            quiet = 0.0
            yield f"event: alerts-changed\ndata: {last}\n\n"
            continue
        await asyncio.sleep(POLL_SECONDS)
        quiet += POLL_SECONDS
        if quiet >= app.state.keepalive_seconds:
            quiet = 0.0
            yield ": keep-alive\n\n"
