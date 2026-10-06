"""Asset inventory (Jakub): one row per IP address seen in the logs.

Zeek writes three "asset" logs because maxguard/zeek/scripts/inventory.zeek
turns on tracking for ALL_HOSTS (by default Zeek only tracks hosts in its
local-networks list, which is empty in our setup):

- known_hosts.log    hosts that completed a TCP handshake
- known_services.log servers that answered on a port (TCP or UDP)
- software.log       client and server software named in the traffic

build() merges them into one dict per IP:

    {"ip": "172.18.0.2", "first_seen": 1791250493.372808,
     "services": ["80/http"], "software": ["SimpleHTTP 0.6-Python/3"],
     "finding_count": 1}

Like the rules, it never reads the clock, so the same logs always give the
same inventory in the same order.
"""

from __future__ import annotations

import ipaddress
from pathlib import Path

from maxguard.adapters.base import read_log
from maxguard.models import Finding


def ip_sort_key(ip: str) -> tuple[int, ipaddress.IPv4Address | ipaddress.IPv6Address]:
    """Sort IPs by number, so 172.18.0.10 comes after 172.18.0.2 (text order would not).

    The IP version comes first because Python cannot compare an IPv4 address
    with an IPv6 address directly.
    """
    address = ipaddress.ip_address(ip)
    return (address.version, address)


def service_names(rec: dict) -> list[str]:
    """Turn one known_services.log record into ["80/http", ...].

    Zeek writes service names in capitals ("HTTP") and an empty name when it
    could not tell the protocol; then we show the transport instead ("8080/tcp").
    """
    port = rec["port_num"]
    names = [name.lower() for name in rec.get("service") or [] if name]
    if not names:
        names = [rec.get("port_proto") or "unknown"]
    return [f"{port}/{name}" for name in names]


def software_version(rec: dict) -> str:
    """Rebuild the version text the way Zeek's software_fmt_version() does.

    Example: major 0, minor 6, addl "Python/3" -> "0.6-Python/3".
    """
    parts = [rec.get(f"version.{key}") for key in ("major", "minor", "minor2", "minor3")]
    numbers = [str(p) for p in parts if p is not None]
    if not numbers:
        return ""
    text = ".".join(numbers)
    if rec.get("version.addl"):
        text += f"-{rec['version.addl']}"
    return text


def software_name(rec: dict) -> str:
    """'name version', or just the name when Zeek found no version."""
    version = software_version(rec)
    return f"{rec['name']} {version}" if version else rec["name"]


def new_asset(ip: str, ts: float) -> dict:
    # sets while collecting (no duplicates); turned into sorted lists at the end
    return {"ip": ip, "first_seen": ts, "services": set(), "software": set(),
            "finding_count": 0}


def asset_for(assets: dict[str, dict], ip: str, ts: float) -> dict:
    """Get (or create) the asset for ip and keep its earliest timestamp."""
    if ip not in assets:
        assets[ip] = new_asset(ip, ts)
    assets[ip]["first_seen"] = min(assets[ip]["first_seen"], ts)
    return assets[ip]


def count_findings(assets: dict[str, dict], findings: list[Finding]) -> None:
    """Add one to finding_count for each finding an IP takes part in (as source or target).

    A host that appears only in a finding is still added, because imported Zeek
    logs may not include the known_*.log files.
    """
    for f in findings:
        for ip in {f.src_ip, f.dst_ip}:  # a set, so src == dst counts once
            asset_for(assets, ip, f.first_seen)["finding_count"] += 1


def finish(asset: dict) -> dict:
    """Turn the working sets into sorted lists (ports in number order)."""
    services = sorted(asset["services"], key=lambda s: (int(s.split("/")[0]), s))
    return {"ip": asset["ip"], "first_seen": asset["first_seen"], "services": services,
            "software": sorted(asset["software"]), "finding_count": asset["finding_count"]}


def build(log_dir: Path, findings: list[Finding]) -> list[dict]:
    """One asset dict per IP, sorted by IP. See the module docstring for the keys."""
    assets: dict[str, dict] = {}
    for rec in read_log(log_dir, "known_hosts.log"):
        asset_for(assets, rec["host"], float(rec["ts"]))
    for rec in read_log(log_dir, "known_services.log"):
        asset = asset_for(assets, rec["host"], float(rec["ts"]))
        asset["services"].update(service_names(rec))
    for rec in read_log(log_dir, "software.log"):
        asset = asset_for(assets, rec["host"], float(rec["ts"]))
        asset["software"].add(software_name(rec))
    count_findings(assets, findings)
    return [finish(assets[ip]) for ip in sorted(assets, key=ip_sort_key)]
