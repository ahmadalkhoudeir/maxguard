"""Tests for maxguard.inventory (asset inventory)."""

import json
from pathlib import Path

import pytest

import maxguard.rules  # noqa: F401  (registers the rules used by run_all)
from maxguard.inventory import build, ip_sort_key, service_names, software_name
from maxguard.models import Finding
from maxguard.rules.base import run_all

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "zeek"
CAPTURES = sorted(p for p in FIXTURES.iterdir() if p.is_dir() and not p.name.startswith("_"))
ASSET_KEYS = ("ip", "first_seen", "services", "software", "finding_count")


def write_log(log_dir: Path, name: str, records: list[dict]) -> None:
    """Write a tiny Zeek JSON log (one object per line) for a test."""
    log_dir.mkdir(parents=True, exist_ok=True)
    (log_dir / name).write_text("".join(json.dumps(r) + "\n" for r in records))


def finding(src: str, dst: str, ts: float = 100.0) -> Finding:
    return Finding(rule_id="cleartext.telnet", title="Telnet", severity="high",
                   src_ip=src, dst_ip=dst, dst_port=23, protocol="telnet",
                   first_seen=ts, last_seen=ts)


def test_plain_http_capture():
    log_dir = FIXTURES / "plain_http"
    assets = build(log_dir, run_all(log_dir))
    assert assets == [
        {"ip": "172.18.0.2", "first_seen": 1791250493.372808, "services": ["80/http"],
         "software": ["SimpleHTTP 0.6-Python/3"], "finding_count": 1},
        {"ip": "172.18.0.3", "first_seen": 1791250493.372808, "services": [],
         "software": ["Python-urllib 3.11"], "finding_count": 1},
    ]


def test_udp_only_client_is_not_in_known_hosts():
    # known_hosts.log needs a finished TCP handshake; the DNS capture is UDP only,
    # so only the DNS server shows up (through known_services.log).
    assets = build(FIXTURES / "dns_lookup", [])
    assert assets == [{"ip": "172.18.0.2", "first_seen": 1791252458.740764,
                       "services": ["53/dns"], "software": [], "finding_count": 0}]


@pytest.mark.parametrize("log_dir", CAPTURES, ids=lambda p: p.name)
def test_every_capture_same_keys_same_result(log_dir):
    findings = run_all(log_dir)
    first = build(log_dir, findings)
    assert first == build(log_dir, findings)
    assert first, "every lab capture has at least one host"
    for asset in first:
        assert tuple(asset) == ASSET_KEYS
        assert asset["services"] == sorted(asset["services"], key=lambda s: int(s.split("/")[0]))
        assert asset["software"] == sorted(asset["software"])
    # every finding is counted on both of its hosts
    assert sum(a["finding_count"] for a in first) == 2 * len(findings)


def test_sorted_by_ip_number_ipv4_before_ipv6(tmp_path):
    write_log(tmp_path, "known_hosts.log", [
        {"ts": 3.0, "host": "fd00::1"},
        {"ts": 2.0, "host": "10.0.0.10"},
        {"ts": 1.0, "host": "10.0.0.9"},
    ])
    assert [a["ip"] for a in build(tmp_path, [])] == ["10.0.0.9", "10.0.0.10", "fd00::1"]


def test_first_seen_is_the_earliest_record(tmp_path):
    write_log(tmp_path, "known_hosts.log", [{"ts": 50.0, "host": "10.0.0.1"}])
    write_log(tmp_path, "known_services.log", [
        {"ts": 20.0, "host": "10.0.0.1", "port_num": 22, "port_proto": "tcp", "service": ["SSH"]},
    ])
    [asset] = build(tmp_path, [])
    assert asset["first_seen"] == 20.0


def test_services_sorted_by_port_number_and_deduplicated(tmp_path):
    write_log(tmp_path, "known_services.log", [
        {"ts": 1.0, "host": "10.0.0.1", "port_num": 443, "port_proto": "tcp", "service": ["SSL"]},
        {"ts": 2.0, "host": "10.0.0.1", "port_num": 80, "port_proto": "tcp", "service": ["HTTP"]},
        {"ts": 3.0, "host": "10.0.0.1", "port_num": 80, "port_proto": "tcp", "service": ["HTTP"]},
    ])
    [asset] = build(tmp_path, [])
    assert asset["services"] == ["80/http", "443/ssl"]


def test_service_without_a_name_shows_the_transport():
    rec = {"host": "10.0.0.1", "port_num": 8443, "port_proto": "tcp", "service": [""]}
    assert service_names(rec) == ["8443/tcp"]
    rec["service"] = ["SSL", "HTTP"]
    assert service_names(rec) == ["8443/ssl", "8443/http"]


def test_software_name_follows_zeek_version_format():
    assert software_name({"name": "OpenSSH", "version.major": 9, "version.minor": 6,
                          "version.addl": "p1"}) == "OpenSSH 9.6-p1"
    assert software_name({"name": "nginx", "version.major": 1, "version.minor": 24,
                          "version.minor2": 0}) == "nginx 1.24.0"
    assert software_name({"name": "curl"}) == "curl"


def test_findings_are_counted_and_finding_only_hosts_are_added(tmp_path):
    write_log(tmp_path, "known_hosts.log", [{"ts": 10.0, "host": "10.0.0.2"}])
    findings = [finding("10.0.0.3", "10.0.0.2", ts=5.0), finding("10.0.0.4", "10.0.0.2")]
    assets = {a["ip"]: a for a in build(tmp_path, findings)}
    assert assets["10.0.0.2"]["finding_count"] == 2
    assert assets["10.0.0.2"]["first_seen"] == 5.0  # the finding is older than the log line
    assert assets["10.0.0.3"] == {"ip": "10.0.0.3", "first_seen": 5.0, "services": [],
                                  "software": [], "finding_count": 1}


def test_no_logs_no_findings_gives_empty_inventory(tmp_path):
    assert build(tmp_path, []) == []


def test_ip_sort_key():
    ips = ["192.168.1.20", "fe80::1", "192.168.1.3", "10.1.1.1"]
    assert sorted(ips, key=ip_sort_key) == ["10.1.1.1", "192.168.1.3", "192.168.1.20", "fe80::1"]
