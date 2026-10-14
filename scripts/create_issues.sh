#!/usr/bin/env bash
# Create the MaxGuard v2.0 labels, milestones, project board and roadmap issues.
#
# The data at the bottom was generated from the roadmap in docs/roadmap/ during
# planning (October 6, 2026); docs/ISSUES.md lists the same rows. When a task is
# added or changed in the roadmap, update its row here as well: one line per
# issue, fields separated by "|" (title|labels|milestone|owner|link|goal|needs).
#
# Usage (from the repository root, with gh logged in):
#   gh auth refresh -s project                 # once: the project board needs it
#   DRY_RUN=1 bash scripts/create_issues.sh    # print every change, make none
#   bash scripts/create_issues.sh              # create what is missing
#   ASSIGN=1 bash scripts/create_issues.sh     # also assign issues to their owners
#
# Safe to run again: existing milestones, issues and the project are skipped,
# labels are updated in place. One change at a time with a pause after each,
# and a retry with back-off when GitHub reports a rate limit
# (https://docs.github.com/en/rest/using-the-rest-api/best-practices-for-using-the-rest-api).
set -euo pipefail

REPO="${REPO:-ahmadalkhoudeir/maxguard}"
OWNER="${REPO%%/*}"
PROJECT_TITLE="${PROJECT_TITLE:-MaxGuard v2.0 Roadmap}"
DRY_RUN="${DRY_RUN:-0}"
ASSIGN="${ASSIGN:-0}"
PAUSE="${PAUSE:-1}"   # seconds to wait after each change

# Print a change; run it unless DRY_RUN=1. Retries up to 3 times on a rate limit.
run() {
  if [[ "$DRY_RUN" == 1 ]]; then
    printf 'would run:'; printf ' %q' "$@"; printf '\n'
    return 0
  fi
  local attempt=1 wait=60 out
  while true; do
    if out=$("$@" 2>&1); then
      printf '%s\n' "$out"
      sleep "$PAUSE"
      return 0
    fi
    if [[ "$out" == *"rate limit"* && $attempt -lt 4 ]]; then
      echo "rate limited; waiting ${wait}s (attempt $attempt of 3)" >&2
      sleep "${RETRY_WAIT:-$wait}"
      wait=$((wait * 2))
      attempt=$((attempt + 1))
    else
      printf '%s\n' "$out" >&2
      return 1
    fi
  done
}

if ! gh auth status >/dev/null 2>&1; then
  echo "gh is not logged in: run 'gh auth login' first" >&2
  exit 4
fi

echo "== labels"
while IFS='|' read -r name color description; do
  [[ -z "$name" ]] && continue
  run gh label create "$name" --repo "$REPO" --color "$color" --description "$description" --force
done <<'LABELS'
type:task|1D76DB|A roadmap task
type:bug|D73A4A|Something is broken
type:question|D876E3|A question (prefer GitHub Discussions)
type:docs|0075CA|Documentation only
phase:alpha|0E8A16|Ships in v2.0-alpha (Fall 2026)
phase:spring|5319E7|Ships in v2.0 (Spring 2027)
area:engine|FBCA04|Adapters, Zeek, Suricata, rules, pipeline
area:ai|C5DEF5|Local AI, citations, offline guard, evaluation
area:mapping|BFD4F2|Compliance and ATT&CK mapping files, reports
area:ui|F9D0C4|Dashboard pages
area:api|D4C5F9|FastAPI backend
area:storage|C2E0C6|SQLite state, Parquet events
area:sensor|FEF2C0|Live sensor, NetFlow, host agent, hardware
area:response|E99695|Blocking, preview, approvals, enforcers
area:testing|BFDADC|Lab, captures, fixtures, integration tests, CI
area:release|006B75|Packaging, Docker, releases, signing
area:program|EDEDED|Planning, meetings, reviews, onboarding
critical-path|B60205|A delay here delays the next demo
contract-change|B60205|Changes a contract: Jaiden reviews, Security Lead approves
blocked|000000|Waiting on another task (say which in a comment)
needs-hardware|FEF2C0|Has steps marked: not run, verify on hardware
owner:ahmad|EDEDED|Assigned to Ahmad
owner:jaiden|EDEDED|Assigned to Jaiden
owner:fiona|EDEDED|Assigned to Fiona
owner:jakub|EDEDED|Assigned to Jakub
owner:jonattan|EDEDED|Assigned to Jonattan
owner:ali|EDEDED|Assigned to Ali
owner:amory|EDEDED|Assigned to Amory
owner:karthik|EDEDED|Assigned to Karthik
LABELS

echo "== milestones"
existing_milestones=$(gh api "repos/$REPO/milestones?state=all&per_page=100" --paginate --jq '.[].title')
while IFS='|' read -r title due description; do
  [[ -z "$title" ]] && continue
  if grep -Fxq -- "$title" <<<"$existing_milestones"; then
    echo "milestone exists: $title"
    continue
  fi
  run gh api "repos/$REPO/milestones" -f title="$title" -f due_on="${due}T23:59:59Z" \
    -f description="$description" >/dev/null
done <<'MILESTONES'
W0 Onboarding and contracts|2026-10-09|Everyone has a merged pull request; repo restructured; CI runs; contracts merged.
W1 Building blocks|2026-10-16|Adapters, rules, lab captures and fixtures, normalizer, inventory, citation check.
W2 First end-to-end demo|2026-10-23|maxguard analyze turns telnet.pcap into a mapped, explained finding.
W3 API and alert queue|2026-10-30|Upload in the browser; alerts stored and listed; CI runs integration tests.
W4 Full offline report|2026-11-06|Alert detail with Analyst and Home modes; Suricata in the pipeline; works unplugged.
W5 Alpha feature freeze|2026-11-13|All alpha features merged; CPG 2.0 and CJIS v6.1 mappings; bug fixes only after this.
W6 Release candidate|2026-11-20|v2.0-alpha-rc1 tagged and handed to an outside tester.
W8 v2.0-alpha|2026-12-04|v2.0-alpha released; acceptance test passes; presentation delivered.
S1-S4 Live sensor|2027-02-12|Pi sensor on the mirror port; logs reach the console every 15 minutes; timeline and device pages.
S5-S8 Respond|2027-03-12|Generated rules, preview before you block, approvals, OPNsense; signed intel bundles; JA4.
S9-S11 Detect more|2027-04-16|Decoys, per-device baselines, NetFlow/IPFIX input.
S12 v2.0 feature freeze|2027-04-23|Host agent; all v2.0 features merged.
S13 v2.0 release candidate|2027-04-30|v2.0-rc1 tagged; outside tester.
S14 v2.0|2027-05-07|v2.0 released; acceptance test passes.
MILESTONES

echo "== project"
project=$(gh project list --owner "$OWNER" --format json \
  --jq ".projects[] | select(.title==\"$PROJECT_TITLE\") | .number" | head -n 1)
if [[ -z "$project" ]]; then
  if [[ "$DRY_RUN" == 1 ]]; then
    run gh project create --owner "$OWNER" --title "$PROJECT_TITLE"
    project="(new)"
  else
    project=$(gh project create --owner "$OWNER" --title "$PROJECT_TITLE" --format json --jq .number)
    sleep "$PAUSE"
    run gh project link "$project" --owner "$OWNER" --repo "${REPO#*/}" >/dev/null
  fi
fi
echo "project number: $project"

echo "== issues"
existing_issues=$(gh issue list --repo "$REPO" --state all --limit 1000 --json title --jq '.[].title')
body_file=$(mktemp)
trap 'rm -f "$body_file"' EXIT
created=0
skipped=0
while IFS='|' read -r title labels milestone assignee doc goal needs; do
  [[ -z "$title" ]] && continue
  if grep -Fxq -- "$title" <<<"$existing_issues"; then
    skipped=$((skipped + 1))
    continue
  fi
  # shellcheck disable=SC2016  # the backticks are Markdown code in the issue body, not a command
  printf '%s\n\n**Task:** https://github.com/%s/blob/main/%s\n\n**Needs first:** %s\n\nThe task lists the exact steps and the pull request checklist. Close this issue from the pull request with `Closes #<this number>`.\n' \
    "$goal" "$REPO" "$doc" "$needs" >"$body_file"
  assign=()
  [[ "$ASSIGN" == 1 ]] && assign=(--assignee "$assignee")
  create=(gh issue create --repo "$REPO" --title "$title" --body-file "$body_file"
          --label "$labels" --milestone "$milestone" ${assign[@]+"${assign[@]}"})
  if [[ "$DRY_RUN" == 1 ]]; then
    run "${create[@]}"
  else
    url=$(run "${create[@]}")
    echo "$url"
    run gh project item-add "$project" --owner "$OWNER" --url "$url" >/dev/null
  fi
  created=$((created + 1))
done <<'ISSUES'
AHM-00: Week 0 onboarding (Ahmad)|type:task,phase:alpha,owner:ahmad,area:program|W0 Onboarding and contracts|ahmadalkhoudeir|docs/roadmap/ahmad.md#week-0--onboarding-due-friday-october-9-2026|Install the tools, clone the repository, merge your first pull request, and post in the Week 0 check-in.|nothing
JAI-00: Week 0 onboarding (Jaiden)|type:task,phase:alpha,owner:jaiden,area:program|W0 Onboarding and contracts|JWinborne1|docs/roadmap/jaiden.md#week-0--onboarding-due-friday-october-9-2026|Install the tools, clone the repository, merge your first pull request, and post in the Week 0 check-in.|nothing
FIO-00: Week 0 onboarding (Fiona)|type:task,phase:alpha,owner:fiona,area:program|W0 Onboarding and contracts|flau0306|docs/roadmap/fiona.md#week-0--onboarding-due-friday-october-9-2026|Install the tools, clone the repository, merge your first pull request, and post in the Week 0 check-in.|nothing
JAK-00: Week 0 onboarding (Jakub)|type:task,phase:alpha,owner:jakub,area:program|W0 Onboarding and contracts|SXafir-byte|docs/roadmap/jakub.md#week-0--onboarding-due-friday-october-9-2026|Install the tools, clone the repository, merge your first pull request, and post in the Week 0 check-in.|nothing
JON-00: Week 0 onboarding (Jonattan)|type:task,phase:alpha,owner:jonattan,area:program|W0 Onboarding and contracts|MeliorExi|docs/roadmap/jonattan.md#week-0--onboarding-due-friday-october-9-2026|Install the tools, clone the repository, merge your first pull request, and post in the Week 0 check-in.|nothing
ALI-00: Week 0 onboarding (Ali)|type:task,phase:alpha,owner:ali,area:program|W0 Onboarding and contracts|al-kheder|docs/roadmap/ali.md#week-0--onboarding-due-friday-october-9-2026|Install the tools, clone the repository, merge your first pull request, and post in the Week 0 check-in.|nothing
AMO-00: Week 0 onboarding (Amory)|type:task,phase:alpha,owner:amory,area:program|W0 Onboarding and contracts|gettalife|docs/roadmap/amory.md#week-0--onboarding-due-friday-october-9-2026|Install the tools, clone the repository, merge your first pull request, and post in the Week 0 check-in.|nothing
KAR-00: Week 0 onboarding (Karthik)|type:task,phase:alpha,owner:karthik,area:program|W0 Onboarding and contracts|Karthiknair91|docs/roadmap/karthik.md#week-0--onboarding-due-friday-october-9-2026|Install the tools, clone the repository, merge your first pull request, and post in the Week 0 check-in.|nothing
AHM-01: Set up GitHub for the team: access, Discussions, labels, milestones, issues|type:task,phase:alpha,owner:ahmad,area:program,critical-path|W0 Onboarding and contracts|ahmadalkhoudeir|docs/roadmap/ahmad.md#ahm-01-set-up-github-for-the-team-access-discussions-labels-milestones-issues|Make the repository ready for eight people as early in Week 0 as possible: everyone has write access, Discussions is on with a pinned "Week 0 check-in", private vulnerability reporting is on, and every roadmap task exists as an issue with its labels and milestone on the project board.|nothing
JAI-01: Restructure the repository, add packaging and CI|type:task,phase:alpha,owner:jaiden,area:release,critical-path|W0 Onboarding and contracts|JWinborne1|docs/roadmap/jaiden.md#jai-01-restructure-the-repository-add-packaging-and-ci|Turn the v0.8 repository into the v2.0 layout: old code moves to `legacy/`, a `pyproject.toml` makes `pip install -e .` work for everyone, and GitHub Actions runs the linter and the tests on every pull request. Every other task builds on this one.|nothing
JAI-02: Merge the three contracts in their v2.0 form|type:task,phase:alpha,owner:jaiden,area:engine,critical-path,contract-change|W0 Onboarding and contracts|JWinborne1|docs/roadmap/jaiden.md#jai-02-merge-the-three-contracts-in-their-v20-form|Add the code everyone else builds against: Contract 1 (the `Finding` dataclass), the record and finding IDs, Contract 3 (the input adapter protocol), the rule registry, and Contract 2's loader for the mapping files. `docs/ARCHITECTURE.md` section 5 explains every extension; the original Fall 2026 code keeps working unchanged.|JAI-01
KAR-01: Traffic lab and the 14 test captures|type:task,phase:alpha,owner:karthik,area:testing,critical-path|W0 Onboarding and contracts|Karthiknair91|docs/roadmap/karthik.md#kar-01-traffic-lab-and-the-14-test-captures|Build MaxGuard's traffic lab: insecure test services and a client on an isolated Docker network, recorded by tcpdump. Record one small capture per weakness (plus a clean TLS 1.3 session and a DNS lookup that must trigger nothing) into `tests/pcaps/`. Every rule's tests are built on these captures.|nothing
JAK-01: MaxGuard's Zeek scripts: cleartext sessions and asset tracking|type:task,phase:alpha,owner:jakub,area:engine,critical-path|W1 Building blocks|SXafir-byte|docs/roadmap/jakub.md#jak-01-maxguards-zeek-scripts-cleartext-sessions-and-asset-tracking|Write the two Zeek scripts MaxGuard loads on every run. `cleartext.zeek` writes `maxguard_cleartext.log`, one line per real Telnet, POP3 or IMAP session that was not upgraded to TLS. `inventory.zeek` turns on Zeek's host, service and software tracking for every address, which the asset inventory (JAK-04) reads. `site.zeek` replaces Zeek's own `local` policy, without the scripts that make DNS lookups.|JAI-01, KAR-01
JAK-02: Suricata configuration: Community ID and JA4|type:task,phase:alpha,owner:jakub,area:engine,critical-path|W1 Building blocks|SXafir-byte|docs/roadmap/jakub.md#jak-02-suricata-configuration-community-id-and-ja4|Add MaxGuard's Suricata settings for reading captures: `eve.json` with flow, alert, DNS, HTTP, TLS (with the JA4 client fingerprint) and DHCP events, and the same Community ID that Zeek writes. Add the (empty) MaxGuard rules file that signed intel bundles fill later.|KAR-01
KAR-02: Test fixtures: Zeek and Suricata output for every capture|type:task,phase:alpha,owner:karthik,area:testing,critical-path|W1 Building blocks|Karthiknair91|docs/roadmap/karthik.md#kar-02-test-fixtures-zeek-and-suricata-output-for-every-capture|Write `scripts/make_fixtures.sh`, which runs Zeek 9.0.0 and Suricata 7.0.10 on every capture exactly the way MaxGuard does and saves the logs to `tests/fixtures/zeek/<capture>/`, and add the hand-made fixtures for traffic the lab does not make yet (DNS with DHCP, RDP, and tab-separated logs). Unit tests read these folders, so they run in seconds without Docker.|KAR-01, JAK-01, JAK-02, JAI-01
FIO-01: Zeek runner and the two input adapters|type:task,phase:alpha,owner:fiona,area:engine,critical-path|W1 Building blocks|flau0306|docs/roadmap/fiona.md#fio-01-zeek-runner-and-the-two-input-adapters|Write the code that turns what a user gives MaxGuard into a folder of Zeek logs: `run_zeek()` runs Zeek 9.0.0 on a capture, `PcapAdapter` accepts `.pcap`/`.pcapng` files, and `ZeekLogAdapter` accepts a folder, `.zip` or `.tar.gz` of logs that someone already has, including the old tab-separated (TSV) format. Both adapters follow Contract 3 (`maxguard/adapters/base.py`).|JAI-02, KAR-02
FIO-02: TLS and certificate rules|type:task,phase:alpha,owner:fiona,area:engine,critical-path|W1 Building blocks|flau0306|docs/roadmap/fiona.md#fio-02-tls-and-certificate-rules|Write six detection rules — outdated TLS version, weak cipher, expired, self-signed, weak-key, and SHA-1-signed certificates — each with a positive test (its capture triggers it) and a negative test (a capture that *almost* matches does not). Also add the tests that prove imported TSV logs find the same problems and that findings are identical on every run.|FIO-01, KAR-02
JAK-03: Cleartext and RDP rules (the rule set is complete)|type:task,phase:alpha,owner:jakub,area:engine,critical-path|W1 Building blocks|SXafir-byte|docs/roadmap/jakub.md#jak-03-cleartext-and-rdp-rules-the-rule-set-is-complete|Write the seven remaining Fall 2026 rules: FTP, Telnet, HTTP, HTTP on port 8080, POP3 and IMAP in cleartext, and RDP with only "standard RDP security". With them, all 13 rules are registered and every lab capture triggers exactly its own rule.|FIO-02, JAK-01, KAR-02
JAI-03: Common event schema: the normalizer and record lookup|type:task,phase:alpha,owner:jaiden,area:engine,area:storage,critical-path|W1 Building blocks|JWinborne1|docs/roadmap/jaiden.md#jai-03-common-event-schema-the-normalizer-and-record-lookup|Turn Zeek logs and Suricata's `eve.json` into one list of events with the same keys, whatever tool wrote them (`docs/ARCHITECTURE.md` section 6), and find the raw log records behind evidence IDs so the AI can show them to the model.|JAI-02, KAR-02, FIO-01, FIO-02, JAK-03
JAK-04: Asset inventory|type:task,phase:alpha,owner:jakub,area:engine|W1 Building blocks|SXafir-byte|docs/roadmap/jakub.md#jak-04-asset-inventory|Write `maxguard/inventory.py`: one row per IP address seen in the logs, with when it was first seen, the services it offered (`80/http`), the software named in its traffic, and how many findings involve it. The pipeline adds this list to every report, and the device inventory page shows it.|JAK-03, KAR-02
JON-01: Citation validator: no evidence, no sentence|type:task,phase:alpha,owner:jonattan,area:ai,critical-path|W1 Building blocks|MeliorExi|docs/roadmap/jonattan.md#jon-01-citation-validator-no-evidence-no-sentence|Write the check that enforces CLAUDE.md rule 3 in code: a sentence from the model is kept only if it cites at least one record ID and every ID it cites belongs to the finding being explained. Everything else is dropped and counted.|JAI-02
AMO-01: NIST SP 800-53 mapping file and the mapping checks|type:task,phase:alpha,owner:amory,area:mapping,critical-path|W1 Building blocks|gettalife|docs/roadmap/amory.md#amo-01-nist-sp-800-53-mapping-file-and-the-mapping-checks|Add the compliance mapping files (Contract 2): NIST SP 800-53 Rev. 5 (Release 5.2.0) with a verified row for every rule, the field guide `mappings/schema.md`, the PCI DSS, CISA CPG and CJIS files with their headers but no rows yet, and the tests that enforce CLAUDE.md rule 8 on every file.|JAI-02, FIO-02, JAK-03
JAI-04: The engine image and the Compose files|type:task,phase:alpha,owner:jaiden,area:release,critical-path|W1 Building blocks|JWinborne1|docs/roadmap/jaiden.md#jai-04-the-engine-image-and-the-compose-files|Package MaxGuard as a Docker image built on the official Zeek 9.0.0 image, with Suricata, MaxGuard in a virtual environment, and a non-root user, plus the Compose files that run it next to a local Ollama. Integration tests (KAR-03), the Week 2 demo with a capture, and the offline bundle all use this image.|JAI-01, AMO-01
ALI-01: Model shortlist and license check|type:task,phase:alpha,owner:ali,area:ai|W1 Building blocks|al-kheder|docs/roadmap/ali.md#ali-01-model-shortlist-and-license-check|Start `docs/model-eval/README.md`: the two hardware tiers, the shortlist of models for each, and for every model its license, whether MaxGuard may ship it in the offline bundle, and exactly what notice or attribution that requires. License is a hard gate: a model we may not redistribute cannot be the default.|nothing
JAI-05: The pipeline: one function from input to report|type:task,phase:alpha,owner:jaiden,area:engine,critical-path|W2 First end-to-end demo|JWinborne1|docs/roadmap/jaiden.md#jai-05-the-pipeline-one-function-from-input-to-report|Write `maxguard/pipeline.py`, the single function the CLI, the API, and the tests call: it picks the right adapter, gets Zeek logs, runs the rules, applies the mapping files, builds the event list and the asset inventory, asks the local AI (when asked to), and returns the report dictionary described in `docs/ARCHITECTURE.md` section 8.|FIO-01, FIO-02, JAK-03, JAI-03, JAK-04, AMO-01
FIO-03: MITRE ATT&CK mapping file|type:task,phase:alpha,owner:fiona,area:mapping,critical-path|W2 First end-to-end demo|flau0306|docs/roadmap/fiona.md#fio-03-mitre-attck-mapping-file|Add `mappings/attack.yaml`: for each rule, the ATT&CK technique an attacker would use against the weakness it finds (for example a cleartext password is collected with T1040 Network Sniffing). The loader puts these rows into `Finding.attack`, separate from the compliance controls.|AMO-01, JAK-03
FIO-04: The maxguard command, first version (JSON reports)|type:task,phase:alpha,owner:fiona,area:engine,critical-path|W2 First end-to-end demo|flau0306|docs/roadmap/fiona.md#fio-04-the-maxguard-command-first-version-json-reports|Give MaxGuard its command line: `maxguard analyze INPUT` runs the pipeline and writes a JSON report, with `--no-ai`, `-o FILE`, and `--frameworks`. Exit codes tell scripts what happened (0 ok, 2 bad input, 3 Zeek failed). This is the command shown at the Week 2 demo.|JAI-05, FIO-03
JON-02: Ollama client: one evidence-citing explanation per finding|type:task,phase:alpha,owner:jonattan,area:ai,critical-path|W2 First end-to-end demo|MeliorExi|docs/roadmap/jonattan.md#jon-02-ollama-client-one-evidence-citing-explanation-per-finding|Ask the local model (through Ollama) to explain each finding in 2 to 4 sentences, giving it the finding's facts and the raw log records behind it, and keep only the sentences that pass the citation check. This is the explanation shown at the Week 2 demo.|JON-01, JAI-03, JAK-03
ALI-02: Evaluation set: the same 13 questions for every model|type:task,phase:alpha,owner:ali,area:ai|W2 First end-to-end demo|al-kheder|docs/roadmap/ali.md#ali-02-evaluation-set-the-same-13-questions-for-every-model|Write `scripts/make_eval_set.py`, which turns the fixture logs into the evaluation set: one item per rule, holding the finding exactly as the pipeline gives it to the AI plus the raw log records it cites. Every model is then asked the same questions.|FIO-02, JAK-03, AMO-01, JAI-03
KAR-03: Integration tests: the real pipeline on every capture|type:task,phase:alpha,owner:karthik,area:testing,critical-path|W2 First end-to-end demo|Karthiknair91|docs/roadmap/karthik.md#kar-03-integration-tests-the-real-pipeline-on-every-capture|Write expected-result files and an integration test that runs the real pipeline on every capture inside the engine image and checks that each capture produces exactly the findings it should, and nothing it should not. Add fast unit checks of Suricata's saved output: a Community ID on every record and a JA4 on every TLS client hello.|JAI-05, JAI-04, KAR-02
JAI-06: Storage: alerts in SQLite, events in hourly Parquet files|type:task,phase:alpha,owner:jaiden,area:storage,critical-path|W3 API and alert queue|JWinborne1|docs/roadmap/jaiden.md#jai-06-storage-alerts-in-sqlite-events-in-hourly-parquet-files|Keep what the dashboard needs after an upload: `StateStore` (one SQLite file: analyses, alerts with status and assignee, and the audit trail) and `EventStore` (normalized events in one Parquet file per hour, queried with DuckDB). See `docs/ARCHITECTURE.md` section 9.|JAI-03
JON-03: Offline guard: make accidental network access fail loudly|type:task,phase:alpha,owner:jonattan,area:ai|W3 API and alert queue|MeliorExi|docs/roadmap/jonattan.md#jon-03-offline-guard-make-accidental-network-access-fail-loudly|Write `maxguard/offline.py`. When it is on (`MAXGUARD_OFFLINE=1` or `maxguard analyze --offline`), every Python connection and every host-name lookup is checked: only this machine, the Ollama host, and hosts the user lists are allowed; anything else raises `OfflineViolation` instead of leaving the computer.|JON-02
JAI-07: The API: uploads, alerts, events, live updates, sensor ingest|type:task,phase:alpha,owner:jaiden,area:api,critical-path|W3 API and alert queue|JWinborne1|docs/roadmap/jaiden.md#jai-07-the-api-uploads-alerts-events-live-updates-sensor-ingest|Write `maxguard/api/app.py` with `create_app(data_dir=None, *, explain=True)`: the JSON API in `docs/ARCHITECTURE.md` section 10 that the dashboard, the sensors, and the host agent use. Uploads run the pipeline and are saved to the two stores; the API is the only part of MaxGuard that reads the clock.|JAI-05, JAI-06, JON-03
AMO-02: PCI DSS v4.0.1 rows, checked in the official document|type:task,phase:alpha,owner:amory,area:mapping|W3 API and alert queue|gettalife|docs/roadmap/amory.md#amo-02-pci-dss-v401-rows-checked-in-the-official-document|Fill `mappings/pci_dss_4_0_1.yaml` with requirement numbers you read in the official PCI DSS v4.0.1 document, starting with `cleartext.telnet` (the demo finding), so the Week 4 report shows PCI DSS controls.|AMO-01
ALI-03: Benchmark script: speed, citations, and unsupported details|type:task,phase:alpha,owner:ali,area:ai|W3 API and alert queue|al-kheder|docs/roadmap/ali.md#ali-03-benchmark-script-speed-citations-and-unsupported-details|Write `scripts/benchmark_models.py`: for each model, run the evaluation set through MaxGuard's own `explain()` twice and record per question the seconds taken, sentences kept and dropped by the citation check, "unsupported details" (an address, port, host name, TLS version or cipher that is not in the evidence), and whether run 2 gave the same answer as run 1.|ALI-02, JON-02
KAR-04: CI runs the integration tests, plus a determinism test|type:task,phase:alpha,owner:karthik,area:testing,area:release|W3 API and alert queue|Karthiknair91|docs/roadmap/karthik.md#kar-04-ci-runs-the-integration-tests-plus-a-determinism-test|Add an `integration` job to CI that builds the engine image and runs the integration tests in it with networking off, and add a test that analyzes every capture twice and checks the two reports are identical.|KAR-03
AHM-02: Dashboard: layout, alert queue, and upload page|type:task,phase:alpha,owner:ahmad,area:ui,critical-path|W3 API and alert queue|ahmadalkhoudeir|docs/roadmap/ahmad.md#ahm-02-dashboard-layout-alert-queue-and-upload-page|Build the first dashboard pages with FastAPI, Jinja2 and htmx: a base layout with the privacy note and the Analyst/Home switch, the alert queue (severity, title, source → destination:port, count, status, assignee, last seen) with filters and live refresh, and an upload page.|JAI-07
JAK-05: Suricata in the pipeline|type:task,phase:alpha,owner:jakub,area:engine|W4 Full offline report|SXafir-byte|docs/roadmap/jakub.md#jak-05-suricata-in-the-pipeline|When Suricata is installed (it is, in the engine image), run it next to Zeek on every capture so `eve.json` lands in the same log folder. The normalizer already reads it, so Suricata's events and JA4 fingerprints appear in the report and the event store. On a laptop without Suricata nothing changes.|JAK-02, FIO-01, JAI-05, JAI-07
AMO-03: Report export: JSON, CSV, and HTML|type:task,phase:alpha,owner:amory,area:mapping,critical-path|W4 Full offline report|gettalife|docs/roadmap/amory.md#amo-03-report-export-json-csv-and-html|Write `maxguard/report.py`, which turns the report into three formats: JSON (all of it), CSV (one row per finding and control, for spreadsheets and auditors), and one self-contained HTML page that opens offline. All three escape text that came from network traffic.|JAI-05
FIO-05: CLI: CSV and HTML reports, and --offline|type:task,phase:alpha,owner:fiona,area:engine|W4 Full offline report|flau0306|docs/roadmap/fiona.md#fio-05-cli-csv-and-html-reports-and---offline|Finish the CLI for the alpha: `--format` (json, csv, or html) uses Amory's report exporters (AMO-03), and `--offline` turns on Jonattan's offline guard (JON-03) before anything else runs, so nothing in the analysis can reach the network.|FIO-04, AMO-03, JON-03
JON-04: Home mode text for every rule|type:task,phase:alpha,owner:jonattan,area:ai,area:ui|W4 Full offline report|MeliorExi|docs/roadmap/jonattan.md#jon-04-home-mode-text-for-every-rule|Write the plain-language headline and one action for each rule that Home mode shows instead of the technical view. People write it, not the AI, so it is the same on every machine and reviewed like code.|JON-01, JAK-03
AHM-03: Alert detail page with Analyst and Home modes|type:task,phase:alpha,owner:ahmad,area:ui,critical-path|W4 Full offline report|ahmadalkhoudeir|docs/roadmap/ahmad.md#ahm-03-alert-detail-page-with-analyst-and-home-modes|Show one alert in full. Analyst mode: evidence records, controls grouped by framework (with version), ATT&CK techniques, and the AI's sentences, each followed by links to the records it cites, plus the status and assignee form. Home mode: the headline, the severity in plain words, and one action, with no jargon.|AHM-02, JON-02, JON-04
ALI-04: Run the benchmark on both tiers and propose the default models|type:task,phase:alpha,owner:ali,area:ai,critical-path,needs-hardware|W4 Full offline report|al-kheder|docs/roadmap/ali.md#ali-04-run-the-benchmark-on-both-tiers-and-propose-the-default-models|Run the benchmark on a Pi-class machine (models of 4B parameters or fewer) and on a laptop (8B or fewer), review the answers by hand, and propose one default model per tier. The choice replaces `TEMPORARY_DEFAULT_MODEL` in `maxguard/ai/ollama_client.py` and goes into the offline bundle (JON-05).|ALI-01, ALI-03
JAI-08: Ed25519 signing library|type:task,phase:alpha,owner:jaiden,area:release|W5 Alpha feature freeze|JWinborne1|docs/roadmap/jaiden.md#jai-08-ed25519-signing-library|Provide `generate_keypair`, `sign`, and `verify` with Ed25519 signatures, used by the chain-of-custody log (AMO-05) and the signed intel bundles (JAI-11).|JAI-01
AMO-04: CISA CPG 2.0 and CJIS v6.1 rows|type:task,phase:alpha,owner:amory,area:mapping|W5 Alpha feature freeze|gettalife|docs/roadmap/amory.md#amo-04-cisa-cpg-20-and-cjis-v61-rows|Fill `mappings/cisa_cpg_2_0.yaml` and `mappings/cjis_6_1.yaml` with goal and control IDs read in the official documents, so all four frameworks appear in the alpha's reports (the Week 5 milestone).|AMO-02
AHM-04: Security review of the alpha|type:task,phase:alpha,owner:ahmad,area:program|W5 Alpha feature freeze|ahmadalkhoudeir|docs/roadmap/ahmad.md#ahm-04-security-review-of-the-alpha|Before the feature freeze, walk through every threat in `docs/ARCHITECTURE.md` section 14 against the real code and record, for each, how it is defended and how you checked.|AHM-03, JON-03, AMO-03
JON-05: Offline bundle: install MaxGuard on a machine with no internet|type:task,phase:alpha,owner:jonattan,area:release,critical-path,needs-hardware|W6 Release candidate|MeliorExi|docs/roadmap/jonattan.md#jon-05-offline-bundle-install-maxguard-on-a-machine-with-no-internet|Write `scripts/build-offline-bundle.sh` and `scripts/install.sh` so a user can install MaxGuard and its AI model from a USB stick or the GitHub Release without the internet: the images, the model, the Compose file, sample data, and a checksum file, split into parts smaller than 2 GiB.|JAI-04, ALI-04
JAI-09: Release workflow and v2.0-alpha-rc1|type:task,phase:alpha,owner:jaiden,area:release,critical-path,needs-hardware|W6 Release candidate|JWinborne1|docs/roadmap/jaiden.md#jai-09-release-workflow-and-v20-alpha-rc1|Add `.github/workflows/release.yml`: when a tag `v*` is pushed, build the image for `linux/amd64` and `linux/arm64`, push it to the GitHub Container Registry, and create a GitHub Release with the small bundle files and a `SHA256SUMS` file. Then tag `v2.0-alpha-rc1` and attach the offline bundle.|JAI-04, KAR-04, JON-05
KAR-05: Release-candidate test with an outside tester|type:task,phase:alpha,owner:karthik,area:testing,area:release,critical-path|W6 Release candidate|Karthiknair91|docs/roadmap/karthik.md#kar-05-release-candidate-test-with-an-outside-tester|Run the alpha acceptance test (`docs/roadmap/README.md`) on `v2.0-alpha-rc1` yourself, then with someone outside the team, on a computer that has never run MaxGuard, and turn every problem into an issue.|JAI-09, JON-05
JAI-10: Release v2.0-alpha|type:task,phase:alpha,owner:jaiden,area:release,critical-path|W8 v2.0-alpha|JWinborne1|docs/roadmap/jaiden.md#jai-10-release-v20-alpha|Fix or defer every issue from the release-candidate test, then tag and publish `v2.0-alpha` with release notes and the offline bundle.|JAI-09, KAR-05
JAK-06: Build the reference lab and prove the mirror works|type:task,phase:alpha,owner:jakub,area:sensor,needs-hardware|W8 v2.0-alpha|SXafir-byte|docs/roadmap/jakub.md#jak-06-build-the-reference-lab-and-prove-the-mirror-works|Build the hardware lab from `docs/HARDWARE.md` — router, TL-SG105E mirror, mesh in bridge mode, Raspberry Pi 5 with a silent capture port, USB SSD, Docker, Zeek and Suricata — and run its five tests. This makes the spring live-sensor work possible and replaces every "not run — verify on hardware" in that guide with what really happened.|JAK-02
AHM-05: Alpha acceptance test and presentation|type:task,phase:alpha,owner:ahmad,area:program,critical-path|W8 v2.0-alpha|ahmadalkhoudeir|docs/roadmap/ahmad.md#ahm-05-alpha-acceptance-test-and-presentation|Run the `v2.0-alpha` acceptance test with someone who did not build the release, record each result, and give the end-of-semester presentation.|JAI-10, KAR-05
JAK-08: Device attribution: which device is behind each IP address|type:task,phase:spring,owner:jakub,area:sensor|S1-S4 Live sensor|SXafir-byte|docs/roadmap/jakub.md#jak-08-device-attribution-which-device-is-behind-each-ip-address|Join DHCP leases (MAC address and host name) and DNS questions with IP addresses, so the timeline and inventory pages can say "laptop-lab (02:00:00:aa:bb:cc)" instead of only an address.|JAK-04, KAR-02
JAK-07: Live sensor: capture, rotation, and shipping to the console|type:task,phase:spring,owner:jakub,area:sensor,critical-path,needs-hardware|S1-S4 Live sensor|SXafir-byte|docs/roadmap/jakub.md#jak-07-live-sensor-capture-rotation-and-shipping-to-the-console|Turn the lab into MaxGuard's live sensor (`docs/ARCHITECTURE.md` section 4): Zeek and Suricata run all the time on the capture port and write their logs into one folder per 15-minute interval on the SSD, and a small shipper sends each completed folder to the console's `POST /api/ingest`. The console analyzes it like an upload, with `sensor_id` set to the sensor's name.|JAK-06, JAI-07, JAK-08
AMO-05: Chain-of-custody log|type:task,phase:spring,owner:amory,area:mapping,area:release|S1-S4 Live sensor|gettalife|docs/roadmap/amory.md#amo-05-chain-of-custody-log|Write `maxguard/custody/log.py`: an append-only, tamper-evident log of what happened to evidence (capture received, report generated, report exported). Each entry holds the previous entry's hash and an Ed25519 signature, so editing, deleting, or reordering any line is detected.|JAI-08
AHM-06: IP timeline and device inventory pages|type:task,phase:spring,owner:ahmad,area:ui|S1-S4 Live sensor|ahmadalkhoudeir|docs/roadmap/ahmad.md#ahm-06-ip-timeline-and-device-inventory-pages|Add `/timeline?ip=` (everything one address did, in time order, with links to the alerts that involve it) and `/assets` (the device inventory with MAC addresses and names from device attribution).|AHM-03, JAK-08, JAI-07, JAK-07
KAR-06: End-to-end test of the live sensor on the lab|type:task,phase:spring,owner:karthik,area:testing,area:sensor,needs-hardware|S1-S4 Live sensor|Karthiknair91|docs/roadmap/karthik.md#kar-06-end-to-end-test-of-the-live-sensor-on-the-lab|Prove the live path works end to end on the reference lab: generate known traffic, and check that the expected alerts appear on the console within the shipping interval, with the right devices attributed.|JAK-07
JAK-09: JA4 watchlist rule|type:task,phase:spring,owner:jakub,area:engine,area:sensor|S5-S8 Respond|SXafir-byte|docs/roadmap/jakub.md#jak-09-ja4-watchlist-rule|Add rule `tls.ja4_watchlist`: a TLS client whose JA4 fingerprint is on MaxGuard's watchlist raises a high finding. The watchlist ships empty; entries come only from our own captures or sources whose license allows copying.|JAK-05
JAI-11: Signed offline intel bundles|type:task,phase:spring,owner:jaiden,area:release|S5-S8 Respond|JWinborne1|docs/roadmap/jaiden.md#jai-11-signed-offline-intel-bundles|Deliver rule and intel updates (Suricata rules, the JA4 watchlist, mapping updates) on a USB stick as a signed bundle that MaxGuard verifies before it unpacks anything.|JAI-08, JAK-09
AHM-07: Response: block proposals, generated rules, and preview before you block|type:task,phase:spring,owner:ahmad,area:response|S5-S8 Respond|ahmadalkhoudeir|docs/roadmap/ahmad.md#ahm-07-response-block-proposals-generated-rules-and-preview-before-you-block|Let an analyst propose blocking one IP address and see, before anything happens, the exact firewall commands (with their undo commands) and what the block would have stopped in the last 7 days (`docs/ARCHITECTURE.md` section 13).|JAI-06, JAI-07
AHM-08: Response: approvals, audit, revert, and the OPNsense connector|type:task,phase:spring,owner:ahmad,area:response,needs-hardware|S5-S8 Respond|ahmadalkhoudeir|docs/roadmap/ahmad.md#ahm-08-response-approvals-audit-revert-and-the-opnsense-connector|Add the approval workflow (propose → preview → approve with the IP typed again → applied → reverted, every step audited) and the first `Enforcer`, which applies an approved block on an OPNsense firewall through its API.|AHM-07, JON-03
JON-06: Prompt-injection tests for the AI layer|type:task,phase:spring,owner:jonattan,area:ai|S5-S8 Respond|MeliorExi|docs/roadmap/jonattan.md#jon-06-prompt-injection-tests-for-the-ai-layer|Prove, with tests, that text an attacker puts into network traffic cannot make MaxGuard's AI hide, change, or invent findings, and cannot make it cite records that do not belong to the finding; and measure how often each model obeys such text.|JON-02, ALI-03
ALI-05: Re-evaluate the models against prompt injection and the spring rules|type:task,phase:spring,owner:ali,area:ai,needs-hardware|S5-S8 Respond|al-kheder|docs/roadmap/ali.md#ali-05-re-evaluate-the-models-against-prompt-injection-and-the-spring-rules|Run the evaluation again on both tiers with Jonattan's prompt-injection set and the spring rules (JA4 watchlist, decoys, baselines), and confirm or change the default models before the v2.0 feature freeze.|ALI-04, JON-06
FIO-06: Decoys: fake services on their own IP address|type:task,phase:spring,owner:fiona,area:engine,needs-hardware|S9-S11 Detect more|flau0306|docs/roadmap/fiona.md#fio-06-decoys-fake-services-on-their-own-ip-address|Add decoys (canaries): fake Telnet, FTP and printer web services on their own IP address that nothing legitimate should ever contact, plus rule `decoy.contact`, which turns any contact into a critical finding.|JAI-07, JON-04
FIO-07: Per-device baselines|type:task,phase:spring,owner:fiona,area:engine|S9-S11 Detect more|flau0306|docs/roadmap/fiona.md#fio-07-per-device-baselines|Learn what each device normally does (the services and ports it uses) during a learning period, then raise `baseline.new_service` when a device uses something new, without breaking the rule that the same logs always give the same findings.|JAI-06, JAK-08
JAK-10: NetFlow and IPFIX input|type:task,phase:spring,owner:jakub,area:sensor,contract-change,needs-hardware|S9-S11 Detect more|SXafir-byte|docs/roadmap/jakub.md#jak-10-netflow-and-ipfix-input|Let a router that exports NetFlow v5/v9 or IPFIX feed MaxGuard: a collector container writes flow records, and `NetflowAdapter` (Contract 3) turns them into `conn.log`-shaped JSON records, so the normalizer, the timeline, and the flow-based checks work unchanged (payload rules simply find nothing).|JAI-07, JAI-03, AHM-06
JAK-11: Host agent for one computer|type:task,phase:spring,owner:jakub,area:sensor,needs-hardware|S12 v2.0 feature freeze|SXafir-byte|docs/roadmap/jakub.md#jak-11-host-agent-for-one-computer|For a home with no mirror port: a small agent on one computer captures that computer's own traffic with the operating system's built-in tools, in rotating files, and uploads each finished file to the console's `POST /api/ingest`.|JAI-07
JAI-12: Release v2.0-rc1 and v2.0|type:task,phase:spring,owner:jaiden,area:release,critical-path|S13 v2.0 release candidate|JWinborne1|docs/roadmap/jaiden.md#jai-12-release-v20-rc1-and-v20|Tag `v2.0-rc1` for an outside tester (April 30, 2027), fix what they find, and release `v2.0` (May 7, 2027) with the sensor image and the offline bundle.|JAI-11, JAK-07, AHM-08
AHM-09: v2.0 acceptance test|type:task,phase:spring,owner:ahmad,area:program,critical-path|S14 v2.0|ahmadalkhoudeir|docs/roadmap/ahmad.md#ahm-09-v20-acceptance-test|Run the `v2.0` acceptance test: the alpha test plus the live sensor on the reference lab, a blocked IP with preview and approval, a verified intel bundle, and the chain-of-custody check.|JAI-12
ISSUES

echo "done: $created issue(s) to create or created, $skipped already existed"
