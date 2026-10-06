# Save point: MaxGuard v2.0 reference build (October 6, 2026, 16:10 UTC)

**Not for merging.** This folder saves the planning session's scratch workspace
so the work can continue in a new session or container. The deliverable is the
documentation in `docs/` on branch `v2-planning` (pull request #3, head
`2e4bdd8` when this was saved). Work stopped here at the project lead's request;
it continues when the project lead says "GO".

## What is in this folder

| Folder | What it is |
|---|---|
| `ref/` | The reference implementation that the roadmap embeds (working tree only). Its git history is not included, because an early commit contained the whole `.venv`; `results/ref-git-log.txt` lists the commits. |
| `docgen/` | The roadmap generator: `plan_<person>.py` (every task), `taskplan.py` (dependency order), `simulate.py` (rebuilds the repository task by task and runs every command), `render.py`, `render_readme.py`, `gen_issues.py` (write `docs/roadmap/`, `docs/ISSUES.md`, `scripts/create_issues.sh`), `snippets/` (earlier versions of files that later tasks change), `outputs/` (the last simulation's real command output). |
| `drafts/week0_template.md` | Read by `render.py` from `/tmp/claude-0/drafts/week0_template.md`. |
| `env/Dockerfile.sandbox` | Builds `maxguard-sandbox:test`: Zeek 9.0.0 plus a Python 3.13 venv with MaxGuard's dependencies, a stand-in for the engine test image (Debian's package servers were blocked, so the real `docker/Dockerfile` could not be built). |
| `workflows/` | The scripts that ran the background builders. `maxguard-reference-build-3-*.js` is the latest (one builder plus one adversarial reviewer per task). |
| `results/karthik-tests-result.json` | Full report of the builder that finished KAR-03/KAR-04/KAR-06. |

## Status of the 19 former design tasks

| Task | State |
|---|---|
| JAI-07 API | Built, tested (27 unit tests, a real capture through Zeek, curl against uvicorn), in the docs as a tested task |
| AMO-05 custody log | Built, tested (21 tests), in the docs |
| JAI-11 signed intel bundles | Built, tested (22 tests), in the docs |
| JON-06 prompt-injection tests | Built, tested (26 tests, mutation-checked), in the docs; ALI-05 rewritten to use them |
| KAR-03, KAR-04 step 3, KAR-06 script | Built by a builder: `tests/expected/*.json`, `tests/integration/test_pcaps.py`, `test_determinism.py`, `tests/unit/test_suricata_eve.py`, `scripts/live_check.sh`, `docs-draft/test-results.md`. Integration tests: 30 passed, 1 skipped in the stand-in image. **Not yet reviewed, not yet in the docs.** Its issues for the lead are in `results/karthik-tests-result.json`. |
| JAK-07 live sensor | Mostly built by a builder that was interrupted: `maxguard/zeek/scripts/live/rotate.zeek`, `maxguard/suricata/maxguard-suricata-live.yaml`, `docker/sensor-compose.yaml`, `maxguard/adapters/live.py` (24 tests pass), `maxguard/sensor/shipper.py` (41 tests pass). Missing: `docs-draft/live-sensor-notes.md`, a final end-to-end run record, the review, the `ADAPTERS` line in `pipeline.py`. |
| AHM-07/08 response, FIO-06/07 decoys and baselines, JAK-10/11 NetFlow and host agent, JAI-09 + JON-05 release and offline bundle, AHM-02/03/06 dashboard | Not built yet (`maxguard/response/` holds only an empty `__init__.py`) |
| KAR-06 run, ALI-05 | Hardware tasks: they stay "not run - verify on hardware" |

## Findings to carry forward

1. **Zeek's `local` policy makes DNS lookups** (fixed and pushed in `2e4bdd8`): `detect-MHR`, `ssh/interesting-hostnames` and `notice/extend-email/hostnames`. MaxGuard loads `maxguard/zeek/site.zeek` instead; the fixtures did not change; `tests/unit/test_zeek_site.py` guards it. **First thing to do next time:** the rebuild commands in `ref/tests/fixtures/zeek/_handmade/README.md` and `_handmade/rdp/README.md` (embedded in `docs/roadmap/karthik.md`, KAR-02) still say `local`; change them to `/src/maxguard/zeek/site.zeek` (they run with `--network none`, so nothing leaked), and fix their "13 lab captures" (there are 14).
2. **The 0-packet mystery** (documented in `docs/HARDWARE.md` 11.3): the `jasonish/suricata:7.0.17` image ships 53,021 ET Open rules; loading them took about 50 s on 4 cores, and Suricata captures nothing until loading ends. With no rules it captured within a second; `jasonish/suricata:8.0.7` ships no rule file (738 packets in a 60 s smoke test).
3. **Live rotation works** with a 1-minute interval: Zeek into `/data/zeek/<YYYY-MM-DD-HHMM>/` via `Log::rotation_format_func`, Suricata 8 into one `eve-YYYY-MM-DD-HHMM.json` per interval; the shipper delivered a folder to `POST /api/ingest` (HTTP 200).
4. **NetworkManager facts** for a silent capture port, from NetworkManager's own source: `ipv4.method disabled`, `ipv6.method disabled`, `ethernet.accept-all-mac-addresses` (promiscuous, since 1.32), ethtool option names `feature-gro` and `feature-lro`.
5. **Open items for review:** DNS rebinding against the console (a `Host` allow-list would stop it); nothing calls `EventStore.prune()` yet (and uploads of old captures complicate a time-based prune); an upload request waits for the AI; `live_check.sh` needs the sensor's and laptop's clocks in sync; whether Debian 13's Suricata package has JA4 is unverified (the first CI run answers it); several texts still say "13 captures" (there are 14).

## How to resume

Commands assume the scratchpad path `SP` of the new session and this repository at `/home/user/maxguard`.

```bash
# 1. Put the workspace back
W=/home/user/maxguard/wip/reference-build
cp -r $W/ref $SP/ref && cp -r $W/docgen $SP/docgen
mkdir -p /tmp/claude-0/drafts && cp $W/drafts/week0_template.md /tmp/claude-0/drafts/
cd $SP/ref && git init -q && git add -A && git commit -qm "restore from save point"

# 2. Python 3.11 venv for the tests (PyPI is reachable from the host)
python3.11 -m venv $SP/ref/.venv && $SP/ref/.venv/bin/pip install -e "$SP/ref[dev]"

# 3. Python 3.13 packages for running tests inside zeek/zeek:9.0.0 (mounted at /deps)
$SP/ref/.venv/bin/pip install --target $SP/deps313 --python-version 3.13 \
  --platform manylinux2014_x86_64 --platform manylinux_2_28_x86_64 \
  --implementation cp --only-binary=:all: \
  "pyyaml>=6.0.3" "requests>=2.34" "fastapi>=0.142" "uvicorn>=0.54" "jinja2>=3.1.6" \
  "python-multipart>=0.0.32" "duckdb>=1.5" "cryptography>=50" "pytest>=9.1" "httpx2>=2.13"

# 4. Docker (start the daemon if needed), then the images the build uses
docker pull zeek/zeek:9.0.0 && docker pull jasonish/suricata:7.0.10
docker pull --platform linux/amd64 jasonish/suricata:8.0.7
docker pull python:3.11-slim-bookworm && docker pull nicolaka/netshoot:v0.15
docker pull koalaman/shellcheck:stable && docker pull alpine:3.20 && docker pull hello-world:latest

# 5. The read-only spec copies the builders read
mkdir -p $SP/ref/docs-spec && cp /home/user/maxguard/docs/{ARCHITECTURE,HARDWARE,DEPENDENCIES}.md $SP/ref/docs-spec/
cp -r /home/user/maxguard/docs/roadmap $SP/ref/docs-spec/roadmap

# 6. Check: everything built so far still passes
cd $SP/ref && ./.venv/bin/ruff check . && ./.venv/bin/pytest -m "not integration" -q
```

At the save point step 6 printed `All checks passed!` and
`628 passed, 1 skipped, 31 deselected`. DuckDB's Python 3.13 wheel is tagged
`manylinux_2_28`, which is why step 3 names two platforms.

`maxguard-sandbox:test` (the stand-in for integration tests) is rebuilt from
`env/Dockerfile.sandbox`: copy `ref`'s `pyproject.toml`, `cli`, `maxguard`,
`mappings` and `tests` next to it, download Python 3.13 wheels for every
dependency into `wheels/` with `pip download`, and build with
`docker build --network none -f Dockerfile.sandbox --target test -t maxguard-sandbox:test .`.
The lab images (`lab-server`, `lab-client`) are only needed to record new captures.

Then: relaunch the builders for the unbuilt tasks (and the two reviews that
did not run) with `workflows/maxguard-reference-build-3-*.js`, integrate,
convert each finished design task in `docgen/plan_*.py` to a tested task, run
`python3 simulate.py`, render into `docs/`, finish `docs/ARCHITECTURE.md`
(sections 2, 4, 13, 15, 17, 18), and update pull request #3.
