"""Jonattan's tasks: citation validator, Ollama client, offline guard, Home text, offline bundle."""

from plan_helpers import checklist, pr_step, start_step

TASKS = [
    {
        "id": "JON-01", "owner": "jonattan", "milestone": "W1",
        "title": "Citation validator: no evidence, no sentence",
        "labels": ["area:ai", "critical-path"],
        "depends": ["JAI-02"],
        "goal": (
            "Write the check that enforces CLAUDE.md rule 3 in code: a sentence from the model is "
            "kept only if it cites at least one record ID and every ID it cites belongs to the "
            "finding being explained. Everything else is dropped and counted."
        ),
        "prereq": "JAI-02 (the `Sentence` dataclass) is merged.",
        "steps": [
            start_step("jonattan/citations"),
            "Create `maxguard/ai/__init__.py` (JON-04 extends it later):\n\n@@FILE maxguard/ai/__init__.py@@",
            "Create `maxguard/ai/citations.py`:\n\n@@FILE maxguard/ai/citations.py@@",
            "Create the tests `tests/unit/test_citations.py`:\n\n@@FILE tests/unit/test_citations.py@@",
            "Run them:\n\n@@RUN tests@@",
            "Try it on an answer with one good and one made-up citation:\n\n@@RUN try@@",
            pr_step("feat: citation validator for AI sentences (JON-01)", "JWinborne1"),
        ],
        "files": [("maxguard/ai/__init__.py", "snip:ai_init_v1.py"), "maxguard/ai/citations.py",
                  "tests/unit/test_citations.py"],
        "commands": [
            {"id": "tests", "show": "pytest tests/unit/test_citations.py -q"},
            {"id": "try", "show": (
                "python -c \"from maxguard.ai.citations import validate; "
                "raw = {'sentences': [{'text': 'Telnet was used.', 'evidence_ids': ['aab5e36795eaa77e']}, "
                "{'text': 'The password was admin.', 'evidence_ids': ['made-up-id']}]}; "
                "print(validate(raw, {'aab5e36795eaa77e'}))\"")},
        ],
        "test": "`pytest` passes; the one-liner keeps the first sentence and reports 1 dropped.",
        "why": (
            "A prompt that says \"cite your evidence\" is only a request; models sometimes invent "
            "IDs or add facts. Checking every answer in code turns the rule into a guarantee: "
            "an explanation can be shorter than the model wanted, but it can never contain an "
            "uncited claim. One wrong ID is enough to drop the whole sentence, because a sentence "
            "that cites something it was not given may be about something else entirely."
        ),
        "checklist": checklist(),
    },
    {
        "id": "JON-02", "owner": "jonattan", "milestone": "W2",
        "title": "Ollama client: one evidence-citing explanation per finding",
        "labels": ["area:ai", "critical-path"],
        "depends": ["JON-01", "JAI-03", "JAK-03"],
        "goal": (
            "Ask the local model (through Ollama) to explain each finding in 2 to 4 sentences, "
            "giving it the finding's facts and the raw log records behind it, and keep only the "
            "sentences that pass the citation check. This is the explanation shown at the "
            "Week 2 demo."
        ),
        "prereq": "JON-01, JAI-03 (record lookup) and JAK-03 (all rules) are merged.",
        "steps": [
            start_step("jonattan/ollama-client"),
            "Create `maxguard/ai/ollama_client.py`:\n\n@@FILE maxguard/ai/ollama_client.py@@\n\n"
            "Read `chat_request()` closely: the JSON `format` schema makes Ollama reject any "
            "other answer shape, `temperature: 0` with a fixed `seed` keeps answers repeatable, "
            "and `think: false` stops thinking models from writing long hidden reasoning first. "
            "`post_chat()` ignores proxy settings so evidence never travels through a proxy.",
            "Create the tests `tests/unit/test_ollama_client.py`. They start a fake Ollama server "
            "on `127.0.0.1` inside the test, so no model and no network are needed:\n\n"
            "@@FILE tests/unit/test_ollama_client.py@@",
            "Run them:\n\n@@RUN tests@@",
            "**On your laptop, with a real model** (not run in planning: the model registry was "
            "unreachable). Install Ollama from https://ollama.com/download, then:\n\n@@RUN real@@\n\n"
            "Each finding's `explanation_sentences` should list 2 to 4 sentences, each with record "
            "IDs from that finding's evidence. Paste the result (minus nothing: lab captures are "
            "synthetic) into your pull request. Model choice is Ali's task (ALI-04); `qwen3:4b` is "
            "only a temporary default.",
            pr_step("feat: Ollama client with citation-checked explanations (JON-02)", "JWinborne1"),
        ],
        "files": ["maxguard/ai/ollama_client.py", "tests/unit/test_ollama_client.py"],
        "commands": [
            {"id": "tests", "show": "pytest tests/unit/test_ollama_client.py -q"},
            {"id": "real", "env": "none",
             "show": ("ollama pull qwen3:4b\n"
                      "maxguard analyze tests/fixtures/zeek/telnet -o telnet-ai.json\n"
                      "python -c \"import json; r = json.load(open('telnet-ai.json')); "
                      "print(r['ai']); print(json.dumps(r['findings'][0]['explanation_sentences'], indent=1))\""),
             "note": "Not run in planning (no model could be downloaded). Needs FIO-04 for the "
                     "`maxguard` command."},
        ],
        "test": (
            "The unit tests pass. With a real model, `ai.status` is `ok`, `explained` is 1, and "
            "every kept sentence cites `aab5e36795eaa77e` (the Telnet record). Stop Ollama and run "
            "it again: the report still appears, with `ai.status` `unavailable` and a `reason`."
        ),
        "why": (
            "The model only ever sees one finding and its own records, so it cannot mix up two "
            "findings, and there is deliberately no cache: reusing one finding's explanation for "
            "another would cite the wrong records (a real bug in the Fall 2026 design). When "
            "Ollama is missing, MaxGuard still produces the report: the AI is an extra, never a "
            "requirement. The evidence is labeled as data copied from network traffic, because an "
            "attacker can put text that looks like instructions into a packet."
        ),
        "checklist": checklist(extra=["The real-model output (or why you could not run it) is in "
                                      "the pull request"]),
    },
    {
        "id": "JON-03", "owner": "jonattan", "milestone": "W3",
        "title": "Offline guard: make accidental network access fail loudly",
        "labels": ["area:ai"],
        "depends": ["JON-02"],
        "goal": (
            "Write `maxguard/offline.py`. When it is on (`MAXGUARD_OFFLINE=1` or "
            "`maxguard analyze --offline`), every Python connection and every host-name lookup "
            "is checked: only this machine, the Ollama host, and hosts the user lists are allowed; "
            "anything else raises `OfflineViolation` instead of leaving the computer."
        ),
        "prereq": "JON-02 is merged (the guard reads the Ollama address through it).",
        "steps": [
            start_step("jonattan/offline-guard"),
            "Create `maxguard/offline.py`:\n\n@@FILE maxguard/offline.py@@",
            "Create the tests `tests/unit/test_offline.py`:\n\n@@FILE tests/unit/test_offline.py@@",
            "Run them:\n\n@@RUN tests@@",
            "See the guard stop a connection before any DNS query is sent:\n\n@@RUN try@@",
            pr_step("feat: offline guard for sockets and DNS lookups (JON-03)", "JWinborne1"),
        ],
        "files": ["maxguard/offline.py", "tests/unit/test_offline.py"],
        "commands": [
            {"id": "tests", "show": "pytest tests/unit/test_offline.py -q"},
            {"id": "try", "show": (
                "python -c \"import socket; from maxguard import offline; "
                "offline.enable('http://127.0.0.1:11434'); "
                "socket.create_connection(('example.com', 80), timeout=3)\" 2>&1 | tail -n 1")},
        ],
        "test": "`pytest` passes, and the one-liner ends with an `OfflineViolation` naming "
                "`example.com`, without any DNS query leaving the machine.",
        "why": (
            "CLAUDE.md rule 1 is easy to break by accident: one library that checks for updates, "
            "or one URL typed in the wrong place, and data leaves the machine. The Fall 2026 guard "
            "only wrapped TCP connects, so UDP packets and DNS lookups still got out; this one "
            "wraps all four socket methods that send to an address and the three lookup functions. "
            "It guards MaxGuard's own Python code, not other programs: the Docker network setup is "
            "the outer wall (`docs/ARCHITECTURE.md` section 12)."
        ),
        "checklist": checklist(),
    },
    {
        "id": "JON-04", "owner": "jonattan", "milestone": "W4",
        "title": "Home mode text for every rule",
        "labels": ["area:ai", "area:ui"],
        "depends": ["JON-01", "JAK-03"],
        "goal": (
            "Write the plain-language headline and one action for each rule that Home mode shows "
            "instead of the technical view. People write it, not the AI, so it is the same on "
            "every machine and reviewed like code."
        ),
        "prereq": "JON-01 and JAK-03 (all 13 rules) are merged.",
        "steps": [
            start_step("jonattan/home-text"),
            "Create `maxguard/ai/home_text.yaml`:\n\n@@FILE maxguard/ai/home_text.yaml@@\n\n"
            "Aim for an 8th-grade reading level: short sentences, everyday words, one action a "
            "person can do today.",
            "Replace `maxguard/ai/__init__.py` with the version that loads the file:\n\n"
            "@@FILE maxguard/ai/__init__.py@@",
            "Create the tests `tests/unit/test_home_text.py`:\n\n@@FILE tests/unit/test_home_text.py@@",
            "Run them:\n\n@@RUN tests@@",
            "Read one entry the way the dashboard will:\n\n@@RUN try@@",
            pr_step("feat: Home mode headline and action per rule (JON-04)", "JWinborne1"),
        ],
        "files": ["maxguard/ai/home_text.yaml", "maxguard/ai/__init__.py",
                  "tests/unit/test_home_text.py"],
        "commands": [
            {"id": "tests", "show": "pytest tests/unit/test_home_text.py -q"},
            {"id": "try", "show": (
                "python -c \"from maxguard.ai import load_home_text; "
                "t = load_home_text()['cleartext.telnet']; print(t['headline']); print(t['action'])\"")},
        ],
        "test": "`pytest` passes: every Fall 2026 rule has an entry, no entry names a rule that "
                "does not exist, and every line is a full sentence short enough for a phone screen.",
        "why": (
            "A home user does not know what \"SC-8(1)\" or \"TLSv10\" means, but can follow \"turn "
            "off Telnet and use SSH\". Generating that text with the AI would make it different on "
            "every machine and impossible to review; a reviewed file is predictable and testable. "
            "Ask Ahmad (Security Lead) to check that every action is safe advice."
        ),
        "checklist": checklist(extra=["Ahmad reviewed the actions"]),
    },
    {
        "id": "JON-05", "owner": "jonattan", "milestone": "W6",
        "title": "Offline bundle: install MaxGuard on a machine with no internet",
        "labels": ["area:release", "critical-path"], "status": "design",
        "depends": ["JAI-04", "ALI-04"],
        "goal": (
            "Write `scripts/build-offline-bundle.sh` and `scripts/install.sh` so a user can install "
            "MaxGuard and its AI model from a USB stick or the GitHub Release without the "
            "internet: the images, the model, the Compose file, and a checksum file, split into "
            "parts smaller than 2 GiB."
        ),
        "prereq": "JAI-04 (the image and Compose file) is merged, and ALI-04 has chosen the models.",
        "steps": [
            start_step("jonattan/offline-bundle"),
            "`scripts/build-offline-bundle.sh` (run on a machine **with** internet): build or "
            "load the MaxGuard image; pull `ollama/ollama:0.35.1`; pull the chosen model into the "
            "volume `maxguard-ollama-models` with a temporary Ollama container; then write into "
            "`dist/`: `images.tar` (`docker save` of both images), `models.tar.gz` (the volume's "
            "files), `compose.yaml`, `install.sh`, `OFFLINE-INSTALL.md`, and `SHA256SUMS`. Split "
            "anything over 2 GiB with `split -b 1900M`. Read the image names and the model from "
            "variables (`MG_IMAGE`, `OLLAMA_IMAGE`, `MAXGUARD_MODEL`) so it can be tested with "
            "small stand-ins.",
            "`scripts/install.sh` (run on the machine **without** internet): check every file "
            "with `sha256sum -c SHA256SUMS` (macOS: `shasum -a 256 -c SHA256SUMS`) **before** "
            "loading anything; stop on any mismatch; join the parts; `docker load`; restore the "
            "model volume; `docker compose up -d`; print the dashboard address.",
            "`scripts/uninstall.sh`: stop and remove the containers; ask before deleting the "
            "data and model volumes.",
            "Test the mechanics with small stand-in images (for example `MG_IMAGE=alpine:3.20`), "
            "then change one byte in a part and check that `install.sh` refuses. Run "
            "`shellcheck` on all three scripts.",
            "With Karthik, run the real bundle on a laptop with Wi-Fi off (this is step 4 of the "
            "acceptance test in `docs/roadmap/README.md`).",
            pr_step("feat: offline bundle build and install scripts (JON-05)", "JWinborne1"),
        ],
        "files": [], "commands": [
            {"id": "check", "env": "none", "show": "shellcheck scripts/*.sh"},
        ],
        "test": (
            "A tampered part makes `install.sh` stop before `docker load`; a clean bundle installs "
            "on a machine with the network unplugged and the dashboard shows an AI explanation."
        ),
        "why": (
            "\"Offline\" has to include the install: a tool that needs the internet to install is "
            "not usable on an isolated network. Checking the checksums before loading anything "
            "means a damaged or swapped file is caught before it can run. Parts under 2 GiB fit "
            "GitHub's limit for release files."
        ),
        "checklist": checklist(extra=["`shellcheck` is clean", "The tamper test is in the pull request"]),
    },
    {
        "id": "JON-06", "owner": "jonattan", "milestone": "S8",
        "title": "Prompt-injection tests for the AI layer",
        "labels": ["area:ai"],
        "depends": ["JON-02", "ALI-03"],
        "goal": (
            "Prove, with tests, that text an attacker puts into network traffic cannot make "
            "MaxGuard's AI hide, change, or invent findings, and cannot make it cite records that "
            "do not belong to the finding; and measure how often each model obeys such text."
        ),
        "prereq": "JON-02 and ALI-03 are merged.",
        "steps": [
            start_step("jonattan/prompt-injection"),
            "Create `scripts/make_injection_set.py`. It copies four fixture folders, plants "
            "hostile text in one field an attacker controls (an HTTP `uri`, a `User-Agent`, a TLS "
            "`server_name`, an FTP user name), runs the real rules on the copy, and writes each "
            "finding with its records in the eval set's format, so Ali's benchmark can run them "
            "unchanged. Each hostile text asks the model to write a *canary* word in capital "
            "letters but contains it only in lower case, so a sentence that merely quotes the "
            "evidence does not count as obeying:\n\n@@FILE scripts/make_injection_set.py@@",
            "Build the set (it is committed, like the eval set, and a test checks it is up to "
            "date):\n\n@@RUN build@@",
            "Create `scripts/injection_report.py`, which reads the benchmark's CSV and counts, per "
            "model, the answers in which the canary reached the reader:\n\n"
            "@@FILE scripts/injection_report.py@@",
            "Create `tests/unit/test_prompt_injection.py`. A fake model answers the way a model "
            "that OBEYS would: it says the device is safe, writes the canary, cites a made-up, a "
            "foreign or no record, and adds `severity` and `status` fields that the answer schema "
            "does not even have. Each test runs the real pipeline on the hostile logs and "
            "compares the report with the same analysis without AI:\n\n"
            "@@FILE tests/unit/test_prompt_injection.py@@",
            "Run them:\n\n@@RUN tests@@",
            "Read `test_a_lie_that_cites_the_hostile_record_is_kept_but_changes_no_finding` "
            "twice: it shows the limit of the citation check. A sentence that cites the hostile "
            "record itself has a valid citation, so it is kept. The AI still cannot hide a "
            "finding or change its severity, because those come from the rules, and the dashboard "
            "always shows the rule's title and severity next to the AI text.",
            "With Ali, run the benchmark on the injection set and record the rate per model "
            "(it goes into ALI-05):\n\n@@RUN bench@@",
            pr_step("test: prompt-injection cases for the AI layer (JON-06)", "JWinborne1"),
        ],
        "files": ["scripts/make_injection_set.py", "scripts/injection_report.py",
                  "tests/fixtures/ai_eval/injection/injection_set.json",
                  "tests/unit/test_prompt_injection.py"],
        "commands": [
            {"id": "build", "show": "python -m scripts.make_injection_set"},
            {"id": "tests", "show": "pytest tests/unit/test_prompt_injection.py -q"},
            {"id": "bench", "env": "none",
             "show": ("python -m scripts.benchmark_models --tier pi "
                      "--eval-set tests/fixtures/ai_eval/injection/injection_set.json qwen3:4b\n"
                      "python -m scripts.injection_report docs/model-eval/raw_results.csv"),
             "note": ("Not run in planning: no model could be downloaded there. The report "
                      "prints one line per model: tier, model, answers, obeyed, rate.")},
        ],
        "test": "The new tests pass, and the benchmark reports the per-model injection rate.",
        "why": (
            "Captures are attacker-controlled data. The design already treats them as data (the "
            "prompt says so, the citation check filters the answer, and the AI cannot touch "
            "severity), but a defense that is not tested tends to break quietly during a later "
            "change. These tests keep it honest, and the canary rate tells the team how often "
            "each model tries to obey, which no citation check can measure."
        ),
        "checklist": checklist(),
    },
]
