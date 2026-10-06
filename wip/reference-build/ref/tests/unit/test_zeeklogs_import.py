"""Importing existing Zeek logs (FIO-02): TSV typing, eve.json, gzip archives, safety limits.

These tests use the TLS and certificate rules, so they come with FIO-02.
"""

import gzip
import shutil
import tarfile
import zipfile
from pathlib import Path

import pytest

import maxguard.rules  # noqa: F401  (importing registers every rule)
from maxguard.adapters import zeeklogs
from maxguard.adapters.base import read_log
from maxguard.adapters.zeeklogs import ArchiveTooLarge, ZeekLogAdapter
from maxguard.rules.base import run_all

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "zeek"


def test_tsv_certificate_logs_still_trigger_certificate_rules(tmp_path):
    # Zeek 9.0.0 TSV output of tests/pcaps/cert_expired.pcap. cert_chain_fps is a
    # vector; before the #types fix it stayed one string and cert rules found nothing.
    log_dir = ZeekLogAdapter().to_zeek_logs(FIXTURES / "_handmade" / "tsv_cert_expired", tmp_path)

    ssl = next(read_log(log_dir, "ssl.log"))
    assert isinstance(ssl["cert_chain_fps"], list)
    assert [f.rule_id for f in run_all(log_dir)] == ["cert.expired"]


def test_tsv_and_json_imports_give_the_same_finding_id(tmp_path):
    from_tsv = run_all(ZeekLogAdapter().to_zeek_logs(
        FIXTURES / "_handmade" / "tsv_cert_expired", tmp_path))
    from_json = run_all(FIXTURES / "cert_expired")
    assert [f.finding_id for f in from_tsv] == [f.finding_id for f in from_json]


def test_eve_json_is_kept(tmp_path):
    log_dir = ZeekLogAdapter().to_zeek_logs(FIXTURES / "tls_weak_version", tmp_path)
    events = list(read_log(log_dir, "eve.json"))
    assert {e["event_type"] for e in events} >= {"tls"}


def test_rotated_gzipped_logs_are_appended_in_order(tmp_path):
    # Zeek's own archive folders hold one gzipped file per hour, for example
    # ssl.00:00:00-01:00:00.log.gz. Both hours must end up in one ssl.log.
    src = tmp_path / "archive"
    src.mkdir()
    shutil.copy(FIXTURES / "tls_weak_version" / "conn.log", src / "conn.log")
    line = (FIXTURES / "tls_weak_version" / "ssl.log").read_text().splitlines()[0]
    for hour in ("00", "01"):
        with gzip.open(src / f"ssl.{hour}:00:00-{hour}:59:59.log.gz", "wt") as f:
            f.write(line + "\n")

    log_dir = ZeekLogAdapter().to_zeek_logs(src, tmp_path / "work")

    assert len(list(read_log(log_dir, "ssl.log"))) == 2
    [finding] = run_all(log_dir)
    assert finding.rule_id == "tls.weak_version" and finding.count == 2


def test_zip_and_tar_imports_match(tmp_path):
    folder = FIXTURES / "tls_weak_version"
    z = tmp_path / "logs.zip"
    with zipfile.ZipFile(z, "w") as zf:
        for p in sorted(folder.iterdir()):
            zf.write(p, f"logs/{p.name}")
    t = tmp_path / "logs.tar.gz"
    with tarfile.open(t, "w:gz") as tf:
        tf.add(folder, arcname="logs")

    a = run_all(ZeekLogAdapter().to_zeek_logs(z, tmp_path / "a"))
    b = run_all(ZeekLogAdapter().to_zeek_logs(t, tmp_path / "b"))
    assert [f.to_dict() for f in a] == [f.to_dict() for f in b]


def test_archive_that_unpacks_too_large_is_refused(tmp_path, monkeypatch):
    monkeypatch.setattr(zeeklogs, "MAX_EXTRACTED_BYTES", 10)
    z = tmp_path / "big.zip"
    with zipfile.ZipFile(z, "w") as zf:
        zf.writestr("conn.log", "x" * 100)
    with pytest.raises(ArchiveTooLarge):
        ZeekLogAdapter().to_zeek_logs(z, tmp_path / "work")
