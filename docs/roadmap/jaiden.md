# Jaiden: Co-lead; Architecture and Release Lead

**Jaiden Winborne** (@JWinborne1) · Module: Architecture, API, storage, releases · Reviewer for your pull requests: @ahmadalkhoudeir (Ahmad) · Ask first when stuck: Ahmad

This is your part of the MaxGuard v2.0 roadmap. Read [the roadmap overview](README.md) once, then work top to bottom: Week 0 first, then your tasks in order. Each task's ID is also the start of its GitHub issue's title.

## Your tasks

| Task | Due | Title | Needs first | Kind |
|---|---|---|---|---|
| [JAI-00](#week-0--onboarding-due-friday-october-9-2026) | W0 | Week 0 onboarding (Jaiden) | — | process |
| [JAI-01](#jai-01-restructure-the-repository-add-packaging-and-ci) | W0 | Restructure the repository, add packaging and CI | — | code, tested |
| [JAI-02](#jai-02-merge-the-three-contracts-in-their-v20-form) | W0 | Merge the three contracts in their v2.0 form | [JAI-01](#jai-01-restructure-the-repository-add-packaging-and-ci) | code, tested |
| [JAI-03](#jai-03-common-event-schema-the-normalizer-and-record-lookup) | W1 | Common event schema: the normalizer and record lookup | [JAI-02](#jai-02-merge-the-three-contracts-in-their-v20-form), [KAR-02](karthik.md#kar-02-test-fixtures-zeek-and-suricata-output-for-every-capture), [FIO-01](fiona.md#fio-01-zeek-runner-and-the-two-input-adapters), [FIO-02](fiona.md#fio-02-tls-and-certificate-rules), [JAK-03](jakub.md#jak-03-cleartext-and-rdp-rules-the-rule-set-is-complete) | code, tested |
| [JAI-04](#jai-04-the-engine-image-and-the-compose-files) | W1 | The engine image and the Compose files | [JAI-01](#jai-01-restructure-the-repository-add-packaging-and-ci), [AMO-01](amory.md#amo-01-nist-sp-800-53-mapping-file-and-the-mapping-checks) | code, written |
| [JAI-05](#jai-05-the-pipeline-one-function-from-input-to-report) | W2 | The pipeline: one function from input to report | [FIO-01](fiona.md#fio-01-zeek-runner-and-the-two-input-adapters), [FIO-02](fiona.md#fio-02-tls-and-certificate-rules), [JAK-03](jakub.md#jak-03-cleartext-and-rdp-rules-the-rule-set-is-complete), [JAI-03](#jai-03-common-event-schema-the-normalizer-and-record-lookup), [JAK-04](jakub.md#jak-04-asset-inventory), [AMO-01](amory.md#amo-01-nist-sp-800-53-mapping-file-and-the-mapping-checks) | code, tested |
| [JAI-06](#jai-06-storage-alerts-in-sqlite-events-in-hourly-parquet-files) | W3 | Storage: alerts in SQLite, events in hourly Parquet files | [JAI-03](#jai-03-common-event-schema-the-normalizer-and-record-lookup) | code, tested |
| [JAI-07](#jai-07-the-api-uploads-alerts-events-live-updates-sensor-ingest) | W3 | The API: uploads, alerts, events, live updates, sensor ingest | [JAI-05](#jai-05-the-pipeline-one-function-from-input-to-report), [JAI-06](#jai-06-storage-alerts-in-sqlite-events-in-hourly-parquet-files), [JON-03](jonattan.md#jon-03-offline-guard-make-accidental-network-access-fail-loudly) | code, tested |
| [JAI-08](#jai-08-ed25519-signing-library) | W5 | Ed25519 signing library | [JAI-01](#jai-01-restructure-the-repository-add-packaging-and-ci) | code, tested |
| [JAI-09](#jai-09-release-workflow-and-v20-alpha-rc1) | W6 | Release workflow and v2.0-alpha-rc1 | [JAI-04](#jai-04-the-engine-image-and-the-compose-files), [KAR-04](karthik.md#kar-04-ci-runs-the-integration-tests-plus-a-determinism-test), [JON-05](jonattan.md#jon-05-offline-bundle-install-maxguard-on-a-machine-with-no-internet) | design |
| [JAI-10](#jai-10-release-v20-alpha) | W8 | Release v2.0-alpha | [JAI-09](#jai-09-release-workflow-and-v20-alpha-rc1), [KAR-05](karthik.md#kar-05-release-candidate-test-with-an-outside-tester) | process |
| [JAI-11](#jai-11-signed-offline-intel-bundles) | S8 | Signed offline intel bundles | [JAI-08](#jai-08-ed25519-signing-library), [JAK-09](jakub.md#jak-09-ja4-watchlist-rule) | code, tested |
| [JAI-12](#jai-12-release-v20-rc1-and-v20) | S13 | Release v2.0-rc1 and v2.0 | [JAI-11](#jai-11-signed-offline-intel-bundles), [JAK-07](jakub.md#jak-07-live-sensor-capture-rotation-and-shipping-to-the-console), [AHM-08](ahmad.md#ahm-08-response-approvals-audit-revert-and-the-opnsense-connector) | process |

**Kind:** *code, tested* — the complete code below was run with its tests during planning; copy it exactly, then improve it in a later pull request if you like. *code, written* — written in planning, but part of it needs a machine planning did not have. *design* — you write the code from the steps. *process* — no code: setup, review, testing or release work.

## Week 0 — Onboarding (due Friday, October 9, 2026)

**Goal:** by Friday you have every tool installed, the repository on your
computer, one merged pull request, and you know where to ask questions.
Plan 2–3 hours. Do the steps in order; each one ends with a check.

> **Windows users:** do every terminal step inside **Ubuntu on WSL 2**, so your
> commands match everyone else's. Keep the project inside your Ubuntu home folder
> (`~/projects`), not under `/mnt/c/...`: it is much faster and avoids Windows
> line-ending problems.

### 0.1 Open a terminal

| Your computer | What to do |
|---|---|
| Windows 10/11 | Right-click **Start → Terminal (Admin)** and run `wsl --install -d Ubuntu-24.04`. Restart when asked. Open **Ubuntu** from the Start menu and choose a Linux user name and password (they do not have to match Windows). |
| macOS | Open **Terminal** (Applications → Utilities). |
| Linux | Open your terminal. |

*Not run here — verify on your machine.* **Check:** in the Ubuntu or macOS
terminal, `uname -s` prints `Linux` or `Darwin`.

### 0.2 Install Git and keep your email private

1. Install Git:
   - Ubuntu / WSL: `sudo apt update && sudo apt install -y git`
   - macOS: `xcode-select --install`, then click **Install**.
2. On github.com, open **Settings → Emails**. Tick **Keep my email addresses
   private** and **Block command line pushes that expose my email**. Copy the
   address GitHub shows, which looks like `12345678+YOUR-USERNAME@users.noreply.github.com`.
3. Tell Git who you are (use the noreply address from step 2, never your
   personal or school email):

```bash
git config --global user.name "Jaiden Winborne"
git config --global user.email "12345678+YOUR-USERNAME@users.noreply.github.com"
git config --global init.defaultBranch main
```

**Check:** `git --version` prints `git version 2.` followed by a number, and
`git config --global user.email` prints your noreply address.

**Why:** every commit records the author's email, and this repository is
public. CLAUDE.md rule 6 forbids publishing email addresses, and GitHub's
noreply address keeps yours private
([GitHub Docs](https://docs.github.com/en/account-and-profile/how-tos/email-preferences/setting-your-commit-email-address)).

### 0.3 Install VS Code

1. Download it from https://code.visualstudio.com and install it.
2. Open VS Code, click the **Extensions** icon (four squares) and install:
   **Python** (Microsoft), **Ruff** (Astral Software), and on Windows **WSL** (Microsoft).
3. Windows: from now on, open the project by typing `code .` inside the Ubuntu
   terminal. The bottom-left corner of VS Code then shows `WSL: Ubuntu-24.04`.

**Check:** `code --version` prints a version number. *Not run here — verify on your machine.*

### 0.4 Install Python 3.11

MaxGuard supports Python 3.11 and newer. CI tests on 3.11 (the oldest version
we promise to support) and the Docker image runs 3.13, so use 3.11 on your laptop
to catch anything that only works on newer versions.

- **Ubuntu 24.04 / WSL** (Ubuntu 24.04 ships Python 3.12, so 3.11 comes from the
  deadsnakes archive, which provides 3.11 for 24.04 —
  [Launchpad](https://launchpad.net/~deadsnakes/+archive/ubuntu/ppa)):

```bash
sudo apt install -y software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.11 python3.11-venv
```

- **macOS:** install Homebrew from https://brew.sh, then `brew install python@3.11`.

**Check:** `python3.11 --version` prints `Python 3.11.` followed by a number.
*Not run here (the package archives are blocked in the planning environment) — verify on your machine.*

### 0.5 Install Docker

| Your computer | What to install |
|---|---|
| Windows | **Docker Desktop** from https://www.docker.com/products/docker-desktop/. In Docker Desktop open **Settings → Resources → WSL integration** and switch on **Ubuntu-24.04**. |
| macOS | **Docker Desktop** (pick Apple Silicon or Intel). In **Settings → Resources**, give it at least 8 GB of memory (the local AI model needs it). |
| Linux | **Docker Engine**: follow https://docs.docker.com/engine/install/ for your distribution, then run `sudo usermod -aG docker $USER` and log out and back in. |

Docker Desktop is free for education and personal use
([Docker license](https://docs.docker.com/subscription-billing/desktop-license/)).

**Check** (run each line; the planning environment ran the last one):

```bash
docker --version
docker compose version
docker run --rm hello-world
```

Expected: two version lines, then a message that starts with `Hello from Docker!`.

### 0.6 Install the GitHub CLI and log in

- Ubuntu / WSL: `sudo apt install -y gh`
- macOS: `brew install gh`

Then run `gh auth login` and choose **GitHub.com → HTTPS → Login with a web
browser**, and paste the one-time code into the page that opens.

**Check:** `gh auth status` prints `Logged in to github.com account YOUR-USERNAME`.

### 0.7 Clone the repository

```bash
mkdir -p ~/projects && cd ~/projects
git clone https://github.com/ahmadalkhoudeir/maxguard.git
cd maxguard
git status
```

Expected:

```text
On branch main
Your branch is up to date with 'origin/main'.

nothing to commit, working tree clean
```

If it says `not a git repository`, you are in the wrong folder: run `cd ~/projects/maxguard`.

### 0.8 Your first Zeek log (proves Docker works)

You will record a tiny web request between two throwaway containers and let
Zeek, the network monitor MaxGuard is built on, turn it into a log. Nothing
leaves your computer, and no real network traffic is recorded. Work in a lab
folder **outside** the repository, so a capture can never be committed by accident.

```bash
mkdir -p ~/mg-lab/pcaps ~/mg-lab/logs
docker network create mg-week0
docker run -d --rm --name mg-web --network mg-week0 python:3.11-slim-bookworm python -m http.server 80
docker run -d --rm --name mg-sniff --network container:mg-web -v ~/mg-lab/pcaps:/pcaps nicolaka/netshoot:v0.15 tcpdump -i eth0 -U -w /pcaps/week0.pcap
sleep 3
docker run --rm --network mg-week0 python:3.11-slim-bookworm python -c "import urllib.request; print(urllib.request.urlopen('http://mg-web/').status)"
sleep 2
docker stop mg-sniff mg-web
docker network rm mg-week0
```

Expected: the `python -c` line prints `200`. Now run Zeek on the capture, with
the network switched off for Zeek's container:

```bash
docker run --rm --network none -v ~/mg-lab/pcaps:/pcaps:ro -v ~/mg-lab/logs:/logs -w /logs zeek/zeek:9.0.0 zeek -C -r /pcaps/week0.pcap LogAscii::use_json=T
ls ~/mg-lab/logs
head -n 1 ~/mg-lab/logs/http.log
```

Expected (run in the planning environment; your timestamps, IDs and addresses will differ):

```text
conn.log  files.log  http.log  packet_filter.log
{"ts":1791255189.849469,"uid":"CCdfUf2LPFi44Vh77j","id.orig_h":"172.18.0.3","id.orig_p":35190,"id.resp_h":"172.18.0.2","id.resp_p":80,"trans_depth":1,"method":"GET","host":"mg-web","uri":"/","version":"1.0","user_agent":"Python-urllib/3.11",...}
```

What each part does: `--network none` proves Zeek works offline; `-C` ignores
bad checksums, which are common in captures; `-r` reads a file instead of a live
network card; `LogAscii::use_json=T` writes one JSON object per line. On Linux
the capture file belongs to `root` (Docker wrote it); delete it later with
`sudo rm ~/mg-lab/pcaps/week0.pcap`.

### 0.9 Your first pull request

You will add your row to `docs/TEAM.md`. Every task in this roadmap uses the
same six steps, so learn them now.

1. **Start from an up-to-date `main` and make a branch** named `<yourname>/<short-task>`:

```bash
cd ~/projects/maxguard
git checkout main && git pull
git checkout -b jaiden/week0-team-row
```

2. **Make the change.** Run `code .`, open `docs/TEAM.md`, and add this line at
   the end (keep the `|` characters):

```markdown
| Jaiden Winborne | Co-lead; Architecture and Release Lead | JWinborne1 | Architecture, API, storage, releases |
```

3. **Commit** (the message says *what changed*, starting with a type such as
   `docs:`, `feat:`, `fix:` or `test:`; see `docs/CONTRIBUTING.md`):

```bash
git add docs/TEAM.md
git commit -m "docs: add Jaiden to TEAM.md"
```

4. **Push** your branch to GitHub:

```bash
git push -u origin jaiden/week0-team-row
```

Expected (from the planning simulation; the first lines differ on GitHub):

```text
 * [new branch]      jaiden/week0-team-row -> jaiden/week0-team-row
branch 'jaiden/week0-team-row' set up to track 'origin/jaiden/week0-team-row'.
```

5. **Open the pull request** and ask for a review:

```bash
gh pr create --base main --title "docs: add Jaiden to TEAM.md" --body "Week 0 onboarding." --reviewer ahmadalkhoudeir
```

`gh` prints the pull request's web address. (You can also click the link Git
printed after the push and press **Create pull request**.)

6. **After approval**, click **Squash and merge** on GitHub, then update your laptop:

```bash
git checkout main && git pull
git branch -d jaiden/week0-team-row
```

**If GitHub says "This branch has conflicts":** eight people are adding a line
to the same file this week, so this is expected. Bring `main` into your branch
and keep both lines:

```bash
git checkout main && git pull
git checkout jaiden/week0-team-row
git merge main
```

Git prints `CONFLICT (content): Merge conflict in docs/TEAM.md`. Open the file;
you will see something like:

```text
<<<<<<< HEAD
| Karthik Nair | Test and CI Engineer | Karthiknair91 | Testing |
=======
| Jakub Kania | Protocol Coverage Engineer | SXafir-byte | Sensor |
>>>>>>> main
```

Delete the three marker lines (`<<<<<<<`, `=======`, `>>>>>>>`), keep **both**
rows, save, then:

```bash
git add docs/TEAM.md
git commit --no-edit
git push
```

(This exact conflict and fix were run in the planning environment.)

### 0.10 Ask questions in GitHub Discussions

1. Open https://github.com/ahmadalkhoudeir/maxguard/discussions.
2. Find the pinned discussion **"Week 0 check-in"** (Ahmad creates it in
   AHM-01) and reply with: the output of `git --version`, `python3.11 --version`,
   `docker --version`, and the first line of your `http.log` from step 0.8.
3. When you are stuck on any task: click **New discussion**, pick the **Q&A**
   category, and write a title that names the task (for example
   `JAI-01: pytest cannot import maxguard`). In the body, paste the
   **exact command** you ran, the **exact output** (in a code block), and what you
   expected. Tag your help person. Never paste passwords, tokens, or captures
   from a real network.

**Why Discussions and not only Teams:** an answer in Discussions can be found
again by the next person with the same problem; a Teams chat scrolls away.

### 0.11 Set up MaxGuard's Python environment (as soon as JAI-01 is merged)

JAI-01 adds `pyproject.toml`, the file that lists everything MaxGuard needs.
Once Jaiden announces it is merged (Discussions → Announcements), run this once
(you do it inside JAI-01):

```bash
cd ~/projects/maxguard
git checkout main && git pull
python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e ".[dev]"
pytest -m "not integration" -q
```

**Check:** the prompt now starts with `(.venv)`, and the last line of `pytest`
says `passed` with no `failed`. In every new terminal, run
`cd ~/projects/maxguard && source .venv/bin/activate` before working.

**Why:** a virtual environment (`.venv/`) keeps MaxGuard's packages separate
from the rest of your computer, so two projects never fight over versions.
`-e` (editable) means Python uses your working copy directly: edit a file and
the next run sees it, no reinstall needed. `.venv/` is listed in `.gitignore`,
so it is never committed.

### Week 0 checklist

- [ ] `git --version`, `python3.11 --version`, `docker --version`, `gh auth status` all work
- [ ] Git uses your GitHub noreply email
- [ ] `zeek/zeek:9.0.0` produced `http.log` from your own capture
- [ ] Your `docs/TEAM.md` pull request is merged
- [ ] You replied to "Week 0 check-in" in Discussions
- [ ] After JAI-01: `.venv` works and `pytest -m "not integration" -q` passes

## Fall 2026: v2.0-alpha

### JAI-01: Restructure the repository, add packaging and CI

**Due:** Week 0 (due Fri Oct 9, 2026) · **Milestone:** `W0 Onboarding and contracts` · **Needs first:** none · **Kind:** code, tested

**Issue labels:** `type:task` `phase:alpha` `owner:jaiden` `area:release` `critical-path`

#### Goal

Turn the v0.8 repository into the v2.0 layout: old code moves to `legacy/`, a `pyproject.toml` makes `pip install -e .` work for everyone, and GitHub Actions runs the linter and the tests on every pull request. Every other task builds on this one.

#### Prerequisites

Your Week 0 onboarding is done. Nothing else: this is the first task in the roadmap.

#### Steps

**Step 1.** Update `main` and create your branch for this task (one branch per task):

```bash
cd ~/projects/maxguard
source .venv/bin/activate
git checkout main && git pull
git checkout -b jaiden/restructure
```

If `source .venv/bin/activate` fails, you have not made the virtual environment yet: do Week 0 section 0.11 first.

**Step 2.** Move the v0.8 code into `legacy/` so nothing is lost (it is deleted at the feature freeze; the `v0.8.0-Spring2026` tag also keeps it forever):

```bash
mkdir legacy
git mv scanner analyzer dashboard reports config .launch .version "Voice Module" Dockerfile requirements.txt .streamlit .devcontainer .dockerignore legacy/
git status --short | head
```

Expected: lines starting with `R ` (renamed), for example `R  scanner/sniffer.py -> legacy/scanner/sniffer.py`.

**Step 3.** Create the package folders. In VS Code, create these two files (folders are created for you when you type the path):

`maxguard/__init__.py`:

```python
"""MaxGuard: offline network security checks for small networks.

See docs/ARCHITECTURE.md for how the parts fit together.
"""

__version__ = "2.0.0a0"
```

`cli/__init__.py`:

```python
"""MaxGuard command line interface (`maxguard` / `python -m cli.main`)."""
```

**Step 4.** Create `pyproject.toml` in the repository root. It names the package, its dependencies with the versions MaxGuard was tested with, the `maxguard` command, the files that are not Python but must be installed, and the settings for Ruff and pytest:

```toml
[build-system]
# 77 is the first setuptools that reads the SPDX "license" string below (PEP 639).
requires = ["setuptools>=77"]
build-backend = "setuptools.build_meta"

[project]
name = "maxguard"
version = "2.0.0a0"
description = "Offline network security checks for small networks: Zeek and Suricata findings, compliance mapping, local AI explanations."
requires-python = ">=3.11"
license = "Apache-2.0"
license-files = ["LICENSE"]
# Lower bounds are the versions MaxGuard v2.0 was tested with (October 2026).
# There are no upper bounds: this is an application installed into its own
# virtual environment, and CI catches a breaking release.
dependencies = [
    "pyyaml>=6.0.3",             # mapping files, AI text, intel watchlists
    "requests>=2.34",            # talks to the local Ollama server only
    "fastapi>=0.142",            # JSON API and web pages
    "uvicorn>=0.54",             # web server inside the container
    "jinja2>=3.1.6",             # HTML templates
    "python-multipart>=0.0.32",  # file uploads (POST /api/analyses)
    "duckdb>=1.5",               # event timeline: queries the Parquet files
    "cryptography>=50",          # Ed25519 signatures (maxguard.custody.signing)
]

[project.optional-dependencies]
dev = [
    "pytest>=9.1",
    "ruff>=0.16",
    "httpx2>=2.13",  # FastAPI's TestClient (Starlette 1.7 deprecates plain httpx for it)
]

[project.scripts]
maxguard = "cli.main:main"

[tool.setuptools.packages.find]
# mappings/ is not a Python package: the Docker image copies the folder and sets
# MAXGUARD_MAPPINGS_DIR, and a checkout finds it next to the maxguard folder.
include = ["maxguard*", "cli*"]

[tool.setuptools.package-data]
# Non-Python files the engine reads at run time. Without these lines a normal
# (non-editable) install, like the one in the Docker image, would leave them out.
maxguard = [
    "zeek/*.zeek",
    "zeek/scripts/*.zeek",
    "zeek/scripts/live/*.zeek",
    "suricata/*.yaml",
    "suricata/rules/*",
    "ai/*.yaml",
    "intel/*.yaml",
    "web/templates/**/*",
    "web/static/**/*",
]

[tool.ruff]
line-length = 100
target-version = "py311"
# The old v0.8 code waits in legacy/ until the feature freeze (JAI-01); it is not linted.
extend-exclude = ["legacy"]

[tool.ruff.lint]
# E/F: real errors; I: sorted imports (ruff check --fix sorts them for you);
# B: common bug patterns; UP: modern Python syntax for 3.11.
select = ["E", "F", "I", "B", "UP"]

[tool.pytest.ini_options]
testpaths = ["tests"]
# Lets "pytest" import maxguard from this checkout without installing it first.
pythonpath = ["."]
# A misspelled marker is an error instead of a silently ignored test filter.
addopts = "--strict-markers"
markers = [
    "integration: needs Zeek (and Suricata); runs inside the engine Docker image",
]
```

**Step 5.** Create the shared test helpers `tests/conftest.py` (pytest loads it automatically):

```python
"""Shared test helpers: where the fixture logs and test captures live.

pytest loads this file automatically before any test. Tests get the helpers as
fixtures (arguments), for example:

    def test_telnet(fixture_dir):
        log_dir = fixture_dir("telnet")   # tests/fixtures/zeek/telnet

Code that runs while pytest collects tests (for example a
@pytest.mark.parametrize list) cannot use fixtures; it can use the constants:

    from conftest import CAPTURE_NAMES
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
TESTS_DIR = REPO_ROOT / "tests"
FIXTURES = TESTS_DIR / "fixtures" / "zeek"  # Zeek JSON logs + eve.json per capture
PCAPS = TESTS_DIR / "pcaps"  # the synthetic lab captures

# One folder per lab capture. Folders starting with "_" hold hand-made extras.
# Empty until Karthik's captures and fixtures are merged (KAR-02).
CAPTURE_NAMES = sorted(
    p.name for p in FIXTURES.iterdir() if p.is_dir() and not p.name.startswith("_")
) if FIXTURES.is_dir() else []


def find_fixture_dir(name: str) -> Path:
    """tests/fixtures/zeek/<name>, e.g. "telnet" or "_handmade/dns_dhcp"."""
    path = FIXTURES / name
    if not path.is_dir():
        raise FileNotFoundError(f"no fixture folder {path}")
    return path


def find_pcap(name: str) -> Path:
    """tests/pcaps/<name>.pcap, e.g. find_pcap("telnet")."""
    path = PCAPS / f"{name}.pcap"
    if not path.is_file():
        raise FileNotFoundError(f"no test capture {path}")
    return path


@pytest.fixture
def fixture_dir() -> Callable[[str], Path]:
    """Returns a function: fixture_dir("telnet") -> Path to that fixture folder."""
    return find_fixture_dir


@pytest.fixture
def pcap_file() -> Callable[[str], Path]:
    """Returns a function: pcap_file("telnet") -> Path to tests/pcaps/telnet.pcap."""
    return find_pcap
```

and the first test, `tests/unit/test_package.py`:

```python
"""The first test in the repository: the package imports and has a version.

It exists so CI has something to run from day one (pytest fails when it finds
no tests at all).
"""

import maxguard


def test_package_imports_and_has_a_version():
    assert maxguard.__version__ == "2.0.0a0"
```

**Step 6.** Create the CI workflow `.github/workflows/ci.yml`:

```yaml
# Runs on every pull request and on every push to main.
# "test": lint + unit tests on Python 3.11 (fast, no Docker).
# (Karthik adds an "integration" job in KAR-04, once there are integration tests.)
name: CI

on:
  push:
    branches: [main]
  pull_request:

# The jobs only read the code; they never need write access to the repository.
permissions:
  contents: read

jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v7

      - uses: actions/setup-python@v7
        with:
          python-version: "3.11"
          cache: pip
          cache-dependency-path: pyproject.toml

      - name: Install MaxGuard and the dev tools
        run: pip install -e ".[dev]"

      - name: Lint
        run: ruff check .

      - name: Unit tests
        run: pytest -m "not integration" -q
```

**Step 7.** Make a virtual environment and install MaxGuard with the developer tools. Do this once; afterwards only `source .venv/bin/activate` in each new terminal:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e ".[dev]"
```

Expected: the last line starts with `Successfully installed` and lists `maxguard-2.0.0a0`.

**Step 8.** Run the two checks CI will run:

```bash
ruff check .
```

Expected output:

```text
All checks passed!
```

```bash
pytest -m "not integration" -q
```

Expected output:

```text
.                                                                                            [100%]
1 passed in 0.01s
```

**Step 9.** Commit, push, and open the pull request:

```bash
git add -A
git status          # only this task's files: nothing from .venv/, data/ or lab/captures/
git commit -m "chore: restructure repo, add pyproject and CI (JAI-01)"
git push -u origin HEAD
```

`HEAD` means "the branch I am on", so you do not have to retype its name. Open the repository on github.com: a yellow bar shows your branch with a **Compare & pull request** button. Click it, keep the title `chore: restructure repo, add pyproject and CI (JAI-01)`, fill in the template (paste the real output of the commands above under **How I tested it**), write `Closes #<issue number>` (this task's issue), and pick **@ahmadalkhoudeir** under **Reviewers**. Click **Create pull request**, then fix anything CI or the reviewer finds with new commits on the same branch.

**Step 10.** **After the pull request is merged**, protect `main` (you need admin rights; ask Ahmad if you do not have them). On github.com open **Settings → Rules → Rulesets → New ruleset → New branch ruleset**:

| Field | Value |
|---|---|
| Ruleset name | `main-protection` |
| Enforcement status | **Active** |
| Target branches | **Add target → Include default branch** |
| Rules | tick **Restrict deletions**, **Block force pushes**, **Require a pull request before merging** (Required approvals: **1**), and **Require status checks to pass** → **Add checks** → type `test` and pick the check from GitHub Actions |

Click **Create**. *Not run here — verify on github.com.* (The `test` check appears in the list only after CI has run once, which is why this comes after the merge.)

#### How to test

Both commands above print what is shown. Then open your pull request on GitHub: the **Checks** tab shows the `test` job with a green tick within about two minutes. `pytest` printing `1 passed` means the package imports and the test setup works.

#### What you just did and why

A Python *package* (`maxguard/` with an `__init__.py`) lets every module import every other with `from maxguard.x import y`. `pyproject.toml` is the one place that lists dependencies, so `pip install -e .` gives everyone the same setup; `-e` (editable) means your code changes take effect without reinstalling. CI runs the same two commands on a clean machine for every pull request, so "it works on my laptop" is never enough. Branch protection makes the rule *at least one review and green CI* impossible to skip, even for the leads.

#### Pull request checklist

- [ ] `ruff check .` prints `All checks passed!`
- [ ] `pytest -m "not integration" -q` passes on your laptop
- [ ] The pull request title has the form `type: summary (TASK-ID)` and the body says `Closes #<issue number>`
- [ ] No secrets, passwords, email addresses, personal data, or captures from a real network (CLAUDE.md rule 6)
- [ ] Any new dependency has a row in `docs/DEPENDENCIES.md` with its license
- [ ] CI is green and your reviewer approved
- [ ] `git status` shows the old folders under `legacy/` (moved, not deleted)
- [ ] The `test` job is green on the pull request
- [ ] After merging: the `main-protection` ruleset is active

### JAI-02: Merge the three contracts in their v2.0 form

**Due:** Week 0 (due Fri Oct 9, 2026) · **Milestone:** `W0 Onboarding and contracts` · **Needs first:** [JAI-01](#jai-01-restructure-the-repository-add-packaging-and-ci) · **Kind:** code, tested

**Issue labels:** `type:task` `phase:alpha` `owner:jaiden` `area:engine` `critical-path` `contract-change`

#### Goal

Add the code everyone else builds against: Contract 1 (the `Finding` dataclass), the record and finding IDs, Contract 3 (the input adapter protocol), the rule registry, and Contract 2's loader for the mapping files. `docs/ARCHITECTURE.md` section 5 explains every extension; the original Fall 2026 code keeps working unchanged.

#### Prerequisites

JAI-01 is merged. Read `docs/ARCHITECTURE.md` sections 5 and 7 first (15 minutes).

#### Steps

**Step 1.** Update `main` and create your branch for this task (one branch per task):

```bash
cd ~/projects/maxguard
source .venv/bin/activate
git checkout main && git pull
git checkout -b jaiden/contracts-v2
```

If `source .venv/bin/activate` fails, you have not made the virtual environment yet: do Week 0 section 0.11 first.

**Step 2.** Create `maxguard/models.py` (Contract 1):

```python
"""Contract 1: the Finding dataclass (MaxGuard v2.0).

This is the original Fall 2026 contract with backward-compatible extensions.
Every original field keeps its name, type, position, and meaning. New fields
come after the original ones and all have defaults, so code written against
the original contract still works unchanged.

Who fills what:
- Rules fill every field from rule_id through evidence (plus source).
- The mapping layer fills controls and attack.
- The AI layer fills explanation_sentences and explanation.
- finding_id is computed automatically from the dedup key.
"""

from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass, field

SEVERITIES = ("critical", "high", "medium", "low", "info")


@dataclass
class Evidence:
    log: str  # e.g. "conn.log" or "eve.json"
    uid: str  # Zeek connection uid (for Suricata records: the Community ID)
    ts: float  # record timestamp (epoch seconds)
    record_id: str = ""  # v2.0: content hash of the exact log record (see maxguard.ids)


@dataclass
class Control:
    framework: str  # "PCI DSS", "NIST SP 800-53", "CISA CPG", "CJIS"
    version: str  # exactly as locked in docs/PROJECT_DECISIONS.md section 8
    control_id: str  # "4.2.1", "SC-8(1)", ...
    title: str
    rationale: str


@dataclass
class Technique:  # v2.0: MITRE ATT&CK technique, filled by the mapping layer
    technique_id: str  # "T1040"
    name: str  # "Network Sniffing"
    tactic: str  # "credential-access"
    version: str  # ATT&CK version, e.g. "v19.2"


@dataclass
class Sentence:  # v2.0: one AI sentence plus the evidence it cites
    text: str
    evidence_ids: list[str] = field(default_factory=list)  # Evidence.record_id values


def make_finding_id(rule_id: str, src_ip: str, dst_ip: str, dst_port: int) -> str:
    """Stable ID for one deduplicated finding. Same key in, same ID out."""
    key = f"{rule_id}|{src_ip}|{dst_ip}|{dst_port}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]


@dataclass
class Finding:
    # ---- original Fall 2026 fields (unchanged) ----
    rule_id: str  # stable key, e.g. "cleartext.telnet"
    title: str
    severity: str  # one of SEVERITIES
    src_ip: str
    dst_ip: str
    dst_port: int
    protocol: str  # "telnet", "tls", ...
    first_seen: float
    last_seen: float
    count: int = 1
    details: dict = field(default_factory=dict)
    evidence: list[Evidence] = field(default_factory=list)
    controls: list[Control] = field(default_factory=list)  # filled by mapping
    explanation: str | None = None  # filled by the AI layer
    # ---- v2.0 extensions (all optional) ----
    finding_id: str = ""  # computed in __post_init__ when empty
    source: str = "zeek"  # "zeek", "suricata", "netflow", "agent", "decoy"
    attack: list[Technique] = field(default_factory=list)  # filled by mapping
    explanation_sentences: list[Sentence] = field(default_factory=list)  # filled by AI

    def __post_init__(self) -> None:
        if self.severity not in SEVERITIES:
            raise ValueError(f"severity must be one of {SEVERITIES}, got {self.severity!r}")
        if not self.finding_id:
            self.finding_id = make_finding_id(
                self.rule_id, self.src_ip, self.dst_ip, self.dst_port
            )

    def to_dict(self) -> dict:
        return asdict(self)
```

**Step 3.** Create `maxguard/ids.py` (stable IDs for log records):

```python
"""Stable IDs for log records (v2.0).

record_id(log, rec) hashes the log name plus the record's content, so the same
record always gets the same ID, on every machine, in every run. The AI cites
these IDs, the event index uses them as event_id, and the dashboard links
evidence back to the raw record with them.
"""

from __future__ import annotations

import hashlib
import json

from maxguard.models import Evidence


def canonical_json(rec: dict) -> str:
    """One fixed text form of a record: sorted keys, no extra spaces."""
    return json.dumps(rec, sort_keys=True, separators=(",", ":"), default=str)


# Fields that change from run to run even for the same capture. Suricata picks
# a random flow_id each run, so it is left out of the hash.
VOLATILE_KEYS = frozenset({"flow_id"})


def record_id(log: str, rec: dict) -> str:
    """16 hex characters identifying one record in one log."""
    stable = {k: v for k, v in rec.items() if k not in VOLATILE_KEYS}
    data = f"{log}\n{canonical_json(stable)}".encode()
    return hashlib.sha256(data).hexdigest()[:16]


def evidence(log: str, rec: dict) -> Evidence:
    """Build the Evidence for a Zeek record or a Suricata eve.json record."""
    # Zeek records have a uid. Suricata records are linked by community_id,
    # which Zeek also logs, so the two tools' records can be joined.
    uid = rec.get("uid") or rec.get("community_id") or ""
    ts = rec.get("ts")
    if ts is None:  # Suricata uses an ISO timestamp string instead of epoch "ts"
        ts = iso_to_epoch(rec["timestamp"])
    return Evidence(log=log, uid=uid, ts=float(ts), record_id=record_id(log, rec))


def iso_to_epoch(value: str) -> float:
    """Convert Suricata's '2026-10-06T01:02:03.456789+0000' to epoch seconds."""
    from datetime import datetime

    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f%z").timestamp()
```

**Step 4.** Create an **empty** file `maxguard/adapters/__init__.py`, then `maxguard/adapters/base.py` (Contract 3):

```python
"""Contract 3: the input adapter interface.

Unchanged from the Fall 2026 roadmap. v2.0 note: the directory returned by
to_zeek_logs() may also contain Suricata's eve.json (one JSON object per line),
which rules read with the same read_log() helper: read_log(log_dir, "eve.json").
"""

from collections.abc import Iterator
from pathlib import Path
from typing import Protocol


class InputAdapter(Protocol):
    name: str

    def accepts(self, path: Path) -> bool: ...

    def to_zeek_logs(self, path: Path, workdir: Path) -> Path:
        """Return a directory of Zeek JSON logs (one object per line)."""


def read_log(log_dir: Path, log_name: str) -> Iterator[dict]:
    """Yield records from e.g. conn.log; yield nothing if the file is absent."""
    import json

    p = log_dir / log_name
    if not p.exists():
        return
    with p.open() as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                yield json.loads(line)
```

**Step 5.** Create the rule registry: `maxguard/rules/__init__.py`

```python
"""Importing this package registers every rule module with the registry.

Rule modules are added here as they are written: FIO-02 (tls, certs) and
JAK-03 (cleartext).
"""
```

and `maxguard/rules/base.py`:

```python
"""Rule registry (Fall 2026 roadmap, unchanged behavior).

A rule is a function that takes a folder of logs and returns Finding objects.
Rules never read the clock, the network, or random numbers, so the same logs
always produce the same findings (CLAUDE.md rule 2).
"""

from collections.abc import Callable
from pathlib import Path

from maxguard.models import Finding

RULES: dict[str, Callable[[Path], list[Finding]]] = {}
MAX_EVIDENCE = 5


def rule(rule_id: str):
    def wrap(fn):
        if rule_id in RULES:
            raise ValueError(f"duplicate rule_id {rule_id!r}")
        RULES[rule_id] = fn
        return fn

    return wrap


def merge(findings: list[Finding]) -> list[Finding]:
    """Collapse duplicates per Contract 1: one Finding per (rule_id, src, dst, port).

    The first Finding for each key is kept and updated in place; at most
    MAX_EVIDENCE evidence records are kept, in the order the logs listed them.
    """
    out: dict[tuple, Finding] = {}
    for f in findings:
        key = (f.rule_id, f.src_ip, f.dst_ip, f.dst_port)
        if key in out:
            g = out[key]
            g.count += f.count
            g.first_seen = min(g.first_seen, f.first_seen)
            g.last_seen = max(g.last_seen, f.last_seen)
            room = max(0, MAX_EVIDENCE - len(g.evidence))
            g.evidence.extend(f.evidence[:room])
        else:
            del f.evidence[MAX_EVIDENCE:]
            out[key] = f
    return list(out.values())


def run_all(log_dir: Path) -> list[Finding]:
    """Run every registered rule in rule_id order and merge the results."""
    found: list[Finding] = []
    for rule_id in sorted(RULES):
        found.extend(RULES[rule_id](log_dir))
    return merge(found)
```

**Step 6.** Create an **empty** file `maxguard/mapping/__init__.py`, then the Contract 2 loader `maxguard/mapping/loader.py`:

```python
"""Contract 2 loader: applies mappings/*.yaml to findings.

The YAML schema is the Fall 2026 one (framework, version, source, mappings ->
rule_id -> list of {control_id, title, rationale}). v2.0 adds two optional row
keys: `tactic` (used only by the ATT&CK file) and `verified` (where in the
source document the row was checked, e.g. "p. 112").

The file whose framework is "MITRE ATT&CK" fills Finding.attack; every other
file fills Finding.controls.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from maxguard.models import Control, Finding, Technique

ATTACK = "MITRE ATT&CK"
REQUIRED_TOP = ("framework", "version", "source", "mappings")
REQUIRED_ROW = ("control_id", "title", "rationale")


def load_all(mapping_dir: Path) -> list[dict]:
    """Load every mapping file, sorted by file name so the order never changes."""
    return [yaml.safe_load(p.read_text()) for p in sorted(mapping_dir.glob("*.yaml"))]


def validate(fw: dict, known_rule_ids: set[str]) -> list[str]:
    """Return a list of problems in one mapping file (empty list means valid)."""
    problems = [f"missing top-level key {k!r}" for k in REQUIRED_TOP if k not in fw]
    for rule_id, rows in (fw.get("mappings") or {}).items():
        if rule_id not in known_rule_ids:
            problems.append(f"unknown rule_id {rule_id!r}")
        for i, row in enumerate(rows or []):
            for k in REQUIRED_ROW:
                if not str(row.get(k, "")).strip():
                    problems.append(f"{rule_id}[{i}] missing {k!r}")
            if fw.get("framework") == ATTACK and not row.get("tactic"):
                problems.append(f"{rule_id}[{i}] missing 'tactic' (required for ATT&CK)")
    return problems


def apply(findings: list[Finding], frameworks: list[dict], selected: set[str] | None = None):
    """Attach controls (and ATT&CK techniques) to each finding, in place."""
    for fw in frameworks:
        is_attack = fw["framework"] == ATTACK
        if selected and not is_attack and fw["framework"] not in selected:
            continue
        for f in findings:
            for row in fw["mappings"].get(f.rule_id, []):
                if is_attack:
                    f.attack.append(
                        Technique(row["control_id"], row["title"], row["tactic"], fw["version"])
                    )
                else:
                    f.controls.append(
                        Control(fw["framework"], fw["version"], row["control_id"],
                                row["title"], row["rationale"])
                    )
    return findings
```

**Step 7.** Create the tests `tests/unit/test_contracts.py`:

```python
"""Contract 1 (Finding), the record IDs, and Contract 2's loader (JAI-02).

These tests protect the promises other modules rely on: the original Fall 2026
fields still work, IDs never change for the same input, and mapping files fill
controls and ATT&CK techniques.
"""

import pytest

from maxguard.ids import evidence, record_id
from maxguard.mapping.loader import apply, validate
from maxguard.models import Evidence, Finding, make_finding_id

TELNET = {"ts": 1791250285.789302, "uid": "CthjcT337OAZB44O4f", "id.orig_h": "172.18.0.3",
          "id.orig_p": 55398, "id.resp_h": "172.18.0.2", "id.resp_p": 23,
          "service": "", "proto": "telnet"}


def make_finding(**changes) -> Finding:
    values = dict(rule_id="cleartext.telnet", title="Telnet session in cleartext",
                  severity="high", src_ip="172.18.0.3", dst_ip="172.18.0.2", dst_port=23,
                  protocol="telnet", first_seen=1.0, last_seen=2.0)
    values.update(changes)
    return Finding(**values)


# ---- Contract 1: Finding ----

def test_original_positional_fields_still_work():
    # Exactly how the Fall 2026 roadmap created findings: positional arguments.
    f = Finding("cleartext.telnet", "Telnet", "high", "10.0.0.1", "10.0.0.2", 23,
                "telnet", 1.0, 2.0)
    assert f.count == 1 and f.evidence == [] and f.controls == [] and f.explanation is None


def test_new_fields_have_defaults():
    f = make_finding()
    assert f.source == "zeek"
    assert f.attack == [] and f.explanation_sentences == []


def test_finding_id_is_computed_from_the_dedup_key():
    f = make_finding()
    assert f.finding_id == make_finding_id("cleartext.telnet", "172.18.0.3", "172.18.0.2", 23)
    assert len(f.finding_id) == 16
    assert make_finding(first_seen=99.0).finding_id == f.finding_id  # times are not in the key


def test_a_misspelled_severity_fails_immediately():
    with pytest.raises(ValueError, match="severity"):
        make_finding(severity="hgih")


def test_to_dict_includes_old_and_new_fields():
    d = make_finding(evidence=[Evidence("conn.log", "C1", 1.0, "abc")]).to_dict()
    assert d["evidence"][0] == {"log": "conn.log", "uid": "C1", "ts": 1.0, "record_id": "abc"}
    assert {"finding_id", "attack", "explanation_sentences", "source"} <= d.keys()


# ---- record IDs ----

def test_record_id_is_stable_and_ignores_key_order():
    shuffled = dict(reversed(list(TELNET.items())))
    assert record_id("maxguard_cleartext.log", TELNET) == record_id("maxguard_cleartext.log",
                                                                    shuffled)


def test_record_id_depends_on_the_log_name_and_content():
    assert record_id("a.log", TELNET) != record_id("b.log", TELNET)
    assert record_id("a.log", TELNET) != record_id("a.log", {**TELNET, "id.resp_p": 24})


def test_record_id_ignores_suricatas_random_flow_id():
    eve = {"timestamp": "2026-10-06T01:31:25.789302+0000", "community_id": "1:abc=",
           "event_type": "flow"}
    assert record_id("eve.json", {**eve, "flow_id": 1}) == record_id("eve.json",
                                                                    {**eve, "flow_id": 2})


def test_evidence_for_a_zeek_record():
    e = evidence("maxguard_cleartext.log", TELNET)
    assert (e.log, e.uid, e.ts) == ("maxguard_cleartext.log", "CthjcT337OAZB44O4f",
                                    1791250285.789302)
    assert e.record_id == record_id("maxguard_cleartext.log", TELNET)


def test_evidence_for_a_suricata_record_uses_the_community_id():
    eve = {"timestamp": "2026-10-06T01:31:25.789302+0000", "flow_id": 7,
           "community_id": "1:4o5Au3/nA2pOwrsX1D6xTgHOOr4=", "event_type": "flow"}
    e = evidence("eve.json", eve)
    assert e.uid == "1:4o5Au3/nA2pOwrsX1D6xTgHOOr4="
    assert e.ts == pytest.approx(1791250285.789302)


# ---- Contract 2: mapping loader ----

PCI = {"framework": "PCI DSS", "version": "4.0.1", "source": "https://example.invalid/pci",
       "mappings": {"cleartext.telnet": [
           {"control_id": "4.2.1", "title": "A title", "rationale": "A reason."}]}}
ATTACK = {"framework": "MITRE ATT&CK", "version": "v19.2", "source": "https://example.invalid/a",
          "mappings": {"cleartext.telnet": [
              {"control_id": "T1040", "title": "Network Sniffing", "rationale": "A reason.",
               "tactic": "credential-access"}]}}


def test_apply_fills_controls_and_attack_techniques():
    f = make_finding()
    apply([f], [PCI, ATTACK])
    assert [(c.framework, c.version, c.control_id) for c in f.controls] == [
        ("PCI DSS", "4.0.1", "4.2.1")]
    assert [(t.technique_id, t.tactic, t.version) for t in f.attack] == [
        ("T1040", "credential-access", "v19.2")]


def test_selecting_frameworks_never_drops_attack():
    f = make_finding()
    apply([f], [PCI, ATTACK], selected={"NIST SP 800-53"})
    assert f.controls == [] and len(f.attack) == 1


def test_validate_reports_problems():
    broken = {"framework": "MITRE ATT&CK", "version": "v19.2", "source": "x",
              "mappings": {"no.such_rule": [{"control_id": "T1040", "title": "",
                                              "rationale": "r"}]}}
    problems = validate(broken, known_rule_ids={"cleartext.telnet"})
    assert "unknown rule_id 'no.such_rule'" in problems
    assert any("missing 'title'" in p for p in problems)
    assert any("missing 'tactic'" in p for p in problems)
    assert validate(PCI, known_rule_ids={"cleartext.telnet"}) == []
```

**Step 8.** Run them:

```bash
pytest tests/unit/test_contracts.py -q
```

Expected output:

```text
.............                                                                                [100%]
13 passed in 0.05s
```

**Step 9.** Commit, push, and open the pull request:

```bash
git add -A
git status          # only this task's files: nothing from .venv/, data/ or lab/captures/
git commit -m "feat: contracts v2.0 - Finding, IDs, adapter protocol, registry, loader (JAI-02)"
git push -u origin HEAD
```

`HEAD` means "the branch I am on", so you do not have to retype its name. Open the repository on github.com: a yellow bar shows your branch with a **Compare & pull request** button. Click it, keep the title `feat: contracts v2.0 - Finding, IDs, adapter protocol, registry, loader (JAI-02)`, fill in the template (paste the real output of the commands above under **How I tested it**), write `Closes #<issue number>` (this task's issue), and pick **@ahmadalkhoudeir** under **Reviewers**. Click **Create pull request**, then fix anything CI or the reviewer finds with new commits on the same branch.

**Step 10.** Announce the merge in GitHub Discussions (category **Announcements**, title `Contracts v2.0 merged`) with a link to `docs/ARCHITECTURE.md` section 5. From now on, a contract change needs a pull request with the `contract-change` label, reviewed by you and approved by Ahmad.

#### How to test

`14 passed` means: the original Fall 2026 way of creating a `Finding` still works, IDs are stable, a misspelled severity fails at once, Suricata's random `flow_id` does not change a record ID, and mapping files fill both controls and ATT&CK techniques. Also run `ruff check .` (must print `All checks passed!`).

#### What you just did and why

Eight people write code in parallel. If the shape of a finding changed every week, every module would break every week. Freezing these few files first lets everyone work against the same definitions from day one. The v2.0 additions all have default values, so code written for the Fall 2026 roadmap (and the code in the archived roadmap) still runs. The IDs are hashes of content, not counters or random numbers, so the same capture always produces the same IDs — the AI cites them and the alert queue tracks them (CLAUDE.md rules 2 and 3).

#### Pull request checklist

- [ ] `ruff check .` prints `All checks passed!`
- [ ] `pytest -m "not integration" -q` passes on your laptop
- [ ] The pull request title has the form `type: summary (TASK-ID)` and the body says `Closes #<issue number>`
- [ ] No secrets, passwords, email addresses, personal data, or captures from a real network (CLAUDE.md rule 6)
- [ ] Any new dependency has a row in `docs/DEPENDENCIES.md` with its license
- [ ] CI is green and your reviewer approved
- [ ] The pull request has the `contract-change` label and Ahmad's approval
- [ ] Announcement posted in Discussions

### JAI-03: Common event schema: the normalizer and record lookup

**Due:** Week 1 (due Fri Oct 16) · **Milestone:** `W1 Building blocks` · **Needs first:** [JAI-02](#jai-02-merge-the-three-contracts-in-their-v20-form), [KAR-02](karthik.md#kar-02-test-fixtures-zeek-and-suricata-output-for-every-capture), [FIO-01](fiona.md#fio-01-zeek-runner-and-the-two-input-adapters), [FIO-02](fiona.md#fio-02-tls-and-certificate-rules), [JAK-03](jakub.md#jak-03-cleartext-and-rdp-rules-the-rule-set-is-complete) · **Kind:** code, tested

**Issue labels:** `type:task` `phase:alpha` `owner:jaiden` `area:engine` `area:storage` `critical-path`

#### Goal

Turn Zeek logs and Suricata's `eve.json` into one list of events with the same keys, whatever tool wrote them (`docs/ARCHITECTURE.md` section 6), and find the raw log records behind evidence IDs so the AI can show them to the model.

#### Prerequisites

JAI-02, KAR-02 (fixtures) and FIO-01 (the log adapter) are merged; the lookup test uses the rules from FIO-02 and JAK-03.

#### Steps

**Step 1.** Update `main` and create your branch for this task (one branch per task):

```bash
cd ~/projects/maxguard
source .venv/bin/activate
git checkout main && git pull
git checkout -b jaiden/event-schema
```

If `source .venv/bin/activate` fails, you have not made the virtual environment yet: do Week 0 section 0.11 first.

**Step 2.** Create `maxguard/events/__init__.py`:

```python
"""Events (v2.0): normalize.py turns Zeek/Suricata logs into common-schema events;
lookup.py finds the raw records behind evidence record_ids."""
```

then `maxguard/events/normalize.py`:

```python
"""Common event schema (v2.0): Zeek logs + Suricata eve.json -> one list of events.

Every event is a flat dict with exactly the keys in EVENT_KEYS, whatever tool
wrote the record, so the timeline, the event store and the inventory never
need to know Zeek's or Suricata's field names.

The output only depends on the log files (no clock, no randomness) and is
sorted by (ts, log, event_id), so the same logs always give the same list.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from maxguard.adapters.base import read_log
from maxguard.ids import iso_to_epoch, record_id

EVENT_KEYS = (
    "event_id", "ts", "sensor_id", "source", "log", "kind", "uid", "community_id",
    "src_ip", "dst_ip", "src_port", "dst_port", "proto", "service",
    "bytes_out", "bytes_in", "device_mac", "summary", "ja4",
)

KNOWN_PROTOS = ("tcp", "udp", "icmp")


# ---------- small helpers ----------

def new_event(log: str, rec: dict, sensor_id: str, source: str, kind: str, ts: float) -> dict:
    """An event with every key present; the converters below fill in what they know."""
    return {
        "event_id": record_id(log, rec), "ts": ts, "sensor_id": sensor_id,
        "source": source, "log": log, "kind": kind, "uid": "", "community_id": "",
        "src_ip": "", "dst_ip": "", "src_port": None, "dst_port": None,
        "proto": "", "service": "", "bytes_out": 0, "bytes_in": 0,
        "device_mac": "", "summary": "", "ja4": "",
    }


def as_int(value: object) -> int | None:
    """Zeek JSON logs hold numbers, but logs converted from TSV hold strings ("443")."""
    if value is None or value == "":
        return None
    return int(value)


def as_list(value: object) -> list[str]:
    """Zeek JSON logs hold lists, but TSV-converted logs hold one "a,b,c" string."""
    if value is None:
        return []
    if isinstance(value, str):
        return value.split(",")
    return [str(item) for item in value]


def proto_name(value: object) -> str:
    """"tcp", "udp", "icmp" or "". Suricata writes "TCP" and "IPv6-ICMP"."""
    name = str(value or "").lower()
    if name == "ipv6-icmp":
        return "icmp"
    return name if name in KNOWN_PROTOS else ""


def words(*parts: object) -> str:
    """Join the non-empty parts with spaces (for the short summary text)."""
    return " ".join(str(part) for part in parts if part not in (None, ""))


# ---------- Zeek logs ----------

def zeek_event(log: str, rec: dict, sensor_id: str, kind: str, service: str) -> dict:
    """The fields that conn, dns, http and ssl logs share: uid and the id.* 4-tuple."""
    event = new_event(log, rec, sensor_id, "zeek", kind, float(rec["ts"]))
    event["uid"] = rec.get("uid") or ""
    event["community_id"] = rec.get("community_id") or ""
    event["src_ip"] = rec.get("id.orig_h") or ""
    event["dst_ip"] = rec.get("id.resp_h") or ""
    event["src_port"] = as_int(rec.get("id.orig_p"))
    event["dst_port"] = as_int(rec.get("id.resp_p"))
    event["proto"] = proto_name(rec.get("proto"))  # http.log/ssl.log: filled from conn.log later
    event["service"] = service
    return event


def from_conn(rec: dict, sensor_id: str) -> dict:
    event = zeek_event("conn.log", rec, sensor_id, "conn", rec.get("service") or "")
    # Only conn events carry byte counts, so adding up bytes never counts twice.
    event["bytes_out"] = as_int(rec.get("orig_bytes")) or 0
    event["bytes_in"] = as_int(rec.get("resp_bytes")) or 0
    event["summary"] = words(f"{event['proto']}/{event['dst_port']}", event["service"],
                             rec.get("conn_state"), f"out={event['bytes_out']}",
                             f"in={event['bytes_in']}")
    return event


def from_dns(rec: dict, sensor_id: str) -> dict:
    event = zeek_event("dns.log", rec, sensor_id, "dns", "dns")
    answers = ",".join(as_list(rec.get("answers")))
    event["summary"] = words(rec.get("qtype_name"), rec.get("query"),
                             rec.get("rcode_name"), answers)
    return event


def from_http(rec: dict, sensor_id: str) -> dict:
    event = zeek_event("http.log", rec, sensor_id, "http", "http")
    event["summary"] = words(rec.get("method"), f"{rec.get('host') or ''}{rec.get('uri') or ''}")
    return event


def from_ssl(rec: dict, sensor_id: str) -> dict:
    # Zeek calls the TLS service "ssl" (conn.log service "ssl"), the event kind is "tls".
    event = zeek_event("ssl.log", rec, sensor_id, "tls", "ssl")
    event["summary"] = words(rec.get("version"), rec.get("server_name"), rec.get("cipher"))
    return event


def from_dhcp(rec: dict, sensor_id: str) -> dict:
    # dhcp.log is different: no id.* fields and no ports (Zeek does not log them),
    # and one record groups several packets, so it has a set of uids.
    event = new_event("dhcp.log", rec, sensor_id, "zeek", "dhcp", float(rec["ts"]))
    uids = sorted(as_list(rec.get("uids")))  # sorted: a set has no fixed order
    event["uid"] = uids[0] if uids else ""
    # Before the lease the client has no address yet; the assigned one is its new IP.
    event["src_ip"] = rec.get("client_addr") or rec.get("assigned_addr") or ""
    event["dst_ip"] = rec.get("server_addr") or ""
    event["proto"] = "udp"
    event["service"] = "dhcp"
    event["device_mac"] = rec.get("mac") or ""
    assigned = rec.get("assigned_addr")
    event["summary"] = words("/".join(as_list(rec.get("msg_types"))), event["device_mac"],
                             rec.get("host_name"), f"-> {assigned}" if assigned else "")
    return event


ZEEK_LOGS: dict[str, Callable[[dict, str], dict]] = {
    "conn.log": from_conn,
    "dns.log": from_dns,
    "http.log": from_http,
    "ssl.log": from_ssl,
    "dhcp.log": from_dhcp,
}


# ---------- Suricata eve.json ----------

def eve_event(rec: dict, sensor_id: str, kind: str) -> dict:
    """The fields every eve.json record shares. Suricata has no Zeek uid."""
    event = new_event("eve.json", rec, sensor_id, "suricata", kind,
                      iso_to_epoch(rec["timestamp"]))
    event["community_id"] = rec.get("community_id") or ""
    event["src_ip"] = rec.get("src_ip") or ""
    event["dst_ip"] = rec.get("dest_ip") or ""
    event["src_port"] = as_int(rec.get("src_port"))
    event["dst_port"] = as_int(rec.get("dest_port"))
    event["proto"] = proto_name(rec.get("proto"))
    event["service"] = rec.get("app_proto") or ""
    return event


def from_eve_alert(rec: dict, sensor_id: str) -> dict:
    event = eve_event(rec, sensor_id, "alert")
    alert = rec.get("alert") or {}
    event["summary"] = words(alert.get("signature"), f"(sid {alert.get('signature_id')})")
    return event


def from_eve_tls(rec: dict, sensor_id: str) -> dict:
    # Kept even though Zeek's ssl.log covers TLS: only Suricata computes JA4.
    event = eve_event(rec, sensor_id, "tls")
    tls = rec.get("tls") or {}
    event["service"] = event["service"] or "tls"
    event["ja4"] = tls.get("ja4") or ""
    event["summary"] = words(tls.get("version"), tls.get("sni"),
                             f"ja4={event['ja4']}" if event["ja4"] else "")
    return event


def dns_question(dns: dict) -> dict:
    """Suricata 7 (eve dns version 2) puts rrname/rrtype at the top of "dns";
    Suricata 8 (version 3) puts them in a "queries" list."""
    if "rrname" in dns:
        return dns
    queries = dns.get("queries") or [{}]
    return queries[0]


def from_eve_dns(rec: dict, sensor_id: str) -> dict:
    event = eve_event(rec, sensor_id, "dns")
    dns = rec.get("dns") or {}
    question = dns_question(dns)
    answers = ",".join(str(a.get("rdata", "")) for a in dns.get("answers") or [])
    event["service"] = event["service"] or "dns"
    event["summary"] = words(dns.get("type"), question.get("rrtype"), question.get("rrname"),
                             dns.get("rcode"), answers)
    return event


def from_eve_dhcp(rec: dict, sensor_id: str) -> dict:
    event = eve_event(rec, sensor_id, "dhcp")
    dhcp = rec.get("dhcp") or {}
    assigned = dhcp.get("assigned_ip")
    event["service"] = event["service"] or "dhcp"
    event["device_mac"] = dhcp.get("client_mac") or ""
    event["summary"] = words(dhcp.get("dhcp_type"), event["device_mac"], dhcp.get("hostname"),
                             f"-> {assigned}" if assigned else "")
    return event


# "flow" is left out on purpose: Zeek's conn.log already has one event per connection.
EVE_TYPES: dict[str, Callable[[dict, str], dict]] = {
    "alert": from_eve_alert,
    "tls": from_eve_tls,
    "dns": from_eve_dns,
    "dhcp": from_eve_dhcp,
}


# ---------- putting it together ----------

def fill_from_conn(events: list[dict]) -> None:
    """Zeek writes community_id only in conn.log, and http.log/ssl.log have no proto.
    Copy both from the conn event of the same connection (same uid), so every Zeek
    event lines up with the Suricata events of that connection."""
    conns = {e["uid"]: e for e in events if e["log"] == "conn.log" and e["uid"]}
    for event in events:
        conn = conns.get(event["uid"])
        if conn is not None:
            event["community_id"] = event["community_id"] or conn["community_id"]
            event["proto"] = event["proto"] or conn["proto"]


def normalize(log_dir: Path, sensor_id: str) -> list[dict]:
    """One event per record of the logs we know. Missing log files are simply skipped."""
    log_dir = Path(log_dir)
    events: list[dict] = []
    for log_name, convert in ZEEK_LOGS.items():
        for rec in read_log(log_dir, log_name):
            events.append(convert(rec, sensor_id))
    for rec in read_log(log_dir, "eve.json"):
        convert = EVE_TYPES.get(rec.get("event_type"))
        if convert is not None:
            events.append(convert(rec, sensor_id))
    fill_from_conn(events)
    events.sort(key=lambda e: (e["ts"], e["log"], e["event_id"]))
    return events
```

**Step 3.** Create `maxguard/events/lookup.py`:

```python
"""Find the raw log records behind evidence record_ids (v2.0).

A finding only stores record_ids (see maxguard.ids). When the AI explains a
finding it must see the actual records, so this module scans the log folder,
recomputes each record's ID and keeps the ones that were asked for.
"""

from __future__ import annotations

from pathlib import Path

from maxguard.adapters.base import read_log
from maxguard.ids import record_id


def log_names(log_dir: Path) -> list[str]:
    """Every Zeek *.log plus Suricata's eve.json, in a fixed (sorted) order."""
    names = sorted(p.name for p in log_dir.glob("*.log"))
    if (log_dir / "eve.json").exists():
        names.append("eve.json")
    return names


def records_for(log_dir: Path, record_ids: set[str]) -> dict[str, dict]:
    """Map each requested record_id to its raw record, with a "_log" key added
    (e.g. "ssl.log") so the reader knows where it came from. IDs that are not
    found are simply missing from the result."""
    log_dir = Path(log_dir)
    wanted = set(record_ids)
    found: dict[str, dict] = {}
    for log_name in log_names(log_dir):
        if len(found) == len(wanted):
            break  # everything found: no need to read the remaining logs
        for rec in read_log(log_dir, log_name):
            rid = record_id(log_name, rec)  # hash the record before adding "_log"
            if rid in wanted:
                found[rid] = {**rec, "_log": log_name}
    return found
```

**Step 4.** Create the tests `tests/unit/test_normalize.py`:

```python
"""Tests for maxguard.events.normalize (common event schema)."""

import shutil
from pathlib import Path

import pytest

from maxguard.adapters.base import read_log
from maxguard.adapters.zeeklogs import ZeekLogAdapter
from maxguard.events.normalize import EVENT_KEYS, as_int, as_list, normalize, proto_name
from maxguard.ids import record_id

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "zeek"
HANDMADE = FIXTURES / "_handmade"
CAPTURES = sorted(p.name for p in FIXTURES.iterdir() if p.is_dir() and not p.name.startswith("_"))
ALL_DIRS = [FIXTURES / name for name in CAPTURES] + [
    HANDMADE / "dns_dhcp", HANDMADE / "dns_dhcp_suricata8"]


def by_log(events: list[dict], log: str) -> list[dict]:
    return [e for e in events if e["log"] == log]


@pytest.mark.parametrize("log_dir", ALL_DIRS, ids=lambda p: p.name)
def test_every_event_has_exactly_the_schema(log_dir):
    events = normalize(log_dir, sensor_id="pcap")
    assert events, "every fixture has at least one event"
    for e in events:
        assert tuple(e) == EVENT_KEYS
        assert isinstance(e["event_id"], str) and len(e["event_id"]) == 16
        assert isinstance(e["ts"], float)
        assert e["sensor_id"] == "pcap"
        assert e["source"] in ("zeek", "suricata")
        assert e["kind"] in ("conn", "dns", "http", "tls", "dhcp", "alert")
        assert e["proto"] in ("tcp", "udp", "icmp", "")
        for port in (e["src_port"], e["dst_port"]):
            assert port is None or isinstance(port, int)
        assert isinstance(e["bytes_out"], int) and isinstance(e["bytes_in"], int)
        for key in ("uid", "community_id", "src_ip", "dst_ip", "service",
                    "device_mac", "summary", "ja4"):
            assert isinstance(e[key], str)


@pytest.mark.parametrize("log_dir", ALL_DIRS, ids=lambda p: p.name)
def test_output_is_sorted_and_the_same_every_time(log_dir):
    first = normalize(log_dir, sensor_id="pcap")
    assert first == normalize(log_dir, sensor_id="pcap")
    keys = [(e["ts"], e["log"], e["event_id"]) for e in first]
    assert keys == sorted(keys)


def test_event_id_is_the_record_id_of_the_raw_record():
    rec = next(read_log(FIXTURES / "plain_http", "http.log"))
    [http] = by_log(normalize(FIXTURES / "plain_http", "pcap"), "http.log")
    assert http["event_id"] == record_id("http.log", rec)


def test_plain_http_conn_and_http_events():
    events = normalize(FIXTURES / "plain_http", sensor_id="pcap")
    # eve.json has only "http" and "flow" records here: both are skipped
    assert [e["log"] for e in events] == ["conn.log", "http.log"]
    conn, http = events
    assert conn["kind"] == "conn" and conn["service"] == "http"
    assert (conn["src_ip"], conn["src_port"], conn["dst_ip"], conn["dst_port"]) == (
        "172.18.0.3", 40288, "172.18.0.2", 80)
    assert (conn["bytes_out"], conn["bytes_in"]) == (113, 924)
    assert conn["summary"] == "tcp/80 http SF out=113 in=924"
    assert http["summary"] == "GET server:80/"
    # http.log has no community_id and no proto: both are copied from conn.log (same uid)
    assert http["uid"] == conn["uid"] == "CJKFoj4bpHEhTeaRoj"
    assert http["community_id"] == conn["community_id"] == "1:Zd6w43plhlSu6wAgAknKxXblpcw="
    assert http["proto"] == "tcp"
    assert (http["bytes_out"], http["bytes_in"]) == (0, 0)  # only conn events count bytes


def test_tls_events_from_zeek_and_suricata():
    events = normalize(FIXTURES / "tls_weak_version", sensor_id="pcap")
    [ssl] = by_log(events, "ssl.log")
    [eve_tls] = by_log(events, "eve.json")
    assert ssl["kind"] == eve_tls["kind"] == "tls"
    assert ssl["summary"] == "TLSv10 port4431.lab.invalid TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA"
    assert ssl["ja4"] == ""
    assert eve_tls["source"] == "suricata" and eve_tls["uid"] == ""
    assert eve_tls["ja4"] == "t10d230600_44099cda8a52_242d16716555"
    assert eve_tls["summary"] == (
        "TLSv1 port4431.lab.invalid ja4=t10d230600_44099cda8a52_242d16716555")
    # Zeek and Suricata agree on the community id, so the two events can be joined
    assert eve_tls["community_id"] == ssl["community_id"] == "1:pRvdZyOxcG+AIDBGMFce8LVpI/I="


def test_zeek_dns_and_dhcp():
    events = normalize(HANDMADE / "dns_dhcp", sensor_id="pcap")
    [dns] = by_log(events, "dns.log")
    assert dns["summary"] == "A printer.lab.invalid NOERROR 192.168.56.20"
    assert (dns["proto"], dns["service"], dns["dst_port"]) == ("udp", "dns", 53)
    [dhcp] = by_log(events, "dhcp.log")
    assert dhcp["device_mac"] == "02:00:00:aa:bb:cc"
    assert (dhcp["src_ip"], dhcp["dst_ip"]) == ("192.168.56.50", "192.168.56.1")
    assert (dhcp["src_port"], dhcp["dst_port"]) == (None, None)  # dhcp.log logs no ports
    assert dhcp["uid"] == "CJKFoj4bpHEhTeaRoj"  # smallest of the record's uids
    assert dhcp["summary"] == (
        "DISCOVER/OFFER/REQUEST/ACK 02:00:00:aa:bb:cc laptop-lab -> 192.168.56.50")


def test_suricata_7_alert_dns_and_dhcp():
    events = by_log(normalize(HANDMADE / "dns_dhcp", sensor_id="pcap"), "eve.json")
    summaries = {(e["kind"], e["summary"]) for e in events}
    assert summaries == {
        ("dhcp", "ack 02:00:00:aa:bb:cc -> 192.168.56.50"),
        ("alert", "MaxGuard fixture: DNS lookup of a lab.invalid name (sid 9000001)"),
        ("dns", "query A printer.lab.invalid"),
        ("dns", "answer A printer.lab.invalid NOERROR 192.168.56.20"),
    }  # the three "flow" records are skipped
    [dhcp] = [e for e in events if e["kind"] == "dhcp"]
    assert dhcp["device_mac"] == "02:00:00:aa:bb:cc"
    [alert] = [e for e in events if e["kind"] == "alert"]
    assert (alert["proto"], alert["service"]) == ("udp", "dns")


def test_suricata_8_dns_format_is_understood_too():
    events = normalize(HANDMADE / "dns_dhcp_suricata8", sensor_id="sensor-1")
    dns = [e["summary"] for e in events if e["kind"] == "dns"]
    assert dns == ["request A printer.lab.invalid NOERROR",
                   "response A printer.lab.invalid NOERROR 192.168.56.20"]
    assert {e["sensor_id"] for e in events} == {"sensor-1"}


def test_absent_logs_give_no_events(tmp_path):
    assert normalize(tmp_path, sensor_id="pcap") == []


def test_ssl_log_alone_still_works(tmp_path):
    shutil.copy(FIXTURES / "tls_weak_version" / "ssl.log", tmp_path / "ssl.log")
    [event] = normalize(tmp_path, sensor_id="pcap")
    assert event["kind"] == "tls"
    assert event["proto"] == "" and event["community_id"] == ""  # no conn.log to copy from


@pytest.mark.parametrize("tsv_dir, json_dir", [
    (HANDMADE / "tsv_plain_http", FIXTURES / "plain_http"),
    (HANDMADE / "tsv_dns_dhcp", HANDMADE / "dns_dhcp"),
], ids=["plain_http", "dns_dhcp"])
def test_tsv_logs_give_the_same_events_as_json_logs(tmp_path, tsv_dir, json_dir):
    # The ZeekLogAdapter turns TSV into JSON where every value is a string ("443").
    converted = ZeekLogAdapter().to_zeek_logs(tsv_dir, tmp_path)
    from_tsv = normalize(converted, sensor_id="import")
    from_json = [e for e in normalize(json_dir, sensor_id="import") if e["source"] == "zeek"]

    def without_event_id(events):  # event_id hashes the raw text, which differs
        return [{k: v for k, v in e.items() if k != "event_id"} for e in events]

    assert len(from_tsv) >= 2
    assert all(isinstance(e["dst_port"], int) for e in from_tsv if e["log"] != "dhcp.log")
    assert without_event_id(from_tsv) == without_event_id(from_json)


def test_helpers():
    assert as_int("443") == 443 and as_int(443) == 443
    assert as_int(None) is None and as_int("") is None
    assert as_list(["a", "b"]) == ["a", "b"] and as_list("a,b") == ["a", "b"]
    assert as_list(None) == []
    assert proto_name("TCP") == "tcp" and proto_name("udp") == "udp"
    assert proto_name("IPv6-ICMP") == "icmp"  # Suricata's name for ICMPv6
    assert proto_name("unknown_transport") == "" and proto_name(None) == ""
```

and `tests/unit/test_lookup.py`:

```python
"""Tests for maxguard.events.lookup.records_for (evidence record_id -> raw record)."""

from pathlib import Path

import maxguard.rules  # noqa: F401  (importing registers every rule)
from maxguard.adapters.base import read_log
from maxguard.events.lookup import log_names, records_for
from maxguard.ids import record_id
from maxguard.rules.base import run_all

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "zeek"


def test_finds_the_evidence_records_of_a_finding():
    log_dir = FIXTURES / "cert_expired"
    [finding] = run_all(log_dir)
    wanted = {ev.record_id for ev in finding.evidence}

    records = records_for(log_dir, wanted)

    assert set(records) == wanted
    assert sorted(rec["_log"] for rec in records.values()) == ["ssl.log", "x509.log"]
    for rid, rec in records.items():
        raw = {k: v for k, v in rec.items() if k != "_log"}
        assert record_id(rec["_log"], raw) == rid  # "_log" is added after hashing


def test_finds_suricata_records_too():
    log_dir = FIXTURES / "tls_weak_version"
    tls = next(r for r in read_log(log_dir, "eve.json") if r["event_type"] == "tls")
    rid = record_id("eve.json", tls)

    records = records_for(log_dir, {rid})

    assert records[rid]["_log"] == "eve.json"
    assert records[rid]["tls"]["ja4"] == "t10d230600_44099cda8a52_242d16716555"


def test_unknown_ids_are_left_out():
    log_dir = FIXTURES / "telnet"
    rec = next(read_log(log_dir, "maxguard_cleartext.log"))
    rid = record_id("maxguard_cleartext.log", rec)

    records = records_for(log_dir, {rid, "0000000000000000"})

    assert list(records) == [rid]


def test_no_ids_and_empty_folder_give_empty_result(tmp_path):
    assert records_for(FIXTURES / "telnet", set()) == {}
    assert records_for(tmp_path, {"0000000000000000"}) == {}


def test_log_names_are_sorted_with_eve_json_last():
    assert log_names(FIXTURES / "telnet") == [
        "conn.log", "known_hosts.log", "maxguard_cleartext.log", "eve.json"]
```

**Step 5.** Run them:

```bash
pytest tests/unit/test_normalize.py tests/unit/test_lookup.py -q
```

Expected output:

```text
................................................                                             [100%]
48 passed in 0.17s
```

**Step 6.** Commit, push, and open the pull request:

```bash
git add -A
git status          # only this task's files: nothing from .venv/, data/ or lab/captures/
git commit -m "feat: common event schema normalizer and record lookup (JAI-03)"
git push -u origin HEAD
```

`HEAD` means "the branch I am on", so you do not have to retype its name. Open the repository on github.com: a yellow bar shows your branch with a **Compare & pull request** button. Click it, keep the title `feat: common event schema normalizer and record lookup (JAI-03)`, fill in the template (paste the real output of the commands above under **How I tested it**), write `Closes #<issue number>` (this task's issue), and pick **@ahmadalkhoudeir** under **Reviewers**. Click **Create pull request**, then fix anything CI or the reviewer finds with new commits on the same branch.

#### How to test

Both test files pass. The normalizer tests cover every lab capture, DNS and DHCP records, Suricata 7 and 8 DNS formats, and TSV-converted logs.

#### What you just did and why

The timeline, the event store, preview-before-you-block, and the inventory all need "what happened on the network" in one shape. Without a common schema each of them would have to know both Zeek's and Suricata's field names. Copying `community_id` from `conn.log` to the other Zeek events is what lets a Zeek event and a Suricata event about the same connection be shown together.

#### Pull request checklist

- [ ] `ruff check .` prints `All checks passed!`
- [ ] `pytest -m "not integration" -q` passes on your laptop
- [ ] The pull request title has the form `type: summary (TASK-ID)` and the body says `Closes #<issue number>`
- [ ] No secrets, passwords, email addresses, personal data, or captures from a real network (CLAUDE.md rule 6)
- [ ] Any new dependency has a row in `docs/DEPENDENCIES.md` with its license
- [ ] CI is green and your reviewer approved
- [ ] A change to `EVENT_KEYS` is a contract change (label it)

### JAI-04: The engine image and the Compose files

**Due:** Week 1 (due Fri Oct 16) · **Milestone:** `W1 Building blocks` · **Needs first:** [JAI-01](#jai-01-restructure-the-repository-add-packaging-and-ci), [AMO-01](amory.md#amo-01-nist-sp-800-53-mapping-file-and-the-mapping-checks) · **Kind:** code, written

**Issue labels:** `type:task` `phase:alpha` `owner:jaiden` `area:release` `critical-path`

> **Written, not fully run.** The files in this task were written during planning, but part of them could not be run there (each such step says why). Your run is the first real one: if anything differs, fix this file in your pull request.

#### Goal

Package MaxGuard as a Docker image built on the official Zeek 9.0.0 image, with Suricata, MaxGuard in a virtual environment, and a non-root user, plus the Compose files that run it next to a local Ollama. Integration tests (KAR-03), the Week 2 demo with a capture, and the offline bundle all use this image.

#### Prerequisites

JAI-01 and AMO-01 (the Dockerfile copies `mappings/`) are merged.

#### Steps

**Step 1.** Update `main` and create your branch for this task (one branch per task):

```bash
cd ~/projects/maxguard
source .venv/bin/activate
git checkout main && git pull
git checkout -b jaiden/docker-image
```

If `source .venv/bin/activate` fails, you have not made the virtual environment yet: do Week 0 section 0.11 first.

**Step 2.** Create `docker/Dockerfile`:

```dockerfile
# MaxGuard engine image: Zeek 9.0.0 + Suricata + the maxguard Python package.
#
# Build from the repository root (the "." at the end is the build context):
#   docker build -f docker/Dockerfile -t maxguard:2.0.0a0 .
# Build the test image that CI uses (adds pytest and the tests folder):
#   docker build -f docker/Dockerfile --target test -t maxguard:test .
#
# Stages: "engine" holds everything both images share, "test" adds the tests,
# and "runtime" (the last stage, so the default) is the image users run.
# Everything is installed at build time: the running container never needs
# the internet.

FROM zeek/zeek:9.0.0 AS engine

# The Zeek image is Debian 13 with Python 3.13, but it has no Python venv
# support (python3-venv) and no Suricata. ca-certificates lets pip check
# PyPI's TLS certificate during the build. The apt lists are deleted because
# nothing in the image runs apt again.
RUN apt-get update \
    && apt-get install -y --no-install-recommends python3-venv suricata ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Debian refuses "pip install" into its own Python (PEP 668), so MaxGuard gets
# a virtual environment. Putting it first on PATH makes "python", "pip",
# "uvicorn" and "maxguard" mean the venv versions.
RUN python3 -m venv /opt/venv
# The Zeek image sets PYTHONPATH to "/usr/local/zeek/lib/zeek/python:". The
# empty entry after the ":" means "the current folder", so a .py file in the
# current folder could replace a real module. Keep only Zeek's folder.
ENV PATH="/opt/venv/bin:${PATH}" \
    PYTHONPATH="/usr/local/zeek/lib/zeek/python" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /opt/maxguard
COPY pyproject.toml ./
COPY cli ./cli
COPY maxguard ./maxguard
COPY mappings ./mappings
RUN pip install --no-cache-dir .

# MaxGuard never needs root: Zeek and Suricata only read capture files here.
# A fixed uid keeps the owner of files in the /data volume the same after a
# rebuild. /data holds the databases, event files and custody keys.
RUN useradd --uid 10001 --user-group --create-home --shell /usr/sbin/nologin maxguard \
    && mkdir /data \
    && chown maxguard:maxguard /data
# The mapping files stay a plain folder (Amory edits them on github.com); the
# pipeline finds them through this variable.
ENV MAXGUARD_DATA_DIR=/data \
    MAXGUARD_MAPPINGS_DIR=/opt/maxguard/mappings


FROM engine AS test

COPY tests ./tests
RUN pip install --no-cache-dir ".[dev]"
USER maxguard
# /opt/maxguard belongs to root, so pytest must not try to write its cache there.
ENV PYTEST_ADDOPTS="-p no:cacheprovider"
CMD ["pytest", "-m", "integration", "-q"]


FROM engine AS runtime

USER maxguard
VOLUME ["/data"]
EXPOSE 8000
# Inside the container the server must listen on 0.0.0.0 or the published
# port cannot reach it; compose publishes that port on the host's 127.0.0.1 only.
CMD ["uvicorn", "maxguard.api.app:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
```

Three stages share one base: `engine` (everything), `test` (adds pytest and the tests; CI uses it), and `runtime` (the default; starts the API from JAI-07 — until then, use the image for `maxguard analyze`, `zeek` and `suricata`).

**Step 3.** Create `.dockerignore` in the repository root (it keeps secrets and data out of every image):

```text
# Files Docker never sends to the build. The Dockerfile copies only what it
# needs, but a smaller build context is faster, and secrets listed here can
# never end up inside an image by accident.

# Version control and local tooling
.git
.github
.venv
venv
**/__pycache__
**/*.pyc
.pytest_cache
.ruff_cache

# Runtime data: databases, Parquet files and the custody signing keys
data
**/*.pem
**/*.key

# Not part of the engine image
docs
lab
scripts
docker
```

**Step 4.** Create `docker/compose.yaml`:

```yaml
# MaxGuard: the engine (web dashboard + API) and a local Ollama for AI explanations.
#
# Start:  docker compose -f docker/compose.yaml up -d
# Open:   http://127.0.0.1:8000
# Stop:   docker compose -f docker/compose.yaml down      (volumes and data are kept)
#
# The maxguard:2.0.0a0 image must already exist on this machine, either built with
#   docker build -f docker/Dockerfile -t maxguard:2.0.0a0 .
# or loaded from the offline bundle. For development use compose.dev.yaml.
name: maxguard

services:
  maxguard:
    image: maxguard:2.0.0a0
    ports:
      # Only this computer can open the dashboard; other machines on the network cannot.
      - "127.0.0.1:8000:8000"
    volumes:
      - maxguard-data:/data
    environment:
      OLLAMA_HOST: http://ollama:11434
      MAXGUARD_OFFLINE: "1" # the Python guard blocks any connection except Ollama
    networks:
      - ui
      - ai
    depends_on:
      - ollama
    restart: unless-stopped

  ollama:
    image: ollama/ollama:0.35.1
    volumes:
      - maxguard-ollama-models:/root/.ollama # where this image keeps downloaded models
    networks:
      - ai # only the internal network: Ollama can reach nothing outside
    restart: unless-stopped

networks:
  # A normal network: needed for the published port, and later for reaching
  # the user's own firewall when a block is approved.
  ui: {}
  # internal: true means containers on it have no route to the internet.
  ai:
    internal: true

volumes:
  maxguard-data:
    name: maxguard-data
  # A fixed name (no "maxguard_" project prefix) so the offline installer can
  # put model files into this volume before the first start.
  maxguard-ollama-models:
    name: maxguard-ollama-models
```

and the development overlay `docker/compose.dev.yaml`:

```yaml
# Development override: build the engine from this checkout and run the code
# from the repository folder, restarting the server when a .py file changes.
#
# Use it on top of compose.yaml:
#   docker compose -f docker/compose.yaml -f docker/compose.dev.yaml up --build
#
# Paths here are relative to docker/ (the folder of the first -f file), so ".."
# is the repository root.
services:
  maxguard:
    image: maxguard:dev
    build:
      context: ..
      dockerfile: docker/Dockerfile
      target: runtime
    volumes:
      # Read-only: the container can read your code but never change it.
      - ..:/src:ro
    working_dir: /src
    environment:
      # Import maxguard from /src (your checkout) instead of the copy installed in the image.
      PYTHONPATH: /src
    command:
      - uvicorn
      - maxguard.api.app:create_app
      - --factory
      - --host
      - 0.0.0.0
      - --port
      - "8000"
      - --reload
      - --reload-dir
      - /src/maxguard
```

**Step 5.** Check that both Compose files are valid:

```bash
docker compose -f docker/compose.yaml config --quiet && echo "compose.yaml OK"
docker compose -f docker/compose.yaml -f docker/compose.dev.yaml config --quiet && echo "compose.dev.yaml OK"
```

Expected output:

```text
compose.yaml OK
compose.dev.yaml OK
```

**Step 6.** Build the image and check the tools inside it, with the network off:

```bash
docker build -f docker/Dockerfile -t maxguard:dev .
docker run --rm --network none maxguard:dev zeek --version
docker run --rm --network none maxguard:dev suricata -V
docker run --rm --network none maxguard:dev python -c "import maxguard; print(maxguard.__version__)"
```

Expected output (not run in planning):

```text
zeek version 9.0.0
This is Suricata version 7.0.10 RELEASE
2.0.0a0
```

*Not run in planning: the build installs Debian packages, and Debian's servers were unreachable there. The expected lines are the versions the image is pinned to; if your build fails, post the last 30 lines in Discussions.*

**Step 7.** Commit, push, and open the pull request:

```bash
git add -A
git status          # only this task's files: nothing from .venv/, data/ or lab/captures/
git commit -m "feat: engine image (Zeek, Suricata, MaxGuard) and Compose files (JAI-04)"
git push -u origin HEAD
```

`HEAD` means "the branch I am on", so you do not have to retype its name. Open the repository on github.com: a yellow bar shows your branch with a **Compare & pull request** button. Click it, keep the title `feat: engine image (Zeek, Suricata, MaxGuard) and Compose files (JAI-04)`, fill in the template (paste the real output of the commands above under **How I tested it**), write `Closes #<issue number>` (this task's issue), and pick **@ahmadalkhoudeir** under **Reviewers**. Click **Create pull request**, then fix anything CI or the reviewer finds with new commits on the same branch.

#### How to test

Both Compose files print `OK`; the image prints the three versions with `--network none`. Also check `docker run --rm maxguard:dev id` shows uid 10001.

#### What you just did and why

Zeek and Suricata are hard to install the same way on Windows, macOS and Linux; one image gives every laptop, CI and the release the same tools. Starting from the Zeek project's own image avoids compiling Zeek. A non-root user limits the damage if a malicious capture ever exploited a parser, and the dashboard port is published on `127.0.0.1` only, so other machines on the network cannot reach it.

#### Pull request checklist

- [ ] `ruff check .` prints `All checks passed!`
- [ ] `pytest -m "not integration" -q` passes on your laptop
- [ ] The pull request title has the form `type: summary (TASK-ID)` and the body says `Closes #<issue number>`
- [ ] No secrets, passwords, email addresses, personal data, or captures from a real network (CLAUDE.md rule 6)
- [ ] Any new dependency has a row in `docs/DEPENDENCIES.md` with its license
- [ ] CI is green and your reviewer approved
- [ ] The image builds on your machine and runs as uid 10001

### JAI-05: The pipeline: one function from input to report

**Due:** Week 2 (due Fri Oct 23) · **Milestone:** `W2 First end-to-end demo` · **Needs first:** [FIO-01](fiona.md#fio-01-zeek-runner-and-the-two-input-adapters), [FIO-02](fiona.md#fio-02-tls-and-certificate-rules), [JAK-03](jakub.md#jak-03-cleartext-and-rdp-rules-the-rule-set-is-complete), [JAI-03](#jai-03-common-event-schema-the-normalizer-and-record-lookup), [JAK-04](jakub.md#jak-04-asset-inventory), [AMO-01](amory.md#amo-01-nist-sp-800-53-mapping-file-and-the-mapping-checks) · **Kind:** code, tested

**Issue labels:** `type:task` `phase:alpha` `owner:jaiden` `area:engine` `critical-path`

#### Goal

Write `maxguard/pipeline.py`, the single function the CLI, the API, and the tests call: it picks the right adapter, gets Zeek logs, runs the rules, applies the mapping files, builds the event list and the asset inventory, asks the local AI (when asked to), and returns the report dictionary described in `docs/ARCHITECTURE.md` section 8.

#### Prerequisites

FIO-01 (adapters), FIO-02 and JAK-03 (rules), JAI-03 (normalizer), JAK-04 (inventory) and AMO-01 (mapping files) are merged.

#### Steps

**Step 1.** Update `main` and create your branch for this task (one branch per task):

```bash
cd ~/projects/maxguard
source .venv/bin/activate
git checkout main && git pull
git checkout -b jaiden/pipeline
```

If `source .venv/bin/activate` fails, you have not made the virtual environment yet: do Week 0 section 0.11 first.

**Step 2.** Create `maxguard/pipeline.py`:

```python
"""The one function the CLI, the API, and the tests all call.

analyze() turns a capture file or a folder of Zeek logs into a report dict
(schema "maxguard.report/2", see docs/ARCHITECTURE.md). It never reads the
clock, so the same input always gives the same report.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path

import maxguard.rules  # noqa: F401  (importing registers every rule)
from maxguard.adapters.pcap import PcapAdapter
from maxguard.adapters.zeeklogs import ZeekLogAdapter
from maxguard.mapping.loader import ATTACK, apply, load_all
from maxguard.models import SEVERITIES, Finding
from maxguard.rules.base import run_all

ADAPTERS = [PcapAdapter(), ZeekLogAdapter()]
REPO_MAPPINGS_DIR = Path(__file__).resolve().parent.parent / "mappings"


class UnsupportedInput(ValueError):
    pass


class MappingsNotFound(RuntimeError):
    pass


def mappings_dir() -> Path:
    """Where the mapping YAML files live: $MAXGUARD_MAPPINGS_DIR, else the repo's mappings/.

    The Docker image copies mappings/ to /opt/maxguard/mappings and sets the variable.
    """
    folder = Path(os.environ.get("MAXGUARD_MAPPINGS_DIR", REPO_MAPPINGS_DIR))
    if not any(folder.glob("*.yaml")):
        raise MappingsNotFound(f"no mapping files (*.yaml) in {folder}; "
                               "set MAXGUARD_MAPPINGS_DIR to the mappings/ folder")
    return folder


def pick_adapter(path: Path):
    for adapter in ADAPTERS:
        if adapter.accepts(path):
            return adapter
    raise UnsupportedInput(f"{path.name}: not a pcap/pcapng file or a Zeek log folder/archive")


def sha256_of(path: Path) -> str:
    if path.is_dir():
        return ""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def sort_key(f: Finding):
    return (SEVERITIES.index(f.severity), f.rule_id, f.src_ip, f.dst_ip, f.dst_port)


def analyze(path, workdir, frameworks=None, explain=True, mapping_dir=None) -> dict:
    """1) pick adapter  2) get logs  3) run rules  4) apply mappings
    5) build inventory and events  6) ask the local AI  7) return report dict"""
    path, workdir = Path(path), Path(workdir)
    adapter = pick_adapter(path)
    log_dir = adapter.to_zeek_logs(path, workdir)

    findings = sorted(run_all(log_dir), key=sort_key)

    fw_files = load_all(Path(mapping_dir) if mapping_dir else mappings_dir())
    apply(findings, fw_files, set(frameworks) if frameworks else None)

    from maxguard.events.normalize import normalize
    from maxguard.inventory import build as build_inventory

    events = normalize(log_dir, sensor_id="pcap" if adapter.name == "pcap" else "import")
    assets = build_inventory(log_dir, findings)

    ai = {"status": "disabled", "model": None, "explained": 0, "dropped_sentences": 0,
          "reason": None}
    if explain:
        from maxguard.ai.ollama_client import explain_all

        ai = explain_all(findings, log_dir)

    return {
        "schema": "maxguard.report/2",
        "input": {"name": path.name, "sha256": sha256_of(path), "adapter": adapter.name},
        "tools": {"zeek": adapter.name == "pcap",
                  "suricata": (log_dir / "eve.json").exists()},
        "frameworks": [{"framework": fw["framework"], "version": fw["version"],
                        "source": fw["source"]} for fw in fw_files if fw["framework"] != ATTACK],
        "findings": [f.to_dict() for f in findings],
        "assets": assets,
        "events": events,
        "ai": ai,
    }
```

Two details to notice: the AI client is imported *inside* `if explain:`, so the pipeline works before JON-02 is merged as long as you pass `explain=False`; and the mapping folder comes from `MAXGUARD_MAPPINGS_DIR` (set in the Docker image) or the repository's `mappings/` folder, and a missing folder is an error instead of silently mapping nothing.

**Step 3.** Create the tests `tests/unit/test_pipeline.py`:

```python
"""The pipeline (Jaiden, JAI-03): picking an adapter and producing the report dict.

These tests use the Zeek-log adapter on fixture folders, so they need no Zeek.
tests/integration/ runs real captures through Zeek inside the engine image.
"""

import zipfile
from pathlib import Path

import pytest

from maxguard.pipeline import MappingsNotFound, UnsupportedInput, analyze, pick_adapter

FIXTURES = Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "zeek"


def test_text_file_is_unsupported_input(tmp_path):
    path = tmp_path / "notes.txt"
    path.write_text("hello\n")
    with pytest.raises(UnsupportedInput):
        pick_adapter(path)


def test_zip_of_logs_is_analyzed(tmp_path):
    archive = tmp_path / "telnet_logs.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        for log in sorted((FIXTURES / "telnet").glob("*.log")):
            zf.write(log, arcname=log.name)

    report = analyze(archive, tmp_path / "work", explain=False)

    assert report["input"]["adapter"] == "zeek-logs"
    assert [f["rule_id"] for f in report["findings"]] == ["cleartext.telnet"]


def test_report_has_every_section(tmp_path):
    report = analyze(FIXTURES / "telnet", tmp_path, explain=False)
    assert report["schema"] == "maxguard.report/2"
    assert set(report) == {"schema", "input", "tools", "frameworks", "findings", "assets",
                           "events", "ai"}
    assert report["ai"]["status"] == "disabled"


def test_findings_are_mapped_to_controls(tmp_path):
    [finding] = analyze(FIXTURES / "telnet", tmp_path, explain=False)["findings"]
    assert any(c["framework"] == "NIST SP 800-53" for c in finding["controls"])


def test_same_input_gives_the_same_report(tmp_path):
    first = analyze(FIXTURES / "cert_expired", tmp_path / "a", explain=False)
    second = analyze(FIXTURES / "cert_expired", tmp_path / "b", explain=False)
    assert first == second  # no clock, no randomness (CLAUDE.md rule 2)


def test_missing_mapping_files_fail_loudly(tmp_path, monkeypatch):
    monkeypatch.setenv("MAXGUARD_MAPPINGS_DIR", str(tmp_path / "nothing-here"))
    with pytest.raises(MappingsNotFound):
        analyze(FIXTURES / "telnet", tmp_path / "work", explain=False)
```

**Step 4.** Run them:

```bash
pytest tests/unit/test_pipeline.py -q
```

Expected output:

```text
......                                                                                       [100%]
6 passed in 0.18s
```

**Step 5.** Try it yourself on a fixture folder (Zeek-log input needs no Zeek):

```bash
python -c "from maxguard.pipeline import analyze; import json, tempfile; r = analyze('tests/fixtures/zeek/telnet', tempfile.mkdtemp(), explain=False); print(json.dumps([(f['rule_id'], f['dst_port'], [c['control_id'] for c in f['controls']]) for f in r['findings']]))"
```

Expected output:

```text
[["cleartext.telnet", 23, ["SC-8", "SC-8(1)", "AC-17(2)", "IA-5(1)"]]]
```

**Step 6.** Commit, push, and open the pull request:

```bash
git add -A
git status          # only this task's files: nothing from .venv/, data/ or lab/captures/
git commit -m "feat: pipeline.analyze from input to report (JAI-05)"
git push -u origin HEAD
```

`HEAD` means "the branch I am on", so you do not have to retype its name. Open the repository on github.com: a yellow bar shows your branch with a **Compare & pull request** button. Click it, keep the title `feat: pipeline.analyze from input to report (JAI-05)`, fill in the template (paste the real output of the commands above under **How I tested it**), write `Closes #<issue number>` (this task's issue), and pick **@ahmadalkhoudeir** under **Reviewers**. Click **Create pull request**, then fix anything CI or the reviewer finds with new commits on the same branch.

#### How to test

`pytest tests/unit/test_pipeline.py -q` passes, and the one-liner prints the Telnet finding with its NIST controls.

#### What you just did and why

If the CLI, the API, and the tests each had their own copy of these steps, they would drift apart and a bug fixed in one place would stay in the others. One function means one behavior. The report has no "generated at" time on purpose: the same input must produce the identical report (CLAUDE.md rule 2); the API records *when* it received an upload separately.

#### Pull request checklist

- [ ] `ruff check .` prints `All checks passed!`
- [ ] `pytest -m "not integration" -q` passes on your laptop
- [ ] The pull request title has the form `type: summary (TASK-ID)` and the body says `Closes #<issue number>`
- [ ] No secrets, passwords, email addresses, personal data, or captures from a real network (CLAUDE.md rule 6)
- [ ] Any new dependency has a row in `docs/DEPENDENCIES.md` with its license
- [ ] CI is green and your reviewer approved

### JAI-06: Storage: alerts in SQLite, events in hourly Parquet files

**Due:** Week 3 (due Fri Oct 30) · **Milestone:** `W3 API and alert queue` · **Needs first:** [JAI-03](#jai-03-common-event-schema-the-normalizer-and-record-lookup) · **Kind:** code, tested

**Issue labels:** `type:task` `phase:alpha` `owner:jaiden` `area:storage` `critical-path`

#### Goal

Keep what the dashboard needs after an upload: `StateStore` (one SQLite file: analyses, alerts with status and assignee, and the audit trail) and `EventStore` (normalized events in one Parquet file per hour, queried with DuckDB). See `docs/ARCHITECTURE.md` section 9.

#### Prerequisites

JAI-03 is merged.

#### Steps

**Step 1.** Update `main` and create your branch for this task (one branch per task):

```bash
cd ~/projects/maxguard
source .venv/bin/activate
git checkout main && git pull
git checkout -b jaiden/storage
```

If `source .venv/bin/activate` fails, you have not made the virtual environment yet: do Week 0 section 0.11 first.

**Step 2.** Create `maxguard/storage/__init__.py`:

```python
"""Storage (v2.0): state.py (SQLite: analyses, alerts, audit) and events.py
(hourly Parquet files queried with DuckDB).

Import the class you need from its module, e.g.
`from maxguard.storage.state import StateStore`. Nothing is imported here, so
using the SQLite store never loads DuckDB.
"""
```

**Step 3.** Create `maxguard/storage/state.py`:

```python
"""StateStore: analyses, alerts and the audit trail in one SQLite file (v2.0).

- WAL mode: the dashboard can keep reading while an upload is being saved.
- An alert is a finding plus what people did with it (status, assignee).
  Alerts are keyed by finding_id, so a new capture that shows the same problem
  updates the existing alert (count, first/last seen) instead of adding a copy.
- Uploading the very same file again (same SHA-256) refreshes the alert's
  details but does not add to its count: the traffic was already counted.
- A "resolved" alert that comes back with newer evidence (last_seen moves
  forward) is reopened as "new", and the reopen is written to the audit table:
  a problem that was fixed and returned must be seen again. "false_positive"
  and "investigating" are never changed by an upload.
- The store never reads the clock: every time is passed in by the caller.
  That keeps tests exact and leaves "what time is it" to the API.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from maxguard.ids import canonical_json
from maxguard.models import SEVERITIES

ALERT_STATUSES = ("new", "investigating", "resolved", "false_positive")

SCHEMA = """
CREATE TABLE IF NOT EXISTS analyses (
    analysis_id   TEXT PRIMARY KEY,
    received_at   REAL NOT NULL,
    input_name    TEXT NOT NULL,
    input_sha256  TEXT NOT NULL,
    finding_count INTEGER NOT NULL,
    report_json   TEXT NOT NULL      -- the report minus "events" (those go to the EventStore)
);
CREATE TABLE IF NOT EXISTS alerts (
    finding_id        TEXT PRIMARY KEY,
    rule_id           TEXT NOT NULL,
    severity          TEXT NOT NULL,
    severity_rank     INTEGER NOT NULL,  -- position in SEVERITIES: 0 = critical
    first_seen        REAL NOT NULL,
    last_seen         REAL NOT NULL,
    count             INTEGER NOT NULL,
    status            TEXT NOT NULL DEFAULT 'new',
    assignee          TEXT NOT NULL DEFAULT '',
    analysis_id       TEXT NOT NULL,     -- the latest analysis that reported it
    first_received_at REAL NOT NULL,
    last_received_at  REAL NOT NULL,
    finding_json      TEXT NOT NULL      -- Finding.to_dict() from that latest analysis
);
CREATE TABLE IF NOT EXISTS audit (
    audit_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    at           REAL NOT NULL,
    actor        TEXT NOT NULL,
    action       TEXT NOT NULL,
    target       TEXT NOT NULL,
    details_json TEXT NOT NULL
);
"""

# status, assignee and first_received_at are not in the UPDATE part, so a
# re-upload keeps them (reopening is done separately, see reopen_if_back()).
# min()/max() widen the time range the alert covers. :repeat is 1 when this
# exact file was analysed before, so its findings are not counted twice.
UPSERT_ALERT = """
INSERT INTO alerts (finding_id, rule_id, severity, severity_rank, first_seen, last_seen,
                    count, analysis_id, first_received_at, last_received_at, finding_json)
VALUES (:finding_id, :rule_id, :severity, :severity_rank, :first_seen, :last_seen,
        :count, :analysis_id, :received_at, :received_at, :finding_json)
ON CONFLICT (finding_id) DO UPDATE SET
    count            = alerts.count + (CASE WHEN :repeat THEN 0 ELSE excluded.count END),
    first_seen       = min(alerts.first_seen, excluded.first_seen),
    last_seen        = max(alerts.last_seen, excluded.last_seen),
    severity         = excluded.severity,
    severity_rank    = excluded.severity_rank,
    analysis_id      = excluded.analysis_id,
    last_received_at = excluded.last_received_at,
    finding_json     = excluded.finding_json
"""

# Columns that override the values inside finding_json when an alert is read.
ALERT_COLUMNS = ("severity", "first_seen", "last_seen", "count", "status", "assignee",
                 "analysis_id", "first_received_at", "last_received_at")


def make_analysis_id(report: dict, received_at: float) -> str:
    """Same report received at the same moment -> same ID (so a retry is not saved twice)."""
    data = f"{received_at!r}\n{canonical_json(report)}".encode()
    return hashlib.sha256(data).hexdigest()[:16]


def alert_params(finding: dict, analysis_id: str, received_at: float,
                 repeat: bool = False) -> dict:
    """The named values UPSERT_ALERT needs for one finding dict."""
    return {
        "repeat": int(repeat),
        "finding_id": finding["finding_id"],
        "rule_id": finding["rule_id"],
        "severity": finding["severity"],
        "severity_rank": SEVERITIES.index(finding["severity"]),
        "first_seen": finding["first_seen"],
        "last_seen": finding["last_seen"],
        "count": finding["count"],
        "analysis_id": analysis_id,
        "received_at": received_at,
        "finding_json": json.dumps(finding, sort_keys=True),
    }


def row_to_alert(row: sqlite3.Row) -> dict:
    """The stored finding, with the merged/updated values from the columns on top."""
    alert = json.loads(row["finding_json"])
    for column in ALERT_COLUMNS:
        alert[column] = row[column]
    return alert


def check_status(status: str) -> None:
    if status not in ALERT_STATUSES:
        raise ValueError(f"status must be one of {ALERT_STATUSES}, got {status!r}")


def check_severity(severity: str) -> None:
    if severity not in SEVERITIES:
        raise ValueError(f"severity must be one of {SEVERITIES}, got {severity!r}")


def insert_audit(conn: sqlite3.Connection, *, actor: str, action: str, target: str,
                 details: dict, at: float) -> int:
    cur = conn.execute(
        "INSERT INTO audit (at, actor, action, target, details_json) VALUES (?, ?, ?, ?, ?)",
        (at, actor, action, target, json.dumps(details, sort_keys=True)),
    )
    return cur.lastrowid


def reopen_if_back(conn: sqlite3.Connection, finding: dict, analysis_id: str,
                   received_at: float) -> None:
    """Reopen a resolved alert when this finding brings newer evidence, and audit it."""
    row = conn.execute("SELECT status, last_seen FROM alerts WHERE finding_id = ?",
                       (finding["finding_id"],)).fetchone()
    if row is None or row["status"] != "resolved" or finding["last_seen"] <= row["last_seen"]:
        return
    conn.execute("UPDATE alerts SET status = 'new' WHERE finding_id = ?",
                 (finding["finding_id"],))
    insert_audit(conn, actor="maxguard", action="alert.reopen", target=finding["finding_id"],
                 details={"status": {"from": "resolved", "to": "new"},
                          "analysis_id": analysis_id, "last_seen": finding["last_seen"]},
                 at=received_at)


class StateStore:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            # WAL is stored in the database file, so setting it once is enough.
            conn.execute("PRAGMA journal_mode=WAL")
            conn.executescript(SCHEMA)

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        """A fresh connection per call: the API serves requests from several threads,
        and one sqlite3 connection must not be shared between threads."""
        conn = sqlite3.connect(self.path, timeout=5.0)  # wait up to 5 s for a lock
        conn.row_factory = sqlite3.Row
        try:
            with conn:  # commit if the block succeeds, roll back if it raises
                yield conn
        finally:
            conn.close()

    # ---------- analyses ----------

    def save_analysis(self, report: dict, *, received_at: float) -> str:
        """Store one pipeline report and merge its findings into the alerts."""
        analysis_id = make_analysis_id(report, received_at)
        stored = {key: value for key, value in report.items() if key != "events"}
        sha = report["input"]["sha256"]  # "" for a folder of logs (no single file to hash)
        with self._connect() as conn:
            repeat = bool(sha) and conn.execute(
                "SELECT 1 FROM analyses WHERE input_sha256 = ?", (sha,)).fetchone() is not None
            cur = conn.execute(
                "INSERT OR IGNORE INTO analyses VALUES (?, ?, ?, ?, ?, ?)",
                (analysis_id, received_at, report["input"]["name"], sha,
                 len(report["findings"]), json.dumps(stored, sort_keys=True)),
            )
            if cur.rowcount == 0:
                return analysis_id  # saved before: do not count its findings twice
            for finding in report["findings"]:
                reopen_if_back(conn, finding, analysis_id, received_at)
                conn.execute(UPSERT_ALERT,
                             alert_params(finding, analysis_id, received_at, repeat))
        return analysis_id

    def get_analysis(self, analysis_id: str) -> dict | None:
        """The stored report (without "events"), or None."""
        with self._connect() as conn:
            row = conn.execute("SELECT report_json FROM analyses WHERE analysis_id = ?",
                               (analysis_id,)).fetchone()
        return json.loads(row["report_json"]) if row else None

    def list_analyses(self, limit: int = 50) -> list[dict]:
        """Newest first: analysis_id, received_at, input_name, input_sha256, finding_count."""
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT analysis_id, received_at, input_name, input_sha256, finding_count "
                "FROM analyses ORDER BY received_at DESC, analysis_id LIMIT ?", (limit,),
            ).fetchall()
        return [dict(row) for row in rows]

    # ---------- alerts ----------

    def list_alerts(self, *, status: str | None = None, severity: str | None = None,
                    limit: int = 200) -> list[dict]:
        """Most severe first, then most recently seen."""
        where, params = [], []
        if status is not None:
            check_status(status)
            where.append("status = ?")
            params.append(status)
        if severity is not None:
            check_severity(severity)
            where.append("severity = ?")
            params.append(severity)
        sql = "SELECT * FROM alerts"
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " ORDER BY severity_rank, last_seen DESC, finding_id LIMIT ?"
        params.append(limit)
        with self._connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        return [row_to_alert(row) for row in rows]

    def get_alert(self, finding_id: str) -> dict | None:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM alerts WHERE finding_id = ?",
                               (finding_id,)).fetchone()
        return row_to_alert(row) if row else None

    def update_alert(self, finding_id: str, *, actor: str, at: float,
                     status: str | None = None, assignee: str | None = None) -> dict:
        """Change status and/or assignee (None = leave as is; assignee "" = nobody).
        Every real change is written to the audit table in the same transaction.
        Raises KeyError for an unknown finding_id, ValueError for an unknown status."""
        if status is not None:
            check_status(status)
        with self._connect() as conn:
            row = conn.execute("SELECT status, assignee FROM alerts WHERE finding_id = ?",
                               (finding_id,)).fetchone()
            if row is None:
                raise KeyError(finding_id)
            new_status = row["status"] if status is None else status
            new_assignee = row["assignee"] if assignee is None else assignee
            changes = {}
            if new_status != row["status"]:
                changes["status"] = {"from": row["status"], "to": new_status}
            if new_assignee != row["assignee"]:
                changes["assignee"] = {"from": row["assignee"], "to": new_assignee}
            if changes:
                conn.execute("UPDATE alerts SET status = ?, assignee = ? WHERE finding_id = ?",
                             (new_status, new_assignee, finding_id))
                insert_audit(conn, actor=actor, action="alert.update", target=finding_id,
                             details=changes, at=at)
        return self.get_alert(finding_id)

    # ---------- audit ----------

    def add_audit(self, *, actor: str, action: str, target: str, details: dict,
                  at: float) -> int:
        """Append one audit row and return its audit_id."""
        with self._connect() as conn:
            return insert_audit(conn, actor=actor, action=action, target=target,
                                details=details, at=at)

    def list_audit(self, limit: int = 200) -> list[dict]:
        """Newest first."""
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM audit ORDER BY audit_id DESC LIMIT ?",
                                (limit,)).fetchall()
        return [{"audit_id": row["audit_id"], "at": row["at"], "actor": row["actor"],
                 "action": row["action"], "target": row["target"],
                 "details": json.loads(row["details_json"])} for row in rows]
```

**Step 4.** Create `maxguard/storage/events.py`:

```python
"""EventStore: normalized events in hourly Parquet files, queried with DuckDB (v2.0).

Layout (UTC):  root/date=2026-10-06/hour=01/part-<sha>.parquet

- One folder per hour, so retention is "delete old folders" (prune) and a
  7-day window is a fixed number of folders.
- <sha> is a hash of the batch's event_ids: writing the same events again
  (the same capture uploaded twice) replaces the same file instead of adding
  a copy.
- The store never reads the clock: the caller says what "older than" means.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
from datetime import UTC, datetime
from pathlib import Path

import duckdb

# Column name -> DuckDB type. Same names and order as maxguard.events.normalize.EVENT_KEYS.
COLUMNS = {
    "event_id": "VARCHAR", "ts": "DOUBLE", "sensor_id": "VARCHAR", "source": "VARCHAR",
    "log": "VARCHAR", "kind": "VARCHAR", "uid": "VARCHAR", "community_id": "VARCHAR",
    "src_ip": "VARCHAR", "dst_ip": "VARCHAR", "src_port": "INTEGER", "dst_port": "INTEGER",
    "proto": "VARCHAR", "service": "VARCHAR", "bytes_out": "BIGINT", "bytes_in": "BIGINT",
    "device_mac": "VARCHAR", "summary": "VARCHAR", "ja4": "VARCHAR",
}
SECONDS_PER_HOUR = 3600
# DuckDB downloads and loads extensions on its own when a query needs one (both
# settings default to true). Parquet and JSON support are built in, so MaxGuard
# never needs a download: switch it off so nothing can go online (CLAUDE.md rule 1).
DUCKDB_CONFIG = {"autoinstall_known_extensions": False, "autoload_known_extensions": False}


def hour_key(ts: float) -> tuple[str, str]:
    """("2026-10-06", "01") for the UTC hour that contains ts."""
    moment = datetime.fromtimestamp(ts, tz=UTC)
    return moment.strftime("%Y-%m-%d"), moment.strftime("%H")


def hour_start(hour_dir: Path) -> float:
    """Epoch seconds at the start of a root/date=YYYY-MM-DD/hour=HH folder."""
    date = hour_dir.parent.name.removeprefix("date=")
    hour = int(hour_dir.name.removeprefix("hour="))
    moment = datetime.strptime(date, "%Y-%m-%d").replace(hour=hour, tzinfo=UTC)
    return moment.timestamp()


def batch_name(events: list[dict]) -> str:
    """part-<sha>.parquet, where sha depends only on which events are in the batch."""
    ids = "\n".join(sorted(e["event_id"] for e in events))
    return f"part-{hashlib.sha256(ids.encode()).hexdigest()[:16]}.parquet"


def group_by_hour(events: list[dict]) -> dict[tuple[str, str], list[dict]]:
    groups: dict[tuple[str, str], list[dict]] = {}
    for event in events:
        groups.setdefault(hour_key(event["ts"]), []).append(event)
    return groups


class EventStore:
    def __init__(self, root: Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def write(self, events: list[dict]) -> int:
        """Store events in their hour folders. Returns how many were written."""
        for (date, hour), group in sorted(group_by_hour(events).items()):
            folder = self.root / f"date={date}" / f"hour={hour}"
            folder.mkdir(parents=True, exist_ok=True)
            self._write_parquet(group, folder / batch_name(group))
        return len(events)

    def _write_parquet(self, events: list[dict], target: Path) -> None:
        # DuckDB inserts Python rows one by one slowly (about 1 ms per row, measured),
        # but loads a JSON-lines file hundreds of times faster. So: write the events
        # as JSON lines, let DuckDB convert that file to Parquet, then delete it.
        staging = target.with_suffix(".jsonl")
        partial = target.with_suffix(".partial")
        try:
            with staging.open("w", encoding="utf-8") as f:
                for event in events:
                    f.write(json.dumps({name: event[name] for name in COLUMNS}) + "\n")
            with duckdb.connect(config=DUCKDB_CONFIG) as con:
                con.execute(
                    "COPY (SELECT * FROM read_json($src, format = 'newline_delimited', "
                    "columns = $columns)) TO $dst (FORMAT parquet, COMPRESSION zstd)",
                    {"src": str(staging), "columns": COLUMNS, "dst": str(partial)},
                )
            # Readers only look at *.parquet, so they never see a half-written file.
            os.replace(partial, target)
        finally:
            staging.unlink(missing_ok=True)
            partial.unlink(missing_ok=True)

    def query(self, *, ip: str | None = None, since: float | None = None,
              until: float | None = None, limit: int = 1000) -> list[dict]:
        """Events in time order. ip matches src_ip or dst_ip; since <= ts < until."""
        if not any(self.root.glob("date=*/hour=*/*.parquet")):
            return []  # read_parquet fails on a pattern that matches no files
        where, params = [], {"files": str(self.root / "date=*" / "hour=*" / "*.parquet")}
        if ip is not None:
            where.append("(src_ip = $ip OR dst_ip = $ip)")
            params["ip"] = ip
        if since is not None:
            where.append("ts >= $since")
            params["since"] = since
        if until is not None:
            where.append("ts < $until")
            params["until"] = until
        # The column names come from COLUMNS (our constant), never from the caller;
        # every caller value goes in as a $parameter. hive_partitioning also turns the
        # folder names into "date" and "hour" columns (handy in the DuckDB shell);
        # we select only the event columns, so the result matches EVENT_KEYS.
        sql = (f"SELECT {', '.join(COLUMNS)} "
               "FROM read_parquet($files, hive_partitioning = true)")
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " ORDER BY ts, event_id LIMIT $limit"
        params["limit"] = limit
        with duckdb.connect(config=DUCKDB_CONFIG) as con:
            rows = con.execute(sql, params).fetchall()
        return [dict(zip(COLUMNS, row, strict=True)) for row in rows]

    def prune(self, *, older_than: float) -> int:
        """Delete every hour folder whose whole hour ended at or before older_than.
        Returns how many hour folders were deleted."""
        removed = 0
        for hour_dir in sorted(self.root.glob("date=*/hour=*")):
            if hour_start(hour_dir) + SECONDS_PER_HOUR <= older_than:
                shutil.rmtree(hour_dir)
                removed += 1
        for date_dir in self.root.glob("date=*"):
            if not any(date_dir.iterdir()):
                date_dir.rmdir()  # keep the tree tidy: no empty date folders
        return removed
```

**Step 5.** Create the tests `tests/unit/test_state_store.py`:

```python
"""Tests for maxguard.storage.state.StateStore (SQLite: analyses, alerts, audit)."""

import copy
import sqlite3
import time
from pathlib import Path

import pytest

import maxguard.rules  # noqa: F401  (importing registers every rule)
from maxguard.events.normalize import normalize
from maxguard.rules.base import run_all
from maxguard.storage.state import ALERT_STATUSES, StateStore

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "zeek"


def make_report(capture: str) -> dict:
    """A report dict shaped like pipeline.analyze() output, built from a fixture."""
    log_dir = FIXTURES / capture
    return {
        "schema": "maxguard.report/2",
        "input": {"name": f"{capture}.pcap", "sha256": "ab" * 32, "adapter": "pcap"},
        "tools": {"zeek": True, "suricata": True},
        "frameworks": [],
        "findings": [f.to_dict() for f in run_all(log_dir)],
        "assets": [],
        "events": normalize(log_dir, sensor_id="pcap"),
        "ai": {"status": "disabled", "model": None, "explained": 0, "dropped_sentences": 0},
    }


@pytest.fixture
def store(tmp_path) -> StateStore:
    return StateStore(tmp_path / "data" / "state.db")


def only_alert(store: StateStore) -> dict:
    [alert] = store.list_alerts()
    return alert


def test_database_uses_wal_and_has_the_tables(store):
    conn = sqlite3.connect(store.path)
    assert conn.execute("PRAGMA journal_mode").fetchone()[0] == "wal"
    tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert {"analyses", "alerts", "audit"} <= tables
    conn.close()


def test_saving_a_report_creates_new_alerts(store):
    report = make_report("telnet")
    analysis_id = store.save_analysis(report, received_at=1000.0)

    alert = only_alert(store)
    finding = report["findings"][0]
    assert alert["finding_id"] == finding["finding_id"]
    assert alert["rule_id"] == "cleartext.telnet"
    assert alert["status"] == "new" and alert["assignee"] == ""
    assert alert["analysis_id"] == analysis_id
    assert alert["first_received_at"] == alert["last_received_at"] == 1000.0
    assert alert["evidence"] == finding["evidence"]  # the full finding is kept
    assert store.get_alert(finding["finding_id"]) == alert


def test_reupload_updates_the_same_alert(store):
    report = make_report("telnet")
    first_id = store.save_analysis(report, received_at=1000.0)
    store.update_alert(report["findings"][0]["finding_id"], actor="amory", at=1100.0,
                       status="investigating", assignee="amory")

    later = copy.deepcopy(report)  # a NEW capture showing the same problem over a wider time
    later["input"]["sha256"] = "cd" * 32
    later["findings"][0]["first_seen"] -= 60
    later["findings"][0]["last_seen"] += 60
    second_id = store.save_analysis(later, received_at=2000.0)

    alert = only_alert(store)
    old = report["findings"][0]
    assert second_id != first_id
    assert alert["count"] == 2
    assert alert["first_seen"] == old["first_seen"] - 60
    assert alert["last_seen"] == old["last_seen"] + 60
    assert (alert["status"], alert["assignee"]) == ("investigating", "amory")  # kept
    assert alert["first_received_at"] == 1000.0 and alert["last_received_at"] == 2000.0
    assert alert["analysis_id"] == second_id  # the latest analysis that reported it


def test_saving_the_same_report_at_the_same_time_twice_counts_once(store):
    report = make_report("ftp")
    assert store.save_analysis(report, received_at=1000.0) == store.save_analysis(
        report, received_at=1000.0)
    assert only_alert(store)["count"] == 1
    assert len(store.list_analyses()) == 1


def test_stored_analysis_has_no_events(store):
    report = make_report("plain_http")
    analysis_id = store.save_analysis(report, received_at=1000.0)

    stored = store.get_analysis(analysis_id)

    assert "events" not in stored  # events live in the EventStore
    assert stored["findings"] == report["findings"]
    assert store.get_analysis("0000000000000000") is None
    [row] = store.list_analyses()
    assert row == {"analysis_id": analysis_id, "received_at": 1000.0,
                   "input_name": "plain_http.pcap", "input_sha256": "ab" * 32,
                   "finding_count": 1}


def test_list_alerts_filters_and_sorts_most_severe_first(store):
    for i, capture in enumerate(["plain_http", "telnet", "cert_self_signed", "ftp"]):
        store.save_analysis(make_report(capture), received_at=1000.0 + i)

    alerts = store.list_alerts()
    ranks = [("critical", "high", "medium", "low", "info").index(a["severity"]) for a in alerts]
    assert ranks == sorted(ranks)
    assert {a["rule_id"] for a in store.list_alerts(severity="high")} == {
        "cleartext.telnet", "cleartext.ftp"}
    assert store.list_alerts(status="resolved") == []
    assert len(store.list_alerts(limit=2)) == 2


def test_bad_filters_are_rejected(store):
    with pytest.raises(ValueError):
        store.list_alerts(status="done")
    with pytest.raises(ValueError):
        store.list_alerts(severity="urgent")


def test_update_alert_changes_status_and_writes_audit(store):
    report = make_report("imap")
    store.save_analysis(report, received_at=1000.0)
    finding_id = report["findings"][0]["finding_id"]

    alert = store.update_alert(finding_id, actor="ahmad", at=1500.0, status="resolved")

    assert alert["status"] == "resolved"
    [entry] = store.list_audit()
    assert entry["actor"] == "ahmad" and entry["at"] == 1500.0
    assert entry["action"] == "alert.update" and entry["target"] == finding_id
    assert entry["details"] == {"status": {"from": "new", "to": "resolved"}}


def test_update_without_a_real_change_writes_no_audit(store):
    report = make_report("imap")
    store.save_analysis(report, received_at=1000.0)
    finding_id = report["findings"][0]["finding_id"]

    store.update_alert(finding_id, actor="ahmad", at=1500.0, status="new")

    assert store.list_audit() == []


def test_update_alert_validates_input(store):
    report = make_report("imap")
    store.save_analysis(report, received_at=1000.0)
    with pytest.raises(ValueError):
        store.update_alert(report["findings"][0]["finding_id"], actor="x", at=1.0,
                           status="closed")
    with pytest.raises(KeyError):
        store.update_alert("0000000000000000", actor="x", at=1.0, status="resolved")
    assert ALERT_STATUSES == ("new", "investigating", "resolved", "false_positive")


def test_audit_is_listed_newest_first(store):
    first = store.add_audit(actor="system", action="analysis.saved", target="a1",
                            details={"findings": 1}, at=10.0)
    second = store.add_audit(actor="fiona", action="block.approved", target="10.0.0.5",
                             details={}, at=20.0)
    assert second > first
    assert [e["audit_id"] for e in store.list_audit()] == [second, first]
    assert store.list_audit(limit=1)[0]["details"] == {}


def test_data_survives_reopening(store):
    store.save_analysis(make_report("pop3"), received_at=1000.0)
    reopened = StateStore(store.path)  # "CREATE TABLE IF NOT EXISTS": safe to run again
    assert len(reopened.list_alerts()) == 1


def test_store_never_reads_the_clock(store, monkeypatch):
    def no_clock():
        raise AssertionError("StateStore must not read the clock")

    monkeypatch.setattr(time, "time", no_clock)
    monkeypatch.setattr(time, "time_ns", no_clock)
    report = make_report("telnet")
    store.save_analysis(report, received_at=1000.0)
    store.update_alert(report["findings"][0]["finding_id"], actor="x", at=1001.0,
                       assignee="jaiden")
    store.add_audit(actor="x", action="test", target="t", details={}, at=1002.0)
    assert len(store.list_audit()) == 2
```

`tests/unit/test_state_store_recurrence.py`:

```python
"""Alerts across several uploads: repeats are not double counted, fixes that come back reopen."""

from copy import deepcopy

from maxguard.storage.state import StateStore


def report(sha: str, last_seen: float, count: int = 1) -> dict:
    finding = {"finding_id": "f1", "rule_id": "cleartext.telnet", "severity": "high",
               "first_seen": last_seen - 1, "last_seen": last_seen, "count": count,
               "title": "Telnet session in cleartext", "evidence": []}
    return {"schema": "maxguard.report/2", "input": {"name": "x.pcap", "sha256": sha,
            "adapter": "pcap"}, "findings": [finding], "events": []}


def test_same_file_uploaded_twice_is_not_counted_twice(tmp_path):
    store = StateStore(tmp_path / "state.db")
    store.save_analysis(report("aaaa", 100.0, count=3), received_at=1000.0)
    store.save_analysis(report("aaaa", 100.0, count=3), received_at=2000.0)  # same file, later

    alert = store.get_alert("f1")
    assert alert["count"] == 3
    assert alert["last_received_at"] == 2000.0
    assert len(store.list_analyses()) == 2  # both uploads are still on record


def test_different_files_add_up(tmp_path):
    store = StateStore(tmp_path / "state.db")
    store.save_analysis(report("aaaa", 100.0, count=3), received_at=1000.0)
    store.save_analysis(report("bbbb", 200.0, count=2), received_at=2000.0)
    assert store.get_alert("f1")["count"] == 5


def test_resolved_alert_reopens_when_new_evidence_arrives(tmp_path):
    store = StateStore(tmp_path / "state.db")
    store.save_analysis(report("aaaa", 100.0), received_at=1000.0)
    store.update_alert("f1", actor="ahmad", at=1100.0, status="resolved")

    store.save_analysis(report("bbbb", 200.0), received_at=2000.0)  # newer traffic

    assert store.get_alert("f1")["status"] == "new"
    newest = store.list_audit()[0]
    assert (newest["action"], newest["actor"], newest["at"]) == ("alert.reopen", "maxguard", 2000.0)


def test_resolved_alert_stays_resolved_for_old_evidence(tmp_path):
    store = StateStore(tmp_path / "state.db")
    store.save_analysis(report("aaaa", 100.0), received_at=1000.0)
    store.update_alert("f1", actor="ahmad", at=1100.0, status="resolved")

    store.save_analysis(report("cccc", 100.0), received_at=2000.0)  # nothing newer

    assert store.get_alert("f1")["status"] == "resolved"


def test_false_positive_is_never_reopened(tmp_path):
    store = StateStore(tmp_path / "state.db")
    store.save_analysis(report("aaaa", 100.0), received_at=1000.0)
    store.update_alert("f1", actor="ahmad", at=1100.0, status="false_positive")
    store.save_analysis(deepcopy(report("bbbb", 300.0)), received_at=2000.0)
    assert store.get_alert("f1")["status"] == "false_positive"
```

and `tests/unit/test_event_store.py`:

```python
"""Tests for maxguard.storage.events.EventStore (hourly Parquet + DuckDB)."""

from pathlib import Path

import duckdb
import pytest

from maxguard.events.normalize import EVENT_KEYS, normalize
from maxguard.storage.events import COLUMNS, DUCKDB_CONFIG, EventStore, hour_key

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "zeek"
CAPTURES = sorted(p for p in FIXTURES.iterdir() if p.is_dir() and not p.name.startswith("_"))

HOUR_01 = 1791248400.0  # 2026-10-06 01:00:00 UTC: 13 of the 14 lab captures are in this hour
HOUR_02 = 1791252000.0  # 2026-10-06 02:00:00 UTC: dns_lookup and the handmade DNS/DHCP capture


def fixture_events() -> list[dict]:
    events = []
    for log_dir in CAPTURES + [FIXTURES / "_handmade" / "dns_dhcp"]:
        events.extend(normalize(log_dir, sensor_id="pcap"))
    return events


@pytest.fixture
def events() -> list[dict]:
    return fixture_events()


@pytest.fixture
def store(tmp_path, events) -> EventStore:
    s = EventStore(tmp_path / "events")
    s.write(events)
    return s


def in_query_order(events: list[dict]) -> list[dict]:
    return sorted(events, key=lambda e: (e["ts"], e["event_id"]))


def test_columns_match_the_event_schema():
    assert tuple(COLUMNS) == EVENT_KEYS


def test_hour_key_uses_utc():
    assert hour_key(HOUR_01) == ("2026-10-06", "01")
    assert hour_key(HOUR_02 - 0.001) == ("2026-10-06", "01")


def test_write_makes_one_file_per_hour(tmp_path, events):
    store = EventStore(tmp_path / "events")
    assert store.write(events) == len(events)
    files = sorted(p.relative_to(store.root).parent.as_posix()
                   for p in store.root.rglob("*") if p.is_file())
    assert files == ["date=2026-10-06/hour=01", "date=2026-10-06/hour=02"]
    names = [p.name for p in store.root.rglob("*.parquet")]
    assert all(n.startswith("part-") and len(n) == len("part-") + 16 + len(".parquet")
               for n in names)


def test_query_returns_every_event_unchanged(store, events):
    assert store.query() == in_query_order(events)


def test_query_by_ip_matches_source_or_destination(store, events):
    laptop = store.query(ip="192.168.56.50")
    assert laptop == in_query_order(
        [e for e in events if "192.168.56.50" in (e["src_ip"], e["dst_ip"])])
    assert {e["log"] for e in laptop} == {"dhcp.log", "conn.log", "dns.log", "eve.json"}
    assert store.query(ip="203.0.113.9") == []


def test_query_time_window_is_since_inclusive_until_exclusive(store, events):
    assert {e["ts"] >= HOUR_02 for e in store.query(since=HOUR_02)} == {True}
    assert {e["ts"] < HOUR_02 for e in store.query(until=HOUR_02)} == {True}
    assert len(store.query(since=HOUR_02)) + len(store.query(until=HOUR_02)) == len(events)
    first = min(e["ts"] for e in events)
    [only] = store.query(since=first, until=first + 0.000001)
    assert only["ts"] == first


def test_query_limit(store):
    assert len(store.query(limit=5)) == 5


def test_empty_store_returns_nothing(tmp_path):
    assert EventStore(tmp_path / "empty").query(ip="10.0.0.1") == []


def test_writing_the_same_events_again_does_not_duplicate_them(store, events):
    store.write(events)  # e.g. the same capture uploaded twice
    assert len(list(store.root.rglob("*.parquet"))) == 2
    assert len(store.query(limit=10_000)) == len(events)


def test_no_staging_files_are_left_behind(store):
    leftovers = [p for p in store.root.rglob("*") if p.is_file() and p.suffix != ".parquet"]
    assert leftovers == []


def test_prune_deletes_only_hours_that_are_completely_older(store):
    assert store.prune(older_than=HOUR_01 + 1800) == 0  # hour 01 is only half over
    assert store.prune(older_than=HOUR_02) == 1  # hour 01 ended exactly at 02:00
    assert {e["ts"] >= HOUR_02 for e in store.query()} == {True}
    assert store.prune(older_than=HOUR_02 + 3600) == 1
    assert store.query() == []
    assert list(store.root.iterdir()) == []  # the empty date folder is removed too

def test_duckdb_never_downloads_extensions():
    # CLAUDE.md rule 1: a query that needs an extension must fail, not download it.
    with duckdb.connect(config=DUCKDB_CONFIG) as con:
        settings = con.execute(
            "SELECT current_setting('autoinstall_known_extensions'), "
            "current_setting('autoload_known_extensions')").fetchone()
    assert settings == (False, False)
```

**Step 6.** Run them:

```bash
pytest tests/unit/test_state_store.py tests/unit/test_state_store_recurrence.py tests/unit/test_event_store.py -q
```

Expected output:

```text
..............................                                                               [100%]
30 passed in 1.17s
```

**Step 7.** Look inside the event store with DuckDB's own Python API (handy for debugging):

```bash
python -c "import tempfile; from pathlib import Path; from maxguard.events.normalize import normalize; from maxguard.storage.events import EventStore; store = EventStore(Path(tempfile.mkdtemp())); print(store.write(normalize(Path('tests/fixtures/zeek/telnet'), 'pcap')), 'events written'); [print(e['kind'], e['src_ip'], '->', e['dst_ip'], e['dst_port'], e['summary']) for e in store.query(limit=5)]"
```

Expected output:

```text
1 events written
conn 172.18.0.3 -> 172.18.0.2 23 tcp/23 SF out=23 in=40
```

**Step 8.** Commit, push, and open the pull request:

```bash
git add -A
git status          # only this task's files: nothing from .venv/, data/ or lab/captures/
git commit -m "feat: StateStore (SQLite) and EventStore (Parquet + DuckDB) (JAI-06)"
git push -u origin HEAD
```

`HEAD` means "the branch I am on", so you do not have to retype its name. Open the repository on github.com: a yellow bar shows your branch with a **Compare & pull request** button. Click it, keep the title `feat: StateStore (SQLite) and EventStore (Parquet + DuckDB) (JAI-06)`, fill in the template (paste the real output of the commands above under **How I tested it**), write `Closes #<issue number>` (this task's issue), and pick **@ahmadalkhoudeir** under **Reviewers**. Click **Create pull request**, then fix anything CI or the reviewer finds with new commits on the same branch.

#### How to test

All three test files pass. The recurrence tests prove two promises: uploading the same file twice does not double the counts, and a resolved alert that comes back with newer evidence is reopened and audited.

#### What you just did and why

SQLite is good at many small updates ("set this alert to investigating") and WAL mode lets the dashboard read while an upload is being saved. Parquet + DuckDB is good at scanning a week of events quickly (preview before you block). Hourly folders make the 7-day retention a matter of deleting old folders instead of rewriting a database, which also spares the Raspberry Pi's storage. The stores never read the clock; the caller passes every time in, which keeps tests exact.

#### Pull request checklist

- [ ] `ruff check .` prints `All checks passed!`
- [ ] `pytest -m "not integration" -q` passes on your laptop
- [ ] The pull request title has the form `type: summary (TASK-ID)` and the body says `Closes #<issue number>`
- [ ] No secrets, passwords, email addresses, personal data, or captures from a real network (CLAUDE.md rule 6)
- [ ] Any new dependency has a row in `docs/DEPENDENCIES.md` with its license
- [ ] CI is green and your reviewer approved

### JAI-07: The API: uploads, alerts, events, live updates, sensor ingest

**Due:** Week 3 (due Fri Oct 30) · **Milestone:** `W3 API and alert queue` · **Needs first:** [JAI-05](#jai-05-the-pipeline-one-function-from-input-to-report), [JAI-06](#jai-06-storage-alerts-in-sqlite-events-in-hourly-parquet-files), [JON-03](jonattan.md#jon-03-offline-guard-make-accidental-network-access-fail-loudly) · **Kind:** code, tested

**Issue labels:** `type:task` `phase:alpha` `owner:jaiden` `area:api` `critical-path`

#### Goal

Write `maxguard/api/app.py` with `create_app(data_dir=None, *, explain=True)`: the JSON API in `docs/ARCHITECTURE.md` section 10 that the dashboard, the sensors, and the host agent use. Uploads run the pipeline and are saved to the two stores; the API is the only part of MaxGuard that reads the clock.

#### Prerequisites

JAI-05 (pipeline), JAI-06 (storage) and JON-03 (the offline guard, which `create_app()` switches on when `MAXGUARD_OFFLINE=1`) are merged.

#### Steps

**Step 1.** Update `main` and create your branch for this task (one branch per task):

```bash
cd ~/projects/maxguard
source .venv/bin/activate
git checkout main && git pull
git checkout -b jaiden/api
```

If `source .venv/bin/activate` fails, you have not made the virtual environment yet: do Week 0 section 0.11 first.

**Step 2.** Let the pipeline name where data came from. In `maxguard/pipeline.py`, give `analyze()` one more optional argument and use it for the events (the default keeps `pcap` and `import`, so nothing else changes):

```python
def analyze(path, workdir, frameworks=None, explain=True, mapping_dir=None,
            sensor_id=None) -> dict:
    ...
    if sensor_id is None:
        sensor_id = "pcap" if adapter.name == "pcap" else "import"
    events = normalize(log_dir, sensor_id=sensor_id)
```

Add a sentence to its docstring: the API passes the sensor's name for data that a sensor or host agent sent to `POST /api/ingest`.

**Step 3.** Create an empty `maxguard/api/__init__.py` and `maxguard/api/app.py`:

```python
"""MaxGuard's JSON API (Jaiden, JAI-07).

The dashboard, the live sensor and the host agent all talk to MaxGuard through
this app. docs/ARCHITECTURE.md section 10 lists the endpoints.

- The API is the only part of MaxGuard that reads the clock and writes to the
  stores. The engine (maxguard.pipeline) never does either, so the same input
  always gives the same report.
- Uploads are saved under a name we generate, never the client's file name
  (which could contain "../"), and the file type is decided by its first bytes.
- One analysis runs at a time: Zeek and Suricata already use every CPU core,
  so two at once on a Raspberry Pi only makes both slower.
- POST /api/ingest is how sensors and host agents on the LAN send data. It is
  OFF unless MAXGUARD_INGEST_TOKEN is set, and every request must carry that
  token. The dashboard and the rest of the API are published on 127.0.0.1 only.
  Sensors reach a second app, create_ingest_app(), which serves nothing but
  POST /api/ingest on its own port; publishing that port on the LAN is an
  explicit, optional choice of the user (CLAUDE.md rule 1: nothing leaves or
  enters the machine by default).
- Browsers refuse to let other websites read this API, but they do let another
  website *send* a form to it. Requests that change something are therefore
  refused when the browser says they come from another site (cross-site
  request forgery, OWASP CSRF Prevention Cheat Sheet).
- A website can also make its own name point to 127.0.0.1 after the page has
  loaded (DNS rebinding); the browser then treats this API as part of that
  website. The API therefore answers only requests whose Host header names this
  machine, or an address listed in MAXGUARD_ALLOWED_HOSTS.

Start it with:  uvicorn maxguard.api.app:create_app --factory --port 8000
Ingest only:    uvicorn maxguard.api.app:create_ingest_app --factory --port 8001
"""

from __future__ import annotations

import asyncio
import hmac
import importlib
import importlib.util
import ipaddress
import os
import re
import secrets
import tarfile
import tempfile
import threading
import time
import zipfile
from collections.abc import AsyncIterator
from pathlib import Path
from typing import BinaryIO
from urllib.parse import urlparse

from fastapi import APIRouter, FastAPI, HTTPException, Query, Request
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from starlette.datastructures import FormData, UploadFile
from starlette.middleware.trustedhost import TrustedHostMiddleware

from maxguard import __version__, offline
from maxguard.adapters.pcap import PCAP_MAGIC
from maxguard.adapters.zeeklogs import ArchiveTooLarge
from maxguard.pipeline import UnsupportedInput, analyze
from maxguard.storage.events import EventStore
from maxguard.storage.state import StateStore
from maxguard.zeek.runner import ZeekError

STATIC_DIR = Path(__file__).resolve().parent.parent / "web" / "static"
OPTIONAL_ROUTERS = ("maxguard.web.routes", "maxguard.response.routes")

DEFAULT_MAX_UPLOAD_MB = 1024
MIB = 1024 * 1024
CHUNK_BYTES = MIB              # copy uploads in 1 MiB blocks: never the whole file in memory
FORM_OVERHEAD_BYTES = 64 * 1024  # room for the multipart headers around the file
MIN_TOKEN_LENGTH = 32          # secrets.token_urlsafe(32) gives 43 characters
DEFAULT_ALLOWED_HOSTS = "localhost,127.0.0.1,[::1]"  # this machine only

DEFAULT_SENSOR_ID = "sensor"
MAX_FORM_FIELDS = 5             # one file plus a few text fields; Starlette allows 1000
SENSOR_ID_PATTERN = re.compile(r"[A-Za-z0-9._-]{1,64}")
ZIP_MAGIC = b"PK\x03\x04"
GZIP_MAGIC = b"\x1f\x8b"

KEEPALIVE_SECONDS = 15.0   # a comment line now and then stops proxies closing the stream
POLL_SECONDS = 0.5         # how often the stream checks the change counter
CHANGING_METHODS = {"POST", "PUT", "PATCH", "DELETE"}

# The file field, written out for the OpenAPI page (/docs): the upload endpoints
# read the form themselves (see check_ingest_token), so FastAPI cannot see it.
FILE_FIELD = {"type": "string", "format": "binary",
              "description": "a .pcap/.pcapng capture, or a .zip/.tar.gz of Zeek logs"}
UPLOAD_FORM = {"requestBody": {"required": True, "content": {"multipart/form-data": {
    "schema": {"type": "object", "required": ["file"], "properties": {"file": FILE_FIELD}}}}}}
INGEST_FORM = {"requestBody": {"required": True, "content": {"multipart/form-data": {
    "schema": {"type": "object", "required": ["file"], "properties": {
        "file": FILE_FIELD,
        "sensor_id": {"type": "string", "default": DEFAULT_SENSOR_ID,
                      "description": "1-64 characters: letters, digits, '.', '_', '-'"},
    }}}}}}

router = APIRouter()
ingest_router = APIRouter()  # also served alone by create_ingest_app()


# ---------- the app ----------

def create_app(data_dir: str | Path | None = None, *, explain: bool = True) -> FastAPI:
    """Build the app. uvicorn --factory calls it with no arguments.

    data_dir defaults to $MAXGUARD_DATA_DIR, then "data". explain=False skips the AI
    (tests, and machines without Ollama)."""
    app = new_app(data_dir, explain)
    app.include_router(router)
    app.include_router(ingest_router)
    for module_name in OPTIONAL_ROUTERS:
        module = optional_module(module_name)
        if module is not None:
            app.include_router(module.router)
    if STATIC_DIR.is_dir():
        app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    return app


def create_ingest_app(data_dir: str | Path | None = None, *, explain: bool = True) -> FastAPI:
    """Only POST /api/ingest: the app for the port that sensors and agents reach over
    the LAN (docker/compose.lan.yaml). The dashboard and the rest of the API stay on
    127.0.0.1, so nobody on the LAN can read alerts or approve a block.

    Both apps share the data folder. The dashboard shows ingested data at its next
    refresh: GET /api/stream only hears about changes made in its own process."""
    app = new_app(data_dir, explain, docs=False)  # no /docs page on the LAN
    if app.state.ingest_token is None:
        raise ValueError("the ingest app needs MAXGUARD_INGEST_TOKEN (at least 32 characters)")
    app.include_router(ingest_router)
    return app


def new_app(data_dir: str | Path | None, explain: bool, *, docs: bool = True) -> FastAPI:
    """What both apps share: settings and stores on app.state, and the two checks
    that run before any route (unknown host names, cross-site changes)."""
    offline.enable_from_env()  # MAXGUARD_OFFLINE=1 (set in docker/compose.yaml)

    folder = Path(data_dir or os.environ.get("MAXGUARD_DATA_DIR", "data"))
    folder.mkdir(parents=True, exist_ok=True)

    no_docs = {} if docs else {"docs_url": None, "redoc_url": None, "openapi_url": None}
    app = FastAPI(title="MaxGuard", version=__version__,
                  description="Offline network security checks. See docs/ARCHITECTURE.md.",
                  **no_docs)
    app.state.data_dir = folder
    app.state.state_store = StateStore(folder / "state.db")
    app.state.event_store = EventStore(folder / "events")
    app.state.explain = explain
    app.state.max_upload_bytes = max_upload_bytes()
    app.state.keep_uploads = os.environ.get("MAXGUARD_KEEP_UPLOADS") == "1"
    app.state.ingest_token = ingest_token()
    app.state.analysis_lock = threading.Lock()
    app.state.changes = 0      # goes up by one whenever alerts change (see notify_change)
    app.state.keepalive_seconds = KEEPALIVE_SECONDS

    app.middleware("http")(refuse_cross_site_changes)
    # Added last, so it runs first: a request for an unknown host name stops here.
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=allowed_hosts(),
                       www_redirect=False)
    return app


def allowed_hosts() -> list[str]:
    """MAXGUARD_ALLOWED_HOSTS: the names and addresses this console may be reached by,
    comma-separated, without http:// or a port. Default: this machine only. Add the
    console's LAN address (for example 192.168.50.20) when sensors or agents send to it."""
    text = os.environ.get("MAXGUARD_ALLOWED_HOSTS", DEFAULT_ALLOWED_HOSTS)
    hosts = [host.strip().lower() for host in text.split(",") if host.strip()]
    if not hosts:
        raise ValueError("MAXGUARD_ALLOWED_HOSTS is empty: the console would answer no one")
    for host in hosts:
        # "*" would switch the check off; "/" or a port can never match a Host header.
        if "*" in host or "/" in host or (":" in host and not host.startswith("[")):
            raise ValueError("MAXGUARD_ALLOWED_HOSTS: write names or addresses only, "
                             f"without http:// or a port, got {host!r}")
    return hosts


def max_upload_bytes() -> int:
    """MAXGUARD_MAX_UPLOAD_MB (default 1024) in bytes; 1 MB here means 1 MiB."""
    text = os.environ.get("MAXGUARD_MAX_UPLOAD_MB", str(DEFAULT_MAX_UPLOAD_MB))
    if not text.isdigit() or int(text) < 1:
        raise ValueError(
            f"MAXGUARD_MAX_UPLOAD_MB must be a whole number of megabytes, got {text!r}")
    return int(text) * MIB


def ingest_token() -> str | None:
    """The sensor token, or None when ingest is off. A short token is refused at start-up."""
    token = os.environ.get("MAXGUARD_INGEST_TOKEN", "")
    if not token:
        return None
    if len(token) < MIN_TOKEN_LENGTH:
        raise ValueError(
            f"MAXGUARD_INGEST_TOKEN must be at least {MIN_TOKEN_LENGTH} characters; make one with: "
            'python -c "import secrets; print(secrets.token_urlsafe(32))"')
    return token


def optional_module(name: str):
    """Import a module that may not exist yet (the dashboard and the response
    module arrive in later tasks). A module that exists but fails to import still
    raises, so a real bug in it is never hidden."""
    try:
        spec = importlib.util.find_spec(name)
    except ModuleNotFoundError:  # its parent package does not exist either
        return None
    return importlib.import_module(name) if spec else None


def notify_change(app: FastAPI) -> None:
    """Tell open dashboards that alerts changed: /api/stream sends alerts-changed.
    Two threads doing += at the same moment can lose one increment; that is fine,
    because the number still changes, and a change is all the stream looks for."""
    app.state.changes += 1


# ---------- cross-site request check ----------

def is_cross_site(request: Request) -> bool:
    """True when the browser says another website (another origin) started this request.

    Sec-Fetch-Site is set by every browser since 2023 and cannot be set by a page's
    scripts. "same-site" is refused too: another program on 127.0.0.1 with a different
    port counts as the same site. Older browsers send only Origin; "null" never matches."""
    if request.headers.get("sec-fetch-site") in ("cross-site", "same-site"):
        return True
    origin = request.headers.get("origin")
    if origin is None:
        return False  # curl, sensors, agents and tests send no Origin header
    return urlparse(origin).netloc != request.headers.get("host", "")


async def refuse_cross_site_changes(request: Request, call_next):
    if request.method in CHANGING_METHODS and is_cross_site(request):
        return JSONResponse({"detail": "cross-site request refused"}, status_code=403)
    return await call_next(request)


# ---------- uploads and ingest ----------

@router.post("/api/analyses", openapi_extra=UPLOAD_FORM)
async def upload_analysis(request: Request) -> dict:
    """Analyze one uploaded capture or zipped log folder (the dashboard's upload page)."""
    check_content_length(request)
    async with request.form(max_files=1, max_fields=MAX_FORM_FIELDS) as form:
        upload = form_file(form)
        return await run_in_threadpool(receive, request.app, upload, sensor_id=None)


@ingest_router.post("/api/ingest", openapi_extra=INGEST_FORM)
async def ingest(request: Request) -> dict:
    """The same as an upload, for sensors and host agents on the LAN."""
    # Both checks come before the body is read, so a stranger without the token
    # cannot make the console store anything.
    check_ingest_token(request)
    check_content_length(request)
    async with request.form(max_files=1, max_fields=MAX_FORM_FIELDS) as form:
        upload = form_file(form)
        sensor_id = check_sensor_id(form.get("sensor_id", DEFAULT_SENSOR_ID))
        return await run_in_threadpool(receive, request.app, upload, sensor_id=sensor_id)


def check_ingest_token(request: Request) -> None:
    token = request.app.state.ingest_token
    if token is None:
        raise HTTPException(404, "Not Found")  # ingest is off: look like any missing page
    scheme, _, given = request.headers.get("authorization", "").partition(" ")
    # compare_digest takes the same time however many characters match, so the
    # answer time does not help anyone guess the token one character at a time.
    if scheme.lower() != "bearer" or not hmac.compare_digest(given.encode(), token.encode()):
        raise HTTPException(401, "missing or wrong token", headers={"WWW-Authenticate": "Bearer"})


def check_content_length(request: Request) -> None:
    """Refuse an upload that announces itself as too large before reading it."""
    length = request.headers.get("content-length", "")
    if length.isdigit() and int(length) > request.app.state.max_upload_bytes + FORM_OVERHEAD_BYTES:
        raise HTTPException(413, too_large_message(request.app))


def too_large_message(app: FastAPI) -> str:
    return f"file larger than {app.state.max_upload_bytes // MIB} MB (MAXGUARD_MAX_UPLOAD_MB)"


def form_file(form: FormData) -> UploadFile:
    upload = form.get("file")
    if not isinstance(upload, UploadFile):
        raise HTTPException(400, "send the file in a multipart form field named 'file'")
    return upload


def check_sensor_id(value) -> str:
    if not isinstance(value, str) or not SENSOR_ID_PATTERN.fullmatch(value):
        raise HTTPException(400, "sensor_id: 1-64 characters, letters, digits, '.', '_' or '-'")
    return value


def receive(app: FastAPI, upload: UploadFile, *, sensor_id: str | None) -> dict:
    """Save the upload, analyze it, store the results, tell the dashboards.
    Runs in a worker thread: analyze() takes seconds and must not block the server."""
    uploads = app.state.data_dir / "uploads"
    uploads.mkdir(exist_ok=True)
    path = save_upload(upload.file, uploads, app)
    try:
        with app.state.analysis_lock:
            report = run_pipeline(app, path, sensor_id)
    finally:
        if not app.state.keep_uploads:
            path.unlink(missing_ok=True)
    # The generated name is in the report; show the person the name they know.
    # It is only ever displayed, never used as a path.
    report["input"]["name"] = display_name(upload.filename)
    analysis_id = app.state.state_store.save_analysis(report, received_at=time.time())
    app.state.event_store.write(report["events"])
    notify_change(app)
    return {"analysis_id": analysis_id, "findings": len(report["findings"])}


def save_upload(source: BinaryIO, folder: Path, app: FastAPI) -> Path:
    """Copy the upload to folder/<random name><suffix>, in blocks, up to the size limit.

    The suffix comes from the file's first bytes (its "magic number"), because the
    adapters recognise archives by suffix, and the client's file name cannot be trusted."""
    first = source.read(CHUNK_BYTES)
    path = folder / (secrets.token_hex(16) + suffix_for(first))
    size = 0
    with path.open("wb") as out:
        block = first
        while block:
            size += len(block)
            if size > app.state.max_upload_bytes:
                out.close()
                path.unlink()
                raise HTTPException(413, too_large_message(app))
            out.write(block)
            block = source.read(CHUNK_BYTES)
    return path


def suffix_for(head: bytes) -> str:
    if head[:4] in PCAP_MAGIC:
        return ".pcap"
    if head.startswith(ZIP_MAGIC):
        return ".zip"
    if head.startswith(GZIP_MAGIC):
        return ".tar.gz"  # a gzip file that is not a tar archive fails later with 400
    return ""  # unknown: the pipeline refuses it (400)


def display_name(filename: str | None) -> str:
    """'C:\\captures\\..\\shop.pcap' -> 'shop.pcap': last part only, safe characters only."""
    last = (filename or "").replace("\\", "/").rsplit("/", 1)[-1]
    cleaned = re.sub(r"[^A-Za-z0-9._ -]", "_", last).strip(" .")
    return cleaned[:100] or "upload"


def run_pipeline(app: FastAPI, path: Path, sensor_id: str | None) -> dict:
    """analyze() in a temporary work folder inside the data folder, errors -> HTTP codes."""
    work = app.state.data_dir / "work"
    work.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=work) as workdir:
        try:
            return analyze(path, workdir, explain=app.state.explain, sensor_id=sensor_id)
        except UnsupportedInput:
            raise HTTPException(
                400, "not a .pcap/.pcapng capture or a .zip/.tar.gz of Zeek logs") from None
        except ArchiveTooLarge as err:
            raise HTTPException(413, str(err)) from None
        except (zipfile.BadZipFile, tarfile.TarError, EOFError) as err:
            raise HTTPException(400, f"not a valid archive: {err}") from None
        except ZeekError as err:
            raise HTTPException(422, str(err)) from None


# ---------- reading ----------

@router.get("/api/analyses")
def list_analyses(request: Request, limit: int = Query(50, ge=1, le=1000)) -> list[dict]:
    return request.app.state.state_store.list_analyses(limit=limit)


@router.get("/api/analyses/{analysis_id}")
def get_analysis(request: Request, analysis_id: str) -> dict:
    report = request.app.state.state_store.get_analysis(analysis_id)
    if report is None:
        raise HTTPException(404, f"no analysis {analysis_id}")
    return report


@router.get("/api/alerts")
def list_alerts(request: Request, status: str | None = None, severity: str | None = None,
                limit: int = Query(200, ge=1, le=1000)) -> list[dict]:
    """The alert queue, most severe first."""
    try:
        return request.app.state.state_store.list_alerts(status=status, severity=severity,
                                                         limit=limit)
    except ValueError as err:  # unknown status or severity
        raise HTTPException(400, str(err)) from None


@router.get("/api/alerts/{finding_id}")
def get_alert(request: Request, finding_id: str) -> dict:
    alert = request.app.state.state_store.get_alert(finding_id)
    if alert is None:
        raise HTTPException(404, f"no alert {finding_id}")
    return alert


class AlertUpdate(BaseModel):
    actor: str = Field(min_length=1, max_length=100)  # who made the change (audit trail)
    status: str | None = None
    assignee: str | None = Field(default=None, max_length=100)


@router.patch("/api/alerts/{finding_id}")
def update_alert(request: Request, finding_id: str, change: AlertUpdate) -> dict:
    """Change an alert's status and/or assignee; StateStore writes the audit row."""
    try:
        alert = request.app.state.state_store.update_alert(
            finding_id, actor=change.actor, at=time.time(),
            status=change.status, assignee=change.assignee)
    except KeyError:
        raise HTTPException(404, f"no alert {finding_id}") from None
    except ValueError as err:  # unknown status
        raise HTTPException(400, str(err)) from None
    notify_change(request.app)
    return alert


@router.get("/api/events")
def list_events(request: Request, ip: str | None = None, since: float | None = None,
                until: float | None = None,
                limit: int = Query(1000, ge=1, le=10000)) -> list[dict]:
    """Timeline events in time order; ip matches the source or the destination."""
    if ip is not None:
        try:
            ip = str(ipaddress.ip_address(ip))  # also writes IPv6 the way Zeek does
        except ValueError:
            raise HTTPException(400, f"not an IP address: {ip!r}") from None
    return request.app.state.event_store.query(ip=ip, since=since, until=until, limit=limit)


@router.get("/api/assets")
def list_assets(request: Request) -> list[dict]:
    """The asset inventory of the newest analysis."""
    store = request.app.state.state_store
    newest = store.list_analyses(limit=1)
    if not newest:
        return []
    return store.get_analysis(newest[0]["analysis_id"])["assets"]


@router.get("/api/audit")
def list_audit(request: Request, limit: int = Query(200, ge=1, le=1000)) -> list[dict]:
    return request.app.state.state_store.list_audit(limit=limit)


# ---------- live updates ----------

@router.get("/api/stream")
async def stream(request: Request, max_events: int | None = Query(None, ge=1)):
    """Server-sent events: alerts-changed when alerts change, a comment line in between.

    The first event is sent at once: a dashboard that reconnects may have missed a
    change, so it refreshes once to catch up. max_events ends the stream after that
    many events (tests use it; browsers never send it)."""
    return StreamingResponse(alert_events(request.app, max_events),
                             media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache",
                                      "X-Accel-Buffering": "no"})  # nginx: do not buffer


async def alert_events(app: FastAPI, max_events: int | None) -> AsyncIterator[str]:
    sent = 0
    last = None
    quiet = 0.0
    while max_events is None or sent < max_events:
        if app.state.changes != last:
            last = app.state.changes
            sent += 1
            quiet = 0.0
            yield f"event: alerts-changed\ndata: {last}\n\n"
            continue
        await asyncio.sleep(POLL_SECONDS)
        quiet += POLL_SECONDS
        if quiet >= app.state.keepalive_seconds:
            quiet = 0.0
            yield ": keep-alive\n\n"
```

What to notice, top to bottom:

- `create_app()` keeps the stores on `app.state`, so the dashboard (AHM-02) and the response module (AHM-08) reach them through `request.app.state`. Their routers are included only when their modules exist (`optional_module`); a module that exists but has a bug still fails loudly.
- An upload is saved under a random name, and its suffix comes from the file's first bytes, never from the client's file name. The client's name is cleaned and only shown, never used as a path.
- The size limit is checked twice: from the `Content-Length` header before the body is read, and while copying (a client can leave the header out).
- `POST /api/ingest` checks the token **before** it reads the body, so a stranger cannot make the console store anything; `hmac.compare_digest` takes the same time however many characters match. A token shorter than 32 characters stops the app at start-up.
- `create_ingest_app()` builds a second, tiny app with nothing but `POST /api/ingest` (no dashboard, no `/docs` page). JAK-07 publishes it on the console's LAN address, port 8001, for sensors and host agents; the full app stays on `127.0.0.1`, so nobody on the network can read alerts or approve a block. Both apps share the data folder; the dashboard shows ingested data at its next refresh.
- Browsers let any website *send* a form to `127.0.0.1`. `refuse_cross_site_changes` refuses changing requests that a browser marks as coming from another site (cross-site request forgery). curl, sensors and tests send no `Origin` header and are not affected.
- A website can also point its own name at `127.0.0.1` after its page has loaded (DNS rebinding). The browser then treats the API as part of that website, and the cross-site check cannot tell. `TrustedHostMiddleware` (from Starlette, which FastAPI is built on) answers `400 Invalid host header` unless the `Host` header names this machine or an address in `MAXGUARD_ALLOWED_HOSTS`. When sensors or agents send to the console over the LAN, add the console's LAN address there.
- `GET /api/stream` sends one `alerts-changed` at once (a dashboard that reconnects may have missed a change), then one per change, with a `: keep-alive` comment every 15 seconds.

**Step 4.** FastAPI's `TestClient` calls the app `testserver`, a name the host check refuses. Add this fixture at the end of `tests/conftest.py` (`autouse=True` gives it to every test without asking):

```python
@pytest.fixture(autouse=True)
def allow_test_client_host(monkeypatch):
    """The API answers only host names in MAXGUARD_ALLOWED_HOSTS (JAI-07), and FastAPI's
    TestClient calls the app "testserver". autouse: every test gets it without asking."""
    monkeypatch.setenv("MAXGUARD_ALLOWED_HOSTS", "testserver,localhost,127.0.0.1,[::1]")
```

**Step 5.** Create the unit tests `tests/unit/test_api.py`:

```python
"""Tests for the API (Jaiden, JAI-07).

Uploads use a zip of the Zeek log fixture tests/fixtures/zeek/telnet: it goes
through ZeekLogAdapter, so these tests need no Zeek. The integration test
tests/integration/test_api_upload.py uploads a real capture.
"""

from __future__ import annotations

import io
import re
import threading
import zipfile
from pathlib import Path

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from maxguard.api import app as api_app
from maxguard.api.app import (
    create_app,
    create_ingest_app,
    display_name,
    notify_change,
    optional_module,
    save_upload,
    suffix_for,
)

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures" / "zeek"
TOKEN = "t" * 43  # a test value with the length of secrets.token_urlsafe(32)


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    """Every test starts with the settings off, whatever the shell has set."""
    for name in ("MAXGUARD_INGEST_TOKEN", "MAXGUARD_MAX_UPLOAD_MB", "MAXGUARD_KEEP_UPLOADS",
                 "MAXGUARD_OFFLINE", "MAXGUARD_DATA_DIR"):
        monkeypatch.delenv(name, raising=False)


@pytest.fixture
def data_dir(tmp_path) -> Path:
    return tmp_path / "data"


@pytest.fixture
def client(data_dir) -> TestClient:
    return TestClient(create_app(data_dir, explain=False))


def zipped_fixture(name: str = "telnet") -> bytes:
    """The fixture folder as a .zip in memory, with the logs at the top level."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        for log in sorted((FIXTURES / name).iterdir()):
            archive.write(log, arcname=log.name)
    return buffer.getvalue()


def upload(client: TestClient, data: bytes, filename: str = "telnet.zip", **kwargs):
    return client.post("/api/analyses", files={"file": (filename, data)}, **kwargs)


def uploaded_files(data_dir: Path) -> list[Path]:
    return sorted((data_dir / "uploads").iterdir())


# ---------- uploads ----------

def test_upload_creates_the_telnet_alert(client):
    response = upload(client, zipped_fixture())
    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"analysis_id", "findings"}
    assert body["findings"] == 1

    [alert] = client.get("/api/alerts").json()
    assert alert["rule_id"] == "cleartext.telnet"
    assert alert["status"] == "new"
    assert alert["count"] == 1
    assert alert["analysis_id"] == body["analysis_id"]

    [analysis] = client.get("/api/analyses").json()
    assert analysis["input_name"] == "telnet.zip"  # the name the person knows
    report = client.get(f"/api/analyses/{body['analysis_id']}").json()
    assert report["schema"] == "maxguard.report/2"
    assert "events" not in report  # events live in the event store


def test_the_same_file_twice_is_not_counted_twice(client):
    data = zipped_fixture()
    upload(client, data)
    upload(client, data)
    [alert] = client.get("/api/alerts").json()
    assert alert["count"] == 1
    assert len(client.get("/api/analyses").json()) == 2  # both uploads are on record


def test_upload_is_stored_under_a_generated_name_and_deleted(client, data_dir):
    response = upload(client, zipped_fixture(), filename="../../evil.zip")
    assert response.status_code == 200
    assert uploaded_files(data_dir) == []  # deleted after the analysis
    assert not (data_dir.parent / "evil.zip").exists()
    assert client.get("/api/analyses").json()[0]["input_name"] == "evil.zip"


def test_keep_uploads_keeps_the_file_under_our_name(monkeypatch, data_dir):
    monkeypatch.setenv("MAXGUARD_KEEP_UPLOADS", "1")
    client = TestClient(create_app(data_dir, explain=False))
    upload(client, zipped_fixture(), filename="../../evil.zip")
    [kept] = uploaded_files(data_dir)
    assert re.fullmatch(r"[0-9a-f]{32}\.zip", kept.name)


def test_unsupported_file_is_refused(client, data_dir):
    response = upload(client, b"just some text", filename="notes.txt")
    assert response.status_code == 400
    assert "not a .pcap/.pcapng capture" in response.json()["detail"]
    assert uploaded_files(data_dir) == []


def test_broken_archive_is_refused(client, data_dir):
    response = upload(client, b"PK\x03\x04 this is not really a zip", filename="logs.zip")
    assert response.status_code == 400
    assert uploaded_files(data_dir) == []


def test_upload_without_a_file_field_is_refused(client):
    response = client.post("/api/analyses", files={"wrong_name": ("a.zip", b"PK")})
    assert response.status_code == 400


def test_too_large_upload_is_refused(monkeypatch, data_dir):
    monkeypatch.setenv("MAXGUARD_MAX_UPLOAD_MB", "1")
    client = TestClient(create_app(data_dir, explain=False))
    response = upload(client, b"\0" * (2 * 1024 * 1024), filename="big.pcap")
    assert response.status_code == 413
    assert "MAXGUARD_MAX_UPLOAD_MB" in response.json()["detail"]
    assert not (data_dir / "uploads").exists() or uploaded_files(data_dir) == []


def test_save_upload_stops_at_the_limit_and_removes_the_partial_file(data_dir):
    # A client can leave out Content-Length; then only the copy loop sees the size.
    app = create_app(data_dir, explain=False)
    app.state.max_upload_bytes = 10
    folder = data_dir / "uploads"
    folder.mkdir()
    with pytest.raises(HTTPException) as caught:
        save_upload(io.BytesIO(b"x" * 11), folder, app)
    assert caught.value.status_code == 413
    assert list(folder.iterdir()) == []


def test_bad_upload_size_setting_fails_at_start(monkeypatch, data_dir):
    monkeypatch.setenv("MAXGUARD_MAX_UPLOAD_MB", "lots")
    with pytest.raises(ValueError, match="MAXGUARD_MAX_UPLOAD_MB"):
        create_app(data_dir, explain=False)


# ---------- alerts, audit, events, assets ----------

def test_patch_changes_status_and_writes_the_audit_trail(client):
    upload(client, zipped_fixture())
    [alert] = client.get("/api/alerts").json()
    url = f"/api/alerts/{alert['finding_id']}"

    response = client.patch(url, json={"actor": "ahmad", "status": "investigating",
                                       "assignee": "fiona"})
    assert response.status_code == 200
    assert response.json()["status"] == "investigating"
    assert client.get(url).json()["assignee"] == "fiona"

    [entry] = client.get("/api/audit").json()
    assert entry["actor"] == "ahmad"
    assert entry["action"] == "alert.update"
    assert entry["target"] == alert["finding_id"]
    assert entry["details"]["status"] == {"from": "new", "to": "investigating"}


def test_patch_errors(client):
    upload(client, zipped_fixture())
    [alert] = client.get("/api/alerts").json()
    url = f"/api/alerts/{alert['finding_id']}"
    assert client.patch("/api/alerts/0000000000000000",
                        json={"actor": "ahmad", "status": "resolved"}).status_code == 404
    assert client.patch(url, json={"actor": "ahmad", "status": "fixed"}).status_code == 400
    assert client.patch(url, json={"status": "resolved"}).status_code == 422  # no actor


def test_alert_filters(client):
    upload(client, zipped_fixture())
    assert len(client.get("/api/alerts", params={"severity": "high"}).json()) == 1
    assert client.get("/api/alerts", params={"severity": "low"}).json() == []
    assert client.get("/api/alerts", params={"status": "new"}).json()[0]["status"] == "new"
    assert client.get("/api/alerts", params={"status": "bogus"}).status_code == 400
    assert client.get("/api/alerts", params={"limit": 0}).status_code == 422


def test_unknown_ids_are_404(client):
    assert client.get("/api/alerts/0000000000000000").status_code == 404
    assert client.get("/api/analyses/0000000000000000").status_code == 404


def test_events_and_assets(client):
    assert client.get("/api/events").json() == []
    assert client.get("/api/assets").json() == []
    upload(client, zipped_fixture())

    events = client.get("/api/events").json()
    assert len(events) == 1
    assert events[0]["dst_port"] == 23
    assert events[0]["sensor_id"] == "import"  # uploaded Zeek logs
    assert client.get("/api/events", params={"ip": "172.18.0.3"}).json() == events
    assert client.get("/api/events", params={"ip": "192.0.2.99"}).json() == []
    assert client.get("/api/events", params={"ip": "not-an-ip"}).status_code == 400

    ips = [asset["ip"] for asset in client.get("/api/assets").json()]
    assert ips == ["172.18.0.2", "172.18.0.3"]


# ---------- ingest ----------

def test_ingest_is_off_without_a_token(client):
    response = client.post("/api/ingest", files={"file": ("x.zip", zipped_fixture())})
    assert response.status_code == 404


def test_ingest_needs_the_right_token(monkeypatch, data_dir):
    monkeypatch.setenv("MAXGUARD_INGEST_TOKEN", TOKEN)
    client = TestClient(create_app(data_dir, explain=False))
    files = {"file": ("2026-10-06-1400.tar.gz", zipped_fixture())}

    missing = client.post("/api/ingest", files=files)
    assert missing.status_code == 401
    assert missing.headers["www-authenticate"] == "Bearer"
    wrong = client.post("/api/ingest", files=files, headers={"Authorization": "Bearer nope"})
    assert wrong.status_code == 401
    assert client.get("/api/alerts").json() == []  # nothing was stored

    right = client.post("/api/ingest", files=files, data={"sensor_id": "lab-sensor"},
                        headers={"Authorization": f"Bearer {TOKEN}"})
    assert right.status_code == 200
    assert right.json()["findings"] == 1
    assert {e["sensor_id"] for e in client.get("/api/events").json()} == {"lab-sensor"}


def test_ingest_refuses_a_bad_sensor_name(monkeypatch, data_dir):
    monkeypatch.setenv("MAXGUARD_INGEST_TOKEN", TOKEN)
    client = TestClient(create_app(data_dir, explain=False))
    response = client.post("/api/ingest", files={"file": ("x.zip", zipped_fixture())},
                           data={"sensor_id": "../etc"},
                           headers={"Authorization": f"Bearer {TOKEN}"})
    assert response.status_code == 400


def test_short_ingest_token_is_refused_at_start(monkeypatch, data_dir):
    monkeypatch.setenv("MAXGUARD_INGEST_TOKEN", "secret")
    with pytest.raises(ValueError, match="at least 32 characters"):
        create_app(data_dir, explain=False)


def test_the_ingest_app_serves_only_ingest(monkeypatch, data_dir):
    # The port published on the LAN (docker/compose.lan.yaml): nothing to read there.
    monkeypatch.setenv("MAXGUARD_INGEST_TOKEN", TOKEN)
    lan = TestClient(create_ingest_app(data_dir, explain=False))
    for path in ("/api/alerts", "/api/events", "/api/audit", "/", "/docs", "/openapi.json"):
        assert lan.get(path).status_code == 404, path
    assert list(lan.app.openapi()["paths"]) == ["/api/ingest"]  # its only route

    sent = lan.post("/api/ingest", files={"file": ("2026-10-06-1400.tar.gz", zipped_fixture())},
                    data={"sensor_id": "lab-sensor"},
                    headers={"Authorization": f"Bearer {TOKEN}"})
    assert sent.status_code == 200
    # The dashboard's app reads the same data folder.
    console = TestClient(create_app(data_dir, explain=False))
    assert [a["rule_id"] for a in console.get("/api/alerts").json()] == ["cleartext.telnet"]


def test_the_ingest_app_needs_a_token(data_dir):
    with pytest.raises(ValueError, match="MAXGUARD_INGEST_TOKEN"):
        create_ingest_app(data_dir, explain=False)


# ---------- cross-site requests ----------

def test_another_website_cannot_upload(client):
    data = zipped_fixture()
    other = upload(client, data, headers={"Origin": "http://evil.example"})
    assert other.status_code == 403
    fetch_metadata = upload(client, data, headers={"Sec-Fetch-Site": "cross-site"})
    assert fetch_metadata.status_code == 403
    other_port = upload(client, data, headers={"Sec-Fetch-Site": "same-site"})
    assert other_port.status_code == 403
    sandboxed = upload(client, data, headers={"Origin": "null"})
    assert sandboxed.status_code == 403
    same_site = upload(client, data, headers={"Origin": "http://testserver"})
    assert same_site.status_code == 200


# ---------- DNS rebinding: only this machine's names ----------

def test_a_request_for_an_unknown_host_name_is_refused(data_dir):
    # What a DNS-rebinding page sends: its own name, now pointing at 127.0.0.1.
    client = TestClient(create_app(data_dir, explain=False),
                        base_url="http://rebind.example:8000")
    response = client.get("/api/alerts")
    assert response.status_code == 400
    assert response.text == "Invalid host header"


@pytest.mark.parametrize("host", ["127.0.0.1:8000", "localhost:8000", "[::1]:8000", "localhost"])
def test_this_machine_is_allowed_by_default(data_dir, monkeypatch, host):
    monkeypatch.delenv("MAXGUARD_ALLOWED_HOSTS")
    client = TestClient(create_app(data_dir, explain=False), base_url=f"http://{host}")
    assert client.get("/api/alerts").status_code == 200


def test_the_consoles_lan_address_can_be_added(data_dir, monkeypatch):
    monkeypatch.setenv("MAXGUARD_ALLOWED_HOSTS", "localhost, 192.168.50.20")
    app = create_app(data_dir, explain=False)
    assert TestClient(app, base_url="http://192.168.50.20:8000").get(
        "/api/alerts").status_code == 200
    assert TestClient(app, base_url="http://192.168.50.21:8000").get(
        "/api/alerts").status_code == 400


@pytest.mark.parametrize("value", ["http://192.168.50.20", "192.168.50.20:8000", "*", " , "])
def test_a_wrong_allowed_hosts_setting_stops_the_app(data_dir, monkeypatch, value):
    monkeypatch.setenv("MAXGUARD_ALLOWED_HOSTS", value)
    with pytest.raises(ValueError, match="MAXGUARD_ALLOWED_HOSTS"):
        create_app(data_dir, explain=False)


# ---------- live updates ----------

def test_stream_sends_alerts_changed(client):
    app = client.app
    app.state.keepalive_seconds = 0.5  # instead of 15 s, so the test sees one
    timer = threading.Timer(1.2, notify_change, args=[app])
    timer.start()
    with client.stream("GET", "/api/stream", params={"max_events": 2}) as response:
        assert response.headers["content-type"].startswith("text/event-stream")
        text = "".join(response.iter_text())
    timer.join()
    assert text.startswith("event: alerts-changed\ndata: 0\n\n")  # sent at once
    assert ": keep-alive\n\n" in text
    assert text.endswith("event: alerts-changed\ndata: 1\n\n")    # after the change


# ---------- small helpers and the app itself ----------

def test_display_name_keeps_only_a_safe_last_part():
    assert display_name("C:\\captures\\..\\shop.pcap") == "shop.pcap"
    assert display_name("../../etc/passwd") == "passwd"
    assert display_name("<script>.pcap") == "_script_.pcap"
    assert display_name(None) == "upload"
    assert display_name("..") == "upload"


def test_suffix_comes_from_the_first_bytes():
    assert suffix_for(b"\xd4\xc3\xb2\xa1rest") == ".pcap"
    assert suffix_for(b"\x0a\x0d\x0d\x0arest") == ".pcap"  # pcapng
    assert suffix_for(b"PK\x03\x04rest") == ".zip"
    assert suffix_for(b"\x1f\x8brest") == ".tar.gz"
    assert suffix_for(b"hello") == ""


def test_optional_modules_that_do_not_exist_are_skipped():
    assert optional_module("maxguard.no_such_module") is None
    assert optional_module("maxguard.no_such_package.routes") is None


def test_static_files_are_served(monkeypatch, data_dir, tmp_path):
    # The dashboard's files (AHM-02) live in maxguard/web/static; a stand-in folder
    # shows the mount works before they exist.
    static = tmp_path / "static"
    static.mkdir()
    (static / "hello.txt").write_text("hello")
    monkeypatch.setattr(api_app, "STATIC_DIR", static)
    client = TestClient(create_app(data_dir, explain=False))
    assert client.get("/static/hello.txt").text == "hello"
    assert client.get("/static/missing.txt").status_code == 404


def test_openapi_page_shows_the_upload_field(client):
    schema = client.get("/openapi.json").json()
    body = schema["paths"]["/api/analyses"]["post"]["requestBody"]
    assert "file" in body["content"]["multipart/form-data"]["schema"]["properties"]
    assert "sensor_id" in str(schema["paths"]["/api/ingest"]["post"]["requestBody"])


def test_data_dir_defaults_to_the_environment(monkeypatch, tmp_path):
    monkeypatch.setenv("MAXGUARD_DATA_DIR", str(tmp_path / "from-env"))
    app = create_app(explain=False)
    assert app.state.data_dir == tmp_path / "from-env"
    assert (tmp_path / "from-env" / "state.db").exists()
```

**Step 6.** Run them:

```bash
pytest tests/unit/test_api.py -q
```

Expected output:

```text
.......................................                                                      [100%]
39 passed in 3.87s
```

**Step 7.** Create the integration test `tests/integration/test_api_upload.py`, which uploads a real capture, so Zeek runs:

```python
"""Integration test for the API (Jaiden, JAI-07): a real capture through Zeek.

Runs inside the engine test image (pytest -m integration), where Zeek is installed.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from maxguard.api.app import create_app

PCAPS = Path(__file__).resolve().parent.parent / "pcaps"

pytestmark = pytest.mark.integration


def test_uploading_a_real_capture_creates_the_alert(tmp_path):
    client = TestClient(create_app(tmp_path / "data", explain=False))
    with (PCAPS / "telnet.pcap").open("rb") as capture:
        response = client.post("/api/analyses", files={"file": ("telnet.pcap", capture)})
    assert response.status_code == 200, response.text

    [alert] = client.get("/api/alerts").json()
    assert alert["rule_id"] == "cleartext.telnet"
    assert alert["dst_port"] == 23

    report = client.get(f"/api/analyses/{response.json()['analysis_id']}").json()
    assert report["tools"]["zeek"] is True
    assert report["input"]["name"] == "telnet.pcap"

    events = client.get("/api/events").json()
    assert events
    assert {event["sensor_id"] for event in events} == {"pcap"}
    assert list((tmp_path / "data" / "uploads").iterdir()) == []  # deleted afterwards
```

Run it in the test image from JAI-04 (rebuild the image first: it copies the tests folder):

```bash
docker build -f docker/Dockerfile --target test -t maxguard:test .
docker run --rm --network none maxguard:test pytest -m integration tests/integration/test_api_upload.py -q
```

Expected output:

```text
.                                                                        [100%]
1 passed in 1.54s
```

*Run in planning inside `zeek/zeek:9.0.0` with MaxGuard's Python packages added, because the engine image build needs Debian's package servers (see JAI-04). The test output is the same.*

**Step 8.** Start the API and try it with curl. Start the server in one terminal, then run the rest in a second terminal from the repository root (on Windows use Git Bash):

```bash
# terminal 1:
uvicorn maxguard.api.app:create_app --factory --host 127.0.0.1 --port 8000
# terminal 2:
python -c "import shutil; shutil.make_archive('data/telnet', 'zip', 'tests/fixtures/zeek/telnet')"
curl -s -F file=@data/telnet.zip http://127.0.0.1:8000/api/analyses; echo
curl -s http://127.0.0.1:8000/api/alerts | python -c "import json, sys; [print(a['rule_id'], a['severity'], a['src_ip'], '->', a['dst_ip'], a['dst_port'], a['status']) for a in json.load(sys.stdin)]"
curl -s -o /dev/null -w '%{http_code}\n' -F file=@data/telnet.zip http://127.0.0.1:8000/api/ingest
```

Expected output:

```text
{"analysis_id":"0c0036ba63bb7644","findings":1}
cleartext.telnet high 172.18.0.3 -> 172.18.0.2 23 new
404
```

*The analysis ID depends on the moment of the upload, so yours differs. The last line is `404`: ingest is off because `MAXGUARD_INGEST_TOKEN` is not set.*

Open http://127.0.0.1:8000/docs: FastAPI's OpenAPI page lists every endpoint, and it is the API contract for the dashboard. Stop the server with Ctrl+C.

**Step 9.** Commit, push, and open the pull request:

```bash
git add -A
git status          # only this task's files: nothing from .venv/, data/ or lab/captures/
git commit -m "feat: FastAPI app with uploads, alerts, events, SSE and ingest (JAI-07)"
git push -u origin HEAD
```

`HEAD` means "the branch I am on", so you do not have to retype its name. Open the repository on github.com: a yellow bar shows your branch with a **Compare & pull request** button. Click it, keep the title `feat: FastAPI app with uploads, alerts, events, SSE and ingest (JAI-07)`, fill in the template (paste the real output of the commands above under **How I tested it**), write `Closes #<issue number>` (this task's issue), and pick **@ahmadalkhoudeir** under **Reviewers**. Click **Create pull request**, then fix anything CI or the reviewer finds with new commits on the same branch.

#### How to test

The unit tests and the integration test pass, and the manual run shows the Telnet alert from the uploaded zip in `/api/alerts`.

#### What you just did and why

The engine never reads the clock and never writes to storage; the API does both, in one place, which keeps the engine deterministic and easy to test. Generated file names, the upload limit, the token check before the body is read, and the cross-site check close the obvious ways a hostile client could attack the console (`docs/ARCHITECTURE.md` section 14).

#### Pull request checklist

- [ ] `ruff check .` prints `All checks passed!`
- [ ] `pytest -m "not integration" -q` passes on your laptop
- [ ] The pull request title has the form `type: summary (TASK-ID)` and the body says `Closes #<issue number>`
- [ ] No secrets, passwords, email addresses, personal data, or captures from a real network (CLAUDE.md rule 6)
- [ ] Any new dependency has a row in `docs/DEPENDENCIES.md` with its license
- [ ] CI is green and your reviewer approved
- [ ] The client's file name is never used as a path
- [ ] Ingest is off unless the token is set

### JAI-08: Ed25519 signing library

**Due:** Week 5 (due Fri Nov 13) · **Milestone:** `W5 Alpha feature freeze` · **Needs first:** [JAI-01](#jai-01-restructure-the-repository-add-packaging-and-ci) · **Kind:** code, tested

**Issue labels:** `type:task` `phase:alpha` `owner:jaiden` `area:release`

#### Goal

Provide `generate_keypair`, `sign`, and `verify` with Ed25519 signatures, used by the chain-of-custody log (AMO-05) and the signed intel bundles (JAI-11).

#### Prerequisites

JAI-01 is merged.

#### Steps

**Step 1.** Update `main` and create your branch for this task (one branch per task):

```bash
cd ~/projects/maxguard
source .venv/bin/activate
git checkout main && git pull
git checkout -b jaiden/signing
```

If `source .venv/bin/activate` fails, you have not made the virtual environment yet: do Week 0 section 0.11 first.

**Step 2.** Create `maxguard/custody/__init__.py`:

```python
"""Chain of custody: proof that reports and evidence were not changed later.

- signing.py: Ed25519 keys, sign() and verify().
- log.py: the append-only custody log.
"""
```

and `maxguard/custody/signing.py`:

```python
"""Ed25519 signatures for chain of custody (v2.0).

MaxGuard signs the reports and evidence files it produces so that anyone with
the public key can later check that a file was not changed after MaxGuard
wrote it. Ed25519 is used because its keys are small, signing is fast, and it
has no settings (curve, hash, padding) that a user could get wrong.

Where the keys live
-------------------
Key files are secrets and must never be inside the git repository. They go in
the MaxGuard data directory, in a "keys" folder (see key_dir_for):
- in the Docker image: /data/keys (the /data volume, outside the code)
- on a developer laptop: ./data/keys (data/ is listed in .gitignore)

The private key file is created with permissions 0600 (only its owner can read
it) and is not password protected: the file permissions are the protection.
"""

from __future__ import annotations

import os
from pathlib import Path

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

KEY_SUBDIR = "keys"
PRIVATE_KEY_NAME = "custody_ed25519_private.pem"
PUBLIC_KEY_NAME = "custody_ed25519_public.pem"


def key_dir_for(data_dir: Path) -> Path:
    """The folder that holds the custody keys inside a MaxGuard data directory."""
    return Path(data_dir) / KEY_SUBDIR


def generate_keypair(key_dir: Path) -> tuple[Path, Path]:
    """Create a new key pair in key_dir and return (private_key_path, public_key_path).

    Refuses to replace an existing private key: a new key would make every
    signature made with the old key impossible to check.
    """
    key_dir = Path(key_dir)
    key_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
    private_path = key_dir / PRIVATE_KEY_NAME
    public_path = key_dir / PUBLIC_KEY_NAME
    if private_path.exists():
        raise FileExistsError(f"{private_path} already exists; refusing to replace a custody key")

    private_key = Ed25519PrivateKey.generate()
    write_private_file(private_path, private_key_pem(private_key))
    public_path.write_bytes(public_key_pem(private_key.public_key()))
    return private_path, public_path


def private_key_pem(private_key: Ed25519PrivateKey) -> bytes:
    return private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )


def public_key_pem(public_key: Ed25519PublicKey) -> bytes:
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )


def write_private_file(path: Path, data: bytes) -> None:
    """Write a secret file that only its owner can read.

    The 0o600 mode is given when the file is created, so the key is never
    readable by other users, not even for a moment. O_EXCL makes the call fail
    if the file already exists instead of overwriting it.
    """
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as f:
        f.write(data)


def load_private_key(private_key_path: Path) -> Ed25519PrivateKey:
    key = serialization.load_pem_private_key(Path(private_key_path).read_bytes(), password=None)
    if not isinstance(key, Ed25519PrivateKey):
        raise TypeError(f"{private_key_path} is not an Ed25519 private key")
    return key


def load_public_key(public_key_path: Path) -> Ed25519PublicKey:
    key = serialization.load_pem_public_key(Path(public_key_path).read_bytes())
    if not isinstance(key, Ed25519PublicKey):
        raise TypeError(f"{public_key_path} is not an Ed25519 public key")
    return key


def sign(data: bytes, private_key_path: Path) -> bytes:
    """Return the 64-byte Ed25519 signature of data.

    Ed25519 signatures are deterministic: the same key and the same data always
    give the same signature (no random numbers are involved).
    """
    return load_private_key(private_key_path).sign(data)


def verify(data: bytes, signature: bytes, public_key_path: Path) -> bool:
    """True if signature was made over exactly these bytes by the matching private key."""
    public_key = load_public_key(public_key_path)
    try:
        public_key.verify(signature, data)
    except InvalidSignature:
        return False
    return True
```

**Step 3.** Create the tests `tests/unit/test_signing.py`:

```python
"""Tests for maxguard.custody.signing (Ed25519 chain-of-custody signatures)."""

from __future__ import annotations

import os
import stat
from pathlib import Path

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec

from maxguard.custody import signing

REPO_ROOT = Path(__file__).resolve().parents[2]
REPORT = b'{"schema": "maxguard.report/2", "findings": []}'


@pytest.fixture
def keys(tmp_path: Path) -> tuple[Path, Path]:
    return signing.generate_keypair(tmp_path / "keys")


def test_generate_keypair_writes_two_pem_files(keys):
    private_path, public_path = keys
    assert private_path.read_bytes().startswith(b"-----BEGIN PRIVATE KEY-----")
    assert public_path.read_bytes().startswith(b"-----BEGIN PUBLIC KEY-----")


@pytest.mark.skipif(os.name != "posix", reason="file modes are a POSIX feature")
def test_private_key_is_readable_by_owner_only(keys):
    private_path, _ = keys
    assert stat.S_IMODE(private_path.stat().st_mode) == 0o600


def test_generate_keypair_refuses_to_replace_existing_key(keys, tmp_path):
    with pytest.raises(FileExistsError):
        signing.generate_keypair(tmp_path / "keys")


def test_signature_verifies(keys):
    private_path, public_path = keys
    signature = signing.sign(REPORT, private_path)
    assert len(signature) == 64
    assert signing.verify(REPORT, signature, public_path) is True


def test_signature_is_deterministic(keys):
    private_path, _ = keys
    assert signing.sign(REPORT, private_path) == signing.sign(REPORT, private_path)


def test_changed_data_fails_verification(keys):
    private_path, public_path = keys
    signature = signing.sign(REPORT, private_path)
    changed = REPORT.replace(b"[]", b"[1]")
    assert signing.verify(changed, signature, public_path) is False


def test_signature_from_another_key_fails(keys, tmp_path):
    private_path, _ = keys
    _, other_public_path = signing.generate_keypair(tmp_path / "other")
    signature = signing.sign(REPORT, private_path)
    assert signing.verify(REPORT, signature, other_public_path) is False


@pytest.mark.parametrize("bad_signature", [b"", b"short", bytes(64), bytes(65)])
def test_malformed_signature_fails(keys, bad_signature):
    _, public_path = keys
    assert signing.verify(REPORT, bad_signature, public_path) is False


def test_sign_rejects_a_non_ed25519_key(tmp_path):
    ec_key = ec.generate_private_key(ec.SECP256R1())
    pem = ec_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    key_path = tmp_path / "ec.pem"
    key_path.write_bytes(pem)
    with pytest.raises(TypeError):
        signing.sign(REPORT, key_path)


def test_key_dir_is_inside_the_data_dir():
    assert signing.key_dir_for(Path("/data")) == Path("/data/keys")


@pytest.mark.skipif(
    not (REPO_ROOT / ".gitignore").exists(), reason="not a git checkout (e.g. the Docker image)"
)
def test_data_dir_is_git_ignored():
    # Keys live under data/ on a laptop; this keeps them out of every commit.
    ignored = (REPO_ROOT / ".gitignore").read_text().splitlines()
    assert "data/" in ignored
```

**Step 4.** Run them:

```bash
pytest tests/unit/test_signing.py -q
```

Expected output:

```text
..............                                                                               [100%]
14 passed in 0.16s
```

**Step 5.** Commit, push, and open the pull request:

```bash
git add -A
git status          # only this task's files: nothing from .venv/, data/ or lab/captures/
git commit -m "feat: Ed25519 signing helpers (JAI-08)"
git push -u origin HEAD
```

`HEAD` means "the branch I am on", so you do not have to retype its name. Open the repository on github.com: a yellow bar shows your branch with a **Compare & pull request** button. Click it, keep the title `feat: Ed25519 signing helpers (JAI-08)`, fill in the template (paste the real output of the commands above under **How I tested it**), write `Closes #<issue number>` (this task's issue), and pick **@ahmadalkhoudeir** under **Reviewers**. Click **Create pull request**, then fix anything CI or the reviewer finds with new commits on the same branch.

#### How to test

The tests sign data, verify it, and prove that changing one byte, using the wrong key, or a damaged signature all fail verification.

#### What you just did and why

A hash proves a file did not change *if* you trust where the hash came from. A signature also proves *who* wrote it: only the holder of the private key can make a signature that the public key accepts. Ed25519 keys are small and fast, and the `cryptography` library (Apache-2.0/BSD) is the standard way to use them in Python. Private keys live in the data folder, never in the repository (CLAUDE.md rule 6).

#### Pull request checklist

- [ ] `ruff check .` prints `All checks passed!`
- [ ] `pytest -m "not integration" -q` passes on your laptop
- [ ] The pull request title has the form `type: summary (TASK-ID)` and the body says `Closes #<issue number>`
- [ ] No secrets, passwords, email addresses, personal data, or captures from a real network (CLAUDE.md rule 6)
- [ ] Any new dependency has a row in `docs/DEPENDENCIES.md` with its license
- [ ] CI is green and your reviewer approved
- [ ] No key file is committed (`git status` shows none)

### JAI-09: Release workflow and v2.0-alpha-rc1

**Due:** Week 6 (due Fri Nov 20) · **Milestone:** `W6 Release candidate` · **Needs first:** [JAI-04](#jai-04-the-engine-image-and-the-compose-files), [KAR-04](karthik.md#kar-04-ci-runs-the-integration-tests-plus-a-determinism-test), [JON-05](jonattan.md#jon-05-offline-bundle-install-maxguard-on-a-machine-with-no-internet) · **Kind:** design

**Issue labels:** `type:task` `phase:alpha` `owner:jaiden` `area:release` `critical-path`

> **Design task.** The code for this task was not written during planning. The steps give the files, the interfaces and the tests to write; the code is yours. Ask in GitHub Discussions when something is unclear, and update this section in your pull request with what you built.

#### Goal

Add `.github/workflows/release.yml`: when a tag `v*` is pushed, build the image for `linux/amd64` and `linux/arm64`, push it to the GitHub Container Registry, and create a GitHub Release with a `SHA256SUMS` file. Then tag `v2.0-alpha-rc1` and attach the offline bundle.

#### Prerequisites

JAI-04, KAR-04 and JON-05 are merged, and every W5 issue is closed or moved.

#### Steps

**Step 1.** Update `main` and create your branch for this task (one branch per task):

```bash
cd ~/projects/maxguard
source .venv/bin/activate
git checkout main && git pull
git checkout -b jaiden/release-workflow
```

If `source .venv/bin/activate` fails, you have not made the virtual environment yet: do Week 0 section 0.11 first.

**Step 2.** Write `release.yml` with `on: push: tags: ["v*"]`, `permissions: contents: write, packages: write`, and the official Docker actions (`docker/setup-qemu-action`, `docker/setup-buildx-action`, `docker/login-action` with `GITHUB_TOKEN`, `docker/build-push-action` with `platforms: linux/amd64,linux/arm64`). On October 6, 2026 the newest major versions were `actions/checkout@v7`, `docker/setup-qemu-action@v4`, `docker/setup-buildx-action@v4`, `docker/login-action@v4` and `docker/build-push-action@v7` (read with `git ls-remote --tags https://github.com/<owner>/<action>`); check again and pin the newest.

**Step 3.** Validate the file with `actionlint` before merging (`pip install actionlint-py==1.7.12.25` in a throwaway virtual environment).

**Step 4.** After merging: write the release notes in `docs/releases/v2.0-alpha-rc1.md` (what works, known limits, how to install offline), then:

```bash
git checkout main && git pull
git tag -a v2.0-alpha-rc1 -m "MaxGuard v2.0-alpha release candidate 1"
git push origin v2.0-alpha-rc1
```

**Step 5.** When the workflow is green, build the offline bundle (JON-05) and attach its parts and `SHA256SUMS` to the release with `gh release upload v2.0-alpha-rc1 dist/*`. Hand it to Karthik for KAR-05.

#### How to test

The release page shows both architectures in the image's manifest and the bundle parts with their checksums.

#### What you just did and why

Releases built by CI from a tag are reproducible: anyone can see exactly which commit and which steps made them. The ARM64 image is what the Raspberry Pi sensor and Apple Silicon laptops run.

#### Pull request checklist

- [ ] `ruff check .` prints `All checks passed!`
- [ ] `pytest -m "not integration" -q` passes on your laptop
- [ ] The pull request title has the form `type: summary (TASK-ID)` and the body says `Closes #<issue number>`
- [ ] No secrets, passwords, email addresses, personal data, or captures from a real network (CLAUDE.md rule 6)
- [ ] Any new dependency has a row in `docs/DEPENDENCIES.md` with its license
- [ ] CI is green and your reviewer approved
- [ ] `actionlint` is clean
- [ ] The release has `SHA256SUMS`

### JAI-10: Release v2.0-alpha

**Due:** Week 8 (due Fri Dec 4) · **Milestone:** `W8 v2.0-alpha` · **Needs first:** [JAI-09](#jai-09-release-workflow-and-v20-alpha-rc1), [KAR-05](karthik.md#kar-05-release-candidate-test-with-an-outside-tester) · **Kind:** process

**Issue labels:** `type:task` `phase:alpha` `owner:jaiden` `area:release` `critical-path`

#### Goal

Fix or defer every issue from the release-candidate test, then tag and publish `v2.0-alpha` with release notes and the offline bundle.

#### Prerequisites

KAR-05's issues are closed or moved to spring with the Security Lead's agreement.

#### Steps

**Step 1.** Merge the last fixes; check CI is green on `main`.

**Step 2.** Write `docs/releases/v2.0-alpha.md`; tag `v2.0-alpha` the same way as the release candidate; attach the bundle; announce it in Discussions.

**Step 3.** Run the acceptance test with Ahmad (AHM-05).

#### How to test

The acceptance test passes on the published release.

#### What you just did and why

A tagged release is a promise the team can be held to: the same files for everyone.

#### Pull request checklist

- [ ] Release notes written
- [ ] Bundle attached with `SHA256SUMS`

## Spring 2027: v2.0

### JAI-11: Signed offline intel bundles

**Due:** Spring S5-S8 (due Fri Mar 12, 2027) · **Milestone:** `S5-S8 Respond` · **Needs first:** [JAI-08](#jai-08-ed25519-signing-library), [JAK-09](jakub.md#jak-09-ja4-watchlist-rule) · **Kind:** code, tested

**Issue labels:** `type:task` `phase:spring` `owner:jaiden` `area:release`

#### Goal

Deliver rule and intel updates (Suricata rules, the JA4 watchlist, mapping updates) on a USB stick as a signed bundle that MaxGuard verifies before it unpacks anything.

#### Prerequisites

JAI-08 (signing) and JAK-09 (the watchlist) are merged.

#### Steps

**Step 1.** Update `main` and create your branch for this task (one branch per task):

```bash
cd ~/projects/maxguard
source .venv/bin/activate
git checkout main && git pull
git checkout -b jaiden/intel-bundles
```

If `source .venv/bin/activate` fails, you have not made the virtual environment yet: do Week 0 section 0.11 first.

**Step 2.** Create `maxguard/intel/bundle.py`:

```python
"""Signed offline intel bundles (Jaiden, JAI-11).

Rule and intel updates (Suricata rules, the JA4 watchlist, mapping files) reach
an offline MaxGuard on a USB stick, as one .tar.gz "bundle":

    manifest.json                 version, created_by, and every file with its SHA-256 and size
    manifest.sig                  Ed25519 signature (64 bytes) over manifest.json's exact bytes
    rules/<name>.rules            Suricata rules
    intel/ja4_watchlist.yaml      the JA4 watchlist
    mappings/<name>.yaml          mapping files

An update channel is a favorite attack path: whoever can change the rules can
blind the sensor. So a bundle is checked in this order, and nothing is written
to disk until every check has passed:
1. the archive's member list: only regular files, no duplicates, sane sizes;
2. the signature over manifest.json, with the public key the user installed;
3. the member list against the manifest: same files, only allowed paths
   (this also refuses absolute paths, "..", links and devices);
4. every file's size and SHA-256 against the manifest.
Installing then extracts into a new folder, checks the hashes again on disk,
and switches the "current" link to it in one step (os.replace), keeping the
previous version for rollback. An older version is refused, so a stolen old
bundle cannot roll the rules back (a "rollback attack").

Command line:
    python -m maxguard.intel.bundle build SRC_DIR OUT.tar.gz PRIVATE_KEY --version 2027.03.01
    python -m maxguard.intel.bundle verify BUNDLE PUBLIC_KEY
    python -m maxguard.intel.bundle install BUNDLE PUBLIC_KEY DEST_DIR
    python -m maxguard.intel.bundle rollback DEST_DIR
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import os
import re
import shutil
import sys
import tarfile
import tempfile
from pathlib import Path

from maxguard import __version__
from maxguard.custody.signing import sign, verify

MANIFEST = "manifest.json"
SIGNATURE = "manifest.sig"
SIGNATURE_BYTES = 64          # an Ed25519 signature is always 64 bytes
MAX_MANIFEST_BYTES = 1 << 20  # 1 MiB
MAX_MEMBERS = 1000
MAX_TOTAL_BYTES = 1 << 30     # 1 GiB unpacked: refuse "archive bombs"

NAME = r"[A-Za-z0-9][A-Za-z0-9._-]*"
ALLOWED_PATHS = (
    re.compile(rf"rules/{NAME}\.rules"),
    re.compile(r"intel/ja4_watchlist\.yaml"),
    re.compile(rf"mappings/{NAME}\.yaml"),
)
VERSION_PATTERN = re.compile(r"\d{1,6}(\.\d{1,6}){0,3}")  # 2027.03.01 or 2027.03.01.2
SHA256_PATTERN = re.compile(r"[0-9a-f]{64}")

VERSIONS_DIR = "versions"
CURRENT = "current"
PREVIOUS = "previous"


class BundleError(ValueError):
    """The bundle is not safe to install. Nothing was written."""


# ---------- building (on the maintainer's machine, which has the private key) ----------

def build_bundle(src_dir: Path, out_path: Path, private_key_path: Path, *, version: str) -> dict:
    """Write a signed bundle of every file under src_dir and return its manifest.

    The same files and version always give the same bundle bytes (fixed times and
    owners, sorted names), so anyone can rebuild it and compare."""
    check_version(version)
    files = collect_files(Path(src_dir))
    manifest = {
        "version": version,
        "created_by": f"maxguard {__version__}",
        "files": [{"path": path, "sha256": hashlib.sha256(data).hexdigest(), "size": len(data)}
                  for path, data in files],
    }
    manifest_bytes = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8")
    signature = sign(manifest_bytes, private_key_path)
    members = [(MANIFEST, manifest_bytes), (SIGNATURE, signature), *files]
    write_tar_gz(Path(out_path), members)
    return manifest


def collect_files(src_dir: Path) -> list[tuple[str, bytes]]:
    """(path inside the bundle, content) for every file, sorted; refuses anything not allowed."""
    files = []
    for path in sorted(src_dir.rglob("*")):
        relative = path.relative_to(src_dir).as_posix()
        if path.is_symlink():
            raise BundleError(f"{relative}: links are not allowed in a bundle")
        if path.is_dir():
            continue
        if not is_allowed(relative):
            raise BundleError(f"{relative}: not an allowed bundle file "
                              "(rules/*.rules, intel/ja4_watchlist.yaml, mappings/*.yaml)")
        files.append((relative, path.read_bytes()))
    if not files:
        raise BundleError(f"{src_dir}: no files to bundle")
    return files


def write_tar_gz(out_path: Path, members: list[tuple[str, bytes]]) -> None:
    """A .tar.gz with fixed times and owners, so the same input gives the same bytes."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("wb") as raw, \
            gzip.GzipFile(filename="", fileobj=raw, mode="wb", mtime=0) as packed, \
            tarfile.open(fileobj=packed, mode="w", format=tarfile.USTAR_FORMAT) as tar:
        for name, data in members:
            info = tarfile.TarInfo(name)
            info.size = len(data)
            info.mode = 0o644
            info.mtime = 0
            tar.addfile(info, io.BytesIO(data))


# ---------- checking (on the user's machine, which has only the public key) ----------

def verify_bundle(path: Path, public_key_path: Path) -> dict:
    """Run every check without writing anything; return the verified manifest."""
    with tarfile.open(path, mode="r:gz") as tar:
        members = list_members(tar)
        manifest_bytes = read_member(tar, members, MANIFEST, MAX_MANIFEST_BYTES)
        signature = read_member(tar, members, SIGNATURE, SIGNATURE_BYTES)
        if not verify(manifest_bytes, signature, public_key_path):
            raise BundleError("bad signature: the manifest was changed, or this is the wrong key")
        manifest = parse_manifest(manifest_bytes)
        check_member_list(members, manifest)
        for entry in manifest["files"]:
            check_content(tar.extractfile(members[entry["path"]]), entry)
    return manifest


def list_members(tar: tarfile.TarFile) -> dict[str, tarfile.TarInfo]:
    """Name -> member. Reads only the headers, and stops early on an archive bomb."""
    members: dict[str, tarfile.TarInfo] = {}
    total = 0
    for member in tar:
        if member.name in members:
            raise BundleError(f"{member.name}: appears twice in the archive")
        if not member.isreg():
            raise BundleError(f"{member.name}: only regular files are allowed "
                              "(no folders, links or devices)")
        total += member.size
        if len(members) >= MAX_MEMBERS or total > MAX_TOTAL_BYTES:
            raise BundleError("archive too large")
        members[member.name] = member
    return members


def read_member(tar: tarfile.TarFile, members: dict, name: str, max_bytes: int) -> bytes:
    member = members.get(name)
    if member is None:
        raise BundleError(f"{name} is missing")
    if member.size > max_bytes:
        raise BundleError(f"{name} is too large")
    return tar.extractfile(member).read()  # into memory: nothing touches the disk


def parse_manifest(data: bytes) -> dict:
    try:
        manifest = json.loads(data)
        version, files = manifest["version"], manifest["files"]
        well_formed = all(isinstance(entry["path"], str) and isinstance(entry["size"], int)
                          and isinstance(entry["sha256"], str)
                          and SHA256_PATTERN.fullmatch(entry["sha256"]) for entry in files)
    except (ValueError, KeyError, TypeError) as err:
        raise BundleError(f"manifest.json is malformed: {err!r}") from None
    if not well_formed:
        raise BundleError("manifest.json: every file needs a path, a size and a sha256")
    check_version(version)
    paths = [entry["path"] for entry in files]
    if len(set(paths)) != len(paths):
        raise BundleError("manifest.json lists a file twice")
    return manifest


def check_member_list(members: dict[str, tarfile.TarInfo], manifest: dict) -> None:
    listed = {entry["path"] for entry in manifest["files"]}
    present = set(members) - {MANIFEST, SIGNATURE}
    for name in sorted(present | listed):
        if not is_allowed(name):
            raise BundleError(f"{name}: not an allowed bundle path")
    if present - listed:
        raise BundleError(f"files not in the manifest: {sorted(present - listed)}")
    if listed - present:
        raise BundleError(f"files missing from the archive: {sorted(listed - present)}")


def check_content(stream, entry: dict) -> None:
    """Size and SHA-256 of one file's content against its manifest entry."""
    digest = hashlib.sha256()
    size = 0
    for block in iter(lambda: stream.read(1 << 20), b""):
        digest.update(block)
        size += len(block)
    if size != entry["size"] or digest.hexdigest() != entry["sha256"]:
        raise BundleError(f"{entry['path']}: content does not match the manifest")


def is_allowed(path: str) -> bool:
    return any(pattern.fullmatch(path) for pattern in ALLOWED_PATHS)


def check_version(version) -> None:
    if not isinstance(version, str) or not VERSION_PATTERN.fullmatch(version):
        raise BundleError(f"version must look like 2027.03.01, got {version!r}")


def version_key(version: str) -> tuple[int, ...]:
    """'2027.03.01' -> (2027, 3, 1), so versions compare as numbers, not text."""
    return tuple(int(part) for part in version.split("."))


# ---------- installing ----------

def install_bundle(path: Path, public_key_path: Path, dest_dir: Path) -> dict:
    """Verify, then install as dest_dir/versions/<version> and point dest_dir/current at it.

    dest_dir/previous keeps the version before, for rollback(). Returns the manifest."""
    manifest = verify_bundle(path, public_key_path)
    dest_dir = Path(dest_dir)
    current = installed_version(dest_dir)
    if current is not None and version_key(manifest["version"]) <= version_key(current):
        raise BundleError(f"version {manifest['version']} is not newer than the installed "
                          f"{current}; use rollback to go back")
    versions = dest_dir / VERSIONS_DIR
    versions.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=".incoming-", dir=versions))
    try:
        extract_checked(path, manifest, staging)
        target = versions / manifest["version"]
        if target.exists():  # left from before a rollback: replace it with the checked copy
            shutil.rmtree(target)
        os.replace(staging, target)  # one step: the folder appears complete or not at all
    except BaseException:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    if current is not None:
        point_link(dest_dir / PREVIOUS, Path(VERSIONS_DIR) / current)
    point_link(dest_dir / CURRENT, Path(VERSIONS_DIR) / manifest["version"])
    remove_unused_versions(dest_dir)
    return manifest


def extract_checked(path: Path, manifest: dict, staging: Path) -> None:
    """Extract the listed files, then check their hashes again on disk: the bundle
    file could have been swapped between verify_bundle() and this read."""
    names = {entry["path"] for entry in manifest["files"]} | {MANIFEST}
    with tarfile.open(path, mode="r:gz") as tar:
        members = [member for member in tar.getmembers() if member.name in names]
        # "data" refuses absolute paths, "..", links and devices a second time.
        tar.extractall(staging, members=members, filter="data")
    for entry in manifest["files"]:
        with (staging / entry["path"]).open("rb") as f:
            check_content(f, entry)
    on_disk = parse_manifest((staging / MANIFEST).read_bytes())
    if on_disk != manifest:
        raise BundleError("manifest.json changed while installing")


def point_link(link: Path, target: Path) -> None:
    """Make link point at target (relative), replacing any old link in one step."""
    temporary = link.with_name(f".{link.name}.new")
    temporary.unlink(missing_ok=True)
    temporary.symlink_to(target, target_is_directory=True)
    os.replace(temporary, link)  # atomic on POSIX: readers see the old or the new link


def installed_version(dest_dir: Path, link: str = CURRENT) -> str | None:
    path = Path(dest_dir) / link
    return os.readlink(path).rsplit("/", 1)[-1] if path.is_symlink() else None


def remove_unused_versions(dest_dir: Path) -> None:
    keep = {installed_version(dest_dir, CURRENT), installed_version(dest_dir, PREVIOUS)}
    for folder in (Path(dest_dir) / VERSIONS_DIR).iterdir():
        if folder.name not in keep and not folder.name.startswith(".incoming-"):
            shutil.rmtree(folder)


def rollback(dest_dir: Path) -> str:
    """Switch current and previous. Returns the version that is now current."""
    current = installed_version(dest_dir, CURRENT)
    previous = installed_version(dest_dir, PREVIOUS)
    if current is None or previous is None:
        raise BundleError("nothing to roll back to")
    point_link(Path(dest_dir) / CURRENT, Path(VERSIONS_DIR) / previous)
    point_link(Path(dest_dir) / PREVIOUS, Path(VERSIONS_DIR) / current)
    return previous


# ---------- command line ----------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m maxguard.intel.bundle",
                                     description="Build, check and install signed intel bundles.")
    commands = parser.add_subparsers(dest="command", required=True)
    build = commands.add_parser("build", help="sign a folder into a bundle")
    build.add_argument("src_dir", type=Path)
    build.add_argument("out", type=Path)
    build.add_argument("private_key", type=Path)
    build.add_argument("--version", required=True)
    check = commands.add_parser("verify", help="check a bundle without installing it")
    check.add_argument("bundle", type=Path)
    check.add_argument("public_key", type=Path)
    install = commands.add_parser("install", help="check and install a bundle")
    install.add_argument("bundle", type=Path)
    install.add_argument("public_key", type=Path)
    install.add_argument("dest_dir", type=Path)
    back = commands.add_parser("rollback", help="go back to the previous version")
    back.add_argument("dest_dir", type=Path)
    args = parser.parse_args(argv)

    try:
        if args.command == "build":
            manifest = build_bundle(args.src_dir, args.out, args.private_key, version=args.version)
            print(f"built {args.out}: version {manifest['version']}, "
                  f"{len(manifest['files'])} files")
        elif args.command == "verify":
            manifest = verify_bundle(args.bundle, args.public_key)
            print(f"ok: version {manifest['version']}, {len(manifest['files'])} files")
        elif args.command == "install":
            manifest = install_bundle(args.bundle, args.public_key, args.dest_dir)
            print(f"installed version {manifest['version']}")
        else:
            print(f"current version is now {rollback(args.dest_dir)}")
    except (BundleError, tarfile.TarError, OSError) as err:
        print(f"refused: {err}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

The order of the checks in `verify_bundle()` is the point of this task: the member list is read from the headers only, the signature is checked before anything in the manifest is trusted, and every file is hashed from memory. Nothing touches the disk until all of that passed. `install_bundle()` then extracts into a new folder, checks the hashes again on disk (the USB stick could change between the two reads), and switches the `current` link in one step. A version that is not newer is refused, so an old signed bundle cannot be replayed to roll the rules back; `rollback` is the deliberate way back.

**Step 3.** Create the tests `tests/unit/test_intel_bundle.py`. Some bad bundles are signed with the **right** key: the path and member checks must hold even if the machine that builds bundles is compromised:

```python
"""Tests for signed offline intel bundles (Jaiden, JAI-11).

Every bad bundle must be refused before anything is written to the install folder.
Some bad bundles below are signed with the RIGHT key: the path and member checks
must hold even if the machine that builds bundles is compromised.
"""

from __future__ import annotations

import gzip
import hashlib
import io
import json
import tarfile
from pathlib import Path

import pytest

from maxguard.custody.signing import generate_keypair, sign
from maxguard.intel import bundle

RULES = b'alert tcp any any -> any 23 (msg:"MaxGuard test"; sid:9000001; rev:1;)\n'
WATCHLIST = b"[]\n"
MAPPING = b"framework: NIST SP 800-53\n"


@pytest.fixture
def keys(tmp_path) -> tuple[Path, Path]:
    return generate_keypair(tmp_path / "keys")


@pytest.fixture
def src(tmp_path) -> Path:
    """A folder laid out like a bundle: rules/, intel/, mappings/."""
    folder = tmp_path / "src"
    for relative, data in (("rules/maxguard-extra.rules", RULES),
                           ("intel/ja4_watchlist.yaml", WATCHLIST),
                           ("mappings/nist_800_53_r5.yaml", MAPPING)):
        (folder / relative).parent.mkdir(parents=True, exist_ok=True)
        (folder / relative).write_bytes(data)
    return folder


@pytest.fixture
def good(tmp_path, src, keys) -> Path:
    path = tmp_path / "intel-2027.03.01.tar.gz"
    bundle.build_bundle(src, path, keys[0], version="2027.03.01")
    return path


def craft(path: Path, members: list[tuple[str, bytes]], private_key: Path | None,
          manifest_files: list[tuple[str, bytes]] | None = None, version="2027.03.01",
          extra: list[tarfile.TarInfo] = ()) -> Path:
    """Write a bundle by hand, the way an attacker could, signed with private_key."""
    listed = members if manifest_files is None else manifest_files
    manifest = {"version": version, "created_by": "test", "files": [
        {"path": name, "sha256": hashlib.sha256(data).hexdigest(), "size": len(data)}
        for name, data in listed]}
    manifest_bytes = json.dumps(manifest).encode()
    signature = sign(manifest_bytes, private_key) if private_key else b"\0" * 64
    with tarfile.open(path, "w:gz") as tar:
        for name, data in [("manifest.json", manifest_bytes), ("manifest.sig", signature),
                           *members]:
            info = tarfile.TarInfo(name)
            info.size = len(data)
            tar.addfile(info, io.BytesIO(data))
        for info in extra:
            tar.addfile(info)
    return path


def rewrite_member(source: Path, target: Path, name: str, new_data: bytes) -> Path:
    """Copy a bundle, replacing one member's content (the header size follows)."""
    with tarfile.open(source, "r:gz") as old, tarfile.open(target, "w:gz") as new:
        for member in old:
            data = old.extractfile(member).read()
            if member.name == name:
                data = new_data
                member.size = len(data)
            new.addfile(member, io.BytesIO(data))
    return target


def assert_refused(path: Path, keys, dest: Path, match: str) -> None:
    with pytest.raises(bundle.BundleError, match=match):
        bundle.install_bundle(path, keys[1], dest)
    assert not dest.exists() or list(dest.iterdir()) == []  # nothing was written


# ---------- good bundles ----------

def test_a_good_bundle_verifies(good, keys):
    manifest = bundle.verify_bundle(good, keys[1])
    assert manifest["version"] == "2027.03.01"
    assert [entry["path"] for entry in manifest["files"]] == [
        "intel/ja4_watchlist.yaml", "mappings/nist_800_53_r5.yaml",
        "rules/maxguard-extra.rules"]


def test_a_good_bundle_installs(good, keys, tmp_path):
    dest = tmp_path / "intel"
    bundle.install_bundle(good, keys[1], dest)
    current = dest / "current"
    assert current.is_symlink()
    assert (current / "rules" / "maxguard-extra.rules").read_bytes() == RULES
    assert (current / "intel" / "ja4_watchlist.yaml").read_bytes() == WATCHLIST
    assert json.loads((current / "manifest.json").read_text())["version"] == "2027.03.01"
    assert bundle.installed_version(dest) == "2027.03.01"


def test_the_same_files_give_the_same_bundle_bytes(src, keys, tmp_path):
    a = tmp_path / "a.tar.gz"
    b = tmp_path / "b.tar.gz"
    bundle.build_bundle(src, a, keys[0], version="2027.03.01")
    bundle.build_bundle(src, b, keys[0], version="2027.03.01")
    assert a.read_bytes() == b.read_bytes()


def test_a_newer_version_keeps_the_previous_one_for_rollback(good, src, keys, tmp_path):
    dest = tmp_path / "intel"
    bundle.install_bundle(good, keys[1], dest)
    (src / "rules" / "maxguard-extra.rules").write_bytes(RULES + b"# v2\n")
    newer = tmp_path / "intel-2027.04.01.tar.gz"
    bundle.build_bundle(src, newer, keys[0], version="2027.04.01")
    bundle.install_bundle(newer, keys[1], dest)
    assert bundle.installed_version(dest) == "2027.04.01"
    assert bundle.installed_version(dest, "previous") == "2027.03.01"

    assert bundle.rollback(dest) == "2027.03.01"
    assert (dest / "current" / "rules" / "maxguard-extra.rules").read_bytes() == RULES


def test_an_older_or_equal_version_is_refused(good, src, keys, tmp_path):
    dest = tmp_path / "intel"
    bundle.install_bundle(good, keys[1], dest)
    with pytest.raises(bundle.BundleError, match="not newer"):
        bundle.install_bundle(good, keys[1], dest)
    older = tmp_path / "old.tar.gz"
    bundle.build_bundle(src, older, keys[0], version="2027.02.28")
    with pytest.raises(bundle.BundleError, match="not newer"):
        bundle.install_bundle(older, keys[1], dest)
    assert bundle.installed_version(dest) == "2027.03.01"


def test_versions_compare_as_numbers():
    assert bundle.version_key("2027.10.01") > bundle.version_key("2027.9.30")


# ---------- refused bundles ----------

def test_a_changed_file_is_refused(good, keys, tmp_path):
    changed = rewrite_member(good, tmp_path / "changed.tar.gz", "rules/maxguard-extra.rules",
                             RULES.replace(b"23", b"24"))
    assert_refused(changed, keys, tmp_path / "intel", "does not match the manifest")


def test_a_changed_manifest_is_refused(good, keys, tmp_path):
    with tarfile.open(good, "r:gz") as tar:
        manifest = json.loads(tar.extractfile("manifest.json").read())
    manifest["version"] = "2099.01.01"
    changed = rewrite_member(good, tmp_path / "changed.tar.gz", "manifest.json",
                             json.dumps(manifest).encode())
    assert_refused(changed, keys, tmp_path / "intel", "bad signature")


def test_the_wrong_key_is_refused(good, tmp_path):
    other = generate_keypair(tmp_path / "other-keys")
    assert_refused(good, other, tmp_path / "intel", "bad signature")


@pytest.mark.parametrize("name", ["../evil.rules", "/etc/evil.rules", "rules/../../evil.rules",
                                  "scripts/run.sh", "rules/sub/deeper.rules"])
def test_a_bad_path_is_refused_even_when_signed(name, keys, tmp_path):
    path = craft(tmp_path / "bad.tar.gz", [(name, RULES)], keys[0])
    assert_refused(path, keys, tmp_path / "intel", "not an allowed bundle path")


def test_an_extra_file_is_refused(keys, tmp_path):
    path = craft(tmp_path / "extra.tar.gz",
                 [("rules/a.rules", RULES), ("rules/b.rules", RULES)], keys[0],
                 manifest_files=[("rules/a.rules", RULES)])
    assert_refused(path, keys, tmp_path / "intel", "not in the manifest")


def test_a_link_is_refused(keys, tmp_path):
    link = tarfile.TarInfo("rules/link.rules")
    link.type = tarfile.SYMTYPE
    link.linkname = "/etc/passwd"
    path = craft(tmp_path / "link.tar.gz", [("rules/a.rules", RULES)], keys[0], extra=[link])
    assert_refused(path, keys, tmp_path / "intel", "only regular files")


def test_a_duplicate_member_is_refused(keys, tmp_path):
    path = craft(tmp_path / "dup.tar.gz", [("rules/a.rules", RULES), ("rules/a.rules", b"x")],
                 keys[0], manifest_files=[("rules/a.rules", RULES)])
    assert_refused(path, keys, tmp_path / "intel", "appears twice")


def test_an_unsigned_bundle_is_refused(keys, tmp_path):
    path = craft(tmp_path / "unsigned.tar.gz", [("rules/a.rules", RULES)], private_key=None)
    assert_refused(path, keys, tmp_path / "intel", "bad signature")


def test_a_bad_version_is_refused(keys, tmp_path):
    path = craft(tmp_path / "v.tar.gz", [("rules/a.rules", RULES)], keys[0], version="../x")
    assert_refused(path, keys, tmp_path / "intel", "version must look like")


def test_build_refuses_files_that_are_not_allowed(src, keys, tmp_path):
    (src / "notes.txt").write_text("not intel")
    with pytest.raises(bundle.BundleError, match="not an allowed bundle file"):
        bundle.build_bundle(src, tmp_path / "x.tar.gz", keys[0], version="2027.03.01")


def test_not_a_gzip_file_is_refused(keys, tmp_path):
    path = tmp_path / "junk.tar.gz"
    path.write_bytes(gzip.compress(b"not a tar archive"))
    with pytest.raises(tarfile.TarError):
        bundle.verify_bundle(path, keys[1])


# ---------- command line ----------

def test_command_line(src, keys, tmp_path, capsys):
    out = tmp_path / "cli.tar.gz"
    dest = tmp_path / "intel"
    assert bundle.main(["build", str(src), str(out), str(keys[0]),
                        "--version", "2027.03.01"]) == 0
    assert bundle.main(["verify", str(out), str(keys[1])]) == 0
    assert bundle.main(["install", str(out), str(keys[1]), str(dest)]) == 0
    assert bundle.main(["install", str(out), str(keys[1]), str(dest)]) == 1
    printed = capsys.readouterr()
    assert "ok: version 2027.03.01, 3 files" in printed.out
    assert "installed version 2027.03.01" in printed.out
    assert "refused: version 2027.03.01 is not newer" in printed.err
```

**Step 4.** Run them:

```bash
pytest tests/unit/test_intel_bundle.py -q
```

Expected output:

```text
......................                                                                       [100%]
22 passed in 0.24s
```

**Step 5.** Try it end to end with a throwaway key pair (JAI-08's helper names the files `custody_ed25519_*.pem`; the real bundle key stays on the maintainer's machine, and only its public key ships with MaxGuard):

```bash
mkdir -p data/bundle-src/rules data/bundle-src/intel
cp maxguard/suricata/rules/maxguard.rules data/bundle-src/rules/
cp maxguard/intel/ja4_watchlist.yaml data/bundle-src/intel/
python -c "from pathlib import Path; from maxguard.custody.signing import generate_keypair; generate_keypair(Path('data/bundle-keys'))"
python -m maxguard.intel.bundle build data/bundle-src data/intel-2027.03.01.tar.gz data/bundle-keys/custody_ed25519_private.pem --version 2027.03.01
python -m maxguard.intel.bundle verify data/intel-2027.03.01.tar.gz data/bundle-keys/custody_ed25519_public.pem
python -m maxguard.intel.bundle install data/intel-2027.03.01.tar.gz data/bundle-keys/custody_ed25519_public.pem data/intel
python -c "import os; print('current ->', os.readlink('data/intel/current'))"
python -m maxguard.intel.bundle install data/intel-2027.03.01.tar.gz data/bundle-keys/custody_ed25519_public.pem data/intel
```

Expected output:

```text
built data/intel-2027.03.01.tar.gz: version 2027.03.01, 2 files
ok: version 2027.03.01, 2 files
installed version 2027.03.01
current -> versions/2027.03.01
refused: version 2027.03.01 is not newer than the installed 2027.03.01; use rollback to go back
```

*The last command exits with 1: the same version is never installed twice. `install` uses symbolic links: on Windows run it in WSL, or turn on Developer Mode, which lets normal users create them.*

**Step 6.** Commit, push, and open the pull request:

```bash
git add -A
git status          # only this task's files: nothing from .venv/, data/ or lab/captures/
git commit -m "feat: signed offline intel bundles (JAI-11)"
git push -u origin HEAD
```

`HEAD` means "the branch I am on", so you do not have to retype its name. Open the repository on github.com: a yellow bar shows your branch with a **Compare & pull request** button. Click it, keep the title `feat: signed offline intel bundles (JAI-11)`, fill in the template (paste the real output of the commands above under **How I tested it**), write `Closes #<issue number>` (this task's issue), and pick **@ahmadalkhoudeir** under **Reviewers**. Click **Create pull request**, then fix anything CI or the reviewer finds with new commits on the same branch.

#### How to test

Every tamper case is refused before anything is written.

#### What you just did and why

An update channel is a favorite attack path: whoever can change the rules can blind the sensor. Verifying the signature first, and refusing anything unexpected, means a tampered USB stick changes nothing. USB delivery keeps MaxGuard offline (CLAUDE.md rule 1).

#### Pull request checklist

- [ ] `ruff check .` prints `All checks passed!`
- [ ] `pytest -m "not integration" -q` passes on your laptop
- [ ] The pull request title has the form `type: summary (TASK-ID)` and the body says `Closes #<issue number>`
- [ ] No secrets, passwords, email addresses, personal data, or captures from a real network (CLAUDE.md rule 6)
- [ ] Any new dependency has a row in `docs/DEPENDENCIES.md` with its license
- [ ] CI is green and your reviewer approved
- [ ] Private keys are never in the repository

### JAI-12: Release v2.0-rc1 and v2.0

**Due:** Spring S13 (due Fri Apr 30, 2027) · **Milestone:** `S13 v2.0 release candidate` · **Needs first:** [JAI-11](#jai-11-signed-offline-intel-bundles), [JAK-07](jakub.md#jak-07-live-sensor-capture-rotation-and-shipping-to-the-console), [AHM-08](ahmad.md#ahm-08-response-approvals-audit-revert-and-the-opnsense-connector) · **Kind:** process

**Issue labels:** `type:task` `phase:spring` `owner:jaiden` `area:release` `critical-path`

#### Goal

Tag `v2.0-rc1` for an outside tester (April 30, 2027), fix what they find, and release `v2.0` (May 7, 2027) with the sensor image and the offline bundle.

#### Prerequisites

All spring features are merged (feature freeze April 23, 2027).

#### Steps

**Step 1.** Re-check that every framework version in `docs/PROJECT_DECISIONS.md` section 8 is still the current published version (CLAUDE.md rule 8) and that the pinned tools have no unfixed security advisories.

**Step 2.** Tag `v2.0-rc1`, hand it to the tester with Karthik, fix, then tag `v2.0` and run the v2.0 acceptance test with Ahmad (AHM-09).

#### How to test

The v2.0 acceptance test passes.

#### What you just did and why

Same process as the alpha, plus the version checks the compliance rows depend on.

#### Pull request checklist

- [ ] Framework versions re-checked
- [ ] Release notes written
