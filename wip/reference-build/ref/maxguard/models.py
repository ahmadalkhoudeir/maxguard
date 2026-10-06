"""Contract 1: the Finding dataclass (MaxGuard v2.0).

This is the original Fall 2026 contract with backward-compatible extensions.
Every original field keeps its name, type, position, and meaning. New fields
come after the original ones and all have defaults, so code written against
the original contract still works unchanged.

Who fills what:
- Rules fill every field from rule_id through evidence (plus source).
- The mapping layer fills controls and attack.
- The AI layer fills explanation_sentences and explanation.
- finding_id is computed automatically from the dedup key.
"""

from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass, field

SEVERITIES = ("critical", "high", "medium", "low", "info")


@dataclass
class Evidence:
    log: str  # e.g. "conn.log" or "eve.json"
    uid: str  # Zeek connection uid (for Suricata records: the Community ID)
    ts: float  # record timestamp (epoch seconds)
    record_id: str = ""  # v2.0: content hash of the exact log record (see maxguard.ids)


@dataclass
class Control:
    framework: str  # "PCI DSS", "NIST SP 800-53", "CISA CPG", "CJIS"
    version: str  # exactly as locked in docs/PROJECT_DECISIONS.md section 8
    control_id: str  # "4.2.1", "SC-8(1)", ...
    title: str
    rationale: str


@dataclass
class Technique:  # v2.0: MITRE ATT&CK technique, filled by the mapping layer
    technique_id: str  # "T1040"
    name: str  # "Network Sniffing"
    tactic: str  # "credential-access"
    version: str  # ATT&CK version, e.g. "v19.2"


@dataclass
class Sentence:  # v2.0: one AI sentence plus the evidence it cites
    text: str
    evidence_ids: list[str] = field(default_factory=list)  # Evidence.record_id values


def make_finding_id(rule_id: str, src_ip: str, dst_ip: str, dst_port: int) -> str:
    """Stable ID for one deduplicated finding. Same key in, same ID out."""
    key = f"{rule_id}|{src_ip}|{dst_ip}|{dst_port}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]


@dataclass
class Finding:
    # ---- original Fall 2026 fields (unchanged) ----
    rule_id: str  # stable key, e.g. "cleartext.telnet"
    title: str
    severity: str  # one of SEVERITIES
    src_ip: str
    dst_ip: str
    dst_port: int
    protocol: str  # "telnet", "tls", ...
    first_seen: float
    last_seen: float
    count: int = 1
    details: dict = field(default_factory=dict)
    evidence: list[Evidence] = field(default_factory=list)
    controls: list[Control] = field(default_factory=list)  # filled by mapping
    explanation: str | None = None  # filled by the AI layer
    # ---- v2.0 extensions (all optional) ----
    finding_id: str = ""  # computed in __post_init__ when empty
    source: str = "zeek"  # "zeek", "suricata", "netflow", "agent", "decoy"
    attack: list[Technique] = field(default_factory=list)  # filled by mapping
    explanation_sentences: list[Sentence] = field(default_factory=list)  # filled by AI

    def __post_init__(self) -> None:
        if self.severity not in SEVERITIES:
            raise ValueError(f"severity must be one of {SEVERITIES}, got {self.severity!r}")
        if not self.finding_id:
            self.finding_id = make_finding_id(
                self.rule_id, self.src_ip, self.dst_ip, self.dst_port
            )

    def to_dict(self) -> dict:
        return asdict(self)
