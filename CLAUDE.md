# MaxGuard — Instructions for Claude Code

MaxGuard v2.0 is an offline SOC-analyst dashboard and network sensor for small
networks (homes and small businesses) that can also run on a company network
rack. It turns network traffic into explained, compliance-mapped security alerts
and lets a human analyst investigate and respond. It is built by an eight-person
CCSU student team led by Ahmad (Security Lead).

Read these before doing any work:
- `docs/PROJECT_DECISIONS.md` — every locked decision (scope, features, owners,
  hardware, framework versions).
- `docs/ARCHITECTURE.md` — components, data flow, the common event schema, and
  the three contracts as extended for v2.0.
- `docs/roadmap/README.md` — the current build order, phases, and Friday checkpoints.
- `docs/archive/ROADMAP_fall2026_original.md` — the original Fall 2026 roadmap. Its
  contracts and conventions still apply unless PROJECT_DECISIONS.md or
  ARCHITECTURE.md says otherwise.

## Non-negotiable rules

1. **Offline at runtime.** No external APIs, telemetry, or cloud calls. The AI runs
   locally through Ollama. Anything that needs a network connection (such as
   updates) must be explicit, optional, and documented.
2. **Deterministic detection.** The rule engine alone decides what is an alert.
   The same input must always produce the same output. The AI never creates,
   hides, or changes the severity of an alert.
3. **Evidence-citing AI.** Every sentence the AI writes must reference the IDs of
   the log records that support it. If it cannot cite evidence, it writes nothing.
   Enforce this in code (validate citations), not only in the prompt.
4. **Defensive only.** Blocking applies only to networks the user owns or
   administers. It always requires explicit human approval, is reversible, and is
   logged. No hack-back, no scanning of third-party hosts, no exploit code.
5. **Passive sensors.** Sensors listen. They never inject packets. Decoys are not
   sensors: a decoy runs as its own container or host with its own IP address and
   only answers connections made to it. A decoy never runs on a capture interface.
6. **Public repository.** Never commit secrets, API keys, personal data, email
   addresses, real captures from anyone's network, or details of team members'
   home networks. Tests use synthetic or publicly licensed sample captures only.
7. **Licensing.** From the JA4+ family, use only JA4 (BSD-3-Clause). The other JA4+
   methods are under the FoxIO License 1.1 and are excluded. Take JA4 from
   Suricata's built-in support, not from FoxIO's Zeek package (which also ships
   the excluded methods). Record the license of every new dependency in
   `docs/DEPENDENCIES.md`.
8. **Compliance accuracy.** Every compliance mapping cites the exact control ID and
   framework version. Use the framework versions locked in
   `docs/PROJECT_DECISIONS.md` section 8, and verify each is still the current
   published version before a release.

## Architecture in one paragraph

Input adapters (pcap upload, live sensor, NetFlow/IPFIX, host agent) feed Zeek and
Suricata. Their output is normalized into one common event schema. A
deterministic rule engine produces findings. Findings are mapped to MITRE ATT&CK
and to four compliance frameworks, explained by a local LLM with evidence
citations, and shown in a dashboard with Analyst and Home modes. A response
module proposes human-approved blocks. Everything ships with Docker Compose and
runs on the user's own machine. Sensor software must run on ARM64 (Raspberry Pi 5)
and x86-64 (mini PC or server).

Keep the three contracts from the original roadmap (the Finding dataclass, the
mapping file schema, and the input adapter protocol). Extend them only in the
backward-compatible ways described in `docs/ARCHITECTURE.md`; do not replace or
break them. A contract change needs a pull request reviewed by Jaiden and
approved by the Security Lead.

## Module owners (GitHub usernames)

| Module | Owner |
|---|---|
| Product direction, detection accuracy, dashboard UI, response module | Ahmad (@ahmadalkhoudeir) |
| Architecture, event schema, API backend, storage, packaging, releases, signing | Jaiden (@JWinborne1) |
| Detection engine, ATT&CK mapping, decoys, device baselines | Fiona (@flau0306) |
| Sensor and live capture, protocol coverage, JA4, device attribution | Jakub (@SXafir-byte) |
| Offline AI and evidence-citing explanations | Jonattan (@MeliorExi) |
| AI model evaluation (accuracy and unsupported-claim testing) | Ali (@al-kheder) |
| Compliance mapping, reports and report export, chain of custody | Amory (@gettalife) |
| Test corpus, CI, end-to-end tests | Karthik (@Karthiknair91) |

## How to work in this repo

- Python 3.11. Tests use pytest. Test captures live in `tests/pcaps/`, their
  expected results in `tests/expected/`, and small hand-written log fixtures in
  `tests/fixtures/`.
- One branch per task, named `<yourname>/<short-task>` (for example
  `fiona/zeek-runner`). Open a pull request into `main`. At least one review and
  passing CI are required to merge. See `docs/CONTRIBUTING.md`.
- Before a large change, a new dependency, or a change to a contract, explain the
  plan and wait for approval.
- Technical questions and design discussions go in GitHub Discussions so the team
  can see, search, and answer them. Microsoft Teams is for meetings and quick chat.
- Write documentation for a junior student: exact commands, expected output, and
  a short explanation of why each step matters.
- Run every command and code snippet you put in documentation whenever possible.
  Clearly mark anything you could not run (for example, hardware steps) as
  "not run — verify on hardware".
