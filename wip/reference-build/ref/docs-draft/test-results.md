# Test results: the lab captures, checked two ways

*Karthik (KAR-03, KAR-04, KAR-06). Recorded October 6, 2026, during planning.*

This page answers one question: **does MaxGuard find exactly what is in each lab
capture?** We do not trust MaxGuard to grade itself, so every capture was also
checked with a second, independent tool: **tshark**, the command-line version of
Wireshark. tshark has its own protocol decoders (it shares no code with Zeek,
Suricata or MaxGuard's rules), and every check below is one short display filter
you can read and rerun.

Result: **all 14 captures agree.** Each capture with a weakness gives exactly its
one finding in MaxGuard and matches exactly its one tshark check; the two clean
captures give no finding and match no weakness check.

## Versions used

| Tool | Version | Where it came from | License |
|---|---|---|---|
| Zeek | 9.0.0 | `zeek/zeek:9.0.0` | BSD-3-Clause |
| Suricata | 7.0.10 (JA4 support: yes, from `suricata --build-info`) | `jasonish/suricata:7.0.10` (`sha256:f8e7d04babeaab8bfac7e327b09e8f7471f144b0b205bfc503f7dd3130a6d2e7`, linux/amd64) | GPL-2.0 |
| tshark | 4.6.2 (Alpine package `tshark-4.6.2-r0`) | `nicolaka/netshoot:v0.15` (`sha256:47b907d662d139d1e2f22bfe14f4efca1e3f1feed283572f47c970c780c03b61`, linux/amd64) | GPL-2.0-or-later |
| ShellCheck | 0.11.0 | `koalaman/shellcheck:stable` (`sha256:bb596a0d169b85ddd81d8b6d3a2ff6d5baf5fca10b97f575ebc647c3dff62b3d`) | GPL-3.0 |
| Python | 3.13 (integration tests), 3.11 (unit tests) | engine stand-in image, `.venv` | PSF |

None of these is a new MaxGuard dependency: tshark and ShellCheck are only
used to check things, and nothing from them ships in MaxGuard.

## 1. MaxGuard compared with tshark

"Connections" is the number of TCP or UDP connections with at least one packet
that matches the filter. MaxGuard's `count` is how many times it saw the
problem; in these one-session captures both should be 1.

| Capture | MaxGuard finding (rule, port, count) | tshark check (display filter) | Connections | Agree |
|---|---|---|---|---|
| `telnet` | `cleartext.telnet`, 23, 1 | `telnet` | 1 (7 packets of Telnet text) | yes |
| `ftp` | `cleartext.ftp`, 21, 1 | `ftp.request.command == "PASS"` (password sent readable) | 1 | yes |
| `plain_http` | `cleartext.http`, 80, 1 | `http.request && tcp.dstport == 80` | 1 | yes |
| `plain_http_alt` | `cleartext.http_alt`, 8080, 1 | `http.request && tcp.dstport == 8080` | 1 | yes |
| `pop3` | `cleartext.pop3`, 110, 1 | `pop.request.command == "PASS"` | 1 | yes |
| `imap` | `cleartext.imap`, 143, 1 | `imap.request.command == "LOGIN"` | 1 | yes |
| `tls_weak_version` | `tls.weak_version`, 4431, 1 | `tls.handshake.type == 2 && tls.handshake.version <= 0x0302` (server picked TLS 1.1 or older) | 1 (server picked `0x0301` = TLS 1.0) | yes |
| `tls_weak_cipher` | `tls.weak_cipher`, 4432, 1 | `tls.handshake.type == 2 && tls.handshake.ciphersuite == 0x003b` | 1 (`TLS_RSA_WITH_NULL_SHA256`: no encryption) | yes |
| `cert_expired` | `cert.expired`, 4433, 1 | `all x509af.utcTime < "2026-10-06"` (both certificate dates before the capture day) | 1 (valid 2020-01-01 to 2020-12-31) | yes |
| `cert_weak_key` | `cert.weak_key`, 4434, 1 | `len(pkixalgs.modulus) < 257` (RSA key under 2048 bits) | 1 (129-byte modulus = 1024 bits) | yes |
| `cert_sha1` | `cert.sha1_signature`, 4435, 1 | `x509af.algorithm.id == 1.2.840.113549.1.1.5` (sha1WithRSAEncryption) | 1 | yes |
| `cert_self_signed` | `cert.self_signed`, 4437, 1 | issuer name equals subject name (tshark fields, compared with `awk`) | 1 (`selfsigned.lab.invalid` signed itself) | yes |
| `clean_tls13` | none | `tls.handshake.type == 2 && tls.handshake.extensions.supported_version == 0x0304` (TLS 1.3) | 1, and 0 for every weakness check | yes |
| `dns_lookup` | none | `dns.flags.response == 0` (DNS questions) | 1 UDP flow (3 questions, 3 answers), and 0 for every weakness check | yes |

Why some filters look the way they do:

- **`len(pkixalgs.modulus) < 257`.** A certificate stores the RSA modulus as a
  signed number, so a full 2048-bit modulus takes 257 bytes (256 plus a leading
  zero byte). Fewer than 257 bytes means fewer than 2048 bits. The weak key here
  is 129 bytes (1024 bits); the good keys are 257 bytes.
- **`all x509af.utcTime < "2026-10-06"`.** A certificate has two dates (not
  before, not after). `all` means both must be before the day the capture was
  recorded, which is what "expired" means. MaxGuard's rule also compares with the
  time the session was seen, never with today (CLAUDE.md rule 2).
- **Self-signed.** A display filter cannot compare two values of one field, so
  the script prints the issuer and subject names and `awk` compares them.
- **`clean_tls13`.** TLS 1.3 encrypts the certificate, so neither tshark nor Zeek
  can see it. This capture proves no rule fires on a modern TLS session; it does
  not prove anything about its certificate.

### Every check on every capture

The table above only shows each capture's own check. This one shows all of them:
the diagonal of 1s, with 0 everywhere else, is what lets each expected file say
which neighbouring rules must stay silent (`must_not_contain`).

| Capture | telnet | ftp pass | http 80 | http 8080 | pop3 pass | imap login | TLS ≤1.1 | NULL cipher | expired | RSA <2048 | SHA-1 | self-signed | TLS 1.3 | DNS |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `cert_expired` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **1** | 0 | 0 | 0 | 0 | 0 |
| `cert_self_signed` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **1** | 0 | 0 |
| `cert_sha1` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **1** | 0 | 0 | 0 |
| `cert_weak_key` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **1** | 0 | 0 | 0 | 0 |
| `clean_tls13` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **1** | 0 |
| `dns_lookup` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **1** |
| `ftp` | 0 | **1** | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `imap` | 0 | 0 | 0 | 0 | 0 | **1** | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `plain_http` | 0 | 0 | **1** | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `plain_http_alt` | 0 | 0 | 0 | **1** | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `pop3` | 0 | 0 | 0 | 0 | **1** | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `telnet` | **1** | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `tls_weak_cipher` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **1** | 0 | 0 | 0 | 0 | 0 | 0 |
| `tls_weak_version` | 0 | 0 | 0 | 0 | 0 | 0 | **1** | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

### How to rerun the tshark side

Save this script as `/tmp/crosscheck.sh` (it runs inside the netshoot
container, which has tshark):

```sh
#!/bin/sh
# Independent cross-check of the lab captures with tshark (Karthik, KAR-03).
# For every capture in /p and every check below, prints how many connections
# (TCP or UDP streams) have a packet that matches the check's display filter.
set -eu

# connections <capture> <display filter>
connections() {
  tshark -r "$1" -Y "$2" -T fields -e tcp.stream -e udp.stream 2> /dev/null | sort -u | grep -c . || true
}

# self_signed <capture>: certificates whose issuer name equals their subject name.
# A display filter cannot compare two values of one field, so awk does it.
self_signed() {
  tshark -r "$1" -Y "tls.handshake.type == 11" -T fields -e tcp.stream -e x509sat.uTF8String \
    2> /dev/null | awk -F '\t' '{ split($2, cn, ","); if (cn[1] == cn[2]) print $1 }' | sort -u | grep -c . || true
}

printf 'capture\ttelnet\tftp_pass\thttp_80\thttp_8080\tpop3_pass\timap_login\ttls_old\ttls_null\tcert_expired\tcert_small_rsa\tcert_sha1\tcert_self_signed\ttls13\tdns\n'
for pcap in /p/*.pcap; do
  printf '%s' "$(basename "$pcap" .pcap)"
  for filter in \
      'telnet' \
      'ftp.request.command == "PASS"' \
      'http.request && tcp.dstport == 80' \
      'http.request && tcp.dstport == 8080' \
      'pop.request.command == "PASS"' \
      'imap.request.command == "LOGIN"' \
      'tls.handshake.type == 2 && tls.handshake.version <= 0x0302' \
      'tls.handshake.type == 2 && tls.handshake.ciphersuite == 0x003b' \
      'all x509af.utcTime < "2026-10-06"' \
      'len(pkixalgs.modulus) < 257' \
      'x509af.algorithm.id == 1.2.840.113549.1.1.5'; do
    printf '\t%s' "$(connections "$pcap" "$filter")"
  done
  printf '\t%s' "$(self_signed "$pcap")"
  printf '\t%s' "$(connections "$pcap" 'tls.handshake.type == 2 && tls.handshake.extensions.supported_version == 0x0304')"
  printf '\t%s\n' "$(connections "$pcap" 'dns.flags.response == 0')"
done
```

Then, from the repository root (networking off: tshark only reads files;
`--user 65534:65534` runs it as the unprivileged "nobody" user):

```bash
docker run --rm --network none --user 65534:65534 -v "$PWD/tests/pcaps:/p:ro" \
  -v /tmp/crosscheck.sh:/crosscheck.sh:ro --entrypoint sh nicolaka/netshoot:v0.15 /crosscheck.sh \
  | expand -t 17
```

Expected output (takes about 30 seconds; every row has exactly one `1`):

```text
capture          telnet           ftp_pass         http_80          http_8080        pop3_pass        imap_login       tls_old          tls_null         cert_expired     cert_small_rsa   cert_sha1        cert_self_signed tls13            dns
cert_expired     0                0                0                0                0                0                0                0                1                0                0                0                0                0
cert_self_signed 0                0                0                0                0                0                0                0                0                0                0                1                0                0
cert_sha1        0                0                0                0                0                0                0                0                0                0                1                0                0                0
cert_weak_key    0                0                0                0                0                0                0                0                0                1                0                0                0                0
clean_tls13      0                0                0                0                0                0                0                0                0                0                0                0                1                0
dns_lookup       0                0                0                0                0                0                0                0                0                0                0                0                0                1
ftp              0                1                0                0                0                0                0                0                0                0                0                0                0                0
imap             0                0                0                0                0                1                0                0                0                0                0                0                0                0
plain_http       0                0                1                0                0                0                0                0                0                0                0                0                0                0
plain_http_alt   0                0                0                1                0                0                0                0                0                0                0                0                0                0
pop3             0                0                0                0                1                0                0                0                0                0                0                0                0                0
telnet           1                0                0                0                0                0                0                0                0                0                0                0                0                0
tls_weak_cipher  0                0                0                0                0                0                0                1                0                0                0                0                0                0
tls_weak_version 0                0                0                0                0                0                1                0                0                0                0                0                0                0
```

### How the MaxGuard side was made

The same command a user runs, once per capture, inside the engine image
(networking off):

```bash
for p in tests/pcaps/*.pcap; do
  printf '%-17s ' "$(basename "$p" .pcap)"
  docker run --rm --network none -v "$PWD/tests/pcaps:/p:ro" maxguard:2.0.0a0 \
    maxguard analyze "/p/$(basename "$p")" --no-ai \
    | python3 -c 'import json, sys; r = json.load(sys.stdin); print([(f["rule_id"], f["dst_port"], f["count"]) for f in r["findings"]] or "no findings")'
done
```

*Not run as written: in planning the engine image could not be built (Debian's
package servers were unreachable). The same loop ran in a stand-in image with the
same Zeek 9.0.0 base and Python 3.13 but no Suricata, calling the CLI from the
checkout (`python -m cli.main analyze <capture> --no-ai`).* Output:

```text
cert_expired      [('cert.expired', 4433, 1)]
cert_self_signed  [('cert.self_signed', 4437, 1)]
cert_sha1         [('cert.sha1_signature', 4435, 1)]
cert_weak_key     [('cert.weak_key', 4434, 1)]
clean_tls13       no findings
dns_lookup        no findings
ftp               [('cleartext.ftp', 21, 1)]
imap              [('cleartext.imap', 143, 1)]
plain_http        [('cleartext.http', 80, 1)]
plain_http_alt    [('cleartext.http_alt', 8080, 1)]
pop3              [('cleartext.pop3', 110, 1)]
telnet            [('cleartext.telnet', 23, 1)]
tls_weak_cipher   [('tls.weak_cipher', 4432, 1)]
tls_weak_version  [('tls.weak_version', 4431, 1)]
```

The same 14 results came out when Suricata 7.0.10 also ran (`report["tools"]`
was `{'zeek': True, 'suricata': True}` for every capture, and every TLS capture
got a JA4, for example `t10d230600_44099cda8a52_242d16716555` for
`tls_weak_version`). Suricata adds events (JA4, Community ID) but no findings in
v2.0-alpha, because `maxguard/suricata/rules/maxguard.rules` is still empty.

## 2. Integration tests (KAR-03, KAR-04)

`tests/integration/test_pcaps.py` runs the real pipeline on every capture and
compares with `tests/expected/<capture>.json`; `tests/integration/test_determinism.py`
analyzes every capture twice and compares the two reports.

Two runs in the stand-in image (networking off), with the repository mounted:

```text
== run 1
..............................s                                          [100%]
=========================== short test summary info ============================
SKIPPED [1] tests/integration/test_pcaps.py:69: suricata is not installed here; the engine image has it
30 passed, 1 skipped, 537 deselected in 24.95s
== run 2
..............................s                                          [100%]
=========================== short test summary info ============================
SKIPPED [1] tests/integration/test_pcaps.py:69: suricata is not installed here; the engine image has it
30 passed, 1 skipped, 537 deselected in 27.69s
```

The 30 tests: 14 captures, 1 "every capture has an expected file", 14
determinism tests, and the API upload test (JAI-07). The skipped one,
`test_zeek_and_suricata_both_ran`, needs Suricata; in the engine image (which has
it) it runs, and CI's `suricata -V` step fails if Suricata is ever missing.

**The Suricata path was also checked in planning**, by running the same two test
files with Zeek 9.0.0 and Suricata 7.0.10 taken from their official images
(a planning-only setup, not a step for you): `30 passed, 1 deselected in 59.72s`,
so `test_zeek_and_suricata_both_ran` passed and the reports were identical twice
even with Suricata's random `flow_id` values in `eve.json`.

### What a failure looks like

To prove the tests can fail, planning ran them with two deliberate breakages:

- Zeek **without `-D`** (random connection IDs): the determinism test failed and
  named the values that changed:

  ```text
  E       AssertionError: report['events'][0]['event_id']: 'bbd7657c05875bf9' != 'e194059dc0684047'
  E         report['events'][0]['uid']: 'CVMEphCWuT6KpTUQg' != 'CeUBb01T2VDCDQU2S6'
  E         report['findings'][0]['evidence'][0]['record_id']: '7f3d21c7f2629d9b' != '9f57616dfb7046b2'
  E         report['findings'][0]['evidence'][0]['uid']: 'CVMEphCWuT6KpTUQg' != 'CeUBb01T2VDCDQU2S6'
  ```

- Zeek **without MaxGuard's `cleartext.zeek` script**: the three captures that
  need it failed, the other captures passed.

  ```text
  FAILED tests/integration/test_pcaps.py::test_capture_gives_the_expected_findings[imap]
  FAILED tests/integration/test_pcaps.py::test_capture_gives_the_expected_findings[pop3]
  FAILED tests/integration/test_pcaps.py::test_capture_gives_the_expected_findings[telnet]
  3 failed, 12 passed, 1 skipped in 12.08s
  ```

## 3. Suricata eve.json checks

`tests/unit/test_suricata_eve.py` reads each capture's `eve.json` fixture and
checks that every record has a Community ID, that Zeek's `conn.log` has the same
Community IDs, that every TLS record whose client hello Suricata saw has a JA4,
and that `maxguard.events.normalize` puts that JA4 on the normalized event.

```bash
pytest tests/unit/test_suricata_eve.py -q
```

```text
.........................................................                [100%]
57 passed in 0.08s
```

**Fresh output.** The fixtures could be stale, so Suricata 7.0.10 was run again
on two captures with MaxGuard's settings, networking off, and the same checks
ran on the new `eve.json` (Zeek's logs were copied from the fixtures: Zeek's
output is identical on every run, KAR-02 step 5):

```bash
FRESH=/tmp/fresh-eve
for name in tls_weak_version dns_lookup; do
  mkdir -p "$FRESH/$name"
  docker run --rm --network none --user "$(id -u):$(id -g)" --entrypoint suricata \
    -v "$PWD/tests/pcaps:/pcaps:ro" -v "$PWD/maxguard/suricata:/cfg:ro" -v "$FRESH/$name:/out" \
    jasonish/suricata:7.0.10 -c /cfg/maxguard-suricata.yaml -r "/pcaps/$name.pcap" -l /out \
    -k none --runmode single -S /cfg/rules/maxguard.rules
  cp tests/fixtures/zeek/"$name"/*.log "$FRESH/$name/"
done
FIXTURES_DIR="$FRESH" pytest tests/unit/test_suricata_eve.py -q
```

```text
i: suricata: This is Suricata version 7.0.10 RELEASE running in USER mode
W: counters: stats are enabled but no loggers are active
W: detect: 1 rule files specified, but no rules were loaded!
i: threads: Threads created -> W: 1 FM: 1 FR: 1   Engine started.
i: suricata: Signal Received.  Stopping engine.
i: pcap: read 1 file, 21 packets, 3094 bytes
...
.........                                                                [100%]
9 passed in 0.06s
```

The two warnings are expected: MaxGuard writes no statistics file, and its rule
file has no rules yet. The fresh `eve.json` files were identical to the fixtures
except for `flow_id` (random on every run, and ignored by MaxGuard's record IDs).

To prove these checks can fail, planning broke copies of three fixtures: a TLS
record without `ja4`, a DNS record with a different Community ID, and a TLS 1.3
record without its client hello. Each one made the matching test fail.

## 4. Live-sensor check script (KAR-06)

`scripts/live_check.sh <console URL> <lab service address>` makes one plain-HTTP
request and one Telnet connection to a lab test service, then polls the
console's `GET /api/alerts` every minute for up to 30 minutes until a
`cleartext.http` and a `cleartext.telnet` alert show traffic seen after the
start. It refuses any address outside the private ranges (RFC 1918) and the
documentation ranges (RFC 5737).

ShellCheck:

```bash
docker run --rm --network none -v "$PWD/scripts:/mnt:ro" koalaman/shellcheck:stable /mnt/live_check.sh && echo "shellcheck: no findings"
```

```text
shellcheck: no findings
```

**Local test** (planning): KAR-01's `lab-server` image as the lab test service on
an internal Docker network (address `172.19.0.2`), and a fake console on
`127.0.0.1:8765` (Python's `http.server` serving a JSON file that a background
job rewrites to "detect" Telnet after 2 s and HTTP after 4 s; an older alert
from an earlier run is in the file from the start and must be ignored).
`LIVE_CHECK_POLL_SECONDS=1 LIVE_CHECK_TIMEOUT_SECONDS=20`:

```text
sent: plain HTTP request to 172.19.0.2 port 80
sent: Telnet session to 172.19.0.2 port 23
waiting for the alerts (checking every 1 s, for up to 0 min 20 s)
cleartext.telnet alert after 0 min 2 s
cleartext.http alert after 0 min 4 s
PASS: both alerts appeared
exit code: 0
```

Only the Telnet alert appearing (`LIVE_CHECK_TIMEOUT_SECONDS=4`):

```text
cleartext.telnet alert after 0 min 1 s
FAIL: no cleartext.http alert
after 0 min 4 s
exit code: 1
```

Addresses outside the lab are refused before anything is sent (exit code 2):

```text
refused: 100.64.0.1 is not a lab address (allowed: 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16 and the documentation ranges 192.0.2.0/24, 198.51.100.0/24, 203.0.113.0/24; IPv4 numbers only)
```

(also refused: `127.0.0.1`, `172.32.0.1`, `192.169.0.1`, `010.0.0.1`,
`256.1.1.1`, `2001:db8::1`, the name `lab-server`). The address rule was compared
with Python's `ipaddress` module on 3,574 addresses, including both ends of every
allowed range and the addresses just outside them: no differences.

**With the real console.** The probes' own traffic was recorded with tcpdump at
the lab service, and 5 seconds after the start the capture was uploaded to the
real API (`POST /api/analyses`, standing in for the sensor's shipping; it answered
`"findings": 2`). The script saw both alerts after 8 seconds. On a second run,
when the alerts already existed, it saw them after 9 seconds: their `count` went
from 1 to 2 and `last_seen` moved past the new start. So the probes trigger
exactly the two rules the script waits for, and a repeat run is not fooled by the
alerts of an earlier run.

**Real lab run: not run — verify on hardware.** It needs the Raspberry Pi
sensor, the mirror port and the live shipping of JAK-07. Record the three runs
in `docs/testing/live-sensor.md`.
