# RDP fixture (hand-made capture, real Zeek output)

No lab capture contains RDP, so `make_rdp_pcap.py` writes a tiny synthetic
capture byte by byte, and Zeek 9.0.0 turns it into the logs in this folder.
The logs are real Zeek output, not typed by hand, so their field names and
values are exactly what Zeek 9 writes.

| File | What |
|---|---|
| `make_rdp_pcap.py` | builds `rdp.pcap` (standard library only) |
| `rdp.pcap` | 2 TCP connections to port 3389, each: handshake, X.224 Connection Request, X.224 Connection Confirm, close |
| `rdp.log` | 2 records: `security_protocol` `"RDP"` (server 192.168.56.30) and `"HYBRID"` (server 192.168.56.31) |
| `conn.log` | the 2 connections (so the folder is also a valid Zeek log folder for `maxguard analyze`) |

`security_protocol` is the protocol the server picked in its RDP Negotiation
Response (`selectedProtocol`, MS-RDPBCGR 2.2.1.2.1:
https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-rdpbcgr/b2975bdc-6d56-49ee-9c57-f2ff3a0b6817).
Zeek 9.0.0 names the values in `base/protocols/rdp/consts.zeek`:
0 = `"RDP"` (Standard RDP Security), 1 = `"SSL"`, 2 = `"HYBRID"` (CredSSP),
8 = `"HYBRID_EX"`. The rdp.log fields are defined in
`base/protocols/rdp/main.zeek` (`RDP::Info`), read from the `zeek/zeek:9.0.0`
image and also at https://github.com/zeek/zeek/blob/v9.0.0/scripts/base/protocols/rdp/main.zeek.

Rule `rdp.standard_security` must fire for the `"RDP"` record only.

All data is synthetic: addresses in 192.168.56.0/24, MACs starting with 02
(locally administered), cookie user name `labuser`.

## Rebuild (from the repository root)

```bash
H=tests/fixtures/zeek/_handmade/rdp
python $H/make_rdp_pcap.py $H/rdp.pcap

# same options as maxguard/zeek/runner.py
docker run --rm --network none -v "$PWD":/src -w /src/$H zeek/zeek:9.0.0 \
  zeek -D -C -r rdp.pcap /src/maxguard/zeek/site.zeek LogAscii::use_json=T \
  policy/protocols/conn/community-id-logging \
  /src/maxguard/zeek/scripts/cleartext.zeek /src/maxguard/zeek/scripts/inventory.zeek
# keep conn.log and rdp.log; delete the other *.log files
```

Running the two steps twice gives byte-identical `rdp.pcap`, `rdp.log` and
`conn.log` (fixed sequence numbers and timestamps, and Zeek's `-D`).
