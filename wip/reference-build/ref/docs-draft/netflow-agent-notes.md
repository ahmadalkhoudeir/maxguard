# NetFlow input (JAK-10) and host agent (JAK-11): builder notes

Written October 8, 2026 by the reference build for Jakub's guide. Everything
below was run in the sandbox unless it says "not run".

## JAK-10: NetFlow / IPFIX through goflow2

### Collector

- Image: `netsampler/goflow2:v2.2.7@sha256:b8fdc8f3666b05b0022ada3a3c8c50dcde97f7d19e3f42d050695fa0571fb952`
  (newest tag upstream: `git ls-remote --tags https://github.com/netsampler/goflow2` ends at v2.2.7;
  Docker Hub tag list shows linux/amd64 and linux/arm64 for that digest). Label
  `org.opencontainers.image.licenses=BSD-3-Clause`, revision 74af41b (= tag v2.2.7). Base: Alpine 3.24.2.
- Do not use `latest`: on Docker Hub it has the same digest as `v1.3.8` (the old v1 line).
- `docker run --rm --network none <image> -v` prints `GoFlow2 v2.2.7 (2026-09-30T06:45:52+0000)`.
- Flags (from `pkg/goflow2/config/config.go` and `config/common.go` at v2.2.7):
  `-listen` (default `sflow://:6343,netflow://:2055`; we use `netflow://:2055`: NetFlow v5, v9 and IPFIX),
  `-format` (default json), `-transport` (default file), `-transport.file` (empty = stdout),
  `-addr` (default `:8080`, the HTTP metrics/templates server; `-addr=` switches it off: `app.go` starts it only
  `if cfg.Addr != ""`). SIGHUP closes and reopens the output file (`transport/file/transport.go`).

### Commands and real output

```bash
sudo mkdir -p /data/netflow && sudo chown 1000:1000 /data/netflow
MAXGUARD_NETFLOW_ADDRESS=127.0.0.1 docker compose -f docker/netflow-compose.yaml up -d
docker compose -f docker/netflow-compose.yaml logs goflow2
```
```
level=INFO msg="starting GoFlow2"
level=INFO msg="starting collection" scheme=netflow hostname="" port=2055 count=1 workers=2 blocking=false queue_size=1000000
```
`docker inspect` of the container: user `1000:1000`, read-only root file system, all capabilities dropped,
port `127.0.0.1:2055->2055/udp`. Flow files are owned by 1000:1000.

Send test flows (generator below) from the host, or from a second container on the compose network
(`docker run --rm --network <project>_default -v $PWD/send_flows.py:/send_flows.py:ro python:3.11-slim-bookworm python3 /send_flows.py goflow2`):
```
sent 4 packets (2 NetFlow v5, 1 NetFlow v9, 1 IPFIX) to 127.0.0.1:2055
```
`wc -l /data/netflow/goflow2.json` -> `7` (5 v5 records, 1 v9, 1 IPFIX). Fields of one line (abridged):
```
NETFLOW_V5 192.0.2.10 49152 -> 198.51.100.20 23 TCP 900 bytes  start 1791295190000000000  end 1791295192000000000
NETFLOW_V5 192.0.2.10 0 -> 198.51.100.20 2048 ICMP   (v5 ICMP: icmp_type/icmp_code are 0, type*256+code is in dst_port)
NETFLOW_V9 192.0.2.12 50022 -> 198.51.100.22 22 TCP 4200
IPFIX      192.0.2.11 50000 -> 203.0.113.5 443 TCP 5200
```
Rotation (one file per period), verified:
```bash
mv /data/netflow/goflow2.json /data/netflow-done/2026-10-06-1400.json
docker compose -f docker/netflow-compose.yaml kill -s HUP goflow2
```
goflow2 created a new empty `goflow2.json`, kept running (restart count 0) and wrote the next flows into it.

Analyze (the folder, or upload the single file on the dashboard):
```python
from maxguard.pipeline import analyze
r = analyze("/data/netflow-done", "/tmp/work", explain=False)
```
```
adapter: netflow
findings: 0 []
tools: {'zeek': False, 'suricata': False}
netflow conn 192.0.2.10 49152 -> 198.51.100.20 23 tcp tcp/23 out=900 in=0 N1eb2a08b7a1c81b41
netflow conn 198.51.100.20 23 -> 192.0.2.10 49152 tcp tcp/49152 out=1400 in=0 Nebea0ae06570205ae
netflow conn 192.0.2.12 50022 -> 198.51.100.22 22 tcp tcp/22 out=4200 in=0 N3890d3923db8a0269
netflow conn 192.0.2.10 49153 -> 198.51.100.20 80 tcp tcp/80 out=640 in=0 N0a1e1408a253fc2cf
netflow conn 192.0.2.11 50000 -> 203.0.113.5 443 tcp tcp/443 out=5200 in=0 N6eb365175225fcf43
netflow conn 192.0.2.10 40000 -> 198.51.100.53 53 udp udp/53 out=60 in=0 Nbaefc50cb62acce14
netflow conn 192.0.2.10 8 -> 198.51.100.20 0 icmp icmp/0 out=84 in=0 N20beebab3404ae7b6
assets: []
same report twice: True
```

### Which rules fire on flow-only data, and why: none

- cleartext.* read ftp.log, http.log, maxguard_cleartext.log and rdp.log; tls.* and cert.* read ssl.log/x509.log;
  tls.ja4_watchlist reads eve.json. All of those come from looking inside packets. A flow record has only
  addresses, ports, protocol, byte and packet counts and times, so the adapter writes only conn.log.
  A flow to port 23 is NOT reported as cleartext.telnet: the rules need proof that the session really was
  Telnet (Zeek's protocol analysis), not just the port number. That is on purpose (deterministic, evidence-based).
- decoy.contact reads the decoy's own log. baseline.new_service is a stateful rule that analyze() does not run.
- The asset inventory is empty: maxguard.inventory.build reads known_hosts.log / known_services.log / software.log.
- What flows DO give: the timeline (GET /api/events), and later baselines and preview-before-you-block.

### Design notes for the guide

- uid: "N" + first 17 hex digits of SHA-256 of the record (sorted keys) minus `time_received_ns`. Same length as
  a Zeek uid. A record that appears twice (same file copied twice) is written once.
- A flow is one direction: orig_bytes = the flow's bytes, resp_bytes = 0; the reply is its own record.
- ICMP: Zeek puts type/code in id.orig_p/id.resp_p; the adapter does the same (v5: from dst_port, which goflow2's
  `producer_nflegacy.go` copies unchanged; v9/IPFIX: icmp_type/icmp_code).
- Byte counts are as exported; with sampling (`sampling_rate` > 1) real traffic is larger.
- accepts(): a goflow2 file (first line is a NETFLOW_V5/NETFLOW_V9/IPFIX record; at most 64 KiB read), or a
  folder of such *.json files without conn.log and without zeek/. Tested: not a Zeek fixture folder, not
  eve.json, not a pcap, not a Zeek folder that also holds goflow2.json, not a live-sensor folder.
- A single file is accepted because the dashboard upload and /api/ingest store uploads under a random name with
  no suffix; this is what makes the flows show on the timeline page (tested through TestClient).

### Flow generator used for step 6 (send_flows.py)

```python
"""Send a few made-up flow records to a NetFlow collector (Jakub, JAK-10 step 6).

NetFlow v5, NetFlow v9 and IPFIX, each with its own header. Only documentation
addresses (RFC 5737). Fixed times, so every run sends the same bytes.

    python3 send_flows.py <collector-host> [port]
"""

import socket
import struct
import sys

EXPORT_TIME = 1791295200  # 2026-10-06 14:00:00 UTC
UPTIME_MS = 600_000       # the router has been up for 10 minutes
TCP, UDP, ICMP = 6, 17, 1


def ip(text: str) -> bytes:
    return socket.inet_aton(text)


# ---------- NetFlow v5 (fixed layout: 24-byte header, 48-byte records) ----------

def v5_record(src, dst, sport, dport, proto, packets, octets, first_ms, last_ms) -> bytes:
    """One NetFlow v5 flow record. first/last are router uptimes in milliseconds."""
    tcp_flags = 0x1B if proto == TCP else 0  # FIN SYN PSH ACK
    return struct.pack("!4s4s4sHHIIIIHHBBBBHHBBH",
                       ip(src), ip(dst), ip("0.0.0.0"), 1, 2,  # next hop, in/out interface
                       packets, octets, first_ms, last_ms,
                       sport, dport, 0, tcp_flags, proto, 0,   # pad, flags, protocol, ToS
                       0, 0, 24, 24, 0)                        # AS numbers, masks, pad


def v5_packet(records: list[bytes], sequence: int) -> bytes:
    header = struct.pack("!HHIIIIBBH", 5, len(records), UPTIME_MS, EXPORT_TIME, 0,
                         sequence, 0, 0, 0)
    return header + b"".join(records)


# ---------- NetFlow v9 (RFC 3954) and IPFIX (RFC 7011): template, then data ----------

# (field type, length): IPv4 src, IPv4 dst, src port, dst port, protocol, bytes, packets
V9_FIELDS = [(8, 4), (12, 4), (7, 2), (11, 2), (4, 1), (1, 4), (2, 4), (22, 4), (21, 4)]
#                                                        FIRST_SWITCHED^  ^LAST_SWITCHED
IPFIX_FIELDS = [(8, 4), (12, 4), (7, 2), (11, 2), (4, 1), (1, 8), (2, 8), (152, 8), (153, 8)]
#                                              flowStartMilliseconds^    ^flowEndMilliseconds


def template_body(template_id: int, fields: list[tuple[int, int]]) -> bytes:
    body = struct.pack("!HH", template_id, len(fields))
    return body + b"".join(struct.pack("!HH", t, n) for t, n in fields)


def flow_set(set_id: int, body: bytes) -> bytes:
    return struct.pack("!HH", set_id, 4 + len(body)) + body


def v9_packet(sequence: int) -> bytes:
    """Template 256 (flowset id 0), then one data record: an SSH flow."""
    data = struct.pack("!4s4sHHBIIII", ip("192.0.2.12"), ip("198.51.100.22"), 50022, 22,
                       TCP, 4200, 30, UPTIME_MS - 8000, UPTIME_MS - 1000)
    flowsets = flow_set(0, template_body(256, V9_FIELDS)) + flow_set(256, data)
    # version, count (records incl. template), sysUptime, unix secs, sequence, source id
    return struct.pack("!HHIIII", 9, 2, UPTIME_MS, EXPORT_TIME, sequence, 1) + flowsets


def ipfix_packet(sequence: int) -> bytes:
    """Template 256 (set id 2), then one data record: an HTTPS flow."""
    start_ms = EXPORT_TIME * 1000 - 5000
    data = struct.pack("!4s4sHHBQQQQ", ip("192.0.2.11"), ip("203.0.113.5"), 50000, 443,
                       TCP, 5200, 14, start_ms, start_ms + 3000)
    sets = flow_set(2, template_body(256, IPFIX_FIELDS)) + flow_set(256, data)
    return struct.pack("!HHIII", 10, 16 + len(sets), EXPORT_TIME, sequence, 1) + sets


def main() -> None:
    host = sys.argv[1]
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 2055
    telnet = v5_record("192.0.2.10", "198.51.100.20", 49152, 23, TCP, 12, 900, 590_000, 592_000)
    answer = v5_record("198.51.100.20", "192.0.2.10", 23, 49152, TCP, 10, 1400, 590_010, 592_000)
    web = v5_record("192.0.2.10", "198.51.100.20", 49153, 80, TCP, 6, 640, 595_000, 595_500)
    dns = v5_record("192.0.2.10", "198.51.100.53", 40000, 53, UDP, 1, 60, 596_000, 596_000)
    ping = v5_record("192.0.2.10", "198.51.100.20", 0, 8 * 256 + 0, ICMP, 1, 84,
                     597_000, 597_000)  # echo request: type 8, code 0
    packets = [v5_packet([telnet, answer], 0), v5_packet([web, dns, ping], 2),
               v9_packet(0), ipfix_packet(0)]
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        for packet in packets:
            sock.sendto(packet, (host, port))
    print(f"sent {len(packets)} packets (2 NetFlow v5, 1 NetFlow v9, 1 IPFIX) to {host}:{port}")


if __name__ == "__main__":
    main()
```

## JAK-11: host agent

### Flags checked against the manuals

- tcpdump(1) (source of the man page: `tcpdump.1.in`, the-tcpdump-group/tcpdump master; published at
  https://www.tcpdump.org/manpages/tcpdump.1.html): -i, -n, -G ("rotates the dump file specified with the -w
  option every rotate_seconds seconds ... should include a time format as defined by strftime(3)"), -w, -Z ("after
  opening the capture device or input savefile, but before opening any savefiles for output, change the user ID to
  user"). tcpdump.c fills the -G pattern with `localtime()`, so the agent sets TZ=UTC.
- pktmon (MicrosoftDocs/windowsserverdocs, pktmon-start.md and pktmon-etl2pcap.md; published at
  https://learn.microsoft.com/windows-server/administration/windows-commands/pktmon-start and .../pktmon-etl2pcap):
  `--capture`, `--comp nics` ("NICs only"), `--pkt-size 0` ("To always log the entire packet, set this to 0.
  Default is 128 bytes"), `--file-name`, `pktmon stop`, `pktmon etl2pcap <file> --out <name>` (pcapng).
  pktmon's `multi-file` mode rotates by size only, so the agent stops and restarts pktmon every interval.

### tcpdump flags, run in a container on its own loopback (no network)

```bash
docker run --rm --network none --cap-add NET_RAW --cap-add NET_ADMIN -e TZ=UTC nicolaka/netshoot:v0.15 sh -c '
mkdir -p /spool && chown nobody /spool
tcpdump -i lo -n -G 2 -w "/spool/capture-%Y%m%d-%H%M%S.pcap" -Z nobody & P=$!
ping -i 0.5 -c 9 127.0.0.1 >/dev/null; kill -INT $P; wait $P; ls -ln /spool'
```
```
tcpdump version 4.99.6
libpcap version 1.10.6 (64-bit time_t, with TPACKET_V3)
-rw-r--r--    1 65534    65534          480 Oct  8 21:43 capture-20261008-214356.pcap
-rw-r--r--    1 65534    65534          936 Oct  8 21:44 capture-20261008-214358.pcap
-rw-r--r--    1 65534    65534          480 Oct  8 21:44 capture-20261008-214400.pcap
```
Files rotate every 2 s, names are UTC, and they belong to `nobody` (65534): -Z worked, so the spool folder must be
writable by capture_user.

### Config file (outside the repository, chmod 600)

`~/.config/maxguard/agent.toml` (Windows: `%APPDATA%\MaxGuard\agent.toml`):
```toml
console_url = "http://192.168.50.20:8001"   # YOUR OWN console, the LAN ingest port
token = "<the console's MAXGUARD_INGEST_TOKEN>"
spool_dir = "/home/alex/maxguard-spool"
sensor_id = "laptop"
capture_user = "alex"        # Linux/macOS: tcpdump -Z drops root to this user
interface = "eth0"           # optional
rotate_seconds = 900         # optional, at least 60
```
On the console: `MAXGUARD_INGEST_TOKEN` must be set (make one with
`python -c "import secrets; print(secrets.token_urlsafe(32))"`), otherwise /api/ingest answers 404 and the
ingest app on port 8001 refuses to start.

### Upload run against the real ingest app (uvicorn on 127.0.0.1:8001)

```bash
MAXGUARD_INGEST_TOKEN=$T MAXGUARD_DATA_DIR=/tmp/e2e/data uvicorn --factory maxguard.api.app:create_ingest_app --host 127.0.0.1 --port 8001
python -m maxguard.sensor.agent --config /tmp/e2e/agent.toml --upload-only
```
```
uploaded 1 file(s)
INFO:     127.0.0.1:48912 - "POST /api/ingest HTTP/1.1" 200 OK
```
The spool file moved to `spool/uploaded/`; the stored events carry `sensor_id` `laptop`. (The file was the goflow2
fixture under a capture name, because this sandbox host has no Zeek; a real pcap goes the same way.)

### Upload rules

- Only files the capture finished: names sort by UTC time; while the capture runs the newest is skipped.
- 2xx -> moved to `uploaded/` (newest 4 kept); 400/413 -> `rejected/`; anything else (unreachable, 401, 5xx)
  -> left in place and retried, oldest first.
- Run with sudo (tcpdump needs root to open the device, then drops to capture_user). Windows: an Administrator
  terminal.

### Not run

- A real capture on Linux, macOS (tcpdump -Z on macOS) or Windows (pktmon start/stop/etl2pcap): not run - verify on
  hardware. The Windows pcapng output going through Zeek: not run.

## Review fixes (October 8, 2026, adversarial review)

- NetflowAdapter: an uploaded flow file is untrusted. Before the fix, one damaged line after a good
  first line gave HTTP 500 on POST /api/analyses (tested: `"bytes": "abc"`, `"dst_port": [1]`,
  `"bytes": 1e400`, `"bytes": 2**70`, a 100,000-deep `[[[...]]]` line, `time_flow_start_ns` 10**40),
  and `"src_addr": null` or `{...}` was stored as the address. Now every number must be a whole JSON
  number from 0 to 2**63-1 (ports up to 65535, ICMP type/code up to 255), both addresses must parse
  with `ipaddress`, and a record that fails is skipped like a half-written line. All eight cases: 200.
- Agent upload: requests honours HTTP_PROXY/HTTPS_PROXY and ~/.netrc by default. Tested: with
  `HTTP_PROXY=http://127.0.0.1:9` the upload went to the proxy (ProxyError), and a ~/.netrc entry for
  the console replaced `Authorization: Bearer ...` with `Basic YWxpY2U6c2VjcmV0` (the netrc password).
  The agent now uses a `requests.Session` with `trust_env = False` (`console_session()`).
- tcpdump runs the whole `-w` name through strftime (tcpdump.c `MakeFilename`), so a `%` in spool_dir
  is now written `%%`.
- A spool folder created by the agent under sudo belonged to root, and tcpdump -Z (capture_user) could not
  write into it. `prepare_spool()` now gives a folder the agent creates to capture_user (an existing
  folder is never changed). `run_tcpdump()` returns tcpdump's exit code, so a failed start is not exit 0.
- `--upload-only` also sends the newest file: run it only while the agent is stopped (help text says so).
