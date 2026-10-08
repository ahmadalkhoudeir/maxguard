    {
        "id": "AHM-07", "owner": "ahmad", "milestone": "S8",
        "title": "Response: block proposals, generated rules, and preview before you block",
        "labels": ["area:response"],
        "depends": ["JAI-06", "JAI-07"],
        "goal": (
            "Let an analyst propose blocking one IP address and see, before anything happens, the "
            "exact firewall commands (with their undo commands) and what the block would have "
            "stopped in the last 7 days (`docs/ARCHITECTURE.md` section 13)."
        ),
        "prereq": "JAI-06 and JAI-07 are merged.",
        "steps": [
            start_step("ahmad/response-generate"),
            "Create `maxguard/response/__init__.py` (one line):\n\n"
            "@@FILE maxguard/response/__init__.py@@\n\n"
            "and `maxguard/response/generate.py`:\n\n@@FILE maxguard/response/generate.py@@\n\n"
            "Four things to notice. `parse_ip()` is the only way an address gets into a "
            "command, and `ipaddress.ip_address()` alone is not enough: it accepts "
            "`2001:db8::1%$(id)` (an IPv6 *scope*, which can hold shell syntax) and plain "
            "integers (`16909060` means `1.2.3.4`), so those are refused too. An nftables set "
            "holds one address family, and a block has a direction, so there are four sets, "
            "created once by `NFT_SETUP`. *Direction* means who starts the connection: "
            "`inbound` blocks connections the address starts, `outbound` blocks connections "
            "your devices start toward it; the rules match conntrack's *original* direction, "
            "so an inbound block still lets your own connections to that address work. And "
            "each `nft` command is one quoted argument, so the shell never reads the braces.",
            "Check the generated commands for real. `nicolaka/netshoot:v0.15` has `nft` and "
            "`iptables`; `--network none` gives the container only its own loopback, so "
            "nothing can leave it. The setup file is loaded twice to show that running it "
            "again never doubles the rules:\n\n@@RUN nft@@",
            "Create `maxguard/response/preview.py`:\n\n@@FILE maxguard/response/preview.py@@\n\n"
            "`window_end` comes from the caller, never from the clock, so the same events "
            "always give the same preview. One connection seen in `conn.log`, `ssl.log` and "
            "`eve.json` counts once (by `community_id`).",
            "Create the tests `tests/unit/test_response_generate.py`:\n\n"
            "@@FILE tests/unit/test_response_generate.py@@\n\n"
            "and `tests/unit/test_response_preview.py`:\n\n"
            "@@FILE tests/unit/test_response_preview.py@@\n\nRun them:\n\n@@RUN tests@@",
            pr_step("feat: block proposals with generated rules and preview (AHM-07)", "JWinborne1"),
        ],
        "files": ["maxguard/response/__init__.py", "maxguard/response/generate.py",
                  "maxguard/response/preview.py", "tests/unit/test_response_generate.py",
                  "tests/unit/test_response_preview.py"],
        "commands": [
            {"id": "nft", "show": (
                "mkdir -p data/nft-check\n"
                "python - <<'EOF'\n"
                "from pathlib import Path\n"
                "from maxguard.response.generate import NFT_SETUP, rules_for\n"
                "Path(\"data/nft-check/maxguard-setup.nft\").write_text(NFT_SETUP)\n"
                "r = rules_for(\"203.0.113.7\", \"both\")\n"
                "commands = (r[\"nftables\"][\"block\"] + r[\"iptables\"][\"block\"]\n"
                "            + [\"nft list set inet maxguard maxguard_block_in_v4 | grep elements\",\n"
                "               \"iptables -S | grep maxguard\"]\n"
                "            + r[\"nftables\"][\"undo\"] + r[\"iptables\"][\"undo\"]\n"
                "            + ['echo \"rules left: $(iptables -S | grep -c maxguard)\"'])\n"
                "# The container runs as root, so sudo is not needed there.\n"
                "Path(\"data/nft-check/run.sh\").write_text(\"\\n\".join(commands).replace(\"sudo \", \"\") + \"\\n\")\n"
                "EOF\n"
                "docker run --rm --network none --cap-add NET_ADMIN --cap-add NET_RAW \\\n"
                "  -v \"$PWD/data/nft-check:/w:ro\" nicolaka/netshoot:v0.15 sh -c '\n"
                "  nft -c -f /w/maxguard-setup.nft && echo \"syntax check: ok\"\n"
                "  nft -f /w/maxguard-setup.nft && nft -f /w/maxguard-setup.nft\n"
                "  echo \"drop rules in input after loading twice: $(nft list chain inet maxguard input | grep -c drop)\"\n"
                "  bash -e /w/run.sh'"),
             "note": ("`nicolaka/netshoot` is for testing only, never shipped "
                      "(`docs/DEPENDENCIES.md`). Not checked here: the older iptables-legacy "
                      "backend, and a real router forwarding traffic (the `forward` chain loads, "
                      "but no routed packets went through it).")},
            {"id": "tests", "show": ("pytest tests/unit/test_response_generate.py "
                                     "tests/unit/test_response_preview.py -q")},
        ],
        "test": "The tests pass, and the nftables commands pass `nft -c`.",
        "why": (
            "Blocking the wrong address can cut off a printer, a phone, or the whole office. "
            "Showing exactly what would have been blocked last week, and the undo command before "
            "the block, is how MaxGuard keeps blocking safe and reversible (CLAUDE.md rule 4)."
        ),
        "checklist": checklist(extra=["A hostile input test exists"]),
    },
    {
        "id": "AHM-08", "owner": "ahmad", "milestone": "S8",
        "title": "Response: approvals, audit, revert, and the OPNsense connector",
        "labels": ["area:response"], "hardware": True,
        "depends": ["AHM-07", "JON-03"],
        "goal": (
            "Add the approval workflow (propose → preview → approve with the IP typed again → "
            "applied → reverted, every step audited) and the first `Enforcer`, which applies an "
            "approved block on an OPNsense firewall through its API."
        ),
        "prereq": ("AHM-07 is merged. For the last step you need an OPNsense test firewall in a "
                   "VM, never a real one."),
        "steps": [
            start_step("ahmad/response-approvals"),
            "Create `maxguard/response/approvals.py`:\n\n"
            "@@FILE maxguard/response/approvals.py@@\n\n"
            "The steps are `proposed → previewed → approved → applied → reverted`, and a "
            "proposed or previewed block can be `rejected`. Approve is allowed only after a "
            "preview, needs the person's name and the IP address typed again, and a refused "
            "approval is audited too. Each check and state change is **one** SQL `UPDATE ... "
            "WHERE state IN (...)`, so two people clicking at the same moment cannot both "
            "approve. The proposals table is created here with `CREATE TABLE IF NOT EXISTS`, so "
            "`storage/state.py` does not change. One gap to know: the state change and its "
            "audit row are two transactions, so a crash between them could lose one audit row; "
            "making them one transaction needs a small new `StateStore` interface (ask Jaiden).",
            "Create the enforcer interface `maxguard/response/enforcers/__init__.py` and "
            "`maxguard/response/enforcers/base.py`:\n\n"
            "@@FILE maxguard/response/enforcers/__init__.py@@\n\n"
            "@@FILE maxguard/response/enforcers/base.py@@\n\n"
            "and the OPNsense client `maxguard/response/enforcers/opnsense.py`:\n\n"
            "@@FILE maxguard/response/enforcers/opnsense.py@@\n\n"
            "The endpoints come from OPNsense's own source code (`opnsense/core`, commit "
            "`1177021c22d6dedb63ff9bffd6300e789a8822e2`, October 6, 2026): `POST "
            "/api/firewall/alias_util/add/<alias>` and `.../delete/<alias>` with "
            "`{\"address\": ip}` (`AliasUtilController.php`; they change the live `pf` table at "
            "once through `pfctl -t <alias> -T add`) and `POST /api/firewall/alias/reconfigure` "
            "(`AliasController.php`, the \"Apply\" step). The key file has `key=` and `secret=` "
            "lines and is sent with HTTP basic auth (OPNsense's API how-to, `api.rst`). The "
            "client accepts only `https://`, always verifies the certificate (your CA file or "
            "the system's), uses short timeouts, follows no redirects, and ignores proxy "
            "settings (`trust_env = False`): the request goes straight to your firewall, and "
            "never toward the blocked address.",
            "Create `maxguard/response/routes.py`, the API under `/api/response`:\n\n"
            "@@FILE maxguard/response/routes.py@@\n\n"
            "`create_app()` (JAI-07) includes this router automatically now that the module "
            "exists. It is part of the dashboard's app on `127.0.0.1` only, never the "
            "ingest-only app that sensors reach. Errors: 400 bad input or a wrong typed IP, 404 "
            "no such proposal, 409 a step that is not allowed now, 502 the firewall refused or "
            "could not be reached.",
            "Create the tests `tests/unit/test_response_approvals.py`:\n\n"
            "@@FILE tests/unit/test_response_approvals.py@@\n\n"
            "`tests/unit/test_opnsense.py` (a fake OPNsense: `http.server` on `127.0.0.1` "
            "wrapped in TLS with a throwaway test CA, so the tests also prove that an untrusted "
            "certificate is refused):\n\n@@FILE tests/unit/test_opnsense.py@@\n\n"
            "and `tests/unit/test_response_routes.py`:\n\n"
            "@@FILE tests/unit/test_response_routes.py@@\n\nRun them:\n\n@@RUN tests@@",
            "Walk through the whole workflow against the API. Start the server in one terminal, "
            "then run the rest in a second one:\n\n@@RUN session@@",
            "**On an OPNsense test VM** (*not run — verify on hardware*; never a real "
            "firewall):\n\n"
            "1. **Firewall > Aliases**: create `maxguard_block_in` and `maxguard_block_out`, "
            "type *Host(s)*, empty.\n"
            "2. **Firewall > Rules > WAN**: a *Block* rule with source `maxguard_block_in`. "
            "**Firewall > Rules > LAN**: a *Block* rule with source `maxguard_block_in` (a "
            "device on your own network) and one with destination `maxguard_block_out`. Apply.\n"
            "3. **System > Access > Users**: a user `maxguard` with only the privileges "
            "*Diagnostics: PF Table IP addresses* and *Firewall: Alias: Edit* (OPNsense's "
            "`ACL.xml`). In its API keys section click **+**; the browser downloads the key "
            "file once.\n"
            "4. On the MaxGuard machine, keep the key in the data folder (never in the "
            "repository) and point MaxGuard at the firewall:\n\n"
            "```bash\n"
            "mkdir -p data/opnsense\n"
            "mv ~/Downloads/<the downloaded key file>.txt data/opnsense/apikey.txt\n"
            "chmod 600 data/opnsense/apikey.txt\n"
            "export MAXGUARD_OPNSENSE_URL=https://fw.home.arpa      # your test firewall\n"
            "export MAXGUARD_OPNSENSE_CA=$PWD/data/opnsense/ca.pem  # if it uses its own CA\n"
            "export MAXGUARD_OFFLINE_ALLOW=fw.home.arpa             # with MAXGUARD_OFFLINE=1\n"
            "```\n\n"
            "5. Repeat the walk-through: `apply` now adds the address to the alias (check "
            "**Firewall > Diagnostics > Aliases**), and `revert` removes it. Without "
            "`MAXGUARD_OFFLINE_ALLOW`, apply answers 502 with the hint to add the firewall "
            "there.",
            pr_step("feat: approvals, audit and OPNsense enforcer (AHM-08)", "JWinborne1"),
        ],
        "files": ["maxguard/response/approvals.py", "maxguard/response/enforcers/__init__.py",
                  "maxguard/response/enforcers/base.py", "maxguard/response/enforcers/opnsense.py",
                  "maxguard/response/routes.py", "tests/unit/test_response_approvals.py",
                  "tests/unit/test_opnsense.py", "tests/unit/test_response_routes.py"],
        "commands": [
            {"id": "tests", "show": ("pytest tests/unit/test_response_approvals.py "
                                     "tests/unit/test_opnsense.py tests/unit/test_response_routes.py -q")},
            {"id": "session", "show": '# terminal 1:\nuvicorn maxguard.api.app:create_app --factory --host 127.0.0.1 --port 8000\n# terminal 2:\npython -c "import shutil; shutil.make_archive(\'data/telnet\', \'zip\', \'tests/fixtures/zeek/telnet\')"\ncurl -s -F file=@data/telnet.zip http://127.0.0.1:8000/api/analyses; echo\npython - <<\'EOF\'\nimport requests\n\nB = "http://127.0.0.1:8000/api/response/proposals"\n\n\ndef step(path, **body):\n    """POST one step and print the answer in one line."""\n    answer = requests.post(B + path, json=body, timeout=60)\n    data = answer.json()\n    print(answer.status_code, data.get("detail") or f"proposal {data[\'proposal_id\']}: {data[\'state\']}")\n    return data\n\n\nstep("", actor="ahmad", ip="1.2.3.4; rm -rf /", direction="both")\np = step("", actor="ahmad", ip="172.18.0.3", direction="both", reason="Telnet client")\nprint("\\n".join(p["rules"]["nftables"]["block"] + p["rules"]["nftables"]["undo"]))\nseen = step("/1/preview", actor="ahmad")["preview"]\nprint("preview:", seen["connections"], "connection(s), devices", seen["devices"],\n      "ports", [s["port"] for s in seen["services"]])\nstep("/1/approve", actor="fiona")                          # the IP was not typed again\nstep("/1/approve", actor="fiona", confirm_ip="172.18.0.3")\nstep("/1/apply", actor="fiona")                            # no firewall connector: by hand\nstep("/1/revert", actor="ahmad")\nfor row in reversed(requests.get("http://127.0.0.1:8000/api/audit", timeout=10).json()):\n    print(row["actor"], row["action"], row["target"])\nEOF', "run": '(uvicorn maxguard.api.app:create_app --factory --host 127.0.0.1 --port 18000 > /tmp/ahm08-uvicorn.log 2>&1 & echo $! > /tmp/ahm08-uvicorn.pid)\nfor i in $(seq 1 50); do curl -s -o /dev/null http://127.0.0.1:18000/docs && break; sleep 0.2; done\npython -c "import shutil; shutil.make_archive(\'data/telnet\', \'zip\', \'tests/fixtures/zeek/telnet\')"\ncurl -s -F file=@data/telnet.zip http://127.0.0.1:18000/api/analyses; echo\npython - <<\'EOF\'\nimport requests\n\nB = "http://127.0.0.1:18000/api/response/proposals"\n\n\ndef step(path, **body):\n    """POST one step and print the answer in one line."""\n    answer = requests.post(B + path, json=body, timeout=60)\n    data = answer.json()\n    print(answer.status_code, data.get("detail") or f"proposal {data[\'proposal_id\']}: {data[\'state\']}")\n    return data\n\n\nstep("", actor="ahmad", ip="1.2.3.4; rm -rf /", direction="both")\np = step("", actor="ahmad", ip="172.18.0.3", direction="both", reason="Telnet client")\nprint("\\n".join(p["rules"]["nftables"]["block"] + p["rules"]["nftables"]["undo"]))\nseen = step("/1/preview", actor="ahmad")["preview"]\nprint("preview:", seen["connections"], "connection(s), devices", seen["devices"],\n      "ports", [s["port"] for s in seen["services"]])\nstep("/1/approve", actor="fiona")                          # the IP was not typed again\nstep("/1/approve", actor="fiona", confirm_ip="172.18.0.3")\nstep("/1/apply", actor="fiona")                            # no firewall connector: by hand\nstep("/1/revert", actor="ahmad")\nfor row in reversed(requests.get("http://127.0.0.1:18000/api/audit", timeout=10).json()):\n    print(row["actor"], row["action"], row["target"])\nEOF\nkill $(cat /tmp/ahm08-uvicorn.pid)',
             "note": ("The analysis ID depends on the moment of the upload, so yours differs. "
                      "The preview counts only the 7 days before now: the fixture's traffic is "
                      "from October 6, 2026, so on a later date your preview shows 0 "
                      "connections. `apply` records a block made by hand because no firewall "
                      "connector is configured.")},
        ],
        "test": "The tests pass, and on a test OPNsense VM an approved block and its revert work.",
        "why": (
            "Typing the address again is a deliberate speed bump: it makes the person read what "
            "they are about to block. The audit trail and revert make every block accountable "
            "and reversible, and testing against a fake server means no test can ever change a "
            "real firewall."
        ),
        "checklist": checklist(extra=["No test talks to a real firewall",
                                      "The API key is read from the data folder"]),
    },
