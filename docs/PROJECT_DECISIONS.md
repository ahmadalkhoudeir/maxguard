# MaxGuard v2.0 — Project Decisions

Locked by Ahmad (Security Lead) on October 5, 2026. Revised October 6, 2026
(see "Change log" at the end).
Changes to this file need the Security Lead's approval.

## 1. What we are building

MaxGuard v2.0 is a downloadable, fully offline SOC-analyst dashboard with a
network sensor. It shows which IP addresses are doing suspicious things, what
they are attempting, how that maps to MITRE ATT&CK and to four compliance
frameworks, and lets a human analyst approve a block. It serves two audiences
with the same data:

- **Analyst mode** for IT staff and SOC analysts: full detail, timelines, ATT&CK.
- **Home mode** for non-experts: plain-language explanations and one clear action.

Primary target: small networks (homes and small businesses). It must also run on
a company network rack using the same software on bigger hardware.

v0.8.0 (the Spring 2026 Streamlit + Scapy + OpenAI scanner) is preserved as the
`v0.8.0` release. v2.0 is a rebuild.

## 2. Timeline and team rhythm

- The timeline is flexible. The original target was December 4, 2026; quality
  comes before speed. The roadmap should still reach a working end-to-end demo as
  early as possible, then add features in a clear build order.
- Release plan (details in `docs/roadmap/README.md`):
  - **Fri Oct 23, 2026:** first end-to-end demo (a test capture becomes a mapped,
    explained finding).
  - **Fri Dec 4, 2026: `v2.0-alpha`.** The original Fall 2026 scope (pcap or Zeek
    log upload, the 13 rules, four frameworks, evidence-citing local AI, offline
    bundle) plus the API, the alert queue, and event storage.
  - **Spring 2027: `v2.0`.** Every remaining feature in section 3, in the build
    order of section 4.
- Team members work on their own time.
- Weekly review meeting on Fridays (possibly Mondays too). Milestones are due
  before the Friday review so the meeting is for review, not catch-up.
- Code and tasks: GitHub (Issues, Projects board, Discussions for Q&A).
  Meetings and quick chat: Microsoft Teams.
- MaxGuard is part of The Project Collective (TPC) at CCSU.

## 3. Features — all ship in v2.0

| Feature | What it does | Owner (support) |
|---|---|---|
| Alert queue | Live list of alerts with severity, status, and assignment | Ahmad |
| Device inventory | Every device seen, its likely type, and its normal contacts | Ahmad (Jakub for data) |
| IP investigation timeline | Everything one IP did, in order, mapped to ATT&CK | Ahmad (Fiona for mapping) |
| Human-approved blocking | Push a block to the user's own router or firewall, or generate the rule for manual use | Ahmad |
| Preview before you block | Replay the last 7 days of stored traffic and show what a proposed rule would have broken | Ahmad (Jaiden/Jakub for retention) |
| Evidence-citing AI | Local LLM explains findings; every sentence cites log record IDs | Jonattan (Ali evaluates) |
| Analyst and Home modes | Two views of the same data | Ahmad (Jonattan for plain-language text) |
| Compliance reports | Findings mapped to PCI DSS, NIST SP 800-53, CISA CPGs, CJIS; JSON, CSV, and HTML export | Amory |
| Tamper-evident chain of custody | Hash every capture and report; signed custody log | Amory (Jaiden for signing) |
| Signed offline intel bundles | Rule and intel updates delivered on USB, signature verified before loading | Jaiden |
| Decoys (canaries) | One-click fake services on their own IP address; any contact is a high-confidence alert. Decoys only answer connections made to them and never run on the sensor's capture interface. | Fiona |
| Per-device behavior baselines | Learn each device's normal behavior and alert on drift | Fiona (Jakub for data) |
| JA4 TLS fingerprinting | Identify suspicious TLS clients without decryption (JA4 only, taken from Suricata — see licensing) | Jakub |
| Device attribution | Tie traffic to devices when NAT hides them: DNS correlation and passive LAN discovery | Jakub |

## 4. Inputs and sensors

Tiered sensors, one common event format:

1. **Pcap upload** — no hardware; works on air-gapped networks.
2. **Live sensor** — Raspberry Pi 5 listening on a switch mirror (SPAN) port.
3. **NetFlow/IPFIX** — from routers such as OPNsense; metadata only.
4. **Host agent** — sees one machine's traffic; easiest for home users.

Build order: pcap upload first, then the live sensor, then NetFlow, then the
host agent.

### Why a mirror port instead of a hardware TAP

A passive copper TAP cannot monitor gigabit Ethernet: 1000BASE-T sends and
receives on all four wire pairs at once, and separating the two directions needs
powered electronics. Lossless gigabit TAPs cost roughly $200 or more
(approximate, October 2026). A smart switch with port mirroring costs roughly $30
and drops packets when combined traffic in both directions exceeds 1 Gbps. On a
500 Mbps symmetrical connection, the maximum combined traffic is exactly 1 Gbps,
so it fits on average but leaves no headroom: short bursts above line rate can
still drop packets. Upgrade path: Dualcomm ETAP-2003 (verify on its data sheet
whether it aggregates both directions onto one monitor port; if it does, it has
the same 1 Gbps ceiling as the mirror port). The software does not change.

### Reference lab hardware

| Part | Purpose |
|---|---|
| Raspberry Pi 5, 8GB, with 27W power supply, Active Cooler, 64GB A2 microSD, case | Sensor (Zeek + Suricata) |
| USB 3 SSD (recommended, 128 GB or more) | Log and event storage, so 7-day retention does not wear out the microSD card |
| USB 3 gigabit Ethernet adapter (RTL8153 chipset) | Second port for management |
| TP-Link TL-SG105E smart switch | Port mirroring |
| TP-Link Archer AX4400 router with its Wi-Fi turned off (already owned) | NAT and DHCP inside the mirrored link |
| Consumer mesh Wi-Fi in bridge (access point) mode | Wi-Fi for the lab |

### Reference lab topology

```
Fiber ONT ──► wired router (NAT + DHCP)
                  │
                  ▼
              switch port 1  ◄── mirror source (ingress and egress)
              switch port 2 ──► mesh Wi-Fi (bridge / access point mode)
              switch port 3 ──► sensor management port (USB adapter)
              switch port 5 ──► sensor capture port (mirror destination)
```

Because the router sits before the mirrored link, the sensor sees each device's
real internal address for all internet-bound traffic, plus DHCP announcements
(hostnames, MAC addresses). Port 1 must be mirrored in both directions (ingress
and egress) or the sensor sees only half of each conversation.

### Known limits (document these for users)

- Copper Ethernet up to 1 Gbps only; faster links drop to 1 Gbps through this switch.
- Mirror ports can drop packets if combined traffic exceeds 1 Gbps, including
  short bursts.
- Traffic between two Wi-Fi devices on the same mesh system usually never crosses
  the cable (mesh nodes normally talk to each other over Wi-Fi), so the sensor
  cannot see it.
- Traffic between two devices that are both plugged into the switch (for example
  port 2 to port 4) does not cross port 1, so the sensor cannot see it. Plug
  nothing into the router's other LAN ports; that traffic is invisible too.
- If the sensor sits outside the router (before NAT), every device appears as the
  one public IP; device attribution then relies on DNS correlation and passive
  LAN discovery, which miss encrypted DNS and direct-to-IP connections.
- A Raspberry Pi is a small-network sensor. Its sustained throughput with Zeek
  and Suricata together is not yet measured; expect it to be below 1 Gbps until
  the benchmark in `docs/HARDWARE.md` says otherwise. For company racks, use the
  company's existing mirror ports or a proper TAP, and run the sensor on a mini
  PC or server.
- The TP-Link Archer AX4400 is not known to offer a local firewall API
  (not verified — check on the hardware). Automatic blocking is therefore
  demonstrated against an OPNsense firewall (a virtual machine is fine); on the
  lab router, MaxGuard generates the rule and the user applies it by hand.

## 5. Team and roles

| Person | GitHub | Role |
|---|---|---|
| Ahmad | @ahmadalkhoudeir | Security Lead; dashboard UI; response module; final sign-off on detection logic and compliance accuracy |
| Jaiden | @JWinborne1 | Co-lead; Architecture and Release Lead; API backend and storage |
| Fiona | @flau0306 | Detection Engine Lead |
| Jakub | @SXafir-byte | Protocol Coverage Engineer; sensor and live capture |
| Jonattan | @MeliorExi | Offline AI Engineer |
| Ali | @al-kheder | AI Model Evaluation Engineer (remote) |
| Amory | @gettalife | Compliance Mapping Analyst; reports and report export |
| Karthik | @Karthiknair91 | Test and CI Engineer |

Where the original Fall 2026 roadmap assigns work differently (for example, it
gave the dashboard and report export to Jakub and described Ahmad as owning no
critical-path code), this file wins.

## 6. Decided (October 6, 2026)

These were open decisions. The Security Lead approved the recommendations below
on October 6, 2026. The options and trade-offs are recorded in
`docs/ARCHITECTURE.md`.

- **Dashboard technology:** FastAPI backend (Jaiden) with server-rendered pages
  using Jinja2 templates, HTMX, and server-sent events for live updates (Ahmad).
  All JavaScript is vendored into the repository; nothing loads from a CDN.
  Streamlit is retired.
- **Event storage:** SQLite (WAL mode) for mutable state (alerts, assignments,
  approvals, audit and custody logs); hourly Parquet files queried with DuckDB for
  events and flows. Retention deletes whole hourly partitions. Default retention
  is 7 days.
- **How blocks are applied:** first, generated rules the user applies by hand
  (nftables, iptables, OPNsense/pfSense alias, plain-English router steps); then
  pluggable `Enforcer` connectors, starting with the OPNsense API. Every block
  needs explicit human approval, is reversible, and is logged.
- **Local models:** two hardware tiers, one model each, chosen by Ali's
  evaluation: a Pi-class tier (4 billion parameters or fewer) and a laptop tier
  (8 billion or fewer). Only models whose license allows redistribution in the
  offline bundle are eligible. Ollama runs on the console machine, not on the
  Pi sensor.
- **Project license:** Apache License 2.0 (proposed in the v2-planning pull
  request; confirm before merging).

## 7. Principles

- Offline, deterministic, evidence-backed, defensive only. See `CLAUDE.md`.
- The repository is public: no secrets, personal data, or home-network details.

## 8. Framework versions (locked)

Every mapping file states one of these exact versions. Re-check each against the
publisher before every release (CLAUDE.md rule 8).

| Framework | Locked version | Publisher | Verified current on |
|---|---|---|---|
| PCI DSS | v4.0.1 (published June 2024; v4.0 retired December 31, 2024) | PCI Security Standards Council | October 6, 2026 |
| NIST SP 800-53 | Rev. 5, Release 5.2.0 (August 27, 2025) | NIST | October 6, 2026 |
| CISA Cross-Sector Cybersecurity Performance Goals | CPG 2.0 (December 11, 2025) | CISA | October 6, 2026 |
| CJIS Security Policy | v6.1 (June 25, 2026) | FBI CJIS Division | October 6, 2026 |
| MITRE ATT&CK | Enterprise v19.x; record the exact point release when `mappings/attack.yaml` is created | MITRE | October 6, 2026 (major version only) |

## Change log

- **October 6, 2026.** Approved by the Security Lead in the v2-planning review:
  copper-TAP wording, no-headroom note, ETAP-2003 verification note, mesh and
  same-switch blind spots, ingress-and-egress mirroring, decoy placement, JA4
  source, USB SSD recommendation, Pi throughput and Archer AX4400 notes, release
  plan, API/storage ownership (Jaiden), report export ownership (Amory), section 6
  decisions, and the section 8 version table.
