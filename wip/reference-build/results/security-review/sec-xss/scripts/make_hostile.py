"""Write a synthetic Zeek-log folder (and a .zip of it) whose attacker-controlled
fields carry XSS, template-injection and CSV-formula payloads.

Base records are copied from the repo's synthetic fixtures (tests/fixtures/zeek),
only the attacker-controlled fields are replaced. Usage:
    python make_hostile.py <alpha repo> <out dir>
"""

import json
import sys
import zipfile
from pathlib import Path

# Distinct numbers so a fired dialog would tell which field leaked.
P_SCRIPT = "<script>alert(1)</script>"
P_IMG = "\"><img src=x onerror=alert(2)>"
P_JS = "javascript:alert(3)"
P_TPL = "{{7*7}}"
P_SVG = "'><svg onload=alert(5)>"

# IPv6 scope IDs accept any text without '%' or '/', and ipaddress.ip_address()
# (used by inventory.build) accepts them, so these survive the analysis.
SRC6 = "fe80::1%\"><svg onload=alert(11)>"
DST6 = "fe80::2%<img src=x onerror=alert(12)>"
DST6B = "fe80::3%javascript:alert(13)"
SRC6_TPL = "fe80::4%{{7*7}}"


def first(path: Path) -> dict:
    return json.loads(path.read_text().splitlines()[0])


def write(folder: Path, name: str, records: list[dict]) -> None:
    (folder / name).write_text("".join(json.dumps(r) + "\n" for r in records))


def build(repo: Path, out: Path) -> Path:
    fx = repo / "tests" / "fixtures" / "zeek"
    folder = out / "hostile_logs"
    folder.mkdir(parents=True, exist_ok=True)

    http = first(fx / "plain_http" / "http.log")
    http80 = {**http, "uid": "CHttp80" + P_SCRIPT, "host": P_IMG,
              "uri": "/" + P_SCRIPT + P_JS, "user_agent": P_TPL + P_SVG,
              "username": P_SCRIPT + P_TPL}
    http8080 = {**http, "uid": "CHttp8080", "id.resp_p": 8080, "id.orig_h": "172.18.0.7",
                "host": P_JS, "uri": "/" + P_IMG, "user_agent": P_SCRIPT}
    write(folder, "http.log", [http80, http8080])

    ftp = first(fx / "ftp" / "ftp.log")
    write(folder, "ftp.log", [{**ftp, "uid": "CFtp1", "user": P_SCRIPT + P_TPL,
                               "command": P_IMG}])

    telnet = first(fx / "telnet" / "maxguard_cleartext.log")
    write(folder, "maxguard_cleartext.log", [
        # hostile uid (shown in the evidence table) + an extra hostile user field
        {**telnet, "uid": P_IMG + P_SCRIPT, "user": P_SCRIPT + P_SVG},
        # hostile IPv6 scope IDs in both addresses (shown on every page)
        {**telnet, "uid": "CTelnet6", "id.orig_h": SRC6, "id.resp_h": DST6, "user": P_TPL},
        {**telnet, "uid": "CTelnet6b", "id.orig_h": SRC6_TPL, "id.resp_h": DST6B},
    ])

    ssl_self = first(fx / "cert_self_signed" / "ssl.log")
    x509 = first(fx / "cert_self_signed" / "x509.log")
    weak = first(fx / "tls_weak_cipher" / "ssl.log")
    write(folder, "ssl.log", [
        {**ssl_self, "uid": "CSsl1", "server_name": P_IMG + P_TPL},
        # the cipher name goes into the finding TITLE ("Weak cipher ..."); it only
        # has to contain one of the weak markers, e.g. "_NULL_"
        {**weak, "uid": "CSsl2", "id.resp_p": 4433,
         "cipher": "TLS_RSA_WITH_NULL_" + P_SCRIPT + P_TPL + "x;=1+1;y"},
    ])
    write(folder, "x509.log", [{**x509, "certificate.subject": P_SCRIPT + P_SVG,
                                "certificate.issuer": P_SCRIPT + P_SVG}])

    conn = first(fx / "telnet" / "conn.log")
    write(folder, "conn.log", [
        {**conn, "uid": "CConn1", "service": P_SCRIPT},
        {**conn, "uid": "CConn6", "id.orig_h": SRC6, "id.resp_h": DST6, "service": P_IMG},
    ])

    archive = out / "hostile_logs.zip"
    with zipfile.ZipFile(archive, "w") as z:
        for log in sorted(folder.iterdir()):
            z.write(log, arcname=log.name)
    return folder


if __name__ == "__main__":
    print(build(Path(sys.argv[1]), Path(sys.argv[2])))
