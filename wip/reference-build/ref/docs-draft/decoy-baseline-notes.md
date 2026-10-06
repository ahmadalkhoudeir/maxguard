# Decoys and per-device baselines: build notes (Fiona, FIO-06 and FIO-07)

Notes from building the reference implementation on October 6, 2026. All
commands were run in the reference repo unless marked "not run".

## Files

| File | What it is |
|---|---|
| `maxguard/decoy/service.py` | asyncio listeners: Telnet (`login: `), FTP (`220 FTP server ready`), HTTP page titled "Printer admin". One JSON line per connection in `decoy.log`. |
| `maxguard/decoy/__main__.py` | `python -m maxguard.decoy`; settings from `MAXGUARD_DECOY_PORTS`, `MAXGUARD_DECOY_LOG`, `MAXGUARD_DECOY_HOST`, `MAXGUARD_DECOY_TIMEOUT`. |
| `maxguard/rules/decoy.py` | Rule `decoy.contact` (critical, `source="decoy"`). Not in `maxguard/rules/__init__.py` until the rule ID is approved. |
| `maxguard/rules/baseline.py` | `build_baseline(events)`, `STATEFUL_RULES`, `@stateful_rule`, `run_stateful()`, rule `baseline.new_service` (medium). |
| `docker/decoy-compose.yaml` | The decoy as its own container with its own LAN address (macvlan). |
| `tests/unit/test_decoy.py`, `tests/unit/test_baseline.py` | 11 + 11 tests. |

## decoy.log format

One JSON object per line, keys sorted:

```json
{"dst_ip": "172.18.0.2", "dst_port": 23, "first_bytes_hex": "726f6f740d0a", "service": "telnet", "src_ip": "172.18.0.3", "src_port": 59642, "ts": 1791322676.0507245}
```

`first_bytes_hex` is at most the first 64 bytes the client sent (`726f6f740d0a` is
`root\r\n`). The decoy reads at most 1024 bytes and waits at most 5 seconds
(`MAXGUARD_DECOY_TIMEOUT`), so a slow client cannot hold a connection open.
The line is written even when the client hangs up early or sends garbage: the
contact itself is the evidence. The evidence `record_id` of a finding is
`maxguard.ids.record_id("decoy.log", line)`, so the AI can cite it.

## Using the rule before it is registered

```python
from maxguard.rules.decoy import decoy_contact   # importing registers decoy.contact
findings = decoy_contact(Path("logs"))
```

## Tests

```bash
pytest tests/unit/test_decoy.py tests/unit/test_baseline.py -q -p no:cacheprovider
```

Expected output:

```
......................                                                   [100%]
22 passed in 0.85s
```

Same result on Python 3.13 inside `zeek/zeek:9.0.0` (`22 passed in 0.43s`).
The whole unit suite still passes (`791 passed, 1 skipped`).

"Never connects out" is tested by wrapping `socket.socket.connect` and
`connect_ex`: after a client talks to the decoy, the only connection recorded in
the process is the test's own connection to the decoy's port.

## The decoy in Docker (bridge network, run here)

macvlan needs a real network card on a real LAN (the decoy gets its own MAC
address on that LAN), so this sandbox proves the decoy on a user-defined bridge
network instead. Same code, same hardening flags as the compose file.

```bash
docker network create fiona-spring-net
docker run -d --name fiona-spring-decoy --network fiona-spring-net \
  --user 10001:10001 --read-only --cap-drop ALL --security-opt no-new-privileges:true \
  --sysctl net.ipv4.ip_unprivileged_port_start=0 \
  -e PYTHONDONTWRITEBYTECODE=1 -e PYTHONPATH=/src -e MAXGUARD_DECOY_LOG=/data/decoy.log \
  -e MAXGUARD_DECOY_TIMEOUT=2 \
  -v $PWD/maxguard:/src/maxguard:ro -v <empty folder>:/data \
  python:3.11-slim-bookworm python -m maxguard.decoy
docker logs fiona-spring-decoy
```

```
decoy ftp listening on 0.0.0.0:21
decoy http listening on 0.0.0.0:80
decoy telnet listening on 0.0.0.0:23
```

A plain container already has `net.ipv4.ip_unprivileged_port_start` = 0
(`docker run --rm python:3.11-slim-bookworm cat /proc/sys/net/ipv4/ip_unprivileged_port_start`
printed `0`); the compose file sets it explicitly so the non-root user can open
ports 21, 23 and 80 without depending on that default.

"Attacker" container (nicolaka/netshoot:v0.15):

```bash
docker run --rm --network fiona-spring-net nicolaka/netshoot:v0.15 sh -c '
printf "root\r\n" | nc -w 3 fiona-spring-decoy 23
printf "USER admin\r\n" | nc -w 3 fiona-spring-decoy 21
curl -s -m 5 http://fiona-spring-decoy/
head -c 300 /dev/urandom | nc -w 3 fiona-spring-decoy 23'
```

```
login:
220 FTP server ready
<!doctype html><html><head><title>Printer admin</title></head>...
login:
```

tcpdump in the decoy's network namespace during those four connections
(`docker run --network container:fiona-spring-decoy --cap-add NET_RAW --cap-add NET_ADMIN nicolaka/netshoot:v0.15 tcpdump -n -i eth0 -U -w /cap/decoy.pcap`):

```
IP 172.18.0.3.59642 > 172.18.0.2.23: Flags [S]
IP 172.18.0.2.23 > 172.18.0.3.59642: Flags [S.]
... (4 SYN from the client, 4 SYN-ACK from the decoy)
packets sent by the decoy with only SYN set: 0
UDP (DNS) packets from the decoy: 0
```

The decoy only answered: it opened no connection and made no DNS lookup.

Copy the log out and run the rule:

```bash
docker cp fiona-spring-decoy:/data/decoy.log logs/decoy.log
python -c "
from pathlib import Path
from maxguard.rules.base import merge
from maxguard.rules.decoy import decoy_contact
for f in merge(decoy_contact(Path('logs'))):
    print(f.severity, f.rule_id, f.src_ip, '->', f.dst_ip, f.dst_port, f.protocol, 'count', f.count)"
```

```
critical decoy.contact 172.18.0.3 -> 172.18.0.2 23 telnet count 2
critical decoy.contact 172.18.0.3 -> 172.18.0.2 21 ftp count 1
critical decoy.contact 172.18.0.3 -> 172.18.0.2 80 http count 1
```

Clean up: `docker rm -f fiona-spring-decoy && docker network rm fiona-spring-net`.

## docker/decoy-compose.yaml

```bash
docker compose -f docker/decoy-compose.yaml config
```

```
error while interpolating services.decoy.networks.decoy-lan.ipv4_address: required variable MAXGUARD_DECOY_IP is missing a value: set MAXGUARD_DECOY_IP to a free LAN address
```

That is on purpose: a default address could clash with a real device. With the
three values set (documentation addresses here; use your own LAN):

```bash
MAXGUARD_DECOY_SUBNET=192.0.2.0/24 MAXGUARD_DECOY_GATEWAY=192.0.2.1 \
MAXGUARD_DECOY_IP=192.0.2.250 docker compose -f docker/decoy-compose.yaml config
```

prints the resolved file (`driver: macvlan`, `parent: eth0`, `ipv4_address: 192.0.2.250`).
`MAXGUARD_DECOY_PARENT` defaults to `eth0`.

Facts from Docker's macvlan page (docker/docs repository,
`content/manuals/engine/network/drivers/macvlan.md`): the network card must accept
several MAC addresses ("promiscuous mode"), and "Containers attached to a macvlan
network cannot communicate with the host directly, this is a restriction in the
Linux kernel". So test the decoy from a laptop, not from the console.

Not run - verify on hardware: `docker compose -f docker/decoy-compose.yaml up -d` on a
real LAN, a connection from a laptop to the decoy address, and that connection
appearing as a critical alert in the dashboard (needs `decoy.log` shipped into the
console's log folder, see open questions).

## Baselines (FIO-07)

`build_baseline(events)` takes normalized events (`EVENT_KEYS`) from the learning
period and uses only `conn` events (http.log, ssl.log and eve.json describe the
same connections again). Device = `src_ip`. Output, ready for `json.dumps`:

```python
{"172.18.0.3": {"peers": 1, "services": [[80, "tcp", "http"], [4436, "tcp", "ssl"]]}}
```

Choices:

- `ftp-data` connections are left out: their port changes on every transfer.
- An event whose service is `""` (Zeek could not tell the protocol, for example a
  refused connection) is "known" when the device already used the same port and proto.
- Devices with no baseline are skipped (nothing to compare with; the device
  inventory shows new devices).
- The rule gets `context = {"baseline": ..., "learning_ends": <epoch seconds>}`;
  events before `learning_ends` never give a finding. It reads neither the clock
  nor a baseline file.
- `run_stateful(log_dir, context)` runs `STATEFUL_RULES` in rule_id order and
  merges like `run_all()`; `run_all()` is unchanged.
