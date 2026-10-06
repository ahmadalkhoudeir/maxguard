"""Certificate rules (Fiona). Checked against Zeek 9.0.0.

In Zeek 9, x509.log has no connection fields (no uid, no IPs). Each
certificate is linked to the TLS session that carried it through
ssl.log's cert_chain_fps list, whose first entry is the server's (leaf)
certificate. Only leaf certificates are checked.
"""

from maxguard.adapters.base import read_log
from maxguard.ids import evidence
from maxguard.models import Finding
from maxguard.rules.base import rule


def _leaf_certs(log_dir):
    """Yield (ssl_record, x509_record) for every TLS session's leaf certificate."""
    certs = {c["fingerprint"]: c for c in read_log(log_dir, "x509.log")}
    for s in read_log(log_dir, "ssl.log"):
        fps = s.get("cert_chain_fps") or []
        if fps and fps[0] in certs:
            yield s, certs[fps[0]]


def _finding(s, c, rule_id, title, severity, details):
    ts = float(s["ts"])
    return Finding(rule_id=rule_id, title=title, severity=severity,
                   src_ip=s["id.orig_h"], dst_ip=s["id.resp_h"],
                   dst_port=int(s["id.resp_p"]), protocol="tls",
                   first_seen=ts, last_seen=ts,
                   details={"subject": c.get("certificate.subject"), **details},
                   evidence=[evidence("ssl.log", s), evidence("x509.log", c)])


@rule("cert.expired")
def expired(log_dir):
    # "Expired" means expired at the moment it was seen in the capture, not
    # today, so results never depend on when the analysis runs.
    return [_finding(s, c, "cert.expired", "Expired certificate", "high",
                     {"not_valid_after": c["certificate.not_valid_after"]})
            for s, c in _leaf_certs(log_dir)
            if float(c["certificate.not_valid_after"]) < float(s["ts"])]


@rule("cert.self_signed")
def self_signed(log_dir):
    return [_finding(s, c, "cert.self_signed", "Self-signed certificate", "medium",
                     {"issuer": c.get("certificate.issuer")})
            for s, c in _leaf_certs(log_dir)
            if c.get("certificate.subject") == c.get("certificate.issuer")]


@rule("cert.weak_key")
def weak_key(log_dir):
    return [_finding(s, c, "cert.weak_key",
                     f"Weak {c.get('certificate.key_length')}-bit RSA key", "high",
                     {"key_length": c.get("certificate.key_length")})
            for s, c in _leaf_certs(log_dir)
            if c.get("certificate.key_type") == "rsa"
            and int(c.get("certificate.key_length") or 0) < 2048]


@rule("cert.sha1_signature")
def sha1_signature(log_dir):
    return [_finding(s, c, "cert.sha1_signature", "Certificate signed with SHA-1", "medium",
                     {"sig_alg": c.get("certificate.sig_alg")})
            for s, c in _leaf_certs(log_dir)
            if "sha1" in (c.get("certificate.sig_alg") or "").lower()]
