"""Preview before you block: what would this block have stopped? (Ahmad, AHM-07)

Before a person approves a block they see the connections of the last 7 days
that the block would have stopped: how many, which of our devices, which
services and ports, first and last seen, and up to 10 sample events.

window_end is passed in by the caller, never read from the clock here, so the
same events and the same window_end always give the same preview (and the tests
do not depend on today's date). Every list is sorted, so the order is fixed.

"inbound" means the address started the connection (it is the event's src_ip);
"outbound" means one of our devices started it (the address is the dst_ip).
This matches the generated firewall rules in generate.py.
"""

from __future__ import annotations

from maxguard.response.generate import check_direction, parse_ip, sides

WINDOW_SECONDS = 7 * 24 * 3600
MAX_SAMPLES = 10
MAX_EVENTS = 100_000  # a preview reads at most this many events (see "truncated")


def preview(ip: str, direction: str, event_store, *, window_end: float) -> dict:
    """Summarize the events in [window_end - 7 days, window_end) that the block matches."""
    address = str(parse_ip(ip))  # the same spelling as Zeek, e.g. "2001:db8::7"
    check_direction(direction)
    window_start = window_end - WINDOW_SECONDS
    events = event_store.query(ip=address, since=window_start, until=window_end,
                               limit=MAX_EVENTS)
    matched = [e for e in events if matches(e, address, direction)]
    matched.sort(key=lambda e: (e["ts"], e["event_id"]))
    return {
        "ip": address,
        "direction": direction,
        "window_start": window_start,
        "window_end": window_end,
        "connections": len({connection_key(e) for e in matched}),
        "events": len(matched),
        "devices": sorted({other_side(e, address) for e in matched}),
        "services": services(matched),
        "first_seen": matched[0]["ts"] if matched else None,
        "last_seen": matched[-1]["ts"] if matched else None,
        "samples": matched[:MAX_SAMPLES],
        "truncated": len(events) == MAX_EVENTS,  # there may be more than we read
    }


def matches(event: dict, address: str, direction: str) -> bool:
    """Would a block in this direction have stopped the connection of this event?"""
    wanted = sides(direction)
    if "inbound" in wanted and event["src_ip"] == address:
        return True
    return "outbound" in wanted and event["dst_ip"] == address


def connection_key(event: dict) -> str:
    """Zeek and Suricata events of one connection share a community_id (or a Zeek uid).

    Counting keys instead of events stops one connection counting three times
    (conn.log + ssl.log + eve.json)."""
    return event["community_id"] or event["uid"] or event["event_id"]


def other_side(event: dict, address: str) -> str:
    """The device at the other end of the connection: the one the block protects."""
    return event["dst_ip"] if event["src_ip"] == address else event["src_ip"]


def services(events: list[dict]) -> list[dict]:
    """Distinct (proto, dst_port, service) with how many events used each."""
    counts: dict[tuple, int] = {}
    for event in events:
        key = (event["proto"], event["dst_port"], event["service"])
        counts[key] = counts.get(key, 0) + 1
    rows = [{"proto": proto, "port": port, "service": service, "events": n}
            for (proto, port, service), n in counts.items()]
    return sorted(rows, key=service_order)


def service_order(row: dict) -> tuple:
    # A port can be None (e.g. DHCP) and None cannot be compared with a number,
    # so those rows sort first by using -1 in their place.
    port = -1 if row["port"] is None else row["port"]
    return (row["proto"], port, row["service"])
