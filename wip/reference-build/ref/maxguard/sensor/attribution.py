"""Device attribution (Jakub): which device is behind each IP address.

Two Zeek logs say who a device is:
- dhcp.log: the DHCP server gave address `assigned_addr` to the network card
  `mac`, and the device called itself `host_name`.
- dns.log: the device at `id.orig_h` asked for the name `query`.

build_device_table() joins them on the IP address, one row per IP:

    {"ip": "192.168.56.50", "mac": "02:00:00:aa:bb:cc", "host_name": "laptop-lab",
     "dns_names": ["printer.lab.invalid"], "first_seen": 1791252600.0}

mac and host_name are "" when no DHCP lease was seen (for example a device
with a fixed address). Like the rules, this never reads the clock, so the same
logs always give the same table in the same order.
"""

from __future__ import annotations

from pathlib import Path

from maxguard.adapters.base import read_log
from maxguard.inventory import ip_sort_key


def new_device(ip: str, ts: float) -> dict:
    return {"ip": ip, "mac": "", "host_name": "", "dns_names": set(), "first_seen": ts}


def device_for(devices: dict[str, dict], ip: str, ts: float) -> dict:
    """Get (or create) the device row for ip and keep its earliest timestamp."""
    if ip not in devices:
        devices[ip] = new_device(ip, ts)
    devices[ip]["first_seen"] = min(devices[ip]["first_seen"], ts)
    return devices[ip]


def leases(log_dir: Path) -> list[dict]:
    """dhcp.log records that handed out an address, oldest first.

    Sorting makes "the latest lease wins" well defined even if records are
    out of order (the MAC breaks ties so the order never depends on luck).
    """
    found = [r for r in read_log(log_dir, "dhcp.log") if r.get("assigned_addr")]
    return sorted(found, key=lambda r: (float(r["ts"]), r.get("mac") or ""))


def apply_lease(device: dict, rec: dict) -> None:
    """Record who holds the address now. A later lease replaces an earlier one."""
    mac = rec.get("mac") or ""
    if mac != device["mac"]:
        device["host_name"] = ""  # another card took the address: forget the old name
    device["mac"] = mac
    # renewals often leave out the host name, so keep the one we already know
    device["host_name"] = rec.get("host_name") or device["host_name"]


def finish(device: dict) -> dict:
    return {**device, "dns_names": sorted(device["dns_names"])}


def build_device_table(log_dir: Path) -> list[dict]:
    """One row per IP seen in a DHCP lease or as a DNS client, sorted by IP."""
    devices: dict[str, dict] = {}
    for rec in leases(log_dir):
        apply_lease(device_for(devices, rec["assigned_addr"], float(rec["ts"])), rec)
    for rec in read_log(log_dir, "dns.log"):
        if rec.get("query"):  # optional in dns.log: a message with no question has none
            device = device_for(devices, rec["id.orig_h"], float(rec["ts"]))
            device["dns_names"].add(rec["query"].lower())  # DNS names ignore case
    return [finish(devices[ip]) for ip in sorted(devices, key=ip_sort_key)]
