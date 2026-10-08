"""Host agent: capture this computer's own traffic and upload it (Jakub, JAK-11).

For a home with no mirror port. The agent runs on one computer, captures only
that computer's traffic with the operating system's built-in tools (no extra
driver), writes one capture file per interval, and uploads every finished file
to the console's POST /api/ingest (the LAN port 8001, docker/compose.lan.yaml).

    sudo python -m maxguard.sensor.agent --config ~/.config/maxguard/agent.toml

Safety rules:
- The console must be YOUR OWN computer running MaxGuard. The agent sends your
  traffic to it, so never point console_url at anyone else's machine.
- Ingest is off on the console unless MAXGUARD_INGEST_TOKEN is set there
  (POST /api/ingest answers 404); the agent's token must be the same value.
- The token lives in a config file outside the repository (default
  ~/.config/maxguard/agent.toml, or %APPDATA%\\MaxGuard\\agent.toml on Windows),
  and the agent refuses a config file other users can read.
- The capture only listens (CLAUDE.md rule 5). Port 8001 is plain HTTP, so the
  token and the captures cross your LAN unencrypted: use a wired or trusted network.
- The upload goes straight to console_url: proxy variables (HTTP_PROXY ...) and
  ~/.netrc are ignored, so your traffic never leaves through a proxy (rule 1).

Capture commands, every flag checked against the manuals:
- Linux and macOS: tcpdump (tcpdump(1), https://www.tcpdump.org/manpages/tcpdump.1.html)
    -i <interface>  capture on this interface (left out: tcpdump picks the lowest
                    numbered interface that is up, not loopback)
    -n              do not turn addresses into names (no DNS lookups of its own)
    -G <seconds>    rotate the file given with -w every <seconds> seconds
    -w <pattern>    write raw packets to a file; with -G the name is a strftime(3)
                    pattern, e.g. capture-%Y%m%d-%H%M%S.pcap
    -Z <user>       after opening the capture device, but before opening any
                    output file, drop root and run as <user>. So the files belong to
                    <user>, and <user> must be able to write the spool folder.
  tcpdump fills the time pattern with localtime(); the agent starts it with TZ=UTC
  so the names are UTC and sort in time order all year (no daylight saving jumps).
  tcpdump starts the next file only when a packet arrives after the interval, so
  the newest file is always the one still being written: it is never uploaded.
- Windows: pktmon (built in since Windows 10 1809; run as Administrator)
    https://learn.microsoft.com/windows-server/administration/windows-commands/pktmon-start
    https://learn.microsoft.com/windows-server/administration/windows-commands/pktmon-etl2pcap
    pktmon start --capture --comp nics --pkt-size 0 --file-name <file.etl>
        --capture: capture packets; --comp nics: only at the network cards (pktmon
        otherwise logs a packet once for every component it passes through);
        --pkt-size 0: the whole packet (the default keeps only 128 bytes)
    pktmon stop
    pktmon etl2pcap <file.etl> --out <file.pcapng>
  pktmon rotates only by size, not by time, so the agent stops and restarts it
  every interval; a stopped .etl file is finished and is converted to pcapng.
  pktmon's default log mode is "circular" with a 512 MB file (--file-size): if
  one interval holds more than that, its oldest packets are overwritten.
"""

from __future__ import annotations

import argparse
import os
import platform
import re
import shutil
import stat
import subprocess
import sys
import time
import tomllib
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import requests

SENSOR_ID = re.compile(r"[A-Za-z0-9._-]{1,64}")  # what POST /api/ingest accepts
CAPTURE_PATTERN = "capture-%Y%m%d-%H%M%S"        # strftime pattern; UTC
UPLOAD_TIMEOUT = (10, 600)  # seconds to connect, seconds to wait for the analysis
CHECK_EVERY = 10            # seconds between looks at the spool folder (Linux, macOS)
KEEP_UPLOADED = 4           # uploaded files kept on this computer, newest first
UPLOADED_DIR = "uploaded"   # inside the spool folder
REJECTED_DIR = "rejected"   # files the console refused: not sent again
REJECTED_STATUSES = (400, 413, 422)  # answers that will be the same next time


@dataclass
class AgentConfig:
    console_url: str          # e.g. "http://192.168.50.20:8001" (your own console)
    token: str                # the console's MAXGUARD_INGEST_TOKEN
    spool_dir: Path           # where capture files wait for upload
    sensor_id: str = "agent"  # this computer's name in every event
    interface: str = ""       # "" = the capture tool's default
    rotate_seconds: int = 900  # 15 minutes, like the live sensor
    capture_user: str = ""    # tcpdump -Z: who owns the files (Linux, macOS)


# ---------- Config file ----------

def default_config_path() -> Path:
    """Outside the repository, in the user's own settings folder."""
    if platform.system() == "Windows":
        return Path(os.environ.get("APPDATA", Path.home())) / "MaxGuard" / "agent.toml"
    return Path.home() / ".config" / "maxguard" / "agent.toml"


def check_private(path: Path) -> None:
    """The file holds the token: refuse it if other users may read it (Linux, macOS)."""
    if platform.system() == "Windows":
        return  # Windows uses ACLs, not mode bits; %APPDATA% is private by default
    if path.stat().st_mode & (stat.S_IRWXG | stat.S_IRWXO):
        raise ValueError(f"{path} can be read by other users: run  chmod 600 {path}")


def load_config(path: Path) -> AgentConfig:
    check_private(path)
    with path.open("rb") as f:
        raw = tomllib.load(f)
    config = AgentConfig(
        console_url=str(raw["console_url"]).rstrip("/"),
        token=str(raw["token"]),
        spool_dir=Path(raw["spool_dir"]).expanduser(),
        sensor_id=str(raw.get("sensor_id", "agent")),
        interface=str(raw.get("interface", "")),
        rotate_seconds=int(raw.get("rotate_seconds", 900)),
        capture_user=str(raw.get("capture_user", "")),
    )
    check_config(config)
    return config


def check_config(config: AgentConfig) -> None:
    if not config.console_url.startswith(("http://", "https://")):
        raise ValueError("console_url must start with http:// or https://")
    if not SENSOR_ID.fullmatch(config.sensor_id):
        raise ValueError("sensor_id: 1-64 characters, letters, digits, '.', '_' or '-'")
    if not config.token:
        raise ValueError("token is empty: copy the console's MAXGUARD_INGEST_TOKEN")
    if config.rotate_seconds < 60:
        raise ValueError("rotate_seconds must be at least 60")


# ---------- Capture commands ----------

def tcpdump_command(config: AgentConfig) -> list[str]:
    """Linux and macOS. Run it with TZ=UTC in its environment (see capture_env)."""
    if not config.capture_user:
        raise ValueError("set capture_user: tcpdump -Z drops root to that user")
    command = ["tcpdump"]
    if config.interface:
        command += ["-i", config.interface]
    # tcpdump runs the WHOLE -w name through strftime, so a "%" in the folder
    # name must be written "%%" to stay a plain "%".
    folder = str(config.spool_dir).replace("%", "%%")
    pattern = f"{folder}{os.sep}{CAPTURE_PATTERN}.pcap"
    command += ["-n", "-G", str(config.rotate_seconds), "-w", pattern,
                "-Z", config.capture_user]
    return command


def capture_env() -> dict[str, str]:
    """tcpdump fills the file name with local time: make that UTC."""
    return {**os.environ, "TZ": "UTC"}


def pktmon_start_command(etl_file: Path) -> list[str]:
    return ["pktmon", "start", "--capture", "--comp", "nics", "--pkt-size", "0",
            "--file-name", str(etl_file)]


def pktmon_stop_command() -> list[str]:
    return ["pktmon", "stop"]


def pktmon_convert_command(etl_file: Path) -> list[str]:
    return ["pktmon", "etl2pcap", str(etl_file), "--out", str(etl_file.with_suffix(".pcapng"))]


def capture_command(system: str, config: AgentConfig, now: float) -> list[str]:
    """The command that starts the capture on this operating system (platform.system())."""
    if system in ("Linux", "Darwin"):
        return tcpdump_command(config)
    if system == "Windows":
        return pktmon_start_command(etl_name(config.spool_dir, now))
    raise ValueError(f"no built-in capture tool known for {system!r}")


def etl_name(spool_dir: Path, now: float) -> Path:
    stamp = datetime.fromtimestamp(now, UTC).strftime(CAPTURE_PATTERN)
    return spool_dir / f"{stamp}.etl"


# ---------- Which files are finished ----------

def finished_files(spool_dir: Path, *, capture_running: bool) -> list[Path]:
    """Capture files that are complete, oldest first.

    The names are UTC times, so sorting by name sorts by time. While the capture
    runs, the newest file is still being written: never upload it."""
    files = sorted(p for p in spool_dir.glob("capture-*") if p.suffix in (".pcap", ".pcapng"))
    if capture_running and files:
        files = files[:-1]
    return files


# ---------- Upload ----------

def console_session() -> requests.Session:
    """A requests session that talks only to console_url.

    trust_env=False: requests would otherwise send the upload through a proxy named
    in HTTP_PROXY/HTTPS_PROXY, and replace our Bearer header with a password from
    ~/.netrc. Both were seen in a test; neither may happen to your captures."""
    session = requests.Session()
    session.trust_env = False
    return session


def upload(path: Path, config: AgentConfig, session=None) -> int | None:
    """POST one file to the console. Returns the HTTP status, or None if unreachable."""
    session = session or console_session()
    url = f"{config.console_url}/api/ingest"
    headers = {"Authorization": f"Bearer {config.token}"}
    try:
        with path.open("rb") as f:
            reply = session.post(url, headers=headers, data={"sensor_id": config.sensor_id},
                                 files={"file": (path.name, f, "application/octet-stream")},
                                 timeout=UPLOAD_TIMEOUT)
    except requests.RequestException as err:
        print(f"console not reachable, will retry {path.name}: {err}", file=sys.stderr)
        return None
    return reply.status_code


def upload_finished(config: AgentConfig, *, capture_running: bool, session=None) -> int:
    """Upload every finished file. Returns how many the console accepted.

    A file counts as uploaded only after a 2xx answer; then it moves to uploaded/.
    400 (not a capture), 413 (too large) and 422 (Zeek or Suricata failed on this
    file) will never work: the file moves to rejected/, so one bad file cannot
    block every later one. Anything else (console down, 401 wrong token, 5xx) is
    tried again later."""
    session = session or console_session()
    accepted = 0
    for path in finished_files(config.spool_dir, capture_running=capture_running):
        status = upload(path, config, session)
        if status is not None and 200 <= status < 300:
            move_into(path, config.spool_dir / UPLOADED_DIR)
            accepted += 1
        elif status in REJECTED_STATUSES:
            print(f"console refused {path.name} ({status}): moved to {REJECTED_DIR}/",
                  file=sys.stderr)
            move_into(path, config.spool_dir / REJECTED_DIR)
        else:
            if status is not None:
                print(f"upload of {path.name} failed ({status}), will retry", file=sys.stderr)
            break  # keep the order: try the oldest file again next time
    prune_uploaded(config.spool_dir / UPLOADED_DIR)
    return accepted


def move_into(path: Path, folder: Path) -> Path:
    folder.mkdir(exist_ok=True)
    return path.replace(folder / path.name)


def prune_uploaded(folder: Path, keep: int = KEEP_UPLOADED) -> None:
    """The console has the data now; keep only the newest few files here."""
    if not folder.is_dir():
        return
    files = sorted(p for p in folder.iterdir() if p.is_file())
    for old in files[:-keep] if keep else files:
        old.unlink()


# ---------- Main loops (they start a real capture: never called by tests) ----------

def prepare_spool(config: AgentConfig, system: str) -> None:
    """Create the spool folder if it is missing.

    tcpdump -Z writes the files as capture_user, but the agent runs as root (sudo),
    so a folder it creates would belong to root and tcpdump could not write into
    it. A folder the agent creates is therefore given to capture_user. An existing
    folder is never changed: it may be shared, and it is yours to set up."""
    if config.spool_dir.is_dir():
        return
    config.spool_dir.mkdir(parents=True)
    if system in ("Linux", "Darwin") and config.capture_user and os.geteuid() == 0:
        shutil.chown(config.spool_dir, user=config.capture_user)


def run_tcpdump(config: AgentConfig) -> int:
    """Capture and upload until tcpdump stops. Returns tcpdump's exit code.

    Not 0 means tcpdump could not capture (it printed why, for example a spool
    folder capture_user cannot write)."""
    capture = subprocess.Popen(tcpdump_command(config), env=capture_env())
    try:
        while capture.poll() is None:
            upload_finished(config, capture_running=True)
            time.sleep(CHECK_EVERY)
    finally:
        capture.terminate()  # SIGTERM: tcpdump closes the current file cleanly
        capture.wait()
        upload_finished(config, capture_running=False)
    return capture.returncode


def run_pktmon(config: AgentConfig) -> None:
    while True:
        etl_file = etl_name(config.spool_dir, time.time())
        subprocess.run(pktmon_start_command(etl_file), check=True)
        try:
            time.sleep(config.rotate_seconds)
        finally:
            subprocess.run(pktmon_stop_command(), check=True)
            convert_etl(etl_file)
        upload_finished(config, capture_running=False)


def convert_etl(etl_file: Path) -> None:
    """ETL -> pcapng (MaxGuard reads pcapng), then delete the ETL file."""
    subprocess.run(pktmon_convert_command(etl_file), check=True)
    etl_file.unlink()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="MaxGuard host agent (capture + upload)")
    parser.add_argument("--config", type=Path, default=default_config_path())
    parser.add_argument("--upload-only", action="store_true",
                        help="upload every capture file once and exit (no capture); "
                             "only while the agent is stopped, because it also sends "
                             "the newest file")
    args = parser.parse_args(argv)
    config = load_config(args.config)
    system = platform.system()
    prepare_spool(config, system)
    if args.upload_only:
        print(f"uploaded {upload_finished(config, capture_running=False)} file(s)")
        return 0
    if system == "Windows":
        run_pktmon(config)
    elif system in ("Linux", "Darwin"):
        return run_tcpdump(config)
    else:
        print(f"no built-in capture tool known for {system}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
