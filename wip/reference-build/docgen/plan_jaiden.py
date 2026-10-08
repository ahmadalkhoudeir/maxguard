"""Jaiden's tasks: repository, contracts, pipeline, data layer, API, packaging, releases."""

from plan_helpers import checklist, pr_step, start_step

# actionlint 1.7.12 from actionlint-py==1.7.12.25, installed once in the planning sandbox.
SCRATCH_ACTIONLINT = "/tmp/claude-0/-home-user-maxguard/d28fe4b6-2c9f-5cd0-8e7f-d2be65aa4c01/scratchpad/jaiden-actionlint/bin/actionlint"

TASKS = [
    {
        "id": "JAI-01", "owner": "jaiden", "milestone": "W0",
        "title": "Restructure the repository, add packaging and CI",
        "labels": ["area:release", "critical-path"],
        "depends": [],
        "goal": (
            "Turn the v0.8 repository into the v2.0 layout: old code moves to `legacy/`, a "
            "`pyproject.toml` makes `pip install -e .` work for everyone, and GitHub Actions runs "
            "the linter and the tests on every pull request. Every other task builds on this one."
        ),
        "prereq": "Your Week 0 onboarding is done. Nothing else: this is the first task in the roadmap.",
        "steps": [
            start_step("jaiden/restructure"),
            "Move the v0.8 code into `legacy/` so nothing is lost (it is deleted at the feature "
            "freeze; the `v0.8.0-Spring2026` tag also keeps it forever):\n\n"
            "```bash\nmkdir legacy\n"
            "git mv scanner analyzer dashboard reports config .launch .version \"Voice Module\" "
            "Dockerfile requirements.txt .streamlit .devcontainer .dockerignore legacy/\n"
            "git status --short | head\n```\n\n"
            "Expected: lines starting with `R ` (renamed), for example `R  scanner/sniffer.py -> legacy/scanner/sniffer.py`.",
            "Create the package folders. In VS Code, create these two files (folders are created "
            "for you when you type the path):\n\n`maxguard/__init__.py`:\n\n@@FILE maxguard/__init__.py@@\n\n"
            "`cli/__init__.py`:\n\n@@FILE cli/__init__.py@@",
            "Create `pyproject.toml` in the repository root. It names the package, its "
            "dependencies with the versions MaxGuard was tested with, the `maxguard` command, "
            "the files that are not Python but must be installed, and the settings for Ruff "
            "and pytest:\n\n@@FILE pyproject.toml@@",
            "Create the shared test helpers `tests/conftest.py` (pytest loads it automatically):\n\n"
            "@@FILE tests/conftest.py@@\n\nand the first test, `tests/unit/test_package.py`:\n\n"
            "@@FILE tests/unit/test_package.py@@",
            "Create the CI workflow `.github/workflows/ci.yml`:\n\n@@FILE .github/workflows/ci.yml@@",
            "Make a virtual environment and install MaxGuard with the developer tools. Do this "
            "once; afterwards only `source .venv/bin/activate` in each new terminal:\n\n"
            "```bash\npython3.11 -m venv .venv\nsource .venv/bin/activate\n"
            "pip install --upgrade pip\npip install -e \".[dev]\"\n```\n\n"
            "Expected: the last line starts with `Successfully installed` and lists `maxguard-2.0.0a0`.",
            "Run the two checks CI will run:\n\n@@RUN lint@@\n\n@@RUN tests@@",
            pr_step("chore: restructure repo, add pyproject and CI (JAI-01)", "ahmadalkhoudeir"),
            "**After the pull request is merged**, protect `main` (you need admin rights; ask Ahmad "
            "if you do not have them). On github.com open **Settings → Rules → Rulesets → New "
            "ruleset → New branch ruleset**:\n\n"
            "| Field | Value |\n|---|---|\n"
            "| Ruleset name | `main-protection` |\n| Enforcement status | **Active** |\n"
            "| Target branches | **Add target → Include default branch** |\n"
            "| Rules | tick **Restrict deletions**, **Block force pushes**, **Require a pull request "
            "before merging** (Required approvals: **1**), and **Require status checks to pass** "
            "→ **Add checks** → type `test` and pick the check from GitHub Actions |\n\n"
            "Click **Create**. *Not run here — verify on github.com.* (The `test` check appears in "
            "the list only after CI has run once, which is why this comes after the merge.)",
        ],
        "files": [
            ("maxguard/__init__.py", "maxguard/__init__.py"), "cli/__init__.py",
            "pyproject.toml", ("tests/conftest.py", "snip:conftest_v1.py"), "tests/unit/test_package.py",
            (".github/workflows/ci.yml", "snip:ci_w0.yml"), (".gitignore", "snip:gitignore"),
        ],
        "commands": [
            {"id": "lint", "show": "ruff check ."},
            {"id": "tests", "show": 'pytest -m "not integration" -q'},
        ],
        "test": (
            "Both commands above print what is shown. Then open your pull request on GitHub: the "
            "**Checks** tab shows the `test` job with a green tick within about two minutes. "
            "`pytest` printing `1 passed` means the package imports and the test setup works."
        ),
        "why": (
            "A Python *package* (`maxguard/` with an `__init__.py`) lets every module import every "
            "other with `from maxguard.x import y`. `pyproject.toml` is the one place that lists "
            "dependencies, so `pip install -e .` gives everyone the same setup; `-e` (editable) "
            "means your code changes take effect without reinstalling. CI runs the same two "
            "commands on a clean machine for every pull request, so \"it works on my laptop\" is "
            "never enough. Branch protection makes the rule *at least one review and green CI* "
            "impossible to skip, even for the leads."
        ),
        "checklist": checklist(extra=[
            "`git status` shows the old folders under `legacy/` (moved, not deleted)",
            "The `test` job is green on the pull request",
            "After merging: the `main-protection` ruleset is active",
        ]),
    },
    {
        "id": "JAI-02", "owner": "jaiden", "milestone": "W0",
        "title": "Merge the three contracts in their v2.0 form",
        "labels": ["area:engine", "critical-path", "contract-change"],
        "depends": ["JAI-01"],
        "goal": (
            "Add the code everyone else builds against: Contract 1 (the `Finding` dataclass), the "
            "record and finding IDs, Contract 3 (the input adapter protocol), the rule registry, and "
            "Contract 2's loader for the mapping files. `docs/ARCHITECTURE.md` section 5 explains "
            "every extension; the original Fall 2026 code keeps working unchanged."
        ),
        "prereq": "JAI-01 is merged. Read `docs/ARCHITECTURE.md` sections 5 and 7 first (15 minutes).",
        "steps": [
            start_step("jaiden/contracts-v2"),
            "Create `maxguard/models.py` (Contract 1):\n\n@@FILE maxguard/models.py@@",
            "Create `maxguard/ids.py` (stable IDs for log records):\n\n@@FILE maxguard/ids.py@@",
            "Create an **empty** file `maxguard/adapters/__init__.py`, then "
            "`maxguard/adapters/base.py` (Contract 3):\n\n@@FILE maxguard/adapters/base.py@@",
            "Create the rule registry: `maxguard/rules/__init__.py`\n\n@@FILE maxguard/rules/__init__.py@@\n\n"
            "and `maxguard/rules/base.py`:\n\n@@FILE maxguard/rules/base.py@@",
            "Create an **empty** file `maxguard/mapping/__init__.py`, then the Contract 2 loader "
            "`maxguard/mapping/loader.py`:\n\n@@FILE maxguard/mapping/loader.py@@",
            "Create the tests `tests/unit/test_contracts.py`:\n\n@@FILE tests/unit/test_contracts.py@@",
            "Run them:\n\n@@RUN tests@@",
            pr_step("feat: contracts v2.0 - Finding, IDs, adapter protocol, registry, loader (JAI-02)",
                    "ahmadalkhoudeir"),
            "Announce the merge in GitHub Discussions (category **Announcements**, title "
            "`Contracts v2.0 merged`) with a link to `docs/ARCHITECTURE.md` section 5. From now "
            "on, a contract change needs a pull request with the `contract-change` label, "
            "reviewed by you and approved by Ahmad.",
        ],
        "files": [
            "maxguard/models.py", "maxguard/ids.py", "maxguard/adapters/__init__.py",
            "maxguard/adapters/base.py", ("maxguard/rules/__init__.py", "snip:rules_init_v0.py"),
            "maxguard/rules/base.py", "maxguard/mapping/__init__.py", "maxguard/mapping/loader.py",
            "tests/unit/test_contracts.py",
        ],
        "commands": [
            {"id": "tests", "show": "pytest tests/unit/test_contracts.py -q"},
        ],
        "test": (
            "`14 passed` means: the original Fall 2026 way of creating a `Finding` still works, "
            "IDs are stable, a misspelled severity fails at once, Suricata's random `flow_id` does "
            "not change a record ID, and mapping files fill both controls and ATT&CK techniques. "
            "Also run `ruff check .` (must print `All checks passed!`)."
        ),
        "why": (
            "Eight people write code in parallel. If the shape of a finding changed every week, "
            "every module would break every week. Freezing these few files first lets everyone "
            "work against the same definitions from day one. The v2.0 additions all have default "
            "values, so code written for the Fall 2026 roadmap (and the code in the archived "
            "roadmap) still runs. The IDs are hashes of content, not counters or random numbers, "
            "so the same capture always produces the same IDs — the AI cites them and the alert "
            "queue tracks them (CLAUDE.md rules 2 and 3)."
        ),
        "checklist": checklist(extra=[
            "The pull request has the `contract-change` label and Ahmad's approval",
            "Announcement posted in Discussions",
        ]),
    },
    {
        "id": "JAI-05", "owner": "jaiden", "milestone": "W2",
        "title": "The pipeline: one function from input to report",
        "labels": ["area:engine", "critical-path"],
        "depends": ["FIO-01", "FIO-02", "JAK-03", "JAI-03", "JAK-04", "AMO-01"],
        "goal": (
            "Write `maxguard/pipeline.py`, the single function the CLI, the API, and the tests call: "
            "it picks the right adapter, gets Zeek logs, runs the rules, applies the mapping files, "
            "builds the event list and the asset inventory, asks the local AI (when asked to), and "
            "returns the report dictionary described in `docs/ARCHITECTURE.md` section 8."
        ),
        "prereq": "FIO-01 (adapters), FIO-02 and JAK-03 (rules), JAI-03 (normalizer), JAK-04 "
                  "(inventory) and AMO-01 (mapping files) are merged.",
        "steps": [
            start_step("jaiden/pipeline"),
            "Create `maxguard/pipeline.py`:\n\n@@FILE maxguard/pipeline.py@@\n\n"
            "Two details to notice: the AI client is imported *inside* `if explain:`, so the pipeline "
            "works before JON-02 is merged as long as you pass `explain=False`; and the mapping "
            "folder comes from `MAXGUARD_MAPPINGS_DIR` (set in the Docker image) or the repository's "
            "`mappings/` folder, and a missing folder is an error instead of silently mapping nothing.",
            "Create the tests `tests/unit/test_pipeline.py`:\n\n@@FILE tests/unit/test_pipeline.py@@",
            "Run them:\n\n@@RUN tests@@",
            "Try it yourself on a fixture folder (Zeek-log input needs no Zeek):\n\n@@RUN try@@",
            pr_step("feat: pipeline.analyze from input to report (JAI-05)", "ahmadalkhoudeir"),
        ],
        "files": [("maxguard/pipeline.py", "snip:pipeline_v1.py"),
                  ("tests/unit/test_pipeline.py", "snip:test_pipeline_v1.py")],
        "commands": [
            {"id": "tests", "show": "pytest tests/unit/test_pipeline.py -q"},
            {"id": "try", "show": (
                "python -c \"from maxguard.pipeline import analyze; import json, tempfile; "
                "r = analyze('tests/fixtures/zeek/telnet', tempfile.mkdtemp(), explain=False); "
                "print(json.dumps([(f['rule_id'], f['dst_port'], [c['control_id'] for c in f['controls']]) "
                "for f in r['findings']]))\"")},
        ],
        "test": "`pytest tests/unit/test_pipeline.py -q` passes, and the one-liner prints the "
                "Telnet finding with its NIST controls.",
        "why": (
            "If the CLI, the API, and the tests each had their own copy of these steps, they would "
            "drift apart and a bug fixed in one place would stay in the others. One function means "
            "one behavior. The report has no \"generated at\" time on purpose: the same input must "
            "produce the identical report (CLAUDE.md rule 2); the API records *when* it received "
            "an upload separately."
        ),
        "checklist": checklist(),
    },
    {
        "id": "JAI-03", "owner": "jaiden", "milestone": "W1",
        "title": "Common event schema: the normalizer and record lookup",
        "labels": ["area:engine", "area:storage", "critical-path"],
        "depends": ["JAI-02", "KAR-02", "FIO-01", "FIO-02", "JAK-03"],
        "goal": (
            "Turn Zeek logs and Suricata's `eve.json` into one list of events with the same keys, "
            "whatever tool wrote them (`docs/ARCHITECTURE.md` section 6), and find the raw log "
            "records behind evidence IDs so the AI can show them to the model."
        ),
        "prereq": "JAI-02, KAR-02 (fixtures) and FIO-01 (the log adapter) are merged; the lookup "
                  "test uses the rules from FIO-02 and JAK-03.",
        "steps": [
            start_step("jaiden/event-schema"),
            "Create `maxguard/events/__init__.py`:\n\n@@FILE maxguard/events/__init__.py@@\n\n"
            "then `maxguard/events/normalize.py`:\n\n@@FILE maxguard/events/normalize.py@@",
            "Create `maxguard/events/lookup.py`:\n\n@@FILE maxguard/events/lookup.py@@",
            "Create the tests `tests/unit/test_normalize.py`:\n\n@@FILE tests/unit/test_normalize.py@@\n\n"
            "and `tests/unit/test_lookup.py`:\n\n@@FILE tests/unit/test_lookup.py@@",
            "Run them:\n\n@@RUN tests@@",
            pr_step("feat: common event schema normalizer and record lookup (JAI-03)", "ahmadalkhoudeir"),
        ],
        "files": ["maxguard/events/__init__.py", ("maxguard/events/normalize.py", "snip:normalize_v1.py"),
                  "maxguard/events/lookup.py", "tests/unit/test_normalize.py",
                  "tests/unit/test_lookup.py"],
        "commands": [
            {"id": "tests", "show": "pytest tests/unit/test_normalize.py tests/unit/test_lookup.py -q"},
        ],
        "test": "Both test files pass. The normalizer tests cover every lab capture, DNS and DHCP "
                "records, Suricata 7 and 8 DNS formats, and TSV-converted logs.",
        "why": (
            "The timeline, the event store, preview-before-you-block, and the inventory all need "
            "\"what happened on the network\" in one shape. Without a common schema each of them "
            "would have to know both Zeek's and Suricata's field names. Copying `community_id` from "
            "`conn.log` to the other Zeek events is what lets a Zeek event and a Suricata event about "
            "the same connection be shown together."
        ),
        "checklist": checklist(extra=["A change to `EVENT_KEYS` is a contract change (label it)"]),
    },
    {
        "id": "JAI-06", "owner": "jaiden", "milestone": "W3",
        "title": "Storage: alerts in SQLite, events in hourly Parquet files",
        "labels": ["area:storage", "critical-path"],
        "depends": ["JAI-03"],
        "goal": (
            "Keep what the dashboard needs after an upload: `StateStore` (one SQLite file: analyses, "
            "alerts with status and assignee, and the audit trail) and `EventStore` (normalized "
            "events in one Parquet file per hour, queried with DuckDB). See `docs/ARCHITECTURE.md` "
            "section 9."
        ),
        "prereq": "JAI-03 is merged.",
        "steps": [
            start_step("jaiden/storage"),
            "Create `maxguard/storage/__init__.py`:\n\n@@FILE maxguard/storage/__init__.py@@",
            "Create `maxguard/storage/state.py`:\n\n@@FILE maxguard/storage/state.py@@",
            "Create `maxguard/storage/events.py`:\n\n@@FILE maxguard/storage/events.py@@",
            "Create the tests `tests/unit/test_state_store.py`:\n\n@@FILE tests/unit/test_state_store.py@@\n\n"
            "`tests/unit/test_state_store_recurrence.py`:\n\n@@FILE tests/unit/test_state_store_recurrence.py@@\n\n"
            "and `tests/unit/test_event_store.py`:\n\n@@FILE tests/unit/test_event_store.py@@",
            "Run them:\n\n@@RUN tests@@",
            "Look inside the event store with DuckDB's own Python API (handy for debugging):\n\n@@RUN peek@@",
            pr_step("feat: StateStore (SQLite) and EventStore (Parquet + DuckDB) (JAI-06)", "ahmadalkhoudeir"),
        ],
        "files": ["maxguard/storage/__init__.py", "maxguard/storage/state.py",
                  "maxguard/storage/events.py", "tests/unit/test_state_store.py",
                  "tests/unit/test_state_store_recurrence.py", "tests/unit/test_event_store.py"],
        "commands": [
            {"id": "tests", "show": ("pytest tests/unit/test_state_store.py "
                                     "tests/unit/test_state_store_recurrence.py "
                                     "tests/unit/test_event_store.py -q")},
            {"id": "peek", "show": (
                "python -c \"import tempfile; from pathlib import Path; "
                "from maxguard.events.normalize import normalize; "
                "from maxguard.storage.events import EventStore; "
                "store = EventStore(Path(tempfile.mkdtemp())); "
                "print(store.write(normalize(Path('tests/fixtures/zeek/telnet'), 'pcap')), 'events written'); "
                "[print(e['kind'], e['src_ip'], '->', e['dst_ip'], e['dst_port'], e['summary']) "
                "for e in store.query(limit=5)]\"")},
        ],
        "test": "All three test files pass. The recurrence tests prove two promises: uploading the "
                "same file twice does not double the counts, and a resolved alert that comes back "
                "with newer evidence is reopened and audited.",
        "why": (
            "SQLite is good at many small updates (\"set this alert to investigating\") and WAL mode "
            "lets the dashboard read while an upload is being saved. Parquet + DuckDB is good at "
            "scanning a week of events quickly (preview before you block). Hourly folders make "
            "the 7-day retention a matter of deleting old folders instead of rewriting a database, "
            "which also spares the Raspberry Pi's storage. The stores never read the clock; the "
            "caller passes every time in, which keeps tests exact."
        ),
        "checklist": checklist(),
    },
    {
        "id": "JAI-08", "owner": "jaiden", "milestone": "W5",
        "title": "Ed25519 signing library",
        "labels": ["area:release"],
        "depends": ["JAI-01"],
        "goal": (
            "Provide `generate_keypair`, `sign`, and `verify` with Ed25519 signatures, used by the "
            "chain-of-custody log (AMO-05) and the signed intel bundles (JAI-11)."
        ),
        "prereq": "JAI-01 is merged.",
        "steps": [
            start_step("jaiden/signing"),
            "Create `maxguard/custody/__init__.py`:\n\n@@FILE maxguard/custody/__init__.py@@\n\n"
            "and `maxguard/custody/signing.py`:\n\n@@FILE maxguard/custody/signing.py@@",
            "Create the tests `tests/unit/test_signing.py`:\n\n@@FILE tests/unit/test_signing.py@@",
            "Run them:\n\n@@RUN tests@@",
            pr_step("feat: Ed25519 signing helpers (JAI-08)", "ahmadalkhoudeir"),
        ],
        "files": ["maxguard/custody/__init__.py", "maxguard/custody/signing.py",
                  "tests/unit/test_signing.py"],
        "commands": [{"id": "tests", "show": "pytest tests/unit/test_signing.py -q"}],
        "test": "The tests sign data, verify it, and prove that changing one byte, using the wrong "
                "key, or a damaged signature all fail verification.",
        "why": (
            "A hash proves a file did not change *if* you trust where the hash came from. A "
            "signature also proves *who* wrote it: only the holder of the private key can make a "
            "signature that the public key accepts. Ed25519 keys are small and fast, and the "
            "`cryptography` library (Apache-2.0/BSD) is the standard way to use them in Python. "
            "Private keys live in the data folder, never in the repository (CLAUDE.md rule 6)."
        ),
        "checklist": checklist(extra=["No key file is committed (`git status` shows none)"]),
    },
    {
        "id": "JAI-04", "owner": "jaiden", "milestone": "W1",
        "title": "The engine image and the Compose files",
        "labels": ["area:release", "critical-path"], "status": "written",
        "depends": ["JAI-01", "AMO-01"],
        "goal": (
            "Package MaxGuard as a Docker image built on the official Zeek 9.0.0 image, with "
            "Suricata, MaxGuard in a virtual environment, and a non-root user, plus the Compose "
            "files that run it next to a local Ollama. Integration tests (KAR-03), the Week 2 demo "
            "with a capture, and the offline bundle all use this image."
        ),
        "prereq": "JAI-01 and AMO-01 (the Dockerfile copies `mappings/`) are merged.",
        "steps": [
            start_step("jaiden/docker-image"),
            "Create `docker/Dockerfile`:\n\n@@FILE docker/Dockerfile@@\n\n"
            "Three stages share one base: `engine` (everything), `test` (adds pytest and the "
            "tests; CI uses it), and `runtime` (the default; starts the API from JAI-07 — until "
            "then, use the image for `maxguard analyze`, `zeek` and `suricata`).",
            "Create `.dockerignore` in the repository root (it keeps secrets and data out of every "
            "image):\n\n@@FILE .dockerignore@@",
            "Create `docker/compose.yaml`:\n\n@@FILE docker/compose.yaml@@\n\n"
            "and the development overlay `docker/compose.dev.yaml`:\n\n@@FILE docker/compose.dev.yaml@@",
            "Check that both Compose files are valid:\n\n@@RUN compose@@",
            "Build the image and check the tools inside it, with the network off:\n\n@@RUN build@@",
            pr_step("feat: engine image (Zeek, Suricata, MaxGuard) and Compose files (JAI-04)",
                    "ahmadalkhoudeir"),
        ],
        "files": ["docker/Dockerfile", ".dockerignore", "docker/compose.yaml", "docker/compose.dev.yaml"],
        "commands": [
            {"id": "compose", "show": (
                "docker compose -f docker/compose.yaml config --quiet && echo \"compose.yaml OK\"\n"
                "docker compose -f docker/compose.yaml -f docker/compose.dev.yaml config --quiet "
                "&& echo \"compose.dev.yaml OK\"")},
            {"id": "build", "env": "none", "show": (
                "docker build -f docker/Dockerfile -t maxguard:dev .\n"
                "docker run --rm --network none maxguard:dev zeek --version\n"
                "docker run --rm --network none maxguard:dev suricata -V\n"
                "docker run --rm --network none maxguard:dev python -c \"import maxguard; print(maxguard.__version__)\""),
             "output": "zeek version 9.0.0\nThis is Suricata version 7.0.10 RELEASE\n2.0.0a0",
             "note": ("Not run in planning: the build installs Debian packages, and Debian's servers "
                      "were unreachable there. The expected lines are the versions the image is "
                      "pinned to; if your build fails, post the last 30 lines in Discussions.")},
        ],
        "test": "Both Compose files print `OK`; the image prints the three versions with "
                "`--network none`. Also check `docker run --rm maxguard:dev id` shows uid 10001.",
        "why": (
            "Zeek and Suricata are hard to install the same way on Windows, macOS and Linux; one "
            "image gives every laptop, CI and the release the same tools. Starting from the Zeek "
            "project's own image avoids compiling Zeek. A non-root user limits the damage if a "
            "malicious capture ever exploited a parser, and the dashboard port is published on "
            "`127.0.0.1` only, so other machines on the network cannot reach it."
        ),
        "checklist": checklist(extra=["The image builds on your machine and runs as uid 10001"]),
    },
    {
        "id": "JAI-07", "owner": "jaiden", "milestone": "W3",
        "title": "The API: uploads, alerts, events, live updates, sensor ingest",
        "labels": ["area:api", "critical-path"],
        "depends": ["JAI-05", "JAI-06", "JON-03"],
        "goal": (
            "Write `maxguard/api/app.py` with `create_app(data_dir=None, *, explain=True)`: the "
            "JSON API in `docs/ARCHITECTURE.md` section 10 that the dashboard, the sensors, and the "
            "host agent use. Uploads run the pipeline and are saved to the two stores; the API is "
            "the only part of MaxGuard that reads the clock."
        ),
        "prereq": "JAI-05 (pipeline), JAI-06 (storage) and JON-03 (the offline guard, which "
                  "`create_app()` switches on when `MAXGUARD_OFFLINE=1`) are merged.",
        "steps": [
            start_step("jaiden/api"),
            "Let the pipeline name where data came from. In `maxguard/pipeline.py`, give "
            "`analyze()` one more optional argument and use it for the events (the default keeps "
            "`pcap` and `import`, so nothing else changes):\n\n"
            "```python\n"
            "def analyze(path, workdir, frameworks=None, explain=True, mapping_dir=None,\n"
            "            sensor_id=None) -> dict:\n"
            "    ...\n"
            "    if sensor_id is None:\n"
            "        sensor_id = \"pcap\" if adapter.name == \"pcap\" else \"import\"\n"
            "    events = normalize(log_dir, sensor_id=sensor_id)\n"
            "```\n\n"
            "Add a sentence to its docstring: the API passes the sensor's name for data that a "
            "sensor or host agent sent to `POST /api/ingest`.",
            "Create an empty `maxguard/api/__init__.py` and `maxguard/api/app.py`:\n\n"
            "@@FILE maxguard/api/app.py@@\n\n"
            "What to notice, top to bottom:\n\n"
            "- `create_app()` keeps the stores on `app.state`, so the dashboard (AHM-02) and the "
            "response module (AHM-08) reach them through `request.app.state`. Their routers are "
            "included only when their modules exist (`optional_module`); a module that exists but "
            "has a bug still fails loudly.\n"
            "- An upload is saved under a random name, and its suffix comes from the file's first "
            "bytes, never from the client's file name. The client's name is cleaned and only "
            "shown, never used as a path.\n"
            "- The size limit is checked twice: from the `Content-Length` header before the body "
            "is read, and while copying (a client can leave the header out).\n"
            "- `POST /api/ingest` checks the token **before** it reads the body, so a stranger "
            "cannot make the console store anything; `hmac.compare_digest` takes the same time "
            "however many characters match. A token shorter than 32 characters stops the app at "
            "start-up.\n"
            "- `create_ingest_app()` builds a second, tiny app with nothing but "
            "`POST /api/ingest` (no dashboard, no `/docs` page). JAK-07 publishes it on the "
            "console's LAN address, port 8001, for sensors and host agents; the full app stays "
            "on `127.0.0.1`, so nobody on the network can read alerts or approve a block. Both "
            "apps share the data folder; the dashboard shows ingested data at its next refresh.\n"
            "- Browsers let any website *send* a form to `127.0.0.1`. `refuse_cross_site_changes` "
            "refuses changing requests that a browser marks as coming from another site "
            "(cross-site request forgery). curl, sensors and tests send no `Origin` header and "
            "are not affected.\n"
            "- A website can also point its own name at `127.0.0.1` after its page has loaded "
            "(DNS rebinding). The browser then treats the API as part of that website, and the "
            "cross-site check cannot tell. `TrustedHostMiddleware` (from Starlette, which FastAPI "
            "is built on) answers `400 Invalid host header` unless the `Host` header names this "
            "machine or an address in `MAXGUARD_ALLOWED_HOSTS`. When sensors or agents send to "
            "the console over the LAN, add the console's LAN address there.\n"
            "- `GET /api/stream` sends one `alerts-changed` at once (a dashboard that reconnects "
            "may have missed a change), then one per change, with a `: keep-alive` comment every "
            "15 seconds.",
            "FastAPI's `TestClient` calls the app `testserver`, a name the host check refuses. "
            "Add this fixture at the end of `tests/conftest.py` (`autouse=True` gives it to "
            "every test without asking):\n\n"
            "```python\n"
            "@pytest.fixture(autouse=True)\n"
            "def allow_test_client_host(monkeypatch):\n"
            "    \"\"\"The API answers only host names in MAXGUARD_ALLOWED_HOSTS (JAI-07), and FastAPI's\n"
            "    TestClient calls the app \"testserver\". autouse: every test gets it without asking.\"\"\"\n"
            "    monkeypatch.setenv(\"MAXGUARD_ALLOWED_HOSTS\", \"testserver,localhost,127.0.0.1,[::1]\")\n"
            "```",
            "Create the unit tests `tests/unit/test_api.py`:\n\n@@FILE tests/unit/test_api.py@@",
            "Run them:\n\n@@RUN tests@@",
            "Create the integration test `tests/integration/test_api_upload.py`, which uploads a "
            "real capture, so Zeek runs:\n\n@@FILE tests/integration/test_api_upload.py@@\n\n"
            "Run it in the test image from JAI-04 (rebuild the image first: it copies the tests "
            "folder):\n\n@@RUN integration@@",
            "Start the API and try it with curl. Start the server in one terminal, then run the "
            "rest in a second terminal from the repository root (on Windows use Git Bash):\n\n"
            "@@RUN run@@\n\n"
            "Open http://127.0.0.1:8000/docs: FastAPI's OpenAPI page lists every endpoint, and "
            "it is the API contract for the dashboard. Stop the server with Ctrl+C.",
            pr_step("feat: FastAPI app with uploads, alerts, events, SSE and ingest (JAI-07)",
                    "ahmadalkhoudeir"),
        ],
        "files": [("maxguard/pipeline.py", "snip:pipeline_v2.py"), "maxguard/api/__init__.py",
                  ("maxguard/api/app.py", "snip:api_app_v1.py"), "tests/unit/test_api.py",
                  "tests/integration/test_api_upload.py", "tests/conftest.py"],
        "commands": [
            {"id": "tests", "show": "pytest tests/unit/test_api.py -q"},
            {"id": "integration", "env": "zeek",
             "show": ("docker build -f docker/Dockerfile --target test -t maxguard:test .\n"
                      "docker run --rm --network none maxguard:test "
                      "pytest -m integration tests/integration/test_api_upload.py -q"),
             "run": ("python3 -m pytest -m integration tests/integration/test_api_upload.py -q "
                     "-p no:cacheprovider"),
             "note": ("Run in planning inside `zeek/zeek:9.0.0` with MaxGuard's Python packages "
                      "added, because the engine image build needs Debian's package servers "
                      "(see JAI-04). The test output is the same.")},
            {"id": "run",
             "show": ("# terminal 1:\n"
                      "uvicorn maxguard.api.app:create_app --factory --host 127.0.0.1 --port 8000\n"
                      "# terminal 2:\n"
                      "python -c \"import shutil; shutil.make_archive('data/telnet', 'zip', "
                      "'tests/fixtures/zeek/telnet')\"\n"
                      "curl -s -F file=@data/telnet.zip http://127.0.0.1:8000/api/analyses; echo\n"
                      "curl -s http://127.0.0.1:8000/api/alerts | python -c \"import json, sys; "
                      "[print(a['rule_id'], a['severity'], a['src_ip'], '->', a['dst_ip'], "
                      "a['dst_port'], a['status']) for a in json.load(sys.stdin)]\"\n"
                      "curl -s -o /dev/null -w '%{http_code}\\n' -F file=@data/telnet.zip "
                      "http://127.0.0.1:8000/api/ingest"),
             "run": ("(uvicorn maxguard.api.app:create_app --factory --host 127.0.0.1 --port 18000 "
                     "> /tmp/jai07-uvicorn.log 2>&1 & echo $! > /tmp/jai07-uvicorn.pid)\n"
                     "for i in $(seq 1 50); do curl -s -o /dev/null http://127.0.0.1:18000/docs "
                     "&& break; sleep 0.2; done\n"
                     "python -c \"import shutil; shutil.make_archive('data/telnet', 'zip', "
                     "'tests/fixtures/zeek/telnet')\"\n"
                     "curl -s -F file=@data/telnet.zip http://127.0.0.1:18000/api/analyses; echo\n"
                     "curl -s http://127.0.0.1:18000/api/alerts | python -c \"import json, sys; "
                     "[print(a['rule_id'], a['severity'], a['src_ip'], '->', a['dst_ip'], "
                     "a['dst_port'], a['status']) for a in json.load(sys.stdin)]\"\n"
                     "curl -s -o /dev/null -w '%{http_code}\\n' -F file=@data/telnet.zip "
                     "http://127.0.0.1:18000/api/ingest\n"
                     "kill $(cat /tmp/jai07-uvicorn.pid)"),
             "note": ("The analysis ID depends on the moment of the upload, so yours differs. "
                      "The last line is `404`: ingest is off because `MAXGUARD_INGEST_TOKEN` is "
                      "not set.")},
        ],
        "test": (
            "The unit tests and the integration test pass, and the manual run shows the Telnet "
            "alert from the uploaded zip in `/api/alerts`."
        ),
        "why": (
            "The engine never reads the clock and never writes to storage; the API does both, in "
            "one place, which keeps the engine deterministic and easy to test. Generated file "
            "names, the upload limit, the token check before the body is read, and the "
            "cross-site check close the obvious ways a hostile client could attack the console "
            "(`docs/ARCHITECTURE.md` section 14)."
        ),
        "checklist": checklist(extra=["The client's file name is never used as a path",
                                      "Ingest is off unless the token is set"]),
    },
    {
        "id": "JAI-09", "owner": "jaiden", "milestone": "W6",
        "title": "Release workflow and v2.0-alpha-rc1",
        "labels": ["area:release", "critical-path"], "hardware": True,
        "depends": ["JAI-04", "KAR-04", "JON-05"],
        "goal": (
            "Add `.github/workflows/release.yml`: when a tag `v*` is pushed, build the image for "
            "`linux/amd64` and `linux/arm64`, push it to the GitHub Container Registry, and create "
            "a GitHub Release with the small bundle files and a `SHA256SUMS` file. Then tag "
            "`v2.0-alpha-rc1` and attach the offline bundle."
        ),
        "prereq": "JAI-04, KAR-04 and JON-05 are merged, and every W5 issue is closed or moved.",
        "steps": [
            start_step("jaiden/release-workflow"),
            "Create `.github/workflows/release.yml`:\n\n@@FILE .github/workflows/release.yml@@\n\n"
            "Four security choices, all from GitHub's *Secure use reference* for "
            "Actions. The top level grants only `contents: read`; the `image` job adds "
            "`packages: write` and the `release` job adds `contents: write`, so neither job "
            "holds both. Every action is pinned to a full commit SHA with its version in a "
            "comment, because a tag such as `v7` can be moved to other code and a commit "
            "cannot (GitHub: pinning to a full-length commit SHA is \"the only way to use an "
            "action as an immutable release\"). `persist-credentials: false` keeps the token "
            "out of `.git/config`. And the tag name reaches shell commands only through "
            "environment variables, never pasted in with `${{ }}`.",
            "Find the newest release of each action and the commit it points to. On October 8, "
            "2026 they were the ones in the file; check again before you merge:\n\n"
            "@@RUN versions@@\n\nWhen a newer version exists, put its SHA and version comment in "
            "the file. (A Dependabot `github-actions` update would keep them current; ask Ahmad "
            "first.)",
            "Validate the workflow with `actionlint` in a throwaway virtual environment (it is "
            "a development tool, never shipped; `docs/DEPENDENCIES.md`):\n\n@@RUN lint@@",
            "Create the release notes `docs/releases/v2.0-alpha-rc1.md`. The workflow refuses "
            "to run without `docs/releases/<tag>.md`, and fails in seconds (before the hour of "
            "building) when it or `docs/OFFLINE-INSTALL.md` is missing. Replace every TODO with "
            "what the acceptance test showed:\n\n@@FILE docs/releases/v2.0-alpha-rc1.md@@",
            "After merging, tag the release from `main`:\n\n```bash\ngit checkout main && git pull\n"
            "git tag -a v2.0-alpha-rc1 -m \"MaxGuard v2.0-alpha release candidate 1\"\n"
            "git push origin v2.0-alpha-rc1\n```\n\n"
            "*Not run — verify on GitHub*: GitHub Actions cannot run in planning. The first "
            "tag push is the test: the run must be green and the release page must show the "
            "image digest. A package on a personal account is **private** the first time it "
            "is published: in the package's settings, make `maxguard` public once (GitHub "
            "warns that this cannot be undone).",
            "When the workflow is green, build the offline bundle (JON-05) from the tagged "
            "commit, with the image CI built, and attach it:\n\n```bash\n"
            "git checkout v2.0-alpha-rc1\n"
            "docker pull --platform linux/amd64 ghcr.io/<owner>/maxguard:2.0-alpha-rc1@<digest from the release page>\n"
            "docker tag ghcr.io/<owner>/maxguard:2.0-alpha-rc1@<digest> maxguard:2.0.0a0\n"
            "rm -rf dist && scripts/build-offline-bundle.sh\n"
            "gh release upload v2.0-alpha-rc1 dist/* --clobber\n```\n\n"
            "`--clobber` is needed because the release already has `SHA256SUMS` and the small "
            "files: they are replaced by identical copies, and `SHA256SUMS` by the bundle's, "
            "which lists every file. Hand the release to Karthik for KAR-05.",
        ],
        "files": [".github/workflows/release.yml", "docs/releases/v2.0-alpha-rc1.md"],
        "commands": [
            {"id": "versions", "show": (
                "for repo in actions/checkout docker/setup-qemu-action docker/setup-buildx-action "
                "docker/login-action docker/build-push-action; do\n"
                "  tag=$(git ls-remote --tags --refs \"https://github.com/$repo\" | sed 's#.*refs/tags/##' \\\n"
                "        | grep -E '^v[0-9]+\\.[0-9]+\\.[0-9]+$' | sort -V | tail -n 1)\n"
                "  sha=$(git ls-remote \"https://github.com/$repo\" \"refs/tags/$tag^{}\" \"refs/tags/$tag\" "
                "| head -n 1 | cut -f 1)\n"
                "  echo \"$repo@$sha # $tag\"\n"
                "done"),
             "note": ("`^{}` asks for the commit an annotated tag points to; for a plain tag only "
                      "the second name exists. Newer releases after October 8, 2026 change "
                      "this output.")},
            {"id": "lint", "show": (
                "python -m venv /tmp/actionlint-venv\n"
                "/tmp/actionlint-venv/bin/pip install -q actionlint-py==1.7.12.25\n"
                "/tmp/actionlint-venv/bin/actionlint .github/workflows/release.yml .github/workflows/ci.yml "
                "&& echo \"actionlint: clean\""),
             "run": (SCRATCH_ACTIONLINT
                     + " .github/workflows/release.yml .github/workflows/ci.yml && echo \"actionlint: clean\""),
             "note": "Installing actionlint-py downloads the actionlint program from GitHub."},
        ],
        "test": "`actionlint` is clean; on the first tag push the release page shows both "
                "architectures in the image's manifest and the bundle parts with their checksums.",
        "why": (
            "Releases built by CI from a tag are reproducible: anyone can see exactly which commit "
            "and which steps made them. The ARM64 image is what the Raspberry Pi sensor and Apple "
            "Silicon laptops run. A release workflow holds a token that can publish code, so it "
            "gets the fewest rights and only actions that cannot change under it."
        ),
        "checklist": checklist(extra=["`actionlint` is clean", "Every action is pinned to a commit SHA",
                                      "The release has `SHA256SUMS`"]),
    },
    {
        "id": "JAI-10", "owner": "jaiden", "milestone": "W8",
        "title": "Release v2.0-alpha",
        "labels": ["area:release", "critical-path"], "status": "process",
        "depends": ["JAI-09", "KAR-05"],
        "goal": "Fix or defer every issue from the release-candidate test, then tag and publish "
                "`v2.0-alpha` with release notes and the offline bundle.",
        "prereq": "KAR-05's issues are closed or moved to spring with the Security Lead's agreement.",
        "steps": [
            "Merge the last fixes; check CI is green on `main`.",
            "Write `docs/releases/v2.0-alpha.md`; tag `v2.0-alpha` the same way as the release "
            "candidate; attach the bundle; announce it in Discussions.",
            "Run the acceptance test with Ahmad (AHM-05).",
        ],
        "files": [], "commands": [],
        "test": "The acceptance test passes on the published release.",
        "why": "A tagged release is a promise the team can be held to: the same files for everyone.",
        "checklist": ["Release notes written", "Bundle attached with `SHA256SUMS`"],
    },
    {
        "id": "JAI-11", "owner": "jaiden", "milestone": "S8",
        "title": "Signed offline intel bundles",
        "labels": ["area:release"],
        "depends": ["JAI-08", "JAK-09"],
        "goal": (
            "Deliver rule and intel updates (Suricata rules, the JA4 watchlist, mapping updates) "
            "on a USB stick as a signed bundle that MaxGuard verifies before it unpacks anything."
        ),
        "prereq": "JAI-08 (signing) and JAK-09 (the watchlist) are merged.",
        "steps": [
            start_step("jaiden/intel-bundles"),
            "Create `maxguard/intel/bundle.py`:\n\n@@FILE maxguard/intel/bundle.py@@\n\n"
            "The order of the checks in `verify_bundle()` is the point of this task: the member "
            "list is read from the headers only, the signature is checked before anything in the "
            "manifest is trusted, and every file is hashed from memory. Nothing touches the disk "
            "until all of that passed. `install_bundle()` then extracts into a new folder, checks "
            "the hashes again on disk (the USB stick could change between the two reads), and "
            "switches the `current` link in one step. A version that is not newer is refused, so "
            "an old signed bundle cannot be replayed to roll the rules back; `rollback` is the "
            "deliberate way back.",
            "Create the tests `tests/unit/test_intel_bundle.py`. Some bad bundles are signed with "
            "the **right** key: the path and member checks must hold even if the machine that "
            "builds bundles is compromised:\n\n@@FILE tests/unit/test_intel_bundle.py@@",
            "Run them:\n\n@@RUN tests@@",
            "Try it end to end with a throwaway key pair (JAI-08's helper names the files "
            "`custody_ed25519_*.pem`; the real bundle key stays on the maintainer's machine, and "
            "only its public key ships with MaxGuard):\n\n@@RUN demo@@",
            pr_step("feat: signed offline intel bundles (JAI-11)", "ahmadalkhoudeir"),
        ],
        "files": ["maxguard/intel/bundle.py", "tests/unit/test_intel_bundle.py"],
        "commands": [
            {"id": "tests", "show": "pytest tests/unit/test_intel_bundle.py -q"},
            {"id": "demo", "expect_code": 1, "show": (
                "mkdir -p data/bundle-src/rules data/bundle-src/intel\n"
                "cp maxguard/suricata/rules/maxguard.rules data/bundle-src/rules/\n"
                "cp maxguard/intel/ja4_watchlist.yaml data/bundle-src/intel/\n"
                "python -c \"from pathlib import Path; "
                "from maxguard.custody.signing import generate_keypair; "
                "generate_keypair(Path('data/bundle-keys'))\"\n"
                "python -m maxguard.intel.bundle build data/bundle-src "
                "data/intel-2027.03.01.tar.gz data/bundle-keys/custody_ed25519_private.pem "
                "--version 2027.03.01\n"
                "python -m maxguard.intel.bundle verify data/intel-2027.03.01.tar.gz "
                "data/bundle-keys/custody_ed25519_public.pem\n"
                "python -m maxguard.intel.bundle install data/intel-2027.03.01.tar.gz "
                "data/bundle-keys/custody_ed25519_public.pem data/intel\n"
                "python -c \"import os; print('current ->', os.readlink('data/intel/current'))\"\n"
                "python -m maxguard.intel.bundle install data/intel-2027.03.01.tar.gz "
                "data/bundle-keys/custody_ed25519_public.pem data/intel"),
             "note": ("The last command exits with 1: the same version is never installed "
                      "twice. `install` uses symbolic links: on Windows run it in WSL, or turn "
                      "on Developer Mode, which lets normal users create them.")},
        ],
        "test": "Every tamper case is refused before anything is written.",
        "why": (
            "An update channel is a favorite attack path: whoever can change the rules can blind "
            "the sensor. Verifying the signature first, and refusing anything unexpected, means a "
            "tampered USB stick changes nothing. USB delivery keeps MaxGuard offline (CLAUDE.md rule 1)."
        ),
        "checklist": checklist(extra=["Private keys are never in the repository"]),
    },
    {
        "id": "JAI-12", "owner": "jaiden", "milestone": "S13",
        "title": "Release v2.0-rc1 and v2.0",
        "labels": ["area:release", "critical-path"], "status": "process",
        "depends": ["JAI-11", "JAK-07", "AHM-08"],
        "goal": "Tag `v2.0-rc1` for an outside tester (April 30, 2027), fix what they find, and "
                "release `v2.0` (May 7, 2027) with the sensor image and the offline bundle.",
        "prereq": "All spring features are merged (feature freeze April 23, 2027).",
        "steps": [
            "Re-check that every framework version in `docs/PROJECT_DECISIONS.md` section 8 is "
            "still the current published version (CLAUDE.md rule 8) and that the pinned tools "
            "have no unfixed security advisories.",
            "Tag `v2.0-rc1`, hand it to the tester with Karthik, fix, then tag `v2.0` and run the "
            "v2.0 acceptance test with Ahmad (AHM-09).",
        ],
        "files": [], "commands": [], "test": "The v2.0 acceptance test passes.",
        "why": "Same process as the alpha, plus the version checks the compliance rows depend on.",
        "checklist": ["Framework versions re-checked", "Release notes written"],
    },
]
