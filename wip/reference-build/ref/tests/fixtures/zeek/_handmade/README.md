# Hand-made fixtures

The 13 lab captures have no DNS or DHCP traffic and no Suricata alert, and all
their logs are JSON. These small fixtures fill those gaps. The folder name
starts with `_` so tests that loop over "one folder per lab capture" skip it.

All data is synthetic: addresses in 192.168.56.0/24, MAC 02:00:00:aa:bb:cc
(locally administered, made up), names under `.invalid`.

| Folder | What | Made with |
|---|---|---|
| `dns_dhcp/` | `dns_dhcp.pcap` (1 DHCP lease + 1 DNS lookup) and its `conn.log`, `dns.log`, `dhcp.log` (Zeek JSON) and `eve.json` (has `alert`, `dns`, `dhcp`, `flow`) | `make_dns_dhcp_pcap.py`, Zeek 9.0.0, Suricata 7.0.10 |
| `dns_dhcp_suricata8/` | `eve.json` of the same capture from Suricata 8.0.7 (eve DNS format version 3) | Suricata 8.0.7 |
| `tsv_plain_http/` | `conn.log`, `http.log` of `tests/pcaps/plain_http.pcap` in Zeek's default TSV format | Zeek 9.0.0 |
| `tsv_dns_dhcp/` | `conn.log`, `dns.log`, `dhcp.log` of `dns_dhcp.pcap` in TSV format | Zeek 9.0.0 |

`fixture-only.rules` holds one Suricata rule (sid 9000001) used only to get a
real `alert` record into `eve.json`. It is not part of MaxGuard's rules.

Field names come from the real tools, and match the Zeek 9.0.0 scripts
`base/protocols/dns/main.zeek` and `base/protocols/dhcp/main.zeek`
(https://github.com/zeek/zeek/tree/v9.0.0/scripts/base/protocols). Note that
`dhcp.log` has no `uid`/`id.*` fields: it has a `uids` set, and the ports are
not logged.

## Rebuild (from the repository root)

```bash
H=tests/fixtures/zeek/_handmade
python $H/make_dns_dhcp_pcap.py $H/dns_dhcp/dns_dhcp.pcap

# Zeek JSON logs (same options as maxguard/zeek/runner.py)
docker run --rm --network none -v "$PWD":/src -w /src/$H/dns_dhcp zeek/zeek:9.0.0 \
  zeek -D -C -r dns_dhcp.pcap local LogAscii::use_json=T \
  policy/protocols/conn/community-id-logging \
  /src/maxguard/zeek/scripts/cleartext.zeek /src/maxguard/zeek/scripts/inventory.zeek
# keep conn.log, dns.log, dhcp.log; delete the other *.log files

# Suricata eve.json (same options as maxguard/suricata/runner.py, plus the fixture rule)
docker run --rm --network none -v "$PWD":/src jasonish/suricata:7.0.10 \
  suricata -c /src/maxguard/suricata/maxguard-suricata.yaml \
  -r /src/$H/dns_dhcp/dns_dhcp.pcap -l /src/$H/dns_dhcp -k none --runmode single \
  -S /src/$H/fixture-only.rules
# delete fast.log, stats.log, suricata.log (only eve.json is kept)
```

For the TSV folders run the same Zeek command without `LogAscii::use_json=T`
(on `tests/pcaps/plain_http.pcap` for `tsv_plain_http/`).
