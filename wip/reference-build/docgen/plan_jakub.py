"""Jakub's tasks: Zeek scripts, Suricata, cleartext rules, inventory, live sensor, NetFlow, agent."""

from plan_helpers import checklist, pr_step, start_step

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
        "files": ["maxguard/rules/cleartext.py", "maxguard/rules/__init__.py",
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
            "The real check runs in the engine image, where Suricata is installed:\n\n@@RUN image@@",
            pr_step("feat: run Suricata next to Zeek on captures (JAK-05)", "flau0306"),
        ],
        "files": ["maxguard/suricata/runner.py", "maxguard/adapters/pcap.py",
                  "maxguard/api/app.py", "tests/unit/test_suricata_runner.py"],
        "commands": [
            {"id": "tests", "show": "pytest tests/unit/test_suricata_runner.py -q"},
            {"id": "all", "show": 'pytest -m "not integration" -q'},
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
        "labels": ["area:sensor", "critical-path"], "hardware": True, "status": "design",
        "depends": ["JAK-06", "JAI-07"],
        "goal": (
            "Turn the lab into MaxGuard's live sensor (`docs/ARCHITECTURE.md` section 4): Zeek and "
            "Suricata run all the time on the capture port, rotate their logs every 15 minutes "
            "into one folder per interval on the SSD, and a small shipper sends each completed "
            "folder to the console's `POST /api/ingest`. The console analyzes it like an upload, "
            "with `sensor_id` set to the sensor's name."
        ),
        "prereq": "JAK-06 (the lab works) and JAI-07 (the API with `/api/ingest`) are merged.",
        "steps": [
            start_step("jakub/live-sensor"),
            "**Zeek rotation.** Find the Zeek 9 way to rotate logs every 15 minutes without "
            "`zeekctl` (look at `Log::default_rotation_interval` and the rotation post-processor "
            "in the Zeek 9.0.0 documentation) so that each interval's logs land in "
            "`/data/zeek/<YYYY-MM-DD-HHMM>/`. Write it as `maxguard/zeek/scripts/live/rotate.zeek`. "
            "Test it on the Pi with a 1-minute interval first.",
            "**Suricata live settings.** Copy `maxguard/suricata/maxguard-suricata.yaml` to "
            "`maxguard/suricata/maxguard-suricata-live.yaml`, add an `af-packet` section for the "
            "capture interface, and turn on `eve` file rotation every 15 minutes (find the option "
            "for Suricata 8.0 in its user guide). Keep Community ID and JA4 exactly as they are.",
            "**Compose file.** Write `docker/sensor-compose.yaml` with two services, "
            "`zeek/zeek:9.0.0` and `jasonish/suricata:8.0.7`, both with `network_mode: host`, "
            "only the capabilities they need (Zeek: `NET_RAW`, `NET_ADMIN`; Suricata: also "
            "`SYS_NICE`), `/data` mounted, and `restart: unless-stopped`. **No `-D` for Zeek** "
            "(random seeds protect a live sensor).",
            "**Adapter.** Write `maxguard/adapters/live.py` with `LiveSensorAdapter` (Contract 3, "
            "unchanged): `accepts()` is true for a sensor data folder; `to_zeek_logs()` returns "
            "the newest *completed* interval folder (never the one still being written) with that "
            "interval's `eve.json` merged in.",
            "**Shipper.** Write `maxguard/sensor/shipper.py`: every minute, find completed "
            "interval folders not shipped yet, pack each as `.tar.gz`, `POST` it to "
            "`<console>/api/ingest` with `Authorization: Bearer <token>` (console URL and token "
            "from a config file in `/data`, never in the repository), and mark it shipped only "
            "after a `2xx` answer. Delete shipped folders older than 7 days.",
            "**Tests** (`tests/unit/test_live_adapter.py`, `tests/unit/test_shipper.py`): the "
            "adapter picks the newest completed folder and ignores the current one; the shipper "
            "sends the right file with the right header to a fake HTTP server on `127.0.0.1` "
            "(`http.server` in a thread), retries after a failure, and never ships a folder twice.",
            "Run the sensor on the lab for one day and check that alerts appear on the console "
            "within about 20 minutes of the traffic.",
            pr_step("feat: live sensor with rotation and shipping (JAK-07)", "flau0306"),
        ],
        "files": [], "commands": [
            {"id": "tests", "env": "none",
             "show": "pytest tests/unit/test_live_adapter.py tests/unit/test_shipper.py -q"},
        ],
        "test": (
            "Both test files pass on your laptop. On the lab, `ls /data/zeek` shows a new folder "
            "every 15 minutes, `docker compose -f docker/sensor-compose.yaml ps` shows both "
            "containers running after a reboot, and the console's alert queue shows the lab "
            "phone's traffic. The capture port still has no IP address (`ip -br addr show eth0`)."
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
        "files": ["maxguard/sensor/__init__.py", "maxguard/sensor/attribution.py",
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
        "labels": ["area:sensor"], "status": "design",
        "depends": ["JAI-07", "JAI-03"],
        "goal": (
            "Let a router that exports NetFlow v5/v9 or IPFIX feed MaxGuard: a collector "
            "container writes flow records, and `NetflowAdapter` (Contract 3) turns them into "
            "`conn.log`-shaped JSON records, so the normalizer, the timeline, and the "
            "flow-based checks work unchanged (payload rules simply find nothing)."
        ),
        "prereq": "JAI-07 is merged. Ask Ahmad which collector to use if you prefer another one.",
        "steps": [
            start_step("jakub/netflow"),
            "Pick the collector: `netsampler/goflow2` (check the image tag, its license, and that "
            "it is published for arm64 and amd64; record it in `docs/DEPENDENCIES.md`). Write "
            "`docker/netflow-compose.yaml` that listens on UDP 2055 and writes JSON lines to `/data/netflow/`.",
            "Write `maxguard/adapters/netflow.py` with `NetflowAdapter`: `accepts()` is true for a "
            "folder of the collector's JSON files; `to_zeek_logs()` writes `conn.log` with `ts`, "
            "`uid` (a deterministic hash of the flow record), `id.orig_h`, `id.orig_p`, "
            "`id.resp_h`, `id.resp_p`, `proto`, `orig_bytes`, `resp_bytes`, `duration`, and "
            "`mg_source: netflow`.",
            "Add it to `ADAPTERS` in `maxguard/pipeline.py` and `netflow` as a `source` value in the "
            "normalizer (a contract change: label the pull request).",
            "Write `tests/unit/test_netflow.py` with a few hand-written collector records using "
            "documentation addresses (RFC 5737, e.g. `192.0.2.10`): the conversion, the "
            "deterministic `uid`, and the normalizer reading the result.",
            "Prove it end to end: a short Python script that sends NetFlow v5 packets "
            "(`struct`-packed header and records, fake addresses) to the collector on your laptop, "
            "then `maxguard analyze` on the output folder.",
            pr_step("feat: NetFlow/IPFIX input through goflow2 (JAK-10)", "flau0306"),
        ],
        "files": [], "commands": [
            {"id": "tests", "env": "none", "show": "pytest tests/unit/test_netflow.py -q"},
        ],
        "test": "The unit tests pass, and the end-to-end check shows the generated flows on the "
                "timeline page.",
        "why": (
            "Many small offices have a router that can export flows but no mirror port. Flow "
            "records carry no payload, so they cannot show a cleartext password, but they do show "
            "who talked to whom, how much, and when, which is enough for the timeline, baselines, "
            "and preview-before-you-block. Converting them to Zeek's `conn.log` shape means no "
            "rule or page needs to know they came from NetFlow."
        ),
        "checklist": checklist(extra=["The collector's license is in `docs/DEPENDENCIES.md`",
                                      "Test data uses only documentation addresses (RFC 5737)"]),
    },
    {
        "id": "JAK-11", "owner": "jakub", "milestone": "S12",
        "title": "Host agent for one computer",
        "labels": ["area:sensor"], "status": "design",
        "depends": ["JAI-07"],
        "goal": (
            "For a home with no mirror port: a small agent on one computer captures that "
            "computer's own traffic with the operating system's built-in tools, in rotating "
            "files, and uploads each finished file to the console's `POST /api/ingest`."
        ),
        "prereq": "JAI-07 is merged (ingest endpoint).",
        "steps": [
            start_step("jakub/host-agent"),
            "Write `maxguard/sensor/agent.py`. It builds the capture command for the operating "
            "system without third-party drivers: Linux and macOS `tcpdump` with `-G` (rotate "
            "every N seconds) and `-w` with a time pattern; Windows `pktmon start --capture` and "
            "`pktmon etl2pcap` to convert each file. Check every flag against the tcpdump manual "
            "page and Microsoft's pktmon documentation, and cite them in the docstring.",
            "Upload each finished file with `requests` and `Authorization: Bearer <token>`; the "
            "console URL and token come from a config file outside the repository. Document that "
            "the console must be the user's own machine and that ingest is off unless "
            "`MAXGUARD_INGEST_TOKEN` is set there.",
            "Write `tests/unit/test_agent.py`: the command built for each operating system, and "
            "uploads to a fake HTTP server on `127.0.0.1`. Never start a real capture in a test.",
            pr_step("feat: host agent with OS-native capture (JAK-11)", "flau0306"),
        ],
        "files": [], "commands": [
            {"id": "tests", "env": "none", "show": "pytest tests/unit/test_agent.py -q"},
        ],
        "test": "The unit tests pass on Linux, and a manual run on your own laptop uploads one "
                "file that appears on the console.",
        "why": (
            "A host agent sees only its own computer, but it needs no extra hardware, which makes "
            "it the easiest way for a home user to try MaxGuard on live traffic. Using the "
            "built-in capture tools avoids installing a driver, and uploading finished files "
            "reuses the exact upload path the dashboard already tests."
        ),
        "checklist": checklist(extra=["No test starts a real capture"]),
    },
]
