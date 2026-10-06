"""LiveSensorAdapter tests (Jakub, JAK-07): pick the newest finished interval, never
the one still being written, and merge Suricata's minute files into it.

No Zeek, Suricata or Docker: each test builds a small sensor data folder by hand,
the way docker/sensor-compose.yaml lays it out, from the plain_http_alt fixture.
"""

import shutil
from pathlib import Path

import pytest

from maxguard import pipeline
from maxguard.adapters.base import read_log
from maxguard.adapters.live import (
    SETTLE_SECONDS,
    LiveSensorAdapter,
    NoCompletedInterval,
    check_interval,
    eve_parts,
    folder_name,
    folder_start,
    interval_minutes_from_env,
    merge_eve,
)
from maxguard.adapters.pcap import PcapAdapter
from maxguard.adapters.zeeklogs import ZeekLogAdapter

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "zeek" / "plain_http_alt"

# The sensor below has three 15-minute folders: 14:00, 14:15 and 14:30 (UTC).
# At NOW the 14:30 interval has ended (14:45) but is still settling until 14:47.
NOW = folder_start("2026-10-06-1430") + 15 * 60 + 60   # 14:46:00 UTC


def write_lines(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(line + "\n" for line in lines))


def make_sensor(root: Path) -> Path:
    """A sensor data folder: three interval folders and Suricata minute files."""
    zeek = root / "zeek"
    for name in ("2026-10-06-1400", "2026-10-06-1430"):
        write_lines(zeek / name / "conn.log", [f'{{"note": "conn from {name}"}}'])
    shutil.copytree(FIXTURE, zeek / "2026-10-06-1415", ignore=shutil.ignore_patterns("eve.json"))
    # The fixture's two Suricata events, as if written in minutes 14:15 and 14:22.
    eve_lines = (FIXTURE / "eve.json").read_text().splitlines()
    spool = root / "spool" / "suricata"
    write_lines(spool / "eve-2026-10-06-1415.json", eve_lines[:1])
    write_lines(spool / "eve-2026-10-06-1422.json", eve_lines[1:])
    write_lines(spool / "eve-2026-10-06-1430.json", ['{"event_type": "flow", "minute": "14:30"}'])
    write_lines(root / "spool" / "zeek" / "conn.log", ['{"note": "interval in progress"}'])
    return root


def adapter_at(now: float) -> LiveSensorAdapter:
    return LiveSensorAdapter(interval_minutes=15, clock=lambda: now)


# ---- folder names are UTC times -------------------------------------------------

def test_folder_names_are_utc_interval_starts():
    assert folder_start("2026-10-06-1415") == 1791296100.0   # 14:15:00 UTC
    assert folder_name(1791296100.0) == "2026-10-06-1415"


@pytest.mark.parametrize("minutes", [1, 5, 15, 30, 60])
def test_intervals_that_divide_an_hour_are_allowed(minutes):
    assert check_interval(minutes) == minutes


@pytest.mark.parametrize("minutes", [0, 7, 45, 90])
def test_other_intervals_are_refused(minutes):
    with pytest.raises(ValueError):
        check_interval(minutes)


def test_interval_comes_from_the_environment(monkeypatch):
    monkeypatch.delenv("MAXGUARD_INTERVAL_MINUTES", raising=False)
    assert interval_minutes_from_env() == 15
    monkeypatch.setenv("MAXGUARD_INTERVAL_MINUTES", "1")
    assert interval_minutes_from_env() == 1
    assert LiveSensorAdapter().interval_minutes == 1


def test_a_wrong_interval_setting_does_not_stop_the_pipeline_from_loading(monkeypatch):
    # pipeline.py builds the adapter when it is imported; the setting is read later.
    monkeypatch.setenv("MAXGUARD_INTERVAL_MINUTES", "7")
    adapter = LiveSensorAdapter()
    with pytest.raises(ValueError, match="interval must be"):
        _ = adapter.interval_minutes


# ---- accepts(): a sensor folder, and nothing ZeekLogAdapter accepts ------------------

def test_accepts_a_sensor_data_folder(tmp_path):
    root = make_sensor(tmp_path)
    assert adapter_at(NOW).accepts(root)
    assert not ZeekLogAdapter().accepts(root)   # no conn.log at the top
    assert not PcapAdapter().accepts(root)


def test_never_takes_a_plain_zeek_log_folder(tmp_path):
    assert not adapter_at(NOW).accepts(FIXTURE)          # conn.log at the top
    root = make_sensor(tmp_path)
    (root / "conn.log").write_text("{}\n")
    assert not adapter_at(NOW).accepts(root)             # conn.log wins, even here
    assert ZeekLogAdapter().accepts(root)


def test_refuses_folders_without_interval_folders(tmp_path):
    (tmp_path / "zeek" / "not-an-interval").mkdir(parents=True)
    assert not adapter_at(NOW).accepts(tmp_path)
    assert not adapter_at(NOW).accepts(tmp_path / "missing")
    assert not adapter_at(NOW).accepts(FIXTURE / "conn.log")   # a file


# ---- to_zeek_logs(): newest complete folder, eve.json merged in ----------------------

def test_picks_the_newest_complete_folder_not_the_one_being_written(tmp_path):
    root = make_sensor(tmp_path)
    log_dir = adapter_at(NOW).to_zeek_logs(root, tmp_path / "work")

    # 14:15 was picked: its conn.log is the fixture's, not 14:30's or 14:00's.
    assert list(read_log(log_dir, "conn.log")) == list(read_log(FIXTURE, "conn.log"))
    assert list(read_log(log_dir, "http.log")) == list(read_log(FIXTURE, "http.log"))
    # Its two Suricata minutes were merged in, in time order; 14:30's minute was not.
    assert list(read_log(log_dir, "eve.json")) == list(read_log(FIXTURE, "eve.json"))


def test_the_current_folder_is_used_once_it_has_settled(tmp_path):
    root = make_sensor(tmp_path)
    settled = folder_start("2026-10-06-1430") + 15 * 60 + SETTLE_SECONDS   # 14:47:00
    log_dir = adapter_at(settled).to_zeek_logs(root, tmp_path / "work")
    assert list(read_log(log_dir, "conn.log")) == [{"note": "conn from 2026-10-06-1430"}]
    assert list(read_log(log_dir, "eve.json")) == [{"event_type": "flow", "minute": "14:30"}]


def test_one_second_before_settling_the_folder_is_not_used(tmp_path):
    root = make_sensor(tmp_path)
    almost = folder_start("2026-10-06-1430") + 15 * 60 + SETTLE_SECONDS - 1
    log_dir = adapter_at(almost).to_zeek_logs(root, tmp_path / "work")
    assert list(read_log(log_dir, "conn.log")) == list(read_log(FIXTURE, "conn.log"))


def test_no_complete_folder_yet_is_a_clear_error(tmp_path):
    root = make_sensor(tmp_path)
    too_early = folder_start("2026-10-06-1400") + 60
    with pytest.raises(NoCompletedInterval, match="no interval has finished yet"):
        adapter_at(too_early).to_zeek_logs(root, tmp_path / "work")


def test_logs_from_before_a_zeek_restart_are_kept(tmp_path):
    root = make_sensor(tmp_path)
    folder = root / "zeek" / "2026-10-06-1415"
    write_lines(folder / "conn.141502.log", ['{"note": "after the restart"}'])
    log_dir = adapter_at(NOW).to_zeek_logs(root, tmp_path / "work")
    notes = [rec.get("note") for rec in read_log(log_dir, "conn.log")]
    assert notes.count("after the restart") == 1
    assert len(notes) == 2   # the fixture's connection plus the one after the restart


# ---- merge_eve(): the minute files of one interval ------------------------------------

def test_merge_moves_exactly_the_intervals_minutes(tmp_path):
    root = make_sensor(tmp_path)
    folder, spool = root / "zeek" / "2026-10-06-1415", root / "spool" / "suricata"
    assert [p.name for p in eve_parts(spool, folder, 15)] == [
        "eve-2026-10-06-1415.json", "eve-2026-10-06-1422.json"]

    merge_eve(folder, spool, 15)

    assert (folder / "eve.json").read_text() == (FIXTURE / "eve.json").read_text()
    assert sorted(p.name for p in spool.iterdir()) == ["eve-2026-10-06-1430.json"]
    assert not list(folder.glob(".eve-*"))   # no temporary file left behind


def test_merge_twice_adds_nothing(tmp_path):
    root = make_sensor(tmp_path)
    folder, spool = root / "zeek" / "2026-10-06-1415", root / "spool" / "suricata"
    merge_eve(folder, spool, 15)
    merge_eve(folder, spool, 15)
    assert (folder / "eve.json").read_text() == (FIXTURE / "eve.json").read_text()


def test_merge_after_a_crash_deletes_the_leftovers_without_adding_them_again(tmp_path):
    root = make_sensor(tmp_path)
    folder, spool = root / "zeek" / "2026-10-06-1415", root / "spool" / "suricata"
    merge_eve(folder, spool, 15)
    # A crash after eve.json was written but before the minute files were deleted:
    write_lines(spool / "eve-2026-10-06-1415.json", ['{"event_type": "flow"}'])
    merge_eve(folder, spool, 15)
    assert (folder / "eve.json").read_text() == (FIXTURE / "eve.json").read_text()
    assert not (spool / "eve-2026-10-06-1415.json").exists()


def test_a_folder_without_suricata_minutes_gets_no_eve_json(tmp_path):
    root = make_sensor(tmp_path)
    folder = root / "zeek" / "2026-10-06-1400"
    merge_eve(folder, root / "spool" / "suricata", 15)
    assert not (folder / "eve.json").exists()


# ---- the whole pipeline on a sensor folder --------------------------------------------

def test_pipeline_analyzes_the_newest_complete_interval(tmp_path, monkeypatch):
    root = make_sensor(tmp_path)
    live = adapter_at(NOW)
    monkeypatch.setattr(pipeline, "ADAPTERS", [PcapAdapter(), ZeekLogAdapter(), live])

    report = pipeline.analyze(root, tmp_path / "work", explain=False, sensor_id="lab-sensor")

    assert report["input"]["adapter"] == "live"
    assert [f["rule_id"] for f in report["findings"]] == ["cleartext.http_alt"]
    assert report["events"]
    assert {e["sensor_id"] for e in report["events"]} == {"lab-sensor"}
    assert report["tools"]["suricata"] is True   # eve.json was merged in
