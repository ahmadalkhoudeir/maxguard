# Where the test captures come from

Every capture in this folder is **synthetic**. It was recorded in MaxGuard's
own traffic lab (`lab/`): a client container talks to a server container on an
isolated Docker network (`internal: true`, no route to the internet or to any
LAN), and a third container records the server's network card with tcpdump.
No capture comes from a real network or from a third party (CLAUDE.md rule 6).

Recorded on October 6, 2026 with the lab as committed: server and client
`python:3.11-slim-bookworm` (pyftpdlib 2.2.0, cryptography 50.0.2, the image's
OpenSSL), sniffer `nicolaka/netshoot:v0.15`. Docker gave the lab network
172.18.0.0/16: server 172.18.0.2, client 172.18.0.3 (your own recordings may
get other addresses). All certificates are fake and made by
`lab/server/make_certs.py`; host names end in `.invalid`.

| Capture | Scenario (`lab/client/scenarios/`) | Shows | Rule it must trigger | SHA-256 (first 16) |
|---|---|---|---|---|
| `telnet.pcap` | `telnet.py` | Telnet login and commands | `cleartext.telnet` | `deb2874b1e5c2b87` |
| `ftp.pcap` | `ftp.py` | FTP login and a directory listing | `cleartext.ftp` | `01434b223a3cabc2` |
| `plain_http.pcap` | `plain_http.py` | HTTP on port 80 | `cleartext.http` | `b7d34b2ce10bbb9e` |
| `plain_http_alt.pcap` | `plain_http_alt.py` | HTTP on port 8080 | `cleartext.http_alt` | `4189f2906f14a26c` |
| `pop3.pcap` | `pop3.py` | POP3 without TLS | `cleartext.pop3` | `4edc60ce003e5b88` |
| `imap.pcap` | `imap.py` | IMAP without TLS | `cleartext.imap` | `d222b4fe1b780a7d` |
| `tls_weak_version.pcap` | `tls_weak_version.py` | TLS 1.0 | `tls.weak_version` | `782cb7525451bbbf` |
| `tls_weak_cipher.pcap` | `tls_weak_cipher.py` | TLS 1.2 with the NULL cipher (no encryption) | `tls.weak_cipher` | `b22a69477de2f5a0` |
| `cert_expired.pcap` | `cert_expired.py` | Certificate that expired in 2020 | `cert.expired` | `b513d0a4d34eb5f6` |
| `cert_self_signed.pcap` | `cert_self_signed.py` | Self-signed certificate | `cert.self_signed` | `47428ab30eea0c7a` |
| `cert_weak_key.pcap` | `cert_weak_key.py` | 1024-bit RSA key | `cert.weak_key` | `705b8183f48bc3b9` |
| `cert_sha1.pcap` | `cert_sha1.py` | Certificate signed with SHA-1 | `cert.sha1_signature` | `d04014c8ec011562` |
| `clean_tls13.pcap` | `clean_tls13.py` | Good TLS 1.3 session | none | `0319e88caf5ecb5c` |
| `dns_lookup.pcap` | `dns_lookup.py` | Three DNS questions and answers | none | `ae6da75fc2cc5f6f` |

The RDP rule (`rdp.standard_security`) and DHCP have no lab capture yet; their
tests use the hand-made fixtures in `tests/fixtures/zeek/_handmade/`.

**Adding a capture:** add a scenario to the lab, record it, add a row here,
regenerate the fixtures (`bash scripts/make_fixtures.sh`), and add its expected
result. No source line, no merge.
