"""Send each finished interval folder of a live sensor to the console (Jakub, JAK-07).

It runs on the sensor, in its own container (docker/sensor-compose.yaml):

    python3 -m maxguard.sensor.shipper --data /data --interval-minutes 15

Every minute it:
1. finds the interval folders under /data/zeek that are complete and not shipped
   yet, oldest first (maxguard/adapters/live.py decides what "complete" means);
2. merges that interval's Suricata minute files into the folder's eve.json;
3. packs the folder as a .tar.gz and POSTs it to <console>/api/ingest with the
   header "Authorization: Bearer <token>" and the form field sensor_id;
4. marks the folder shipped (a hidden ".shipped" file) only after a 2xx answer.
   After any failure it stops and tries again on the next round, so a console
   that is down only delays folders, and a shipped folder is never sent again;
5. deletes shipped folders whose interval started more than 7 days ago.

The console's address and token come from /data/shipper.toml on the sensor,
never from the repository (CLAUDE.md rule 6). Shipping is the sensor's only
network traffic: it goes out of the management port, only to the console the
user configured, and never through a proxy (CLAUDE.md rules 1 and 5).

Only main() reads the clock; every other function takes `now` (Unix seconds),
so the tests can say exactly which folders are ready. Like live.py, this module
uses only Python's standard library.
"""

from __future__ import annotations

import argparse
import gzip
import http.client
import io
import logging
import re
import secrets
import shutil
import ssl
import tarfile
import time
import tomllib
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from maxguard.adapters.live import (
    EVE_DIR,
    ZEEK_DIR,
    check_interval,
    completed_folders,
    folder_start,
    interval_folders,
    interval_minutes_from_env,
    merge_eve,
    part_start,
)

CONFIG_NAME = "shipper.toml"   # in the data folder, e.g. /data/shipper.toml
SHIPPED_MARKER = ".shipped"    # hidden, so it is never packed
KEEP_DAYS = 7                  # ARCHITECTURE.md section 4: 7 days on the sensor
LOOP_SECONDS = 60
# The console analyzes the folder before it answers, and explaining the findings
# with a local AI model can take minutes on a small machine.
POST_TIMEOUT_SECONDS = 900
SENSOR_ID = re.compile(r"[A-Za-z0-9._-]{1,64}")  # exactly what POST /api/ingest accepts

log = logging.getLogger("maxguard.shipper")


class ConfigError(ValueError):
    """shipper.toml is missing a setting or has a wrong one."""


@dataclass(frozen=True)
class ShipperConfig:
    console_url: str             # "http://192.168.50.20:8001", no trailing slash
    token: str                   # the console's MAXGUARD_INGEST_TOKEN
    sensor_id: str               # this sensor's name, e.g. "sensor-01"
    ca_file: str | None = None   # only for an https:// console with its own certificate


def load_config(path: Path) -> ShipperConfig:
    """Read shipper.toml (TOML: one `key = "value"` per line, # starts a comment)."""
    with path.open("rb") as f:
        raw = tomllib.load(f)
    url = str(raw.get("console_url", "")).rstrip("/")
    if not url.startswith(("http://", "https://")):
        raise ConfigError(f"{path}: console_url must start with http:// or https://")
    token = str(raw.get("token", ""))
    if not token:
        raise ConfigError(f"{path}: token is empty; copy the console's MAXGUARD_INGEST_TOKEN")
    sensor_id = str(raw.get("sensor_id", ""))
    if not SENSOR_ID.fullmatch(sensor_id):
        raise ConfigError(f"{path}: sensor_id must be 1-64 letters, digits, '.', '_' or '-'")
    ca_file = raw.get("ca_file")
    return ShipperConfig(url, token, sensor_id, str(ca_file) if ca_file else None)


# ---------- which folders, and remembering what was shipped ----------

def is_shipped(folder: Path) -> bool:
    return (folder / SHIPPED_MARKER).exists()


def mark_shipped(folder: Path, now: float) -> None:
    """Remember that the console accepted this folder (and when, for people)."""
    (folder / SHIPPED_MARKER).write_text(f"{now:.0f}\n")


def folders_to_ship(data_dir: Path, now: float, interval_minutes: int) -> list[Path]:
    """Complete folders the console has not accepted yet, oldest first."""
    done = completed_folders(data_dir / ZEEK_DIR, now, interval_minutes)
    return [folder for folder in done if not is_shipped(folder)]


# ---------- packing and sending ----------

def without_owner(info: tarfile.TarInfo) -> tarfile.TarInfo:
    """Leave the sensor's user and group names out of the archive."""
    info.uid = info.gid = 0
    info.uname = info.gname = ""
    return info


def pack_folder(folder: Path) -> bytes:
    """The folder as .tar.gz bytes (2026-10-06-1415/conn.log, ...), hidden files left out.

    Packing the same folder twice gives the same bytes (sorted names, no owner,
    gzip time 0). If the sensor crashes after sending but before writing
    .shipped, the folder is sent again, and the console sees the same SHA-256
    and does not count its alerts twice.
    """
    buffer = io.BytesIO()
    with gzip.GzipFile(fileobj=buffer, mode="wb", mtime=0) as gz:
        with tarfile.open(fileobj=gz, mode="w") as tar:
            for path in sorted(folder.iterdir()):
                if path.is_file() and not path.name.startswith("."):
                    tar.add(path, arcname=f"{folder.name}/{path.name}", filter=without_owner)
    return buffer.getvalue()


def multipart_body(fields: dict[str, str], file_name: str, data: bytes,
                   boundary: str) -> bytes:
    """Text fields plus one file as multipart/form-data (RFC 7578), the format a
    browser uses to upload a file, and the one the console's /api/ingest reads."""
    text = ""
    for name, value in fields.items():
        text += (f"--{boundary}\r\n"
                 f'Content-Disposition: form-data; name="{name}"\r\n\r\n'
                 f"{value}\r\n")
    text += (f"--{boundary}\r\n"
             f'Content-Disposition: form-data; name="file"; filename="{file_name}"\r\n'
             "Content-Type: application/gzip\r\n\r\n")
    return text.encode() + data + f"\r\n--{boundary}--\r\n".encode()


def opener(config: ShipperConfig) -> urllib.request.OpenerDirector:
    """An HTTP client that never uses a proxy: the logs and the token go straight
    to the console. https:// checks the certificate (with ca_file when given)."""
    context = ssl.create_default_context(cafile=config.ca_file)
    return urllib.request.build_opener(urllib.request.ProxyHandler({}),
                                       urllib.request.HTTPSHandler(context=context))


def post_archive(config: ShipperConfig, file_name: str, data: bytes,
                 timeout: float = POST_TIMEOUT_SECONDS) -> int:
    """POST one archive to <console>/api/ingest and return the HTTP status code.

    A console that cannot be reached raises OSError (connection refused, timeout)."""
    boundary = secrets.token_hex(16)
    request = urllib.request.Request(
        config.console_url + "/api/ingest", method="POST",
        data=multipart_body({"sensor_id": config.sensor_id}, file_name, data, boundary),
        headers={"Authorization": f"Bearer {config.token}",
                 "Content-Type": f"multipart/form-data; boundary={boundary}"})
    try:
        with opener(config).open(request, timeout=timeout) as response:
            return response.status
    except urllib.error.HTTPError as err:  # the console answered, with 4xx or 5xx
        err.close()
        return err.code


def ship_folder(folder: Path, data_dir: Path, config: ShipperConfig,
                interval_minutes: int, now: float) -> bool:
    """Merge, pack, send and mark one folder. True when the console answered 2xx."""
    merge_eve(folder, data_dir / EVE_DIR, interval_minutes)
    data = pack_folder(folder)
    try:
        status = post_archive(config, f"{folder.name}.tar.gz", data)
    except (OSError, http.client.HTTPException) as err:
        log.warning("%s: console not reachable (%s); will retry", folder.name, err)
        return False
    if not 200 <= status < 300:
        log.warning("%s: console answered HTTP %d; will retry", folder.name, status)
        return False
    mark_shipped(folder, now)
    log.info("%s: shipped (%d bytes, HTTP %d)", folder.name, len(data), status)
    return True


def ship_ready_folders(data_dir: Path, config: ShipperConfig, interval_minutes: int,
                       now: float) -> list[str]:
    """Ship every ready folder, oldest first; stop at the first failure."""
    shipped = []
    for folder in folders_to_ship(data_dir, now, interval_minutes):
        if not ship_folder(folder, data_dir, config, interval_minutes, now):
            break  # the console is down or refusing: keep the order, retry next round
        shipped.append(folder.name)
    return shipped


# ---------- retention ----------

def prune(data_dir: Path, now: float, keep_days: int = KEEP_DAYS) -> list[str]:
    """Delete shipped folders, and leftover Suricata minute files, older than keep_days.

    A folder that was never shipped is kept, so a console that was down for a
    week loses nothing; watch the disk if a sensor has no console."""
    cutoff = now - keep_days * 86400
    deleted = []
    for folder in interval_folders(data_dir / ZEEK_DIR):
        if is_shipped(folder) and folder_start(folder.name) < cutoff:
            shutil.rmtree(folder)
            deleted.append(folder.name)
    eve_dir = data_dir / EVE_DIR
    if eve_dir.is_dir():
        for part in sorted(eve_dir.iterdir()):
            minute = part_start(part)
            if minute is not None and minute < cutoff:  # no Zeek folder ever claimed it
                part.unlink()
                deleted.append(part.name)
    return deleted


# ---------- one round, and the loop ----------

def run_once(data_dir: Path, interval_minutes: int, now: float) -> dict:
    """Ship what is ready, then delete what is old. Returns what happened."""
    shipped: list[str] = []
    config_path = data_dir / CONFIG_NAME
    try:
        config = load_config(config_path)
    except FileNotFoundError:
        log.warning("%s not found: folders stay on the sensor until it exists", config_path)
    except (ConfigError, tomllib.TOMLDecodeError) as err:
        log.error("%s", err)
    else:
        shipped = ship_ready_folders(data_dir, config, interval_minutes, now)
    return {"shipped": shipped, "deleted": prune(data_dir, now)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Send finished interval folders to the MaxGuard console.")
    parser.add_argument("--data", type=Path, default=Path("/data"),
                        help="the sensor's data folder (default: /data)")
    parser.add_argument("--interval-minutes", type=int, default=None,
                        help="the same interval Zeek rotates with "
                             "(default: $MAXGUARD_INTERVAL_MINUTES, else 15)")
    parser.add_argument("--once", action="store_true", help="run one round, then exit")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    if args.interval_minutes is None:
        interval = interval_minutes_from_env()
    else:
        interval = check_interval(args.interval_minutes)
    log.info("shipping complete %d-minute folders from %s", interval, args.data / ZEEK_DIR)
    while True:
        run_once(args.data, interval, now=time.time())  # the only place that reads the clock
        if args.once:
            return 0
        time.sleep(LOOP_SECONDS)


if __name__ == "__main__":
    raise SystemExit(main())
