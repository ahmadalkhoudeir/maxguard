"""Per-device baselines and rule baseline.new_service (Fiona, FIO-07, proposed for v2.0 spring).

During a learning period MaxGuard records, per device IP address, which services
it uses: the set of (dst_port, proto, service) it connects to, plus how many
different peers it talks to. After the learning period, a device that uses a
service missing from its baseline gets a medium finding.

Why a second registry: a normal rule takes only a log folder, so the same logs
always give the same findings (CLAUDE.md rule 2). This rule also needs history.
The history (the baseline) and the end of the learning period are passed in
through `context`; the rule never reads the clock or a baseline file itself.
So the same logs plus the same context always give the same findings.
run_all() and the Fall 2026 RULES registry (maxguard/rules/base.py) do not change.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from maxguard.events.normalize import normalize
from maxguard.models import Evidence, Finding
from maxguard.rules.base import RULES, merge

RULE_ID = "baseline.new_service"

StatefulRule = Callable[[Path, dict], list[Finding]]
STATEFUL_RULES: dict[str, StatefulRule] = {}

# Zeek labels FTP data connections "ftp-data". Their port is picked fresh for every
# file transfer, so it would look "new" every time: leave them out of baselines.
IGNORED_SERVICES = frozenset({"ftp-data"})


def stateful_rule(rule_id: str):
    """Register a rule that takes (log_dir, context) instead of just log_dir."""
    def wrap(fn: StatefulRule) -> StatefulRule:
        if rule_id in STATEFUL_RULES or rule_id in RULES:  # rule IDs are unique across both
            raise ValueError(f"duplicate rule_id {rule_id!r}")
        STATEFUL_RULES[rule_id] = fn
        return fn

    return wrap


def run_stateful(log_dir: Path, context: dict) -> list[Finding]:
    """Run every stateful rule in rule_id order and merge the results (like run_all)."""
    found: list[Finding] = []
    for rule_id in sorted(STATEFUL_RULES):
        found.extend(STATEFUL_RULES[rule_id](log_dir, context))
    return merge(found)


def connections(events: list[dict]) -> list[dict]:
    """The events that describe one connection each (conn.log), with a destination port.

    http.log, ssl.log and eve.json describe the same connections again, so counting
    only conn events never counts a connection twice.
    """
    return [e for e in events
            if e["kind"] == "conn" and e["dst_port"] is not None
            and e["service"] not in IGNORED_SERVICES]


def service_key(event: dict) -> tuple[int, str, str]:
    return (int(event["dst_port"]), event["proto"], event["service"])


def build_baseline(events: list[dict]) -> dict:
    """Per device IP: the sorted (dst_port, proto, service) list it used and its peer count.

    `events` are normalized events (maxguard.events.normalize) from the learning
    period. The result only contains lists, strings and numbers in sorted order, so
    it can be stored as JSON, and the same events (in any order) give the same baseline.
    Example: {"192.0.2.10": {"peers": 1, "services": [[80, "tcp", "http"]]}}
    """
    services: dict[str, set[tuple[int, str, str]]] = {}
    peers: dict[str, set[str]] = {}
    for event in connections(events):
        device = event["src_ip"]
        services.setdefault(device, set()).add(service_key(event))
        peers.setdefault(device, set()).add(event["dst_ip"])
    return {device: {"peers": len(peers[device]),
                     "services": [list(key) for key in sorted(services[device])]}
            for device in sorted(services)}


def known_services(baseline: dict, device: str) -> set[tuple[int, str, str]]:
    """The device's services as tuples (JSON turned them into lists)."""
    return {tuple(key) for key in baseline[device]["services"]}


def is_known(key: tuple[int, str, str], known: set[tuple[int, str, str]]) -> bool:
    if key in known:
        return True
    # Zeek leaves service empty when it could not tell the protocol (for example a
    # connection that was refused). Same port and proto as a known service: not new.
    port, proto, service = key
    return service == "" and any(k[0] == port and k[1] == proto for k in known)


def new_service_finding(event: dict, learning_ends: float) -> Finding:
    ev = Evidence(log=event["log"], uid=event["uid"], ts=event["ts"],
                  record_id=event["event_id"])  # event_id is the record_id of the conn record
    return Finding(rule_id=RULE_ID, title="Device used a service new to it", severity="medium",
                   src_ip=event["src_ip"], dst_ip=event["dst_ip"],
                   dst_port=int(event["dst_port"]),
                   protocol=event["service"] or event["proto"],
                   first_seen=event["ts"], last_seen=event["ts"], source=event["source"],
                   details={"proto": event["proto"], "service": event["service"],
                            "learning_ends": learning_ends},
                   evidence=[ev])


@stateful_rule(RULE_ID)
def new_service(log_dir: Path, context: dict) -> list[Finding]:
    """A device used a (dst_port, proto, service) missing from its baseline.

    context["baseline"]: the dict from build_baseline() (for example loaded from storage)
    context["learning_ends"]: epoch seconds; events before it belong to the learning
    period and never give a finding.
    Devices without a baseline are skipped: there is nothing to compare them with
    (new devices show up in the device inventory instead).
    """
    baseline: dict = context["baseline"]
    learning_ends = float(context["learning_ends"])
    findings = []
    # sensor_id does not change any field this rule uses, so "" is fine here.
    for event in connections(normalize(log_dir, sensor_id="")):
        device = event["src_ip"]
        if event["ts"] < learning_ends or device not in baseline:
            continue
        if not is_known(service_key(event), known_services(baseline, device)):
            findings.append(new_service_finding(event, learning_ends))
    return findings
