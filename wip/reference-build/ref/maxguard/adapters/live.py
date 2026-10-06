"""LiveSensorAdapter: the newest finished interval of a live sensor (Jakub, JAK-07).

The live sensor (docker/sensor-compose.yaml) keeps everything in one data
folder, /data on the sensor's SSD:

    /data/zeek/2026-10-06-1415/   one folder per interval, named after its start
                                  in UTC (maxguard/zeek/scripts/live/rotate.zeek)
    /data/spool/zeek/             Zeek's logs of the interval in progress
    /data/spool/suricata/         Suricata's events, one file per minute:
                                  eve-2026-10-06-1415.json, eve-2026-10-06-1416.json, ...

An interval folder is *complete* when its interval has ended and SETTLE_SECONDS
more have passed. By then Zeek has moved every log into it, and Suricata has
closed the last minute file that belongs to it. merge_eve() then joins that
interval's minute files into one eve.json inside the folder, so the folder
holds everything MaxGuard needs, like a folder made from a capture file.

The shipper (maxguard/sensor/shipper.py) uses the same functions before it
sends a folder to the console. This module uses only Python's standard library,
because the shipper runs in the zeek/zeek:9.0.0 image with nothing installed.
"""

from __future__ import annotations

import os
import re
import shutil
import tempfile
import time
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path

from maxguard.adapters.zeeklogs import ZeekLogAdapter

ZEEK_DIR = Path("zeek")                 # inside the data folder
EVE_DIR = Path("spool") / "suricata"    # inside the data folder
FOLDER_FORMAT = "%Y-%m-%d-%H%M"         # 2026-10-06-1415, always UTC
FOLDER_NAME = re.compile(r"\d{4}-\d{2}-\d{2}-\d{4}")
EVE_PART_NAME = re.compile(r"eve-(\d{4}-\d{2}-\d{2}-\d{4})\.json")
DEFAULT_INTERVAL_MINUTES = 15
# Suricata starts a new minute file with the first event after the minute ends,
# so the last minute file of an interval can still grow for up to a minute after
# the interval ends. Two minutes covers that, plus Zeek moving its logs.
SETTLE_SECONDS = 120


class NoCompletedInterval(RuntimeError):
    """The sensor has not finished any interval yet."""


def check_interval(minutes: int) -> int:
    """The interval must divide an hour evenly, like Zeek's rotation times do."""
    if minutes < 1 or 60 % minutes != 0:
        raise ValueError(f"interval must be 1, 2, 3, 4, 5, 6, 10, 12, 15, 20, 30 or 60 "
                         f"minutes, got {minutes}")
    return minutes


def interval_minutes_from_env() -> int:
    """MAXGUARD_INTERVAL_MINUTES (default 15): the same value Zeek rotates with."""
    text = os.environ.get("MAXGUARD_INTERVAL_MINUTES", str(DEFAULT_INTERVAL_MINUTES))
    if not text.isdigit():
        raise ValueError(f"MAXGUARD_INTERVAL_MINUTES must be a whole number, got {text!r}")
    return check_interval(int(text))


def folder_start(name: str) -> float:
    """'2026-10-06-1415' -> the Unix time of 14:15:00 UTC on that day."""
    return datetime.strptime(name, FOLDER_FORMAT).replace(tzinfo=UTC).timestamp()


def folder_name(start: float) -> str:
    """The opposite of folder_start(): a Unix time -> '2026-10-06-1415'."""
    return datetime.fromtimestamp(start, UTC).strftime(FOLDER_FORMAT)


def interval_folders(zeek_dir: Path) -> list[Path]:
    """Every interval folder, oldest first (the names sort in time order)."""
    if not zeek_dir.is_dir():
        return []
    return sorted(p for p in zeek_dir.iterdir() if p.is_dir() and FOLDER_NAME.fullmatch(p.name))


def is_complete(folder: Path, now: float, interval_minutes: int) -> bool:
    """True once the folder's interval ended at least SETTLE_SECONDS before now."""
    end = folder_start(folder.name) + interval_minutes * 60
    return now >= end + SETTLE_SECONDS


def completed_folders(zeek_dir: Path, now: float, interval_minutes: int) -> list[Path]:
    """The interval folders that are complete, oldest first."""
    return [f for f in interval_folders(zeek_dir) if is_complete(f, now, interval_minutes)]


def part_start(part: Path) -> float | None:
    """'eve-2026-10-06-1416.json' -> the Unix time of 14:16 UTC; None for other files."""
    match = EVE_PART_NAME.fullmatch(part.name)
    return folder_start(match.group(1)) if match else None


def eve_parts(eve_dir: Path, folder: Path, interval_minutes: int) -> list[Path]:
    """Suricata's minute files whose minute lies inside the folder's interval, in order."""
    start = folder_start(folder.name)
    end = start + interval_minutes * 60
    if not eve_dir.is_dir():
        return []
    parts = []
    for path in sorted(eve_dir.iterdir()):  # the names sort in time order
        minute = part_start(path)
        if minute is not None and start <= minute < end:
            parts.append(path)
    return parts


def merge_eve(folder: Path, eve_dir: Path, interval_minutes: int) -> None:
    """Join the interval's minute files into folder/eve.json, then delete them.

    Call it only for a complete folder. It is safe to run again after a crash:
    eve.json appears in one step (written to a hidden file first, then renamed),
    and once it exists it is never written again, so no event is added twice.
    """
    parts = eve_parts(eve_dir, folder, interval_minutes)
    target = folder / "eve.json"
    if parts and not target.exists():
        # Hidden (starts with "."), so nothing reads or ships a half-written file.
        with tempfile.NamedTemporaryFile(dir=folder, prefix=".eve-", suffix=".partial",
                                         delete=False) as out:
            for part in parts:
                with part.open("rb") as src:
                    shutil.copyfileobj(src, out)
        os.chmod(out.name, 0o644)  # readable by every user, like Zeek's own logs
        Path(out.name).replace(target)  # a rename on one disk is all-or-nothing
    for part in parts:  # merged now, or on an earlier run that stopped halfway
        part.unlink(missing_ok=True)


class LiveSensorAdapter:
    """Contract 3 adapter for a live sensor's data folder (for example /data).

    accepts() is true only for a folder that has zeek/<YYYY-MM-DD-HHMM>/ folders
    inside and no conn.log of its own, so it never takes a plain Zeek log folder
    away from ZeekLogAdapter (and ZeekLogAdapter never takes a sensor folder).
    """

    name = "live"

    def __init__(self, interval_minutes: int | None = None,
                 clock: Callable[[], float] = time.time) -> None:
        if interval_minutes is None:
            self.interval_minutes = interval_minutes_from_env()
        else:
            self.interval_minutes = check_interval(interval_minutes)
        self.clock = clock  # tests pass a fixed time; on a sensor it is the real clock

    def accepts(self, path: Path) -> bool:
        if not path.is_dir() or (path / "conn.log").exists():
            return False
        return bool(interval_folders(path / ZEEK_DIR))

    def to_zeek_logs(self, path: Path, workdir: Path) -> Path:
        """Copy the newest complete interval (never the one still being written)."""
        done = completed_folders(path / ZEEK_DIR, self.clock(), self.interval_minutes)
        if not done:
            raise NoCompletedInterval(
                f"{path / ZEEK_DIR}: no interval has finished yet; the first one is complete "
                f"{self.interval_minutes} minutes plus {SETTLE_SECONDS} seconds after the "
                "sensor starts")
        newest = done[-1]
        merge_eve(newest, path / EVE_DIR, self.interval_minutes)
        # From here on it is an ordinary folder of Zeek logs plus eve.json. ZeekLogAdapter
        # copies it into workdir and joins conn.log with conn.<time>.log after a restart.
        return ZeekLogAdapter().to_zeek_logs(newest, workdir)
