"""Jakub's tasks: Zeek scripts, Suricata, cleartext rules, inventory, live sensor, NetFlow, agent."""

from plan_helpers import checklist, pr_step, start_step

JAK10_PROOF = (
                "mkdir -p data/netflow data/netflow-done\n"
                "export MAXGUARD_NETFLOW_ADDRESS=127.0.0.1 MAXGUARD_NETFLOW_DATA=\"$PWD/data/netflow\"\n"
                "export MAXGUARD_UID=$(id -u) MAXGUARD_GID=$(id -g)\n"
                "NF=\"docker compose -p maxguard-netflow-test -f docker/netflow-compose.yaml\"\n"
                "$NF up -d 2> /dev/null\n"
                "for i in $(seq 1 40); do $NF logs goflow2 | grep -q 'starting collection' && break; "
                "sleep 0.5; done\n"
                "python scripts/send_test_flows.py 127.0.0.1\n"
                "for i in $(seq 1 40); do [ \"$(wc -l < data/netflow/goflow2.json)\" -ge 7 ] && break; "
                "sleep 0.5; done\n"
                "echo \"flows written: $(wc -l < data/netflow/goflow2.json)\"\n"
                "mv data/netflow/goflow2.json data/netflow-done/2026-10-06-1400.json\n"
                "$NF kill -s HUP goflow2 2> /dev/null\n"
                "for i in $(seq 1 20); do [ -f data/netflow/goflow2.json ] && break; sleep 0.5; done\n"
                "ls data/netflow\n"
                "$NF down 2> /dev/null\n"
                "maxguard analyze data/netflow-done --no-ai -o data/netflow-report.json\n"
                "python - <<'EOF'\n"
                "import json\n"
                "from pathlib import Path\n"
                "from maxguard.adapters.netflow import NetflowAdapter\n"
                "from maxguard.events.normalize import normalize\n"
                "\n"
                "report = json.loads(Path(\"data/netflow-report.json\").read_text())\n"
                "print(\"findings:\", len(report[\"findings\"]), \"| zeek and suricata ran:\", report[\"tools\"])\n"
                "logs = NetflowAdapter().to_zeek_logs(Path(\"data/netflow-done\"), Path(\"data/netflow-work\"))\n"
                "for e in normalize(logs, \"router\"):\n"
                "    print(e[\"source\"], e[\"uid\"], e[\"src_ip\"], e[\"src_port\"], \"->\", e[\"dst_ip\"], "
                "e[\"dst_port\"], e[\"summary\"])\n"
                "EOF")


JAK11_UPLOAD = (
                "mkdir -p data/agent/spool\n"
                "cp tests/pcaps/telnet.pcap data/agent/spool/capture-20261006-140000.pcap\n"
                "T=$(python -c \"import secrets; print(secrets.token_urlsafe(32))\")\n"
                "cat > data/agent/agent.toml <<EOF\n"
                "console_url = \"http://127.0.0.1:8001\"\n"
                "token = \"$T\"\n"
                "spool_dir = \"data/agent/spool\"\n"
                "sensor_id = \"laptop\"\n"
                "capture_user = \"nobody\"\n"
                "EOF\n"
                "chmod 600 data/agent/agent.toml\n"
                "MAXGUARD_INGEST_TOKEN=$T MAXGUARD_DATA_DIR=data/console \\\n"
                "  uvicorn --factory maxguard.api.app:create_ingest_app --host 127.0.0.1 --port 8001 "
                "> data/agent/console.log 2>&1 & U=$!\n"
                "for i in $(seq 1 50); do python -c \"import socket; "
                "socket.create_connection(('127.0.0.1', 8001), 1)\" 2> /dev/null && break; "
                "sleep 0.2; done\n"
                "python -m maxguard.sensor.agent --config data/agent/agent.toml --upload-only\n"
                "ls data/agent/spool/uploaded\n"
                "grep -o '\"POST /api/ingest HTTP/1.1\" [0-9]* [A-Za-z]*' data/agent/console.log\n"
                "python -c \"from maxguard.storage.events import EventStore; "
                "e = EventStore('data/console/events').query(ip='172.18.0.3', since=0); "
                "print(len(e), 'event(s) from sensor', sorted({x['sensor_id'] for x in e}))\"\n"
                "kill $U")


TASKS = [
    {
        "id": "JAK-01", "owner": "jakub", "milestone": "W1",
        "title": "MaxGuard's Zeek scripts: cleartext sessions and asset tracking",
        "labels": ["area:engine", "critical-path"],
        "depends": ["JAI-01", "KAR-01"],
        "goal": (
            "Write the two Zeek scripts MaxGuard loads on every run. `cleartext.zeek` writes "
            "`maxguard_cleartext.log`, one line per real Telnet, POP3 or IMAP session that was not "
            "upgraded to TLS. `inventory.zeek` turns on Zeek's host, service and software tracking "
            "for every address, which the asset inventory (JAK-04) reads. `site.zeek` replaces "
            "Zeek's own `local` policy, without the scripts that make DNS lookups."
        ),
        "prereq": "JAI-01 and KAR-01 (the lab captures) are merged.",
        "steps": [
            start_step("jakub/zeek-scripts"),
            "Create `maxguard/zeek/scripts/cleartext.zeek`:\n\n@@FILE maxguard/zeek/scripts/cleartext.zeek@@\n\n"
            "Two details matter. `c$resp$size == 0` skips connections where the server never sent "
            "anything (a port scan is not a session). And Zeek stores analyzer names in upper case "
            "(`SSL`), so the STARTTLS check compares lower-case text; without `to_lower` an IMAP "
            "session upgraded to TLS would be reported as cleartext.",
            "Create `maxguard/zeek/scripts/inventory.zeek`:\n\n@@FILE maxguard/zeek/scripts/inventory.zeek@@",
            "Create `maxguard/zeek/site.zeek`, MaxGuard's site policy. It is outside "
            "`scripts/` on purpose: everything in `scripts/` is loaded on every run, and this file "
            "replaces the `local` argument instead:\n\n@@FILE maxguard/zeek/site.zeek@@\n\n"
            "Zeek's own `local` policy is fine on an analyst's laptop that is meant to be online, "
            "but MaxGuard must never contact anything (CLAUDE.md rule 1), and Zeek runs as its own "
            "program, so MaxGuard's Python offline guard cannot stop its DNS queries. This was found "
            "while building the live sensor in planning.",
            "Run Zeek on the Telnet capture with your script (the Zeek image has everything; "
            "`--network none` proves it needs no network):\n\n@@RUN telnet@@",
            "Run it on the clean TLS 1.3 capture: there must be **no** cleartext log, and the "
            "inventory logs must appear:\n\n@@RUN clean@@",
            "Compare the scripts that `site.zeek` and Zeek's `local` load: `loaded_scripts.log` "
            "names every script, and the first count must be 0:\n\n@@RUN lookups@@",
            pr_step("feat: Zeek scripts for cleartext sessions and asset tracking (JAK-01)",
                    "flau0306"),
        ],
        "files": ["maxguard/zeek/scripts/cleartext.zeek", "maxguard/zeek/scripts/inventory.zeek",
                  "maxguard/zeek/site.zeek"],
        "commands": [
            {"id": "telnet", "show": (
                "docker run --rm --network none -v \"$PWD:/src:ro\" -w /tmp zeek/zeek:9.0.0 sh -c "
                "\"zeek -D -C -r /src/tests/pcaps/telnet.pcap /src/maxguard/zeek/site.zeek LogAscii::use_json=T "
                "/src/maxguard/zeek/scripts/cleartext.zeek && cat maxguard_cleartext.log\"")},
            {"id": "clean", "show": (
                "docker run --rm --network none -v \"$PWD:/src:ro\" -w /tmp zeek/zeek:9.0.0 sh -c "
                "\"zeek -D -C -r /src/tests/pcaps/clean_tls13.pcap /src/maxguard/zeek/site.zeek LogAscii::use_json=T "
                "/src/maxguard/zeek/scripts/*.zeek && ls *.log\"")},
            {"id": "lookups", "show": (
                "docker run --rm --network none -v \"$PWD:/src:ro\" -w /tmp zeek/zeek:9.0.0 sh -c "
                "\"zeek -D -C -r /src/tests/pcaps/plain_http.pcap /src/maxguard/zeek/site.zeek; "
                "grep -c 'detect-MHR\\|interesting-hostnames\\|extend-email' loaded_scripts.log; "
                "rm -f *.log; zeek -D -C -r /src/tests/pcaps/plain_http.pcap local; "
                "grep -c 'detect-MHR\\|interesting-hostnames\\|extend-email' loaded_scripts.log\"")},
        ],
        "test": (
            "The Telnet run prints one JSON line with `\"proto\":\"telnet\"`. The clean run lists "
            "`known_hosts.log` and `known_services.log` but no `maxguard_cleartext.log`. The "
            "lookups check prints `0` for `site.zeek` and `3` for `local`. KAR-02 "
            "then bakes both scripts into the test fixtures."
        ),
        "why": (
            "Zeek already logs FTP and HTTP in detail, but it has no Telnet log, and its POP3/IMAP "
            "support does not say clearly whether a session stayed unencrypted. A small script that "
            "watches the port and the analyzers gives one clear line per cleartext session, with "
            "the connection `uid` that links it to `conn.log`. By default Zeek tracks known hosts "
            "only inside its `Site::local_nets` list, which is empty in a container, so without "
            "`ALL_HOSTS` the inventory would always be empty. And a sensor that quietly asks an "
            "outside DNS service about the files people download would break the promise MaxGuard "
            "makes in every report: your data never leaves this computer."
        ),
        "checklist": checklist(extra=["Both commands above give the expected output"]),
    },
    {
        "id": "JAK-02", "owner": "jakub", "milestone": "W1",
        "title": "Suricata configuration: Community ID and JA4",
        "labels": ["area:engine", "critical-path"],
        "depends": ["KAR-01"],
        "goal": (
            "Add MaxGuard's Suricata settings for reading captures: `eve.json` with flow, alert, "
            "DNS, HTTP, TLS (with the JA4 client fingerprint) and DHCP events, and the same "
            "Community ID that Zeek writes. Add the (empty) MaxGuard rules file that signed "
            "intel bundles fill later."
        ),
        "prereq": "KAR-01 (the lab captures) is merged.",
        "steps": [
            start_step("jakub/suricata-config"),
            "Create `maxguard/suricata/maxguard-suricata.yaml`:\n\n"
            "@@FILE maxguard/suricata/maxguard-suricata.yaml@@\n\n"
            "Suricata fills in its defaults for everything not listed. JA4 needs two switches: "
            "`app-layer.protocols.tls.ja4-fingerprints: yes` computes it, and `ja4: on` under "
            "the `tls` event type writes it.",
            "Create an **empty** file `maxguard/suricata/__init__.py` (it makes the folder part "
            "of the Python package, so `pip install` ships the YAML file), then "
            "`maxguard/suricata/rules/maxguard.rules`:\n\n@@FILE maxguard/suricata/rules/maxguard.rules@@",
            "Run Suricata 7.0.10 (the version in the engine image) on the weak-TLS capture and "
            "pull out the two fields MaxGuard needs:\n\n@@RUN suricata@@",
            "Compare with Zeek's Community ID for the same connection (it must be identical):\n\n"
            "@@RUN zeek@@",
            pr_step("feat: Suricata config with Community ID and JA4 (JAK-02)", "flau0306"),
        ],
        "files": ["maxguard/suricata/__init__.py", "maxguard/suricata/maxguard-suricata.yaml",
                  "maxguard/suricata/rules/maxguard.rules"],
        "commands": [
            {"id": "suricata", "show": (
                "docker run --rm --network none -v \"$PWD:/src:ro\" --entrypoint sh "
                "jasonish/suricata:7.0.10 -c \"suricata -c /src/maxguard/suricata/maxguard-suricata.yaml "
                "-r /src/tests/pcaps/tls_weak_version.pcap -l /tmp -k none --runmode single "
                "-S /src/maxguard/suricata/rules/maxguard.rules > /dev/null && grep '\\\"event_type\\\":\\\"tls\\\"' "
                "/tmp/eve.json | grep -o '\\\"community_id\\\":\\\"[^\\\"]*\\\"\\|\\\"ja4\\\":\\\"[^\\\"]*\\\"'\"")},
            {"id": "zeek", "show": (
                "docker run --rm --network none -v \"$PWD:/src:ro\" -w /tmp zeek/zeek:9.0.0 sh -c "
                "\"zeek -D -C -r /src/tests/pcaps/tls_weak_version.pcap LogAscii::use_json=T "
                "policy/protocols/conn/community-id-logging && grep -o '\\\"community_id\\\":\\\"[^\\\"]*\\\"' conn.log\"")},
        ],
        "test": (
            "Suricata prints a `community_id` and a `ja4` value starting with `t10` (TLS 1.0, the "
            "weak version in this capture); Zeek prints the same `community_id`."
        ),
        "why": (
            "Zeek and Suricata see the same traffic but describe it differently. The Community ID "
            "is a hash of the connection's addresses, ports and protocol that both tools compute "
            "the same way, so the normalizer (JAI-03) can show a Zeek event and a Suricata event "
            "about one connection side by side. JA4 identifies the TLS client software from its "
            "first message, even when everything after it is encrypted; MaxGuard uses only JA4 "
            "from the JA4+ family because only JA4 is BSD-licensed (CLAUDE.md rule 7). Suricata's "
            "own `flow_id` is random on every run, which is why MaxGuard never uses it."
        ),
        "checklist": checklist(extra=["Both commands print the same Community ID"]),
    },
    {
        "id": "JAK-03", "owner": "jakub", "milestone": "W1",
        "title": "Cleartext and RDP rules (the rule set is complete)",
        "labels": ["area:engine", "critical-path"],
        "depends": ["FIO-02", "JAK-01", "KAR-02"],
        "goal": (
            "Write the seven remaining Fall 2026 rules: FTP, Telnet, HTTP, HTTP on port 8080, POP3 "
            "and IMAP in cleartext, and RDP with only \"standard RDP security\". With them, all 13 "
            "rules are registered and every lab capture triggers exactly its own rule."
        ),
        "prereq": "FIO-02 (it creates the rule package layout), JAK-01 and KAR-02 are merged.",
        "steps": [
            start_step("jakub/cleartext-rules"),
            "Create `maxguard/rules/cleartext.py`:\n\n@@FILE maxguard/rules/cleartext.py@@",
            "Register it: replace the contents of `maxguard/rules/__init__.py` with\n\n"
            "@@FILE maxguard/rules/__init__.py@@",
            "Create the rule tests `tests/unit/test_rules_cleartext.py`:\n\n"
            "@@FILE tests/unit/test_rules_cleartext.py@@\n\n"
            "and the whole-rule-set test `tests/unit/test_rule_registry.py`:\n\n"
            "@@FILE tests/unit/test_rule_registry.py@@",
            "Run them:\n\n@@RUN tests@@",
            "Run every rule on every lab fixture and count the findings:\n\n@@RUN try@@",
            pr_step("feat: cleartext and RDP rules, all 13 rules registered (JAK-03)", "flau0306"),
        ],
        "files": ["maxguard/rules/cleartext.py", ("maxguard/rules/__init__.py", "snip:rules_init_jak03.py"),
                  "tests/unit/test_rules_cleartext.py", "tests/unit/test_rule_registry.py"],
        "commands": [
            {"id": "tests", "show": "pytest tests/unit/test_rules_cleartext.py tests/unit/test_rule_registry.py -q"},
            {"id": "try", "show": (
                "python -c \"from pathlib import Path; import maxguard.rules; "
                "from maxguard.rules.base import RULES, run_all; print(len(RULES), 'rules'); "
                "[print(d.name, [f.rule_id for f in run_all(d)]) "
                "for d in sorted(Path('tests/fixtures/zeek').iterdir()) if not d.name.startswith('_')]\"")},
        ],
        "test": "Both files pass; the one-liner prints `13 rules`, then one rule per capture and an "
                "empty list for `clean_tls13` and `dns_lookup`.",
        "why": (
            "Splitting the rules by file (`tls.py`, `certs.py`, `cleartext.py`) lets two people "
            "write rules in the same week without editing the same file. The registry test is the "
            "safety net for the whole set: it fails if a rule is forgotten in `__init__.py`, if a "
            "capture starts triggering a second rule, or if a clean capture triggers anything. "
            "HTTP on 8080 is its own rule because the same weakness on an \"admin\" port usually "
            "means a device's management page."
        ),
        "checklist": checklist(extra=["Ahmad approved the severities"]),
    },
    {
        "id": "JAK-04", "owner": "jakub", "milestone": "W1",
        "title": "Asset inventory",
        "labels": ["area:engine"],
        "depends": ["JAK-03", "KAR-02"],
        "goal": (
            "Write `maxguard/inventory.py`: one row per IP address seen in the logs, with when it "
            "was first seen, the services it offered (`80/http`), the software named in its "
            "traffic, and how many findings involve it. The pipeline adds this list to every "
            "report, and the device inventory page shows it."
        ),
        "prereq": "JAK-03 and KAR-02 are merged.",
        "steps": [
            start_step("jakub/inventory"),
            "Create `maxguard/inventory.py`:\n\n@@FILE maxguard/inventory.py@@",
            "Create the tests `tests/unit/test_inventory.py`:\n\n@@FILE tests/unit/test_inventory.py@@",
            "Run them:\n\n@@RUN tests@@",
            "Build the inventory for the plain-HTTP fixture:\n\n@@RUN try@@",
            pr_step("feat: asset inventory from Zeek's known-hosts, services and software logs (JAK-04)",
                    "flau0306"),
        ],
        "files": ["maxguard/inventory.py", "tests/unit/test_inventory.py"],
        "commands": [
            {"id": "tests", "show": "pytest tests/unit/test_inventory.py -q"},
            {"id": "try", "show": (
                "python -c \"import json; from pathlib import Path; import maxguard.rules; "
                "from maxguard.inventory import build; from maxguard.rules.base import run_all; "
                "d = Path('tests/fixtures/zeek/plain_http'); "
                "[print(json.dumps(a)) for a in build(d, run_all(d))]\"")},
        ],
        "test": "`pytest` passes, and the one-liner prints the lab server with `80/http` and "
                "Python's web server software, and the client with one finding.",
        "why": (
            "An alert says \"172.18.0.2 offers Telnet\"; the inventory answers \"what is "
            "172.18.0.2?\". Sorting IPs by their numeric value (`ip_sort_key`) keeps `.10` after "
            "`.2`, and never reading the clock keeps the list identical on every run. Later the "
            "live sensor adds MAC addresses and host names to the same rows (JAK-07)."
        ),
        "checklist": checklist(),
    },
    {
        "id": "JAK-05", "owner": "jakub", "milestone": "W4",
        "title": "Suricata in the pipeline",
        "labels": ["area:engine"],
        "depends": ["JAK-02", "FIO-01", "JAI-05", "JAI-07"],
        "goal": (
            "When Suricata is installed (it is, in the engine image), run it next to Zeek on every "
            "capture so `eve.json` lands in the same log folder. The normalizer already reads it, "
            "so Suricata's events and JA4 fingerprints appear in the report and the event store. "
            "On a laptop without Suricata nothing changes."
        ),
        "prereq": "JAK-02, FIO-01, JAI-05 and JAI-07 (the API) are merged.",
        "steps": [
            start_step("jakub/suricata-pipeline"),
            "Create `maxguard/suricata/runner.py`:\n\n@@FILE maxguard/suricata/runner.py@@",
            "Replace `maxguard/adapters/pcap.py` with the version that calls it:\n\n"
            "@@FILE maxguard/adapters/pcap.py@@",
            "A Suricata failure must reach the dashboard like a Zeek failure: as HTTP 422 with "
            "the error message. In `maxguard/api/app.py` (JAI-07), import the new error next to "
            "`ZeekError` and catch both in `run_pipeline()`:\n\n"
            "```python\n"
            "from maxguard.suricata.runner import SuricataError\n"
            "...\n"
            "        except (ZeekError, SuricataError) as err:\n"
            "            raise HTTPException(422, str(err)) from None\n"
            "```\n\n"
            "Ask Jaiden to review this part: the API is his module.",
            "Create the tests `tests/unit/test_suricata_runner.py`. They put a tiny fake "
            "`suricata` program on the `PATH`, so they run without the real one:\n\n"
            "@@FILE tests/unit/test_suricata_runner.py@@",
            "Run them, then the whole unit suite:\n\n@@RUN tests@@\n\n@@RUN all@@",
            "Add the integration test that proves Suricata now runs next to Zeek, "
            "`tests/integration/test_suricata_pipeline.py`. Where Suricata is missing it shows "
            "as skipped, with the reason, instead of passing:\n\n"
            "@@FILE tests/integration/test_suricata_pipeline.py@@\n\n@@RUN integration@@",
            "The real check runs in the engine image, where Suricata is installed:\n\n@@RUN image@@",
            pr_step("feat: run Suricata next to Zeek on captures (JAK-05)", "flau0306"),
        ],
        "files": ["maxguard/suricata/runner.py", "maxguard/adapters/pcap.py",
                  "maxguard/api/app.py", "tests/unit/test_suricata_runner.py",
                  "tests/integration/test_suricata_pipeline.py"],
        "commands": [
            {"id": "tests", "show": "pytest tests/unit/test_suricata_runner.py -q"},
            {"id": "all", "show": 'pytest -m "not integration" -q'},
            {"id": "integration", "env": "zeek",
             "show": ("docker build -f docker/Dockerfile --target test -t maxguard:test .\n"
                      "docker run --rm --network none maxguard:test "
                      "pytest -m integration tests/integration/test_suricata_pipeline.py -q -rs"),
             "run": ("python3 -m pytest -m integration tests/integration/test_suricata_pipeline.py "
                     "-q -rs -p no:cacheprovider"),
             "note": ("In planning this ran in `zeek/zeek:9.0.0`, which has no Suricata, so it was "
                      "skipped as shown. With Zeek and Suricata both available it passed: the "
                      "Suricata TLS event had a JA4 and the same Community ID as Zeek's. In the "
                      "engine image you should see `1 passed`.")},
            {"id": "image", "env": "none",
             "show": ("docker run --rm --network none -v \"$PWD/tests/pcaps:/pcaps:ro\" maxguard:dev "
                      "python -c \"import json, tempfile; from pathlib import Path; "
                      "from maxguard.pipeline import analyze; "
                      "r = analyze(Path('/pcaps/tls_weak_version.pcap'), Path(tempfile.mkdtemp()), explain=False); "
                      "print(r['tools']); print(sorted({e['source'] for e in r['events']})); "
                      "print([e['ja4'] for e in r['events'] if e['ja4']])\""),
             "output": ("{'zeek': True, 'suricata': True}\n['suricata', 'zeek']\n"
                        "['t10d230600_44099cda8a52_242d16716555']"),
             "note": ("Not run in planning: the engine image needs Debian's package servers to build. "
                      "The expected output is what the same pipeline gives on this capture's fixture "
                      "(its JA4 came from Suricata 7.0.10 with MaxGuard's settings).")},
        ],
        "test": (
            "The unit tests pass without Suricata installed. In the image, `tools` lists both Zeek "
            "and Suricata, events come from both `zeek` and `suricata`, and the TLS client hello "
            "has a JA4 fingerprint."
        ),
        "why": (
            "Zeek and Suricata are good at different things: Zeek describes every connection, "
            "Suricata matches signatures and computes JA4. Running both on the same capture costs "
            "a few seconds and gives the analyst both views, joined by Community ID. Making "
            "Suricata optional keeps the unit tests fast on any laptop, while the report's `tools` "
            "section says honestly which tools ran."
        ),
        "checklist": checklist(extra=["The image check lists events from both tools"]),
    },
    {
        "id": "JAK-06", "owner": "jakub", "milestone": "W8",
        "title": "Build the reference lab and prove the mirror works",
        "labels": ["area:sensor"], "hardware": True, "status": "process",
        "depends": ["JAK-02"],
        "goal": (
            "Build the hardware lab from `docs/HARDWARE.md` — router, TL-SG105E mirror, mesh in "
            "bridge mode, Raspberry Pi 5 with a silent capture port, USB SSD, Docker, Zeek and "
            "Suricata — and run its five tests. This makes the spring live-sensor work possible "
            "and replaces every \"not run — verify on hardware\" in that guide with what really "
            "happened."
        ),
        "prereq": (
            "The parts in `docs/HARDWARE.md` section 2 have arrived (ask Ahmad). If they arrive "
            "after December 4, do this task in the first spring week."
        ),
        "steps": [
            start_step("jakub/lab-build"),
            "Follow `docs/HARDWARE.md` sections 3 to 11 in order. Keep a text file of every command "
            "you ran and its output (no real addresses or MAC addresses: replace them with the "
            "guide's example addresses before committing).",
            "Run the five tests in section 12 and fill in the throughput table of test 4.",
            "Edit `docs/HARDWARE.md`: for each step you ran, replace \"not run — verify on hardware\" "
            "with \"verified on <date>\" and fix every menu name, output, or command that was "
            "different on the real devices. Fill in section 11.3 with the Suricata command that "
            "worked.",
            pr_step("docs: verify HARDWARE.md on the reference lab (JAK-06)", "flau0306"),
        ],
        "files": [], "commands": [],
        "test": (
            "Test 1 prints `PASS: both directions are reaching the sensor.`, test 5 prints `FAIL` "
            "with mirroring off and `PASS` again after turning it back on, and stage 5 of test 4 "
            "shows loss (if it shows none, the measurement is wrong)."
        ),
        "why": (
            "Everything in the hardware guide was checked against manuals, not devices, so some "
            "details will be wrong. Running it once, carefully, and fixing the guide is what makes "
            "it safe for the next student. The throughput table tells users honestly how much "
            "traffic a Pi sensor can watch."
        ),
        "checklist": checklist(extra=[
            "No real IP addresses, MAC addresses, Wi-Fi names or passwords in the pull request",
            "Test 4's table is filled in",
        ]),
    },
    {
        "id": "JAK-07", "owner": "jakub", "milestone": "S4",
        "title": "Live sensor: capture, rotation, and shipping to the console",
        "labels": ["area:sensor", "critical-path"], "hardware": True,
        "depends": ["JAK-06", "JAI-07", "JAK-08"],
        "goal": (
            "Turn the lab into MaxGuard's live sensor (`docs/ARCHITECTURE.md` section 4): Zeek and "
            "Suricata run all the time on the capture port and write their logs into one folder "
            "per 15-minute interval on the SSD, and a small shipper sends each completed folder "
            "to the console's `POST /api/ingest`. The console analyzes it like an upload, with "
            "`sensor_id` set to the sensor's name."
        ),
        "prereq": ("JAK-06 (the lab works), JAI-07 (the API with `/api/ingest`) and JAK-08 "
                   "(which creates `maxguard/sensor/`) are merged."),
        "steps": [
            start_step("jakub/live-sensor"),
            "**Zeek rotation.** Zeek 9 rotates its own logs, without `zeekctl`, when "
            "`Log::default_rotation_interval` is set. `Log::rotation_format_func` decides where "
            "each closed file goes. Create `maxguard/zeek/scripts/live/rotate.zeek`:\n\n"
            "@@FILE maxguard/zeek/scripts/live/rotate.zeek@@\n\n"
            "The folder is named after the interval's **start** in UTC, and the files keep their "
            "plain names, so a finished folder is an ordinary Zeek log folder. The script sits in "
            "`scripts/live/` on purpose: `maxguard/zeek/runner.py` loads only `scripts/*.zeek`, so "
            "analyzing a capture file never rotates anything.",
            "**Suricata live settings.** Create `maxguard/suricata/maxguard-suricata-live.yaml`, "
            "a copy of `maxguard-suricata.yaml` with three changes (Community ID and JA4 are "
            "unchanged):\n\n@@FILE maxguard/suricata/maxguard-suricata-live.yaml@@\n\n"
            "Why a file per **minute** and not per 15 minutes: Suricata 8.0's `rotate-interval` "
            "accepts `minute`, `hour` and `day`, which start at the next whole minute, hour or "
            "day, or a relative value such as `15m`, which counts from the moment Suricata "
            "started (user guide, \"Rotate log file\"; source: `src/util-logopenfile.c`). A "
            "relative 15 minutes would not line up with Zeek's folders, so Suricata writes "
            "minute files and the adapter merges each interval's minutes into that interval's "
            "folder. Never add `copy-mode` to the `af-packet` section: it turns Suricata into an "
            "inline device that sends packets (CLAUDE.md rule 5).",
            "**Compose file.** Create `docker/sensor-compose.yaml`:\n\n"
            "@@FILE docker/sensor-compose.yaml@@\n\n"
            "Zeek runs **without `-D`**: random seeds protect a live sensor's tables against "
            "deliberate slow-down attacks. Every service drops all capabilities and adds back "
            "only what it needs. Suricata needs five more than `NET_ADMIN`, `NET_RAW` and "
            "`SYS_NICE` only while it starts: the image's start script hands its folders (such as `/var/log/suricata`) "
            "to the `suricata` user, and Suricata then switches to that user. The shipper uses "
            "the `zeek/zeek` image only for its Python 3: it needs nothing outside the standard "
            "library. Check the file:\n\n@@RUN compose@@",
            "**Adapter.** Create `maxguard/adapters/live.py` with `LiveSensorAdapter` "
            "(Contract 3, unchanged):\n\n@@FILE maxguard/adapters/live.py@@\n\n"
            "A folder is *complete* two minutes after its interval ends: by then Zeek has moved "
            "every log into it and Suricata has closed the last minute file that belongs to it. "
            "`merge_eve()` writes `eve.json` under a hidden name first and renames it, so a crash "
            "halfway never leaves a half-merged file. The adapter reads "
            "`MAXGUARD_INTERVAL_MINUTES` only when it analyzes a folder, because "
            "`pipeline.py` creates it when it is imported, and a wrong setting must not stop "
            "MaxGuard from analyzing uploads.",
            "Add it to `ADAPTERS` in `maxguard/pipeline.py` (two lines change):\n\n"
            "@@FILE maxguard/pipeline.py@@",
            "Add one line to the docstring of `maxguard/sensor/__init__.py`:\n\n"
            "@@FILE maxguard/sensor/__init__.py@@",
            "**Shipper.** Create `maxguard/sensor/shipper.py`:\n\n"
            "@@FILE maxguard/sensor/shipper.py@@\n\n"
            "Three choices to notice. It marks a folder shipped only after a `2xx` answer and "
            "stops at the first failure, so a console that is down only delays folders. It packs "
            "the same folder into the same bytes every time, so if the sensor crashes between "
            "sending and marking, the console sees the same SHA-256 and does not count the "
            "alerts twice. And it never uses a proxy: the token and the logs go straight to the "
            "console the user configured.",
            "**Tests.** Create `tests/unit/test_live_adapter.py`:\n\n"
            "@@FILE tests/unit/test_live_adapter.py@@\n\n"
            "and `tests/unit/test_shipper.py` (a fake console: `http.server` in a thread on "
            "`127.0.0.1`):\n\n@@FILE tests/unit/test_shipper.py@@\n\nRun them:\n\n@@RUN tests@@",
            "**The console side.** The dashboard listens only on `127.0.0.1`, so nobody on the "
            "network can read alerts or approve a block. Sensors get their own door: a second "
            "container that serves nothing but `POST /api/ingest` on port 8001 of the console's "
            "LAN address (`create_ingest_app()` from JAI-07). Create `docker/compose.lan.yaml`:"
            "\n\n@@FILE docker/compose.lan.yaml@@\n\n"
            "Check both Compose files (the values here are examples; yours go in `docker/.env`, "
            "which `.gitignore` already keeps out of git):\n\n@@RUN lan@@",
            "On the console machine (address `192.168.50.20` in the lab), make a token, then "
            "create `docker/.env` with your editor (for example `nano docker/.env`):\n\n"
            "```bash\npython3 -c \"import secrets; print(secrets.token_urlsafe(32))\"\n```\n\n"
            "```text\n"
            "MAXGUARD_LAN_ADDRESS=192.168.50.20\n"
            "MAXGUARD_INGEST_TOKEN=<paste the token here>\n"
            "```\n\n"
            "Make it readable only by you and start MaxGuard with both files:\n\n"
            "```bash\n"
            "chmod 600 docker/.env\n"
            "docker compose -f docker/compose.yaml -f docker/compose.lan.yaml up -d\n"
            "```\n\n"
            "Docker Compose reads `docker/.env` by itself because it sits next to the first "
            "Compose file.",
            "Then, on the sensor, put the console's ingest address and the same token in "
            "`/data/shipper.toml` (never in the repository) and make it readable only by root:"
            "\n\n"
            "```toml\n"
            "console_url = \"http://192.168.50.20:8001\"   # the console's LAN address, port 8001\n"
            "token = \"<MAXGUARD_INGEST_TOKEN from docker/.env on the console>\"\n"
            "sensor_id = \"sensor-01\"\n"
            "```\n\n"
            "```bash\nsudo chmod 600 /data/shipper.toml\n```",
            "Try the whole path on the Pi with 1-minute folders first. The test traffic must "
            "cross switch port 1, the only port the sensor watches (`docs/HARDWARE.md` section "
            "1): run the lab service (`docker run -d --rm --name lab-service -p 23:23 -p 8080:8080 "
            "lab-server`) on a machine plugged into a LAN port of the router, and connect to it "
            "from a device on the mesh Wi-Fi. Stop it afterwards (`docker stop lab-service`): it "
            "is insecure on purpose.\n\n@@RUN lab@@",
            "Then start it for real (15-minute folders), run the sensor on the lab for one day, "
            "and check that alerts appear on the console within about 20 minutes of the "
            "traffic: `docker compose -f docker/sensor-compose.yaml up -d`.",
            pr_step("feat: live sensor with rotation and shipping (JAK-07)", "flau0306"),
        ],
        "files": ["maxguard/zeek/scripts/live/rotate.zeek",
                  "maxguard/suricata/maxguard-suricata-live.yaml", "docker/sensor-compose.yaml",
                  "maxguard/adapters/live.py", ("maxguard/pipeline.py", "snip:pipeline_v3.py"),
                  "maxguard/sensor/__init__.py", "maxguard/sensor/shipper.py",
                  "tests/unit/test_live_adapter.py", "tests/unit/test_shipper.py",
                  "docker/compose.lan.yaml"],
        "commands": [
            {"id": "compose", "show": ("docker compose -f docker/sensor-compose.yaml config --quiet "
                                       "&& echo \"compose file OK\"")},
            {"id": "tests",
             "show": "pytest tests/unit/test_live_adapter.py tests/unit/test_shipper.py -q"},
            {"id": "lan", "expect_code": 1, "show": (
                "MAXGUARD_LAN_ADDRESS=192.168.50.20 MAXGUARD_INGEST_TOKEN=example-token-of-32-characters-or-more \\\n"
                "  docker compose -f docker/compose.yaml -f docker/compose.lan.yaml config "
                "--format json | python3 -c \"import json, sys; "
                "s = json.load(sys.stdin)['services']['maxguard-ingest']; "
                "print(s['command'][1], s['ports'][0]['host_ip'], s['ports'][0]['published'])\"\n"
                "docker compose -f docker/compose.yaml -f docker/compose.lan.yaml config --quiet"),
             "note": ("The first command shows the ingest app published only on the LAN "
                      "address, port 8001. The second fails on purpose (exit code 1): without "
                      "the two settings, Compose refuses to start the ingest container.")},
            {"id": "lab", "env": "none", "show": '# On the sensor: 1-minute folders for this test only\nexport MAXGUARD_INTERVAL_MINUTES=1\ndocker compose -f docker/sensor-compose.yaml up -d\n# use the lab service\'s HTTP (port 8080) and Telnet from a lab machine, wait 4 minutes\nls /data/zeek\nls -A /data/zeek/2026-10-06-2103\ndocker compose -f docker/sensor-compose.yaml ps --format \'{{.Service}} {{.State}}\'\ndocker compose -f docker/sensor-compose.yaml logs --no-log-prefix shipper\n# On the console:\ncurl -s http://127.0.0.1:8000/api/alerts | python3 -c "import json, sys; [print(a[\'rule_id\'], a[\'severity\'], a[\'count\']) for a in json.load(sys.stdin)]"\ncurl -s \'http://127.0.0.1:8000/api/events?limit=1\' | python3 -c "import json, sys; e = json.load(sys.stdin)[0]; print(e[\'sensor_id\'], e[\'source\'], e[\'log\'])"\n# Back on the sensor: stop the test\ndocker compose -f docker/sensor-compose.yaml down && unset MAXGUARD_INTERVAL_MINUTES', "output": '2026-10-06-2102\n2026-10-06-2103\n2026-10-06-2104\n2026-10-06-2105\n.shipped\ncapture_loss.log\nconn.log\neve.json\nfiles.log\nhttp.log\nknown_hosts.log\nknown_services.log\nmaxguard_cleartext.log\nsoftware.log\nshipper running\nsuricata running\nzeek running\n2026-10-06 21:02:35,859 INFO shipping complete 1-minute folders from /data/zeek\n2026-10-06 21:05:36,159 INFO 2026-10-06-2102: shipped (5066 bytes, HTTP 200)\n2026-10-06 21:06:36,274 INFO 2026-10-06-2103: shipped (2612 bytes, HTTP 200)\n2026-10-06 21:07:36,351 INFO 2026-10-06-2104: shipped (2218 bytes, HTTP 200)\ncleartext.telnet high 5\ncleartext.http_alt medium 6\nlab-sensor-01 zeek conn.log',
             "note": 'Not run on a Raspberry Pi: verify on hardware. This output is from planning, where Zeek and Suricata listened inside a lab-server container\'s network namespace instead of on `eth0` (a two-line Compose override), the console ran on the same machine, and `shipper.toml` named `sensor_id = "lab-sensor-01"`. The first Telnet session was at 21:03:09 and its alert reached the console at 21:06:36: the 21:03 folder is complete at 21:06:00 (end of the interval plus two minutes), and the shipper checks once a minute. With 15-minute folders, expect up to about 18 minutes plus the analysis time. Your folder names are your own times.'},
        ],
        "test": (
            "Both test files pass on your laptop. On the lab, `ls /data/zeek` shows a new folder "
            "every 15 minutes, `docker compose -f docker/sensor-compose.yaml ps` shows all three "
            "containers running after a reboot, and the console's alert queue shows the lab "
            "phone's traffic with the sensor's `sensor_id`. The capture port still has no IP "
            "address (`ip -br addr show eth0`)."
        ),
        "why": (
            "Shipping completed folders instead of streaming keeps the design simple: the console "
            "already knows how to analyze a folder of logs, and a network hiccup only delays a "
            "folder instead of losing events. A 15-minute interval is the trade-off between how "
            "quickly an alert appears and how many small Parquet files the console has to manage "
            "(each one costs about 3 KB). The sensor never transmits on the capture port; the "
            "shipper uses only the management port (CLAUDE.md rule 5)."
        ),
        "checklist": checklist(extra=[
            "Zeek runs without `-D`",
            "The token and console address are read from `/data`, not from the repository",
            "One full day of live data reached the console",
        ]),
    },
    {
        "id": "JAK-08", "owner": "jakub", "milestone": "S4",
        "title": "Device attribution: which device is behind each IP address",
        "labels": ["area:sensor"],
        "depends": ["JAK-04", "KAR-02"],
        "goal": (
            "Join DHCP leases (MAC address and host name) and DNS questions with IP addresses, so "
            "the timeline and inventory pages can say \"laptop-lab (02:00:00:aa:bb:cc)\" instead "
            "of only an address."
        ),
        "prereq": "JAK-04 and KAR-02 are merged.",
        "steps": [
            start_step("jakub/attribution"),
            "Create `maxguard/sensor/__init__.py`:\n\n@@FILE maxguard/sensor/__init__.py@@\n\n"
            "and `maxguard/sensor/attribution.py`:\n\n@@FILE maxguard/sensor/attribution.py@@",
            "Create the tests `tests/unit/test_attribution.py`:\n\n@@FILE tests/unit/test_attribution.py@@",
            "Run them:\n\n@@RUN tests@@",
            "Build the device table for the hand-made DNS and DHCP fixture:\n\n@@RUN try@@",
            pr_step("feat: device attribution from DHCP and DNS logs (JAK-08)", "flau0306"),
        ],
        "files": [("maxguard/sensor/__init__.py", "snip:sensor_init_v1.py"),
                  "maxguard/sensor/attribution.py",
                  "tests/unit/test_attribution.py"],
        "commands": [
            {"id": "tests", "show": "pytest tests/unit/test_attribution.py -q"},
            {"id": "try", "show": (
                "python -c \"import json; from pathlib import Path; "
                "from maxguard.sensor.attribution import build_device_table; "
                "[print(json.dumps(d)) for d in build_device_table(Path('tests/fixtures/zeek/_handmade/dns_dhcp'))]\"")},
        ],
        "test": "`pytest` passes and the one-liner prints the lab laptop with its MAC address, "
                "host name, and the name it looked up.",
        "why": (
            "IP addresses change when DHCP leases expire, and phones use random Wi-Fi MAC "
            "addresses, so an IP alone does not identify a device for long. DHCP is the one "
            "moment a device announces its MAC address and often its name; that is why the "
            "hardware guide makes sure DHCP crosses the mirrored port. Attribution only reads "
            "logs and never asks the network, so it stays passive."
        ),
        "checklist": checklist(),
    },
    {
        "id": "JAK-09", "owner": "jakub", "milestone": "S8",
        "title": "JA4 watchlist rule",
        "labels": ["area:engine", "area:sensor"],
        "depends": ["JAK-05"],
        "goal": (
            "Add rule `tls.ja4_watchlist`: a TLS client whose JA4 fingerprint is on MaxGuard's "
            "watchlist raises a high finding. The watchlist ships empty; entries come only from "
            "our own captures or sources whose license allows copying."
        ),
        "prereq": "JAK-05 (Suricata in the pipeline) is merged. The new rule ID needs the "
                  "Security Lead's approval: ask Ahmad in the issue before you start.",
        "steps": [
            start_step("jakub/ja4-watchlist"),
            "Create `maxguard/intel/__init__.py`:\n\n@@FILE maxguard/intel/__init__.py@@\n\n"
            "and the empty watchlist `maxguard/intel/ja4_watchlist.yaml`:\n\n"
            "@@FILE maxguard/intel/ja4_watchlist.yaml@@",
            "Create the rule `maxguard/rules/ja4.py`:\n\n@@FILE maxguard/rules/ja4.py@@",
            "Register it: replace the contents of `maxguard/rules/__init__.py` with\n\n"
            "@@FILE maxguard/rules/__init__.py@@",
            "Create the tests `tests/unit/test_ja4_rule.py`:\n\n@@FILE tests/unit/test_ja4_rule.py@@",
            "Run them, then the whole unit suite (the registry test must still pass):\n\n"
            "@@RUN tests@@\n\n@@RUN all@@",
            "Add the rule's Home text (Jonattan reviews it) and ask Amory and Fiona whether a "
            "mapping row or ATT&CK row fits; add them in the same pull request if so.",
            pr_step("feat: tls.ja4_watchlist rule with an empty watchlist (JAK-09)", "flau0306"),
        ],
        "files": ["maxguard/intel/__init__.py", "maxguard/intel/ja4_watchlist.yaml",
                  "maxguard/rules/ja4.py", ("maxguard/rules/__init__.py", "snip:rules_init_v2.py"),
                  "tests/unit/test_ja4_rule.py"],
        "commands": [
            {"id": "tests", "show": "pytest tests/unit/test_ja4_rule.py -q"},
            {"id": "all", "show": 'pytest -m "not integration" -q'},
        ],
        "test": "Both commands pass. With the empty watchlist the rule finds nothing on any "
                "capture; the tests add a fingerprint to a temporary watchlist to prove it fires.",
        "why": (
            "A fingerprint list is only as trustworthy as its source, and copying a third-party "
            "database with an unknown license into a public repository is not allowed. Shipping "
            "the list empty and requiring a `source` for every entry keeps the rule honest. JA4 "
            "comes from Suricata, the only JA4+ method MaxGuard may use (CLAUDE.md rule 7)."
        ),
        "checklist": checklist(extra=["Ahmad approved the new rule ID in the issue"]),
    },
    {
        "id": "JAK-10", "owner": "jakub", "milestone": "S11",
        "title": "NetFlow and IPFIX input",
        "labels": ["area:sensor", "contract-change"], "hardware": True,
        "depends": ["JAI-07", "JAI-03", "AHM-06"],
        "goal": (
            "Let a router that exports NetFlow v5/v9 or IPFIX feed MaxGuard: a collector "
            "container writes flow records, and `NetflowAdapter` (Contract 3) turns them into "
            "`conn.log`-shaped JSON records, so the normalizer, the timeline, and the "
            "flow-based checks work unchanged (payload rules simply find nothing)."
        ),
        "prereq": ("JAI-07 is merged. This task adds a `source` value to the event schema, a "
                   "contract change: the pull request needs Jaiden's review and Ahmad's approval."),
        "steps": [
            start_step("jakub/netflow"),
            "The collector is `netsampler/goflow2` (BSD-3-Clause, already in "
            "`docs/DEPENDENCIES.md`). Pin the version **and** the digest: on Docker Hub the tag "
            "`latest` still points at the old v1.3.8, not v2. Check the newest tag with "
            "`git ls-remote --tags https://github.com/netsampler/goflow2` (on October 8, 2026 it "
            "was `v2.2.7`, published for `linux/amd64` and `linux/arm64`). Create "
            "`docker/netflow-compose.yaml`:\n\n@@FILE docker/netflow-compose.yaml@@\n\n"
            "It listens on UDP 2055 of the address you give it, writes one JSON line per flow, "
            "runs as a normal user with a read-only file system and no capabilities, and its "
            "HTTP metrics server is switched off (`-addr=`), because nothing should be listening "
            "that MaxGuard does not need. Check it; the second command fails on purpose, "
            "because the listening address has no default:\n\n@@RUN compose@@",
            "Create `maxguard/adapters/netflow.py`:\n\n@@FILE maxguard/adapters/netflow.py@@\n\n"
            "Things to notice. A flow record has one direction, so `orig_bytes` is the flow's "
            "byte count and `resp_bytes` is 0; the answer is its own record. The `uid` is `N` "
            "plus 17 hex digits of a SHA-256 over the record without the time goflow2 received "
            "it, so the same flow always gets the same uid and a file copied twice is counted "
            "once. ICMP type and code go into the port fields, as Zeek does. `accepts()` also "
            "takes a single goflow2 file, recognised by its first line: the dashboard and "
            "`/api/ingest` save uploads under a random name with no `.json` suffix, so a "
            "folder can never arrive that way. It never takes a folder that has `conn.log` or "
            "`zeek/`, so it cannot steal a Zeek log folder or a sensor folder. An uploaded file "
            "is attacker-controlled, so every number and address is checked "
            "(`whole_number()`, `ip_text()`) and a damaged record is skipped, not fatal: "
            "before the security review, one bad line made the upload answer HTTP 500.",
            "Add the adapter **last** in `ADAPTERS` in `maxguard/pipeline.py` (the other "
            "three always get the first look):\n\n@@FILE maxguard/pipeline.py@@\n\n"
            "and give flow records their own `source` in `maxguard/events/normalize.py` (the "
            "two new lines in `from_conn`):\n\n@@FILE maxguard/events/normalize.py@@",
            "Create the test data `tests/fixtures/netflow/goflow2.json` (real goflow2 v2.2.7 "
            "output from the generator below, documentation addresses only):\n\n"
            "@@FILE tests/fixtures/netflow/goflow2.json@@\n\n"
            "and the tests `tests/unit/test_netflow.py`:\n\n@@FILE tests/unit/test_netflow.py@@"
            "\n\nRun them with the tests of the two files you changed:\n\n@@RUN tests@@",
            "Create the flow generator `scripts/send_test_flows.py`. It packs NetFlow v5, v9 "
            "and IPFIX packets by hand with `struct`, so you can see exactly what a router "
            "sends:\n\n@@FILE scripts/send_test_flows.py@@",
            "Prove it end to end: start the collector on `127.0.0.1`, send the test flows, "
            "start a new file the way you would every hour (`mv`, then `SIGHUP`), and analyze "
            "the finished file:\n\n@@RUN proof@@\n\n"
            "No rule fires, and that is correct. The cleartext, TLS and certificate rules read "
            "Zeek's protocol logs (`ftp.log`, `ssl.log`, ...), which only exist when someone "
            "looked inside the packets. A flow to port 23 is not proof of Telnet, and MaxGuard "
            "only reports what it can prove. What flows do give is the timeline (who talked "
            "to whom, how much, when): upload the finished `.json` file on the dashboard and "
            "open the timeline for `192.0.2.10`.",
            "**On the lab** (*not run — verify on hardware*): if your router can export "
            "NetFlow or IPFIX, point it at the console's LAN address, UDP port 2055, start the "
            "collector with `MAXGUARD_NETFLOW_ADDRESS=<console address>`, and check that "
            "`/data/netflow/goflow2.json` grows. Also run the collector once on the Raspberry "
            "Pi 5 (the arm64 image was not run in planning). Many home routers cannot export "
            "flows at all; write down what yours can do in the issue.",
            pr_step("feat: NetFlow/IPFIX input through goflow2 (JAK-10)", "JWinborne1"),
        ],
        "files": ["docker/netflow-compose.yaml", "maxguard/adapters/netflow.py",
                  "maxguard/pipeline.py", "maxguard/events/normalize.py",
                  "tests/fixtures/netflow/goflow2.json", "tests/unit/test_netflow.py",
                  "scripts/send_test_flows.py"],
        "commands": [
            {"id": "compose", "expect_code": 1, "show": (
                "MAXGUARD_NETFLOW_ADDRESS=127.0.0.1 \\\n"
                "  docker compose -f docker/netflow-compose.yaml config --format json | python -c "
                "\"import json, sys; s = json.load(sys.stdin)['services']['goflow2']; "
                "print(s['image'].split('@')[0], s['user'], s['read_only'], s['cap_drop'], "
                "[(p['host_ip'], p['published'], p['protocol']) for p in s['ports']])\"\n"
                "docker compose -f docker/netflow-compose.yaml config --quiet")},
            {"id": "tests", "show": ("pytest tests/unit/test_netflow.py tests/unit/test_normalize.py "
                                     "tests/unit/test_pipeline.py -q")},
            {"id": "proof", "show": JAK10_PROOF,
             "run": JAK10_PROOF.replace("maxguard analyze", "python -m cli.main analyze"),
             "note": ("goflow2 runs with your user ID here, so you can read the files without "
                      "`sudo`; on the console the default is 1000:1000, the first user.")},
        ],
        "test": "The tests pass, the proof prints seven flows and zero findings, and an "
                "uploaded flow file shows on the timeline page.",
        "why": (
            "Many small offices have a router that can export flows but no mirror port. Flow "
            "records carry no payload, so they cannot show a cleartext password, but they do show "
            "who talked to whom, how much, and when, which is enough for the timeline, baselines, "
            "and preview-before-you-block. Converting them to Zeek's `conn.log` shape means no "
            "rule or page needs to know they came from NetFlow."
        ),
        "checklist": checklist(extra=["The collector image is pinned by version and digest",
                                      "Test data uses only documentation addresses (RFC 5737)",
                                      "Jaiden reviewed the new `source` value"]),
    },
    {
        "id": "JAK-11", "owner": "jakub", "milestone": "S12",
        "title": "Host agent for one computer",
        "labels": ["area:sensor"], "hardware": True,
        "depends": ["JAI-07"],
        "goal": (
            "For a home with no mirror port: a small agent on one computer captures that "
            "computer's own traffic with the operating system's built-in tools, in rotating "
            "files, and uploads each finished file to the console's `POST /api/ingest`."
        ),
        "prereq": "JAI-07 is merged (ingest endpoint and the ingest-only app on port 8001).",
        "steps": [
            start_step("jakub/host-agent"),
            "Create `maxguard/sensor/agent.py`:\n\n@@FILE maxguard/sensor/agent.py@@\n\n"
            "The docstring lists every capture flag with the manual it comes from. Four "
            "decisions to understand. tcpdump runs as root only long enough to open the network "
            "card, then `-Z` drops to your normal user before it writes any file. tcpdump names "
            "files with the *local* time, so the agent starts it with `TZ=UTC`: the names then "
            "sort in time order all year. The newest file is the one tcpdump is still writing, "
            "so it is never uploaded; a file counts as uploaded only after a `2xx` answer, "
            "goes to `rejected/` on 400, 413 or 422 (answers that would be the same next time, "
            "so one bad file cannot block the rest), and is retried (oldest first) on anything "
            "else. Windows' `pktmon` rotates only by size, so the agent stops and restarts it "
            "every interval and converts each finished `.etl` file to pcapng.\n\n"
            "The security review added three more details. The upload uses a session with "
            "`trust_env = False`: by default `requests` would send your captures through any "
            "proxy in `HTTP_PROXY` and replace the token with a password from `~/.netrc`. A "
            "`%` in the spool folder's name is doubled, because tcpdump runs the whole `-w` "
            "name through `strftime`. And a spool folder the agent creates as root is given to "
            "`capture_user`, because tcpdump opens its files only after `-Z` dropped root.",
            "Create the tests `tests/unit/test_agent.py`. They check the command for each "
            "operating system and upload to a fake server and to the real ingest app through "
            "`TestClient`; no test ever starts a capture:\n\n@@FILE tests/unit/test_agent.py@@"
            "\n\nRun them:\n\n@@RUN tests@@",
            "See the capture flags work. This runs tcpdump inside a container that has no "
            "network, on its own loopback, with 2-second files: the names are UTC and the "
            "files belong to `nobody` (user 65534), which shows that `-Z` dropped root:"
            "\n\n@@RUN tcpdump@@",
            "Upload for real: the ingest-only app (the one sensors reach on port 8001) and the "
            "agent in `--upload-only` mode, with the Telnet capture standing in for a finished "
            "file. The config file must be private (`chmod 600`), because it holds the "
            "token:\n\n@@RUN upload@@",
            "**On your own laptop** (*not run — verify on hardware*). On the console set "
            "`MAXGUARD_INGEST_TOKEN` (make one with "
            "`python -c \"import secrets; print(secrets.token_urlsafe(32))\"`) and start "
            "`docker/compose.lan.yaml`. On the laptop write `~/.config/maxguard/agent.toml` "
            "(Windows: `%APPDATA%\\MaxGuard\\agent.toml`) with `console_url = "
            "\"http://<console address>:8001\"`, the same token, `spool_dir`, `sensor_id`, "
            "`capture_user` (your login name) and `rotate_seconds = 900`; `chmod 600` it; then "
            "`sudo python -m maxguard.sensor.agent` (Windows: an Administrator terminal). After "
            "15 minutes the first file appears on the console. Port 8001 is plain HTTP, so the "
            "token and your captures cross the LAN unencrypted: use a wired or trusted network. "
            "Check macOS's `tcpdump -Z` and Windows' `pktmon` too; neither could be run in "
            "planning.",
            pr_step("feat: host agent with OS-native capture (JAK-11)", "JWinborne1"),
        ],
        "files": ["maxguard/sensor/agent.py", "tests/unit/test_agent.py"],
        "commands": [
            {"id": "tests", "show": "pytest tests/unit/test_agent.py -q"},
            {"id": "tcpdump", "show": (
                "docker run --rm --network none --cap-add NET_RAW --cap-add NET_ADMIN -e TZ=UTC "
                "nicolaka/netshoot:v0.15 sh -c '\n"
                "  mkdir -p /spool && chown nobody /spool\n"
                "  tcpdump -i lo -n -G 2 -w \"/spool/capture-%Y%m%d-%H%M%S.pcap\" -Z nobody "
                "2> /dev/null & P=$!\n"
                "  ping -i 0.5 -c 9 127.0.0.1 > /dev/null; kill -INT $P; wait $P\n"
                "  ls -ln /spool'"),
             "note": "The file names carry the time you run it, so yours differ."},
            {"id": "upload", "env": "zeek", "show": JAK11_UPLOAD,
             "run": (JAK11_UPLOAD.replace("python ", "python3 ")
                     .replace("  uvicorn ", "  python3 -m uvicorn ")),
             "note": ("`uvicorn` and the agent run inside the `zeek/zeek:9.0.0` image here, "
                      "because the console needs Zeek to read a capture. The console refuses a "
                      "token shorter than 32 characters.")},
        ],
        "test": "The tests pass, the upload check prints `uploaded 1 file(s)` and `200 OK`, and "
                "a manual run on your own laptop uploads one file that appears on the console.",
        "why": (
            "A host agent sees only its own computer, but it needs no extra hardware, which makes "
            "it the easiest way for a home user to try MaxGuard on live traffic. Using the "
            "built-in capture tools avoids installing a driver, and uploading finished files "
            "reuses the exact upload path the dashboard already tests."
        ),
        "checklist": checklist(extra=["No test starts a real capture",
                                      "The token is read from a private config file"]),
    },
]
