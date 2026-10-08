"""Common event schema (v2.0): Zeek logs + Suricata eve.json -> one list of events.

Every event is a flat dict with exactly the keys in EVENT_KEYS, whatever tool
wrote the record, so the timeline, the event store and the inventory never
need to know Zeek's or Suricata's field names.

The output only depends on the log files (no clock, no randomness) and is
sorted by (ts, log, event_id), so the same logs always give the same list.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from maxguard.adapters.base import read_log
from maxguard.ids import iso_to_epoch, record_id

EVENT_KEYS = (
    "event_id", "ts", "sensor_id", "source", "log", "kind", "uid", "community_id",
    "src_ip", "dst_ip", "src_port", "dst_port", "proto", "service",
    "bytes_out", "bytes_in", "device_mac", "summary", "ja4",
)

KNOWN_PROTOS = ("tcp", "udp", "icmp")


# ---------- small helpers ----------

def new_event(log: str, rec: dict, sensor_id: str, source: str, kind: str, ts: float) -> dict:
    """An event with every key present; the converters below fill in what they know."""
    return {
        "event_id": record_id(log, rec), "ts": ts, "sensor_id": sensor_id,
        "source": source, "log": log, "kind": kind, "uid": "", "community_id": "",
        "src_ip": "", "dst_ip": "", "src_port": None, "dst_port": None,
        "proto": "", "service": "", "bytes_out": 0, "bytes_in": 0,
        "device_mac": "", "summary": "", "ja4": "",
    }


def as_int(value: object) -> int | None:
    """Zeek JSON logs hold numbers, but logs converted from TSV hold strings ("443")."""
    if value is None or value == "":
        return None
    return int(value)


def as_list(value: object) -> list[str]:
    """Zeek JSON logs hold lists, but TSV-converted logs hold one "a,b,c" string."""
    if value is None:
        return []
    if isinstance(value, str):
        return value.split(",")
    return [str(item) for item in value]


def proto_name(value: object) -> str:
    """"tcp", "udp", "icmp" or "". Suricata writes "TCP" and "IPv6-ICMP"."""
    name = str(value or "").lower()
    if name == "ipv6-icmp":
        return "icmp"
    return name if name in KNOWN_PROTOS else ""


def words(*parts: object) -> str:
    """Join the non-empty parts with spaces (for the short summary text)."""
    return " ".join(str(part) for part in parts if part not in (None, ""))


# ---------- Zeek logs ----------

def zeek_event(log: str, rec: dict, sensor_id: str, kind: str, service: str) -> dict:
    """The fields that conn, dns, http and ssl logs share: uid and the id.* 4-tuple."""
    event = new_event(log, rec, sensor_id, "zeek", kind, float(rec["ts"]))
    event["uid"] = rec.get("uid") or ""
    event["community_id"] = rec.get("community_id") or ""
    event["src_ip"] = rec.get("id.orig_h") or ""
    event["dst_ip"] = rec.get("id.resp_h") or ""
    event["src_port"] = as_int(rec.get("id.orig_p"))
    event["dst_port"] = as_int(rec.get("id.resp_p"))
    event["proto"] = proto_name(rec.get("proto"))  # http.log/ssl.log: filled from conn.log later
    event["service"] = service
    return event


def from_conn(rec: dict, sensor_id: str) -> dict:
    event = zeek_event("conn.log", rec, sensor_id, "conn", rec.get("service") or "")
    # Only conn events carry byte counts, so adding up bytes never counts twice.
    event["bytes_out"] = as_int(rec.get("orig_bytes")) or 0
    event["bytes_in"] = as_int(rec.get("resp_bytes")) or 0
    event["summary"] = words(f"{event['proto']}/{event['dst_port']}", event["service"],
                             rec.get("conn_state"), f"out={event['bytes_out']}",
                             f"in={event['bytes_in']}")
    return event


def from_dns(rec: dict, sensor_id: str) -> dict:
    event = zeek_event("dns.log", rec, sensor_id, "dns", "dns")
    answers = ",".join(as_list(rec.get("answers")))
    event["summary"] = words(rec.get("qtype_name"), rec.get("query"),
                             rec.get("rcode_name"), answers)
    return event


def from_http(rec: dict, sensor_id: str) -> dict:
    event = zeek_event("http.log", rec, sensor_id, "http", "http")
    event["summary"] = words(rec.get("method"), f"{rec.get('host') or ''}{rec.get('uri') or ''}")
    return event


def from_ssl(rec: dict, sensor_id: str) -> dict:
    # Zeek calls the TLS service "ssl" (conn.log service "ssl"), the event kind is "tls".
    event = zeek_event("ssl.log", rec, sensor_id, "tls", "ssl")
    event["summary"] = words(rec.get("version"), rec.get("server_name"), rec.get("cipher"))
    return event


def from_dhcp(rec: dict, sensor_id: str) -> dict:
    # dhcp.log is different: no id.* fields and no ports (Zeek does not log them),
    # and one record groups several packets, so it has a set of uids.
    event = new_event("dhcp.log", rec, sensor_id, "zeek", "dhcp", float(rec["ts"]))
    uids = sorted(as_list(rec.get("uids")))  # sorted: a set has no fixed order
    event["uid"] = uids[0] if uids else ""
    # Before the lease the client has no address yet; the assigned one is its new IP.
    event["src_ip"] = rec.get("client_addr") or rec.get("assigned_addr") or ""
    event["dst_ip"] = rec.get("server_addr") or ""
    event["proto"] = "udp"
    event["service"] = "dhcp"
    event["device_mac"] = rec.get("mac") or ""
    assigned = rec.get("assigned_addr")
    event["summary"] = words("/".join(as_list(rec.get("msg_types"))), event["device_mac"],
                             rec.get("host_name"), f"-> {assigned}" if assigned else "")
    return event


ZEEK_LOGS: dict[str, Callable[[dict, str], dict]] = {
    "conn.log": from_conn,
    "dns.log": from_dns,
    "http.log": from_http,
    "ssl.log": from_ssl,
    "dhcp.log": from_dhcp,
}


# ---------- Suricata eve.json ----------

def eve_event(rec: dict, sensor_id: str, kind: str) -> dict:
    """The fields every eve.json record shares. Suricata has no Zeek uid."""
    event = new_event("eve.json", rec, sensor_id, "suricata", kind,
                      iso_to_epoch(rec["timestamp"]))
    event["community_id"] = rec.get("community_id") or ""
    event["src_ip"] = rec.get("src_ip") or ""
    event["dst_ip"] = rec.get("dest_ip") or ""
    event["src_port"] = as_int(rec.get("src_port"))
    event["dst_port"] = as_int(rec.get("dest_port"))
    event["proto"] = proto_name(rec.get("proto"))
    event["service"] = rec.get("app_proto") or ""
    return event


def from_eve_alert(rec: dict, sensor_id: str) -> dict:
    event = eve_event(rec, sensor_id, "alert")
    alert = rec.get("alert") or {}
    event["summary"] = words(alert.get("signature"), f"(sid {alert.get('signature_id')})")
    return event


def from_eve_tls(rec: dict, sensor_id: str) -> dict:
    # Kept even though Zeek's ssl.log covers TLS: only Suricata computes JA4.
    event = eve_event(rec, sensor_id, "tls")
    tls = rec.get("tls") or {}
    event["service"] = event["service"] or "tls"
    event["ja4"] = tls.get("ja4") or ""
    event["summary"] = words(tls.get("version"), tls.get("sni"),
                             f"ja4={event['ja4']}" if event["ja4"] else "")
    return event


def dns_question(dns: dict) -> dict:
    """Suricata 7 (eve dns version 2) puts rrname/rrtype at the top of "dns";
    Suricata 8 (version 3) puts them in a "queries" list."""
    if "rrname" in dns:
        return dns
    queries = dns.get("queries") or [{}]
    return queries[0]


def from_eve_dns(rec: dict, sensor_id: str) -> dict:
    event = eve_event(rec, sensor_id, "dns")
    dns = rec.get("dns") or {}
    question = dns_question(dns)
    answers = ",".join(str(a.get("rdata", "")) for a in dns.get("answers") or [])
    event["service"] = event["service"] or "dns"
    event["summary"] = words(dns.get("type"), question.get("rrtype"), question.get("rrname"),
                             dns.get("rcode"), answers)
    return event


def from_eve_dhcp(rec: dict, sensor_id: str) -> dict:
    event = eve_event(rec, sensor_id, "dhcp")
    dhcp = rec.get("dhcp") or {}
    assigned = dhcp.get("assigned_ip")
    event["service"] = event["service"] or "dhcp"
    event["device_mac"] = dhcp.get("client_mac") or ""
    event["summary"] = words(dhcp.get("dhcp_type"), event["device_mac"], dhcp.get("hostname"),
                             f"-> {assigned}" if assigned else "")
    return event


# "flow" is left out on purpose: Zeek's conn.log already has one event per connection.
EVE_TYPES: dict[str, Callable[[dict, str], dict]] = {
    "alert": from_eve_alert,
    "tls": from_eve_tls,
    "dns": from_eve_dns,
    "dhcp": from_eve_dhcp,
}


# ---------- putting it together ----------

def fill_from_conn(events: list[dict]) -> None:
    """Zeek writes community_id only in conn.log, and http.log/ssl.log have no proto.
    Copy both from the conn event of the same connection (same uid), so every Zeek
    event lines up with the Suricata events of that connection."""
    conns = {e["uid"]: e for e in events if e["log"] == "conn.log" and e["uid"]}
    for event in events:
        conn = conns.get(event["uid"])
        if conn is not None:
            event["community_id"] = event["community_id"] or conn["community_id"]
            event["proto"] = event["proto"] or conn["proto"]


def normalize(log_dir: Path, sensor_id: str) -> list[dict]:
    """One event per record of the logs we know. Missing log files are simply skipped."""
    log_dir = Path(log_dir)
    events: list[dict] = []
    for log_name, convert in ZEEK_LOGS.items():
        for rec in read_log(log_dir, log_name):
            events.append(convert(rec, sensor_id))
    for rec in read_log(log_dir, "eve.json"):
        convert = EVE_TYPES.get(rec.get("event_type"))
        if convert is not None:
            events.append(convert(rec, sensor_id))
    fill_from_conn(events)
    events.sort(key=lambda e: (e["ts"], e["log"], e["event_id"]))
    return events
