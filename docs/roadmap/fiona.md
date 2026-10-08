# Fiona: Detection Engine Lead

**Fiona Lau** (@flau0306) · Module: Engine · Reviewer for your pull requests: @JWinborne1 (Jaiden) · Ask first when stuck: Jaiden

This is your part of the MaxGuard v2.0 roadmap. Read [the roadmap overview](README.md) once, then work top to bottom: Week 0 first, then your tasks in order. Each task's ID is also the start of its GitHub issue's title.

## Your tasks

| Task | Due | Title | Needs first | Kind |
|---|---|---|---|---|
| [FIO-00](#week-0--onboarding-due-friday-october-9-2026) | W0 | Week 0 onboarding (Fiona) | — | process |
| [FIO-01](#fio-01-zeek-runner-and-the-two-input-adapters) | W1 | Zeek runner and the two input adapters | [JAI-02](jaiden.md#jai-02-merge-the-three-contracts-in-their-v20-form), [KAR-02](karthik.md#kar-02-test-fixtures-zeek-and-suricata-output-for-every-capture) | code, tested |
| [FIO-02](#fio-02-tls-and-certificate-rules) | W1 | TLS and certificate rules | [FIO-01](#fio-01-zeek-runner-and-the-two-input-adapters), [KAR-02](karthik.md#kar-02-test-fixtures-zeek-and-suricata-output-for-every-capture) | code, tested |
| [FIO-03](#fio-03-mitre-attck-mapping-file) | W2 | MITRE ATT&CK mapping file | [AMO-01](amory.md#amo-01-nist-sp-800-53-mapping-file-and-the-mapping-checks), [JAK-03](jakub.md#jak-03-cleartext-and-rdp-rules-the-rule-set-is-complete) | code, tested |
| [FIO-04](#fio-04-the-maxguard-command-first-version-json-reports) | W2 | The maxguard command, first version (JSON reports) | [JAI-05](jaiden.md#jai-05-the-pipeline-one-function-from-input-to-report), [FIO-03](#fio-03-mitre-attck-mapping-file) | code, tested |
| [FIO-05](#fio-05-cli-csv-and-html-reports-and---offline) | W4 | CLI: CSV and HTML reports, and --offline | [FIO-04](#fio-04-the-maxguard-command-first-version-json-reports), [AMO-03](amory.md#amo-03-report-export-json-csv-and-html), [JON-03](jonattan.md#jon-03-offline-guard-make-accidental-network-access-fail-loudly) | code, tested |
| [FIO-06](#fio-06-decoys-fake-services-on-their-own-ip-address) | S11 | Decoys: fake services on their own IP address | [JAI-07](jaiden.md#jai-07-the-api-uploads-alerts-events-live-updates-sensor-ingest), [JON-04](jonattan.md#jon-04-home-mode-text-for-every-rule) | code, tested |
| [FIO-07](#fio-07-per-device-baselines) | S11 | Per-device baselines | [JAI-06](jaiden.md#jai-06-storage-alerts-in-sqlite-events-in-hourly-parquet-files), [JAK-08](jakub.md#jak-08-device-attribution-which-device-is-behind-each-ip-address) | code, tested |

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
git config --global user.name "Fiona Lau"
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

Your row is already in `docs/TEAM.md`, but the file has no table header, so GitHub does not show it as a table. You will add the header. Every task in this roadmap uses the same six steps, so learn them now.

1. **Start from an up-to-date `main` and make a branch** named `<yourname>/<short-task>`:

```bash
cd ~/projects/maxguard
git checkout main && git pull
git checkout -b fiona/week0-team-header
```

2. **Make the change.** Run `code .`, open `docs/TEAM.md`, and add these two
   lines at the very top (keep the `|` characters):

```markdown
| Name | Role | GitHub | Module |
|---|---|---|---|
```

3. **Commit** (the message says *what changed*, starting with a type such as
   `docs:`, `feat:`, `fix:` or `test:`; see `docs/CONTRIBUTING.md`):

```bash
git add docs/TEAM.md
git commit -m "docs: add a table header to TEAM.md"
```

4. **Push** your branch to GitHub:

```bash
git push -u origin fiona/week0-team-header
```

Expected (from the planning simulation; the first lines differ on GitHub):

```text
 * [new branch]      fiona/week0-team-header -> fiona/week0-team-header
branch 'fiona/week0-team-header' set up to track 'origin/fiona/week0-team-header'.
```

5. **Open the pull request** and ask for a review:

```bash
gh pr create --base main --title "docs: add a table header to TEAM.md" --body "Week 0 onboarding." --reviewer JWinborne1
```

`gh` prints the pull request's web address. (You can also click the link Git
printed after the push and press **Create pull request**.)

6. **After approval**, click **Squash and merge** on GitHub, then update your laptop:

```bash
git checkout main && git pull
git branch -d fiona/week0-team-header
```

**If GitHub says "This branch has conflicts":** eight people are adding a line
to the same file this week, so this is expected. Bring `main` into your branch
and keep both lines:

```bash
git checkout main && git pull
git checkout fiona/week0-team-header
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
   `FIO-01: pytest cannot import maxguard`). In the body, paste the
   **exact command** you ran, the **exact output** (in a code block), and what you
   expected. Tag your help person. Never paste passwords, tokens, or captures
   from a real network.

**Why Discussions and not only Teams:** an answer in Discussions can be found
again by the next person with the same problem; a Teams chat scrolls away.

### 0.11 Set up MaxGuard's Python environment (as soon as JAI-01 is merged)

JAI-01 adds `pyproject.toml`, the file that lists everything MaxGuard needs.
Once Jaiden announces it is merged (Discussions → Announcements), run this once
(Jaiden does it inside JAI-01):

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

### FIO-01: Zeek runner and the two input adapters

**Due:** Week 1 (due Fri Oct 16) · **Milestone:** `W1 Building blocks` · **Needs first:** [JAI-02](jaiden.md#jai-02-merge-the-three-contracts-in-their-v20-form), [KAR-02](karthik.md#kar-02-test-fixtures-zeek-and-suricata-output-for-every-capture) · **Kind:** code, tested

**Issue labels:** `type:task` `phase:alpha` `owner:fiona` `area:engine` `critical-path`

#### Goal

Write the code that turns what a user gives MaxGuard into a folder of Zeek logs: `run_zeek()` runs Zeek 9.0.0 on a capture, `PcapAdapter` accepts `.pcap`/`.pcapng` files, and `ZeekLogAdapter` accepts a folder, `.zip` or `.tar.gz` of logs that someone already has, including the old tab-separated (TSV) format. Both adapters follow Contract 3 (`maxguard/adapters/base.py`).

#### Prerequisites

JAI-02 (contracts) and KAR-02 (fixtures) are merged.

#### Steps

**Step 1.** Update `main` and create your branch for this task (one branch per task):

```bash
cd ~/projects/maxguard
source .venv/bin/activate
git checkout main && git pull
git checkout -b fiona/zeek-runner-adapters
```

If `source .venv/bin/activate` fails, you have not made the virtual environment yet: do Week 0 section 0.11 first.

**Step 2.** Create an **empty** file `maxguard/zeek/__init__.py`, then the runner `maxguard/zeek/runner.py`:

```python
"""Run Zeek on one capture file.

Fall 2026 roadmap runner with two v2.0 additions:
- `-D` (deterministic): Zeek normally picks random seeds, so connection uids
  change on every run. With -D the same capture always gives the same uids,
  which keeps finding evidence and AI citations stable (CLAUDE.md rule 2).
  Only use -D for capture files; a live sensor keeps random seeds.
- community-id logging: adds `community_id` to conn.log, the same value
  Suricata writes, so Zeek and Suricata records can be joined.
And one fix found in planning: Zeek's own "local" policy makes DNS lookups
(detect-MHR asks an outside service about file hashes), so MaxGuard loads its
own copy without them, site.zeek (CLAUDE.md rule 1).
"""

import subprocess
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent / "scripts"
SITE_POLICY = Path(__file__).parent / "site.zeek"  # Zeek's "local" without network lookups


class ZeekError(RuntimeError):
    pass


def run_zeek(pcap: Path, out_dir: Path, timeout: int = 1800) -> Path:
    """Run Zeek on one capture file and write JSON logs into out_dir."""
    out_dir.mkdir(parents=True, exist_ok=True)
    extra = sorted(str(p) for p in SCRIPTS_DIR.glob("*.zeek"))  # Jakub's scripts
    cmd = ["zeek", "-D", "-C", "-r", str(pcap.resolve()), str(SITE_POLICY),
           "LogAscii::use_json=T", "policy/protocols/conn/community-id-logging", *extra]
    try:
        res = subprocess.run(cmd, cwd=out_dir, capture_output=True,
                             text=True, timeout=timeout, check=False)
    except FileNotFoundError:
        raise ZeekError("zeek is not installed or not on PATH: run MaxGuard inside its "
                        "Docker image, or install Zeek 9.0.0") from None
    except subprocess.TimeoutExpired:
        raise ZeekError(f"Zeek took longer than {timeout} seconds; try a smaller capture") from None
    if res.returncode != 0:
        raise ZeekError(res.stderr.strip() or "zeek failed")
    if not (out_dir / "conn.log").exists():
        raise ZeekError("Zeek produced no conn.log: is this a valid capture?")
    return out_dir
```

`-D` makes Zeek's connection IDs (`uid`) the same on every run, and the Community ID script adds the `community_id` that Suricata also writes. `docs/ARCHITECTURE.md` section 7 explains why both matter. The runner loads `site.zeek` (JAK-01) where Zeek's documentation would say `local`.

**Step 3.** Create `tests/unit/test_zeek_site.py`. It fails if any MaxGuard `.zeek` file loads `local` or a script that makes DNS lookups, and checks that the runner passes `site.zeek` to Zeek:

```python
"""MaxGuard's Zeek site policy makes no network lookups (Jakub, JAK-01).

Zeek's own "local" policy loads scripts that send DNS queries (CLAUDE.md rule 1).
Zeek runs as its own program, so the Python offline guard cannot catch them:
these tests make sure no MaxGuard Zeek file loads them, and that the runner
uses site.zeek instead of "local".
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from maxguard.zeek import runner

ZEEK_DIR = Path(runner.__file__).parent
NETWORK_SCRIPTS = (
    "frameworks/files/detect-MHR",              # DNS query per downloaded file's hash
    "protocols/ssh/interesting-hostnames",      # reverse DNS on SSH logins
    "frameworks/notice/extend-email/hostnames",  # reverse DNS for notice e-mails
)


def loaded(path: Path) -> list[str]:
    """The scripts a .zeek file loads with @load."""
    return [line.split()[1] for line in path.read_text().splitlines()
            if line.startswith("@load ")]


def test_no_maxguard_zeek_file_loads_a_script_that_uses_the_network():
    for path in sorted(ZEEK_DIR.rglob("*.zeek")):
        for script in loaded(path):
            assert not script.endswith(NETWORK_SCRIPTS), f"{path.name} loads {script}"
            assert script not in ("local", "site/local"), f"{path.name} loads Zeek's local"


def test_site_policy_keeps_the_logs_maxguard_reads():
    scripts = loaded(runner.SITE_POLICY)
    for needed in ("protocols/conn/known-hosts", "protocols/conn/known-services",
                   "protocols/ssl/validate-certs", "frameworks/files/hash-all-files"):
        assert needed in scripts


def test_runner_loads_site_zeek_not_local(monkeypatch, tmp_path):
    seen = {}

    def fake_run(cmd, **kwargs):
        seen["cmd"] = cmd
        (tmp_path / "conn.log").write_text("")
        return subprocess.CompletedProcess(cmd, 0, "", "")

    monkeypatch.setattr(runner.subprocess, "run", fake_run)
    runner.run_zeek(tmp_path / "x.pcap", tmp_path)
    assert str(runner.SITE_POLICY) in seen["cmd"]
    assert "local" not in seen["cmd"]
```

**Step 4.** Create `maxguard/adapters/pcap.py`:

```python
"""PcapAdapter: a .pcap or .pcapng file -> Zeek logs."""

from pathlib import Path

from maxguard.zeek.runner import run_zeek

PCAP_MAGIC = {b"\xd4\xc3\xb2\xa1", b"\xa1\xb2\xc3\xd4",   # pcap
              b"\x4d\x3c\xb2\xa1", b"\xa1\xb2\x3c\x4d",   # pcap (ns)
              b"\x0a\x0d\x0d\x0a"}                       # pcapng


class PcapAdapter:
    name = "pcap"

    def accepts(self, path: Path) -> bool:
        if not path.is_file():
            return False
        with path.open("rb") as f:
            return f.read(4) in PCAP_MAGIC

    def to_zeek_logs(self, path: Path, workdir: Path) -> Path:
        return run_zeek(path, workdir / "zeek_logs")
```

It decides by the file's first four bytes (its *magic number*), not by its name, so a renamed text file is refused. JAK-05 adds Suricata to it in Week 4.

**Step 5.** Create `maxguard/adapters/zeeklogs.py`:

```python
"""ZeekLogAdapter: a folder, .zip, or .tar.gz of existing Zeek logs (JSON or TSV).

Fall 2026 roadmap adapter with v2.0 fixes found while testing with Zeek 9.0.0:
- TSV values are converted with the log's own `#types` header, so numbers become
  numbers and sets/vectors become lists. Before, a set like cert_chain_fps stayed
  one comma-separated string and every certificate rule silently found nothing.
- Suricata's eve.json is kept (it used to be dropped, so JA4 and Suricata
  events were lost for imported folders).
- Zeek's rotated, gzipped archives (conn.00:00:00-01:00:00.log.gz) are read, and
  logs of the same type are appended in sorted order instead of overwriting each
  other, so the result does not depend on folder order.
- Archives are checked before extracting, so a tiny "zip bomb" cannot fill the disk.
"""

from __future__ import annotations

import gzip
import json
import shutil
import tarfile
import zipfile
from pathlib import Path

MAX_EXTRACTED_BYTES = 4 * 1024**3  # 4 GiB: refuse archives that unpack to more


class ArchiveTooLarge(ValueError):
    pass


def _convert(value: str, zeek_type: str, set_sep: str, empty: str, unset: str):
    """Turn one TSV text value into the same JSON value Zeek would have written."""
    if value == unset:
        return None
    if zeek_type.startswith(("set[", "vector[")):
        if value == empty:
            return []
        inner = zeek_type[zeek_type.index("[") + 1 : -1]
        return [_convert(v, inner, set_sep, empty, unset) for v in value.split(set_sep)]
    if value == empty:
        return ""
    if zeek_type in ("count", "int", "port"):
        return int(value)
    if zeek_type in ("double", "time", "interval"):
        return float(value)
    if zeek_type == "bool":
        return value == "T"
    return value


def _tsv_to_json(fin, fout) -> None:
    """Convert one TSV log (an open text file) to JSON lines written to fout."""
    sep, set_sep, empty, unset = "\t", ",", "(empty)", "-"
    fields: list[str] = []
    types: list[str] = []
    for line in fin:
        line = line.rstrip("\n")
        if line.startswith("#set_separator"):
            set_sep = line.split(sep, 1)[1]
        elif line.startswith("#empty_field"):
            empty = line.split(sep, 1)[1]
        elif line.startswith("#unset_field"):
            unset = line.split(sep, 1)[1]
        elif line.startswith("#fields"):
            fields = line.split(sep)[1:]
        elif line.startswith("#types"):
            types = line.split(sep)[1:]
        elif line.startswith("#") or not line:
            continue
        elif fields:
            values = line.split(sep)
            kinds = types or ["string"] * len(fields)
            rec = {f: _convert(v, t, set_sep, empty, unset)
                   # strict=False: a line cut short (e.g. by a crash) keeps the fields it has
                   for f, v, t in zip(fields, values, kinds, strict=False)}
            fout.write(json.dumps(rec) + "\n")


def _open_text(path: Path):
    if path.name.endswith(".gz"):
        return gzip.open(path, "rt")
    return path.open()


def _log_name(path: Path) -> str:
    """'conn.00:00:00-01:00:00.log.gz' -> 'conn.log'; 'eve.json' stays 'eve.json'."""
    base = path.name.split(".")[0]
    return "eve.json" if base == "eve" else f"{base}.log"


def _check_size(sizes: list[int]) -> None:
    if sum(sizes) > MAX_EXTRACTED_BYTES:
        raise ArchiveTooLarge("archive unpacks to more than 4 GiB; split it into smaller parts")


def _extract(path: Path, dest: Path) -> None:
    if path.suffix == ".zip":
        with zipfile.ZipFile(path) as z:
            _check_size([i.file_size for i in z.infolist()])
            z.extractall(dest)  # zipfile drops absolute paths and ".." parts
    else:
        with tarfile.open(path) as t:
            _check_size([m.size for m in t.getmembers()])
            t.extractall(dest, filter="data")  # "data" blocks links, devices, "..", absolute


class ZeekLogAdapter:
    name = "zeek-logs"

    def accepts(self, path: Path) -> bool:
        return (path.is_dir() and (path / "conn.log").exists()) or \
               path.suffix == ".zip" or path.name.endswith(".tar.gz")

    def to_zeek_logs(self, path: Path, workdir: Path) -> Path:
        src = workdir / "imported"
        if path.is_dir():
            shutil.copytree(path, src, dirs_exist_ok=True)
        else:
            _extract(path, src)
        out = workdir / "zeek_logs"
        out.mkdir(parents=True, exist_ok=True)
        found = [p for p in src.rglob("*") if p.is_file() and (
            p.name.endswith((".log", ".log.gz")) or p.name.startswith("eve.json"))]
        for log in sorted(found):  # sorted: same result whatever order the disk lists files
            with _open_text(log) as fin, (out / _log_name(log)).open("a") as fout:
                first = fin.readline()
                if first.startswith("{"):  # JSON lines (Zeek JSON or Suricata eve.json)
                    fout.write(first if first.endswith("\n") else first + "\n")
                    shutil.copyfileobj(fin, fout)
                else:  # Zeek's default tab-separated format
                    _tsv_to_json([first, *fin], fout)
        return out
```

The long part is the TSV conversion: Zeek's older text format puts the type of every column in a `#types` header line, and `_convert` uses it so that numbers become numbers and sets become lists, exactly as in Zeek's JSON output.

**Step 6.** Create the tests `tests/unit/test_adapters.py`:

```python
"""Adapter tests (Fiona, FIO-01): which inputs each adapter accepts, and TSV -> JSON.

No test here runs Zeek: PcapAdapter.accepts() only reads the file's first
4 bytes ("magic number"), and ZeekLogAdapter only copies or converts logs.
"""

import struct
import zipfile
from pathlib import Path

import pytest

from maxguard.adapters.base import read_log
from maxguard.adapters.pcap import PcapAdapter
from maxguard.adapters.zeeklogs import ZeekLogAdapter

REPO = Path(__file__).resolve().parents[2]
PCAPS = REPO / "tests" / "pcaps"
FIXTURES = REPO / "tests" / "fixtures" / "zeek"


def pcap_header() -> bytes:
    """Classic pcap file header: magic, version 2.4, timezone, accuracy, snaplen, Ethernet."""
    return struct.pack("<IHHiIII", 0xA1B2C3D4, 2, 4, 0, 0, 65535, 1)


def pcapng_header() -> bytes:
    """pcapng Section Header Block: block type, length, byte-order magic, version 1.0,
    section length -1 ("unknown"), length again."""
    return struct.pack("<IIIHHqI", 0x0A0D0D0A, 28, 0x1A2B3C4D, 1, 0, -1, 28)


# ---- PcapAdapter: the magic number decides, not the file name ---------------

def test_pcap_adapter_accepts_a_lab_capture():
    assert PcapAdapter().accepts(PCAPS / "telnet.pcap")


@pytest.mark.parametrize(("name", "content"), [
    ("capture.pcap", pcap_header()),
    ("capture.pcapng", pcapng_header()),
    ("no_extension", pcap_header()),  # the extension does not matter
])
def test_pcap_adapter_accepts_pcap_and_pcapng(tmp_path, name, content):
    path = tmp_path / name
    path.write_bytes(content)
    assert PcapAdapter().accepts(path)


@pytest.mark.parametrize(("name", "content"), [
    ("notes.txt", b"hello, this is text\n"),
    ("fake.pcap", b"not a capture, just a .pcap name\n"),  # the extension does not help
    ("empty.pcap", b""),
])
def test_pcap_adapter_rejects_other_files(tmp_path, name, content):
    path = tmp_path / name
    path.write_bytes(content)
    assert not PcapAdapter().accepts(path)


def test_pcap_adapter_rejects_a_folder(tmp_path):
    assert not PcapAdapter().accepts(tmp_path)


# ---- ZeekLogAdapter: folders and archives of Zeek logs -----------------------

def test_zeek_log_adapter_accepts_a_folder_with_conn_log():
    assert ZeekLogAdapter().accepts(FIXTURES / "telnet")


def test_zeek_log_adapter_rejects_a_folder_without_conn_log(tmp_path):
    (tmp_path / "notes.txt").write_text("hello\n")
    assert not ZeekLogAdapter().accepts(tmp_path)


def test_json_logs_are_copied_unchanged(tmp_path):
    log_dir = ZeekLogAdapter().to_zeek_logs(FIXTURES / "telnet", tmp_path)

    for name in ("conn.log", "maxguard_cleartext.log"):
        assert (log_dir / name).read_bytes() == (FIXTURES / "telnet" / name).read_bytes()


def test_zip_of_logs_is_unpacked(tmp_path):
    archive = tmp_path / "telnet_logs.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        for log in sorted((FIXTURES / "telnet").glob("*.log")):
            zf.write(log, arcname=log.name)

    assert ZeekLogAdapter().accepts(archive)
    log_dir = ZeekLogAdapter().to_zeek_logs(archive, tmp_path / "work")
    assert (log_dir / "maxguard_cleartext.log").read_bytes() == (
        FIXTURES / "telnet" / "maxguard_cleartext.log").read_bytes()


# ---- TSV (Zeek's default log format) -> JSON ---------------------------------

TAB = "\t"
TSV_HEADER = [
    "#separator \\x09",
    "#set_separator" + TAB + ",",
    "#empty_field" + TAB + "(empty)",
    "#unset_field" + TAB + "-",
    "#path" + TAB + "conn",
    "#open" + TAB + "2026-10-06-01-52-44",
    TAB.join(["#fields", "ts", "uid", "id.orig_h", "id.orig_p", "id.resp_h", "id.resp_p",
              "proto", "service", "tunnel_parents"]),
    TAB.join(["#types", "time", "string", "addr", "port", "addr", "port",
              "enum", "string", "set[string]"]),
]
TSV_ROWS = [
    ["1791250000.100000", "C1aaaaaaaaaaaaaaaa", "192.168.56.50", "50001", "192.168.56.30", "23",
     "tcp", "-", "(empty)"],
    ["1791250001.200000", "C2bbbbbbbbbbbbbbbb", "192.168.56.50", "50002", "192.168.56.31", "80",
     "tcp", "http", "(empty)"],
    ["1791250002.300000", "C3cccccccccccccccc", "192.168.56.50", "53001", "192.168.56.1", "53",
     "udp", "dns", "(empty)"],
]


def write_tsv_conn_log(folder: Path) -> Path:
    folder.mkdir()
    lines = TSV_HEADER + [TAB.join(row) for row in TSV_ROWS] + ["#close" + TAB + "2026-10-06"]
    (folder / "conn.log").write_text("\n".join(lines) + "\n")
    return folder


def test_tsv_conn_log_becomes_one_json_record_per_row(tmp_path):
    tsv_dir = write_tsv_conn_log(tmp_path / "tsv")

    log_dir = ZeekLogAdapter().to_zeek_logs(tsv_dir, tmp_path / "work")
    records = list(read_log(log_dir, "conn.log"))

    assert len(records) == 3  # header and #close lines are not records
    assert [r["uid"] for r in records] == [row[1] for row in TSV_ROWS]
    first = records[0]
    assert first["id.resp_h"] == "192.168.56.30"
    # Values are converted with the #types header, the way Zeek writes JSON:
    # port -> int, time -> float, "-" (unset) -> None, "(empty)" set -> [].
    assert first["id.resp_p"] == 23
    assert first["ts"] == 1791250000.1
    assert first["service"] is None
    assert first["tunnel_parents"] == []
```

**Step 7.** Run them:

```bash
pytest tests/unit/test_adapters.py tests/unit/test_zeek_site.py -q
```

Expected output:

```text
................                                                                             [100%]
16 passed in 0.08s
```

**Step 8.** See the TSV conversion work on a hand-made fixture:

```bash
python -c "import json, tempfile; from pathlib import Path; from maxguard.adapters.zeeklogs import ZeekLogAdapter; out = ZeekLogAdapter().to_zeek_logs(Path('tests/fixtures/zeek/_handmade/tsv_plain_http'), Path(tempfile.mkdtemp())); print(sorted(p.name for p in out.iterdir())); rec = json.loads((out / 'conn.log').read_text().splitlines()[0]); print({k: rec[k] for k in ('ts', 'id.orig_h', 'id.resp_p', 'proto', 'service')})"
```

Expected output:

```text
['conn.log', 'http.log']
{'ts': 1791250493.372657, 'id.orig_h': '172.18.0.3', 'id.resp_p': 80, 'proto': 'tcp', 'service': 'http'}
```

**Step 9.** Commit, push, and open the pull request:

```bash
git add -A
git status          # only this task's files: nothing from .venv/, data/ or lab/captures/
git commit -m "feat: Zeek runner, PcapAdapter and ZeekLogAdapter (FIO-01)"
git push -u origin HEAD
```

`HEAD` means "the branch I am on", so you do not have to retype its name. Open the repository on github.com: a yellow bar shows your branch with a **Compare & pull request** button. Click it, keep the title `feat: Zeek runner, PcapAdapter and ZeekLogAdapter (FIO-01)`, fill in the template (paste the real output of the commands above under **How I tested it**), write `Closes #<issue number>` (this task's issue), and pick **@JWinborne1** under **Reviewers**. Click **Create pull request**, then fix anything CI or the reviewer finds with new commits on the same branch.

#### How to test

`pytest` passes. In the one-liner's output, `ts` and `id.resp_p` are numbers, not strings in quotes: that is the TSV conversion working. No test here needs Zeek; KAR-03's integration tests run the real `run_zeek()` inside the engine image.

#### What you just did and why

Contract 3 means the rest of MaxGuard never cares where logs came from: a capture, an imported folder, and later the live sensor and NetFlow all end up as one folder of Zeek JSON logs. The TSV fix matters because a set such as `cert_chain_fps` used to stay one long string, and every certificate rule then silently found nothing — a bug that only shows up with real Zeek output, which is why the tests use real fixtures. The archive checks (`ArchiveTooLarge`) stop a small zip that unpacks to terabytes from filling the disk.

#### Pull request checklist

- [ ] `ruff check .` prints `All checks passed!`
- [ ] `pytest -m "not integration" -q` passes on your laptop
- [ ] The pull request title has the form `type: summary (TASK-ID)` and the body says `Closes #<issue number>`
- [ ] No secrets, passwords, email addresses, personal data, or captures from a real network (CLAUDE.md rule 6)
- [ ] Any new dependency has a row in `docs/DEPENDENCIES.md` with its license
- [ ] CI is green and your reviewer approved
- [ ] `pcap.py` does not call Suricata yet (that is JAK-05)

### FIO-02: TLS and certificate rules

**Due:** Week 1 (due Fri Oct 16) · **Milestone:** `W1 Building blocks` · **Needs first:** [FIO-01](#fio-01-zeek-runner-and-the-two-input-adapters), [KAR-02](karthik.md#kar-02-test-fixtures-zeek-and-suricata-output-for-every-capture) · **Kind:** code, tested

**Issue labels:** `type:task` `phase:alpha` `owner:fiona` `area:engine` `critical-path`

#### Goal

Write six detection rules — outdated TLS version, weak cipher, expired, self-signed, weak-key, and SHA-1-signed certificates — each with a positive test (its capture triggers it) and a negative test (a capture that *almost* matches does not). Also add the tests that prove imported TSV logs find the same problems and that findings are identical on every run.

#### Prerequisites

FIO-01 is merged.

#### Steps

**Step 1.** Update `main` and create your branch for this task (one branch per task):

```bash
cd ~/projects/maxguard
source .venv/bin/activate
git checkout main && git pull
git checkout -b fiona/tls-cert-rules
```

If `source .venv/bin/activate` fails, you have not made the virtual environment yet: do Week 0 section 0.11 first.

**Step 2.** Create `maxguard/rules/tls.py`:

```python
"""TLS rules (Fiona). Field names checked against Zeek 9.0.0 ssl.log."""

from maxguard.adapters.base import read_log
from maxguard.ids import evidence
from maxguard.models import Finding
from maxguard.rules.base import rule

WEAK_VERSIONS = {"SSLv2", "SSLv3", "TLSv10", "TLSv11"}
WEAK_CIPHER_MARKERS = ("_NULL_", "_EXPORT", "_RC4_", "_DES_", "_3DES_", "_anon_")


def _finding(rec, rule_id, title, severity, details):
    return Finding(rule_id=rule_id, title=title, severity=severity,
                   src_ip=rec["id.orig_h"], dst_ip=rec["id.resp_h"],
                   dst_port=int(rec["id.resp_p"]), protocol="tls",
                   first_seen=float(rec["ts"]), last_seen=float(rec["ts"]),
                   details=details, evidence=[evidence("ssl.log", rec)])


@rule("tls.weak_version")
def weak_version(log_dir):
    return [_finding(r, "tls.weak_version", f"Outdated protocol {r['version']}",
                     "high", {"version": r["version"], "server_name": r.get("server_name")})
            for r in read_log(log_dir, "ssl.log") if r.get("version") in WEAK_VERSIONS]


@rule("tls.weak_cipher")
def weak_cipher(log_dir):
    return [_finding(r, "tls.weak_cipher", f"Weak cipher {r['cipher']}",
                     "high", {"cipher": r["cipher"]})
            for r in read_log(log_dir, "ssl.log")
            if r.get("cipher") and any(m in r["cipher"] for m in WEAK_CIPHER_MARKERS)]
```

**Step 3.** Create `maxguard/rules/certs.py`:

```python
"""Certificate rules (Fiona). Checked against Zeek 9.0.0.

In Zeek 9, x509.log has no connection fields (no uid, no IPs). Each
certificate is linked to the TLS session that carried it through
ssl.log's cert_chain_fps list, whose first entry is the server's (leaf)
certificate. Only leaf certificates are checked.
"""

from maxguard.adapters.base import read_log
from maxguard.ids import evidence
from maxguard.models import Finding
from maxguard.rules.base import rule


def _leaf_certs(log_dir):
    """Yield (ssl_record, x509_record) for every TLS session's leaf certificate."""
    certs = {c["fingerprint"]: c for c in read_log(log_dir, "x509.log")}
    for s in read_log(log_dir, "ssl.log"):
        fps = s.get("cert_chain_fps") or []
        if fps and fps[0] in certs:
            yield s, certs[fps[0]]


def _finding(s, c, rule_id, title, severity, details):
    ts = float(s["ts"])
    return Finding(rule_id=rule_id, title=title, severity=severity,
                   src_ip=s["id.orig_h"], dst_ip=s["id.resp_h"],
                   dst_port=int(s["id.resp_p"]), protocol="tls",
                   first_seen=ts, last_seen=ts,
                   details={"subject": c.get("certificate.subject"), **details},
                   evidence=[evidence("ssl.log", s), evidence("x509.log", c)])


@rule("cert.expired")
def expired(log_dir):
    # "Expired" means expired at the moment it was seen in the capture, not
    # today, so results never depend on when the analysis runs.
    return [_finding(s, c, "cert.expired", "Expired certificate", "high",
                     {"not_valid_after": c["certificate.not_valid_after"]})
            for s, c in _leaf_certs(log_dir)
            if float(c["certificate.not_valid_after"]) < float(s["ts"])]


@rule("cert.self_signed")
def self_signed(log_dir):
    return [_finding(s, c, "cert.self_signed", "Self-signed certificate", "medium",
                     {"issuer": c.get("certificate.issuer")})
            for s, c in _leaf_certs(log_dir)
            if c.get("certificate.subject") == c.get("certificate.issuer")]


@rule("cert.weak_key")
def weak_key(log_dir):
    return [_finding(s, c, "cert.weak_key",
                     f"Weak {c.get('certificate.key_length')}-bit RSA key", "high",
                     {"key_length": c.get("certificate.key_length")})
            for s, c in _leaf_certs(log_dir)
            if c.get("certificate.key_type") == "rsa"
            and int(c.get("certificate.key_length") or 0) < 2048]


@rule("cert.sha1_signature")
def sha1_signature(log_dir):
    return [_finding(s, c, "cert.sha1_signature", "Certificate signed with SHA-1", "medium",
                     {"sig_alg": c.get("certificate.sig_alg")})
            for s, c in _leaf_certs(log_dir)
            if "sha1" in (c.get("certificate.sig_alg") or "").lower()]
```

Zeek 9's `x509.log` has no IP addresses. A certificate is linked to its TLS session through `ssl.log`'s `cert_chain_fps`, whose first entry is the server's own (leaf) certificate; `_leaf_certs` does that join.

**Step 4.** Register the two modules: replace the contents of `maxguard/rules/__init__.py` with

```python
"""Importing this package registers every rule module with the registry."""

from . import certs, tls  # noqa: F401
```

(JAK-03 adds `cleartext` to this line.)

**Step 5.** Create the rule tests `tests/unit/test_rules_tls_certs.py`:

```python
"""TLS and certificate rule tests (Fiona, FIO-02): positive and negative for each rule.

tests/fixtures/zeek/<capture>/ holds the Zeek 9.0.0 logs of the lab capture
tests/pcaps/<capture>.pcap. Each capture shows exactly one weakness.
"""

from pathlib import Path

import pytest

import maxguard.rules  # noqa: F401  (importing registers every rule)
from maxguard.adapters.base import read_log
from maxguard.ids import record_id
from maxguard.rules.base import RULES

REPO = Path(__file__).resolve().parents[2]
FIXTURES = REPO / "tests" / "fixtures" / "zeek"

# capture folder -> the one rule it must trigger
EXPECTED = {
    "tls_weak_version": "tls.weak_version",
    "tls_weak_cipher": "tls.weak_cipher",
    "cert_expired": "cert.expired",
    "cert_self_signed": "cert.self_signed",
    "cert_weak_key": "cert.weak_key",
    "cert_sha1": "cert.sha1_signature",
}

# rule -> a capture that ALMOST matches it but must not trigger it
NEAR_MISS = {
    "tls.weak_version": "clean_tls13",  # TLSv13
    "tls.weak_cipher": "tls_weak_version",  # old version, but a strong cipher
    "cert.expired": "cert_self_signed",  # bad certificate, but not expired
    "cert.self_signed": "cert_expired",  # signed by the lab CA, not by itself
    "cert.weak_key": "cert_sha1",
    "cert.sha1_signature": "cert_weak_key",
}

TLS_AND_CERT_RULES = set(EXPECTED.values())


def test_the_six_tls_and_certificate_rules_are_registered():
    assert TLS_AND_CERT_RULES <= set(RULES)


def test_every_rule_has_a_near_miss_test():
    # A new rule must come with a negative test, not only a positive one.
    assert set(NEAR_MISS) == TLS_AND_CERT_RULES


@pytest.mark.parametrize(("capture", "rule_id"), sorted(EXPECTED.items()))
def test_rule_fires_on_its_capture(capture, rule_id):
    findings = RULES[rule_id](FIXTURES / capture)

    assert len(findings) >= 1
    for finding in findings:
        assert finding.rule_id == rule_id
        assert finding.protocol == "tls"
        assert finding.evidence, "every finding needs evidence the AI can cite"


@pytest.mark.parametrize(("capture", "rule_id"), sorted(EXPECTED.items()))
def test_evidence_points_at_real_log_records(capture, rule_id):
    # The AI cites evidence by record_id, so each one must name a record that
    # really is in that log file (ssl.log, and x509.log for certificate rules).
    log_dir = FIXTURES / capture
    for finding in RULES[rule_id](log_dir):
        for ev in finding.evidence:
            ids_in_log = {record_id(ev.log, rec) for rec in read_log(log_dir, ev.log)}
            assert ev.record_id in ids_in_log


@pytest.mark.parametrize(("rule_id", "capture"), sorted(NEAR_MISS.items()))
def test_rule_is_silent_on_near_miss(rule_id, capture):
    assert RULES[rule_id](FIXTURES / capture) == []


@pytest.mark.parametrize("rule_id", sorted(TLS_AND_CERT_RULES))
def test_rule_is_silent_on_clean_tls13(rule_id):
    assert RULES[rule_id](FIXTURES / "clean_tls13") == []


def test_certificate_findings_cite_both_the_session_and_the_certificate():
    [finding] = RULES["cert.expired"](FIXTURES / "cert_expired")
    assert [ev.log for ev in finding.evidence] == ["ssl.log", "x509.log"]


def test_expired_means_expired_when_seen_not_today():
    # cert.expired compares with the capture time, so the result never depends
    # on the day the analysis runs (CLAUDE.md rule 2).
    [finding] = RULES["cert.expired"](FIXTURES / "cert_expired")
    assert finding.details["not_valid_after"] < finding.first_seen
```

**Step 6.** Now that certificate rules exist, add the import tests `tests/unit/test_zeeklogs_import.py`:

```python
"""Importing existing Zeek logs (FIO-02): TSV typing, eve.json, gzip archives, safety limits.

These tests use the TLS and certificate rules, so they come with FIO-02.
"""

import gzip
import shutil
import tarfile
import zipfile
from pathlib import Path

import pytest

import maxguard.rules  # noqa: F401  (importing registers every rule)
from maxguard.adapters import zeeklogs
from maxguard.adapters.base import read_log
from maxguard.adapters.zeeklogs import ArchiveTooLarge, ZeekLogAdapter
from maxguard.rules.base import run_all

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "zeek"


def test_tsv_certificate_logs_still_trigger_certificate_rules(tmp_path):
    # Zeek 9.0.0 TSV output of tests/pcaps/cert_expired.pcap. cert_chain_fps is a
    # vector; before the #types fix it stayed one string and cert rules found nothing.
    log_dir = ZeekLogAdapter().to_zeek_logs(FIXTURES / "_handmade" / "tsv_cert_expired", tmp_path)

    ssl = next(read_log(log_dir, "ssl.log"))
    assert isinstance(ssl["cert_chain_fps"], list)
    assert [f.rule_id for f in run_all(log_dir)] == ["cert.expired"]


def test_tsv_and_json_imports_give_the_same_finding_id(tmp_path):
    from_tsv = run_all(ZeekLogAdapter().to_zeek_logs(
        FIXTURES / "_handmade" / "tsv_cert_expired", tmp_path))
    from_json = run_all(FIXTURES / "cert_expired")
    assert [f.finding_id for f in from_tsv] == [f.finding_id for f in from_json]


def test_eve_json_is_kept(tmp_path):
    log_dir = ZeekLogAdapter().to_zeek_logs(FIXTURES / "tls_weak_version", tmp_path)
    events = list(read_log(log_dir, "eve.json"))
    assert {e["event_type"] for e in events} >= {"tls"}


def test_rotated_gzipped_logs_are_appended_in_order(tmp_path):
    # Zeek's own archive folders hold one gzipped file per hour, for example
    # ssl.00:00:00-01:00:00.log.gz. Both hours must end up in one ssl.log.
    src = tmp_path / "archive"
    src.mkdir()
    shutil.copy(FIXTURES / "tls_weak_version" / "conn.log", src / "conn.log")
    line = (FIXTURES / "tls_weak_version" / "ssl.log").read_text().splitlines()[0]
    for hour in ("00", "01"):
        with gzip.open(src / f"ssl.{hour}:00:00-{hour}:59:59.log.gz", "wt") as f:
            f.write(line + "\n")

    log_dir = ZeekLogAdapter().to_zeek_logs(src, tmp_path / "work")

    assert len(list(read_log(log_dir, "ssl.log"))) == 2
    [finding] = run_all(log_dir)
    assert finding.rule_id == "tls.weak_version" and finding.count == 2


def test_zip_and_tar_imports_match(tmp_path):
    folder = FIXTURES / "tls_weak_version"
    z = tmp_path / "logs.zip"
    with zipfile.ZipFile(z, "w") as zf:
        for p in sorted(folder.iterdir()):
            zf.write(p, f"logs/{p.name}")
    t = tmp_path / "logs.tar.gz"
    with tarfile.open(t, "w:gz") as tf:
        tf.add(folder, arcname="logs")

    a = run_all(ZeekLogAdapter().to_zeek_logs(z, tmp_path / "a"))
    b = run_all(ZeekLogAdapter().to_zeek_logs(t, tmp_path / "b"))
    assert [f.to_dict() for f in a] == [f.to_dict() for f in b]


def test_archive_that_unpacks_too_large_is_refused(tmp_path, monkeypatch):
    monkeypatch.setattr(zeeklogs, "MAX_EXTRACTED_BYTES", 10)
    z = tmp_path / "big.zip"
    with zipfile.ZipFile(z, "w") as zf:
        zf.writestr("conn.log", "x" * 100)
    with pytest.raises(ArchiveTooLarge):
        ZeekLogAdapter().to_zeek_logs(z, tmp_path / "work")
```

and the merge and determinism tests `tests/unit/test_merge_determinism.py`:

```python
"""merge() and determinism tests (Fiona).

merge(): many findings for the same (rule_id, src, dst, port) become one, with
a count and at most MAX_EVIDENCE evidence records (Contract 1).

Determinism (CLAUDE.md rule 2): the same logs must always give the same
findings, finding_ids and evidence record_ids, or AI citations and alert
de-duplication break.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

import maxguard.rules  # noqa: F401  (importing registers every rule)
from maxguard.adapters.zeeklogs import ZeekLogAdapter
from maxguard.models import Evidence, Finding, make_finding_id
from maxguard.rules.base import MAX_EVIDENCE, merge, run_all

REPO = Path(__file__).resolve().parents[2]
FIXTURES = REPO / "tests" / "fixtures" / "zeek"


def telnet_finding(ts: float, record: str, dst_port: int = 23) -> Finding:
    """One finding as a rule would make it: one connection, one evidence record."""
    return Finding(rule_id="cleartext.telnet", title="Telnet session in cleartext",
                   severity="high", src_ip="192.168.56.50", dst_ip="192.168.56.30",
                   dst_port=dst_port, protocol="telnet", first_seen=ts, last_seen=ts,
                   evidence=[Evidence(log="maxguard_cleartext.log", uid=f"C{record}",
                                      ts=ts, record_id=record)])


# ---- merge() ---------------------------------------------------------------

def test_duplicates_collapse_into_one_finding_with_a_count():
    findings = [telnet_finding(200.0, "r1"), telnet_finding(100.0, "r2"),
                telnet_finding(300.0, "r3")]

    merged = merge(findings)

    assert len(merged) == 1
    assert merged[0].count == 3
    assert (merged[0].first_seen, merged[0].last_seen) == (100.0, 300.0)
    assert [ev.record_id for ev in merged[0].evidence] == ["r1", "r2", "r3"]


def test_finding_id_depends_only_on_rule_hosts_and_port():
    a, b = telnet_finding(100.0, "r1"), telnet_finding(999.0, "r2")
    assert a.finding_id == b.finding_id
    assert a.finding_id == make_finding_id("cleartext.telnet", "192.168.56.50",
                                           "192.168.56.30", 23)


def test_a_different_port_is_a_different_finding():
    merged = merge([telnet_finding(100.0, "r1", dst_port=23),
                    telnet_finding(200.0, "r2", dst_port=2323)])

    assert [(f.dst_port, f.count) for f in merged] == [(23, 1), (2323, 1)]
    assert merged[0].finding_id != merged[1].finding_id


def test_evidence_is_capped_at_five_but_count_is_not():
    findings = [telnet_finding(100.0 + i, f"r{i}") for i in range(7)]

    merged = merge(findings)

    assert MAX_EVIDENCE == 5
    assert merged[0].count == 7  # every connection is counted...
    # ...but only the first five records are kept, so reports stay small.
    assert [ev.record_id for ev in merged[0].evidence] == ["r0", "r1", "r2", "r3", "r4"]


def test_merge_keeps_the_order_findings_first_appeared_in():
    other = telnet_finding(50.0, "x1", dst_port=2323)
    merged = merge([telnet_finding(100.0, "r1"), other, telnet_finding(200.0, "r2")])
    assert [f.dst_port for f in merged] == [23, 2323]


# ---- determinism -----------------------------------------------------------

def json_fixture_dirs() -> list[Path]:
    """Every fixture folder of JSON logs: the lab captures and the hand-made ones."""
    folders = [p for p in FIXTURES.iterdir() if p.is_dir() and not p.name.startswith("_")]
    handmade = [p for p in (FIXTURES / "_handmade").iterdir()
                if p.is_dir() and not p.name.startswith("tsv_")]  # TSV needs the adapter first
    return sorted(folders + handmade)


def tsv_fixture_dirs() -> list[Path]:
    return sorted((FIXTURES / "_handmade").glob("tsv_*"))


def findings_as_dicts(log_dir: Path) -> list[dict]:
    return [f.to_dict() for f in run_all(log_dir)]


@pytest.mark.parametrize("log_dir", json_fixture_dirs(), ids=lambda p: p.name)
def test_run_all_twice_gives_identical_findings(log_dir):
    assert findings_as_dicts(log_dir) == findings_as_dicts(log_dir)


@pytest.mark.parametrize("tsv_dir", tsv_fixture_dirs(), ids=lambda p: p.name)
def test_tsv_import_twice_gives_identical_findings(tsv_dir, tmp_path):
    first = ZeekLogAdapter().to_zeek_logs(tsv_dir, tmp_path / "first")
    second = ZeekLogAdapter().to_zeek_logs(tsv_dir, tmp_path / "second")
    assert findings_as_dicts(first) == findings_as_dicts(second)


# Python gives each run a random "hash seed", which changes the order of a set.
# Two runs inside one test share the seed, so a rule that loops over a set
# would still pass the test above. Separate processes with different seeds
# catch that.
PRINT_ALL_FINDINGS = """
import json, sys
from pathlib import Path
import maxguard.rules
from maxguard.rules.base import run_all
out = {d: [f.to_dict() for f in run_all(Path(d))] for d in sys.argv[1:]}
print(json.dumps(out, sort_keys=True))
"""


def findings_in_new_process(hash_seed: str) -> dict:
    env = {**os.environ, "PYTHONHASHSEED": hash_seed}
    folders = [str(p) for p in json_fixture_dirs()]
    result = subprocess.run([sys.executable, "-c", PRINT_ALL_FINDINGS, *folders],
                            cwd=REPO, env=env, capture_output=True, text=True, check=True)
    return json.loads(result.stdout)


def test_findings_do_not_depend_on_the_hash_seed():
    first = findings_in_new_process("1")
    assert any(first.values()), "the fixtures should produce some findings"
    assert first == findings_in_new_process("2")
```

**Step 7.** Run them:

```bash
pytest tests/unit/test_rules_tls_certs.py tests/unit/test_zeeklogs_import.py tests/unit/test_merge_determinism.py -q
```

Expected output:

```text
............................................................                                 [100%]
60 passed in 0.26s
```

**Step 8.** Run all registered rules on one fixture folder, the way the pipeline will:

```bash
python -c "from pathlib import Path; import maxguard.rules; from maxguard.rules.base import run_all; [print(f.rule_id, f.severity, f.dst_ip, f.dst_port, f.title, f.evidence[0].record_id) for f in run_all(Path('tests/fixtures/zeek/cert_expired'))]"
```

Expected output:

```text
cert.expired high 172.18.0.2 4433 Expired certificate c4e373ad73162b38
```

**Step 9.** Commit, push, and open the pull request:

```bash
git add -A
git status          # only this task's files: nothing from .venv/, data/ or lab/captures/
git commit -m "feat: TLS and certificate rules with tests (FIO-02)"
git push -u origin HEAD
```

`HEAD` means "the branch I am on", so you do not have to retype its name. Open the repository on github.com: a yellow bar shows your branch with a **Compare & pull request** button. Click it, keep the title `feat: TLS and certificate rules with tests (FIO-02)`, fill in the template (paste the real output of the commands above under **How I tested it**), write `Closes #<issue number>` (this task's issue), and pick **@JWinborne1** under **Reviewers**. Click **Create pull request**, then fix anything CI or the reviewer finds with new commits on the same branch.

#### How to test

All three files pass. The one-liner prints exactly one finding, `cert.expired`, with the record ID of the `ssl.log` line that is its evidence. Run it twice: the record ID does not change.

#### What you just did and why

Each lab capture contains exactly one weakness, so a positive test shows the rule fires and the negative "near miss" test shows it does not fire on something that only looks similar (a strong cipher, a valid certificate). Without the negative tests a rule that fires on everything would pass. `merge()` collapses many identical findings into one with a count, and keeps at most five evidence records, so a busy network gives one alert instead of thousands. Severities are part of the Security Lead's review, so Ahmad signs off on this pull request too.

#### Pull request checklist

- [ ] `ruff check .` prints `All checks passed!`
- [ ] `pytest -m "not integration" -q` passes on your laptop
- [ ] The pull request title has the form `type: summary (TASK-ID)` and the body says `Closes #<issue number>`
- [ ] No secrets, passwords, email addresses, personal data, or captures from a real network (CLAUDE.md rule 6)
- [ ] Any new dependency has a row in `docs/DEPENDENCIES.md` with its license
- [ ] CI is green and your reviewer approved
- [ ] Every rule has a positive and a negative test
- [ ] Ahmad approved the severities

### FIO-03: MITRE ATT&CK mapping file

**Due:** Week 2 (due Fri Oct 23) · **Milestone:** `W2 First end-to-end demo` · **Needs first:** [AMO-01](amory.md#amo-01-nist-sp-800-53-mapping-file-and-the-mapping-checks), [JAK-03](jakub.md#jak-03-cleartext-and-rdp-rules-the-rule-set-is-complete) · **Kind:** code, tested

**Issue labels:** `type:task` `phase:alpha` `owner:fiona` `area:mapping` `critical-path`

#### Goal

Add `mappings/attack.yaml`: for each rule, the ATT&CK technique an attacker would use against the weakness it finds (for example a cleartext password is collected with T1040 Network Sniffing). The loader puts these rows into `Finding.attack`, separate from the compliance controls.

#### Prerequisites

AMO-01 (mapping file checks) and JAK-03 (all 13 rules registered) are merged.

#### Steps

**Step 1.** Update `main` and create your branch for this task (one branch per task):

```bash
cd ~/projects/maxguard
source .venv/bin/activate
git checkout main && git pull
git checkout -b fiona/attack-mapping
```

If `source .venv/bin/activate` fails, you have not made the virtual environment yet: do Week 0 section 0.11 first.

**Step 2.** Create `mappings/attack.yaml`:

```yaml
# MITRE ATT&CK mappings for MaxGuard rules (Contract 2; fields explained in
# mappings/schema.md). Each row names a technique an attacker would use
# AGAINST the weakness a rule finds (for example: a cleartext password is
# collected with T1040 Network Sniffing). These rows fill Finding.attack, not
# Finding.controls, so they never appear in the compliance tables.
#
# How the rows were checked (CLAUDE.md rule 8), on 2026-10-06:
#   Current Enterprise release = 19.2 (modified 2026-08-05), read from MITRE's
#   own index: https://raw.githubusercontent.com/mitre-attack/attack-stix-data/master/index.json
#   Every technique ID, name and tactic below was read from that release's
#   STIX bundle (the "source" link): attack-pattern name, external_id, and
#   kill_chain_phases.phase_name (= the tactic shortname). None is revoked or
#   deprecated in 19.2.
#   Note: v19 split Defense Evasion into "stealth" and "defense-impairment",
#   so older lists that say "defense-evasion" are out of date.
#
# Sources for facts used in the rationales:
#   RDP: MS-RDPBCGR 1.3.1.2 says the standard RDP connection sequence does not
#     authenticate the server and is open to man-in-the-middle attacks:
#     https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-rdpbcgr/49e2791f-72d0-4229-92b7-8f32c48a7206
#   SHA-1: first practical chosen-prefix collision (Leurent & Peyrin, USENIX Security 2020):
#     https://www.usenix.org/conference/usenixsecurity20/presentation/leurent
#
# Fields for ATT&CK rows:
#   control_id = technique ID, title = technique name (a sub-technique is
#   written "<technique>: <sub-technique>", the way attack.mitre.org shows it),
#   tactic = ONE tactic shortname (a technique can belong to several; we pick
#   the one the rationale describes), rationale = one plain sentence.
#
# Before every release, check for a newer point release in the index above.

framework: MITRE ATT&CK
version: "v19.2"
source: https://github.com/mitre-attack/attack-stix-data/blob/master/enterprise-attack/enterprise-attack-19.2.json

mappings:
  cleartext.ftp:
    - control_id: T1040
      title: Network Sniffing
      tactic: credential-access
      rationale: FTP sends the user name and password unencrypted, so anyone who can capture traffic on the network path can read the login.
      verified: "enterprise-attack-19.2.json, T1040 (credential-access, discovery)"

  cleartext.telnet:
    - control_id: T1040
      title: Network Sniffing
      tactic: credential-access
      rationale: Telnet sends the password and every command unencrypted, so anyone who can capture traffic on the network path can read them.
      verified: "enterprise-attack-19.2.json, T1040 (credential-access, discovery)"

  cleartext.http:
    - control_id: T1040
      title: Network Sniffing
      tactic: credential-access
      rationale: Plain HTTP sends logins, form data and session cookies unencrypted, so anyone who can capture traffic can read them.
      verified: "enterprise-attack-19.2.json, T1040 (credential-access, discovery)"
    - control_id: T1557
      title: Adversary-in-the-Middle
      tactic: credential-access
      rationale: Without TLS the client cannot tell whether it is talking to the real server, so an attacker in the middle can read and change pages and steal sessions.
      verified: "enterprise-attack-19.2.json, T1557 (credential-access, collection)"

  cleartext.http_alt:
    - control_id: T1040
      title: Network Sniffing
      tactic: credential-access
      rationale: Plain HTTP on port 8080 sends logins, form data and session cookies unencrypted, so anyone who can capture traffic can read them.
      verified: "enterprise-attack-19.2.json, T1040 (credential-access, discovery)"
    - control_id: T1557
      title: Adversary-in-the-Middle
      tactic: credential-access
      rationale: Without TLS the client cannot tell whether it is talking to the real server, so an attacker in the middle can read and change pages and steal sessions.
      verified: "enterprise-attack-19.2.json, T1557 (credential-access, collection)"

  cleartext.pop3:
    - control_id: T1040
      title: Network Sniffing
      tactic: credential-access
      rationale: POP3 without TLS sends the mailbox password and the mail itself unencrypted, so anyone who can capture traffic can read both.
      verified: "enterprise-attack-19.2.json, T1040 (credential-access, discovery)"

  cleartext.imap:
    - control_id: T1040
      title: Network Sniffing
      tactic: credential-access
      rationale: IMAP without TLS sends the mailbox password and the mail itself unencrypted, so anyone who can capture traffic can read both.
      verified: "enterprise-attack-19.2.json, T1040 (credential-access, discovery)"

  rdp.standard_security:
    - control_id: T1557
      title: Adversary-in-the-Middle
      tactic: credential-access
      rationale: Standard RDP Security does not prove the server's identity (MS-RDPBCGR 1.3.1.2), so an attacker in the middle can pose as the server and capture the login.
      verified: "enterprise-attack-19.2.json, T1557 (credential-access, collection)"

  tls.weak_version:
    - control_id: T1557
      title: Adversary-in-the-Middle
      tactic: credential-access
      rationale: Old SSL/TLS versions have known attacks that an attacker in the middle can use to read or change the protected traffic.
      verified: "enterprise-attack-19.2.json, T1557 (credential-access, collection); its description names SSL/TLS version downgrades"
    - control_id: T1689
      title: Downgrade Attack
      tactic: defense-impairment
      rationale: Because the server still accepts an outdated TLS version, an attacker can push connections down to it on purpose.
      verified: "enterprise-attack-19.2.json, T1689 (defense-impairment); replaces revoked T1562.010"

  tls.weak_cipher:
    - control_id: T1040
      title: Network Sniffing
      tactic: credential-access
      rationale: A NULL, export-grade or broken cipher leaves the traffic readable or easy to decrypt, so captured traffic exposes logins and data.
      verified: "enterprise-attack-19.2.json, T1040 (credential-access, discovery)"
    - control_id: T1689
      title: Downgrade Attack
      tactic: defense-impairment
      rationale: Because the server still accepts a weak cipher, an attacker can steer connections to use it on purpose.
      verified: "enterprise-attack-19.2.json, T1689 (defense-impairment); replaces revoked T1562.010"

  cert.expired:
    - control_id: T1557
      title: Adversary-in-the-Middle
      tactic: credential-access
      rationale: Users who are used to clicking through an expired-certificate warning will also click through the warning for an attacker's fake certificate.
      verified: "enterprise-attack-19.2.json, T1557 (credential-access, collection)"

  cert.self_signed:
    - control_id: T1557
      title: Adversary-in-the-Middle
      tactic: credential-access
      rationale: Clients that accept this self-signed certificate cannot tell it apart from an attacker's, so an attacker in the middle can pose as the server.
      verified: "enterprise-attack-19.2.json, T1557 (credential-access, collection)"
    - control_id: T1587.003
      title: "Develop Capabilities: Digital Certificates"
      tactic: resource-development
      rationale: Making a self-signed certificate that looks just like this one costs an attacker nothing, because no certificate authority has to sign it.
      verified: "enterprise-attack-19.2.json, T1587.003 (resource-development)"

  cert.weak_key:
    - control_id: T1557
      title: Adversary-in-the-Middle
      tactic: credential-access
      rationale: An RSA key shorter than 2048 bits may be broken, and with the private key an attacker in the middle can pose as the server.
      verified: "enterprise-attack-19.2.json, T1557 (credential-access, collection)"

  cert.sha1_signature:
    - control_id: T1557
      title: Adversary-in-the-Middle
      tactic: credential-access
      rationale: SHA-1 collisions are practical, so a forged certificate with a matching SHA-1 signature could let an attacker in the middle pose as the server.
      verified: "enterprise-attack-19.2.json, T1557 (credential-access, collection)"
```

Every row was checked against MITRE's own release file for Enterprise ATT&CK v19.2 (the `source` link). Before every release, check the index in the header for a newer v19 point release and update `version` if there is one.

**Step 3.** Run the mapping checks (they now include this file):

```bash
pytest tests/unit/test_mappings.py -q
```

Expected output:

```text
..........................s..........                                                        [100%]
36 passed, 1 skipped in 0.26s
```

**Step 4.** See the techniques the loader adds to the Telnet finding:

```bash
python -c "from pathlib import Path; import maxguard.rules; from maxguard.rules.base import run_all; from maxguard.mapping.loader import apply, load_all; findings = apply(run_all(Path('tests/fixtures/zeek/telnet')), load_all(Path('mappings'))); [print(t.technique_id, t.name, '-', t.tactic) for t in findings[0].attack]"
```

Expected output:

```text
T1040 Network Sniffing - credential-access
```

**Step 5.** Commit, push, and open the pull request:

```bash
git add -A
git status          # only this task's files: nothing from .venv/, data/ or lab/captures/
git commit -m "feat: MITRE ATT&CK v19.2 mapping file (FIO-03)"
git push -u origin HEAD
```

`HEAD` means "the branch I am on", so you do not have to retype its name. Open the repository on github.com: a yellow bar shows your branch with a **Compare & pull request** button. Click it, keep the title `feat: MITRE ATT&CK v19.2 mapping file (FIO-03)`, fill in the template (paste the real output of the commands above under **How I tested it**), write `Closes #<issue number>` (this task's issue), and pick **@ahmadalkhoudeir** under **Reviewers**. Click **Create pull request**, then fix anything CI or the reviewer finds with new commits on the same branch.

#### How to test

`test_mappings.py` passes for all five files, and the one-liner prints T1040 for the Telnet finding.

#### What you just did and why

Compliance controls say *which rule of a framework* a weakness breaks; ATT&CK says *how an attacker would use it*. Analysts think in ATT&CK, and the timeline page groups events by technique. Reusing the Contract 2 file format (plus a `tactic` key) means the same loader and the same checks work for both. In ATT&CK v19, Defense Evasion was split into two tactics, which is why the version is pinned and checked (CLAUDE.md rule 8).

#### Pull request checklist

- [ ] `ruff check .` prints `All checks passed!`
- [ ] `pytest -m "not integration" -q` passes on your laptop
- [ ] The pull request title has the form `type: summary (TASK-ID)` and the body says `Closes #<issue number>`
- [ ] No secrets, passwords, email addresses, personal data, or captures from a real network (CLAUDE.md rule 6)
- [ ] Any new dependency has a row in `docs/DEPENDENCIES.md` with its license
- [ ] CI is green and your reviewer approved
- [ ] Every row has `verified` naming the release file it was checked in
- [ ] Ahmad reviewed the rows (compliance accuracy)

### FIO-04: The maxguard command, first version (JSON reports)

**Due:** Week 2 (due Fri Oct 23) · **Milestone:** `W2 First end-to-end demo` · **Needs first:** [JAI-05](jaiden.md#jai-05-the-pipeline-one-function-from-input-to-report), [FIO-03](#fio-03-mitre-attck-mapping-file) · **Kind:** code, tested

**Issue labels:** `type:task` `phase:alpha` `owner:fiona` `area:engine` `critical-path`

#### Goal

Give MaxGuard its command line: `maxguard analyze INPUT` runs the pipeline and writes a JSON report, with `--no-ai`, `-o FILE`, and `--frameworks`. Exit codes tell scripts what happened (0 ok, 2 bad input, 3 Zeek failed). This is the command shown at the Week 2 demo.

#### Prerequisites

JAI-05 (pipeline) and FIO-03 (ATT&CK file) are merged.

#### Steps

**Step 1.** Update `main` and create your branch for this task (one branch per task):

```bash
cd ~/projects/maxguard
source .venv/bin/activate
git checkout main && git pull
git checkout -b fiona/cli
```

If `source .venv/bin/activate` fails, you have not made the virtual environment yet: do Week 0 section 0.11 first.

**Step 2.** Create `cli/main.py`:

```python
"""MaxGuard command line (Fiona).

    maxguard analyze INPUT [-o report.json] [--no-ai]
                           [--frameworks 'PCI DSS,NIST SP 800-53']

INPUT is a .pcap/.pcapng capture, or a folder/.zip/.tar.gz of Zeek logs.
Run it as `maxguard ...` (console script) or `python -m cli.main ...`.

Exit codes, so scripts and CI can react without reading the text:
    0  the report was written
    2  bad input: missing file, not a capture or Zeek log folder, unknown framework
       (argparse also uses 2 for a wrong option)
    3  Zeek failed on the capture
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

from maxguard.mapping.loader import ATTACK, load_all
from maxguard.pipeline import UnsupportedInput, analyze, mappings_dir
from maxguard.zeek.runner import ZeekError

EXIT_OK = 0
EXIT_BAD_INPUT = 2
EXIT_ZEEK_ERROR = 3


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="maxguard", description="Find security weaknesses in network traffic, offline.")
    commands = parser.add_subparsers(dest="command", required=True)

    cmd = commands.add_parser(
        "analyze", help="analyze a capture file or a folder/archive of Zeek logs")
    cmd.add_argument("input", type=Path,
                     help=".pcap/.pcapng file, or a folder, .zip or .tar.gz of Zeek logs")
    cmd.add_argument("-o", "--output", type=Path,
                     help="write the report to this file (default: print it)")
    cmd.add_argument("--no-ai", action="store_true",
                     help="skip the AI explanations (no Ollama needed)")
    cmd.add_argument("--frameworks",
                     help="comma-separated list, e.g. 'PCI DSS,NIST SP 800-53' (default: all)")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)  # a wrong option: argparse prints usage, exits with 2
    if args.command == "analyze":
        return run_analyze(args)
    parser.error(f"unknown command {args.command!r}")  # exits with 2


def run_analyze(args: argparse.Namespace) -> int:
    """The `analyze` command: check the input, run the pipeline, write the report."""
    if not args.input.exists():
        return fail(f"{args.input}: no such file or folder", EXIT_BAD_INPUT)

    frameworks = parse_frameworks(args.frameworks)
    unknown = unknown_frameworks(frameworks)
    if unknown:
        # Without this check a typo ("PCI-DSS") would silently give a report with no controls.
        return fail(f"unknown framework(s): {', '.join(unknown)}. "
                    f"Known: {', '.join(known_frameworks())}", EXIT_BAD_INPUT)

    try:
        # Zeek's logs go to a temporary folder that is deleted afterwards, so no
        # copy of the user's traffic is left behind on disk.
        with tempfile.TemporaryDirectory(prefix="maxguard-") as workdir:
            report = analyze(args.input, workdir, frameworks=frameworks,
                             explain=not args.no_ai)
    except UnsupportedInput as error:
        return fail(str(error), EXIT_BAD_INPUT)
    except ZeekError as error:
        return fail(f"Zeek failed: {error}", EXIT_ZEEK_ERROR)

    write_report(to_json(report), args.output)
    if args.output:
        # Status goes to stderr, so stdout stays clean when the report is printed.
        print(f"maxguard: {len(report['findings'])} finding(s), report written to "
              f"{args.output}", file=sys.stderr)
    return EXIT_OK


def parse_frameworks(text: str | None) -> list[str] | None:
    """'PCI DSS, NIST SP 800-53' -> ['PCI DSS', 'NIST SP 800-53']. None means "all"."""
    if not text:
        return None
    names = [name.strip() for name in text.split(",")]
    return [name for name in names if name] or None


def known_frameworks() -> list[str]:
    """Compliance framework names from mappings/*.yaml, e.g. ['CISA CPG', 'CJIS', ...].

    MITRE ATT&CK is left out: its techniques are always added, so it is not
    something to select (and selecting only it would hide every control).
    """
    return sorted({fw["framework"] for fw in load_all(mappings_dir())} - {ATTACK})


def unknown_frameworks(selected: list[str] | None) -> list[str]:
    if not selected:
        return []
    known = set(known_frameworks())
    return [name for name in selected if name not in known]


def to_json(report: dict) -> str:
    """The report as JSON. Sorted keys and a fixed indent make two reports easy to diff."""
    return json.dumps(report, sort_keys=True, indent=2) + "\n"


def write_report(text: str, output: Path | None) -> None:
    if output is None:
        sys.stdout.write(text)
    else:
        output.write_text(text, encoding="utf-8")


def fail(message: str, exit_code: int) -> int:
    print(f"maxguard: error: {message}", file=sys.stderr)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
```

`pyproject.toml` (JAI-01) already declares the `maxguard` command as `cli.main:main`, so after this file exists the command works in your virtual environment.

**Step 3.** Create the tests `tests/unit/test_cli.py`:

```python
"""CLI tests (Fiona): `maxguard analyze` on a fixture log folder, and exit codes.

These call cli.main.main([...]) directly instead of starting a new process:
same code path, much faster. A fixture *log folder* goes through
ZeekLogAdapter, so no Zeek is needed, and --no-ai means no Ollama is needed.
"""

import json
from pathlib import Path

import pytest

from cli import main as cli
from maxguard.zeek.runner import ZeekError

REPO = Path(__file__).resolve().parents[2]
TELNET_LOGS = REPO / "tests" / "fixtures" / "zeek" / "telnet"


def test_analyze_log_folder_writes_json_report(tmp_path, capsys):
    out = tmp_path / "report.json"

    code = cli.main(["analyze", str(TELNET_LOGS), "--no-ai", "-o", str(out)])

    assert code == cli.EXIT_OK
    report = json.loads(out.read_text())
    assert report["schema"] == "maxguard.report/2"
    assert report["input"]["adapter"] == "zeek-logs"
    assert report["ai"]["status"] == "disabled"
    assert [f["rule_id"] for f in report["findings"]] == ["cleartext.telnet"]
    # mappings/attack.yaml is applied: Telnet passwords can be sniffed.
    assert "T1040" in [t["technique_id"] for t in report["findings"][0]["attack"]]
    assert "1 finding(s)" in capsys.readouterr().err


def test_without_output_file_the_report_goes_to_stdout(capsys):
    code = cli.main(["analyze", str(TELNET_LOGS), "--no-ai"])

    assert code == cli.EXIT_OK
    report = json.loads(capsys.readouterr().out)
    assert report["findings"][0]["rule_id"] == "cleartext.telnet"


def test_same_input_gives_byte_identical_reports(tmp_path):
    first, second = tmp_path / "first.json", tmp_path / "second.json"
    cli.main(["analyze", str(TELNET_LOGS), "--no-ai", "-o", str(first)])
    cli.main(["analyze", str(TELNET_LOGS), "--no-ai", "-o", str(second)])
    assert first.read_bytes() == second.read_bytes()


def test_frameworks_option_keeps_only_those_controls(tmp_path):
    out = tmp_path / "report.json"

    cli.main(["analyze", str(TELNET_LOGS), "--no-ai", "-o", str(out),
              "--frameworks", "NIST SP 800-53"])

    finding = json.loads(out.read_text())["findings"][0]
    assert finding["controls"], "NIST maps cleartext.telnet"
    assert {c["framework"] for c in finding["controls"]} == {"NIST SP 800-53"}
    assert finding["attack"], "ATT&CK techniques are always added"


# ---- exit codes ------------------------------------------------------------

def test_text_file_is_bad_input(tmp_path, capsys):
    notes = tmp_path / "notes.txt"
    notes.write_text("hello\n")

    assert cli.main(["analyze", str(notes), "--no-ai"]) == cli.EXIT_BAD_INPUT
    assert "not a pcap/pcapng file" in capsys.readouterr().err


def test_missing_input_is_bad_input(tmp_path):
    missing = tmp_path / "missing.pcap"
    assert cli.main(["analyze", str(missing), "--no-ai"]) == cli.EXIT_BAD_INPUT


def test_unknown_framework_is_bad_input(capsys):
    code = cli.main(["analyze", str(TELNET_LOGS), "--no-ai", "--frameworks", "PCI-DSS"])

    assert code == cli.EXIT_BAD_INPUT
    assert "unknown framework(s): PCI-DSS" in capsys.readouterr().err


def test_wrong_option_exits_with_2():
    with pytest.raises(SystemExit) as stop:  # argparse exits by itself
        cli.main(["analyze", str(TELNET_LOGS), "--colour"])
    assert stop.value.code == cli.EXIT_BAD_INPUT


def test_zeek_failure_exits_with_3(monkeypatch, tmp_path, capsys):
    def zeek_fails(*args, **kwargs):
        raise ZeekError("problem with trace file")

    monkeypatch.setattr(cli, "analyze", zeek_fails)
    capture = tmp_path / "broken.pcap"
    capture.write_bytes(b"\xd4\xc3\xb2\xa1 not really a capture")

    assert cli.main(["analyze", str(capture), "--no-ai"]) == cli.EXIT_ZEEK_ERROR
    assert "Zeek failed: problem with trace file" in capsys.readouterr().err
```

**Step 4.** Run them:

```bash
pytest tests/unit/test_cli.py -q
```

Expected output:

```text
.........                                                                                    [100%]
9 passed in 0.27s
```

**Step 5.** Analyze a fixture log folder (no Zeek needed) and look at the start of the report:

```bash
maxguard analyze tests/fixtures/zeek/telnet --no-ai | head -n 12
```

Expected output:

```text
{
  "ai": {
    "dropped_sentences": 0,
    "explained": 0,
    "model": null,
    "reason": null,
    "status": "disabled"
  },
  "assets": [
    {
      "finding_count": 1,
      "first_seen": 1791250284.287571,
```

**Step 6.** **The Week 2 demo command.** A capture needs Zeek, so it runs inside the engine image from JAI-04 (build it first with `docker build -f docker/Dockerfile -t maxguard:dev .`):

```bash
docker run --rm --network none -v "$PWD/tests/pcaps:/pcaps:ro" maxguard:dev maxguard analyze /pcaps/telnet.pcap --no-ai -o /tmp/r.json && echo ok
```

Expected output:

```text
maxguard: 1 finding(s), report written to /tmp/r.json
ok
```

*Recorded by running the same command inside `zeek/zeek:9.0.0` with MaxGuard's Python packages added, because building the image needs Debian's package servers, which the planning environment could not reach. That image has no Suricata, so only Zeek ran; the real image runs both and must report the same one finding.*

**Step 7.** Commit, push, and open the pull request:

```bash
git add -A
git status          # only this task's files: nothing from .venv/, data/ or lab/captures/
git commit -m "feat: maxguard analyze command with JSON output (FIO-04)"
git push -u origin HEAD
```

`HEAD` means "the branch I am on", so you do not have to retype its name. Open the repository on github.com: a yellow bar shows your branch with a **Compare & pull request** button. Click it, keep the title `feat: maxguard analyze command with JSON output (FIO-04)`, fill in the template (paste the real output of the commands above under **How I tested it**), write `Closes #<issue number>` (this task's issue), and pick **@JWinborne1** under **Reviewers**. Click **Create pull request**, then fix anything CI or the reviewer finds with new commits on the same branch.

#### How to test

`pytest` passes; the report starts with `"ai"` because keys are sorted; the demo prints `maxguard: 1 finding(s), report written to /tmp/r.json` and `ok`.

#### What you just did and why

The CLI is the thinnest possible layer: it checks the input, calls `analyze()`, and writes the result. All the real work stays in the pipeline, so the dashboard (JAI-07) gives exactly the same report. Status messages go to stderr and the report to stdout, so `maxguard analyze x > report.json` stays valid JSON. Zeek's logs are written to a temporary folder that is deleted afterwards, so no copy of the user's traffic is left on disk.

#### Pull request checklist

- [ ] `ruff check .` prints `All checks passed!`
- [ ] `pytest -m "not integration" -q` passes on your laptop
- [ ] The pull request title has the form `type: summary (TASK-ID)` and the body says `Closes #<issue number>`
- [ ] No secrets, passwords, email addresses, personal data, or captures from a real network (CLAUDE.md rule 6)
- [ ] Any new dependency has a row in `docs/DEPENDENCIES.md` with its license
- [ ] CI is green and your reviewer approved
- [ ] `maxguard analyze tests/fixtures/zeek/telnet --no-ai` works in your venv
- [ ] The demo command works in the engine image

### FIO-05: CLI: CSV and HTML reports, and --offline

**Due:** Week 4 (due Fri Nov 6) · **Milestone:** `W4 Full offline report` · **Needs first:** [FIO-04](#fio-04-the-maxguard-command-first-version-json-reports), [AMO-03](amory.md#amo-03-report-export-json-csv-and-html), [JON-03](jonattan.md#jon-03-offline-guard-make-accidental-network-access-fail-loudly) · **Kind:** code, tested

**Issue labels:** `type:task` `phase:alpha` `owner:fiona` `area:engine`

#### Goal

Finish the CLI for the alpha: `--format` (json, csv, or html) uses Amory's report exporters (AMO-03), and `--offline` turns on Jonattan's offline guard (JON-03) before anything else runs, so nothing in the analysis can reach the network.

#### Prerequisites

AMO-03 (report export) and JON-03 (offline guard) are merged.

#### Steps

**Step 1.** Update `main` and create your branch for this task (one branch per task):

```bash
cd ~/projects/maxguard
source .venv/bin/activate
git checkout main && git pull
git checkout -b fiona/cli-formats-offline
```

If `source .venv/bin/activate` fails, you have not made the virtual environment yet: do Week 0 section 0.11 first.

**Step 2.** Replace `cli/main.py` with the final version:

```python
"""MaxGuard command line (Fiona).

    maxguard analyze INPUT [-o report.json] [--no-ai] [--offline]
                           [--frameworks 'PCI DSS,NIST SP 800-53'] [--format json|csv|html]

INPUT is a .pcap/.pcapng capture, or a folder/.zip/.tar.gz of Zeek logs.
Run it as `maxguard ...` (console script) or `python -m cli.main ...`.

Exit codes, so scripts and CI can react without reading the text:
    0  the report was written
    2  bad input: missing file, not a capture or Zeek log folder, unknown framework
       (argparse also uses 2 for a wrong option)
    3  Zeek failed on the capture
"""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

from maxguard.mapping.loader import ATTACK, load_all
from maxguard.pipeline import UnsupportedInput, analyze, mappings_dir
from maxguard.zeek.runner import ZeekError

EXIT_OK = 0
EXIT_BAD_INPUT = 2
EXIT_ZEEK_ERROR = 3

FORMATS = ("json", "csv", "html")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="maxguard", description="Find security weaknesses in network traffic, offline.")
    commands = parser.add_subparsers(dest="command", required=True)

    cmd = commands.add_parser(
        "analyze", help="analyze a capture file or a folder/archive of Zeek logs")
    cmd.add_argument("input", type=Path,
                     help=".pcap/.pcapng file, or a folder, .zip or .tar.gz of Zeek logs")
    cmd.add_argument("-o", "--output", type=Path,
                     help="write the report to this file (default: print it)")
    cmd.add_argument("--no-ai", action="store_true",
                     help="skip the AI explanations (no Ollama needed)")
    cmd.add_argument("--offline", action="store_true",
                     help="block all network access except this machine and the local Ollama")
    cmd.add_argument("--frameworks",
                     help="comma-separated list, e.g. 'PCI DSS,NIST SP 800-53' (default: all)")
    cmd.add_argument("--format", choices=FORMATS, default="json",
                     help="report format (default: json)")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)  # a wrong option: argparse prints usage, exits with 2
    if args.command == "analyze":
        return run_analyze(args)
    parser.error(f"unknown command {args.command!r}")  # exits with 2


def run_analyze(args: argparse.Namespace) -> int:
    """The `analyze` command: check the input, run the pipeline, write the report."""
    if not args.input.exists():
        return fail(f"{args.input}: no such file or folder", EXIT_BAD_INPUT)

    frameworks = parse_frameworks(args.frameworks)
    unknown = unknown_frameworks(frameworks)
    if unknown:
        # Without this check a typo ("PCI-DSS") would silently give a report with no controls.
        return fail(f"unknown framework(s): {', '.join(unknown)}. "
                    f"Known: {', '.join(known_frameworks())}", EXIT_BAD_INPUT)

    if args.offline:
        enable_offline_guard()  # first, so no Python code in the analysis can go online

    try:
        # Zeek's logs go to a temporary folder that is deleted afterwards, so no
        # copy of the user's traffic is left behind on disk.
        with tempfile.TemporaryDirectory(prefix="maxguard-") as workdir:
            report = analyze(args.input, workdir, frameworks=frameworks,
                             explain=not args.no_ai)
    except UnsupportedInput as error:
        return fail(str(error), EXIT_BAD_INPUT)
    except ZeekError as error:
        return fail(f"Zeek failed: {error}", EXIT_ZEEK_ERROR)

    write_report(render(report, args.format), args.output)
    if args.output:
        # Status goes to stderr, so stdout stays clean when the report is printed.
        print(f"maxguard: {len(report['findings'])} finding(s), report written to "
              f"{args.output}", file=sys.stderr)
    return EXIT_OK


def parse_frameworks(text: str | None) -> list[str] | None:
    """'PCI DSS, NIST SP 800-53' -> ['PCI DSS', 'NIST SP 800-53']. None means "all"."""
    if not text:
        return None
    names = [name.strip() for name in text.split(",")]
    return [name for name in names if name] or None


def known_frameworks() -> list[str]:
    """Compliance framework names from mappings/*.yaml, e.g. ['CISA CPG', 'CJIS', ...].

    MITRE ATT&CK is left out: its techniques are always added, so it is not
    something to select (and selecting only it would hide every control).
    """
    return sorted({fw["framework"] for fw in load_all(mappings_dir())} - {ATTACK})


def unknown_frameworks(selected: list[str] | None) -> list[str]:
    if not selected:
        return []
    known = set(known_frameworks())
    return [name for name in selected if name not in known]


def enable_offline_guard() -> None:
    # Imported here, not at the top: only --offline needs these modules.
    from maxguard import offline
    from maxguard.ai.ollama_client import ollama_url

    offline.enable(ollama_url())


def render(report: dict, fmt: str) -> str:
    """The report as JSON, CSV or HTML text."""
    # Imported here, not at the top: the analysis itself does not need the
    # export code, so `analyze` keeps working even while report.py changes.
    from maxguard import report as export

    writers = {"json": export.to_json, "csv": export.to_csv, "html": export.to_html}
    return writers[fmt](report)


def write_report(text: str, output: Path | None) -> None:
    if output is None:
        sys.stdout.write(text)
    else:
        output.write_text(text, encoding="utf-8")


def fail(message: str, exit_code: int) -> int:
    print(f"maxguard: error: {message}", file=sys.stderr)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
```

The JSON output is byte-for-byte the same as before: `report.to_json` uses the same settings as the first version's `to_json`.

**Step 3.** Replace `tests/unit/test_cli.py`:

```python
"""CLI tests (Fiona): `maxguard analyze` on a fixture log folder, and exit codes.

These call cli.main.main([...]) directly instead of starting a new process:
same code path, much faster. A fixture *log folder* goes through
ZeekLogAdapter, so no Zeek is needed, and --no-ai means no Ollama is needed.
"""

import json
from pathlib import Path

import pytest

from cli import main as cli
from maxguard.zeek.runner import ZeekError

REPO = Path(__file__).resolve().parents[2]
TELNET_LOGS = REPO / "tests" / "fixtures" / "zeek" / "telnet"


def test_analyze_log_folder_writes_json_report(tmp_path, capsys):
    out = tmp_path / "report.json"

    code = cli.main(["analyze", str(TELNET_LOGS), "--no-ai", "-o", str(out)])

    assert code == cli.EXIT_OK
    report = json.loads(out.read_text())
    assert report["schema"] == "maxguard.report/2"
    assert report["input"]["adapter"] == "zeek-logs"
    assert report["ai"]["status"] == "disabled"
    assert [f["rule_id"] for f in report["findings"]] == ["cleartext.telnet"]
    # mappings/attack.yaml is applied: Telnet passwords can be sniffed.
    assert "T1040" in [t["technique_id"] for t in report["findings"][0]["attack"]]
    assert "1 finding(s)" in capsys.readouterr().err


def test_without_output_file_the_report_goes_to_stdout(capsys):
    code = cli.main(["analyze", str(TELNET_LOGS), "--no-ai"])

    assert code == cli.EXIT_OK
    report = json.loads(capsys.readouterr().out)
    assert report["findings"][0]["rule_id"] == "cleartext.telnet"


def test_same_input_gives_byte_identical_reports(tmp_path):
    first, second = tmp_path / "first.json", tmp_path / "second.json"
    cli.main(["analyze", str(TELNET_LOGS), "--no-ai", "-o", str(first)])
    cli.main(["analyze", str(TELNET_LOGS), "--no-ai", "-o", str(second)])
    assert first.read_bytes() == second.read_bytes()


def test_frameworks_option_keeps_only_those_controls(tmp_path):
    out = tmp_path / "report.json"

    cli.main(["analyze", str(TELNET_LOGS), "--no-ai", "-o", str(out),
              "--frameworks", "NIST SP 800-53"])

    finding = json.loads(out.read_text())["findings"][0]
    assert finding["controls"], "NIST maps cleartext.telnet"
    assert {c["framework"] for c in finding["controls"]} == {"NIST SP 800-53"}
    assert finding["attack"], "ATT&CK techniques are always added"


@pytest.mark.parametrize(("fmt", "start"), [("csv", "finding_id,rule_id"),
                                            ("html", "<!doctype html>")])
def test_csv_and_html_formats(tmp_path, fmt, start):
    out = tmp_path / f"report.{fmt}"

    code = cli.main(["analyze", str(TELNET_LOGS), "--no-ai", "--format", fmt, "-o", str(out)])

    assert code == cli.EXIT_OK
    assert out.read_text().startswith(start)


# ---- exit codes ------------------------------------------------------------

def test_text_file_is_bad_input(tmp_path, capsys):
    notes = tmp_path / "notes.txt"
    notes.write_text("hello\n")

    assert cli.main(["analyze", str(notes), "--no-ai"]) == cli.EXIT_BAD_INPUT
    assert "not a pcap/pcapng file" in capsys.readouterr().err


def test_missing_input_is_bad_input(tmp_path):
    missing = tmp_path / "missing.pcap"
    assert cli.main(["analyze", str(missing), "--no-ai"]) == cli.EXIT_BAD_INPUT


def test_unknown_framework_is_bad_input(capsys):
    code = cli.main(["analyze", str(TELNET_LOGS), "--no-ai", "--frameworks", "PCI-DSS"])

    assert code == cli.EXIT_BAD_INPUT
    assert "unknown framework(s): PCI-DSS" in capsys.readouterr().err


def test_wrong_option_exits_with_2():
    with pytest.raises(SystemExit) as stop:  # argparse exits by itself
        cli.main(["analyze", str(TELNET_LOGS), "--format", "pdf"])
    assert stop.value.code == cli.EXIT_BAD_INPUT


def test_zeek_failure_exits_with_3(monkeypatch, tmp_path, capsys):
    def zeek_fails(*args, **kwargs):
        raise ZeekError("problem with trace file")

    monkeypatch.setattr(cli, "analyze", zeek_fails)
    capture = tmp_path / "broken.pcap"
    capture.write_bytes(b"\xd4\xc3\xb2\xa1 not really a capture")

    assert cli.main(["analyze", str(capture), "--no-ai"]) == cli.EXIT_ZEEK_ERROR
    assert "Zeek failed: problem with trace file" in capsys.readouterr().err


# ---- --offline ---------------------------------------------------------------

def test_offline_turns_the_guard_on_before_the_analysis(monkeypatch, tmp_path):
    from maxguard import offline

    calls = []
    # Record the calls instead of really enabling the guard: enable() would
    # look up the Ollama host name, and unit tests never touch the network.
    monkeypatch.setattr(offline, "enable", lambda url, *rest: calls.append(("offline", url)))
    real_analyze = cli.analyze

    def recording_analyze(*args, **kwargs):
        calls.append(("analyze", None))
        return real_analyze(*args, **kwargs)

    monkeypatch.setattr(cli, "analyze", recording_analyze)
    monkeypatch.setenv("OLLAMA_HOST", "http://ollama:11434")

    code = cli.main(["analyze", str(TELNET_LOGS), "--no-ai", "--offline",
                     "-o", str(tmp_path / "report.json")])

    assert code == cli.EXIT_OK
    assert calls == [("offline", "http://ollama:11434"), ("analyze", None)]
```

**Step 4.** Run them:

```bash
pytest tests/unit/test_cli.py -q
```

Expected output:

```text
............                                                                                 [100%]
12 passed in 0.41s
```

**Step 5.** Try the CSV format:

```bash
maxguard analyze tests/fixtures/zeek/telnet --no-ai --format csv | head -n 3 | cut -c1-150
```

Expected output:

```text
finding_id,rule_id,severity,title,src_ip,dst_ip,dst_port,protocol,count,first_seen,last_seen,framework,version,control_id,control_title,rationale,evid
c6823b232c932762,cleartext.telnet,high,Telnet session in cleartext,172.18.0.3,172.18.0.2,23,telnet,1,2026-10-06T01:31:25Z,2026-10-06T01:31:25Z,NIST SP
c6823b232c932762,cleartext.telnet,high,Telnet session in cleartext,172.18.0.3,172.18.0.2,23,telnet,1,2026-10-06T01:31:25Z,2026-10-06T01:31:25Z,NIST SP
```

**Step 6.** Commit, push, and open the pull request:

```bash
git add -A
git status          # only this task's files: nothing from .venv/, data/ or lab/captures/
git commit -m "feat: CLI --format csv/html and --offline (FIO-05)"
git push -u origin HEAD
```

`HEAD` means "the branch I am on", so you do not have to retype its name. Open the repository on github.com: a yellow bar shows your branch with a **Compare & pull request** button. Click it, keep the title `feat: CLI --format csv/html and --offline (FIO-05)`, fill in the template (paste the real output of the commands above under **How I tested it**), write `Closes #<issue number>` (this task's issue), and pick **@JWinborne1** under **Reviewers**. Click **Create pull request**, then fix anything CI or the reviewer finds with new commits on the same branch.

#### How to test

`pytest` passes, including the test that proves the guard is switched on *before* the analysis starts.

#### What you just did and why

Order matters for `--offline`: a guard switched on after the analysis started could miss a connection made during it. The test records the order of the calls to prove it. The exporters are imported only when needed, so a bug in the HTML exporter can never stop an analysis from running.

#### Pull request checklist

- [ ] `ruff check .` prints `All checks passed!`
- [ ] `pytest -m "not integration" -q` passes on your laptop
- [ ] The pull request title has the form `type: summary (TASK-ID)` and the body says `Closes #<issue number>`
- [ ] No secrets, passwords, email addresses, personal data, or captures from a real network (CLAUDE.md rule 6)
- [ ] Any new dependency has a row in `docs/DEPENDENCIES.md` with its license
- [ ] CI is green and your reviewer approved

## Spring 2027: v2.0

### FIO-06: Decoys: fake services on their own IP address

**Due:** Spring S9-S11 (due Fri Apr 16, 2027) · **Milestone:** `S9-S11 Detect more` · **Needs first:** [JAI-07](jaiden.md#jai-07-the-api-uploads-alerts-events-live-updates-sensor-ingest), [JON-04](jonattan.md#jon-04-home-mode-text-for-every-rule) · **Kind:** code, tested

**Issue labels:** `type:task` `phase:spring` `owner:fiona` `area:engine` `needs-hardware`

> **Needs hardware.** Steps that use the Raspberry Pi, the switch or other devices were not run during planning; they are marked *not run — verify on hardware*.

#### Goal

Add decoys (canaries): fake Telnet, FTP and printer web services on their own IP address that nothing legitimate should ever contact, plus rule `decoy.contact`, which turns any contact into a critical finding.

#### Prerequisites

JAI-07 is merged. The new rule ID needs the Security Lead's approval: ask Ahmad in the issue first.

#### Steps

**Step 1.** Update `main` and create your branch for this task (one branch per task):

```bash
cd ~/projects/maxguard
source .venv/bin/activate
git checkout main && git pull
git checkout -b fiona/decoys
```

If `source .venv/bin/activate` fails, you have not made the virtual environment yet: do Week 0 section 0.11 first.

**Step 2.** Create `maxguard/decoy/__init__.py` and the decoy itself, `maxguard/decoy/service.py`:

```python
"""Decoys: fake services on their own IP address (Fiona, FIO-06).

A decoy only answers connections made to it and writes one line per connection
to decoy.log. Rule decoy.contact (maxguard/rules/decoy.py) turns those lines
into critical findings. Decoys are not sensors (CLAUDE.md rule 5).
"""
```

```python
"""Fake Telnet, FTP and printer web services (Fiona, FIO-06).

Nothing legitimate on the network has a reason to contact these services, so
every connection is worth an alert. For each connection the decoy:

1. sends a fake banner (Telnet and FTP speak first; HTTP answers a request),
2. reads at most READ_LIMIT bytes, waiting at most `timeout` seconds,
3. writes one JSON line to decoy.log and closes the connection.

Safety (CLAUDE.md rule 5): the decoy only answers. This module never opens a
connection, never resolves a name and never sends anything except its banner
to the client that connected. It runs in its own container with its own IP
address, never on the sensor's capture interface.
"""

from __future__ import annotations

import asyncio
import functools
import json
import time
from collections.abc import Callable
from pathlib import Path

DEFAULT_PORTS = {"telnet": 23, "ftp": 21, "http": 80}
DEFAULT_TIMEOUT = 5.0  # seconds; a slow or silent client cannot keep a connection open
READ_LIMIT = 1024  # bytes; we never buffer more than this from one client
LOGGED_BYTES = 64  # bytes of what the client sent that go into decoy.log (as hex)

PRINTER_PAGE = (
    b"<!doctype html><html><head><title>Printer admin</title></head>"
    b"<body><h1>Printer admin</h1><form method=post>"
    b"<input name=user><input name=pass type=password><button>Log in</button>"
    b"</form></body></html>"
)
HTTP_RESPONSE = (
    b"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n"
    b"Content-Length: " + str(len(PRINTER_PAGE)).encode() + b"\r\n"
    b"Connection: close\r\n\r\n" + PRINTER_PAGE
)
# Sent as soon as a client connects (these protocols make the server speak first).
GREETINGS = {"telnet": b"login: ", "ftp": b"220 FTP server ready\r\n"}
# Sent after the client has said something (HTTP waits for the request).
REPLIES = {"http": HTTP_RESPONSE}


def parse_ports(text: str) -> dict[str, int]:
    """Turn "telnet=23,ftp=21,http=80" into {"telnet": 23, "ftp": 21, "http": 80}."""
    ports: dict[str, int] = {}
    for item in text.split(","):
        name, _, port = item.strip().partition("=")
        if name not in GREETINGS and name not in REPLIES:
            raise ValueError(f"unknown decoy service {name!r} (use telnet, ftp or http)")
        if not port.isdigit() or not 0 <= int(port) <= 65535:
            raise ValueError(f"bad port for {name}: {port!r}")
        ports[name] = int(port)
    return ports


def contact_record(service: str, peer: tuple, local: tuple, data: bytes, ts: float) -> dict:
    """The decoy.log line for one connection."""
    return {
        "ts": ts,
        "service": service,
        "src_ip": peer[0],
        "src_port": peer[1],
        "dst_ip": local[0],
        "dst_port": local[1],
        "first_bytes_hex": data[:LOGGED_BYTES].hex(),
    }


def append_line(log_path: Path, record: dict) -> None:
    # asyncio runs one handler at a time, so lines from two clients never mix.
    with log_path.open("a") as f:
        f.write(json.dumps(record, sort_keys=True) + "\n")


async def read_some(reader: asyncio.StreamReader, timeout: float) -> bytes:
    """Whatever the client sends first, capped at READ_LIMIT bytes; b"" if it stays silent."""
    try:
        return await asyncio.wait_for(reader.read(READ_LIMIT), timeout)
    except (TimeoutError, OSError):  # silent client, or it reset the connection
        return b""


async def send(writer: asyncio.StreamWriter, data: bytes) -> None:
    """Send data; a client that already left is not an error for a decoy."""
    try:
        writer.write(data)
        await writer.drain()
    except OSError:
        pass


async def close(writer: asyncio.StreamWriter) -> None:
    writer.close()
    try:
        await writer.wait_closed()
    except OSError:
        pass


async def handle(service: str, reader: asyncio.StreamReader, writer: asyncio.StreamWriter,
                 *, log_path: Path, timeout: float, clock: Callable[[], float]) -> None:
    """Answer one connection, log it, close it."""
    ts = clock()  # the time the client connected
    # (ip, port). IPv6 adds two more fields, which we drop. None if the client already left.
    peer = (writer.get_extra_info("peername") or ("", 0))[:2]
    local = (writer.get_extra_info("sockname") or ("", 0))[:2]
    data = b""
    try:
        if service in GREETINGS:
            await send(writer, GREETINGS[service])
        data = await read_some(reader, timeout)
        if service in REPLIES and data:
            await send(writer, REPLIES[service])
    finally:
        # Log even if something above failed: the contact itself is the evidence.
        append_line(log_path, contact_record(service, peer, local, data, ts))
        await close(writer)


async def start(ports: dict[str, int], log_path: Path, *, host: str = "0.0.0.0",
                timeout: float = DEFAULT_TIMEOUT,
                clock: Callable[[], float] = time.time) -> list[asyncio.Server]:
    """Start one listener per service. Port 0 picks a free port (used by the tests)."""
    servers = []
    for service, port in sorted(ports.items()):
        # partial() fixes everything except (reader, writer), which asyncio passes in.
        on_connect = functools.partial(handle, service, log_path=log_path, timeout=timeout,
                                       clock=clock)
        servers.append(await asyncio.start_server(on_connect, host, port))
    return servers


async def serve_forever(ports: dict[str, int], log_path: Path, *, host: str = "0.0.0.0",
                        timeout: float = DEFAULT_TIMEOUT) -> None:
    servers = await start(ports, log_path, host=host, timeout=timeout)
    for service, server in zip(sorted(ports), servers, strict=True):  # start() sorts too
        for sock in server.sockets:
            address, port = sock.getsockname()[:2]
            print(f"decoy {service} listening on {address}:{port}", flush=True)
    await asyncio.gather(*(server.serve_forever() for server in servers))
```

Telnet and FTP send their banner first (those servers speak first); HTTP waits for the request and answers with a page titled "Printer admin". Every connection writes one JSON line to `decoy.log` in a `finally` block, so garbage, silence or an early hang-up is still logged: the contact itself is the evidence. It reads at most 1024 bytes, keeps the first 64 as hex, and waits at most 5 seconds. The decoy only answers; it never opens a connection (CLAUDE.md rule 5).

**Step 3.** Create `maxguard/decoy/__main__.py`, so `python -m maxguard.decoy` starts it with settings from environment variables:

```python
"""Run the decoys: python -m maxguard.decoy (Fiona, FIO-06).

Settings come from environment variables, so docker/decoy-compose.yaml can set them:
  MAXGUARD_DECOY_PORTS    services and ports, default "telnet=23,ftp=21,http=80"
  MAXGUARD_DECOY_LOG      where decoy.log goes, default "decoy.log"
  MAXGUARD_DECOY_HOST     address to listen on, default "0.0.0.0" (all of the container's)
  MAXGUARD_DECOY_TIMEOUT  seconds to wait for a client, default 5
"""

from __future__ import annotations

import asyncio
import os
from pathlib import Path

from maxguard.decoy.service import DEFAULT_TIMEOUT, parse_ports, serve_forever


def main() -> None:
    ports = parse_ports(os.environ.get("MAXGUARD_DECOY_PORTS", "telnet=23,ftp=21,http=80"))
    log_path = Path(os.environ.get("MAXGUARD_DECOY_LOG", "decoy.log"))
    host = os.environ.get("MAXGUARD_DECOY_HOST", "0.0.0.0")
    timeout = float(os.environ.get("MAXGUARD_DECOY_TIMEOUT", DEFAULT_TIMEOUT))
    log_path.parent.mkdir(parents=True, exist_ok=True)
    asyncio.run(serve_forever(ports, log_path, host=host, timeout=timeout))


if __name__ == "__main__":
    main()
```

**Step 4.** Create the rule `maxguard/rules/decoy.py`. Do **not** add it to `maxguard/rules/__init__.py` until Ahmad approves the rule ID; importing the module registers it, which is how the tests use it. Its Home text and mapping rows come from Jonattan and Amory:

```python
"""Rule decoy.contact (Fiona, FIO-06, proposed for v2.0 spring).

Each line of decoy.log (written by maxguard/decoy/service.py) records one
connection to a decoy. Nothing legitimate has a reason to contact a decoy, so
every line becomes a critical finding. The evidence is the decoy.log line
itself (its record_id), so the AI can cite it.

Not yet in maxguard/rules/__init__.py: the rule ID needs the Security Lead's
approval first. Until then it registers only when imported, for example in a test:
    from maxguard.rules.decoy import decoy_contact
"""

from __future__ import annotations

from pathlib import Path

from maxguard.adapters.base import read_log
from maxguard.ids import evidence
from maxguard.models import Finding
from maxguard.rules.base import rule

RULE_ID = "decoy.contact"
LOG_NAME = "decoy.log"


def contact_finding(rec: dict) -> Finding:
    ev = evidence(LOG_NAME, rec)  # uid is "": the decoy is not a Zeek connection
    return Finding(rule_id=RULE_ID, title="Someone contacted a decoy", severity="critical",
                   src_ip=rec["src_ip"], dst_ip=rec["dst_ip"], dst_port=int(rec["dst_port"]),
                   protocol=rec.get("service") or "tcp", first_seen=ev.ts, last_seen=ev.ts,
                   source="decoy",
                   details={"service": rec.get("service"),
                            "first_bytes_hex": rec.get("first_bytes_hex", "")},
                   evidence=[ev])


@rule(RULE_ID)
def decoy_contact(log_dir: Path) -> list[Finding]:
    """One finding per decoy.log line (merge() then counts repeats per src/dst/port)."""
    return [contact_finding(rec) for rec in read_log(log_dir, LOG_NAME)]
```

**Step 5.** Create the tests `tests/unit/test_decoy.py`. "Never connects out" is tested by wrapping `socket.socket.connect`: after a client talks to the decoy, the only connection in the process is the test's own:

```python
"""Tests for the decoy service and rule decoy.contact (Fiona, FIO-06).

The decoy listens on 127.0.0.1 with port 0 (the system picks a free port), so
the tests need no root, no Docker and no network.
"""

from __future__ import annotations

import asyncio
import json
import socket

import pytest

from maxguard.decoy import service
from maxguard.ids import record_id
from maxguard.rules.base import RULES, merge

# Importing the module registers decoy.contact. It is not in maxguard/rules/__init__.py
# yet, because a new rule ID needs the Security Lead's approval.
from maxguard.rules.decoy import decoy_contact

FIXED_TS = 1791250284.5  # the tests pass a fixed clock, so decoy.log is predictable
LINE = {"ts": FIXED_TS, "service": "telnet", "src_ip": "192.0.2.10", "src_port": 50000,
        "dst_ip": "192.0.2.250", "dst_port": 23, "first_bytes_hex": "726f6f740d0a"}


@pytest.fixture
def connects(monkeypatch):
    """Record every outgoing connection made in this process (the test client's too)."""
    made: list[tuple] = []
    real_connect, real_connect_ex = socket.socket.connect, socket.socket.connect_ex

    def connect(sock, address):
        made.append(tuple(address[:2]))
        return real_connect(sock, address)

    def connect_ex(sock, address):
        made.append(tuple(address[:2]))
        return real_connect_ex(sock, address)

    monkeypatch.setattr(socket.socket, "connect", connect)
    monkeypatch.setattr(socket.socket, "connect_ex", connect_ex)
    return made


async def talk(port: int, send: bytes, *, close_early: bool = False) -> bytes:
    """Connect like an attacker would: read the banner, send something, read the answer."""
    reader, writer = await asyncio.open_connection("127.0.0.1", port)
    if close_early:
        writer.close()
        return b""
    if send:
        writer.write(send)
        await writer.drain()
    answer = await reader.read()  # until the decoy closes the connection
    writer.close()
    return answer


async def run_decoys(log_path, clients: list[tuple[str, bytes]]) -> list[bytes]:
    servers = await service.start({"telnet": 0, "ftp": 0, "http": 0}, log_path,
                                  host="127.0.0.1", timeout=0.3, clock=lambda: FIXED_TS)
    ports = {name: srv.sockets[0].getsockname()[1]
             for name, srv in zip(sorted(["telnet", "ftp", "http"]), servers, strict=True)}
    try:
        return [await talk(ports[name], data) for name, data in clients]
    finally:
        for srv in servers:
            srv.close()
            await srv.wait_closed()


def read_lines(path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines()]


def test_service_logs_a_connection_and_never_connects_out(tmp_path, connects):
    log_path = tmp_path / "decoy.log"
    answers = asyncio.run(run_decoys(log_path, [("telnet", b"root\r\n")]))

    assert answers == [b"login: "]
    [line] = read_lines(log_path)
    assert line["ts"] == FIXED_TS
    assert line["service"] == "telnet"
    assert line["src_ip"] == "127.0.0.1" and line["dst_ip"] == "127.0.0.1"
    assert isinstance(line["src_port"], int) and isinstance(line["dst_port"], int)
    assert bytes.fromhex(line["first_bytes_hex"]) == b"root\r\n"
    # The only connection in this process is the test's own, to the decoy.
    assert connects == [("127.0.0.1", line["dst_port"])]


def test_each_service_has_its_banner(tmp_path):
    answers = asyncio.run(run_decoys(tmp_path / "decoy.log", [
        ("ftp", b"USER admin\r\n"), ("http", b"GET / HTTP/1.1\r\nHost: printer\r\n\r\n")]))
    assert answers[0] == b"220 FTP server ready\r\n"
    assert answers[1].startswith(b"HTTP/1.1 200 OK")
    assert b"<title>Printer admin</title>" in answers[1]


def test_only_the_first_64_bytes_are_logged(tmp_path):
    log_path = tmp_path / "decoy.log"
    asyncio.run(run_decoys(log_path, [("http", b"A" * 5000)]))
    [line] = read_lines(log_path)
    assert bytes.fromhex(line["first_bytes_hex"]) == b"A" * 64


def test_silent_client_is_logged_after_the_timeout(tmp_path):
    log_path = tmp_path / "decoy.log"
    asyncio.run(run_decoys(log_path, [("ftp", b"")]))  # connects, sends nothing
    [line] = read_lines(log_path)
    assert line["first_bytes_hex"] == ""


def test_garbage_and_early_close_do_not_stop_the_decoy(tmp_path):
    log_path = tmp_path / "decoy.log"

    async def scenario():
        servers = await service.start({"telnet": 0}, log_path, host="127.0.0.1",
                                      timeout=0.3, clock=lambda: FIXED_TS)
        port = servers[0].sockets[0].getsockname()[1]
        await talk(port, bytes(range(256)) * 8)  # binary garbage, not valid Telnet
        await talk(port, b"", close_early=True)  # hangs up before the banner is read
        answer = await talk(port, b"admin\r\n")  # the decoy still answers afterwards
        servers[0].close()
        await servers[0].wait_closed()
        return answer

    assert asyncio.run(scenario()) == b"login: "
    assert len(read_lines(log_path)) == 3


def test_parse_ports():
    assert service.parse_ports("telnet=2323, http=8080") == {"telnet": 2323, "http": 8080}
    with pytest.raises(ValueError):
        service.parse_ports("ssh=22")
    with pytest.raises(ValueError):
        service.parse_ports("ftp=21x")


def test_rule_turns_a_decoy_log_line_into_one_finding(tmp_path):
    (tmp_path / "decoy.log").write_text(json.dumps(LINE) + "\n")
    [finding] = decoy_contact(tmp_path)
    assert finding.rule_id == "decoy.contact"
    assert finding.severity == "critical"
    assert finding.source == "decoy"
    assert (finding.src_ip, finding.dst_ip, finding.dst_port) == ("192.0.2.10", "192.0.2.250", 23)
    assert finding.protocol == "telnet"
    assert finding.first_seen == finding.last_seen == FIXED_TS
    # The evidence ID is the hash of the decoy.log line, so the AI can cite it.
    assert finding.evidence[0].log == "decoy.log"
    assert finding.evidence[0].record_id == record_id("decoy.log", LINE)


def test_repeated_contacts_merge_into_one_finding(tmp_path):
    second = {**LINE, "ts": FIXED_TS + 60, "src_port": 50001}
    (tmp_path / "decoy.log").write_text(json.dumps(LINE) + "\n" + json.dumps(second) + "\n")
    [finding] = merge(decoy_contact(tmp_path))
    assert finding.count == 2
    assert (finding.first_seen, finding.last_seen) == (FIXED_TS, FIXED_TS + 60)


def test_no_decoy_log_means_no_findings(tmp_path):
    assert decoy_contact(tmp_path) == []


def test_rule_registers_when_imported():
    assert RULES["decoy.contact"] is decoy_contact


def test_service_end_to_end_with_the_rule(tmp_path):
    asyncio.run(run_decoys(tmp_path / "decoy.log", [("http", b"GET / HTTP/1.1\r\n\r\n")]))
    [finding] = decoy_contact(tmp_path)
    assert finding.protocol == "http" and finding.src_ip == "127.0.0.1"
```

Run them:

```bash
pytest tests/unit/test_decoy.py -q
```

Expected output:

```text
...........                                                                                  [100%]
11 passed in 0.39s
```

**Step 6.** Create `docker/decoy-compose.yaml`. `macvlan` gives the decoy its own MAC and IP address on your LAN; the parent must be the console's normal wired network card, never the sensor's capture port:

```yaml
# MaxGuard decoys (Fiona, FIO-06): fake Telnet, FTP and printer web services on
# their OWN address on your LAN. Nothing legitimate should ever connect to them,
# so every connection becomes a critical "decoy.contact" alert.
#
# Rules (CLAUDE.md rule 5):
#   - The decoy has its own IP address on a macvlan network, so it looks like a
#     separate device on the LAN (its own MAC address too).
#   - It only answers connections made to it; it never opens one.
#   - NEVER use the sensor's capture interface as the parent: that port has no IP
#     address and must only listen. Use the console's normal network card.
#
# Settings (environment variables or a .env file next to the command you run):
#   MAXGUARD_DECOY_PARENT   the console's normal LAN network card (default eth0;
#                           see yours with: ip -br link). Use a wired card: the
#                           card and switch must accept several MAC addresses on
#                           one port ("promiscuous mode" in Docker's macvlan docs),
#                           which Wi-Fi often cannot do.
#   MAXGUARD_DECOY_SUBNET   your LAN, e.g. 192.168.1.0/24 (required)
#   MAXGUARD_DECOY_GATEWAY  your router's address, e.g. 192.168.1.1 (required)
#   MAXGUARD_DECOY_IP       a FREE address for the decoy, outside the router's
#                           DHCP range, e.g. 192.168.1.250 (required)
#
# Check:  MAXGUARD_DECOY_SUBNET=192.168.1.0/24 MAXGUARD_DECOY_GATEWAY=192.168.1.1 \
#         MAXGUARD_DECOY_IP=192.168.1.250 docker compose -f docker/decoy-compose.yaml config
# Start:  (same variables) docker compose -f docker/decoy-compose.yaml up -d
# Stop:   docker compose -f docker/decoy-compose.yaml down
#
# The console itself cannot reach a macvlan container ("a restriction in the Linux
# kernel", Docker's macvlan docs); test from another device such as a laptop.
name: maxguard-decoy

services:
  decoy:
    image: maxguard:2.0.0a0 # the same image as the console; it contains maxguard.decoy
    command: ["python", "-m", "maxguard.decoy"]
    environment:
      MAXGUARD_DECOY_PORTS: "telnet=23,ftp=21,http=80"
      MAXGUARD_DECOY_LOG: /data/decoy.log
    volumes:
      - maxguard-decoy-data:/data # decoy.log lives here
    networks:
      decoy-lan:
        ipv4_address: ${MAXGUARD_DECOY_IP:?set MAXGUARD_DECOY_IP to a free LAN address}
    # Least privilege: the image's non-root user, no Linux capabilities, a
    # read-only root file system. Ports 21/23/80 still work without root
    # because this sysctl lets any user of this container use low ports.
    read_only: true
    cap_drop: [ALL]
    security_opt: ["no-new-privileges:true"]
    sysctls:
      net.ipv4.ip_unprivileged_port_start: "0"
    restart: unless-stopped

networks:
  decoy-lan:
    name: maxguard-decoy-lan
    driver: macvlan
    driver_opts:
      parent: ${MAXGUARD_DECOY_PARENT:-eth0}
    ipam:
      config:
        - subnet: ${MAXGUARD_DECOY_SUBNET:?set MAXGUARD_DECOY_SUBNET to your LAN, e.g. 192.168.1.0/24}
          gateway: ${MAXGUARD_DECOY_GATEWAY:?set MAXGUARD_DECOY_GATEWAY to your router address}

volumes:
  maxguard-decoy-data:
    name: maxguard-decoy-data
```

Check it. The three addresses have no defaults on purpose (a default could clash with a real device), so the second command fails with a clear message:

```bash
MAXGUARD_DECOY_SUBNET=192.0.2.0/24 MAXGUARD_DECOY_GATEWAY=192.0.2.1 MAXGUARD_DECOY_IP=192.0.2.250 \
  docker compose -f docker/decoy-compose.yaml config --format json | python -c "import json, sys; c = json.load(sys.stdin); n = c['networks']['decoy-lan']; s = c['services']['decoy']; print(n['driver'], n['driver_opts']['parent'], s['networks']['decoy-lan']['ipv4_address'], s['read_only'], s['cap_drop'])"
docker compose -f docker/decoy-compose.yaml config --quiet
```

Expected output:

```text
macvlan eth0 192.0.2.250 True ['ALL']
error while interpolating services.decoy.networks.decoy-lan.ipv4_address: required variable MAXGUARD_DECOY_IP is missing a value: set MAXGUARD_DECOY_IP to a free LAN address
```

*Documentation addresses (`192.0.2.0/24`) are used here; yours are free addresses on your own LAN.*

**Step 7.** Prove the decoy in Docker. `macvlan` needs a real network card on a real LAN, so this uses a private bridge network with the same hardening as the Compose file (a non-root user, read-only, all capabilities dropped). A second container plays the intruder, then the rule reads the copied `decoy.log`:

```bash
mkdir -p data/decoy-test data/decoy-logs && chmod 777 data/decoy-test
docker network create maxguard-decoy-test > /dev/null
docker run -d --rm --name maxguard-decoy-test --network maxguard-decoy-test \
  --user 10001:10001 --read-only --cap-drop ALL --security-opt no-new-privileges:true \
  --sysctl net.ipv4.ip_unprivileged_port_start=0 \
  -e PYTHONDONTWRITEBYTECODE=1 -e PYTHONPATH=/src -e MAXGUARD_DECOY_LOG=/data/decoy.log -e MAXGUARD_DECOY_TIMEOUT=2 \
  -v "$PWD/maxguard:/src/maxguard:ro" -v "$PWD/data/decoy-test:/data" \
  python:3.11-slim-bookworm python -m maxguard.decoy > /dev/null
for i in $(seq 1 40); do docker logs maxguard-decoy-test 2>&1 | grep -q telnet && break; sleep 0.5; done
docker logs maxguard-decoy-test
docker run --rm --network maxguard-decoy-test nicolaka/netshoot:v0.15 sh -c '
  printf "root\r\n" | nc -w 3 maxguard-decoy-test 23; echo
  printf "USER admin\r\n" | nc -w 3 maxguard-decoy-test 21
  curl -s -m 5 http://maxguard-decoy-test/ | head -c 60; echo'
docker rm -f maxguard-decoy-test > /dev/null && docker network rm maxguard-decoy-test > /dev/null
cp data/decoy-test/decoy.log data/decoy-logs/decoy.log
python -c "
from pathlib import Path
from maxguard.rules.base import merge
from maxguard.rules.decoy import decoy_contact
for f in merge(decoy_contact(Path('data/decoy-logs'))):
    print(f.severity, f.rule_id, f.src_ip, '->', f.dst_ip, f.dst_port, f.protocol)"
```

Expected output:

```text
decoy ftp listening on 0.0.0.0:21
decoy http listening on 0.0.0.0:80
decoy telnet listening on 0.0.0.0:23
login: 
220 FTP server ready
<!doctype html><html><head><title>Printer admin</title></hea
critical decoy.contact 172.18.0.3 -> 172.18.0.2 23 telnet
critical decoy.contact 172.18.0.3 -> 172.18.0.2 21 ftp
critical decoy.contact 172.18.0.3 -> 172.18.0.2 80 http
```

*The addresses come from Docker's private network, so yours may differ. `chmod 777` lets the container's non-root user (10001) write the log into the folder.*

In planning, a packet capture in the decoy's network namespace during these connections showed only SYN-ACK answers from the decoy: no connection it started and no DNS lookup.

**Step 8.** **On the lab** (*not run — verify on hardware*): put the three addresses in `docker/.env`, start the decoy with `docker compose -f docker/decoy-compose.yaml up -d`, and connect to its address from a laptop (Docker's macvlan driver does not let the host itself reach its own macvlan containers). Check whether your network card accepts several MAC addresses; Wi-Fi cards often do not. Getting `decoy.log` into the console's analysis is still open (see `docs/ARCHITECTURE.md` section 5).

**Step 9.** Commit, push, and open the pull request:

```bash
git add -A
git status          # only this task's files: nothing from .venv/, data/ or lab/captures/
git commit -m "feat: decoys and the decoy.contact rule (FIO-06)"
git push -u origin HEAD
```

`HEAD` means "the branch I am on", so you do not have to retype its name. Open the repository on github.com: a yellow bar shows your branch with a **Compare & pull request** button. Click it, keep the title `feat: decoys and the decoy.contact rule (FIO-06)`, fill in the template (paste the real output of the commands above under **How I tested it**), write `Closes #<issue number>` (this task's issue), and pick **@JWinborne1** under **Reviewers**. Click **Create pull request**, then fix anything CI or the reviewer finds with new commits on the same branch.

#### How to test

The tests pass, and on the lab a connection from a laptop to the decoy's address appears as a critical alert.

#### What you just did and why

Nobody has a reason to log in to a printer that does not exist, so any contact is almost certainly someone exploring the network: one of the most reliable signals a small network can get, with almost no false positives. Its own IP address keeps the decoy separate from the passive sensor.

#### Pull request checklist

- [ ] `ruff check .` prints `All checks passed!`
- [ ] `pytest -m "not integration" -q` passes on your laptop
- [ ] The pull request title has the form `type: summary (TASK-ID)` and the body says `Closes #<issue number>`
- [ ] No secrets, passwords, email addresses, personal data, or captures from a real network (CLAUDE.md rule 6)
- [ ] Any new dependency has a row in `docs/DEPENDENCIES.md` with its license
- [ ] CI is green and your reviewer approved
- [ ] The decoy never opens a connection
- [ ] Ahmad approved `decoy.contact`

### FIO-07: Per-device baselines

**Due:** Spring S9-S11 (due Fri Apr 16, 2027) · **Milestone:** `S9-S11 Detect more` · **Needs first:** [JAI-06](jaiden.md#jai-06-storage-alerts-in-sqlite-events-in-hourly-parquet-files), [JAK-08](jakub.md#jak-08-device-attribution-which-device-is-behind-each-ip-address) · **Kind:** code, tested

**Issue labels:** `type:task` `phase:spring` `owner:fiona` `area:engine`

#### Goal

Learn what each device normally does (the services and ports it uses) during a learning period, then raise `baseline.new_service` when a device uses something new, without breaking the rule that the same logs always give the same findings.

#### Prerequisites

JAI-06 (events) and JAK-08 (devices) are merged. The new rule ID needs the Security Lead's approval.

#### Steps

**Step 1.** Update `main` and create your branch for this task (one branch per task):

```bash
cd ~/projects/maxguard
source .venv/bin/activate
git checkout main && git pull
git checkout -b fiona/baselines
```

If `source .venv/bin/activate` fails, you have not made the virtual environment yet: do Week 0 section 0.11 first.

**Step 2.** Create `maxguard/rules/baseline.py`:

```python
"""Per-device baselines and rule baseline.new_service (Fiona, FIO-07, proposed for v2.0 spring).

During a learning period MaxGuard records, per device IP address, which services
it uses: the set of (dst_port, proto, service) it connects to, plus how many
different peers it talks to. After the learning period, a device that uses a
service missing from its baseline gets a medium finding.

Why a second registry: a normal rule takes only a log folder, so the same logs
always give the same findings (CLAUDE.md rule 2). This rule also needs history.
The history (the baseline) and the end of the learning period are passed in
through `context`; the rule never reads the clock or a baseline file itself.
So the same logs plus the same context always give the same findings.
run_all() and the Fall 2026 RULES registry (maxguard/rules/base.py) do not change.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from maxguard.events.normalize import normalize
from maxguard.models import Evidence, Finding
from maxguard.rules.base import RULES, merge

RULE_ID = "baseline.new_service"

StatefulRule = Callable[[Path, dict], list[Finding]]
STATEFUL_RULES: dict[str, StatefulRule] = {}

# Zeek labels FTP data connections "ftp-data". Their port is picked fresh for every
# file transfer, so it would look "new" every time: leave them out of baselines.
IGNORED_SERVICES = frozenset({"ftp-data"})


def stateful_rule(rule_id: str):
    """Register a rule that takes (log_dir, context) instead of just log_dir."""
    def wrap(fn: StatefulRule) -> StatefulRule:
        if rule_id in STATEFUL_RULES or rule_id in RULES:  # rule IDs are unique across both
            raise ValueError(f"duplicate rule_id {rule_id!r}")
        STATEFUL_RULES[rule_id] = fn
        return fn

    return wrap


def run_stateful(log_dir: Path, context: dict) -> list[Finding]:
    """Run every stateful rule in rule_id order and merge the results (like run_all)."""
    found: list[Finding] = []
    for rule_id in sorted(STATEFUL_RULES):
        found.extend(STATEFUL_RULES[rule_id](log_dir, context))
    return merge(found)


def connections(events: list[dict]) -> list[dict]:
    """The events that describe one connection each (conn.log), with a destination port.

    http.log, ssl.log and eve.json describe the same connections again, so counting
    only conn events never counts a connection twice.
    """
    return [e for e in events
            if e["kind"] == "conn" and e["dst_port"] is not None
            and e["service"] not in IGNORED_SERVICES]


def service_key(event: dict) -> tuple[int, str, str]:
    return (int(event["dst_port"]), event["proto"], event["service"])


def build_baseline(events: list[dict]) -> dict:
    """Per device IP: the sorted (dst_port, proto, service) list it used and its peer count.

    `events` are normalized events (maxguard.events.normalize) from the learning
    period. The result only contains lists, strings and numbers in sorted order, so
    it can be stored as JSON, and the same events (in any order) give the same baseline.
    Example: {"192.0.2.10": {"peers": 1, "services": [[80, "tcp", "http"]]}}
    """
    services: dict[str, set[tuple[int, str, str]]] = {}
    peers: dict[str, set[str]] = {}
    for event in connections(events):
        device = event["src_ip"]
        services.setdefault(device, set()).add(service_key(event))
        peers.setdefault(device, set()).add(event["dst_ip"])
    return {device: {"peers": len(peers[device]),
                     "services": [list(key) for key in sorted(services[device])]}
            for device in sorted(services)}


def known_services(baseline: dict, device: str) -> set[tuple[int, str, str]]:
    """The device's services as tuples (JSON turned them into lists)."""
    return {tuple(key) for key in baseline[device]["services"]}


def is_known(key: tuple[int, str, str], known: set[tuple[int, str, str]]) -> bool:
    if key in known:
        return True
    # Zeek leaves service empty when it could not tell the protocol (for example a
    # connection that was refused). Same port and proto as a known service: not new.
    port, proto, service = key
    return service == "" and any(k[0] == port and k[1] == proto for k in known)


def new_service_finding(event: dict, learning_ends: float) -> Finding:
    ev = Evidence(log=event["log"], uid=event["uid"], ts=event["ts"],
                  record_id=event["event_id"])  # event_id is the record_id of the conn record
    return Finding(rule_id=RULE_ID, title="Device used a service new to it", severity="medium",
                   src_ip=event["src_ip"], dst_ip=event["dst_ip"],
                   dst_port=int(event["dst_port"]),
                   protocol=event["service"] or event["proto"],
                   first_seen=event["ts"], last_seen=event["ts"], source=event["source"],
                   details={"proto": event["proto"], "service": event["service"],
                            "learning_ends": learning_ends},
                   evidence=[ev])


@stateful_rule(RULE_ID)
def new_service(log_dir: Path, context: dict) -> list[Finding]:
    """A device used a (dst_port, proto, service) missing from its baseline.

    context["baseline"]: the dict from build_baseline() (for example loaded from storage)
    context["learning_ends"]: epoch seconds; events before it belong to the learning
    period and never give a finding.
    Devices without a baseline are skipped: there is nothing to compare them with
    (new devices show up in the device inventory instead).
    """
    baseline: dict = context["baseline"]
    learning_ends = float(context["learning_ends"])
    findings = []
    # sensor_id does not change any field this rule uses, so "" is fine here.
    for event in connections(normalize(log_dir, sensor_id="")):
        device = event["src_ip"]
        if event["ts"] < learning_ends or device not in baseline:
            continue
        if not is_known(service_key(event), known_services(baseline, device)):
            findings.append(new_service_finding(event, learning_ends))
    return findings
```

Three parts. `build_baseline(events)` turns the learning period's events into `{ip: {"peers": n, "services": [[port, proto, service], ...]}}`, sorted and ready for `json.dumps`. `STATEFUL_RULES` and `@stateful_rule` are a second registry for rules that need history; `run_all()` and Contract 3 do not change (`docs/ARCHITECTURE.md` section 5). The rule `baseline.new_service` gets the baseline and the end of the learning period through `context` and never reads the clock or a file, so the same logs and the same context always give the same findings. Choices that cut false positives: only `conn` events count (http, ssl and eve records describe the same connections again); `ftp-data` is ignored (its port changes on every transfer); an event whose service Zeek could not tell is known when the device already used that port and protocol; a device with no baseline is skipped (the device inventory shows new devices). A *device* is the address that **starts** a connection, so this finds new services a device **uses**.

**Step 3.** Create the tests `tests/unit/test_baseline.py`:

```python
"""Tests for per-device baselines and rule baseline.new_service (Fiona, FIO-07).

The lab fixtures in tests/fixtures/zeek/ all come from one client (172.18.0.3)
talking to one server (172.18.0.2), each capture on a different service. So the
"learning period" here is the plain_http and clean_tls13 captures, and the
telnet capture is the device trying something new.
"""

from __future__ import annotations

import json
import random
from pathlib import Path

import pytest

from maxguard.events.normalize import normalize
from maxguard.rules.base import RULES, run_all
from maxguard.rules.baseline import (
    STATEFUL_RULES,
    build_baseline,
    new_service,
    run_stateful,
    stateful_rule,
)

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "zeek"
CLIENT, SERVER = "172.18.0.3", "172.18.0.2"
# Every lab capture was made after this moment, so all their events count as "after learning".
LEARNING_ENDS = 1791250000.0


def events_of(*captures: str) -> list[dict]:
    events: list[dict] = []
    for capture in captures:
        events.extend(normalize(FIXTURES / capture, sensor_id="pcap"))
    return events


@pytest.fixture
def baseline() -> dict:
    return build_baseline(events_of("plain_http", "clean_tls13"))


def test_baseline_lists_services_and_peers(baseline):
    assert baseline == {CLIENT: {"peers": 1, "services": [[80, "tcp", "http"],
                                                          [4436, "tcp", "ssl"]]}}


def test_same_events_always_build_the_same_baseline():
    events = events_of("plain_http", "clean_tls13", "_handmade/dns_dhcp", "ftp")
    shuffled = list(events)
    random.Random(7).shuffle(shuffled)  # a different order must not matter
    first, second = build_baseline(events), build_baseline(shuffled)
    assert json.dumps(first) == json.dumps(second)  # byte for byte, key order included


def test_baseline_survives_a_json_round_trip(baseline):
    # The baseline is stored as JSON between runs; the rule must work on the loaded copy.
    stored = json.loads(json.dumps(baseline))
    assert stored == baseline
    context = {"baseline": stored, "learning_ends": LEARNING_ENDS}
    assert new_service(FIXTURES / "plain_http", context) == []


def test_several_devices_and_ftp_data_left_out():
    baseline = build_baseline(events_of("_handmade/dns_dhcp", "ftp"))
    assert baseline["192.168.56.50"] == {"peers": 1, "services": [[53, "udp", "dns"]]}
    # ftp-data ports change on every transfer, so only the control port 21 is learned.
    assert baseline[CLIENT]["services"] == [[21, "tcp", "ftp"]]
    assert list(baseline) == sorted(baseline)


def test_a_new_port_is_found(baseline):
    context = {"baseline": baseline, "learning_ends": LEARNING_ENDS}
    [finding] = new_service(FIXTURES / "telnet", context)
    assert finding.rule_id == "baseline.new_service"
    assert finding.severity == "medium"
    assert (finding.src_ip, finding.dst_ip, finding.dst_port) == (CLIENT, SERVER, 23)
    assert finding.protocol == "tcp"  # Zeek has no Telnet analyzer, so service is ""
    [ev] = finding.evidence
    [conn] = [e for e in normalize(FIXTURES / "telnet", "pcap") if e["log"] == "conn.log"]
    assert ev.log == "conn.log" and ev.record_id == conn["event_id"]


def test_a_known_service_is_not_found(baseline):
    context = {"baseline": baseline, "learning_ends": LEARNING_ENDS}
    assert new_service(FIXTURES / "plain_http", context) == []
    assert new_service(FIXTURES / "clean_tls13", context) == []


def test_nothing_is_found_during_the_learning_period(baseline):
    # The telnet capture happened before this "end of learning": it is still learning.
    context = {"baseline": baseline, "learning_ends": 1791260000.0}
    assert new_service(FIXTURES / "telnet", context) == []


def test_unknown_devices_are_skipped():
    context = {"baseline": {"192.0.2.99": {"peers": 1, "services": [[80, "tcp", "http"]]}},
               "learning_ends": LEARNING_ENDS}
    assert new_service(FIXTURES / "telnet", context) == []


def test_same_logs_and_context_give_the_same_findings(baseline):
    context = {"baseline": baseline, "learning_ends": LEARNING_ENDS}
    first = [f.to_dict() for f in run_stateful(FIXTURES / "telnet", context)]
    second = [f.to_dict() for f in run_stateful(FIXTURES / "telnet", context)]
    assert first == second and len(first) == 1


def test_stateful_registry_is_separate_from_run_all():
    assert STATEFUL_RULES["baseline.new_service"] is new_service
    assert "baseline.new_service" not in RULES
    # run_all() is unchanged: on the telnet capture it still finds only cleartext.telnet.
    assert {f.rule_id for f in run_all(FIXTURES / "telnet")} == {"cleartext.telnet"}


def test_duplicate_rule_ids_are_refused():
    with pytest.raises(ValueError):
        stateful_rule("baseline.new_service")(new_service)
    with pytest.raises(ValueError):
        stateful_rule("cleartext.telnet")(new_service)  # taken in the normal registry
```

Run them:

```bash
pytest tests/unit/test_baseline.py -q
```

Expected output:

```text
...........                                                                                  [100%]
11 passed in 0.07s
```

**Step 4.** Nothing calls `run_stateful()` yet: where the baseline is stored and when the learning period ends is an open decision (`docs/ARCHITECTURE.md` section 5). Propose it in GitHub Discussions with Jaiden.

**Step 5.** Commit, push, and open the pull request:

```bash
git add -A
git status          # only this task's files: nothing from .venv/, data/ or lab/captures/
git commit -m "feat: per-device baselines and baseline.new_service (FIO-07)"
git push -u origin HEAD
```

`HEAD` means "the branch I am on", so you do not have to retype its name. Open the repository on github.com: a yellow bar shows your branch with a **Compare & pull request** button. Click it, keep the title `feat: per-device baselines and baseline.new_service (FIO-07)`, fill in the template (paste the real output of the commands above under **How I tested it**), write `Closes #<issue number>` (this task's issue), and pick **@JWinborne1** under **Reviewers**. Click **Create pull request**, then fix anything CI or the reviewer finds with new commits on the same branch.

#### How to test

The tests pass, including one that builds the baseline twice and compares.

#### What you just did and why

Small networks are predictable: a printer prints, a camera streams. A device that suddenly uses a new service is worth a look. Passing the baseline in explicitly keeps the rule deterministic: given the same logs and the same baseline it always gives the same answer (CLAUDE.md rule 2).

#### Pull request checklist

- [ ] `ruff check .` prints `All checks passed!`
- [ ] `pytest -m "not integration" -q` passes on your laptop
- [ ] The pull request title has the form `type: summary (TASK-ID)` and the body says `Closes #<issue number>`
- [ ] No secrets, passwords, email addresses, personal data, or captures from a real network (CLAUDE.md rule 6)
- [ ] Any new dependency has a row in `docs/DEPENDENCIES.md` with its license
- [ ] CI is green and your reviewer approved
- [ ] Ahmad approved `baseline.new_service`
