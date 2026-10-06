"""Karthik's tasks: traffic lab and captures, fixtures, integration tests, CI, release testing."""

from plan_helpers import checklist, pr_step, start_step

SCENARIOS = ["_common.py", "telnet.py", "ftp.py", "plain_http.py", "plain_http_alt.py", "pop3.py",
             "imap.py", "tls_weak_version.py", "tls_weak_cipher.py", "cert_expired.py",
             "cert_self_signed.py", "cert_weak_key.py", "cert_sha1.py", "clean_tls13.py",
             "dns_lookup.py"]

LAB_POP3_OUTPUT = """client-1 exited with code 0
 Compose Stopping Aborting on container exit...
sniffer-1  | 24 packets captured
sniffer-1  | 24 packets received by filter
sniffer-1  | 0 packets dropped by kernel
server-1 exited with code 137"""

TASKS = [
    {
        "id": "KAR-01", "owner": "karthik", "milestone": "W0",
        "title": "Traffic lab and the 14 test captures",
        "labels": ["area:testing", "critical-path"],
        "depends": [],
        "goal": (
            "Build MaxGuard's traffic lab: insecure test services and a client on an isolated "
            "Docker network, recorded by tcpdump. Record one small capture per weakness (plus a "
            "clean TLS 1.3 session and a DNS lookup that must trigger nothing) into "
            "`tests/pcaps/`. Every rule's tests are built on these captures."
        ),
        "prereq": "Week 0 sections 0.1 to 0.8 are done (Docker works). This task does not need JAI-01.",
        "steps": [
            "Update `main` and create your branch (this task needs no Python environment, so "
            "there is nothing to activate yet):\n\n```bash\ncd ~/projects/maxguard\n"
            "git checkout main && git pull\ngit checkout -b karthik/traffic-lab\n```",
            "Create the lab's Compose file `lab/compose.yaml`:\n\n@@FILE lab/compose.yaml@@\n\n"
            "`internal: true` is the important line: nothing in the lab can reach the internet or "
            "your home network. The sniffer shares the server's network card, so it records "
            "exactly what the server sends and receives.",
            "Create the server: `lab/server/Dockerfile`\n\n@@FILE lab/server/Dockerfile@@\n\n"
            "`lab/server/make_certs.py` (fake certificates; the SHA-1 one is made with the "
            "`openssl` command because the `cryptography` library refuses to sign with SHA-1):\n\n"
            "@@FILE lab/server/make_certs.py@@\n\nand `lab/server/services.py` (every service is "
            "insecure on purpose):\n\n@@FILE lab/server/services.py@@",
            "Create the client: `lab/client/Dockerfile`\n\n@@FILE lab/client/Dockerfile@@\n\n"
            "and the scenarios in `lab/client/scenarios/`, one file per capture. The shared "
            "helpers `_common.py`:\n\n@@FILE lab/client/scenarios/_common.py@@\n\n"
            + "\n\n".join(f"`{name}`:\n\n@@FILE lab/client/scenarios/{name}@@" for name in SCENARIOS[1:])
            + "\n\n(The two HTTP scenarios are not called `http.py`: a file with that name would "
            "hide Python's own `http` package from the client.)",
            "Build the images once (this downloads Python packages, so it needs the internet):\n\n"
            "@@RUN build@@",
            "Record every capture. Each run starts the server and the sniffer, runs one scenario, "
            "and stops everything when the client finishes:\n\n@@RUN record@@",
            "Copy the captures into the tests folder and add the source file "
            "`tests/pcaps/SOURCES.md` (update the SHA-256 column with "
            "`sha256sum tests/pcaps/*.pcap | cut -c1-16` if you re-recorded):\n\n"
            "```bash\nmkdir -p tests/pcaps\ncp lab/captures/*.pcap tests/pcaps/\n```\n\n"
            "@@FILE tests/pcaps/SOURCES.md@@",
            "Look inside one capture with tcpdump (the netshoot image has it):\n\n@@RUN look@@",
            pr_step("test: traffic lab and the 14 synthetic test captures (KAR-01)", "JWinborne1"),
        ],
        "files": (["lab/compose.yaml", "lab/server/Dockerfile", "lab/server/make_certs.py",
                   "lab/server/services.py", "lab/client/Dockerfile"]
                  + [f"lab/client/scenarios/{name}" for name in SCENARIOS]
                  + [("tests/pcaps", "tests/pcaps"),
                     ("tests/pcaps/SOURCES.md", "snip:pcaps_SOURCES.md")]),
        "commands": [
            {"id": "build", "env": "none", "show": "cd lab && docker compose build && cd ..",
             "note": "Run in planning with the same Dockerfiles; the build log is long and differs "
                     "on every machine, so it is not shown. It ends without an error."},
            {"id": "record", "env": "none",
             "show": ("cd lab\n"
                      "for s in telnet ftp plain_http plain_http_alt pop3 imap tls_weak_version "
                      "tls_weak_cipher cert_expired cert_self_signed cert_weak_key cert_sha1 "
                      "clean_tls13 dns_lookup; do\n"
                      "  CAPTURE=$s SCENARIO=$s docker compose up --abort-on-container-exit "
                      "--exit-code-from client\n"
                      "  docker compose down\n"
                      "done\nls -l captures\ncd .."),
             "output": LAB_POP3_OUTPUT,
             "label": "Expected output (the end of the planning run for pop3)",
             "note": "The server's exit code 137 is normal: Compose stops it once the client is done."},
            {"id": "look", "show": ("docker run --rm -v \"$PWD/tests/pcaps:/p:ro\" --entrypoint tcpdump "
                                    "nicolaka/netshoot:v0.15 -nn -r /p/telnet.pcap 'tcp port 23' | head -n 4")},
        ],
        "test": (
            "`ls -l lab/captures` lists 14 files of 1 to 4 KB. The tcpdump command shows the "
            "client (`172.18.0.3` in planning) opening a connection to port 23 on the server. "
            "Docker may give your lab network other addresses; that is fine. KAR-02 then turns "
            "the captures into fixtures, and FIO-02 and JAK-03 prove each one triggers exactly "
            "its rule."
        ),
        "why": (
            "A detection rule is only as good as its test data, and this repository is public, so "
            "real captures from anyone's network are not allowed (CLAUDE.md rule 6). A lab of our "
            "own makes captures we can share, regenerate, and explain line by line. One weakness "
            "per capture keeps each test unambiguous; the two clean captures catch rules that "
            "fire on everything."
        ),
        "checklist": checklist(extra=["Every capture has a row in `tests/pcaps/SOURCES.md`",
                                      "Each capture is under 1 MB"]),
    },
    {
        "id": "KAR-02", "owner": "karthik", "milestone": "W1",
        "title": "Test fixtures: Zeek and Suricata output for every capture",
        "labels": ["area:testing", "critical-path"],
        "depends": ["KAR-01", "JAK-01", "JAK-02", "JAI-01"],
        "goal": (
            "Write `scripts/make_fixtures.sh`, which runs Zeek 9.0.0 and Suricata 7.0.10 on every "
            "capture exactly the way MaxGuard does and saves the logs to "
            "`tests/fixtures/zeek/<capture>/`, and add the hand-made fixtures for traffic the lab "
            "does not make yet (DNS with DHCP, RDP, and tab-separated logs). Unit tests read these "
            "folders, so they run in seconds without Docker."
        ),
        "prereq": "KAR-01, JAK-01 (Zeek scripts) and JAK-02 (Suricata config) are merged.",
        "steps": [
            start_step("karthik/fixtures"),
            "Create `scripts/make_fixtures.sh`:\n\n@@FILE scripts/make_fixtures.sh@@",
            "Run it:\n\n```bash\nbash scripts/make_fixtures.sh\n```\n\nIt prints one line per "
            "capture with the files it wrote, for example "
            "`telnet: conn.log eve.json known_hosts.log maxguard_cleartext.log`.",
            "Add the hand-made fixtures for traffic the lab does not make yet. Create "
            "`tests/fixtures/zeek/_handmade/README.md`:\n\n@@FILE tests/fixtures/zeek/_handmade/README.md@@\n\n"
            "the two capture generators (they write the same bytes on every run) "
            "`tests/fixtures/zeek/_handmade/make_dns_dhcp_pcap.py`:\n\n"
            "@@FILE tests/fixtures/zeek/_handmade/make_dns_dhcp_pcap.py@@\n\n"
            "and `tests/fixtures/zeek/_handmade/rdp/make_rdp_pcap.py` with its notes "
            "`tests/fixtures/zeek/_handmade/rdp/README.md`:\n\n"
            "@@FILE tests/fixtures/zeek/_handmade/rdp/make_rdp_pcap.py@@\n\n"
            "@@FILE tests/fixtures/zeek/_handmade/rdp/README.md@@\n\n"
            "and the one Suricata rule used only to get an `alert` event into a fixture, "
            "`tests/fixtures/zeek/_handmade/fixture-only.rules`:\n\n"
            "@@FILE tests/fixtures/zeek/_handmade/fixture-only.rules@@\n\n"
            "Then run the commands in the README's **Rebuild** section (and the ones in the RDP "
            "notes). They were run when the fixtures were made in planning.",
            "Prove the fixtures are reproducible: make them again into a temporary folder and "
            "compare (Zeek's logs must be identical; Suricata's `eve.json` has a random "
            "`flow_id`, which MaxGuard ignores):\n\n@@RUN again@@",
            "Run the unit tests (nothing should break):\n\n@@RUN tests@@",
            pr_step("test: Zeek and Suricata fixtures for every capture (KAR-02)", "JWinborne1"),
        ],
        "files": ["scripts/make_fixtures.sh", ("tests/fixtures/zeek", "tests/fixtures/zeek")],
        "commands": [
            {"id": "again", "timeout": 900, "show": (
                "FIXTURES_DIR=/tmp/fixture-check bash scripts/make_fixtures.sh > /dev/null\n"
                "for d in tests/fixtures/zeek/[a-z]*/; do n=$(basename \"$d\"); "
                "diff -rq --exclude=eve.json \"$d\" \"/tmp/fixture-check/$n\" > /dev/null "
                "&& echo \"$n: identical\" || echo \"$n: DIFFERENT\"; done")},
            {"id": "tests", "show": 'pytest -m "not integration" -q'},
        ],
        "test": "Every capture prints `identical`, and the unit tests still pass.",
        "why": (
            "Unit tests that need Docker and a capture are slow, so nobody runs them often. Running "
            "Zeek and Suricata once, committing their output, and testing against it gives fast "
            "tests with real tool output. Zeek's `-D` option is what makes the output identical "
            "on every run; without it every fixture would change every time and the tests could "
            "never compare exact IDs. Re-run the script whenever a capture, a Zeek script, or the "
            "Suricata config changes, and commit the result."
        ),
        "checklist": checklist(extra=["All captures print `identical`"]),
    },
    {
        "id": "KAR-03", "owner": "karthik", "milestone": "W2",
        "title": "Integration tests: the real pipeline on every capture",
        "labels": ["area:testing", "critical-path"],
        "depends": ["JAI-05", "JAI-04", "KAR-02"],
        "goal": (
            "Write expected-result files and an integration test that runs the real pipeline on "
            "every capture inside the engine image and checks that each capture produces exactly "
            "the findings it should, and nothing it should not. Add fast unit checks of Suricata's "
            "saved output: a Community ID on every record and a JA4 on every TLS client hello."
        ),
        "prereq": "JAI-05 (pipeline) and JAI-04 (engine image) are merged.",
        "steps": [
            start_step("karthik/integration-tests"),
            "Write one expected-result file per capture in `tests/expected/`, in the Fall 2026 "
            "format. `expected` names the rule the capture was recorded to trigger, on its port. "
            "`must_not_contain` lists the other rules of the same family: they read the same logs, "
            "so they are the likely misfires, and a new rule never forces you to edit every file. "
            "The two clean captures say `expect_no_findings` instead.\n\n"
            + "\n\n".join(f"`tests/expected/{name}.json`:\n\n@@FILE tests/expected/{name}.json@@"
                          for name in ("telnet", "ftp", "pop3", "imap", "plain_http",
                                       "plain_http_alt", "tls_weak_version", "tls_weak_cipher",
                                       "cert_expired", "cert_self_signed", "cert_sha1",
                                       "cert_weak_key", "clean_tls13", "dns_lookup")),
            "Create `tests/integration/test_pcaps.py`. Besides one test per expected file, "
            "`test_every_capture_has_an_expected_file` fails when someone adds a capture without "
            "an answer key, so no capture goes untested:\n\n@@FILE tests/integration/test_pcaps.py@@\n\n"
            "Whether Suricata ran is checked later, in JAK-05: the pipeline starts running it there.",
            "Create `tests/unit/test_suricata_eve.py`. It reads the saved `eve.json` fixtures, so it "
            "runs with the fast unit tests. A record with a server name (SNI) proves Suricata parsed "
            "the client hello, because the name is only sent there, and that is the message JA4 is "
            "computed from. Zeek's TLS sessions are a second witness, so the JA4 check cannot pass "
            "by checking nothing:\n\n@@FILE tests/unit/test_suricata_eve.py@@",
            "Run it:\n\n@@RUN eve@@",
            "Build the test image and run the integration tests in it with networking off:\n\n"
            "@@RUN integration@@",
            pr_step("test: integration tests on every lab capture (KAR-03)", "JWinborne1"),
        ],
        "files": ["tests/expected", "tests/integration/test_pcaps.py",
                  "tests/unit/test_suricata_eve.py"],
        "commands": [
            {"id": "eve", "show": "pytest tests/unit/test_suricata_eve.py -q"},
            {"id": "integration", "env": "zeek",
             "show": ("docker build -f docker/Dockerfile --target test -t maxguard:test .\n"
                      "docker run --rm --network none maxguard:test pytest -m integration -q"),
             "run": "python3 -m pytest -m integration -q -p no:cacheprovider",
             "note": ("Run in planning inside `zeek/zeek:9.0.0` with MaxGuard's Python packages "
                      "added, because the engine image build needs Debian's package servers "
                      "(JAI-04). Zeek ran for real on every capture.")},
        ],
        "test": ("`pytest -m integration -q` passes inside the test image (15 tests: one per "
                 "capture, plus the one that checks every capture has an expected file), and the "
                 "Suricata checks pass with the unit tests."),
        "why": (
            "Unit tests use saved fixtures, so they cannot notice when the way MaxGuard *runs* Zeek "
            "or Suricata breaks (a missing script, a wrong option, a new tool version). Integration "
            "tests run the real tools on the real captures, offline, the same way users will. In "
            "planning, leaving `cleartext.zeek` out of the Zeek command made exactly the Telnet, "
            "POP3 and IMAP tests fail, and nothing else. The `must_not_contain` lists catch a rule "
            "that starts firing where it should not."
        ),
        "checklist": checklist(extra=["One expected file per capture",
                                      "The integration tests pass in the test image"]),
    },
    {
        "id": "KAR-04", "owner": "karthik", "milestone": "W3",
        "title": "CI runs the integration tests, plus a determinism test",
        "labels": ["area:testing", "area:release"], "status": "written",
        "depends": ["KAR-03"],
        "goal": (
            "Add an `integration` job to CI that builds the engine image and runs the integration "
            "tests in it with networking off, and add a test that analyzes every capture twice "
            "and checks the two reports are identical."
        ),
        "prereq": "KAR-03 is merged.",
        "steps": [
            start_step("karthik/ci-integration"),
            "Replace `.github/workflows/ci.yml` with the version that has the second job:\n\n"
            "@@FILE .github/workflows/ci.yml@@\n\n*Written in planning; its first real run is "
            "your pull request.* Check the action versions (`actions/checkout`, "
            "`actions/setup-python`) against their GitHub releases pages before merging. The "
            "`HAVE_JA4` line fails the job if the image's Suricata was built without JA4: "
            "Suricata 7.0.10 and 8.0.7 from `jasonish/suricata` list it, but Debian's package "
            "could not be checked in planning, so the first CI run answers that question.",
            "Create `tests/integration/test_determinism.py`. It analyzes every capture twice, into "
            "two *different* folders (so a folder path that leaks into the report fails too), and "
            "when the reports differ, `differences()` names the exact value, for example "
            "`report['events'][0]['uid']: 'CVMEph...' != 'CeUBb0...'`. The small test of that helper "
            "is not marked, so it also runs with the unit tests:\n\n"
            "@@FILE tests/integration/test_determinism.py@@",
            "Run the integration tests again:\n\n@@RUN integration@@",
            "Open the pull request and watch both jobs. In the `integration` job's log, check "
            "that the tests ran with `--network none`.",
            pr_step("ci: integration job in the engine image, determinism test (KAR-04)", "JWinborne1"),
        ],
        "files": [".github/workflows/ci.yml", "tests/integration/test_determinism.py"],
        "commands": [
            {"id": "integration", "env": "zeek",
             "show": ("docker build -f docker/Dockerfile --target test -t maxguard:test .\n"
                      "docker run --rm --network none maxguard:test pytest -m integration -q"),
             "run": "python3 -m pytest -m integration -q -p no:cacheprovider",
             "note": ("Run in planning inside `zeek/zeek:9.0.0` with MaxGuard's Python packages "
                      "added (see KAR-03). Running Zeek without `-D` made the Telnet determinism "
                      "test fail on the connection IDs, which is the mistake this test exists to catch.")},
        ],
        "test": "Both CI jobs are green on your pull request. After merging, ask Jaiden to add "
                "`integration` to the required checks of the `main-protection` ruleset.",
        "why": (
            "Running the integration tests on every pull request means nobody can merge a change "
            "that breaks the real pipeline, even if all unit tests pass. Running them with the "
            "network off proves the engine works offline (CLAUDE.md rule 1), and the determinism "
            "test guards rule 2 with the real tools, not only with fixtures."
        ),
        "checklist": checklist(extra=["The `integration` job is green",
                                      "Jaiden added it to the required checks"]),
    },
    {
        "id": "KAR-05", "owner": "karthik", "milestone": "W6",
        "title": "Release-candidate test with an outside tester",
        "labels": ["area:testing", "area:release", "critical-path"], "status": "process",
        "depends": ["JAI-09", "JON-05"],
        "goal": (
            "Run the alpha acceptance test (`docs/roadmap/README.md`) on `v2.0-alpha-rc1` "
            "yourself, then with someone outside the team, on a computer that has never run "
            "MaxGuard, and turn every problem into an issue."
        ),
        "prereq": "JAI-09 (`v2.0-alpha-rc1` is tagged) and JON-05 (offline bundle) are merged.",
        "steps": [
            "Write `docs/testing/rc-checklist.md`: the acceptance test steps as a checklist with a "
            "result column (pass, fail, notes), plus the exact versions under test.",
            "Run it yourself first, with the network unplugged at step 4.",
            "Run it with the outside tester (a classmate not on the team). Do not help unless they "
            "are stuck for more than 10 minutes; write down every place they hesitated.",
            "Open one issue per problem with the label `type:bug` and the milestone "
            "`W8 v2.0-alpha`. Commit the filled-in checklist.",
            pr_step("docs: release-candidate test results (KAR-05)", "JWinborne1"),
        ],
        "files": [], "commands": [],
        "test": "The checklist is filled in for both runs, and every failure has an issue.",
        "why": (
            "The team knows MaxGuard too well to notice what is confusing. An outside tester on a "
            "clean machine finds the missing step, the unclear error, and the assumption that only "
            "works on the developers' laptops, while there is still time to fix them."
        ),
        "checklist": checklist(extra=["Every failure has an issue"]),
    },
    {
        "id": "KAR-06", "owner": "karthik", "milestone": "S4",
        "title": "End-to-end test of the live sensor on the lab",
        "labels": ["area:testing", "area:sensor"], "hardware": True,
        "depends": ["JAK-07"],
        "goal": (
            "Prove the live path works end to end on the reference lab: generate known traffic, "
            "and check that the expected alerts appear on the console within the shipping interval, "
            "with the right devices attributed."
        ),
        "prereq": "JAK-07 (live sensor) is merged and running on the lab.",
        "steps": [
            start_step("karthik/live-e2e"),
            "Create `scripts/live_check.sh`:\n\n@@FILE scripts/live_check.sh@@\n\n"
            "Three choices to notice. It refuses any address outside the lab ranges, because "
            "probing someone else's machine is never acceptable (CLAUDE.md rule 4). It uses "
            "`curl` for the Telnet probe too, so no Telnet client is needed. And it compares the "
            "alert's `last_seen` (the sensor's clock) with the console's clock, so both must keep "
            "the right time (NTP); a Raspberry Pi without a clock battery has the wrong time until "
            "it reaches a time server.",
            "Check the script with ShellCheck, and see it refuse an address outside the lab "
            "before it contacts anything:\n\n@@RUN check@@",
            "On another lab machine, start a test service with Telnet and HTTP. The lab server "
            "from KAR-01 is one: `docker run -d --rm --name lab-service -p 23:23 -p 80:80 "
            "lab-server`. It is insecure on purpose: run it only on the lab network, and stop it "
            "(`docker stop lab-service`) after the test. Plug that machine into a LAN port of "
            "the **router** for the test, not into the switch or the mesh Wi-Fi: the sensor sees "
            "only traffic that crosses the cable on switch port 1 (`docs/HARDWARE.md` section 1), "
            "and traffic between two devices behind the switch never does.",
            "On the console machine (on the mesh Wi-Fi), run the check against the console and "
            "the lab service. The console's API answers only on `127.0.0.1`; sensors use the "
            "separate ingest port:\n\n@@RUN lab@@",
            "Run it three times on different days and record how long each alert took in "
            "`docs/testing/live-sensor.md`.",
            pr_step("test: live-sensor end-to-end check on the lab (KAR-06)", "JWinborne1"),
        ],
        "files": ["scripts/live_check.sh"],
        "commands": [
            {"id": "check", "expect_code": 2, "show": (
                "docker run --rm -v \"$PWD/scripts:/mnt:ro\" koalaman/shellcheck:v0.11.0 "
                "/mnt/live_check.sh && echo \"shellcheck: no findings\"\n"
                "bash scripts/live_check.sh http://127.0.0.1:8000 100.64.0.1"),
             "note": "The second command exits with 2: `100.64.0.1` is not a lab address."},
            {"id": "lab", "env": "none",
             "show": "bash scripts/live_check.sh http://127.0.0.1:8000 192.168.50.30",
             "output": ("sent: plain HTTP request to 172.19.0.2 port 80\n"
                        "sent: Telnet session to 172.19.0.2 port 23\n"
                        "waiting for the alerts (checking every 1 s, for up to 0 min 20 s)\n"
                        "cleartext.telnet alert after 0 min 2 s\n"
                        "cleartext.http alert after 0 min 4 s\n"
                        "PASS: both alerts appeared"),
             "note": ("Not run on the lab: verify on hardware. This output is from planning, "
                      "where the test service was the lab server in a container (172.19.0.2), a "
                      "fake console answered `/api/alerts`, and `LIVE_CHECK_POLL_SECONDS=1` and "
                      "`LIVE_CHECK_TIMEOUT_SECONDS=20` shortened the waits. On the lab, expect "
                      "up to one 15-minute interval plus the analysis time.")},
        ],
        "test": "All three runs show both alerts within one shipping interval plus the analysis time.",
        "why": (
            "Each piece of the live path is unit-tested, but the joints between them (rotation, "
            "shipping, ingest, analysis, dashboard) only break on real hardware. A repeatable "
            "end-to-end check catches those breaks before the v2.0 release."
        ),
        "checklist": checklist(extra=["Only lab machines were contacted",
                                      "The test service was stopped after the test"]),
    },
]
