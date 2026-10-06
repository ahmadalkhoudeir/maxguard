# MaxGuard v2.0 — Project Decisions

Locked by Ahmad (Security Lead) on October 5, 2026.
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
| Compliance reports | Findings mapped to PCI DSS, NIST SP 800-53, CISA CPGs, CJIS | Amory |
| Tamper-evident chain of custody | Hash every capture and report; signed custody log | Amory (Jaiden for signing) |
| Signed offline intel bundles | Rule and intel updates delivered on USB, signature verified before loading | Jaiden |
| Decoys (canaries) | One-click fake services; any contact is a high-confidence alert | Fiona |
| Per-device behavior baselines | Learn each device's normal behavior and alert on drift | Fiona (Jakub for data) |
| JA4 TLS fingerprinting | Identify suspicious TLS clients without decryption (JA4 only — see licensing) | Jakub |
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

A passive TAP cannot monitor gigabit Ethernet. Lossless gigabit TAPs start
around $200. A smart switch with port mirroring costs about $30 and only drops
packets when combined traffic in both directions exceeds 1 Gbps. On a
500 Mbps symmetrical connection, the maximum combined traffic is 1 Gbps, which
fits. Upgrade path for guaranteed lossless capture: Dualcomm ETAP-2003. The
software does not change.

### Reference lab hardware

| Part | Purpose |
|---|---|
| Raspberry Pi 5, 8GB, with 27W power supply, Active Cooler, 64GB A2 microSD, case | Sensor (Zeek + Suricata) |
| USB 3 gigabit Ethernet adapter (RTL8153 chipset) | Second port for management |
| TP-Link TL-SG105E smart switch | Port mirroring |
| TP-Link Archer AX4400 router with its Wi-Fi turned off (already owned) | NAT and DHCP inside the mirrored link |
| Consumer mesh Wi-Fi in bridge (access point) mode | Wi-Fi for the lab |

### Reference lab topology

```
Fiber ONT ──► wired router (NAT + DHCP)
                  │
                  ▼
              switch port 1  ◄── mirror source
              switch port 2 ──► mesh Wi-Fi (bridge / access point mode)
              switch port 3 ──► sensor management port (USB adapter)
              switch port 5 ──► sensor capture port (mirror destination)
```

Because the router sits before the mirrored link, the sensor sees each device's
real internal address for all internet-bound traffic, plus DHCP announcements
(hostnames, MAC addresses).

### Known limits (document these for users)

- Copper Ethernet up to 1 Gbps only; faster links drop to 1 Gbps through this switch.
- Mirror ports can drop packets if combined traffic exceeds 1 Gbps.
- Traffic between two Wi-Fi devices on the same access point never crosses the
  cable, so the sensor cannot see it.
- If the sensor sits outside the router (before NAT), every device appears as the
  one public IP; device attribution then relies on DNS correlation and passive
  LAN discovery, which miss encrypted DNS and direct-to-IP connections.
- A Raspberry Pi is a small-network sensor. For company racks, use the company's
  existing mirror ports or a proper TAP, and run the sensor on a mini PC or server.

## 5. Team and roles

| Person | GitHub | Role |
|---|---|---|
| Ahmad | @ahmadalkhoudeir | Security Lead; dashboard UI; response module; final sign-off on detection logic and compliance accuracy |
| Jaiden | @JWinborne1 | Co-lead; Architecture and Release Lead |
| Fiona | @flau0306 | Detection Engine Lead |
| Jakub | @SXafir-byte | Protocol Coverage Engineer; sensor and live capture |
| Jonattan | @MeliorExi | Offline AI Engineer |
| Ali | @al-kheder | AI Model Evaluation Engineer (remote) |
| Amory | @gettalife | Compliance Mapping Analyst |
| Karthik | @Karthiknair91 | Test and CI Engineer |

## 6. Open decisions (propose options with trade-offs; the Security Lead decides)

- Dashboard technology: keep Streamlit or move to an API backend with a web
  frontend. A SOC view needs live updates, multiple linked views, and actions.
- Event storage: for example SQLite or DuckDB, sized for 7+ days of flow
  retention on a Pi.
- How the response module applies blocks: router or firewall API where one
  exists, otherwise generated rules the user applies by hand.
- Which local model(s) to support in Ollama, given Pi-class and laptop-class hardware.

## 7. Principles

- Offline, deterministic, evidence-backed, defensive only. See `CLAUDE.md`.
- The repository is public: no secrets, personal data, or home-network details.
