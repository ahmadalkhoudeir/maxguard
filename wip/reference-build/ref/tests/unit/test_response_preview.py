"""Tests for maxguard.response.preview (Ahmad, AHM-07). Synthetic events only."""

import pytest

from maxguard.events.normalize import EVENT_KEYS
from maxguard.response.preview import WINDOW_SECONDS, preview
from maxguard.storage.events import EventStore

WINDOW_END = 1791331200.0   # 2026-10-07 00:00:00 UTC
BAD = "203.0.113.7"          # the address we want to block
LAPTOP = "192.168.1.20"
PRINTER = "192.168.1.30"


def event(n: int, ts: float, src: str, dst: str, port: int, service: str = "",
          community_id: str = "") -> dict:
    row = dict.fromkeys(EVENT_KEYS, "")
    row.update(event_id=f"ev{n:04d}", ts=ts, sensor_id="pcap", source="zeek", log="conn.log",
               kind="conn", community_id=community_id or f"1:c{n}=", src_ip=src, dst_ip=dst,
               src_port=40000 + n, dst_port=port, proto="tcp", service=service,
               bytes_out=10, bytes_in=20)
    return row


@pytest.fixture
def store(tmp_path):
    events = [
        # inbound: the bad address starts connections to our devices
        event(1, WINDOW_END - 3600, BAD, LAPTOP, 22, "ssh"),
        event(2, WINDOW_END - 1800, BAD, PRINTER, 23),
        # outbound: our laptop starts a connection to it (two events of one connection)
        event(3, WINDOW_END - 7200, LAPTOP, BAD, 443, "ssl", community_id="1:same="),
        event(4, WINDOW_END - 7199, LAPTOP, BAD, 443, "ssl", community_id="1:same="),
        # outside the 7-day window, and exactly at window_end (the end is not included)
        event(5, WINDOW_END - WINDOW_SECONDS - 1, BAD, LAPTOP, 22, "ssh"),
        event(6, WINDOW_END, BAD, LAPTOP, 22, "ssh"),
        # another address: never part of the preview
        event(7, WINDOW_END - 60, "198.51.100.9", LAPTOP, 80, "http"),
    ]
    events += [event(100 + i, WINDOW_END - 100 + i, BAD, LAPTOP, 22, "ssh") for i in range(12)]
    target = EventStore(tmp_path / "events")
    target.write(events)
    return target


def test_inbound_counts_only_connections_the_address_starts(store):
    result = preview(BAD, "inbound", store, window_end=WINDOW_END)
    assert result["connections"] == 14            # events 1, 2 and the 12 extra ones
    assert result["devices"] == [LAPTOP, PRINTER]
    assert result["first_seen"] == WINDOW_END - 3600
    assert result["last_seen"] == WINDOW_END - 100 + 11
    assert [s["port"] for s in result["services"]] == [22, 23]


def test_outbound_counts_one_connection_once(store):
    result = preview(BAD, "outbound", store, window_end=WINDOW_END)
    assert result["events"] == 2
    assert result["connections"] == 1             # the two events share a community_id
    assert result["devices"] == [LAPTOP]
    assert result["services"] == [{"proto": "tcp", "port": 443, "service": "ssl", "events": 2}]


def test_samples_are_ten_in_time_order(store):
    result = preview(BAD, "both", store, window_end=WINDOW_END)
    assert result["connections"] == 15
    samples = result["samples"]
    assert len(samples) == 10
    assert [s["ts"] for s in samples] == sorted(s["ts"] for s in samples)
    assert samples[0]["event_id"] == "ev0003"     # the oldest event in the window


def test_window_end_comes_from_the_caller(store):
    result = preview(BAD, "both", store, window_end=WINDOW_END - 5000)
    assert result["window_start"] == WINDOW_END - 5000 - WINDOW_SECONDS
    # The window moved back: events 3, 4 (outbound) and 5 are inside it now.
    assert [s["event_id"] for s in result["samples"]] == ["ev0005", "ev0003", "ev0004"]


def test_same_input_same_preview(store):
    first = preview(BAD, "both", store, window_end=WINDOW_END)
    assert preview(BAD, "both", store, window_end=WINDOW_END) == first


def test_no_events_gives_an_empty_preview(tmp_path):
    result = preview(BAD, "both", EventStore(tmp_path / "empty"), window_end=WINDOW_END)
    assert result["connections"] == 0 and result["samples"] == []
    assert result["first_seen"] is None and result["last_seen"] is None


def test_hostile_input_is_refused_before_any_query(store):
    with pytest.raises(ValueError):
        preview("1.2.3.4; rm -rf /", "both", store, window_end=WINDOW_END)
    with pytest.raises(ValueError):
        preview("127.0.0.1", "both", store, window_end=WINDOW_END)
