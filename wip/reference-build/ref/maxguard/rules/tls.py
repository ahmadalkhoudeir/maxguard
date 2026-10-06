"""TLS rules (Fiona). Field names checked against Zeek 9.0.0 ssl.log."""

from maxguard.adapters.base import read_log
from maxguard.ids import evidence
from maxguard.models import Finding
from maxguard.rules.base import rule

WEAK_VERSIONS = {"SSLv2", "SSLv3", "TLSv10", "TLSv11"}
WEAK_CIPHER_MARKERS = ("_NULL_", "_EXPORT", "_RC4_", "_DES_", "_3DES_", "_anon_")


def _finding(rec, rule_id, title, severity, details):
    return Finding(rule_id=rule_id, title=title, severity=severity,
                   src_ip=rec["id.orig_h"], dst_ip=rec["id.resp_h"],
                   dst_port=int(rec["id.resp_p"]), protocol="tls",
                   first_seen=float(rec["ts"]), last_seen=float(rec["ts"]),
                   details=details, evidence=[evidence("ssl.log", rec)])


@rule("tls.weak_version")
def weak_version(log_dir):
    return [_finding(r, "tls.weak_version", f"Outdated protocol {r['version']}",
                     "high", {"version": r["version"], "server_name": r.get("server_name")})
            for r in read_log(log_dir, "ssl.log") if r.get("version") in WEAK_VERSIONS]


@rule("tls.weak_cipher")
def weak_cipher(log_dir):
    return [_finding(r, "tls.weak_cipher", f"Weak cipher {r['cipher']}",
                     "high", {"cipher": r["cipher"]})
            for r in read_log(log_dir, "ssl.log")
            if r.get("cipher") and any(m in r["cipher"] for m in WEAK_CIPHER_MARKERS)]
