"""Tests for maxguard.events.normalize (common event schema)."""

import shutil
from pathlib import Path

import pytest

from maxguard.adapters.base import read_log
from maxguard.adapters.zeeklogs import ZeekLogAdapter
from maxguard.events.normalize import EVENT_KEYS, as_int, as_list, normalize, proto_name
from maxguard.ids import record_id

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "zeek"
HANDMADE = FIXTURES / "_handmade"
CAPTURES = sorted(p.name for p in FIXTURES.iterdir() if p.is_dir() and not p.name.startswith("_"))
ALL_DIRS = [FIXTURES / name for name in CAPTURES] + [
    HANDMADE / "dns_dhcp", HANDMADE / "dns_dhcp_suricata8"]


def by_log(events: list[dict], log: str) -> list[dict]:
    return [e for e in events if e["log"] == log]


@pytest.mark.parametrize("log_dir", ALL_DIRS, ids=lambda p: p.name)
def test_every_event_has_exactly_the_schema(log_dir):
    events = normalize(log_dir, sensor_id="pcap")
    assert events, "every fixture has at least one event"
    for e in events:
        assert tuple(e) == EVENT_KEYS
        assert isinstance(e["event_id"], str) and len(e["event_id"]) == 16
        assert isinstance(e["ts"], float)
        assert e["sensor_id"] == "pcap"
        assert e["source"] in ("zeek", "suricata")
        assert e["kind"] in ("conn", "dns", "http", "tls", "dhcp", "alert")
        assert e["proto"] in ("tcp", "udp", "icmp", "")
        for port in (e["src_port"], e["dst_port"]):
            assert port is None or isinstance(port, int)
        assert isinstance(e["bytes_out"], int) and isinstance(e["bytes_in"], int)
        for key in ("uid", "community_id", "src_ip", "dst_ip", "service",
                    "device_mac", "summary", "ja4"):
            assert isinstance(e[key], str)


@pytest.mark.parametrize("log_dir", ALL_DIRS, ids=lambda p: p.name)
def test_output_is_sorted_and_the_same_every_time(log_dir):
    first = normalize(log_dir, sensor_id="pcap")
    assert first == normalize(log_dir, sensor_id="pcap")
    keys = [(e["ts"], e["log"], e["event_id"]) for e in first]
    assert keys == sorted(keys)


def test_event_id_is_the_record_id_of_the_raw_record():
    rec = next(read_log(FIXTURES / "plain_http", "http.log"))
    [http] = by_log(normalize(FIXTURES / "plain_http", "pcap"), "http.log")
    assert http["event_id"] == record_id("http.log", rec)


def test_plain_http_conn_and_http_events():
    events = normalize(FIXTURES / "plain_http", sensor_id="pcap")
    # eve.json has only "http" and "flow" records here: both are skipped
    assert [e["log"] for e in events] == ["conn.log", "http.log"]
    conn, http = events
    assert conn["kind"] == "conn" and conn["service"] == "http"
    assert (conn["src_ip"], conn["src_port"], conn["dst_ip"], conn["dst_port"]) == (
        "172.18.0.3", 40288, "172.18.0.2", 80)
    assert (conn["bytes_out"], conn["bytes_in"]) == (113, 924)
    assert conn["summary"] == "tcp/80 http SF out=113 in=924"
    assert http["summary"] == "GET server:80/"
    # http.log has no community_id and no proto: both are copied from conn.log (same uid)
    assert http["uid"] == conn["uid"] == "CJKFoj4bpHEhTeaRoj"
    assert http["community_id"] == conn["community_id"] == "1:Zd6w43plhlSu6wAgAknKxXblpcw="
    assert http["proto"] == "tcp"
    assert (http["bytes_out"], http["bytes_in"]) == (0, 0)  # only conn events count bytes


def test_tls_events_from_zeek_and_suricata():
    events = normalize(FIXTURES / "tls_weak_version", sensor_id="pcap")
    [ssl] = by_log(events, "ssl.log")
    [eve_tls] = by_log(events, "eve.json")
    assert ssl["kind"] == eve_tls["kind"] == "tls"
    assert ssl["summary"] == "TLSv10 port4431.lab.invalid TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA"
    assert ssl["ja4"] == ""
    assert eve_tls["source"] == "suricata" and eve_tls["uid"] == ""
    assert eve_tls["ja4"] == "t10d230600_44099cda8a52_242d16716555"
    assert eve_tls["summary"] == (
        "TLSv1 port4431.lab.invalid ja4=t10d230600_44099cda8a52_242d16716555")
    # Zeek and Suricata agree on the community id, so the two events can be joined
    assert eve_tls["community_id"] == ssl["community_id"] == "1:pRvdZyOxcG+AIDBGMFce8LVpI/I="


def test_zeek_dns_and_dhcp():
    events = normalize(HANDMADE / "dns_dhcp", sensor_id="pcap")
    [dns] = by_log(events, "dns.log")
    assert dns["summary"] == "A printer.lab.invalid NOERROR 192.168.56.20"
    assert (dns["proto"], dns["service"], dns["dst_port"]) == ("udp", "dns", 53)
    [dhcp] = by_log(events, "dhcp.log")
    assert dhcp["device_mac"] == "02:00:00:aa:bb:cc"
    assert (dhcp["src_ip"], dhcp["dst_ip"]) == ("192.168.56.50", "192.168.56.1")
    assert (dhcp["src_port"], dhcp["dst_port"]) == (None, None)  # dhcp.log logs no ports
    assert dhcp["uid"] == "CJKFoj4bpHEhTeaRoj"  # smallest of the record's uids
    assert dhcp["summary"] == (
        "DISCOVER/OFFER/REQUEST/ACK 02:00:00:aa:bb:cc laptop-lab -> 192.168.56.50")


def test_suricata_7_alert_dns_and_dhcp():
    events = by_log(normalize(HANDMADE / "dns_dhcp", sensor_id="pcap"), "eve.json")
    summaries = {(e["kind"], e["summary"]) for e in events}
    assert summaries == {
        ("dhcp", "ack 02:00:00:aa:bb:cc -> 192.168.56.50"),
        ("alert", "MaxGuard fixture: DNS lookup of a lab.invalid name (sid 9000001)"),
        ("dns", "query A printer.lab.invalid"),
        ("dns", "answer A printer.lab.invalid NOERROR 192.168.56.20"),
    }  # the three "flow" records are skipped
    [dhcp] = [e for e in events if e["kind"] == "dhcp"]
    assert dhcp["device_mac"] == "02:00:00:aa:bb:cc"
    [alert] = [e for e in events if e["kind"] == "alert"]
    assert (alert["proto"], alert["service"]) == ("udp", "dns")


def test_suricata_8_dns_format_is_understood_too():
    events = normalize(HANDMADE / "dns_dhcp_suricata8", sensor_id="sensor-1")
    dns = [e["summary"] for e in events if e["kind"] == "dns"]
    assert dns == ["request A printer.lab.invalid NOERROR",
                   "response A printer.lab.invalid NOERROR 192.168.56.20"]
    assert {e["sensor_id"] for e in events} == {"sensor-1"}


def test_absent_logs_give_no_events(tmp_path):
    assert normalize(tmp_path, sensor_id="pcap") == []


def test_ssl_log_alone_still_works(tmp_path):
    shutil.copy(FIXTURES / "tls_weak_version" / "ssl.log", tmp_path / "ssl.log")
    [event] = normalize(tmp_path, sensor_id="pcap")
    assert event["kind"] == "tls"
    assert event["proto"] == "" and event["community_id"] == ""  # no conn.log to copy from


@pytest.mark.parametrize("tsv_dir, json_dir", [
    (HANDMADE / "tsv_plain_http", FIXTURES / "plain_http"),
    (HANDMADE / "tsv_dns_dhcp", HANDMADE / "dns_dhcp"),
], ids=["plain_http", "dns_dhcp"])
def test_tsv_logs_give_the_same_events_as_json_logs(tmp_path, tsv_dir, json_dir):
    # The ZeekLogAdapter turns TSV into JSON where every value is a string ("443").
    converted = ZeekLogAdapter().to_zeek_logs(tsv_dir, tmp_path)
    from_tsv = normalize(converted, sensor_id="import")
    from_json = [e for e in normalize(json_dir, sensor_id="import") if e["source"] == "zeek"]

    def without_event_id(events):  # event_id hashes the raw text, which differs
        return [{k: v for k, v in e.items() if k != "event_id"} for e in events]

    assert len(from_tsv) >= 2
    assert all(isinstance(e["dst_port"], int) for e in from_tsv if e["log"] != "dhcp.log")
    assert without_event_id(from_tsv) == without_event_id(from_json)


def test_helpers():
    assert as_int("443") == 443 and as_int(443) == 443
    assert as_int(None) is None and as_int("") is None
    assert as_list(["a", "b"]) == ["a", "b"] and as_list("a,b") == ["a", "b"]
    assert as_list(None) == []
    assert proto_name("TCP") == "tcp" and proto_name("udp") == "udp"
    assert proto_name("IPv6-ICMP") == "icmp"  # Suricata's name for ICMPv6
    assert proto_name("unknown_transport") == "" and proto_name(None) == ""
