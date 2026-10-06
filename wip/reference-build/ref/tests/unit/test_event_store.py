"""Tests for maxguard.storage.events.EventStore (hourly Parquet + DuckDB)."""

from pathlib import Path

import duckdb
import pytest

from maxguard.events.normalize import EVENT_KEYS, normalize
from maxguard.storage.events import COLUMNS, DUCKDB_CONFIG, EventStore, hour_key

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "zeek"
CAPTURES = sorted(p for p in FIXTURES.iterdir() if p.is_dir() and not p.name.startswith("_"))

HOUR_01 = 1791248400.0  # 2026-10-06 01:00:00 UTC: 13 of the 14 lab captures are in this hour
HOUR_02 = 1791252000.0  # 2026-10-06 02:00:00 UTC: dns_lookup and the handmade DNS/DHCP capture


def fixture_events() -> list[dict]:
    events = []
    for log_dir in CAPTURES + [FIXTURES / "_handmade" / "dns_dhcp"]:
        events.extend(normalize(log_dir, sensor_id="pcap"))
    return events


@pytest.fixture
def events() -> list[dict]:
    return fixture_events()


@pytest.fixture
def store(tmp_path, events) -> EventStore:
    s = EventStore(tmp_path / "events")
    s.write(events)
    return s


def in_query_order(events: list[dict]) -> list[dict]:
    return sorted(events, key=lambda e: (e["ts"], e["event_id"]))


def test_columns_match_the_event_schema():
    assert tuple(COLUMNS) == EVENT_KEYS


def test_hour_key_uses_utc():
    assert hour_key(HOUR_01) == ("2026-10-06", "01")
    assert hour_key(HOUR_02 - 0.001) == ("2026-10-06", "01")


def test_write_makes_one_file_per_hour(tmp_path, events):
    store = EventStore(tmp_path / "events")
    assert store.write(events) == len(events)
    files = sorted(p.relative_to(store.root).parent.as_posix()
                   for p in store.root.rglob("*") if p.is_file())
    assert files == ["date=2026-10-06/hour=01", "date=2026-10-06/hour=02"]
    names = [p.name for p in store.root.rglob("*.parquet")]
    assert all(n.startswith("part-") and len(n) == len("part-") + 16 + len(".parquet")
               for n in names)


def test_query_returns_every_event_unchanged(store, events):
    assert store.query() == in_query_order(events)


def test_query_by_ip_matches_source_or_destination(store, events):
    laptop = store.query(ip="192.168.56.50")
    assert laptop == in_query_order(
        [e for e in events if "192.168.56.50" in (e["src_ip"], e["dst_ip"])])
    assert {e["log"] for e in laptop} == {"dhcp.log", "conn.log", "dns.log", "eve.json"}
    assert store.query(ip="203.0.113.9") == []


def test_query_time_window_is_since_inclusive_until_exclusive(store, events):
    assert {e["ts"] >= HOUR_02 for e in store.query(since=HOUR_02)} == {True}
    assert {e["ts"] < HOUR_02 for e in store.query(until=HOUR_02)} == {True}
    assert len(store.query(since=HOUR_02)) + len(store.query(until=HOUR_02)) == len(events)
    first = min(e["ts"] for e in events)
    [only] = store.query(since=first, until=first + 0.000001)
    assert only["ts"] == first


def test_query_limit(store):
    assert len(store.query(limit=5)) == 5


def test_empty_store_returns_nothing(tmp_path):
    assert EventStore(tmp_path / "empty").query(ip="10.0.0.1") == []


def test_writing_the_same_events_again_does_not_duplicate_them(store, events):
    store.write(events)  # e.g. the same capture uploaded twice
    assert len(list(store.root.rglob("*.parquet"))) == 2
    assert len(store.query(limit=10_000)) == len(events)


def test_no_staging_files_are_left_behind(store):
    leftovers = [p for p in store.root.rglob("*") if p.is_file() and p.suffix != ".parquet"]
    assert leftovers == []


def test_prune_deletes_only_hours_that_are_completely_older(store):
    assert store.prune(older_than=HOUR_01 + 1800) == 0  # hour 01 is only half over
    assert store.prune(older_than=HOUR_02) == 1  # hour 01 ended exactly at 02:00
    assert {e["ts"] >= HOUR_02 for e in store.query()} == {True}
    assert store.prune(older_than=HOUR_02 + 3600) == 1
    assert store.query() == []
    assert list(store.root.iterdir()) == []  # the empty date folder is removed too

def test_duckdb_never_downloads_extensions():
    # CLAUDE.md rule 1: a query that needs an extension must fail, not download it.
    with duckdb.connect(config=DUCKDB_CONFIG) as con:
        settings = con.execute(
            "SELECT current_setting('autoinstall_known_extensions'), "
            "current_setting('autoload_known_extensions')").fetchone()
    assert settings == (False, False)
