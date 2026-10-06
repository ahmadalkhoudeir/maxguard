"""Fiona's tasks: Zeek runner, adapters, TLS and certificate rules, ATT&CK, CLI, decoys, baselines."""

from plan_helpers import checklist, pr_step, start_step

IMAGE_NOTE = (
    "Recorded by running the same command inside `zeek/zeek:9.0.0` with MaxGuard's Python "
    "packages added, because building the image needs Debian's package servers, which the "
    "planning environment could not reach. That image has no Suricata, so only Zeek ran; the "
    "real image runs both and must report the same one finding."
)

TASKS = [
    {
        "id": "FIO-01", "owner": "fiona", "milestone": "W1",
        "title": "Zeek runner and the two input adapters",
        "labels": ["area:engine", "critical-path"],
        "depends": ["JAI-02", "KAR-02"],
        "goal": (
            "Write the code that turns what a user gives MaxGuard into a folder of Zeek logs: "
            "`run_zeek()` runs Zeek 9.0.0 on a capture, `PcapAdapter` accepts `.pcap`/`.pcapng` "
            "files, and `ZeekLogAdapter` accepts a folder, `.zip` or `.tar.gz` of logs that "
            "someone already has, including the old tab-separated (TSV) format. Both adapters "
            "follow Contract 3 (`maxguard/adapters/base.py`)."
        ),
        "prereq": "JAI-02 (contracts) and KAR-02 (fixtures) are merged.",
        "steps": [
            start_step("fiona/zeek-runner-adapters"),
            "Create an **empty** file `maxguard/zeek/__init__.py`, then the runner "
            "`maxguard/zeek/runner.py`:\n\n@@FILE maxguard/zeek/runner.py@@\n\n"
            "`-D` makes Zeek's connection IDs (`uid`) the same on every run, and the "
            "Community ID script adds the `community_id` that Suricata also writes. "
            "`docs/ARCHITECTURE.md` section 7 explains why both matter. The runner loads "
            "`site.zeek` (JAK-01) where Zeek's documentation would say `local`.",
            "Create `tests/unit/test_zeek_site.py`. It fails if any MaxGuard `.zeek` file loads "
            "`local` or a script that makes DNS lookups, and checks that the runner passes "
            "`site.zeek` to Zeek:\n\n@@FILE tests/unit/test_zeek_site.py@@",
            "Create `maxguard/adapters/pcap.py`:\n\n@@FILE maxguard/adapters/pcap.py@@\n\n"
            "It decides by the file's first four bytes (its *magic number*), not by its name, "
            "so a renamed text file is refused. JAK-05 adds Suricata to it in Week 4.",
            "Create `maxguard/adapters/zeeklogs.py`:\n\n@@FILE maxguard/adapters/zeeklogs.py@@\n\n"
            "The long part is the TSV conversion: Zeek's older text format puts the type of "
            "every column in a `#types` header line, and `_convert` uses it so that numbers "
            "become numbers and sets become lists, exactly as in Zeek's JSON output.",
            "Create the tests `tests/unit/test_adapters.py`:\n\n@@FILE tests/unit/test_adapters.py@@",
            "Run them:\n\n@@RUN tests@@",
            "See the TSV conversion work on a hand-made fixture:\n\n@@RUN try@@",
            pr_step("feat: Zeek runner, PcapAdapter and ZeekLogAdapter (FIO-01)", "JWinborne1"),
        ],
        "files": [
            "maxguard/zeek/__init__.py", "maxguard/zeek/runner.py",
            ("maxguard/adapters/pcap.py", "snip:pcap_v1.py"), "maxguard/adapters/zeeklogs.py",
            "tests/unit/test_adapters.py", "tests/unit/test_zeek_site.py",
        ],
        "commands": [
            {"id": "tests", "show": "pytest tests/unit/test_adapters.py tests/unit/test_zeek_site.py -q"},
            {"id": "try", "show": (
                "python -c \"import json, tempfile; from pathlib import Path; "
                "from maxguard.adapters.zeeklogs import ZeekLogAdapter; "
                "out = ZeekLogAdapter().to_zeek_logs(Path('tests/fixtures/zeek/_handmade/tsv_plain_http'), "
                "Path(tempfile.mkdtemp())); "
                "print(sorted(p.name for p in out.iterdir())); "
                "rec = json.loads((out / 'conn.log').read_text().splitlines()[0]); "
                "print({k: rec[k] for k in ('ts', 'id.orig_h', 'id.resp_p', 'proto', 'service')})\"")},
        ],
        "test": (
            "`pytest` passes. In the one-liner's output, `ts` and `id.resp_p` are numbers, not "
            "strings in quotes: that is the TSV conversion working. No test here needs Zeek; "
            "KAR-03's integration tests run the real `run_zeek()` inside the engine image."
        ),
        "why": (
            "Contract 3 means the rest of MaxGuard never cares where logs came from: a capture, an "
            "imported folder, and later the live sensor and NetFlow all end up as one folder of "
            "Zeek JSON logs. The TSV fix matters because a set such as `cert_chain_fps` used to stay "
            "one long string, and every certificate rule then silently found nothing — a bug that "
            "only shows up with real Zeek output, which is why the tests use real fixtures. The "
            "archive checks (`ArchiveTooLarge`) stop a small zip that unpacks to terabytes from "
            "filling the disk."
        ),
        "checklist": checklist(extra=[
            "`pcap.py` does not call Suricata yet (that is JAK-05)",
        ]),
    },
    {
        "id": "FIO-02", "owner": "fiona", "milestone": "W1",
        "title": "TLS and certificate rules",
        "labels": ["area:engine", "critical-path"],
        "depends": ["FIO-01", "KAR-02"],
        "goal": (
            "Write six detection rules — outdated TLS version, weak cipher, expired, self-signed, "
            "weak-key, and SHA-1-signed certificates — each with a positive test (its capture "
            "triggers it) and a negative test (a capture that *almost* matches does not). Also add "
            "the tests that prove imported TSV logs find the same problems and that findings are "
            "identical on every run."
        ),
        "prereq": "FIO-01 is merged.",
        "steps": [
            start_step("fiona/tls-cert-rules"),
            "Create `maxguard/rules/tls.py`:\n\n@@FILE maxguard/rules/tls.py@@",
            "Create `maxguard/rules/certs.py`:\n\n@@FILE maxguard/rules/certs.py@@\n\n"
            "Zeek 9's `x509.log` has no IP addresses. A certificate is linked to its TLS session "
            "through `ssl.log`'s `cert_chain_fps`, whose first entry is the server's own (leaf) "
            "certificate; `_leaf_certs` does that join.",
            "Register the two modules: replace the contents of `maxguard/rules/__init__.py` with\n\n"
            "@@FILE maxguard/rules/__init__.py@@\n\n(JAK-03 adds `cleartext` to this line.)",
            "Create the rule tests `tests/unit/test_rules_tls_certs.py`:\n\n"
            "@@FILE tests/unit/test_rules_tls_certs.py@@",
            "Now that certificate rules exist, add the import tests "
            "`tests/unit/test_zeeklogs_import.py`:\n\n@@FILE tests/unit/test_zeeklogs_import.py@@\n\n"
            "and the merge and determinism tests `tests/unit/test_merge_determinism.py`:\n\n"
            "@@FILE tests/unit/test_merge_determinism.py@@",
            "Run them:\n\n@@RUN tests@@",
            "Run all registered rules on one fixture folder, the way the pipeline will:\n\n@@RUN try@@",
            pr_step("feat: TLS and certificate rules with tests (FIO-02)", "JWinborne1"),
        ],
        "files": [
            "maxguard/rules/tls.py", "maxguard/rules/certs.py",
            ("maxguard/rules/__init__.py", "snip:rules_init_v1.py"),
            "tests/unit/test_rules_tls_certs.py", "tests/unit/test_zeeklogs_import.py",
            "tests/unit/test_merge_determinism.py",
        ],
        "commands": [
            {"id": "tests", "show": ("pytest tests/unit/test_rules_tls_certs.py "
                                     "tests/unit/test_zeeklogs_import.py "
                                     "tests/unit/test_merge_determinism.py -q")},
            {"id": "try", "show": (
                "python -c \"from pathlib import Path; import maxguard.rules; "
                "from maxguard.rules.base import run_all; "
                "[print(f.rule_id, f.severity, f.dst_ip, f.dst_port, f.title, f.evidence[0].record_id) "
                "for f in run_all(Path('tests/fixtures/zeek/cert_expired'))]\"")},
        ],
        "test": (
            "All three files pass. The one-liner prints exactly one finding, `cert.expired`, with "
            "the record ID of the `ssl.log` line that is its evidence. Run it twice: the record ID "
            "does not change."
        ),
        "why": (
            "Each lab capture contains exactly one weakness, so a positive test shows the rule "
            "fires and the negative \"near miss\" test shows it does not fire on something that "
            "only looks similar (a strong cipher, a valid certificate). Without the negative tests a "
            "rule that fires on everything would pass. `merge()` collapses many identical findings "
            "into one with a count, and keeps at most five evidence records, so a busy network "
            "gives one alert instead of thousands. Severities are part of the Security Lead's "
            "review, so Ahmad signs off on this pull request too."
        ),
        "checklist": checklist(extra=[
            "Every rule has a positive and a negative test",
            "Ahmad approved the severities",
        ]),
    },
    {
        "id": "FIO-03", "owner": "fiona", "milestone": "W2",
        "title": "MITRE ATT&CK mapping file",
        "labels": ["area:mapping", "critical-path"],
        "depends": ["AMO-01", "JAK-03"],
        "goal": (
            "Add `mappings/attack.yaml`: for each rule, the ATT&CK technique an attacker would use "
            "against the weakness it finds (for example a cleartext password is collected with "
            "T1040 Network Sniffing). The loader puts these rows into `Finding.attack`, separate "
            "from the compliance controls."
        ),
        "prereq": "AMO-01 (mapping file checks) and JAK-03 (all 13 rules registered) are merged.",
        "steps": [
            start_step("fiona/attack-mapping"),
            "Create `mappings/attack.yaml`:\n\n@@FILE mappings/attack.yaml@@\n\n"
            "Every row was checked against MITRE's own release file for Enterprise ATT&CK v19.2 "
            "(the `source` link). Before every release, check the index in the header for a newer "
            "v19 point release and update `version` if there is one.",
            "Run the mapping checks (they now include this file):\n\n@@RUN tests@@",
            "See the techniques the loader adds to the Telnet finding:\n\n@@RUN try@@",
            pr_step("feat: MITRE ATT&CK v19.2 mapping file (FIO-03)", "ahmadalkhoudeir"),
        ],
        "files": ["mappings/attack.yaml"],
        "commands": [
            {"id": "tests", "show": "pytest tests/unit/test_mappings.py -q"},
            {"id": "try", "show": (
                "python -c \"from pathlib import Path; import maxguard.rules; "
                "from maxguard.rules.base import run_all; "
                "from maxguard.mapping.loader import apply, load_all; "
                "findings = apply(run_all(Path('tests/fixtures/zeek/telnet')), load_all(Path('mappings'))); "
                "[print(t.technique_id, t.name, '-', t.tactic) for t in findings[0].attack]\"")},
        ],
        "test": "`test_mappings.py` passes for all five files, and the one-liner prints T1040 "
                "for the Telnet finding.",
        "why": (
            "Compliance controls say *which rule of a framework* a weakness breaks; ATT&CK says "
            "*how an attacker would use it*. Analysts think in ATT&CK, and the timeline page groups "
            "events by technique. Reusing the Contract 2 file format (plus a `tactic` key) means "
            "the same loader and the same checks work for both. In ATT&CK v19, Defense Evasion was "
            "split into two tactics, which is why the version is pinned and checked "
            "(CLAUDE.md rule 8)."
        ),
        "checklist": checklist(extra=[
            "Every row has `verified` naming the release file it was checked in",
            "Ahmad reviewed the rows (compliance accuracy)",
        ]),
    },
    {
        "id": "FIO-04", "owner": "fiona", "milestone": "W2",
        "title": "The maxguard command, first version (JSON reports)",
        "labels": ["area:engine", "critical-path"],
        "depends": ["JAI-05", "FIO-03"],
        "goal": (
            "Give MaxGuard its command line: `maxguard analyze INPUT` runs the pipeline and writes "
            "a JSON report, with `--no-ai`, `-o FILE`, and `--frameworks`. Exit codes tell scripts "
            "what happened (0 ok, 2 bad input, 3 Zeek failed). This is the command shown at the "
            "Week 2 demo."
        ),
        "prereq": "JAI-05 (pipeline) and FIO-03 (ATT&CK file) are merged.",
        "steps": [
            start_step("fiona/cli"),
            "Create `cli/main.py`:\n\n@@FILE cli/main.py@@\n\n"
            "`pyproject.toml` (JAI-01) already declares the `maxguard` command as `cli.main:main`, "
            "so after this file exists the command works in your virtual environment.",
            "Create the tests `tests/unit/test_cli.py`:\n\n@@FILE tests/unit/test_cli.py@@",
            "Run them:\n\n@@RUN tests@@",
            "Analyze a fixture log folder (no Zeek needed) and look at the start of the report:\n\n"
            "@@RUN try@@",
            "**The Week 2 demo command.** A capture needs Zeek, so it runs inside the engine "
            "image from JAI-04 (build it first with "
            "`docker build -f docker/Dockerfile -t maxguard:dev .`):\n\n@@RUN demo@@",
            pr_step("feat: maxguard analyze command with JSON output (FIO-04)", "JWinborne1"),
        ],
        "files": [("cli/main.py", "snip:cli_main_v1.py"),
                  ("tests/unit/test_cli.py", "snip:test_cli_v1.py")],
        "commands": [
            {"id": "tests", "show": "pytest tests/unit/test_cli.py -q"},
            {"id": "try", "show": "maxguard analyze tests/fixtures/zeek/telnet --no-ai | head -n 12",
             "run": "python -m cli.main analyze tests/fixtures/zeek/telnet --no-ai | head -n 12"},
            {"id": "demo", "env": "zeek",
             "show": ("docker run --rm --network none -v \"$PWD/tests/pcaps:/pcaps:ro\" maxguard:dev "
                      "maxguard analyze /pcaps/telnet.pcap --no-ai -o /tmp/r.json && echo ok"),
             "run": ("python3 -m cli.main analyze tests/pcaps/telnet.pcap --no-ai -o /tmp/r.json "
                     "&& echo ok"),
             "note": IMAGE_NOTE},
        ],
        "test": (
            "`pytest` passes; the report starts with `\"ai\"` because keys are sorted; the demo "
            "prints `maxguard: 1 finding(s), report written to /tmp/r.json` and `ok`."
        ),
        "why": (
            "The CLI is the thinnest possible layer: it checks the input, calls `analyze()`, and "
            "writes the result. All the real work stays in the pipeline, so the dashboard (JAI-07) "
            "gives exactly the same report. Status messages go to stderr and the report to stdout, "
            "so `maxguard analyze x > report.json` stays valid JSON. Zeek's logs are written to a "
            "temporary folder that is deleted afterwards, so no copy of the user's traffic is left "
            "on disk."
        ),
        "checklist": checklist(extra=[
            "`maxguard analyze tests/fixtures/zeek/telnet --no-ai` works in your venv",
            "The demo command works in the engine image",
        ]),
    },
    {
        "id": "FIO-05", "owner": "fiona", "milestone": "W4",
        "title": "CLI: CSV and HTML reports, and --offline",
        "labels": ["area:engine"],
        "depends": ["FIO-04", "AMO-03", "JON-03"],
        "goal": (
            "Finish the CLI for the alpha: `--format` (json, csv, or html) uses Amory's report exporters "
            "(AMO-03), and `--offline` turns on Jonattan's offline guard (JON-03) before anything "
            "else runs, so nothing in the analysis can reach the network."
        ),
        "prereq": "AMO-03 (report export) and JON-03 (offline guard) are merged.",
        "steps": [
            start_step("fiona/cli-formats-offline"),
            "Replace `cli/main.py` with the final version:\n\n@@FILE cli/main.py@@\n\n"
            "The JSON output is byte-for-byte the same as before: `report.to_json` uses the same "
            "settings as the first version's `to_json`.",
            "Replace `tests/unit/test_cli.py`:\n\n@@FILE tests/unit/test_cli.py@@",
            "Run them:\n\n@@RUN tests@@",
            "Try the CSV format:\n\n@@RUN try@@",
            pr_step("feat: CLI --format csv/html and --offline (FIO-05)", "JWinborne1"),
        ],
        "files": ["cli/main.py", "tests/unit/test_cli.py"],
        "commands": [
            {"id": "tests", "show": "pytest tests/unit/test_cli.py -q"},
            {"id": "try", "show": ("maxguard analyze tests/fixtures/zeek/telnet --no-ai --format csv "
                                   "| head -n 3 | cut -c1-150"),
             "run": ("python -m cli.main analyze tests/fixtures/zeek/telnet --no-ai --format csv "
                     "| head -n 3 | cut -c1-150")},
        ],
        "test": "`pytest` passes, including the test that proves the guard is switched on "
                "*before* the analysis starts.",
        "why": (
            "Order matters for `--offline`: a guard switched on after the analysis started could "
            "miss a connection made during it. The test records the order of the calls to prove "
            "it. The exporters are imported only when needed, so a bug in the HTML exporter can "
            "never stop an analysis from running."
        ),
        "checklist": checklist(),
    },
    {
        "id": "FIO-06", "owner": "fiona", "milestone": "S11",
        "title": "Decoys: fake services on their own IP address",
        "labels": ["area:engine"], "hardware": True,
        "depends": ["JAI-07", "JON-04"],
        "goal": (
            "Add decoys (canaries): fake Telnet, FTP and printer web services on their own IP "
            "address that nothing legitimate should ever contact, plus rule `decoy.contact`, which "
            "turns any contact into a critical finding."
        ),
        "prereq": "JAI-07 is merged. The new rule ID needs the Security Lead's approval: ask Ahmad "
                  "in the issue first.",
        "steps": [
            start_step("fiona/decoys"),
            "Create `maxguard/decoy/__init__.py` and the decoy itself, "
            "`maxguard/decoy/service.py`:\n\n@@FILE maxguard/decoy/__init__.py@@\n\n"
            "@@FILE maxguard/decoy/service.py@@\n\n"
            "Telnet and FTP send their banner first (those servers speak first); HTTP waits "
            "for the request and answers with a page titled \"Printer admin\". Every connection "
            "writes one JSON line to `decoy.log` in a `finally` block, so garbage, silence or an "
            "early hang-up is still logged: the contact itself is the evidence. It reads at "
            "most 1024 bytes, keeps the first 64 as hex, and waits at most 5 seconds. The "
            "decoy only answers; it never opens a connection (CLAUDE.md rule 5).",
            "Create `maxguard/decoy/__main__.py`, so `python -m maxguard.decoy` starts it with "
            "settings from environment variables:\n\n@@FILE maxguard/decoy/__main__.py@@",
            "Create the rule `maxguard/rules/decoy.py`. Do **not** add it to "
            "`maxguard/rules/__init__.py` until Ahmad approves the rule ID; importing the "
            "module registers it, which is how the tests use it. Its Home text and mapping rows "
            "come from Jonattan and Amory:\n\n@@FILE maxguard/rules/decoy.py@@",
            "Create the tests `tests/unit/test_decoy.py`. \"Never connects out\" is tested by "
            "wrapping `socket.socket.connect`: after a client talks to the decoy, the only "
            "connection in the process is the test's own:\n\n@@FILE tests/unit/test_decoy.py@@\n\n"
            "Run them:\n\n@@RUN tests@@",
            "Create `docker/decoy-compose.yaml`. `macvlan` gives the decoy its own MAC and IP "
            "address on your LAN; the parent must be the console's normal wired network card, "
            "never the sensor's capture port:\n\n@@FILE docker/decoy-compose.yaml@@\n\n"
            "Check it. The three addresses have no defaults on purpose (a default could clash "
            "with a real device), so the second command fails with a clear message:\n\n"
            "@@RUN compose@@",
            "Prove the decoy in Docker. `macvlan` needs a real network card on a real LAN, so "
            "this uses a private bridge network with the same hardening as the Compose file "
            "(a non-root user, read-only, all capabilities dropped). A second container plays "
            "the intruder, then the rule reads the copied `decoy.log`:\n\n@@RUN proof@@\n\n"
            "In planning, a packet capture in the decoy's network namespace during these "
            "connections showed only SYN-ACK answers from the decoy: no connection it started "
            "and no DNS lookup.",
            "**On the lab** (*not run — verify on hardware*): put the three addresses in "
            "`docker/.env`, start the decoy with "
            "`docker compose -f docker/decoy-compose.yaml up -d`, and connect to its address "
            "from a laptop (Docker's macvlan driver does not let the host itself reach its own "
            "macvlan containers). Check whether your network card accepts several MAC "
            "addresses; Wi-Fi cards often do not. Getting `decoy.log` into the console's "
            "analysis is still open (see `docs/ARCHITECTURE.md` section 5).",
            pr_step("feat: decoys and the decoy.contact rule (FIO-06)", "JWinborne1"),
        ],
        "files": ["maxguard/decoy/__init__.py", "maxguard/decoy/service.py",
                  "maxguard/decoy/__main__.py", "maxguard/rules/decoy.py",
                  "tests/unit/test_decoy.py", "docker/decoy-compose.yaml"],
        "commands": [
            {"id": "tests", "show": "pytest tests/unit/test_decoy.py -q"},
            {"id": "compose", "expect_code": 1, "show": (
                "MAXGUARD_DECOY_SUBNET=192.0.2.0/24 MAXGUARD_DECOY_GATEWAY=192.0.2.1 "
                "MAXGUARD_DECOY_IP=192.0.2.250 \\\n"
                "  docker compose -f docker/decoy-compose.yaml config --format json | python -c "
                "\"import json, sys; c = json.load(sys.stdin); n = c['networks']['decoy-lan']; "
                "s = c['services']['decoy']; print(n['driver'], n['driver_opts']['parent'], "
                "s['networks']['decoy-lan']['ipv4_address'], s['read_only'], s['cap_drop'])\"\n"
                "docker compose -f docker/decoy-compose.yaml config --quiet"),
             "note": ("Documentation addresses (`192.0.2.0/24`) are used here; yours are free "
                      "addresses on your own LAN.")},
            {"id": "proof", "show": (
                "mkdir -p data/decoy-test data/decoy-logs && chmod 777 data/decoy-test\n"
                "docker network create maxguard-decoy-test > /dev/null\n"
                "docker run -d --rm --name maxguard-decoy-test --network maxguard-decoy-test \\\n"
                "  --user 10001:10001 --read-only --cap-drop ALL "
                "--security-opt no-new-privileges:true \\\n"
                "  --sysctl net.ipv4.ip_unprivileged_port_start=0 \\\n"
                "  -e PYTHONDONTWRITEBYTECODE=1 -e PYTHONPATH=/src "
                "-e MAXGUARD_DECOY_LOG=/data/decoy.log -e MAXGUARD_DECOY_TIMEOUT=2 \\\n"
                "  -v \"$PWD/maxguard:/src/maxguard:ro\" -v \"$PWD/data/decoy-test:/data\" \\\n"
                "  python:3.11-slim-bookworm python -m maxguard.decoy > /dev/null\n"
                "for i in $(seq 1 40); do docker logs maxguard-decoy-test 2>&1 | grep -q telnet "
                "&& break; sleep 0.5; done\n"
                "docker logs maxguard-decoy-test\n"
                "docker run --rm --network maxguard-decoy-test nicolaka/netshoot:v0.15 sh -c '\n"
                "  printf \"root\\r\\n\" | nc -w 3 maxguard-decoy-test 23; echo\n"
                "  printf \"USER admin\\r\\n\" | nc -w 3 maxguard-decoy-test 21\n"
                "  curl -s -m 5 http://maxguard-decoy-test/ | head -c 60; echo'\n"
                "docker rm -f maxguard-decoy-test > /dev/null && docker network rm "
                "maxguard-decoy-test > /dev/null\n"
                "cp data/decoy-test/decoy.log data/decoy-logs/decoy.log\n"
                "python -c \"\n"
                "from pathlib import Path\n"
                "from maxguard.rules.base import merge\n"
                "from maxguard.rules.decoy import decoy_contact\n"
                "for f in merge(decoy_contact(Path('data/decoy-logs'))):\n"
                "    print(f.severity, f.rule_id, f.src_ip, '->', f.dst_ip, f.dst_port, f.protocol)\""),
             "note": ("The addresses come from Docker's private network, so yours may differ. "
                      "`chmod 777` lets the container's non-root user (10001) write the log "
                      "into the folder.")},
        ],
        "test": "The tests pass, and on the lab a connection from a laptop to the decoy's address "
                "appears as a critical alert.",
        "why": (
            "Nobody has a reason to log in to a printer that does not exist, so any contact is "
            "almost certainly someone exploring the network: one of the most reliable signals a "
            "small network can get, with almost no false positives. Its own IP address keeps the "
            "decoy separate from the passive sensor."
        ),
        "checklist": checklist(extra=["The decoy never opens a connection",
                                      "Ahmad approved `decoy.contact`"]),
    },
    {
        "id": "FIO-07", "owner": "fiona", "milestone": "S11",
        "title": "Per-device baselines",
        "labels": ["area:engine"],
        "depends": ["JAI-06", "JAK-08"],
        "goal": (
            "Learn what each device normally does (the services and ports it uses) during a "
            "learning period, then raise `baseline.new_service` when a device uses something new, "
            "without breaking the rule that the same logs always give the same findings."
        ),
        "prereq": "JAI-06 (events) and JAK-08 (devices) are merged. The new rule ID needs the "
                  "Security Lead's approval.",
        "steps": [
            start_step("fiona/baselines"),
            "Create `maxguard/rules/baseline.py`:\n\n@@FILE maxguard/rules/baseline.py@@\n\n"
            "Three parts. `build_baseline(events)` turns the learning period's events into "
            "`{ip: {\"peers\": n, \"services\": [[port, proto, service], ...]}}`, sorted and "
            "ready for `json.dumps`. `STATEFUL_RULES` and `@stateful_rule` are a second "
            "registry for rules that need history; `run_all()` and Contract 3 do not change "
            "(`docs/ARCHITECTURE.md` section 5). The rule `baseline.new_service` gets the "
            "baseline and the end of the learning period through `context` and never reads the "
            "clock or a file, so the same logs and the same context always give the same "
            "findings. Choices that cut false positives: only `conn` events count (http, ssl "
            "and eve records describe the same connections again); `ftp-data` is ignored (its "
            "port changes on every transfer); an event whose service Zeek could not tell is "
            "known when the device already used that port and protocol; a device with no "
            "baseline is skipped (the device inventory shows new devices). A *device* is the "
            "address that **starts** a connection, so this finds new services a device "
            "**uses**.",
            "Create the tests `tests/unit/test_baseline.py`:\n\n"
            "@@FILE tests/unit/test_baseline.py@@\n\nRun them:\n\n@@RUN tests@@",
            "Nothing calls `run_stateful()` yet: where the baseline is stored and when the "
            "learning period ends is an open decision (`docs/ARCHITECTURE.md` section 5). "
            "Propose it in GitHub Discussions with Jaiden.",
            pr_step("feat: per-device baselines and baseline.new_service (FIO-07)", "JWinborne1"),
        ],
        "files": ["maxguard/rules/baseline.py", "tests/unit/test_baseline.py"],
        "commands": [
            {"id": "tests", "show": "pytest tests/unit/test_baseline.py -q"},
        ],
        "test": "The tests pass, including one that builds the baseline twice and compares.",
        "why": (
            "Small networks are predictable: a printer prints, a camera streams. A device that "
            "suddenly uses a new service is worth a look. Passing the baseline in explicitly "
            "keeps the rule deterministic: given the same logs and the same baseline it always "
            "gives the same answer (CLAUDE.md rule 2)."
        ),
        "checklist": checklist(extra=["Ahmad approved `baseline.new_service`"]),
    },
]
