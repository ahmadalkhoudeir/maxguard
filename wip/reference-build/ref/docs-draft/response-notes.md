# Response module notes (Ahmad, AHM-07 and AHM-08)

Notes for the guide in `docs/roadmap/ahmad.md` and `docs/ARCHITECTURE.md` section 13.
Everything below was run on October 6, 2026, unless marked **not run - verify on hardware**.

## What was built

| File | What it does |
|---|---|
| `maxguard/response/generate.py` | `rules_for(ip, direction) -> dict`: nftables (with a one-time setup file), iptables, OPNsense and home-router steps, each with its undo. `parse_ip()` is the only way an address gets in. |
| `maxguard/response/preview.py` | `preview(ip, direction, event_store, *, window_end)`: connections in `[window_end - 7 days, window_end)`, devices, services/ports, first/last seen, up to 10 samples. |
| `maxguard/response/approvals.py` | `ProposalStore(state_store)`: the table `response_proposals` in `state.db` and the steps propose, record_preview, approve, mark_applied, revert, reject. Every step calls `StateStore.add_audit` (`response.<step>`, target = proposal id). |
| `maxguard/response/routes.py` | `APIRouter` under `/api/response` (included by `create_app()`). |
| `maxguard/response/enforcers/base.py` | `Enforcer` protocol (`add(ip)`, `remove(ip)`, `apply()`) and `EnforcerError`. |
| `maxguard/response/enforcers/opnsense.py` | `OPNsenseEnforcer` for one firewall alias, `read_api_key()`, `from_env()`. |

### The steps (state machine)

```
proposed -> previewed -> approved -> applied -> reverted
proposed / previewed -> rejected
```

- Approve is only possible after a preview, and needs `actor` plus `confirm_ip`
  equal to the proposal's IP. A missing or wrong `confirm_ip` is refused with 400
  and audited as `response.approve_refused`.
- The check and the state change are one SQL `UPDATE ... WHERE state IN (...)`, so
  two people clicking at the same moment cannot both approve or both revert.
- An enforcer error keeps the state (`approved` or `applied`), is audited as
  `response.apply_failed` / `response.revert_failed`, and the API answers 502.
- Revert uses the same method as apply: a block applied by hand is undone by hand,
  a block applied by OPNsense is removed from OPNsense.

### What "direction" means

- `inbound`: connections **the address starts** (it is the Zeek originator, `src_ip`).
- `outbound`: connections **our devices start toward the address** (`dst_ip`).
- `both`: either.

The firewall rules match the connection's original direction (conntrack), and the
preview uses the same definition, so the preview counts exactly what the rule stops.

### Address safety

`ipaddress.ip_address()` alone is not enough:

```
$ python3 -I ipcheck.py      # (sandbox check, Python 3.11.15)
'1.2.3.4; rm -rf /'          -> ValueError
'2001:db8::1%$(id)'          -> 2001:db8::1%$(id)    scope_id='$(id)'   <- accepted by ipaddress!
ip_address(16909060)         -> IPv4Address('1.2.3.4')                  <- a number is accepted
'::ffff:203.0.113.7'         -> an IPv4 address written as IPv6
```

So `parse_ip()` also refuses non-text input, any `%scope`, IPv4-mapped IPv6, and
(as required) loopback, multicast, unspecified and link-local, plus 255.255.255.255.
Private addresses are allowed: blocking a compromised device on your own network is valid.

## Checking the generated firewall commands for real (AHM-07 step 3)

Image: `nicolaka/netshoot:v0.15`
(`sha256:47b907d662d139d1e2f22bfe14f4efca1e3f1feed283572f47c970c780c03b61`, amd64,
Apache-2.0), contains nftables 1.1.6 and iptables 1.8.11 (nf_tables). `--network none`
gives the container only its own loopback, so nothing can leave it.

Write the setup file and the commands from the code:

```bash
mkdir -p /tmp/nft-check
python - <<'EOF'
from pathlib import Path
from maxguard.response.generate import NFT_SETUP, rules_for
Path("/tmp/nft-check/maxguard-setup.nft").write_text(NFT_SETUP)
r = rules_for("203.0.113.7", "both")
Path("/tmp/nft-check/run.sh").write_text("\n".join(
    r["nftables"]["block"] + r["iptables"]["block"]
    + ["iptables -S | grep maxguard"] + r["nftables"]["undo"] + r["iptables"]["undo"]
    + ['echo "rules left: $(iptables -S | grep -c maxguard)"']).replace("sudo ", "") + "\n")
EOF
docker run --rm --network none --cap-add NET_ADMIN --cap-add NET_RAW \
  -v /tmp/nft-check:/w:ro nicolaka/netshoot:v0.15 sh -c '
  nft -c -f /w/maxguard-setup.nft; echo "check exit=$?"
  nft -f /w/maxguard-setup.nft && nft -f /w/maxguard-setup.nft
  echo "rules in input after loading twice: $(nft list chain inet maxguard input | grep -c drop)"
  bash -e /w/run.sh'
```

Output (the run used the same commands for 203.0.113.7 and 2001:db8::7):

```
check exit=0
rules in input after loading twice: 2
-A INPUT -m conntrack --ctorigsrc 203.0.113.7 -m comment --comment maxguard -j DROP
-A FORWARD -m conntrack --ctorigdst 203.0.113.7 -m comment --comment maxguard -j DROP
-A FORWARD -m conntrack --ctorigsrc 203.0.113.7 -m comment --comment maxguard -j DROP
-A OUTPUT -m conntrack --ctorigdst 203.0.113.7 -m comment --comment maxguard -j DROP
rules left: 0
```

The set after `nft add element`: `elements = { 203.0.113.7 }` (and `{ 2001:db8::7 }` for v6).
Loading the setup file twice keeps the addresses already in the sets and does not
double the rules (`flush chain` before `add rule`).

That the rules really block, in the right direction (loopback demo inside the
container, by hand: MaxGuard itself refuses loopback addresses):

```
== inbound block of 127.0.0.2 (connections 127.0.0.2 starts)
127.0.0.2 starts -> 127.0.0.1: BLOCKED
127.0.0.1 starts -> 127.0.0.2: ok
== outbound block of 127.0.0.2 (connections we start toward it)
127.0.0.2 starts -> 127.0.0.1: ok
127.0.0.1 starts -> 127.0.0.2: BLOCKED
== after undo
127.0.0.2 starts -> 127.0.0.1: ok
127.0.0.1 starts -> 127.0.0.2: ok
```

Not checked: the iptables-legacy backend (only iptables-nft ran), and a real router
forwarding traffic (the `forward` chain was loaded but no routed packets went through it)
- **not run - verify on hardware**.

## The API (AHM-08 step 3)

| Method and path | Body | Answer |
|---|---|---|
| `POST /api/response/proposals` | `{actor, ip, direction, reason?, finding_id?}` | the proposal (with `rules`) |
| `GET /api/response/proposals?limit=` | | newest first |
| `GET /api/response/proposals/{id}` | | one proposal, 404 |
| `POST /api/response/proposals/{id}/preview` | `{actor}` | proposal with `preview` (window_end = now) |
| `POST /api/response/proposals/{id}/approve` | `{actor, confirm_ip}` | 400 if confirm_ip is missing or different |
| `POST /api/response/proposals/{id}/apply` | `{actor}` | OPNsense if configured, else "I ran the commands" |
| `POST /api/response/proposals/{id}/revert` | `{actor}` | undo, the same way it was applied |
| `POST /api/response/proposals/{id}/reject` | `{actor, reason?}` | |

Errors: 400 bad input, 404 no such proposal, 409 step not allowed now, 502 firewall error.
Cross-site requests are refused (403) by the API's middleware like every other change.

A real session (uvicorn on 127.0.0.1:8765, the telnet lab logs uploaded as a .zip):

```bash
uvicorn maxguard.api.app:create_app --factory --port 8765 &
curl -s -F file=@telnet-logs.zip http://127.0.0.1:8765/api/analyses
B=http://127.0.0.1:8765/api/response/proposals
curl -s -X POST $B -H 'Content-Type: application/json' \
  -d '{"actor": "ahmad", "ip": "1.2.3.4; rm -rf /", "direction": "both"}'
curl -s -X POST $B -H 'Content-Type: application/json' \
  -d '{"actor": "ahmad", "ip": "172.18.0.3", "direction": "both", "reason": "telnet client"}'
curl -s -X POST $B/1/preview -H 'Content-Type: application/json' -d '{"actor": "ahmad"}'
curl -s -X POST $B/1/approve -H 'Content-Type: application/json' -d '{"actor": "fiona"}'
curl -s -X POST $B/1/approve -H 'Content-Type: application/json' \
  -d '{"actor": "fiona", "confirm_ip": "172.18.0.3"}'
curl -s -X POST $B/1/apply -H 'Content-Type: application/json' -d '{"actor": "fiona"}'
curl -s -X POST $B/1/revert -H 'Content-Type: application/json' -d '{"actor": "ahmad"}'
curl -s http://127.0.0.1:8765/api/audit
```

Output (trimmed to the interesting fields):

```
{"analysis_id":"1c17da4707ad3bba","findings":1}
{"detail":"'1.2.3.4; rm -rf /' does not appear to be an IPv4 or IPv6 address"}   HTTP 400
{"detail":"127.0.0.1 is a loopback address (this machine)"}                      HTTP 400
proposal 1: ip 172.18.0.3, direction both, state proposed
  sudo nft 'add element inet maxguard maxguard_block_in_v4 { 172.18.0.3 }'
  sudo nft 'add element inet maxguard maxguard_block_out_v4 { 172.18.0.3 }'
  sudo nft 'delete element inet maxguard maxguard_block_in_v4 { 172.18.0.3 }'
  sudo nft 'delete element inet maxguard maxguard_block_out_v4 { 172.18.0.3 }'
previewed {'connections': 1, 'devices': ['172.18.0.2'], 'events': 1,
           'first_seen': 1791250284.287418, 'last_seen': 1791250284.287418,
           'services': [{'events': 1, 'port': 23, 'proto': 'tcp', 'service': ''}], ...}
{"detail":"the IP address you typed does not match the proposal"}               HTTP 400
approved fiona
applied manual
reverted
audit (oldest first):
ahmad response.proposed 1 {"direction": "both", "finding_id": null, "ip": "172.18.0.3"}
ahmad response.previewed 1 {"connections": 1, "devices": 1, "window_end": 1791321105.5348117}
fiona response.approve_refused 1 {"reason": "typed IP does not match"}
fiona response.approved 1 {"ip": "172.18.0.3"}
fiona response.applied 1 {"ip": "172.18.0.3", "method": "manual"}
ahmad response.reverted 1 {"ip": "172.18.0.3", "method": "manual"}
```

## OPNsense enforcer (AHM-08 step 4)

Endpoints, read from the OPNsense source, `opnsense/core` commit
`1177021c22d6dedb63ff9bffd6300e789a8822e2` (2026-10-06). docs.opnsense.org was not
reachable from the sandbox; the files were read from raw.githubusercontent.com.

| Call | Source | Answer |
|---|---|---|
| `POST /api/firewall/alias_util/add/<alias>` `{"address": ip}` | `src/opnsense/mvc/app/controllers/OPNsense/Firewall/Api/AliasUtilController.php` `addAction` | `{"status": "done"}`; `not_an_address` for characters outside `[0-9a-f:./_]`; `failed` for an unknown alias |
| `POST /api/firewall/alias_util/delete/<alias>` `{"address": ip}` | same file, `deleteAction` | `{"status": "done"}` |
| `POST /api/firewall/alias/reconfigure` | `.../Firewall/Api/AliasController.php` `reconfigureAction` | `{"status": "ok"}` |

- add/delete change the alias in the configuration and the live pf table at once
  (`src/opnsense/service/conf/actions.d/actions_filter.conf`, `[add.table]` runs
  `/sbin/pfctl -t %s -T add %s`). `reconfigure` is the "Apply" step; MaxGuard calls it
  after every change, as the spec asks.
- A JSON body is read like a form (`ApiControllerBase.php`, `parseJsonBodyData`).
- API key file and basic auth: opnsense/docs `source/development/how-tos/api.rst`
  ("key=..." and "secret=..." lines; Python `requests` with `auth=(key, secret)`).
- Least-privilege API user (`src/opnsense/mvc/app/models/OPNsense/Core/ACL/ACL.xml`):
  **Diagnostics: PF Table IP addresses** (`api/firewall/alias_util/*`) and
  **Firewall: Alias: Edit** (`api/firewall/alias/*`).

### Setting it up (**not run - verify on hardware**: an OPNsense VM, never a real firewall)

1. **Firewall > Aliases**: create `maxguard_block_in` and `maxguard_block_out`, type Hosts, empty.
2. **Firewall > Rules > WAN**: Block, source `maxguard_block_in`.
   **Firewall > Rules > LAN**: Block, destination `maxguard_block_out`. Apply.
3. **System > Access > Users**: a user `maxguard` with only the two privileges above.
   In its API keys section click **+**; the browser downloads the key file once.
4. On the MaxGuard machine:

   ```bash
   mkdir -p data/opnsense
   mv ~/Downloads/<the downloaded key file>.txt data/opnsense/apikey.txt
   chmod 600 data/opnsense/apikey.txt          # only you can read it
   export MAXGUARD_OPNSENSE_URL=https://fw.home.arpa      # your firewall
   export MAXGUARD_OPNSENSE_CA=$PWD/data/opnsense/ca.pem   # if it uses its own CA
   export MAXGUARD_OFFLINE_ALLOW=fw.home.arpa              # with MAXGUARD_OFFLINE=1
   ```

   `data/` is in `.gitignore`, so the key never reaches the repository.
5. Without `MAXGUARD_OFFLINE_ALLOW`, apply fails with 502 and the message
   `OFFLINE MODE: blocked address lookup of 'fw.home.arpa' ... (add the firewall to MAXGUARD_OFFLINE_ALLOW)`.

Safety choices in the client: https only (http:// is refused), TLS verification always
on (`verify=<CA file>` or the system CAs, never False), timeouts 5 s connect / 20 s read,
no redirects, and `trust_env = False` so proxy settings and `~/.netrc` are ignored (the
request goes straight to the firewall on the user's own network). The address is parsed
again in `add()`/`remove()`, so only a clean address is ever sent, and it is only ever
sent *to the firewall*, never toward the blocked address.

## Tests

```bash
pytest tests/unit/test_response_generate.py tests/unit/test_response_preview.py \
       tests/unit/test_response_approvals.py tests/unit/test_response_routes.py \
       tests/unit/test_opnsense.py -q
```

```
........................................................................ [ 80%]
..................                                                       [100%]
90 passed
```

(Python 3.11 in .venv, and Python 3.13.5 in the `maxguard-sandbox:test` image, both pass.)
The whole unit suite: `718 passed, 1 skipped`.

- The fake OPNsense (`FakeOPNsense` in `tests/unit/test_opnsense.py`) is an
  `http.server` on 127.0.0.1 wrapped in TLS, with a certificate from a throwaway
  test CA made with `cryptography`; so the tests also prove that a firewall
  certificate the client does not trust is refused.
- The offline-guard tests make `fw.home.arpa` resolve to 127.0.0.1, then enable the
  guard: with `fw.home.arpa` allowed the block works; without it, nothing is sent.
