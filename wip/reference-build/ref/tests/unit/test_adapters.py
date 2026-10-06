"""Adapter tests (Fiona, FIO-01): which inputs each adapter accepts, and TSV -> JSON.

No test here runs Zeek: PcapAdapter.accepts() only reads the file's first
4 bytes ("magic number"), and ZeekLogAdapter only copies or converts logs.
"""

import struct
import zipfile
from pathlib import Path

import pytest

from maxguard.adapters.base import read_log
from maxguard.adapters.pcap import PcapAdapter
from maxguard.adapters.zeeklogs import ZeekLogAdapter

REPO = Path(__file__).resolve().parents[2]
PCAPS = REPO / "tests" / "pcaps"
FIXTURES = REPO / "tests" / "fixtures" / "zeek"


def pcap_header() -> bytes:
    """Classic pcap file header: magic, version 2.4, timezone, accuracy, snaplen, Ethernet."""
    return struct.pack("<IHHiIII", 0xA1B2C3D4, 2, 4, 0, 0, 65535, 1)


def pcapng_header() -> bytes:
    """pcapng Section Header Block: block type, length, byte-order magic, version 1.0,
    section length -1 ("unknown"), length again."""
    return struct.pack("<IIIHHqI", 0x0A0D0D0A, 28, 0x1A2B3C4D, 1, 0, -1, 28)


# ---- PcapAdapter: the magic number decides, not the file name ---------------

def test_pcap_adapter_accepts_a_lab_capture():
    assert PcapAdapter().accepts(PCAPS / "telnet.pcap")


@pytest.mark.parametrize(("name", "content"), [
    ("capture.pcap", pcap_header()),
    ("capture.pcapng", pcapng_header()),
    ("no_extension", pcap_header()),  # the extension does not matter
])
def test_pcap_adapter_accepts_pcap_and_pcapng(tmp_path, name, content):
    path = tmp_path / name
    path.write_bytes(content)
    assert PcapAdapter().accepts(path)


@pytest.mark.parametrize(("name", "content"), [
    ("notes.txt", b"hello, this is text\n"),
    ("fake.pcap", b"not a capture, just a .pcap name\n"),  # the extension does not help
    ("empty.pcap", b""),
])
def test_pcap_adapter_rejects_other_files(tmp_path, name, content):
    path = tmp_path / name
    path.write_bytes(content)
    assert not PcapAdapter().accepts(path)


def test_pcap_adapter_rejects_a_folder(tmp_path):
    assert not PcapAdapter().accepts(tmp_path)


# ---- ZeekLogAdapter: folders and archives of Zeek logs -----------------------

def test_zeek_log_adapter_accepts_a_folder_with_conn_log():
    assert ZeekLogAdapter().accepts(FIXTURES / "telnet")


def test_zeek_log_adapter_rejects_a_folder_without_conn_log(tmp_path):
    (tmp_path / "notes.txt").write_text("hello\n")
    assert not ZeekLogAdapter().accepts(tmp_path)


def test_json_logs_are_copied_unchanged(tmp_path):
    log_dir = ZeekLogAdapter().to_zeek_logs(FIXTURES / "telnet", tmp_path)

    for name in ("conn.log", "maxguard_cleartext.log"):
        assert (log_dir / name).read_bytes() == (FIXTURES / "telnet" / name).read_bytes()


def test_zip_of_logs_is_unpacked(tmp_path):
    archive = tmp_path / "telnet_logs.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        for log in sorted((FIXTURES / "telnet").glob("*.log")):
            zf.write(log, arcname=log.name)

    assert ZeekLogAdapter().accepts(archive)
    log_dir = ZeekLogAdapter().to_zeek_logs(archive, tmp_path / "work")
    assert (log_dir / "maxguard_cleartext.log").read_bytes() == (
        FIXTURES / "telnet" / "maxguard_cleartext.log").read_bytes()


# ---- TSV (Zeek's default log format) -> JSON ---------------------------------

TAB = "\t"
TSV_HEADER = [
    "#separator \\x09",
    "#set_separator" + TAB + ",",
    "#empty_field" + TAB + "(empty)",
    "#unset_field" + TAB + "-",
    "#path" + TAB + "conn",
    "#open" + TAB + "2026-10-06-01-52-44",
    TAB.join(["#fields", "ts", "uid", "id.orig_h", "id.orig_p", "id.resp_h", "id.resp_p",
              "proto", "service", "tunnel_parents"]),
    TAB.join(["#types", "time", "string", "addr", "port", "addr", "port",
              "enum", "string", "set[string]"]),
]
TSV_ROWS = [
    ["1791250000.100000", "C1aaaaaaaaaaaaaaaa", "192.168.56.50", "50001", "192.168.56.30", "23",
     "tcp", "-", "(empty)"],
    ["1791250001.200000", "C2bbbbbbbbbbbbbbbb", "192.168.56.50", "50002", "192.168.56.31", "80",
     "tcp", "http", "(empty)"],
    ["1791250002.300000", "C3cccccccccccccccc", "192.168.56.50", "53001", "192.168.56.1", "53",
     "udp", "dns", "(empty)"],
]


def write_tsv_conn_log(folder: Path) -> Path:
    folder.mkdir()
    lines = TSV_HEADER + [TAB.join(row) for row in TSV_ROWS] + ["#close" + TAB + "2026-10-06"]
    (folder / "conn.log").write_text("\n".join(lines) + "\n")
    return folder


def test_tsv_conn_log_becomes_one_json_record_per_row(tmp_path):
    tsv_dir = write_tsv_conn_log(tmp_path / "tsv")

    log_dir = ZeekLogAdapter().to_zeek_logs(tsv_dir, tmp_path / "work")
    records = list(read_log(log_dir, "conn.log"))

    assert len(records) == 3  # header and #close lines are not records
    assert [r["uid"] for r in records] == [row[1] for row in TSV_ROWS]
    first = records[0]
    assert first["id.resp_h"] == "192.168.56.30"
    # Values are converted with the #types header, the way Zeek writes JSON:
    # port -> int, time -> float, "-" (unset) -> None, "(empty)" set -> [].
    assert first["id.resp_p"] == 23
    assert first["ts"] == 1791250000.1
    assert first["service"] is None
    assert first["tunnel_parents"] == []
