# Issues, labels, milestones, and the project board

Every task in `docs/roadmap/` becomes one GitHub issue, so the team can assign,
track, and close work on the project board. `scripts/create_issues.sh` creates
them (its data rows were generated from the roadmap; keep them in step when a
task changes), together with the labels, the milestones, and the project
**MaxGuard v2.0 Roadmap**. Ahmad runs it once in Week 0 (task AHM-01 in
`docs/roadmap/ahmad.md`).

## Running the script

You need the GitHub CLI (`gh`) logged in with an account that can write to the
repository, plus the `project` permission for the board:

```bash
gh auth login
gh auth refresh -s project
DRY_RUN=1 bash scripts/create_issues.sh    # prints every change, makes none
bash scripts/create_issues.sh              # creates what is missing
```

What it does, in order:

1. Creates or updates every label below (`gh label create --force`).
2. Creates each milestone that does not exist yet, with its due date (GitHub's
   REST API through `gh api`; `gh` has no milestone command).
3. Finds or creates the project **MaxGuard v2.0 Roadmap** and links it to the repository.
4. Creates each issue whose exact title does not exist yet (open or closed), with
   its labels and milestone, and adds it to the project.

It is safe to run again: everything that already exists is skipped (labels are
updated in place). It makes one change at a time and waits one second after
each, as GitHub asks scripts to do, and it retries when GitHub reports a rate
limit. Set `ASSIGN=1` to also assign each issue to its owner; GitHub can only
assign people who already accepted the invitation to the repository.

The script was tested in planning against a stand-in for `gh` that records the
calls without contacting GitHub, including a second run and a rate-limit retry.
It was **not run against the real repository** (not run — run it in AHM-01).

## Labels

| Label | Color | Meaning |
|---|---|---|
| `type:task` | `#1D76DB` | A roadmap task |
| `type:bug` | `#D73A4A` | Something is broken |
| `type:question` | `#D876E3` | A question (prefer GitHub Discussions) |
| `type:docs` | `#0075CA` | Documentation only |
| `phase:alpha` | `#0E8A16` | Ships in v2.0-alpha (Fall 2026) |
| `phase:spring` | `#5319E7` | Ships in v2.0 (Spring 2027) |
| `area:engine` | `#FBCA04` | Adapters, Zeek, Suricata, rules, pipeline |
| `area:ai` | `#C5DEF5` | Local AI, citations, offline guard, evaluation |
| `area:mapping` | `#BFD4F2` | Compliance and ATT&CK mapping files, reports |
| `area:ui` | `#F9D0C4` | Dashboard pages |
| `area:api` | `#D4C5F9` | FastAPI backend |
| `area:storage` | `#C2E0C6` | SQLite state, Parquet events |
| `area:sensor` | `#FEF2C0` | Live sensor, NetFlow, host agent, hardware |
| `area:response` | `#E99695` | Blocking, preview, approvals, enforcers |
| `area:testing` | `#BFDADC` | Lab, captures, fixtures, integration tests, CI |
| `area:release` | `#006B75` | Packaging, Docker, releases, signing |
| `area:program` | `#EDEDED` | Planning, meetings, reviews, onboarding |
| `critical-path` | `#B60205` | A delay here delays the next demo |
| `contract-change` | `#B60205` | Changes a contract: Jaiden reviews, Security Lead approves |
| `blocked` | `#000000` | Waiting on another task (say which in a comment) |
| `needs-hardware` | `#FEF2C0` | Has steps marked: not run, verify on hardware |
| `owner:ahmad` | `#EDEDED` | Assigned to Ahmad |
| `owner:jaiden` | `#EDEDED` | Assigned to Jaiden |
| `owner:fiona` | `#EDEDED` | Assigned to Fiona |
| `owner:jakub` | `#EDEDED` | Assigned to Jakub |
| `owner:jonattan` | `#EDEDED` | Assigned to Jonattan |
| `owner:ali` | `#EDEDED` | Assigned to Ali |
| `owner:amory` | `#EDEDED` | Assigned to Amory |
| `owner:karthik` | `#EDEDED` | Assigned to Karthik |

## Milestones

| Milestone | Due | What it means |
|---|---|---|
| `W0 Onboarding and contracts` | 2026-10-09 | Everyone has a merged pull request; repo restructured; CI runs; contracts merged. |
| `W1 Building blocks` | 2026-10-16 | Adapters, rules, lab captures and fixtures, normalizer, inventory, citation check. |
| `W2 First end-to-end demo` | 2026-10-23 | maxguard analyze turns telnet.pcap into a mapped, explained finding. |
| `W3 API and alert queue` | 2026-10-30 | Upload in the browser; alerts stored and listed; CI runs integration tests. |
| `W4 Full offline report` | 2026-11-06 | Alert detail with Analyst and Home modes; Suricata in the pipeline; works unplugged. |
| `W5 Alpha feature freeze` | 2026-11-13 | All alpha features merged; CPG 2.0 and CJIS v6.1 mappings; bug fixes only after this. |
| `W6 Release candidate` | 2026-11-20 | v2.0-alpha-rc1 tagged and handed to an outside tester. |
| `W8 v2.0-alpha` | 2026-12-04 | v2.0-alpha released; acceptance test passes; presentation delivered. |
| `S1-S4 Live sensor` | 2027-02-12 | Pi sensor on the mirror port; logs reach the console every 15 minutes; timeline and device pages. |
| `S5-S8 Respond` | 2027-03-12 | Generated rules, preview before you block, approvals, OPNsense; signed intel bundles; JA4. |
| `S9-S11 Detect more` | 2027-04-16 | Decoys, per-device baselines, NetFlow/IPFIX input. |
| `S12 v2.0 feature freeze` | 2027-04-23 | Host agent; all v2.0 features merged. |
| `S13 v2.0 release candidate` | 2027-04-30 | v2.0-rc1 tagged; outside tester. |
| `S14 v2.0` | 2027-05-07 | v2.0 released; acceptance test passes. |

## The 69 issues

| Issue title | Owner | Milestone | Labels | Needs first |
|---|---|---|---|---|
| [AHM-00: Week 0 onboarding (Ahmad)](roadmap/ahmad.md#week-0--onboarding-due-friday-october-9-2026) | Ahmad | `W0 Onboarding and contracts` | `type:task` `phase:alpha` `owner:ahmad` `area:program` | — |
| [JAI-00: Week 0 onboarding (Jaiden)](roadmap/jaiden.md#week-0--onboarding-due-friday-october-9-2026) | Jaiden | `W0 Onboarding and contracts` | `type:task` `phase:alpha` `owner:jaiden` `area:program` | — |
| [FIO-00: Week 0 onboarding (Fiona)](roadmap/fiona.md#week-0--onboarding-due-friday-october-9-2026) | Fiona | `W0 Onboarding and contracts` | `type:task` `phase:alpha` `owner:fiona` `area:program` | — |
| [JAK-00: Week 0 onboarding (Jakub)](roadmap/jakub.md#week-0--onboarding-due-friday-october-9-2026) | Jakub | `W0 Onboarding and contracts` | `type:task` `phase:alpha` `owner:jakub` `area:program` | — |
| [JON-00: Week 0 onboarding (Jonattan)](roadmap/jonattan.md#week-0--onboarding-due-friday-october-9-2026) | Jonattan | `W0 Onboarding and contracts` | `type:task` `phase:alpha` `owner:jonattan` `area:program` | — |
| [ALI-00: Week 0 onboarding (Ali)](roadmap/ali.md#week-0--onboarding-due-friday-october-9-2026) | Ali | `W0 Onboarding and contracts` | `type:task` `phase:alpha` `owner:ali` `area:program` | — |
| [AMO-00: Week 0 onboarding (Amory)](roadmap/amory.md#week-0--onboarding-due-friday-october-9-2026) | Amory | `W0 Onboarding and contracts` | `type:task` `phase:alpha` `owner:amory` `area:program` | — |
| [KAR-00: Week 0 onboarding (Karthik)](roadmap/karthik.md#week-0--onboarding-due-friday-october-9-2026) | Karthik | `W0 Onboarding and contracts` | `type:task` `phase:alpha` `owner:karthik` `area:program` | — |
| [AHM-01: Set up GitHub for the team: access, Discussions, labels, milestones, issues](roadmap/ahmad.md#ahm-01-set-up-github-for-the-team-access-discussions-labels-milestones-issues) | Ahmad | `W0 Onboarding and contracts` | `type:task` `phase:alpha` `owner:ahmad` `area:program` `critical-path` | — |
| [JAI-01: Restructure the repository, add packaging and CI](roadmap/jaiden.md#jai-01-restructure-the-repository-add-packaging-and-ci) | Jaiden | `W0 Onboarding and contracts` | `type:task` `phase:alpha` `owner:jaiden` `area:release` `critical-path` | — |
| [JAI-02: Merge the three contracts in their v2.0 form](roadmap/jaiden.md#jai-02-merge-the-three-contracts-in-their-v20-form) | Jaiden | `W0 Onboarding and contracts` | `type:task` `phase:alpha` `owner:jaiden` `area:engine` `critical-path` `contract-change` | JAI-01 |
| [KAR-01: Traffic lab and the 14 test captures](roadmap/karthik.md#kar-01-traffic-lab-and-the-14-test-captures) | Karthik | `W0 Onboarding and contracts` | `type:task` `phase:alpha` `owner:karthik` `area:testing` `critical-path` | — |
| [JAK-01: MaxGuard's Zeek scripts: cleartext sessions and asset tracking](roadmap/jakub.md#jak-01-maxguards-zeek-scripts-cleartext-sessions-and-asset-tracking) | Jakub | `W1 Building blocks` | `type:task` `phase:alpha` `owner:jakub` `area:engine` `critical-path` | JAI-01, KAR-01 |
| [JAK-02: Suricata configuration: Community ID and JA4](roadmap/jakub.md#jak-02-suricata-configuration-community-id-and-ja4) | Jakub | `W1 Building blocks` | `type:task` `phase:alpha` `owner:jakub` `area:engine` `critical-path` | KAR-01 |
| [KAR-02: Test fixtures: Zeek and Suricata output for every capture](roadmap/karthik.md#kar-02-test-fixtures-zeek-and-suricata-output-for-every-capture) | Karthik | `W1 Building blocks` | `type:task` `phase:alpha` `owner:karthik` `area:testing` `critical-path` | KAR-01, JAK-01, JAK-02, JAI-01 |
| [FIO-01: Zeek runner and the two input adapters](roadmap/fiona.md#fio-01-zeek-runner-and-the-two-input-adapters) | Fiona | `W1 Building blocks` | `type:task` `phase:alpha` `owner:fiona` `area:engine` `critical-path` | JAI-02, KAR-02 |
| [FIO-02: TLS and certificate rules](roadmap/fiona.md#fio-02-tls-and-certificate-rules) | Fiona | `W1 Building blocks` | `type:task` `phase:alpha` `owner:fiona` `area:engine` `critical-path` | FIO-01, KAR-02 |
| [JAK-03: Cleartext and RDP rules (the rule set is complete)](roadmap/jakub.md#jak-03-cleartext-and-rdp-rules-the-rule-set-is-complete) | Jakub | `W1 Building blocks` | `type:task` `phase:alpha` `owner:jakub` `area:engine` `critical-path` | FIO-02, JAK-01, KAR-02 |
| [JAI-03: Common event schema: the normalizer and record lookup](roadmap/jaiden.md#jai-03-common-event-schema-the-normalizer-and-record-lookup) | Jaiden | `W1 Building blocks` | `type:task` `phase:alpha` `owner:jaiden` `area:engine` `area:storage` `critical-path` | JAI-02, KAR-02, FIO-01, FIO-02, JAK-03 |
| [JAK-04: Asset inventory](roadmap/jakub.md#jak-04-asset-inventory) | Jakub | `W1 Building blocks` | `type:task` `phase:alpha` `owner:jakub` `area:engine` | JAK-03, KAR-02 |
| [JON-01: Citation validator: no evidence, no sentence](roadmap/jonattan.md#jon-01-citation-validator-no-evidence-no-sentence) | Jonattan | `W1 Building blocks` | `type:task` `phase:alpha` `owner:jonattan` `area:ai` `critical-path` | JAI-02 |
| [AMO-01: NIST SP 800-53 mapping file and the mapping checks](roadmap/amory.md#amo-01-nist-sp-800-53-mapping-file-and-the-mapping-checks) | Amory | `W1 Building blocks` | `type:task` `phase:alpha` `owner:amory` `area:mapping` `critical-path` | JAI-02, FIO-02, JAK-03 |
| [JAI-04: The engine image and the Compose files](roadmap/jaiden.md#jai-04-the-engine-image-and-the-compose-files) | Jaiden | `W1 Building blocks` | `type:task` `phase:alpha` `owner:jaiden` `area:release` `critical-path` | JAI-01, AMO-01 |
| [ALI-01: Model shortlist and license check](roadmap/ali.md#ali-01-model-shortlist-and-license-check) | Ali | `W1 Building blocks` | `type:task` `phase:alpha` `owner:ali` `area:ai` | — |
| [JAI-05: The pipeline: one function from input to report](roadmap/jaiden.md#jai-05-the-pipeline-one-function-from-input-to-report) | Jaiden | `W2 First end-to-end demo` | `type:task` `phase:alpha` `owner:jaiden` `area:engine` `critical-path` | FIO-01, FIO-02, JAK-03, JAI-03, JAK-04, AMO-01 |
| [FIO-03: MITRE ATT&CK mapping file](roadmap/fiona.md#fio-03-mitre-attck-mapping-file) | Fiona | `W2 First end-to-end demo` | `type:task` `phase:alpha` `owner:fiona` `area:mapping` `critical-path` | AMO-01, JAK-03 |
| [FIO-04: The maxguard command, first version (JSON reports)](roadmap/fiona.md#fio-04-the-maxguard-command-first-version-json-reports) | Fiona | `W2 First end-to-end demo` | `type:task` `phase:alpha` `owner:fiona` `area:engine` `critical-path` | JAI-05, FIO-03 |
| [JON-02: Ollama client: one evidence-citing explanation per finding](roadmap/jonattan.md#jon-02-ollama-client-one-evidence-citing-explanation-per-finding) | Jonattan | `W2 First end-to-end demo` | `type:task` `phase:alpha` `owner:jonattan` `area:ai` `critical-path` | JON-01, JAI-03, JAK-03 |
| [ALI-02: Evaluation set: the same 13 questions for every model](roadmap/ali.md#ali-02-evaluation-set-the-same-13-questions-for-every-model) | Ali | `W2 First end-to-end demo` | `type:task` `phase:alpha` `owner:ali` `area:ai` | FIO-02, JAK-03, AMO-01, JAI-03 |
| [KAR-03: Integration tests: the real pipeline on every capture](roadmap/karthik.md#kar-03-integration-tests-the-real-pipeline-on-every-capture) | Karthik | `W2 First end-to-end demo` | `type:task` `phase:alpha` `owner:karthik` `area:testing` `critical-path` | JAI-05, JAI-04, KAR-02 |
| [JAI-06: Storage: alerts in SQLite, events in hourly Parquet files](roadmap/jaiden.md#jai-06-storage-alerts-in-sqlite-events-in-hourly-parquet-files) | Jaiden | `W3 API and alert queue` | `type:task` `phase:alpha` `owner:jaiden` `area:storage` `critical-path` | JAI-03 |
| [JON-03: Offline guard: make accidental network access fail loudly](roadmap/jonattan.md#jon-03-offline-guard-make-accidental-network-access-fail-loudly) | Jonattan | `W3 API and alert queue` | `type:task` `phase:alpha` `owner:jonattan` `area:ai` | JON-02 |
| [JAI-07: The API: uploads, alerts, events, live updates, sensor ingest](roadmap/jaiden.md#jai-07-the-api-uploads-alerts-events-live-updates-sensor-ingest) | Jaiden | `W3 API and alert queue` | `type:task` `phase:alpha` `owner:jaiden` `area:api` `critical-path` | JAI-05, JAI-06, JON-03 |
| [AMO-02: PCI DSS v4.0.1 rows, checked in the official document](roadmap/amory.md#amo-02-pci-dss-v401-rows-checked-in-the-official-document) | Amory | `W3 API and alert queue` | `type:task` `phase:alpha` `owner:amory` `area:mapping` | AMO-01 |
| [ALI-03: Benchmark script: speed, citations, and unsupported details](roadmap/ali.md#ali-03-benchmark-script-speed-citations-and-unsupported-details) | Ali | `W3 API and alert queue` | `type:task` `phase:alpha` `owner:ali` `area:ai` | ALI-02, JON-02 |
| [KAR-04: CI runs the integration tests, plus a determinism test](roadmap/karthik.md#kar-04-ci-runs-the-integration-tests-plus-a-determinism-test) | Karthik | `W3 API and alert queue` | `type:task` `phase:alpha` `owner:karthik` `area:testing` `area:release` | KAR-03 |
| [AHM-02: Dashboard: layout, alert queue, and upload page](roadmap/ahmad.md#ahm-02-dashboard-layout-alert-queue-and-upload-page) | Ahmad | `W3 API and alert queue` | `type:task` `phase:alpha` `owner:ahmad` `area:ui` `critical-path` | JAI-07 |
| [JAK-05: Suricata in the pipeline](roadmap/jakub.md#jak-05-suricata-in-the-pipeline) | Jakub | `W4 Full offline report` | `type:task` `phase:alpha` `owner:jakub` `area:engine` | JAK-02, FIO-01, JAI-05, JAI-07 |
| [AMO-03: Report export: JSON, CSV, and HTML](roadmap/amory.md#amo-03-report-export-json-csv-and-html) | Amory | `W4 Full offline report` | `type:task` `phase:alpha` `owner:amory` `area:mapping` `critical-path` | JAI-05 |
| [FIO-05: CLI: CSV and HTML reports, and --offline](roadmap/fiona.md#fio-05-cli-csv-and-html-reports-and---offline) | Fiona | `W4 Full offline report` | `type:task` `phase:alpha` `owner:fiona` `area:engine` | FIO-04, AMO-03, JON-03 |
| [JON-04: Home mode text for every rule](roadmap/jonattan.md#jon-04-home-mode-text-for-every-rule) | Jonattan | `W4 Full offline report` | `type:task` `phase:alpha` `owner:jonattan` `area:ai` `area:ui` | JON-01, JAK-03 |
| [AHM-03: Alert detail page with Analyst and Home modes](roadmap/ahmad.md#ahm-03-alert-detail-page-with-analyst-and-home-modes) | Ahmad | `W4 Full offline report` | `type:task` `phase:alpha` `owner:ahmad` `area:ui` `critical-path` | AHM-02, JON-02, JON-04 |
| [ALI-04: Run the benchmark on both tiers and propose the default models](roadmap/ali.md#ali-04-run-the-benchmark-on-both-tiers-and-propose-the-default-models) | Ali | `W4 Full offline report` | `type:task` `phase:alpha` `owner:ali` `area:ai` `critical-path` `needs-hardware` | ALI-01, ALI-03 |
| [JAI-08: Ed25519 signing library](roadmap/jaiden.md#jai-08-ed25519-signing-library) | Jaiden | `W5 Alpha feature freeze` | `type:task` `phase:alpha` `owner:jaiden` `area:release` | JAI-01 |
| [AMO-04: CISA CPG 2.0 and CJIS v6.1 rows](roadmap/amory.md#amo-04-cisa-cpg-20-and-cjis-v61-rows) | Amory | `W5 Alpha feature freeze` | `type:task` `phase:alpha` `owner:amory` `area:mapping` | AMO-02 |
| [AHM-04: Security review of the alpha](roadmap/ahmad.md#ahm-04-security-review-of-the-alpha) | Ahmad | `W5 Alpha feature freeze` | `type:task` `phase:alpha` `owner:ahmad` `area:program` | AHM-03, JON-03, AMO-03 |
| [JON-05: Offline bundle: install MaxGuard on a machine with no internet](roadmap/jonattan.md#jon-05-offline-bundle-install-maxguard-on-a-machine-with-no-internet) | Jonattan | `W6 Release candidate` | `type:task` `phase:alpha` `owner:jonattan` `area:release` `critical-path` | JAI-04, ALI-04 |
| [JAI-09: Release workflow and v2.0-alpha-rc1](roadmap/jaiden.md#jai-09-release-workflow-and-v20-alpha-rc1) | Jaiden | `W6 Release candidate` | `type:task` `phase:alpha` `owner:jaiden` `area:release` `critical-path` | JAI-04, KAR-04, JON-05 |
| [KAR-05: Release-candidate test with an outside tester](roadmap/karthik.md#kar-05-release-candidate-test-with-an-outside-tester) | Karthik | `W6 Release candidate` | `type:task` `phase:alpha` `owner:karthik` `area:testing` `area:release` `critical-path` | JAI-09, JON-05 |
| [JAI-10: Release v2.0-alpha](roadmap/jaiden.md#jai-10-release-v20-alpha) | Jaiden | `W8 v2.0-alpha` | `type:task` `phase:alpha` `owner:jaiden` `area:release` `critical-path` | JAI-09, KAR-05 |
| [JAK-06: Build the reference lab and prove the mirror works](roadmap/jakub.md#jak-06-build-the-reference-lab-and-prove-the-mirror-works) | Jakub | `W8 v2.0-alpha` | `type:task` `phase:alpha` `owner:jakub` `area:sensor` `needs-hardware` | JAK-02 |
| [AHM-05: Alpha acceptance test and presentation](roadmap/ahmad.md#ahm-05-alpha-acceptance-test-and-presentation) | Ahmad | `W8 v2.0-alpha` | `type:task` `phase:alpha` `owner:ahmad` `area:program` `critical-path` | JAI-10, KAR-05 |
| [JAK-08: Device attribution: which device is behind each IP address](roadmap/jakub.md#jak-08-device-attribution-which-device-is-behind-each-ip-address) | Jakub | `S1-S4 Live sensor` | `type:task` `phase:spring` `owner:jakub` `area:sensor` | JAK-04, KAR-02 |
| [JAK-07: Live sensor: capture, rotation, and shipping to the console](roadmap/jakub.md#jak-07-live-sensor-capture-rotation-and-shipping-to-the-console) | Jakub | `S1-S4 Live sensor` | `type:task` `phase:spring` `owner:jakub` `area:sensor` `critical-path` `needs-hardware` | JAK-06, JAI-07, JAK-08 |
| [AMO-05: Chain-of-custody log](roadmap/amory.md#amo-05-chain-of-custody-log) | Amory | `S1-S4 Live sensor` | `type:task` `phase:spring` `owner:amory` `area:mapping` `area:release` | JAI-08 |
| [AHM-06: IP timeline and device inventory pages](roadmap/ahmad.md#ahm-06-ip-timeline-and-device-inventory-pages) | Ahmad | `S1-S4 Live sensor` | `type:task` `phase:spring` `owner:ahmad` `area:ui` | AHM-03, JAK-08, JAI-07 |
| [KAR-06: End-to-end test of the live sensor on the lab](roadmap/karthik.md#kar-06-end-to-end-test-of-the-live-sensor-on-the-lab) | Karthik | `S1-S4 Live sensor` | `type:task` `phase:spring` `owner:karthik` `area:testing` `area:sensor` `needs-hardware` | JAK-07 |
| [JAK-09: JA4 watchlist rule](roadmap/jakub.md#jak-09-ja4-watchlist-rule) | Jakub | `S5-S8 Respond` | `type:task` `phase:spring` `owner:jakub` `area:engine` `area:sensor` | JAK-05 |
| [JAI-11: Signed offline intel bundles](roadmap/jaiden.md#jai-11-signed-offline-intel-bundles) | Jaiden | `S5-S8 Respond` | `type:task` `phase:spring` `owner:jaiden` `area:release` | JAI-08, JAK-09 |
| [AHM-07: Response: block proposals, generated rules, and preview before you block](roadmap/ahmad.md#ahm-07-response-block-proposals-generated-rules-and-preview-before-you-block) | Ahmad | `S5-S8 Respond` | `type:task` `phase:spring` `owner:ahmad` `area:response` | JAI-06, JAI-07 |
| [AHM-08: Response: approvals, audit, revert, and the OPNsense connector](roadmap/ahmad.md#ahm-08-response-approvals-audit-revert-and-the-opnsense-connector) | Ahmad | `S5-S8 Respond` | `type:task` `phase:spring` `owner:ahmad` `area:response` `needs-hardware` | AHM-07, JON-03 |
| [JON-06: Prompt-injection tests for the AI layer](roadmap/jonattan.md#jon-06-prompt-injection-tests-for-the-ai-layer) | Jonattan | `S5-S8 Respond` | `type:task` `phase:spring` `owner:jonattan` `area:ai` | JON-02, ALI-03 |
| [ALI-05: Re-evaluate the models against prompt injection and the spring rules](roadmap/ali.md#ali-05-re-evaluate-the-models-against-prompt-injection-and-the-spring-rules) | Ali | `S5-S8 Respond` | `type:task` `phase:spring` `owner:ali` `area:ai` `needs-hardware` | ALI-04, JON-06 |
| [FIO-06: Decoys: fake services on their own IP address](roadmap/fiona.md#fio-06-decoys-fake-services-on-their-own-ip-address) | Fiona | `S9-S11 Detect more` | `type:task` `phase:spring` `owner:fiona` `area:engine` | JAI-07, JON-04 |
| [FIO-07: Per-device baselines](roadmap/fiona.md#fio-07-per-device-baselines) | Fiona | `S9-S11 Detect more` | `type:task` `phase:spring` `owner:fiona` `area:engine` | JAI-06, JAK-08 |
| [JAK-10: NetFlow and IPFIX input](roadmap/jakub.md#jak-10-netflow-and-ipfix-input) | Jakub | `S9-S11 Detect more` | `type:task` `phase:spring` `owner:jakub` `area:sensor` | JAI-07, JAI-03 |
| [JAK-11: Host agent for one computer](roadmap/jakub.md#jak-11-host-agent-for-one-computer) | Jakub | `S12 v2.0 feature freeze` | `type:task` `phase:spring` `owner:jakub` `area:sensor` | JAI-07 |
| [JAI-12: Release v2.0-rc1 and v2.0](roadmap/jaiden.md#jai-12-release-v20-rc1-and-v20) | Jaiden | `S13 v2.0 release candidate` | `type:task` `phase:spring` `owner:jaiden` `area:release` `critical-path` | JAI-11, JAK-07, AHM-08 |
| [AHM-09: v2.0 acceptance test](roadmap/ahmad.md#ahm-09-v20-acceptance-test) | Ahmad | `S14 v2.0` | `type:task` `phase:spring` `owner:ahmad` `area:program` `critical-path` | JAI-12 |

Bugs and questions use the forms in `.github/ISSUE_TEMPLATE/`; questions
belong in GitHub Discussions first.
