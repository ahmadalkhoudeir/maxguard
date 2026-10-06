"""Tests for maxguard.sensor.attribution (device table from DHCP + DNS)."""

import json
from pathlib import Path

from maxguard.sensor.attribution import build_device_table

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "zeek"
DEVICE_KEYS = ("ip", "mac", "host_name", "dns_names", "first_seen")


def write_log(log_dir: Path, name: str, records: list[dict]) -> None:
    """Write a tiny Zeek JSON log (one object per line) for a test."""
    log_dir.mkdir(parents=True, exist_ok=True)
    (log_dir / name).write_text("".join(json.dumps(r) + "\n" for r in records))


def lease(ts: float, ip: str, mac: str, host_name: str | None = None) -> dict:
    rec = {"ts": ts, "mac": mac, "assigned_addr": ip, "msg_types": ["REQUEST", "ACK"]}
    if host_name:
        rec["host_name"] = host_name
    return rec


def query(ts: float, ip: str, name: str | None) -> dict:
    rec = {"ts": ts, "id.orig_h": ip, "id.resp_h": "10.0.0.1", "id.resp_p": 53}
    if name:
        rec["query"] = name
    return rec


def test_dhcp_and_dns_joined_on_the_ip():
    # Zeek 9.0.0 logs of a synthetic DHCP lease followed by one DNS lookup
    table = build_device_table(FIXTURES / "_handmade" / "dns_dhcp")
    assert table == [{"ip": "192.168.56.50", "mac": "02:00:00:aa:bb:cc",
                      "host_name": "laptop-lab", "dns_names": ["printer.lab.invalid"],
                      "first_seen": 1791252600.0}]


def test_dns_only_device_from_the_lab_capture():
    # The lab uses fixed addresses (no DHCP), so MAC and host name stay empty.
    table = build_device_table(FIXTURES / "dns_lookup")
    assert table == [{"ip": "172.18.0.3", "mac": "", "host_name": "",
                      "dns_names": ["camera.lab.invalid", "nas.lab.invalid",
                                    "printer.lab.invalid"],
                      "first_seen": 1791252458.738595}]


def test_latest_lease_wins_and_a_new_mac_forgets_the_old_name(tmp_path):
    write_log(tmp_path, "dhcp.log", [
        lease(30.0, "10.0.0.5", "02:00:00:00:00:02"),  # new card, no host name sent
        lease(10.0, "10.0.0.5", "02:00:00:00:00:01", "old-laptop"),
    ])
    [device] = build_device_table(tmp_path)
    assert (device["mac"], device["host_name"], device["first_seen"]) == (
        "02:00:00:00:00:02", "", 10.0)


def test_renewal_without_host_name_keeps_the_name(tmp_path):
    write_log(tmp_path, "dhcp.log", [
        lease(10.0, "10.0.0.5", "02:00:00:00:00:01", "printer"),
        lease(20.0, "10.0.0.5", "02:00:00:00:00:01"),
    ])
    [device] = build_device_table(tmp_path)
    assert device["host_name"] == "printer"


def test_dns_names_are_unique_lower_case_and_sorted(tmp_path):
    write_log(tmp_path, "dns.log", [
        query(1.0, "10.0.0.7", "NAS.lab.invalid"),
        query(2.0, "10.0.0.7", "nas.lab.invalid"),
        query(3.0, "10.0.0.7", "camera.lab.invalid"),
        query(4.0, "10.0.0.7", None),  # no question in this message: skipped
    ])
    [device] = build_device_table(tmp_path)
    assert device["dns_names"] == ["camera.lab.invalid", "nas.lab.invalid"]


def test_rows_sorted_by_ip_and_line_order_does_not_matter(tmp_path):
    records = [query(1.0, "10.0.0.10", "a.lab.invalid"), query(2.0, "10.0.0.9", "b.lab.invalid")]
    write_log(tmp_path / "one", "dns.log", records)
    write_log(tmp_path / "two", "dns.log", list(reversed(records)))
    one = build_device_table(tmp_path / "one")
    assert [d["ip"] for d in one] == ["10.0.0.9", "10.0.0.10"]
    assert one == build_device_table(tmp_path / "two")
    assert all(tuple(d) == DEVICE_KEYS for d in one)


def test_dhcp_record_without_an_address_is_ignored(tmp_path):
    write_log(tmp_path, "dhcp.log", [{"ts": 1.0, "mac": "02:00:00:00:00:09",
                                      "msg_types": ["DISCOVER"]}])
    assert build_device_table(tmp_path) == []


def test_no_logs_gives_empty_table(tmp_path):
    assert build_device_table(tmp_path) == []
