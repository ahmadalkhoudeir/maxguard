"""Tests for NetflowAdapter (Jakub, JAK-10).

tests/fixtures/netflow/goflow2.json is real goflow2 v2.2.7 output for flows sent
by a small generator (2 NetFlow v5 packets, 1 NetFlow v9, 1 IPFIX) with
documentation addresses only (RFC 5737). The collector's own container address
was replaced by 203.0.113.1.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from maxguard.adapters.base import read_log
from maxguard.adapters.netflow import NetflowAdapter, flow_uid, to_conn
from maxguard.events.normalize import normalize
from maxguard.pipeline import analyze, pick_adapter

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "netflow" / "goflow2.json"
TELNET_FLOW = {
    "type": "NETFLOW_V5", "time_received_ns": 1791323155565530742, "sequence_num": 0,
    "sampling_rate": 0, "sampler_address": "203.0.113.1",
    "time_flow_start_ns": 1791295190000000000, "time_flow_end_ns": 1791295192000000000,
    "bytes": 900, "packets": 12, "src_addr": "192.0.2.10", "dst_addr": "198.51.100.20",
    "etype": "IPv4", "proto": "TCP", "src_port": 49152, "dst_port": 23,
    "icmp_type": 0, "icmp_code": 0,
}


def flow_folder(tmp_path: Path) -> Path:
    folder = tmp_path / "netflow"
    folder.mkdir()
    shutil.copy(FIXTURE, folder / "goflow2.json")
    return folder


def test_one_flow_becomes_a_conn_record():
    assert to_conn(TELNET_FLOW) == {
        "ts": 1791295190.0,
        "uid": flow_uid(TELNET_FLOW),
        "id.orig_h": "192.0.2.10", "id.orig_p": 49152,
        "id.resp_h": "198.51.100.20", "id.resp_p": 23,
        "proto": "tcp", "duration": 2.0,
        "orig_bytes": 900, "resp_bytes": 0,
        "mg_source": "netflow",
    }


def test_uid_is_deterministic_and_ignores_the_receive_time():
    again = dict(TELNET_FLOW, time_received_ns=1791399999000000000)  # read again later
    other = dict(TELNET_FLOW, bytes=901)  # a different flow
    assert flow_uid(TELNET_FLOW) == flow_uid(dict(TELNET_FLOW)) == flow_uid(again)
    assert flow_uid(other) != flow_uid(TELNET_FLOW)
    assert flow_uid(TELNET_FLOW).startswith("N") and len(flow_uid(TELNET_FLOW)) == 18


def test_netflow_v5_icmp_type_and_code_come_from_the_destination_port():
    ping = dict(TELNET_FLOW, proto="ICMP", src_port=0, dst_port=8 * 256 + 0)  # echo request
    conn = to_conn(ping)
    assert (conn["proto"], conn["id.orig_p"], conn["id.resp_p"]) == ("icmp", 8, 0)


def test_ipfix_icmp_uses_the_icmp_fields():
    ping = dict(TELNET_FLOW, type="IPFIX", proto="ICMP", dst_port=0, icmp_type=3, icmp_code=1)
    conn = to_conn(ping)
    assert (conn["id.orig_p"], conn["id.resp_p"]) == (3, 1)


def test_accepts_a_goflow2_folder_and_a_single_file(tmp_path):
    folder = flow_folder(tmp_path)
    assert NetflowAdapter().accepts(folder)
    assert NetflowAdapter().accepts(folder / "goflow2.json")
    assert pick_adapter(folder).name == "netflow"


def test_does_not_steal_other_inputs(tmp_path, fixture_dir, pcap_file):
    adapter = NetflowAdapter()
    zeek_folder = fixture_dir("telnet")  # conn.log + eve.json
    assert not adapter.accepts(zeek_folder)
    assert not adapter.accepts(zeek_folder / "eve.json")
    assert not adapter.accepts(pcap_file("telnet"))
    # A Zeek log folder that also holds a goflow2 file still belongs to ZeekLogAdapter.
    mixed = flow_folder(tmp_path)
    shutil.copy(zeek_folder / "conn.log", mixed / "conn.log")
    assert not adapter.accepts(mixed)
    assert pick_adapter(mixed).name == "zeek-logs"
    # A live sensor folder (zeek/<interval>/) belongs to LiveSensorAdapter.
    sensor = tmp_path / "sensor"
    (sensor / "zeek" / "2026-10-06-1400").mkdir(parents=True)
    shutil.copy(FIXTURE, sensor / "goflow2.json")
    assert not adapter.accepts(sensor)
    assert pick_adapter(sensor).name == "live"
    # An empty folder and a folder of other JSON are not flows.
    other = tmp_path / "other"
    other.mkdir()
    assert not adapter.accepts(other)
    (other / "settings.json").write_text('{"type": "settings"}\n')
    assert not adapter.accepts(other)


def test_to_zeek_logs_writes_a_sorted_conn_log(tmp_path):
    log_dir = NetflowAdapter().to_zeek_logs(flow_folder(tmp_path), tmp_path / "work")
    records = list(read_log(log_dir, "conn.log"))
    assert len(records) == 7  # 5 NetFlow v5 + 1 NetFlow v9 + 1 IPFIX
    assert [r["ts"] for r in records] == sorted(r["ts"] for r in records)
    assert {r["mg_source"] for r in records} == {"netflow"}
    ssh = [r for r in records if r["id.resp_p"] == 22]  # the NetFlow v9 flow
    assert ssh[0]["id.orig_h"] == "192.0.2.12" and ssh[0]["orig_bytes"] == 4200


def test_same_files_give_the_same_conn_log(tmp_path):
    folder = flow_folder(tmp_path)
    first = NetflowAdapter().to_zeek_logs(folder, tmp_path / "a") / "conn.log"
    second = NetflowAdapter().to_zeek_logs(folder, tmp_path / "b") / "conn.log"
    assert first.read_bytes() == second.read_bytes()


def test_duplicates_and_a_half_written_line_are_skipped(tmp_path):
    folder = flow_folder(tmp_path)
    lines = FIXTURE.read_text().splitlines()
    # The same records again in a second file, then a line goflow2 is still writing.
    (folder / "goflow2-copy.json").write_text("\n".join(lines) + "\n" + lines[0][:40])
    log_dir = NetflowAdapter().to_zeek_logs(folder, tmp_path / "work")
    assert len(list(read_log(log_dir, "conn.log"))) == 7


def test_normalizer_reads_the_result_as_netflow(tmp_path):
    log_dir = NetflowAdapter().to_zeek_logs(flow_folder(tmp_path), tmp_path / "work")
    events = normalize(log_dir, sensor_id="router")
    assert len(events) == 7
    assert {(e["source"], e["kind"], e["sensor_id"]) for e in events} == {
        ("netflow", "conn", "router")}
    telnet = [e for e in events if e["dst_port"] == 23][0]
    assert (telnet["src_ip"], telnet["dst_ip"], telnet["proto"]) == (
        "192.0.2.10", "198.51.100.20", "tcp")
    assert (telnet["bytes_out"], telnet["bytes_in"]) == (900, 0)


def test_zeek_conn_records_stay_zeek(fixture_dir):
    events = normalize(fixture_dir("telnet"), sensor_id="pcap")
    assert {e["source"] for e in events if e["log"] == "conn.log"} == {"zeek"}


def test_analyze_flow_only_data(tmp_path):
    report = analyze(flow_folder(tmp_path), tmp_path / "work", explain=False)
    assert report["input"]["adapter"] == "netflow"
    assert report["findings"] == []  # no payload: no payload rule can fire
    assert len(report["events"]) == 7
    assert report["tools"] == {"zeek": False, "suricata": False}


def test_uploaded_flow_file_reaches_the_timeline(tmp_path):
    # The dashboard upload (and POST /api/ingest) store the file without its name,
    # so NetflowAdapter recognises one goflow2 file by its first line.
    from fastapi.testclient import TestClient

    from maxguard.api.app import create_app

    client = TestClient(create_app(tmp_path / "data", explain=False))
    with FIXTURE.open("rb") as f:
        reply = client.post("/api/analyses", files={"file": ("goflow2.json", f)})
    assert reply.status_code == 200, reply.text
    assert reply.json()["findings"] == 0
    events = client.get("/api/events", params={"ip": "192.0.2.10"}).json()
    assert len(events) == 5 and {e["source"] for e in events} == {"netflow"}  # 4 out, 1 in


def test_damaged_records_are_skipped_not_fatal(tmp_path):
    # An upload is untrusted: a record goflow2 would never write is skipped, the
    # good records still arrive, and nothing raises (a crash would be a 500).
    bad_records = [
        dict(TELNET_FLOW, bytes="900"),                 # text, not a number
        dict(TELNET_FLOW, dst_port=[23]),               # a list
        dict(TELNET_FLOW, bytes=2**70),                 # too large for the event store
        dict(TELNET_FLOW, time_flow_start_ns=-5),       # negative time
        dict(TELNET_FLOW, src_addr={"ip": "192.0.2.10"}),
        dict(TELNET_FLOW, dst_addr=None),
        dict(TELNET_FLOW, src_addr="not an address"),
    ]
    lines = [json.dumps(TELNET_FLOW)] + [json.dumps(r) for r in bad_records]
    lines += ['{"type": "IPFIX", "src_addr": "192.0.2.1", "bytes": 1e400}',
              "[" * 100_000 + "]" * 100_000]  # deeper than Python's recursion limit
    upload = tmp_path / "upload"
    upload.write_text("\n".join(lines) + "\n")
    assert NetflowAdapter().accepts(upload)
    records = list(read_log(NetflowAdapter().to_zeek_logs(upload, tmp_path / "w"), "conn.log"))
    assert [r["uid"] for r in records] == [flow_uid(TELNET_FLOW)]


def test_icmp_type_and_code_must_fit_in_a_byte():
    with pytest.raises(ValueError):
        to_conn(dict(TELNET_FLOW, type="IPFIX", proto="ICMP", icmp_type=300))


def test_uid_does_not_depend_on_the_order_of_the_fields():
    # Another goflow2 version may write the same fields in another order.
    reordered = dict(reversed(list(TELNET_FLOW.items())))
    assert flow_uid(reordered) == flow_uid(TELNET_FLOW)


def test_flow_without_flow_times_uses_the_receive_time():
    no_times = dict(TELNET_FLOW, time_flow_start_ns=0, time_flow_end_ns=0)
    conn = to_conn(no_times)
    assert (conn["ts"], conn["duration"]) == (1791323155.565531, 0.0)


def test_sflow_and_other_json_with_src_addr_are_not_flows(tmp_path):
    sflow = dict(TELNET_FLOW, type="SFLOW_5")  # sampled packets, not flow records
    for name, record in [("sflow", sflow), ("other", {"src_addr": "192.0.2.10"})]:
        path = tmp_path / name
        path.write_text(json.dumps(record) + "\n")
        assert not NetflowAdapter().accepts(path)
