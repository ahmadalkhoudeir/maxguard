"""Suricata eve.json checks (Karthik, KAR-03): Community ID and JA4 for every capture.

The eve.json in each tests/fixtures/zeek/<capture>/ folder was written by
Suricata 7.0.10 with MaxGuard's settings (scripts/make_fixtures.sh). For each one:
1. every record has a Community ID, the key that links it to Zeek's records;
2. Zeek's conn.log has the same Community IDs (both tools must use seed 0);
3. every TLS record whose client hello Suricata saw has a JA4;
4. maxguard.events.normalize copies that JA4 onto the normalized event.

These read saved files only, so they run with the unit tests. To check fresh
output the same way, write it to another folder and point FIXTURES_DIR there
(the same variable scripts/make_fixtures.sh uses):
    FIXTURES_DIR=/tmp/fresh bash scripts/make_fixtures.sh
    FIXTURES_DIR=/tmp/fresh pytest tests/unit/test_suricata_eve.py -q
"""

from __future__ import annotations

import os
import re
from pathlib import Path

import pytest

from maxguard.adapters.base import read_log
from maxguard.events.normalize import normalize
from maxguard.ids import record_id

DEFAULT_FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "zeek"
FIXTURES = Path(os.environ.get("FIXTURES_DIR", DEFAULT_FIXTURES))
# One folder per lab capture. _handmade/ has no eve.json directly inside, so it is left out.
EVE_FOLDERS = sorted(p.parent for p in FIXTURES.glob("*/eve.json"))

# Community ID version 1: "1:" and the base64 text of a 20-byte SHA-1 hash (28 characters).
COMMUNITY_ID = re.compile(r"^1:[A-Za-z0-9+/]{27}=$")
# JA4 as Suricata writes it: 10 characters (protocol, TLS version, domain or IP,
# number of ciphers, number of extensions, first ALPN), then two 12-character hashes.
JA4 = re.compile(r"^[a-zA-Z0-9]{10}_[0-9a-f]{12}_[0-9a-f]{12}$")


def eve_records(folder: Path) -> list[dict]:
    return list(read_log(folder, "eve.json"))


def client_hellos(folder: Path) -> list[dict]:
    """The eve "tls" records whose client hello Suricata parsed. The server name (SNI)
    is sent only in the client hello, so a record with an "sni" proves Suricata saw it."""
    return [rec for rec in eve_records(folder)
            if rec["event_type"] == "tls" and rec["tls"].get("sni")]


def test_there_are_eve_files_to_check():
    assert EVE_FOLDERS, f"no <capture>/eve.json under {FIXTURES}"


@pytest.mark.parametrize("folder", EVE_FOLDERS, ids=lambda p: p.name)
def test_every_record_has_a_community_id(folder):
    for rec in eve_records(folder):
        assert COMMUNITY_ID.match(rec.get("community_id", "")), rec["event_type"]


@pytest.mark.parametrize("folder", EVE_FOLDERS, ids=lambda p: p.name)
def test_zeek_logged_the_same_community_ids(folder):
    zeek_ids = {rec.get("community_id") for rec in read_log(folder, "conn.log")}
    for rec in eve_records(folder):
        assert rec["community_id"] in zeek_ids, rec["event_type"]


@pytest.mark.parametrize("folder", EVE_FOLDERS, ids=lambda p: p.name)
def test_every_client_hello_has_a_ja4(folder):
    hellos = client_hellos(folder)
    for rec in hellos:
        assert JA4.match(rec["tls"].get("ja4", "")), rec["tls"]
    # Zeek is a second witness, so this test cannot pass by checking nothing: every
    # TLS session in Zeek's ssl.log must be one of the client hellos above (every
    # lab client sends a server name). normalize() gives Zeek's TLS events the
    # Community ID of their connection.
    zeek_sessions = {e["community_id"] for e in normalize(folder, sensor_id="pcap")
                     if e["source"] == "zeek" and e["kind"] == "tls"}
    assert zeek_sessions == {rec["community_id"] for rec in hellos}


@pytest.mark.parametrize("folder", EVE_FOLDERS, ids=lambda p: p.name)
def test_normalize_puts_the_ja4_on_the_event(folder):
    events = {e["event_id"]: e for e in normalize(folder, sensor_id="pcap")}
    for rec in client_hellos(folder):
        event = events[record_id("eve.json", rec)]  # event_id is the record's ID
        assert event["kind"] == "tls"
        assert event["ja4"] == rec["tls"].get("ja4", "")  # a missing JA4 fails the test above
