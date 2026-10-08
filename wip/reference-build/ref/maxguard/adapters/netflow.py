"""NetflowAdapter: flow records from a router -> conn.log (Jakub, JAK-10).

A router that exports NetFlow v5, NetFlow v9 or IPFIX sends its flow records
over UDP to the goflow2 collector (docker/netflow-compose.yaml). goflow2 v2.2.7
writes one JSON object per flow, one per line, for example (shortened):

    {"type": "NETFLOW_V5", "time_received_ns": 1791323155565530742,
     "sequence_num": 0, "sampling_rate": 0, "sampler_address": "203.0.113.1",
     "time_flow_start_ns": 1791295190000000000, "time_flow_end_ns": 1791295192000000000,
     "bytes": 900, "packets": 12, "src_addr": "192.0.2.10", "dst_addr": "198.51.100.20",
     "proto": "TCP", "src_port": 49152, "dst_port": 23, "icmp_type": 0, "icmp_code": 0, ...}

This adapter turns each flow into a record shaped like a line of Zeek's
conn.log, plus "mg_source": "netflow", so the normalizer, the timeline and the
inventory work unchanged. Rules that need the payload (cleartext protocols,
TLS versions, certificates, JA4) find nothing, because a flow record has no
payload.

It accepts a folder of goflow2 JSON files (for example /data/netflow) or one
such file (what the dashboard upload and POST /api/ingest receive).

Differences from Zeek's conn.log, on purpose:
- A flow is one direction only (A -> B); a Zeek connection has both. So
  orig_bytes is the flow's byte count and resp_bytes is always 0; the answer
  B -> A is a separate flow record.
- There is no "service" (Zeek guesses it from the payload) and no conn_state.
- Byte counts are what the router reported. With packet sampling
  ("sampling_rate" > 1) the real traffic is about that many times larger.
"""

from __future__ import annotations

import hashlib
import ipaddress
import json
from pathlib import Path

# goflow2's "type" values for NetFlow v5, NetFlow v9 and IPFIX (its pb/flow.proto).
# sFlow ("SFLOW_5") is left out: it carries sampled packets, not flow records.
FLOW_TYPES = ("NETFLOW_V5", "NETFLOW_V9", "IPFIX")

# goflow2 writes the protocol by name. Zeek's conn.log uses "tcp", "udp", "icmp"
# (also for ICMPv6) and "unknown_transport" for everything else.
ZEEK_PROTOS = {"TCP": "tcp", "UDP": "udp", "ICMP": "icmp", "IPv6-ICMP": "icmp"}

# When the collector received the record is not part of the flow itself. Leaving
# it out of the hash gives a flow the same uid however often it is read.
NOT_PART_OF_FLOW = ("time_received_ns",)

# A goflow2 line is about 1.2 KB. Reading at most this much of a first line means
# a large binary file (a capture without newlines) is never read into memory.
MAX_FIRST_LINE = 64 * 1024

# The largest whole number the event store (SQLite INTEGER) can hold. goflow2's
# counters and nanosecond times always fit; a bigger value was not written by goflow2.
MAX_NUMBER = 2**63 - 1
MAX_PORT = 65535


def is_flow_record(rec: object) -> bool:
    return isinstance(rec, dict) and rec.get("type") in FLOW_TYPES and "src_addr" in rec


def first_record(path: Path) -> object:
    """The first non-empty line of a file, parsed as JSON (None if it is not JSON)."""
    with path.open("rb") as f:
        for _ in range(10):  # skip a few blank lines, never scan a whole file
            line = f.readline(MAX_FIRST_LINE)
            if not line:
                return None
            if line.strip():
                try:
                    return json.loads(line)
                except (ValueError, RecursionError):  # not JSON, not text, or absurdly nested
                    return None
    return None


def is_flow_file(path: Path) -> bool:
    return path.is_file() and is_flow_record(first_record(path))


def flow_files(path: Path) -> list[Path]:
    """The collector's files: the file itself, or a folder's *.json files that hold flows.

    Sorted, so the order never depends on how the disk lists the folder."""
    if path.is_file():
        return [path]
    return sorted(p for p in path.glob("*.json") if is_flow_file(p))


def read_flows(path: Path) -> list[dict]:
    """Every flow record of one file. Other lines (sFlow, a half-written last line) are skipped."""
    flows = []
    with path.open(errors="replace") as f:
        for line in f:
            try:
                rec = json.loads(line)
            except (ValueError, RecursionError):
                continue  # the collector may still be writing the last line
            if is_flow_record(rec):
                flows.append(rec)
    return flows


def flow_uid(flow: dict) -> str:
    """A deterministic uid: the same flow record always gets the same uid.

    Zeek's uids are random ("C" + 17 characters); this one is "N" (for NetFlow)
    + the first 17 hex digits of a SHA-256 of the record, so it has the same length."""
    stable = {k: v for k, v in flow.items() if k not in NOT_PART_OF_FLOW}
    text = json.dumps(stable, sort_keys=True, separators=(",", ":"))
    return "N" + hashlib.sha256(text.encode()).hexdigest()[:17]


def whole_number(value: object, largest: int = MAX_NUMBER) -> int:
    """A count, port or time from a flow record: a whole number from 0 to largest.

    goflow2 always writes these as JSON numbers; a missing one counts as 0.
    Anything else (text, a list, 1e400, a negative or huge number) means the line
    was not written by goflow2. ValueError then makes the caller skip the record,
    so a damaged or hostile upload cannot crash the analysis."""
    if value is None:
        return 0
    if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= largest:
        raise ValueError(f"not a whole number from 0 to {largest}: {value!r}")
    return value


def ip_text(value: object) -> str:
    """An IPv4 or IPv6 address as text; ValueError for anything else.

    The isinstance check matters: ipaddress also turns a plain number into an address."""
    if not isinstance(value, str):
        raise ValueError(f"not an IP address: {value!r}")
    return str(ipaddress.ip_address(value))


def seconds(nanoseconds: object) -> float:
    """goflow2 times are nanoseconds since 1970; Zeek's are seconds with 6 decimals."""
    return round(whole_number(nanoseconds) / 1e9, 6)


def ports(flow: dict, proto: str) -> tuple[int, int]:
    """Like Zeek: for ICMP the "ports" are the ICMP type and code."""
    if proto != "icmp":
        return (whole_number(flow.get("src_port"), MAX_PORT),
                whole_number(flow.get("dst_port"), MAX_PORT))
    if flow.get("type") == "NETFLOW_V5":
        # NetFlow v5 has no ICMP fields: the usual exporter convention puts
        # type * 256 + code in the destination port, and goflow2 passes that
        # number on unchanged (its producer_nflegacy.go copies the port).
        dst_port = whole_number(flow.get("dst_port"), MAX_PORT)
        return dst_port // 256, dst_port % 256
    return (whole_number(flow.get("icmp_type"), 255),
            whole_number(flow.get("icmp_code"), 255))


def to_conn(flow: dict) -> dict:
    """One goflow2 flow record -> one conn.log-shaped record.

    Raises ValueError if a field is not what goflow2 writes (see whole_number)."""
    start = seconds(flow.get("time_flow_start_ns"))
    end = seconds(flow.get("time_flow_end_ns"))
    if start == 0:  # some exporters leave the flow times out
        start = end = seconds(flow.get("time_received_ns"))
    proto = ZEEK_PROTOS.get(str(flow.get("proto")), "unknown_transport")
    orig_p, resp_p = ports(flow, proto)
    return {
        "ts": start,
        "uid": flow_uid(flow),
        "id.orig_h": ip_text(flow.get("src_addr")),
        "id.orig_p": orig_p,
        "id.resp_h": ip_text(flow.get("dst_addr")),
        "id.resp_p": resp_p,
        "proto": proto,
        "duration": round(max(end - start, 0.0), 6),
        "orig_bytes": whole_number(flow.get("bytes")),
        "resp_bytes": 0,  # one direction only: the answer is its own flow record
        "mg_source": "netflow",
    }


class NetflowAdapter:
    name = "netflow"

    def accepts(self, path: Path) -> bool:
        """goflow2 output (a file, or a folder of files), and nothing else.

        A Zeek log folder (it has conn.log) and a live sensor folder (it has
        zeek/) belong to the other adapters, even if a .json file is in them.
        A capture or an eve.json file fails the first-line check."""
        if path.is_file():
            return is_flow_file(path)
        if not path.is_dir() or (path / "conn.log").exists() or (path / "zeek").is_dir():
            return False
        return bool(flow_files(path))

    def to_zeek_logs(self, path: Path, workdir: Path) -> Path:
        conns: dict[str, dict] = {}
        for flow_file in flow_files(path):
            for flow in read_flows(flow_file):
                try:
                    conn = to_conn(flow)
                except (ValueError, RecursionError):
                    continue  # not what goflow2 writes: skip it, like a half-written line
                conns[conn["uid"]] = conn  # a record that appears twice is kept once
        out = workdir / "zeek_logs"
        out.mkdir(parents=True, exist_ok=True)
        with (out / "conn.log").open("w") as f:
            # Sorted by time, then uid: the same files always give the same conn.log.
            for conn in sorted(conns.values(), key=lambda c: (c["ts"], c["uid"])):
                f.write(json.dumps(conn) + "\n")
        return out
