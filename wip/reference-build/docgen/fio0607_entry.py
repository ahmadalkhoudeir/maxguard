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
