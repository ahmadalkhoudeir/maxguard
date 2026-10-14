# Ahmad: Security Lead

**Ahmad Al Khoudeir** (@ahmadalkhoudeir) · Module: Dashboard, response module · Reviewer for your pull requests: @JWinborne1 (Jaiden) · Ask first when stuck: Jaiden

This is your part of the MaxGuard v2.0 roadmap. Read [the roadmap overview](README.md) once, then work top to bottom: Week 0 first, then your tasks in order. Each task's ID is also the start of its GitHub issue's title.

## Your tasks

| Task | Due | Title | Needs first | Kind |
|---|---|---|---|---|
| [AHM-00](#week-0--onboarding-due-friday-october-9-2026) | W0 | Week 0 onboarding (Ahmad) | — | process |
| [AHM-01](#ahm-01-set-up-github-for-the-team-access-discussions-labels-milestones-issues) | W0 | Set up GitHub for the team: access, Discussions, labels, milestones, issues | — | process |
| [AHM-02](#ahm-02-dashboard-layout-alert-queue-and-upload-page) | W3 | Dashboard: layout, alert queue, and upload page | [JAI-07](jaiden.md#jai-07-the-api-uploads-alerts-events-live-updates-sensor-ingest) | code, tested |
| [AHM-03](#ahm-03-alert-detail-page-with-analyst-and-home-modes) | W4 | Alert detail page with Analyst and Home modes | [AHM-02](#ahm-02-dashboard-layout-alert-queue-and-upload-page), [JON-02](jonattan.md#jon-02-ollama-client-one-evidence-citing-explanation-per-finding), [JON-04](jonattan.md#jon-04-home-mode-text-for-every-rule) | code, tested |
| [AHM-04](#ahm-04-security-review-of-the-alpha) | W5 | Security review of the alpha | [AHM-03](#ahm-03-alert-detail-page-with-analyst-and-home-modes), [JON-03](jonattan.md#jon-03-offline-guard-make-accidental-network-access-fail-loudly), [AMO-03](amory.md#amo-03-report-export-json-csv-and-html) | process |
| [AHM-05](#ahm-05-alpha-acceptance-test-and-presentation) | W8 | Alpha acceptance test and presentation | [JAI-10](jaiden.md#jai-10-release-v20-alpha), [KAR-05](karthik.md#kar-05-release-candidate-test-with-an-outside-tester) | process |
| [AHM-06](#ahm-06-ip-timeline-and-device-inventory-pages) | S4 | IP timeline and device inventory pages | [AHM-03](#ahm-03-alert-detail-page-with-analyst-and-home-modes), [JAK-08](jakub.md#jak-08-device-attribution-which-device-is-behind-each-ip-address), [JAI-07](jaiden.md#jai-07-the-api-uploads-alerts-events-live-updates-sensor-ingest), [JAK-07](jakub.md#jak-07-live-sensor-capture-rotation-and-shipping-to-the-console) | code, tested |
| [AHM-07](#ahm-07-response-block-proposals-generated-rules-and-preview-before-you-block) | S8 | Response: block proposals, generated rules, and preview before you block | [JAI-06](jaiden.md#jai-06-storage-alerts-in-sqlite-events-in-hourly-parquet-files), [JAI-07](jaiden.md#jai-07-the-api-uploads-alerts-events-live-updates-sensor-ingest) | code, tested |
| [AHM-08](#ahm-08-response-approvals-audit-revert-and-the-opnsense-connector) | S8 | Response: approvals, audit, revert, and the OPNsense connector | [AHM-07](#ahm-07-response-block-proposals-generated-rules-and-preview-before-you-block), [JON-03](jonattan.md#jon-03-offline-guard-make-accidental-network-access-fail-loudly) | code, tested |
| [AHM-09](#ahm-09-v20-acceptance-test) | S14 | v2.0 acceptance test | [JAI-12](jaiden.md#jai-12-release-v20-rc1-and-v20) | process |

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
git config --global user.name "Ahmad Al Khoudeir"
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
git checkout -b ahmad/week0-team-row
```

2. **Make the change.** Run `code .`, open `docs/TEAM.md`, and add this line at
   the end (keep the `|` characters):

```markdown
| Ahmad Al Khoudeir | Security Lead | ahmadalkhoudeir | Dashboard, response module |
```

3. **Commit** (the message says *what changed*, starting with a type such as
   `docs:`, `feat:`, `fix:` or `test:`; see `docs/CONTRIBUTING.md`):

```bash
git add docs/TEAM.md
git commit -m "docs: add Ahmad to TEAM.md"
```

4. **Push** your branch to GitHub:

```bash
git push -u origin ahmad/week0-team-row
```

Expected (from the planning simulation; the first lines differ on GitHub):

```text
 * [new branch]      ahmad/week0-team-row -> ahmad/week0-team-row
branch 'ahmad/week0-team-row' set up to track 'origin/ahmad/week0-team-row'.
```

5. **Open the pull request** and ask for a review:

```bash
gh pr create --base main --title "docs: add Ahmad to TEAM.md" --body "Week 0 onboarding." --reviewer JWinborne1
```

`gh` prints the pull request's web address. (You can also click the link Git
printed after the push and press **Create pull request**.)

6. **After approval**, click **Squash and merge** on GitHub, then update your laptop:

```bash
git checkout main && git pull
git branch -d ahmad/week0-team-row
```

**If GitHub says "This branch has conflicts":** eight people are adding a line
to the same file this week, so this is expected. Bring `main` into your branch
and keep both lines:

```bash
git checkout main && git pull
git checkout ahmad/week0-team-row
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
   `AHM-01: pytest cannot import maxguard`). In the body, paste the
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

### AHM-01: Set up GitHub for the team: access, Discussions, labels, milestones, issues

**Due:** Week 0 (due Fri Oct 9, 2026) · **Milestone:** `W0 Onboarding and contracts` · **Needs first:** none · **Kind:** process

**Issue labels:** `type:task` `phase:alpha` `owner:ahmad` `area:program` `critical-path`

#### Goal

Make the repository ready for eight people as early in Week 0 as possible: everyone has write access, Discussions is on with a pinned "Week 0 check-in", private vulnerability reporting is on, and every roadmap task exists as an issue with its labels and milestone on the project board.

#### Prerequisites

The planning pull request (it adds `scripts/create_issues.sh` and the templates) is merged. You need admin rights on the repository.

#### Steps

**Step 1.** **Access.** On github.com: **Settings → Collaborators → Add people**, and invite each teammate by the GitHub name in `docs/TEAM.md` with the **Write** role.

**Step 2.** **Discussions.** **Settings → General → Features**: tick **Discussions**. GitHub creates the categories the team uses (*Announcements*, *Q&A*, *Ideas*, *General*). Then open **Discussions → New discussion → General**, title `Week 0 check-in`, body: "Reply with the output of `git --version`, `python3.11 --version`, `docker --version`, and the first line of your `http.log` from Week 0 step 0.8." Open it and click **Pin discussion**.

**Step 3.** **Security reports.** In **Settings**, open the page in the *Security* part of the sidebar (named *Code security* or *Advanced Security*, depending on the account) and **Enable** **Private vulnerability reporting**, so outsiders can report a problem without a public issue. *Not run in planning — verify on github.com.*

**Step 4.** **Labels, milestones, issues, and the project.** The GitHub CLI needs the `project` permission for the board:

```bash
gh auth refresh -s project
```

Preview what the script will do (it changes nothing in this mode):

```bash
DRY_RUN=1 bash scripts/create_issues.sh | head -n 25
```

Expected output (recorded in planning):

```text
== labels
would run: gh label create type:task --repo ahmadalkhoudeir/maxguard --color 1D76DB --description A\ roadmap\ task --force
would run: gh label create type:bug --repo ahmadalkhoudeir/maxguard --color D73A4A --description Something\ is\ broken --force
would run: gh label create type:question --repo ahmadalkhoudeir/maxguard --color D876E3 --description A\ question\ \(prefer\ GitHub\ Discussions\) --force
would run: gh label create type:docs --repo ahmadalkhoudeir/maxguard --color 0075CA --description Documentation\ only --force
would run: gh label create phase:alpha --repo ahmadalkhoudeir/maxguard --color 0E8A16 --description Ships\ in\ v2.0-alpha\ \(Fall\ 2026\) --force
would run: gh label create phase:spring --repo ahmadalkhoudeir/maxguard --color 5319E7 --description Ships\ in\ v2.0\ \(Spring\ 2027\) --force
would run: gh label create area:engine --repo ahmadalkhoudeir/maxguard --color FBCA04 --description Adapters\,\ Zeek\,\ Suricata\,\ rules\,\ pipeline --force
would run: gh label create area:ai --repo ahmadalkhoudeir/maxguard --color C5DEF5 --description Local\ AI\,\ citations\,\ offline\ guard\,\ evaluation --force
would run: gh label create area:mapping --repo ahmadalkhoudeir/maxguard --color BFD4F2 --description Compliance\ and\ ATT\&CK\ mapping\ files\,\ reports --force
would run: gh label create area:ui --repo ahmadalkhoudeir/maxguard --color F9D0C4 --description Dashboard\ pages --force
would run: gh label create area:api --repo ahmadalkhoudeir/maxguard --color D4C5F9 --description FastAPI\ backend --force
would run: gh label create area:storage --repo ahmadalkhoudeir/maxguard --color C2E0C6 --description SQLite\ state\,\ Parquet\ events --force
would run: gh label create area:sensor --repo ahmadalkhoudeir/maxguard --color FEF2C0 --description Live\ sensor\,\ NetFlow\,\ host\ agent\,\ hardware --force
would run: gh label create area:response --repo ahmadalkhoudeir/maxguard --color E99695 --description Blocking\,\ preview\,\ approvals\,\ enforcers --force
would run: gh label create area:testing --repo ahmadalkhoudeir/maxguard --color BFDADC --description Lab\,\ captures\,\ fixtures\,\ integration\ tests\,\ CI --force
would run: gh label create area:release --repo ahmadalkhoudeir/maxguard --color 006B75 --description Packaging\,\ Docker\,\ releases\,\ signing --force
would run: gh label create area:program --repo ahmadalkhoudeir/maxguard --color EDEDED --description Planning\,\ meetings\,\ reviews\,\ onboarding --force
would run: gh label create critical-path --repo ahmadalkhoudeir/maxguard --color B60205 --description A\ delay\ here\ delays\ the\ next\ demo --force
would run: gh label create contract-change --repo ahmadalkhoudeir/maxguard --color B60205 --description Changes\ a\ contract:\ Jaiden\ reviews\,\ Security\ Lead\ approves --force
would run: gh label create blocked --repo ahmadalkhoudeir/maxguard --color 000000 --description Waiting\ on\ another\ task\ \(say\ which\ in\ a\ comment\) --force
would run: gh label create needs-hardware --repo ahmadalkhoudeir/maxguard --color FEF2C0 --description Has\ steps\ marked:\ not\ run\,\ verify\ on\ hardware --force
would run: gh label create owner:ahmad --repo ahmadalkhoudeir/maxguard --color EDEDED --description Assigned\ to\ Ahmad --force
would run: gh label create owner:jaiden --repo ahmadalkhoudeir/maxguard --color EDEDED --description Assigned\ to\ Jaiden --force
would run: gh label create owner:fiona --repo ahmadalkhoudeir/maxguard --color EDEDED --description Assigned\ to\ Fiona --force
```

*Recorded in planning with a stand-in for `gh` that only prints the calls.*

Then run it for real (*not run in planning*; it is safe to run again, it skips what already exists):

```bash
bash scripts/create_issues.sh
```

**Step 5.** Check the result: **Issues** lists every task (title starts with its ID, such as `JAI-01`), each with an `owner:` label and a milestone, and **Projects → MaxGuard v2.0 Roadmap** shows them all. Assign each issue to its owner once they accept the invitation (GitHub can only assign collaborators).

**Step 6.** Post in **Announcements**: the link to `docs/roadmap/README.md` and "Start with Week 0 in your own file".

#### How to test

Every teammate can open the pinned discussion, sees their issues with `owner:<name>`, and has write access (they can push a branch).

#### What you just did and why

Issues, labels, and milestones made by a script are consistent and complete; made by hand, 69 of them would not be. The board then shows at a glance who is blocked and what is late, which is what the Friday review needs. Discussions keeps answers searchable for the next person with the same problem.

#### Pull request checklist

- [ ] All seven teammates accepted the invitation
- [ ] The `Week 0 check-in` discussion is pinned
- [ ] Private vulnerability reporting is on
- [ ] Every roadmap task has an issue, a milestone and its labels

### AHM-02: Dashboard: layout, alert queue, and upload page

**Due:** Week 3 (due Fri Oct 30) · **Milestone:** `W3 API and alert queue` · **Needs first:** [JAI-07](jaiden.md#jai-07-the-api-uploads-alerts-events-live-updates-sensor-ingest) · **Kind:** code, tested

**Issue labels:** `type:task` `phase:alpha` `owner:ahmad` `area:ui` `critical-path`

#### Goal

Build the first dashboard pages with FastAPI, Jinja2 and htmx: a base layout with the privacy note and the Analyst/Home switch, the alert queue (severity, title, source → destination:port, count, status, assignee, last seen) with filters and live refresh, and an upload page.

#### Prerequisites

JAI-07 (the API and `create_app`) is merged. Read `docs/ARCHITECTURE.md` sections 10 and 14 first.

#### Steps

**Step 1.** Update `main` and create your branch for this task (one branch per task):

```bash
cd ~/projects/maxguard
source .venv/bin/activate
git checkout main && git pull
git checkout -b ahmad/dashboard-queue
```

If `source .venv/bin/activate` fails, you have not made the virtual environment yet: do Week 0 section 0.11 first.

**Step 2.** Vendor htmx (one file, 0BSD license) from the npm registry and check it is the exact file the team reviewed:

```bash
mkdir -p maxguard/web/static
curl -sSL https://registry.npmjs.org/htmx.org/-/htmx.org-2.0.11.tgz -o /tmp/htmx.tgz
tar -xzOf /tmp/htmx.tgz package/dist/htmx.min.js > maxguard/web/static/htmx-2.0.11.min.js
sha256sum maxguard/web/static/htmx-2.0.11.min.js
```

Expected output:

```text
d6fdc75f204e6bdefa99b69bf1e6d4ac69b8a364f77929f45c13476b4000f717  maxguard/web/static/htmx-2.0.11.min.js
```

On macOS use `shasum -a 256` instead of `sha256sum`. htmx already has a row in `docs/DEPENDENCIES.md`.

**Step 3.** Create `maxguard/web/__init__.py` (one line):

```python

```

and `maxguard/web/routes.py`:

```python
"""The dashboard's HTML pages (Ahmad, AHM-02).

create_app() in maxguard/api/app.py includes this router when it imports.

    GET   /                             alert queue (filters: ?status=&severity=)
    GET   /upload                       upload form (posts to /api/analyses)
    POST  /mode                         Analyst/Home switch (cookie mg_mode)

The pages read the stores only through request.app.state. Jinja2 escapes every
value; nothing from traffic or from the AI is ever marked |safe, because an
attacker writes the traffic (docs/ARCHITECTURE.md section 14).
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates

from maxguard.models import SEVERITIES
from maxguard.storage.state import ALERT_STATUSES

router = APIRouter()
TEMPLATES = Jinja2Templates(directory=Path(__file__).resolve().parent / "templates")

MODES = ("analyst", "home")
YEAR_SECONDS = 365 * 24 * 3600

# Home mode: the severity in plain words (no jargon), and color is never the only signal.
SEVERITY_WORDS = {
    "critical": "Critical: fix this today",
    "high": "High: fix this week",
    "medium": "Medium: fix this month",
    "low": "Low: fix when you can",
    "info": "Info: nothing to fix, good to know",
}
STATUS_LABELS = {"new": "New", "investigating": "Investigating", "resolved": "Resolved",
                 "false_positive": "False positive"}

# Sent with every page. The dashboard needs nothing from outside this computer, so the
# browser is told to refuse anything else, even if some text ever slipped past escaping.
SECURITY_HEADERS = {
    "Content-Security-Policy": (
        "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self'; "
        "connect-src 'self'; form-action 'self'; base-uri 'none'; object-src 'none'; "
        "frame-ancestors 'none'"),
    "X-Content-Type-Options": "nosniff",
    # "same-origin", not "no-referrer": with no-referrer, Chrome sends "Origin: null" on
    # form posts, and the API's cross-site check (rightly) refuses those.
    "Referrer-Policy": "same-origin",
}


# ---------- small helpers ----------

def utc_time(ts: float | None) -> str:
    """Unix seconds -> "2026-10-06 14:03:22 UTC" (the same on every machine)."""
    if ts is None:
        return ""
    return datetime.fromtimestamp(ts, tz=UTC).strftime("%Y-%m-%d %H:%M:%S UTC")


TEMPLATES.env.filters["utc_time"] = utc_time


def mode_of(request: Request) -> str:
    """"home" or "analyst" (the default) from the mg_mode cookie."""
    return "home" if request.cookies.get("mg_mode") == "home" else "analyst"


def render(request: Request, name: str, context: dict, status_code: int = 200) -> HTMLResponse:
    """Render a template with the values every page needs, plus the security headers."""
    full = {"mode": mode_of(request), "severities": SEVERITIES,
            "severity_words": SEVERITY_WORDS, "status_labels": STATUS_LABELS, **context}
    response = TEMPLATES.TemplateResponse(request, name, full, status_code=status_code)
    response.headers.update(SECURITY_HEADERS)
    return response


def error_page(request: Request, status_code: int, message: str) -> HTMLResponse:
    return render(request, "error.html", {"message": message}, status_code=status_code)


def empty_to_none(value: str | None) -> str | None:
    """A filter <select> sends "" for "All"."""
    return value or None


def safe_next(path: str) -> str:
    """Only a path on this site: "//evil.example" or "https://..." would be an open redirect."""
    if path.startswith("/") and not path.startswith("//") and "\\" not in path:
        return path
    return "/"


# ---------- AHM-02: queue, upload, mode switch ----------

@router.get("/", response_class=HTMLResponse)
def queue(request: Request, status: str | None = None, severity: str | None = None):
    status, severity = empty_to_none(status), empty_to_none(severity)
    try:
        alerts = request.app.state.state_store.list_alerts(status=status, severity=severity)
    except ValueError as err:  # unknown status or severity in the URL
        return error_page(request, 400, str(err))
    return render(request, "queue.html", {
        "alerts": alerts, "status": status or "", "severity": severity or "",
        "statuses": ALERT_STATUSES,
    })


@router.get("/upload", response_class=HTMLResponse)
def upload_page(request: Request):
    return render(request, "upload.html", {})


@router.post("/mode")
async def switch_mode(request: Request):
    """The Analyst/Home switch: a plain form, so it works with the keyboard and without
    JavaScript. The cookie is only a display preference, not a security setting."""
    form = await request.form()
    mode = form.get("mode")
    response = RedirectResponse(safe_next(str(form.get("next", "/"))), status_code=303)
    if mode in MODES:
        response.set_cookie("mg_mode", mode, max_age=YEAR_SECONDS, path="/",
                            samesite="lax", httponly=True)
    return response


@router.get("/favicon.ico", include_in_schema=False)
def favicon() -> Response:
    """Browsers ask for this on every page; answer "nothing" instead of a 404 log line."""
    return Response(status_code=204)
```

`create_app()` includes this router as soon as the module exists. What to notice: `render()` adds three headers to every page. The **Content-Security-Policy** tells the browser to load and run nothing that does not come from this computer, a second wall in case some text ever slipped past escaping. **Referrer-Policy** is `same-origin`, not `no-referrer`: with `no-referrer`, Chrome sends `Origin: null` on form posts, and the API's cross-site check refuses those (found in a real browser, not by a unit test). The Analyst/Home switch is a small `POST` form, so it works with the keyboard and without JavaScript, and `safe_next()` keeps its redirect on this site.

**Step 4.** Create the templates in `maxguard/web/templates/`. The layout, `base.html` (the `htmx-config` tag keeps htmx inside the CSP: no inline styles, no `eval`, no scripts from responses, only this site):

```html
<!doctype html>
{# The layout every page extends (Ahmad, AHM-02). Everything is served by this
   computer: no CDN, no web fonts. Jinja2 escapes every {{ value }}. #}
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  {# htmx settings: no inline <style> (our CSP blocks it), never run scripts or eval
     from a response, only talk to this site, and show 400 answers (form errors). #}
  <meta name="htmx-config" content='{"includeIndicatorStyles": false, "allowEval": false, "allowScriptTags": false, "selfRequestsOnly": true, "responseHandling": [{"code": "204", "swap": false}, {"code": "[23]..", "swap": true}, {"code": "400", "swap": true, "error": false}, {"code": "[45]..", "swap": false, "error": true}]}'>
  <title>{% block title %}MaxGuard{% endblock %} · MaxGuard</title>
  <link rel="stylesheet" href="/static/app.css">
  <script src="/static/htmx-2.0.11.min.js" defer></script>
  <script src="/static/app.js" defer></script>
</head>
<body class="mode-{{ mode }}">
  <a class="skip" href="#main">Skip to content</a>
  <header class="top">
    <div class="brand">MaxGuard</div>
    <nav aria-label="Main">
      <a href="/">Alerts</a>
      <a href="/upload">Upload</a>
    </nav>
    <form class="mode-switch" method="post" action="/mode">
      <input type="hidden" name="next" value="{{ request.url.path }}{% if request.url.query %}?{{ request.url.query }}{% endif %}">
      <span id="mode-label">View:</span>
      <button type="submit" name="mode" value="analyst" aria-describedby="mode-label"
              aria-pressed="{{ 'true' if mode == 'analyst' else 'false' }}">Analyst</button>
      <button type="submit" name="mode" value="home" aria-describedby="mode-label"
              aria-pressed="{{ 'true' if mode == 'home' else 'false' }}">Home</button>
    </form>
  </header>
  <p class="privacy">Your data never leaves this computer.</p>
  <main id="main" tabindex="-1">
    {% block content %}{% endblock %}
  </main>
</body>
</html>
```

The severity badge `_severity.html` (the word *and* a color, never color alone) and the error page `error.html`:

```html
{# Severity as text AND color (Ahmad, AHM-02): never color alone. In Home mode the
   words say what to do ("High: fix this week"). Expects "severity" in the context. #}
<span class="sev sev-{{ severity }}">{% if mode == "home" %}{{ severity_words[severity] }}{% else %}{{ severity | capitalize }}{% endif %}</span>
```

```html
{% extends "base.html" %}
{# Error page (Ahmad, AHM-03): 404 for an unknown alert, 400 for a bad filter or address. #}
{% block title %}Error{% endblock %}
{% block content %}
<h1>Sorry</h1>
<p class="error">{{ message }}</p>
<p><a href="/">Back to the alert queue</a></p>
{% endblock %}
```

The queue, `queue.html`:

```html
{% extends "base.html" %}
{# The alert queue (Ahmad, AHM-02). The filters swap only the #alerts table; the
   table also reloads itself on "refresh" (sent by app.js when the server says
   alerts changed) and every 30 seconds in case the live stream is down. #}
{% block title %}Alerts{% endblock %}
{% block content %}
<h1>Alerts</h1>

<form id="filters" class="filters" method="get" action="/">
  <label for="status">Status</label>
  <select id="status" name="status"
          hx-get="/" hx-target="#alerts" hx-select="#alerts" hx-swap="outerHTML"
          hx-include="#filters" hx-push-url="true">
    <option value="">All</option>
    {% for value in statuses %}
    <option value="{{ value }}" {% if value == status %}selected{% endif %}>{{ status_labels[value] }}</option>
    {% endfor %}
  </select>
  <label for="severity">Severity</label>
  <select id="severity" name="severity"
          hx-get="/" hx-target="#alerts" hx-select="#alerts" hx-swap="outerHTML"
          hx-include="#filters" hx-push-url="true">
    <option value="">All</option>
    {% for value in severities %}
    <option value="{{ value }}" {% if value == severity %}selected{% endif %}>{{ value | capitalize }}</option>
    {% endfor %}
  </select>
  {# Without JavaScript the selects do nothing on their own; this button still works. #}
  <button type="submit" class="secondary">Apply</button>
</form>

<div id="alerts" hx-get="/?status={{ status | urlencode }}&amp;severity={{ severity | urlencode }}"
     hx-trigger="refresh, every 30s" hx-select="#alerts" hx-swap="outerHTML" aria-live="polite">
  {% if alerts %}
  <table class="stack">
    <caption>{{ alerts | length }} alert{{ "" if alerts | length == 1 else "s" }}, most severe first</caption>
    <thead>
      <tr>
        <th scope="col">Severity</th>
        <th scope="col">Alert</th>
        <th scope="col">Source → destination:port</th>
        <th scope="col">Count</th>
        <th scope="col">Status</th>
        <th scope="col">Assignee</th>
        <th scope="col">Last seen</th>
      </tr>
    </thead>
    <tbody>
      {% for alert in alerts %}
      <tr>
        <td data-label="Severity">{% with severity = alert.severity %}{% include "_severity.html" %}{% endwith %}</td>
        <td data-label="Alert"><a href="/alerts/{{ alert.finding_id }}">{{ alert.title }}</a></td>
        <td data-label="Source → destination" class="mono">{{ alert.src_ip }} → {{ alert.dst_ip }}:{{ alert.dst_port }}</td>
        <td data-label="Count">{{ alert.count }}</td>
        <td data-label="Status">{{ status_labels.get(alert.status, alert.status) }}</td>
        <td data-label="Assignee">{{ alert.assignee or "—" }}</td>
        <td data-label="Last seen">{{ alert.last_seen | utc_time }}</td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
  {% else %}
  <p class="empty">No alerts{% if status or severity %} match these filters{% endif %}.
    <a href="/upload">Upload a capture</a> to check it.</p>
  {% endif %}
</div>
{% endblock %}
```

and the upload page, `upload.html`:

```html
{% extends "base.html" %}
{# Upload page (Ahmad, AHM-02). The form posts to the JSON API; app.js shows the
   answer as plain text. The request waits for the whole analysis, AI included. #}
{% block title %}Upload{% endblock %}
{% block content %}
<h1>Upload a capture</h1>
<p>Choose a <code>.pcap</code> or <code>.pcapng</code> capture, or a <code>.zip</code> or
  <code>.tar.gz</code> of Zeek logs. It is analyzed on this computer and then deleted.</p>

<form id="upload-form" class="card" method="post" action="/api/analyses"
      enctype="multipart/form-data"
      hx-post="/api/analyses" hx-encoding="multipart/form-data" hx-swap="none"
      hx-indicator="#upload-busy" hx-disabled-elt="find button">
  <label for="file">Capture or log archive</label>
  <input id="file" name="file" type="file" required
         accept=".pcap,.pcapng,.cap,.zip,.tar.gz,.tgz">
  <button type="submit">Analyze</button>
  <p id="upload-busy" class="htmx-indicator" role="status">Analyzing… this can take a few minutes.</p>
</form>

<p id="upload-result" role="status" aria-live="polite"></p>
<p><a href="/">Go to the alert queue</a></p>
{% endblock %}
```

No template uses `|safe`: titles, addresses and names come from network traffic, which an attacker writes. The queue links each alert to its detail page, which arrives in AHM-03.

**Step 5.** Create `maxguard/web/static/app.css` (it already holds the styles for the pages of AHM-03 and AHM-06):

```css
/* MaxGuard dashboard styles (Ahmad, AHM-02). System fonts only: nothing is
   downloaded. Colors meet WCAG AA contrast; severity is always text + color. */

:root {
  --bg: #f6f7f9;
  --panel: #ffffff;
  --text: #1b1f24;
  --muted: #57606a;
  --line: #d0d7de;
  --accent: #0b5cad;
  --focus: #e36209;
  --critical: #82071e;
  --high: #b42318;
  --medium: #8a5300;
  --low: #0b5cad;
  --info: #57606a;
}

* { box-sizing: border-box; }

body {
  margin: 0;
  background: var(--bg);
  color: var(--text);
  font: 16px/1.5 system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
}

a { color: var(--accent); }
a:focus-visible, button:focus-visible, select:focus-visible, input:focus-visible,
[tabindex]:focus-visible {
  outline: 3px solid var(--focus);
  outline-offset: 2px;
}

.skip { position: absolute; left: -9999px; }
.skip:focus { left: 16px; top: 8px; background: var(--panel); padding: 8px; z-index: 1; }

.top {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px 24px;
  padding: 12px 16px;
  background: #0d1b2a;
  color: #ffffff;
}
.brand { font-weight: 700; font-size: 1.2rem; }
.top nav { display: flex; flex-wrap: wrap; gap: 4px 16px; }
.top nav a { color: #ffffff; text-decoration: none; padding: 4px 0; }
.top nav a:hover { text-decoration: underline; }
.mode-switch { margin-left: auto; display: flex; align-items: center; gap: 4px; }
.mode-switch button { background: transparent; color: #ffffff; border: 1px solid #8fa3b8; }
.mode-switch button[aria-pressed="true"] { background: #ffffff; color: #0d1b2a; font-weight: 700; }

.privacy {
  margin: 0;
  padding: 6px 16px;
  background: #dff3e4;
  color: #14532d;
  font-size: 0.9rem;
}

main { max-width: 1200px; margin: 0 auto; padding: 16px; }
h1 { font-size: 1.6rem; margin: 8px 0 16px; overflow-wrap: anywhere; }
h2 { font-size: 1.2rem; margin-top: 32px; }

.card { background: var(--panel); border: 1px solid var(--line); border-radius: 6px; padding: 16px; }
.muted { color: var(--muted); }
.mono { font-family: ui-monospace, "SFMono-Regular", Menlo, Consolas, monospace; font-size: 0.9em; overflow-wrap: anywhere; }
.empty { background: var(--panel); border: 1px dashed var(--line); padding: 16px; }
.error { color: var(--high); font-weight: 600; }
.message { margin: 8px 0 0; font-weight: 600; }

button {
  font: inherit;
  padding: 6px 14px;
  border-radius: 4px;
  border: 1px solid var(--accent);
  background: var(--accent);
  color: #ffffff;
  cursor: pointer;
}
button.secondary { background: var(--panel); color: var(--accent); }
button[disabled] { opacity: 0.6; cursor: wait; }
select, input[type="text"], input[type="file"] {
  font: inherit;
  padding: 5px 8px;
  border: 1px solid var(--muted);
  border-radius: 4px;
  background: var(--panel);
  color: var(--text);
  max-width: 100%;
}

.filters { display: flex; flex-wrap: wrap; align-items: center; gap: 8px 12px; margin-bottom: 16px; }
.status-form, #upload-form { display: grid; gap: 8px; max-width: 420px; }

/* Severity badges: the word is always there; the color only helps. */
.sev {
  display: inline-block;
  padding: 1px 8px;
  border-radius: 10px;
  color: #ffffff;
  font-weight: 700;
  font-size: 0.85rem;
  white-space: nowrap;
}
.sev-critical { background: var(--critical); }
.sev-high { background: var(--high); }
.sev-medium { background: var(--medium); }
.sev-low { background: var(--low); }
.sev-info { background: var(--info); }

table { width: 100%; border-collapse: collapse; background: var(--panel); }
caption { text-align: left; color: var(--muted); padding: 4px 0; }
th, td { text-align: left; padding: 8px; border-bottom: 1px solid var(--line); vertical-align: top; }
th { background: #eef1f4; }
.table-wrap { overflow-x: auto; }
tr:target { background: #fff3c4; }  /* the evidence row a citation link points to */

.facts { display: grid; grid-template-columns: max-content 1fr; gap: 4px 16px; }
.facts dt { font-weight: 600; }
.facts dd { margin: 0; }

.banner {
  border: 2px solid var(--medium);
  background: #fff4d6;
  padding: 12px 16px;
  border-radius: 6px;
  margin-bottom: 12px;
}
.ai-sentences li { margin-bottom: 8px; }
.chip {
  display: inline-block;
  margin-left: 4px;
  padding: 0 6px;
  border: 1px solid var(--line);
  border-radius: 10px;
  background: #eef1f4;
  font-size: 0.8rem;
  text-decoration: none;
}
.controls { padding-left: 20px; }
.controls li { margin-bottom: 8px; }
.version { font-weight: 400; color: var(--muted); font-size: 0.9rem; }

.home-view h1 { font-size: 1.5rem; }
.home-view .sev { font-size: 1rem; padding: 4px 12px; }
.home-action { font-size: 1.2rem; font-weight: 600; }

/* htmx shows this while a request runs (its own inline style is switched off: CSP). */
.htmx-indicator { display: none; }
.htmx-request .htmx-indicator, .htmx-request.htmx-indicator { display: block; }

/* Phones (375 px): each table row becomes a small card with labels. */
@media (max-width: 700px) {
  .stack thead { position: absolute; left: -9999px; }
  .stack tr { display: block; border-bottom: 2px solid var(--line); padding: 4px 0; }
  .stack td { display: grid; grid-template-columns: 9rem 1fr; gap: 8px; border: 0; padding: 4px 8px; }
  .stack td::before {
    content: attr(data-label);
    font: 600 0.9rem system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
    color: var(--muted);
  }
  .stack td .sev { justify-self: start; }
  .facts { grid-template-columns: 1fr; }
  .facts dd { margin-bottom: 8px; }
  .mode-switch { margin-left: 0; }
}
```

and `maxguard/web/static/app.js`, the only script besides htmx:

```javascript
// MaxGuard dashboard script (Ahmad, AHM-02). Everything else is htmx.
// 1) Live refresh: the server sends "alerts-changed" on /api/stream; the alert
//    table reloads itself on "refresh" (it also polls every 30 s as a fallback).
// 2) Upload: /api/analyses answers JSON; show it as plain text (textContent,
//    never innerHTML, because an error message can contain a file name).
"use strict";

document.addEventListener("DOMContentLoaded", function () {
  if (document.getElementById("alerts") && window.EventSource) {
    const stream = new EventSource("/api/stream");
    stream.addEventListener("alerts-changed", function () {
      htmx.trigger("#alerts", "refresh");
    });
  }

  const form = document.getElementById("upload-form");
  if (form) {
    form.addEventListener("htmx:afterRequest", function (event) {
      document.getElementById("upload-result").textContent = uploadMessage(event.detail.xhr);
    });
  }
});

function uploadMessage(xhr) {
  let body = {};
  try {
    body = JSON.parse(xhr.responseText);
  } catch (error) {
    body = {};
  }
  if (xhr.status === 200) {
    const n = body.findings;
    return "Done: " + n + " finding" + (n === 1 ? "" : "s") + ". They are in the alert queue.";
  }
  if (xhr.status === 0) {
    return "Upload failed: the MaxGuard server could not be reached.";
  }
  const detail = typeof body.detail === "string" ? body.detail : "error " + xhr.status;
  return "Upload failed: " + detail;
}
```

The live refresh: the server sends `alerts-changed` on `/api/stream`, and the table reloads itself; `hx-trigger="refresh, every 30s"` is the fallback. The upload answer is written with `textContent`, never `innerHTML`, because an error message can contain a file name.

**Step 6.** Create the tests `tests/unit/test_web.py`:

```python
"""Tests for the dashboard pages (Ahmad, AHM-02).

Reports come from maxguard.pipeline.analyze on the Zeek log fixtures (no Zeek,
no AI) and are saved through the stores, exactly as the upload endpoint does.
"""

from __future__ import annotations

import copy
import hashlib
import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from maxguard.api.app import STATIC_DIR, create_app
from maxguard.pipeline import analyze

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures" / "zeek"
HTMX_SHA256 = "d6fdc75f204e6bdefa99b69bf1e6d4ac69b8a364f77929f45c13476b4000f717"
RECEIVED_AT = 1791300000.0  # a fixed "upload time" (Oct 2026), so tests never read the clock
HOSTILE = "<script>alert('xss')</script>"


@pytest.fixture(scope="module")
def telnet_report(tmp_path_factory) -> dict:
    return analyze(FIXTURES / "telnet", tmp_path_factory.mktemp("telnet"), explain=False)


@pytest.fixture(scope="module")
def ftp_report(tmp_path_factory) -> dict:
    return analyze(FIXTURES / "ftp", tmp_path_factory.mktemp("ftp"), explain=False)


@pytest.fixture
def app(tmp_path):
    return create_app(tmp_path / "data", explain=False)


@pytest.fixture
def client(app) -> TestClient:
    return TestClient(app)


def save(app, report: dict, received_at: float = RECEIVED_AT) -> str:
    """Store a report the way POST /api/analyses does."""
    analysis_id = app.state.state_store.save_analysis(report, received_at=received_at)
    app.state.event_store.write(report.get("events", []))
    return analysis_id


def with_ai_sentences(report: dict) -> dict:
    """A copy of the report with one AI sentence per finding, citing its evidence."""
    report = copy.deepcopy(report)
    for finding in report["findings"]:
        ids = [e["record_id"] for e in finding["evidence"]]
        finding["explanation_sentences"] = [
            {"text": "A device logged in with Telnet, so the session was readable.",
             "evidence_ids": ids}]
        finding["explanation"] = finding["explanation_sentences"][0]["text"]
    report["ai"] = {"status": "ok", "model": "qwen3:4b", "explained": len(report["findings"]),
                    "dropped_sentences": 0, "reason": None}
    return report


def telnet_id(report: dict) -> str:
    return report["findings"][0]["finding_id"]


# ---------- AHM-02: layout, queue, upload ----------

def test_htmx_file_is_the_reviewed_one():
    data = (STATIC_DIR / "htmx-2.0.11.min.js").read_bytes()
    assert hashlib.sha256(data).hexdigest() == HTMX_SHA256


@pytest.mark.parametrize("path", ["/", "/upload"])
def test_pages_return_200_with_the_layout(client, path):
    page = client.get(path)
    assert page.status_code == 200
    assert "Your data never leaves this computer." in page.text
    assert '<script src="/static/htmx-2.0.11.min.js"' in page.text
    assert 'href="/static/app.css"' in page.text
    csp = page.headers["content-security-policy"]
    assert "default-src 'self'" in csp and "script-src 'self';" in csp
    assert "unsafe" not in csp  # no inline scripts, no eval: a second wall behind escaping
    # not "no-referrer": Chrome then sends "Origin: null" on form posts, which the API refuses
    assert page.headers["referrer-policy"] == "same-origin"


def test_static_files_are_served(client):
    assert client.get("/static/app.js").status_code == 200
    assert client.get("/static/app.css").status_code == 200


def test_queue_lists_the_telnet_alert(app, client, telnet_report):
    save(app, telnet_report)
    page = client.get("/")
    assert "Telnet session in cleartext" in page.text
    assert f'href="/alerts/{telnet_id(telnet_report)}"' in page.text
    assert "172.18.0.3 → 172.18.0.2:23" in page.text
    # severity as text and color: the word is in the badge with the color class
    assert '<span class="sev sev-high">High</span>' in page.text


def test_queue_has_the_htmx_wiring(client):
    page = client.get("/")
    assert 'hx-trigger="refresh, every 30s"' in page.text
    assert page.text.count('hx-get="/" hx-target="#alerts" hx-select="#alerts"') == 2
    assert 'new EventSource("/api/stream")' in client.get("/static/app.js").text


def test_queue_filters(app, client, telnet_report, ftp_report):
    save(app, telnet_report)
    save(app, ftp_report, received_at=RECEIVED_AT + 1)
    app.state.state_store.update_alert(telnet_id(telnet_report), actor="test",
                                       at=RECEIVED_AT + 2, status="resolved")
    resolved = client.get("/?status=resolved&severity=").text
    assert "Telnet session in cleartext" in resolved
    assert "FTP" not in resolved.split('id="alerts"')[1]
    new = client.get("/", params={"status": "new"}).text
    assert "Telnet session in cleartext" not in new
    low = client.get("/", params={"severity": "low"}).text
    assert "No alerts match these filters" in low


def test_unknown_filter_value_is_a_400_page(client):
    page = client.get("/?status=bogus")
    assert page.status_code == 400
    assert "status must be one of" in page.text


def test_hostile_values_are_escaped(app, client, telnet_report):
    report = with_ai_sentences(telnet_report)
    finding = report["findings"][0]
    finding["title"] = HOSTILE
    finding["details"] = {"user": HOSTILE}
    finding["explanation_sentences"][0]["text"] = HOSTILE
    save(app, report)
    app.state.state_store.update_alert(finding["finding_id"], actor="test",
                                       at=RECEIVED_AT, assignee=HOSTILE)
    for path in ("/",):  # the alert page comes in AHM-03
        page = client.get(path).text
        assert HOSTILE not in page
        assert "&lt;script&gt;" in page


@pytest.mark.parametrize("mode", ["analyst", "home"])
def test_no_page_loads_anything_from_outside(app, client, telnet_report, mode):
    save(app, with_ai_sentences(telnet_report))
    client.cookies.set("mg_mode", mode)
    pages = ["/", "/upload"]
    for path in pages:
        for url in re.findall(r'(?:src|href|action|hx-[a-z]+)="([^"]*)"', client.get(path).text):
            assert not url.startswith(("http:", "https:", "//")), (path, url)


def test_mode_switch_sets_the_cookie(client):
    answer = client.post("/mode", data={"mode": "home", "next": "/assets"},
                         follow_redirects=False)
    assert answer.status_code == 303
    assert answer.headers["location"] == "/assets"
    cookie = answer.headers["set-cookie"].lower()
    assert "mg_mode=home" in cookie and "httponly" in cookie and "samesite=lax" in cookie


# Browsers read /\evil.example like //evil.example: another website.
@pytest.mark.parametrize("next_path", ["//evil.example/", "/\\evil.example/",
                                       "https://evil.example/", "javascript:alert(1)"])
def test_mode_switch_never_redirects_off_site(client, next_path):
    answer = client.post("/mode", data={"mode": "home", "next": next_path},
                         follow_redirects=False)
    assert answer.headers["location"] == "/"


def test_cross_site_mode_switch_is_refused(client):
    answer = client.post("/mode", data={"mode": "home"},
                         headers={"Sec-Fetch-Site": "cross-site"})
    assert answer.status_code == 403


def test_upload_page_posts_to_the_api(client):
    page = client.get("/upload").text
    assert 'hx-post="/api/analyses"' in page
    assert 'hx-encoding="multipart/form-data"' in page
    assert 'href="/"' in page
```

Run them:

```bash
pytest tests/unit/test_web.py -q
```

Expected output:

```text
..................                                                                           [100%]
18 passed in 1.19s
```

**Step 7.** Start the server and check the headers every page sends:

```bash
# terminal 1:
uvicorn maxguard.api.app:create_app --factory --host 127.0.0.1 --port 8000
# terminal 2:
curl -s -D - -o /dev/null http://127.0.0.1:8000/ | grep -i -E '^(content-security-policy|referrer-policy|x-content-type-options):'
```

Expected output:

```text
content-security-policy: default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self'; connect-src 'self'; form-action 'self'; base-uri 'none'; object-src 'none'; frame-ancestors 'none'
x-content-type-options: nosniff
referrer-policy: same-origin
```

**Step 8.** Open http://127.0.0.1:8000, upload `tests/fixtures/zeek/telnet` as a `.zip` on the Upload page, and watch the alert appear in the queue in another tab without reloading. Then check the pages in a 375-pixel-wide window (your browser's device toolbar) and with the keyboard only (Tab, Enter, arrow keys). In planning, Chromium at 375 px showed no sideways scrolling, and every control was reachable with Tab.

**Step 9.** Commit, push, and open the pull request:

```bash
git add -A
git status          # only this task's files: nothing from .venv/, data/ or lab/captures/
git commit -m "feat: dashboard layout, alert queue and upload page (AHM-02)"
git push -u origin HEAD
```

`HEAD` means "the branch I am on", so you do not have to retype its name. Open the repository on github.com: a yellow bar shows your branch with a **Compare & pull request** button. Click it, keep the title `feat: dashboard layout, alert queue and upload page (AHM-02)`, fill in the template (paste the real output of the commands above under **How I tested it**), write `Closes #<issue number>` (this task's issue), and pick **@JWinborne1** under **Reviewers**. Click **Create pull request**, then fix anything CI or the reviewer finds with new commits on the same branch.

#### How to test

`pytest tests/unit/test_web.py -q` passes. Uploading the Telnet fixture logs on http://127.0.0.1:8000/upload makes the Telnet alert appear in the queue in another tab without reloading the page.

#### What you just did and why

Server-rendered pages with htmx keep the whole dashboard in Python and one small, vendored JavaScript file, so it works offline and every dependency is accounted for. Escaping everything matters because alert titles and hosts come from network traffic, which an attacker controls (`docs/ARCHITECTURE.md` section 14).

#### Pull request checklist

- [ ] `ruff check .` prints `All checks passed!`
- [ ] `pytest -m "not integration" -q` passes on your laptop
- [ ] The pull request title has the form `type: summary (TASK-ID)` and the body says `Closes #<issue number>`
- [ ] No secrets, passwords, email addresses, personal data, or captures from a real network (CLAUDE.md rule 6)
- [ ] Any new dependency has a row in `docs/DEPENDENCIES.md` with its license
- [ ] CI is green and your reviewer approved
- [ ] The htmx file's SHA-256 matches
- [ ] Nothing loads from outside the app
- [ ] Usable with the keyboard and at 375 px

### AHM-03: Alert detail page with Analyst and Home modes

**Due:** Week 4 (due Fri Nov 6) · **Milestone:** `W4 Full offline report` · **Needs first:** [AHM-02](#ahm-02-dashboard-layout-alert-queue-and-upload-page), [JON-02](jonattan.md#jon-02-ollama-client-one-evidence-citing-explanation-per-finding), [JON-04](jonattan.md#jon-04-home-mode-text-for-every-rule) · **Kind:** code, tested

**Issue labels:** `type:task` `phase:alpha` `owner:ahmad` `area:ui` `critical-path`

#### Goal

Show one alert in full. Analyst mode: evidence records, controls grouped by framework (with version), ATT&CK techniques, and the AI's sentences, each followed by links to the records it cites, plus the status and assignee form. Home mode: the headline, the severity in plain words, and one action, with no jargon.

#### Prerequisites

AHM-02, JON-02 (AI sentences) and JON-04 (Home text) are merged.

#### Steps

**Step 1.** Update `main` and create your branch for this task (one branch per task):

```bash
cd ~/projects/maxguard
source .venv/bin/activate
git checkout main && git pull
git checkout -b ahmad/alert-detail
```

If `source .venv/bin/activate` fails, you have not made the virtual environment yet: do Week 0 section 0.11 first.

**Step 2.** Extend `maxguard/web/routes.py` with the alert page and the status form (the new parts are under `# ---------- AHM-03`; the queue now passes the Home text too):

```python
"""The dashboard's HTML pages (Ahmad, AHM-02, AHM-03).

create_app() in maxguard/api/app.py includes this router when it imports.

    GET   /                             alert queue (filters: ?status=&severity=)
    GET   /upload                       upload form (posts to /api/analyses)
    GET   /alerts/{finding_id}          one alert, Analyst or Home mode
    PATCH /alerts/{finding_id}/status   change status/assignee, returns the form again
    POST  /mode                         Analyst/Home switch (cookie mg_mode)

The pages read the stores only through request.app.state. Jinja2 escapes every
value; nothing from traffic or from the AI is ever marked |safe, because an
attacker writes the traffic (docs/ARCHITECTURE.md section 14).
"""

from __future__ import annotations

import time
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import quote, unquote

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates

from maxguard.ai import load_home_text
from maxguard.api.app import notify_change
from maxguard.models import SEVERITIES
from maxguard.storage.state import ALERT_STATUSES

router = APIRouter()
TEMPLATES = Jinja2Templates(directory=Path(__file__).resolve().parent / "templates")

MODES = ("analyst", "home")
YEAR_SECONDS = 365 * 24 * 3600
MAX_NAME_LENGTH = 100      # the same limit as "actor" in PATCH /api/alerts

# Home mode: the severity in plain words (no jargon), and color is never the only signal.
SEVERITY_WORDS = {
    "critical": "Critical: fix this today",
    "high": "High: fix this week",
    "medium": "Medium: fix this month",
    "low": "Low: fix when you can",
    "info": "Info: nothing to fix, good to know",
}
STATUS_LABELS = {"new": "New", "investigating": "Investigating", "resolved": "Resolved",
                 "false_positive": "False positive"}

# Sent with every page. The dashboard needs nothing from outside this computer, so the
# browser is told to refuse anything else, even if some text ever slipped past escaping.
SECURITY_HEADERS = {
    "Content-Security-Policy": (
        "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self'; "
        "connect-src 'self'; form-action 'self'; base-uri 'none'; object-src 'none'; "
        "frame-ancestors 'none'"),
    "X-Content-Type-Options": "nosniff",
    # "same-origin", not "no-referrer": with no-referrer, Chrome sends "Origin: null" on
    # form posts, and the API's cross-site check (rightly) refuses those.
    "Referrer-Policy": "same-origin",
}


# ---------- small helpers ----------

def now() -> float:
    """The clock, in one place (the web layer may read it; the engine never does)."""
    return time.time()


def utc_time(ts: float | None) -> str:
    """Unix seconds -> "2026-10-06 14:03:22 UTC" (the same on every machine)."""
    if ts is None:
        return ""
    return datetime.fromtimestamp(ts, tz=UTC).strftime("%Y-%m-%d %H:%M:%S UTC")


TEMPLATES.env.filters["utc_time"] = utc_time


def mode_of(request: Request) -> str:
    """"home" or "analyst" (the default) from the mg_mode cookie."""
    return "home" if request.cookies.get("mg_mode") == "home" else "analyst"


def actor_of(request: Request) -> str:
    """The display name stored in the mg_actor cookie ("" when not set yet or not valid)."""
    name = unquote(request.cookies.get("mg_actor", "")).strip()
    return name if valid_name(name) else ""


def valid_name(name: str) -> bool:
    """1 to 100 printable characters. A line break or another control character
    could fake an extra line in the audit trail, so it is refused."""
    return 0 < len(name) <= MAX_NAME_LENGTH and name.isprintable()


def render(request: Request, name: str, context: dict, status_code: int = 200) -> HTMLResponse:
    """Render a template with the values every page needs, plus the security headers."""
    full = {"mode": mode_of(request), "severities": SEVERITIES,
            "severity_words": SEVERITY_WORDS, "status_labels": STATUS_LABELS, **context}
    response = TEMPLATES.TemplateResponse(request, name, full, status_code=status_code)
    response.headers.update(SECURITY_HEADERS)
    return response


def error_page(request: Request, status_code: int, message: str) -> HTMLResponse:
    return render(request, "error.html", {"message": message}, status_code=status_code)


def empty_to_none(value: str | None) -> str | None:
    """A filter <select> sends "" for "All"."""
    return value or None


def safe_next(path: str) -> str:
    """Only a path on this site: "//evil.example" or "https://..." would be an open redirect."""
    if path.startswith("/") and not path.startswith("//") and "\\" not in path:
        return path
    return "/"


# ---------- AHM-02: queue, upload, mode switch ----------

@router.get("/", response_class=HTMLResponse)
def queue(request: Request, status: str | None = None, severity: str | None = None):
    status, severity = empty_to_none(status), empty_to_none(severity)
    try:
        alerts = request.app.state.state_store.list_alerts(status=status, severity=severity)
    except ValueError as err:  # unknown status or severity in the URL
        return error_page(request, 400, str(err))
    return render(request, "queue.html", {
        "alerts": alerts, "status": status or "", "severity": severity or "",
        "statuses": ALERT_STATUSES, "home_text": load_home_text(),
    })


@router.get("/upload", response_class=HTMLResponse)
def upload_page(request: Request):
    return render(request, "upload.html", {})


@router.post("/mode")
async def switch_mode(request: Request):
    """The Analyst/Home switch: a plain form, so it works with the keyboard and without
    JavaScript. The cookie is only a display preference, not a security setting."""
    form = await request.form()
    mode = form.get("mode")
    response = RedirectResponse(safe_next(str(form.get("next", "/"))), status_code=303)
    if mode in MODES:
        response.set_cookie("mg_mode", mode, max_age=YEAR_SECONDS, path="/",
                            samesite="lax", httponly=True)
    return response


# ---------- AHM-03: alert detail ----------

def controls_by_framework(controls: list[dict]) -> list[dict]:
    """[{"framework", "version", "controls": [...]}, ...] in the order they first appear."""
    groups: dict[tuple[str, str], list[dict]] = {}
    for control in controls:
        groups.setdefault((control["framework"], control["version"]), []).append(control)
    return [{"framework": framework, "version": version, "controls": items}
            for (framework, version), items in groups.items()]


def ai_status(request: Request, alert: dict) -> dict:
    """The "ai" part of the report that last updated this alert."""
    report = request.app.state.state_store.get_analysis(alert["analysis_id"]) or {}
    return report.get("ai") or {"status": "disabled", "reason": None}


def status_context(alert: dict, actor: str, message: str = "") -> dict:
    return {"alert": alert, "actor": actor, "statuses": ALERT_STATUSES, "message": message}


@router.get("/alerts/{finding_id}", response_class=HTMLResponse)
def alert_detail(request: Request, finding_id: str):
    alert = request.app.state.state_store.get_alert(finding_id)
    if alert is None:
        return error_page(request, 404, "No alert with this ID. It may have been removed.")
    return render(request, "alert.html", {
        **status_context(alert, actor_of(request)),
        "groups": controls_by_framework(alert["controls"]),
        "ai": ai_status(request, alert),
        "home": load_home_text().get(alert["rule_id"]),
    })


@router.patch("/alerts/{finding_id}/status", response_class=HTMLResponse)
async def change_status(request: Request, finding_id: str):
    """Called by the htmx form on the alert page; returns the form again (a fragment).
    The first time, the form also sends the person's display name ("actor"), which
    is stored in the mg_actor cookie so the page does not ask again."""
    form = await request.form()
    actor = actor_of(request) or str(form.get("actor", "")).strip()
    store = request.app.state.state_store
    alert = store.get_alert(finding_id)
    if alert is None:
        return error_page(request, 404, "No alert with this ID.")
    if not valid_name(actor):
        return render(request, "_status.html", status_context(
            alert, "", f"Type your name (1 to {MAX_NAME_LENGTH} characters) first."), 400)
    try:
        alert = store.update_alert(
            finding_id, actor=actor, at=now(),
            status=empty_to_none(str(form.get("status", ""))),
            assignee=str(form.get("assignee", "")).strip()[:MAX_NAME_LENGTH])
    except ValueError as err:  # unknown status
        return render(request, "_status.html", status_context(alert, actor, str(err)), 400)
    notify_change(request.app)  # open queues refresh themselves
    response = render(request, "_status.html", status_context(alert, actor, "Saved."))
    # Percent-encoded ("Jos%C3%A9"): a cookie value may only hold plain ASCII
    # (RFC 6265 section 4.1.1), and names such as "José" or "Łukasz" are not.
    response.set_cookie("mg_actor", quote(actor, safe=""), max_age=YEAR_SECONDS, path="/",
                        samesite="lax", httponly=True)
    return response


@router.get("/favicon.ico", include_in_schema=False)
def favicon() -> Response:
    """Browsers ask for this on every page; answer "nothing" instead of a 404 log line."""
    return Response(status_code=204)
```

`update_alert()` needs `at=now()`: the stores never read the clock, the web layer does, in one place (`now()`), so tests can replace it. After a change, `notify_change()` makes every open queue refresh itself. The person's name is checked **before** anything is saved (`valid_name()`: 1 to 100 printable characters) and kept in the `mg_actor` cookie percent-encoded: a cookie can only hold Latin-1 text, so a name such as *Łukasz* or *علي* used to crash the page *after* the change was saved (found by the security review).

**Step 3.** Create `maxguard/web/templates/alert.html`:

```html
{% extends "base.html" %}
{# One alert (Ahmad, AHM-03). Analyst mode: facts, AI sentences with citation links,
   evidence, controls, techniques, and the status form. Home mode: the human-written
   headline and action, and the severity in words; no IDs and no framework names.
   AI text and anything from traffic is plain, escaped text: never |safe. #}
{% block title %}{{ alert.title }}{% endblock %}
{% block content %}
<p class="back"><a href="/">← All alerts</a></p>

{% if mode == "home" %}
<article class="home-view card">
  <h1>{{ home.headline if home else alert.title }}</h1>
  <p class="home-severity">{% with severity = alert.severity %}{% include "_severity.html" %}{% endwith %}</p>
  <h2>What to do</h2>
  <p class="home-action">{{ home.action if home else "Ask the person who looks after your network to look at this alert." }}</p>
  <p class="muted">Device involved: {{ alert.src_ip }}. Last seen {{ alert.last_seen | utc_time }}.</p>
</article>
{% else %}
<h1>{{ alert.title }}</h1>
<dl class="facts">
  <dt>Severity</dt><dd>{% with severity = alert.severity %}{% include "_severity.html" %}{% endwith %} <span class="muted">(set by the rule, never by the AI)</span></dd>
  <dt>Rule</dt><dd class="mono">{{ alert.rule_id }}</dd>
  <dt>Source → destination</dt>
  <dd class="mono">{{ alert.src_ip }}
    → {{ alert.dst_ip }}:{{ alert.dst_port }} ({{ alert.protocol }})</dd>
  <dt>Seen</dt><dd>{{ alert.count }} time{{ "" if alert.count == 1 else "s" }}, first {{ alert.first_seen | utc_time }}, last {{ alert.last_seen | utc_time }}</dd>
  <dt>Detected by</dt><dd>{{ alert.source }}</dd>
  {% for key, value in alert.details | dictsort %}
  <dt>{{ key }}</dt><dd class="mono">{{ value }}</dd>
  {% endfor %}
</dl>

<section aria-labelledby="ai-heading">
  <h2 id="ai-heading">What the local AI says</h2>
  {% if ai.status == "unavailable" %}
  <div class="banner" role="alert">
    <strong>The AI explanation is not available.</strong>
    {{ ai.reason or "The local AI (Ollama) could not be reached." }}
    The alert itself is complete: the rules, not the AI, decide what is an alert.
  </div>
  {% endif %}
  {% if alert.explanation_sentences %}
  <p class="muted">About: <strong>{{ alert.title }}</strong>, severity {{ alert.severity | capitalize }} (from the rule).
    Each sentence links to the records it cites; check them before you trust it.</p>
  <ul class="ai-sentences">
    {% for sentence in alert.explanation_sentences %}
    <li>{{ sentence.text }}
      {% for record_id in sentence.evidence_ids %}<a class="chip mono" href="#ev-{{ record_id }}" title="Evidence record {{ record_id }}">{{ record_id }}</a>{% endfor %}
    </li>
    {% endfor %}
  </ul>
  {% elif ai.status != "unavailable" %}
  <p class="muted">No AI explanation for this alert{% if ai.status == "disabled" %} (the AI was switched off for this analysis){% endif %}.</p>
  {% endif %}
</section>

<section aria-labelledby="ev-heading">
  <h2 id="ev-heading">Evidence</h2>
  <div class="table-wrap">
  <table>
    <thead><tr><th scope="col">Record ID</th><th scope="col">Log</th><th scope="col">UID</th><th scope="col">Time</th></tr></thead>
    <tbody>
      {% for evidence in alert.evidence %}
      <tr id="ev-{{ evidence.record_id }}" tabindex="-1">
        <td class="mono">{{ evidence.record_id }}</td>
        <td class="mono">{{ evidence.log }}</td>
        <td class="mono">{{ evidence.uid }}</td>
        <td>{{ evidence.ts | utc_time }}</td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
  </div>
</section>

<section aria-labelledby="controls-heading">
  <h2 id="controls-heading">Compliance controls</h2>
  {% for group in groups %}
  <h3>{{ group.framework }} <span class="version">{{ group.version }}</span></h3>
  <ul class="controls">
    {% for control in group.controls %}
    <li><span class="mono">{{ control.control_id }}</span> {{ control.title }}
      <div class="muted">{{ control.rationale }}</div></li>
    {% endfor %}
  </ul>
  {% else %}
  <p class="muted">No compliance controls are mapped to this rule.</p>
  {% endfor %}
</section>

<section aria-labelledby="attack-heading">
  <h2 id="attack-heading">MITRE ATT&amp;CK techniques</h2>
  {% if alert.attack %}
  <ul class="controls">
    {% for technique in alert.attack %}
    <li><span class="mono">{{ technique.technique_id }}</span> {{ technique.name }}
      <span class="muted">tactic: {{ technique.tactic }} · ATT&amp;CK {{ technique.version }}</span></li>
    {% endfor %}
  </ul>
  {% else %}
  <p class="muted">No ATT&amp;CK technique is mapped to this rule.</p>
  {% endif %}
</section>

<section aria-labelledby="status-heading">
  <h2 id="status-heading">Status and assignee</h2>
  {% include "_status.html" %}
</section>
{% endif %}
{% endblock %}
```

and the status form fragment `_status.html`, which the `PATCH` answer replaces in place:

```html
{# The status and assignee form (Ahmad, AHM-03). PATCH /alerts/{id}/status returns
   this fragment again, and htmx swaps it in place. The display name is asked for
   once and then kept in the mg_actor cookie (for the audit trail, not security). #}
<form id="status-form" class="card status-form"
      hx-patch="/alerts/{{ alert.finding_id }}/status" hx-target="this" hx-swap="outerHTML">
  {% if actor %}
  <p class="muted">Changes are recorded in the audit trail as <strong>{{ actor }}</strong>.</p>
  {% else %}
  <label for="actor">Your name (asked once, for the audit trail)</label>
  <input id="actor" name="actor" type="text" maxlength="100" required autocomplete="name">
  {% endif %}
  <label for="alert-status">Status</label>
  <select id="alert-status" name="status">
    {% for value in statuses %}
    <option value="{{ value }}" {% if value == alert.status %}selected{% endif %}>{{ status_labels[value] }}</option>
    {% endfor %}
  </select>
  <label for="assignee">Assignee</label>
  <input id="assignee" name="assignee" type="text" maxlength="100" value="{{ alert.assignee or '' }}">
  <button type="submit">Save</button>
  {% if message %}<p class="message" role="status">{{ message }}</p>{% endif %}
</form>
```

Each evidence row has `id="ev-<record_id>"`, and every AI sentence is followed by links to the rows it cites: that is how an analyst checks the AI instead of trusting it (CLAUDE.md rule 3). Above the sentences the page repeats the rule's title and severity and says the severity comes from the rule. In Home mode the page shows the headline and action from `load_home_text()`, the severity in words ("High: fix this week") and the device's address, and no rule, record, framework or technique IDs. The status form appears in Analyst mode only: its words, such as "False positive", are jargon.

**Step 4.** In Home mode the queue shows the Home headline instead of the rule title. Update `maxguard/web/templates/queue.html`:

```html
{% extends "base.html" %}
{# The alert queue (Ahmad, AHM-02). The filters swap only the #alerts table; the
   table also reloads itself on "refresh" (sent by app.js when the server says
   alerts changed) and every 30 seconds in case the live stream is down. #}
{% block title %}Alerts{% endblock %}
{% block content %}
<h1>Alerts</h1>

<form id="filters" class="filters" method="get" action="/">
  <label for="status">Status</label>
  <select id="status" name="status"
          hx-get="/" hx-target="#alerts" hx-select="#alerts" hx-swap="outerHTML"
          hx-include="#filters" hx-push-url="true">
    <option value="">All</option>
    {% for value in statuses %}
    <option value="{{ value }}" {% if value == status %}selected{% endif %}>{{ status_labels[value] }}</option>
    {% endfor %}
  </select>
  <label for="severity">Severity</label>
  <select id="severity" name="severity"
          hx-get="/" hx-target="#alerts" hx-select="#alerts" hx-swap="outerHTML"
          hx-include="#filters" hx-push-url="true">
    <option value="">All</option>
    {% for value in severities %}
    <option value="{{ value }}" {% if value == severity %}selected{% endif %}>{{ value | capitalize }}</option>
    {% endfor %}
  </select>
  {# Without JavaScript the selects do nothing on their own; this button still works. #}
  <button type="submit" class="secondary">Apply</button>
</form>

<div id="alerts" hx-get="/?status={{ status | urlencode }}&amp;severity={{ severity | urlencode }}"
     hx-trigger="refresh, every 30s" hx-select="#alerts" hx-swap="outerHTML" aria-live="polite">
  {% if alerts %}
  <table class="stack">
    <caption>{{ alerts | length }} alert{{ "" if alerts | length == 1 else "s" }}, most severe first</caption>
    <thead>
      <tr>
        <th scope="col">Severity</th>
        <th scope="col">Alert</th>
        <th scope="col">Source → destination:port</th>
        <th scope="col">Count</th>
        <th scope="col">Status</th>
        <th scope="col">Assignee</th>
        <th scope="col">Last seen</th>
      </tr>
    </thead>
    <tbody>
      {% for alert in alerts %}
      {% set home = home_text.get(alert.rule_id) %}
      <tr>
        <td data-label="Severity">{% with severity = alert.severity %}{% include "_severity.html" %}{% endwith %}</td>
        <td data-label="Alert"><a href="/alerts/{{ alert.finding_id }}">{% if mode == "home" and home %}{{ home.headline }}{% else %}{{ alert.title }}{% endif %}</a></td>
        <td data-label="Source → destination" class="mono">{{ alert.src_ip }} → {{ alert.dst_ip }}:{{ alert.dst_port }}</td>
        <td data-label="Count">{{ alert.count }}</td>
        <td data-label="Status">{{ status_labels.get(alert.status, alert.status) }}</td>
        <td data-label="Assignee">{{ alert.assignee or "—" }}</td>
        <td data-label="Last seen">{{ alert.last_seen | utc_time }}</td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
  {% else %}
  <p class="empty">No alerts{% if status or severity %} match these filters{% endif %}.
    <a href="/upload">Upload a capture</a> to check it.</p>
  {% endif %}
</div>
{% endblock %}
```

**Step 5.** Add the AHM-03 tests to `tests/unit/test_web.py` (the new section is `# ---------- AHM-03`):

```python
"""Tests for the dashboard pages (Ahmad, AHM-02, AHM-03).

Reports come from maxguard.pipeline.analyze on the Zeek log fixtures (no Zeek,
no AI) and are saved through the stores, exactly as the upload endpoint does.
"""

from __future__ import annotations

import copy
import hashlib
import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from maxguard.api.app import STATIC_DIR, create_app
from maxguard.pipeline import analyze
from maxguard.web import routes

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures" / "zeek"
HTMX_SHA256 = "d6fdc75f204e6bdefa99b69bf1e6d4ac69b8a364f77929f45c13476b4000f717"
RECEIVED_AT = 1791300000.0  # a fixed "upload time" (Oct 2026), so tests never read the clock
HOSTILE = "<script>alert('xss')</script>"


@pytest.fixture(scope="module")
def telnet_report(tmp_path_factory) -> dict:
    return analyze(FIXTURES / "telnet", tmp_path_factory.mktemp("telnet"), explain=False)


@pytest.fixture(scope="module")
def ftp_report(tmp_path_factory) -> dict:
    return analyze(FIXTURES / "ftp", tmp_path_factory.mktemp("ftp"), explain=False)


@pytest.fixture
def app(tmp_path):
    return create_app(tmp_path / "data", explain=False)


@pytest.fixture
def client(app) -> TestClient:
    return TestClient(app)


def save(app, report: dict, received_at: float = RECEIVED_AT) -> str:
    """Store a report the way POST /api/analyses does."""
    analysis_id = app.state.state_store.save_analysis(report, received_at=received_at)
    app.state.event_store.write(report.get("events", []))
    return analysis_id


def with_ai_sentences(report: dict) -> dict:
    """A copy of the report with one AI sentence per finding, citing its evidence."""
    report = copy.deepcopy(report)
    for finding in report["findings"]:
        ids = [e["record_id"] for e in finding["evidence"]]
        finding["explanation_sentences"] = [
            {"text": "A device logged in with Telnet, so the session was readable.",
             "evidence_ids": ids}]
        finding["explanation"] = finding["explanation_sentences"][0]["text"]
    report["ai"] = {"status": "ok", "model": "qwen3:4b", "explained": len(report["findings"]),
                    "dropped_sentences": 0, "reason": None}
    return report


def telnet_id(report: dict) -> str:
    return report["findings"][0]["finding_id"]


# ---------- AHM-02: layout, queue, upload ----------

def test_htmx_file_is_the_reviewed_one():
    data = (STATIC_DIR / "htmx-2.0.11.min.js").read_bytes()
    assert hashlib.sha256(data).hexdigest() == HTMX_SHA256


@pytest.mark.parametrize("path", ["/", "/upload"])
def test_pages_return_200_with_the_layout(client, path):
    page = client.get(path)
    assert page.status_code == 200
    assert "Your data never leaves this computer." in page.text
    assert '<script src="/static/htmx-2.0.11.min.js"' in page.text
    assert 'href="/static/app.css"' in page.text
    csp = page.headers["content-security-policy"]
    assert "default-src 'self'" in csp and "script-src 'self';" in csp
    assert "unsafe" not in csp  # no inline scripts, no eval: a second wall behind escaping
    # not "no-referrer": Chrome then sends "Origin: null" on form posts, which the API refuses
    assert page.headers["referrer-policy"] == "same-origin"


def test_static_files_are_served(client):
    assert client.get("/static/app.js").status_code == 200
    assert client.get("/static/app.css").status_code == 200


def test_queue_lists_the_telnet_alert(app, client, telnet_report):
    save(app, telnet_report)
    page = client.get("/")
    assert "Telnet session in cleartext" in page.text
    assert f'href="/alerts/{telnet_id(telnet_report)}"' in page.text
    assert "172.18.0.3 → 172.18.0.2:23" in page.text
    # severity as text and color: the word is in the badge with the color class
    assert '<span class="sev sev-high">High</span>' in page.text


def test_queue_has_the_htmx_wiring(client):
    page = client.get("/")
    assert 'hx-trigger="refresh, every 30s"' in page.text
    assert page.text.count('hx-get="/" hx-target="#alerts" hx-select="#alerts"') == 2
    assert 'new EventSource("/api/stream")' in client.get("/static/app.js").text


def test_queue_filters(app, client, telnet_report, ftp_report):
    save(app, telnet_report)
    save(app, ftp_report, received_at=RECEIVED_AT + 1)
    app.state.state_store.update_alert(telnet_id(telnet_report), actor="test",
                                       at=RECEIVED_AT + 2, status="resolved")
    resolved = client.get("/?status=resolved&severity=").text
    assert "Telnet session in cleartext" in resolved
    assert "FTP" not in resolved.split('id="alerts"')[1]
    new = client.get("/", params={"status": "new"}).text
    assert "Telnet session in cleartext" not in new
    low = client.get("/", params={"severity": "low"}).text
    assert "No alerts match these filters" in low


def test_unknown_filter_value_is_a_400_page(client):
    page = client.get("/?status=bogus")
    assert page.status_code == 400
    assert "status must be one of" in page.text


def test_hostile_values_are_escaped(app, client, telnet_report):
    report = with_ai_sentences(telnet_report)
    finding = report["findings"][0]
    finding["title"] = HOSTILE
    finding["details"] = {"user": HOSTILE}
    finding["explanation_sentences"][0]["text"] = HOSTILE
    save(app, report)
    app.state.state_store.update_alert(finding["finding_id"], actor="test",
                                       at=RECEIVED_AT, assignee=HOSTILE)
    for path in ("/", f"/alerts/{finding['finding_id']}"):
        page = client.get(path).text
        assert HOSTILE not in page
        assert "&lt;script&gt;" in page


@pytest.mark.parametrize("mode", ["analyst", "home"])
def test_no_page_loads_anything_from_outside(app, client, telnet_report, mode):
    save(app, with_ai_sentences(telnet_report))
    client.cookies.set("mg_mode", mode)
    pages = ["/", "/upload", f"/alerts/{telnet_id(telnet_report)}"]
    for path in pages:
        for url in re.findall(r'(?:src|href|action|hx-[a-z]+)="([^"]*)"', client.get(path).text):
            assert not url.startswith(("http:", "https:", "//")), (path, url)


def test_mode_switch_sets_the_cookie(client):
    answer = client.post("/mode", data={"mode": "home", "next": "/assets"},
                         follow_redirects=False)
    assert answer.status_code == 303
    assert answer.headers["location"] == "/assets"
    cookie = answer.headers["set-cookie"].lower()
    assert "mg_mode=home" in cookie and "httponly" in cookie and "samesite=lax" in cookie


# Browsers read /\evil.example like //evil.example: another website.
@pytest.mark.parametrize("next_path", ["//evil.example/", "/\\evil.example/",
                                       "https://evil.example/", "javascript:alert(1)"])
def test_mode_switch_never_redirects_off_site(client, next_path):
    answer = client.post("/mode", data={"mode": "home", "next": next_path},
                         follow_redirects=False)
    assert answer.headers["location"] == "/"


def test_cross_site_mode_switch_is_refused(client):
    answer = client.post("/mode", data={"mode": "home"},
                         headers={"Sec-Fetch-Site": "cross-site"})
    assert answer.status_code == 403


def test_upload_page_posts_to_the_api(client):
    page = client.get("/upload").text
    assert 'hx-post="/api/analyses"' in page
    assert 'hx-encoding="multipart/form-data"' in page
    assert 'href="/"' in page


# ---------- AHM-03: alert detail ----------

def test_alert_detail_analyst_mode(app, client, telnet_report):
    report = with_ai_sentences(telnet_report)
    save(app, report)
    page = client.get(f"/alerts/{telnet_id(report)}").text
    finding = report["findings"][0]
    assert finding["evidence"][0]["record_id"] in page
    assert "NIST SP 800-53" in page
    assert "Rev. 5 (Release 5.2.0)" in page  # the version next to the framework
    assert "T1040" in page and "credential-access" in page
    assert "A device logged in with Telnet" in page
    assert 'id="status-form"' in page


def test_controls_are_grouped_by_framework():
    controls = [
        {"framework": "PCI DSS", "version": "4.0.1", "control_id": "4.2.1"},
        {"framework": "NIST SP 800-53", "version": "Rev. 5 (Release 5.2.0)", "control_id": "SC-8"},
        {"framework": "PCI DSS", "version": "4.0.1", "control_id": "8.3.2"},
    ]
    groups = routes.controls_by_framework(controls)
    assert [(g["framework"], len(g["controls"])) for g in groups] == [
        ("PCI DSS", 2), ("NIST SP 800-53", 1)]


def test_citation_links_point_to_evidence_rows(app, client, telnet_report):
    report = with_ai_sentences(telnet_report)
    save(app, report)
    page = client.get(f"/alerts/{telnet_id(report)}").text
    cited = re.findall(r'href="#ev-([0-9a-f]+)"', page)
    assert cited  # at least one citation chip
    for record_id in cited:
        assert f'id="ev-{record_id}"' in page


def test_alert_detail_home_mode(app, client, telnet_report):
    report = with_ai_sentences(telnet_report)
    save(app, report)
    finding = report["findings"][0]
    client.cookies.set("mg_mode", "home")
    page = client.get(f"/alerts/{finding['finding_id']}").text
    home = routes.load_home_text()["cleartext.telnet"]
    assert home["headline"] in page
    assert home["action"] in page
    assert "High: fix this week" in page
    main = page.split('<main id="main"', 1)[1]  # the page body, not the URLs in the nav
    for jargon in (finding["evidence"][0]["record_id"], "cleartext.telnet", "NIST",
                   "PCI DSS", "CISA", "CJIS", "T1040", "ATT&amp;CK"):
        assert jargon not in main.replace(f"/alerts/{finding['finding_id']}", "")


def test_unknown_alert_is_a_404_page(client):
    page = client.get("/alerts/0000000000000000")
    assert page.status_code == 404
    assert "No alert with this ID" in page.text


def test_ai_unavailable_banner_shows_the_reason(app, client, telnet_report):
    report = copy.deepcopy(telnet_report)
    reason = "model 'qwen3:4b' not found: run ollama pull qwen3:4b"
    report["ai"] = {"status": "unavailable", "model": "qwen3:4b", "explained": 0,
                    "dropped_sentences": 0, "reason": reason}
    save(app, report)
    page = client.get(f"/alerts/{telnet_id(report)}").text
    assert 'class="banner" role="alert"' in page
    assert "model &#39;qwen3:4b&#39; not found: run ollama pull qwen3:4b" in page


def test_no_banner_when_the_ai_worked(app, client, telnet_report):
    save(app, with_ai_sentences(telnet_report))
    assert 'class="banner"' not in client.get(f"/alerts/{telnet_id(telnet_report)}").text


def test_status_change_is_saved_and_audited(app, client, telnet_report):
    save(app, telnet_report)
    finding_id = telnet_id(telnet_report)
    answer = client.patch(f"/alerts/{finding_id}/status",
                          data={"actor": "Ahmad", "status": "investigating",
                                "assignee": "Fiona"})
    assert answer.status_code == 200
    assert "Saved." in answer.text
    assert "mg_actor=Ahmad" in answer.headers["set-cookie"]
    alert = app.state.state_store.get_alert(finding_id)
    assert (alert["status"], alert["assignee"]) == ("investigating", "Fiona")
    audit = app.state.state_store.list_audit()
    assert audit[0]["actor"] == "Ahmad"
    assert audit[0]["target"] == finding_id
    assert audit[0]["details"]["status"] == {"from": "new", "to": "investigating"}


def test_status_change_uses_the_name_cookie(app, client, telnet_report):
    save(app, telnet_report)
    client.cookies.set("mg_actor", "Jaiden")
    answer = client.patch(f"/alerts/{telnet_id(telnet_report)}/status",
                          data={"status": "resolved", "assignee": ""})
    assert answer.status_code == 200
    assert app.state.state_store.list_audit()[0]["actor"] == "Jaiden"


def test_status_change_needs_a_name(app, client, telnet_report):
    save(app, telnet_report)
    answer = client.patch(f"/alerts/{telnet_id(telnet_report)}/status",
                          data={"status": "resolved"})
    assert answer.status_code == 400
    assert "Type your name" in answer.text
    assert app.state.state_store.list_audit() == []


def test_unknown_status_is_refused(app, client, telnet_report):
    save(app, telnet_report)
    answer = client.patch(f"/alerts/{telnet_id(telnet_report)}/status",
                          data={"actor": "Ahmad", "status": "deleted"})
    assert answer.status_code == 400


def test_status_change_refreshes_open_queues(app, client, telnet_report):
    save(app, telnet_report)
    before = app.state.changes  # /api/stream sends alerts-changed when this goes up
    client.patch(f"/alerts/{telnet_id(telnet_report)}/status",
                 data={"actor": "Ahmad", "status": "investigating"})
    assert app.state.changes == before + 1


@pytest.mark.parametrize("name", ["José", "Łukasz", "علي", "Ann Lee"])
def test_any_name_works_and_is_remembered(app, client, telnet_report, name):
    save(app, telnet_report)
    path = f"/alerts/{telnet_id(telnet_report)}/status"
    first = client.patch(path, data={"actor": name, "status": "investigating"})
    assert first.status_code == 200
    second = client.patch(path, data={"status": "resolved"})  # the name now comes from the cookie
    assert second.status_code == 200
    assert [row["actor"] for row in app.state.state_store.list_audit()] == [name, name]


@pytest.mark.parametrize("name", ["Ann\nAdmin approved", "Ann\x00", " ", "x" * 101])
def test_bad_names_are_refused(app, client, telnet_report, name):
    save(app, telnet_report)
    answer = client.patch(f"/alerts/{telnet_id(telnet_report)}/status",
                          data={"actor": name, "status": "resolved"})
    assert answer.status_code == 400
    assert app.state.state_store.list_audit() == []


def test_cross_site_status_change_is_refused(app, client, telnet_report):
    save(app, telnet_report)
    answer = client.patch(f"/alerts/{telnet_id(telnet_report)}/status",
                          data={"actor": "x", "status": "resolved"},
                          headers={"Origin": "http://evil.example"})
    assert answer.status_code == 403
    assert app.state.state_store.get_alert(telnet_id(telnet_report))["status"] == "new"
```

Run them:

```bash
pytest tests/unit/test_web.py -q
```

Expected output:

```text
.......................................                                                      [100%]
39 passed in 2.64s
```

**Step 6.** Open an alert in both modes and change its status with the keyboard only. Then ask someone who is not technical to read the Home view of the Telnet alert and say what they would do.

**Step 7.** Commit, push, and open the pull request:

```bash
git add -A
git status          # only this task's files: nothing from .venv/, data/ or lab/captures/
git commit -m "feat: alert detail with Analyst and Home modes (AHM-03)"
git push -u origin HEAD
```

`HEAD` means "the branch I am on", so you do not have to retype its name. Open the repository on github.com: a yellow bar shows your branch with a **Compare & pull request** button. Click it, keep the title `feat: alert detail with Analyst and Home modes (AHM-03)`, fill in the template (paste the real output of the commands above under **How I tested it**), write `Closes #<issue number>` (this task's issue), and pick **@JWinborne1** under **Reviewers**. Click **Create pull request**, then fix anything CI or the reviewer finds with new commits on the same branch.

#### How to test

The tests pass, and a non-technical friend can read the Home view of the Telnet alert and say what to do.

#### What you just did and why

The citation links are how an analyst checks the AI instead of trusting it: every sentence leads to the exact record behind it (CLAUDE.md rule 3). Home mode exists because most small-network owners are not analysts; the same alert, in plain words, with one action, is what makes them act.

#### Pull request checklist

- [ ] `ruff check .` prints `All checks passed!`
- [ ] `pytest -m "not integration" -q` passes on your laptop
- [ ] The pull request title has the form `type: summary (TASK-ID)` and the body says `Closes #<issue number>`
- [ ] No secrets, passwords, email addresses, personal data, or captures from a real network (CLAUDE.md rule 6)
- [ ] Any new dependency has a row in `docs/DEPENDENCIES.md` with its license
- [ ] CI is green and your reviewer approved
- [ ] No `|safe` on traffic or AI text
- [ ] Status changes appear in the audit trail

### AHM-04: Security review of the alpha

**Due:** Week 5 (due Fri Nov 13) · **Milestone:** `W5 Alpha feature freeze` · **Needs first:** [AHM-03](#ahm-03-alert-detail-page-with-analyst-and-home-modes), [JON-03](jonattan.md#jon-03-offline-guard-make-accidental-network-access-fail-loudly), [AMO-03](amory.md#amo-03-report-export-json-csv-and-html) · **Kind:** process

**Issue labels:** `type:task` `phase:alpha` `owner:ahmad` `area:program`

#### Goal

Before the feature freeze, walk through every threat in `docs/ARCHITECTURE.md` section 14 against the real code and record, for each, how it is defended and how you checked.

#### Prerequisites

The alpha features are merged (AHM-03, JON-03, AMO-03 at least).

#### Steps

**Step 1.** For each row of the threat table, find the code and the test that defend it, and try the attack yourself where it is safe: a zip whose files unpack to more than 4 GiB, a file named `../../x` inside a tar, an HTTP host name containing `<script>` in a capture, a CSV cell starting with `=`, the dashboard from another machine on the LAN.

**Step 2.** Run `pip-audit` (or GitHub's Dependabot alerts) on the installed packages and check Zeek's, Suricata's and Ollama's release notes for security fixes since our pinned versions.

**Step 3.** Write `docs/security-review-alpha.md`: one row per threat with *defense*, *how checked*, *result*, and an issue link for anything that failed (label `type:bug` and `critical-path` if it blocks the release).

#### How to test

Every threat has a result, and every failure has an issue with an owner.

#### What you just did and why

A security tool with a security hole is worse than no tool. Checking the defenses against the running code, not against the design document, is the Security Lead's job before the alpha goes to an outside tester.

#### Pull request checklist

- [ ] Every threat in section 14 has a result
- [ ] Every failure has an issue

### AHM-05: Alpha acceptance test and presentation

**Due:** Week 8 (due Fri Dec 4) · **Milestone:** `W8 v2.0-alpha` · **Needs first:** [JAI-10](jaiden.md#jai-10-release-v20-alpha), [KAR-05](karthik.md#kar-05-release-candidate-test-with-an-outside-tester) · **Kind:** process

**Issue labels:** `type:task` `phase:alpha` `owner:ahmad` `area:program` `critical-path`

#### Goal

Run the `v2.0-alpha` acceptance test with someone who did not build the release, record each result, and give the end-of-semester presentation.

#### Prerequisites

JAI-10 has tagged `v2.0-alpha`.

#### Steps

**Step 1.** Follow the acceptance test in `docs/roadmap/README.md` with the tester; write the result of each step in the findings log.

**Step 2.** Prepare the presentation: the problem, the architecture (section 1 diagram), a live demo of upload → alert → explanation with citations → Home mode, what is next in spring, and what each person built.

#### How to test

All ten acceptance steps pass, or the failures are documented with issues.

#### What you just did and why

A release is done when someone else can install and use it, not when the code is merged.

#### Pull request checklist

- [ ] Acceptance results recorded
- [ ] Presentation delivered

## Spring 2027: v2.0

### AHM-06: IP timeline and device inventory pages

**Due:** Spring S1-S4 (due Fri Feb 12, 2027) · **Milestone:** `S1-S4 Live sensor` · **Needs first:** [AHM-03](#ahm-03-alert-detail-page-with-analyst-and-home-modes), [JAK-08](jakub.md#jak-08-device-attribution-which-device-is-behind-each-ip-address), [JAI-07](jaiden.md#jai-07-the-api-uploads-alerts-events-live-updates-sensor-ingest), [JAK-07](jakub.md#jak-07-live-sensor-capture-rotation-and-shipping-to-the-console) · **Kind:** code, tested

**Issue labels:** `type:task` `phase:spring` `owner:ahmad` `area:ui`

#### Goal

Add `/timeline?ip=` (everything one address did, in time order, with links to the alerts that involve it) and `/assets` (the device inventory with MAC addresses and names from device attribution).

#### Prerequisites

AHM-03 and JAK-08 (device attribution) are merged.

#### Steps

**Step 1.** Update `main` and create your branch for this task (one branch per task):

```bash
cd ~/projects/maxguard
source .venv/bin/activate
git checkout main && git pull
git checkout -b ahmad/timeline-devices
```

If `source .venv/bin/activate` fails, you have not made the virtual environment yet: do Week 0 section 0.11 first.

**Step 2.** The device table (JAK-08) must travel in the report: the log folder is deleted after an upload, so the dashboard cannot rebuild it later. In `maxguard/pipeline.py`, import `build_device_table` next to `build_inventory` and add a `devices` key after `assets` (a new optional report key, so nothing that reads reports breaks; tell Jaiden in the pull request):

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
from maxguard.adapters.live import LiveSensorAdapter
from maxguard.adapters.pcap import PcapAdapter
from maxguard.adapters.zeeklogs import ZeekLogAdapter
from maxguard.mapping.loader import ATTACK, apply, load_all
from maxguard.models import SEVERITIES, Finding
from maxguard.rules.base import run_all

# Order matters only for clarity: each adapter accepts a different kind of input
# (a capture file; a folder with conn.log; a sensor folder with zeek/<interval>/).
ADAPTERS = [PcapAdapter(), ZeekLogAdapter(), LiveSensorAdapter()]
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


def analyze(path, workdir, frameworks=None, explain=True, mapping_dir=None,
            sensor_id=None) -> dict:
    """1) pick adapter  2) get logs  3) run rules  4) apply mappings
    5) build inventory and events  6) ask the local AI  7) return report dict

    sensor_id names where the data came from in every event: by default "pcap" for
    a capture and "import" for Zeek logs; the API passes the sensor's name for data
    a sensor or host agent sent to POST /api/ingest."""
    path, workdir = Path(path), Path(workdir)
    adapter = pick_adapter(path)
    log_dir = adapter.to_zeek_logs(path, workdir)

    findings = sorted(run_all(log_dir), key=sort_key)

    fw_files = load_all(Path(mapping_dir) if mapping_dir else mappings_dir())
    apply(findings, fw_files, set(frameworks) if frameworks else None)

    from maxguard.events.normalize import normalize
    from maxguard.inventory import build as build_inventory
    from maxguard.sensor.attribution import build_device_table

    if sensor_id is None:
        sensor_id = "pcap" if adapter.name == "pcap" else "import"
    events = normalize(log_dir, sensor_id=sensor_id)
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
        # MAC address, host name and DNS names per IP, from DHCP and DNS (JAK-08). The
        # log folder is deleted after an upload, so the dashboard reads them from here.
        "devices": build_device_table(log_dir),
        "events": events,
        "ai": ai,
    }
```

Update `tests/unit/test_pipeline.py`: the report's key list gains `devices`, and a new test checks the DHCP fixture's laptop:

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
                           "devices", "events", "ai"}
    assert report["ai"]["status"] == "disabled"


def test_report_names_the_devices_from_dhcp_and_dns(tmp_path):
    report = analyze(FIXTURES / "_handmade" / "dns_dhcp", tmp_path, explain=False)
    [device] = [d for d in report["devices"] if d["mac"]]
    assert device["ip"] == "192.168.56.50"
    assert device["host_name"] == "laptop-lab"


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

**Step 3.** Add the timeline and the devices page to `maxguard/web/routes.py` (the new section is `# ---------- AHM-06`):

```python
"""The dashboard's HTML pages (Ahmad, AHM-02, AHM-03, AHM-06).

create_app() in maxguard/api/app.py includes this router when it imports.

    GET   /                             alert queue (filters: ?status=&severity=)
    GET   /upload                       upload form (posts to /api/analyses)
    GET   /alerts/{finding_id}          one alert, Analyst or Home mode
    PATCH /alerts/{finding_id}/status   change status/assignee, returns the form again
    POST  /mode                         Analyst/Home switch (cookie mg_mode)
    GET   /timeline?ip=&hours=&end=     everything one address did (AHM-06)
    GET   /assets                       device inventory (AHM-06)

The pages read the stores only through request.app.state. Jinja2 escapes every
value; nothing from traffic or from the AI is ever marked |safe, because an
attacker writes the traffic (docs/ARCHITECTURE.md section 14).
"""

from __future__ import annotations

import ipaddress
import time
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import quote, unquote

from fastapi import APIRouter, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates

from maxguard.ai import load_home_text
from maxguard.api.app import notify_change
from maxguard.inventory import ip_sort_key
from maxguard.models import SEVERITIES
from maxguard.storage.state import ALERT_STATUSES

router = APIRouter()
TEMPLATES = Jinja2Templates(directory=Path(__file__).resolve().parent / "templates")

MODES = ("analyst", "home")
YEAR_SECONDS = 365 * 24 * 3600
MAX_NAME_LENGTH = 100      # the same limit as "actor" in PATCH /api/alerts
TIMELINE_HOURS = {1: "Last hour", 6: "Last 6 hours", 24: "Last 24 hours", 72: "Last 3 days",
                  168: "Last 7 days"}  # the window selector: up to the 7 days events are kept
TIMELINE_LIMIT = 1000

# Home mode: the severity in plain words (no jargon), and color is never the only signal.
SEVERITY_WORDS = {
    "critical": "Critical: fix this today",
    "high": "High: fix this week",
    "medium": "Medium: fix this month",
    "low": "Low: fix when you can",
    "info": "Info: nothing to fix, good to know",
}
STATUS_LABELS = {"new": "New", "investigating": "Investigating", "resolved": "Resolved",
                 "false_positive": "False positive"}

# Sent with every page. The dashboard needs nothing from outside this computer, so the
# browser is told to refuse anything else, even if some text ever slipped past escaping.
SECURITY_HEADERS = {
    "Content-Security-Policy": (
        "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self'; "
        "connect-src 'self'; form-action 'self'; base-uri 'none'; object-src 'none'; "
        "frame-ancestors 'none'"),
    "X-Content-Type-Options": "nosniff",
    # "same-origin", not "no-referrer": with no-referrer, Chrome sends "Origin: null" on
    # form posts, and the API's cross-site check (rightly) refuses those.
    "Referrer-Policy": "same-origin",
}


# ---------- small helpers ----------

def now() -> float:
    """The clock, in one place (the web layer may read it; the engine never does)."""
    return time.time()


def utc_time(ts: float | None) -> str:
    """Unix seconds -> "2026-10-06 14:03:22 UTC" (the same on every machine)."""
    if ts is None:
        return ""
    return datetime.fromtimestamp(ts, tz=UTC).strftime("%Y-%m-%d %H:%M:%S UTC")


TEMPLATES.env.filters["utc_time"] = utc_time


def mode_of(request: Request) -> str:
    """"home" or "analyst" (the default) from the mg_mode cookie."""
    return "home" if request.cookies.get("mg_mode") == "home" else "analyst"


def actor_of(request: Request) -> str:
    """The display name stored in the mg_actor cookie ("" when not set yet or not valid)."""
    name = unquote(request.cookies.get("mg_actor", "")).strip()
    return name if valid_name(name) else ""


def valid_name(name: str) -> bool:
    """1 to 100 printable characters. A line break or another control character
    could fake an extra line in the audit trail, so it is refused."""
    return 0 < len(name) <= MAX_NAME_LENGTH and name.isprintable()


def render(request: Request, name: str, context: dict, status_code: int = 200) -> HTMLResponse:
    """Render a template with the values every page needs, plus the security headers."""
    full = {"mode": mode_of(request), "severities": SEVERITIES,
            "severity_words": SEVERITY_WORDS, "status_labels": STATUS_LABELS, **context}
    response = TEMPLATES.TemplateResponse(request, name, full, status_code=status_code)
    response.headers.update(SECURITY_HEADERS)
    return response


def error_page(request: Request, status_code: int, message: str) -> HTMLResponse:
    return render(request, "error.html", {"message": message}, status_code=status_code)


def empty_to_none(value: str | None) -> str | None:
    """A filter <select> sends "" for "All"."""
    return value or None


def safe_next(path: str) -> str:
    """Only a path on this site: "//evil.example" or "https://..." would be an open redirect."""
    if path.startswith("/") and not path.startswith("//") and "\\" not in path:
        return path
    return "/"


# ---------- AHM-02: queue, upload, mode switch ----------

@router.get("/", response_class=HTMLResponse)
def queue(request: Request, status: str | None = None, severity: str | None = None):
    status, severity = empty_to_none(status), empty_to_none(severity)
    try:
        alerts = request.app.state.state_store.list_alerts(status=status, severity=severity)
    except ValueError as err:  # unknown status or severity in the URL
        return error_page(request, 400, str(err))
    return render(request, "queue.html", {
        "alerts": alerts, "status": status or "", "severity": severity or "",
        "statuses": ALERT_STATUSES, "home_text": load_home_text(),
    })


@router.get("/upload", response_class=HTMLResponse)
def upload_page(request: Request):
    return render(request, "upload.html", {})


@router.post("/mode")
async def switch_mode(request: Request):
    """The Analyst/Home switch: a plain form, so it works with the keyboard and without
    JavaScript. The cookie is only a display preference, not a security setting."""
    form = await request.form()
    mode = form.get("mode")
    response = RedirectResponse(safe_next(str(form.get("next", "/"))), status_code=303)
    if mode in MODES:
        response.set_cookie("mg_mode", mode, max_age=YEAR_SECONDS, path="/",
                            samesite="lax", httponly=True)
    return response


# ---------- AHM-03: alert detail ----------

def controls_by_framework(controls: list[dict]) -> list[dict]:
    """[{"framework", "version", "controls": [...]}, ...] in the order they first appear."""
    groups: dict[tuple[str, str], list[dict]] = {}
    for control in controls:
        groups.setdefault((control["framework"], control["version"]), []).append(control)
    return [{"framework": framework, "version": version, "controls": items}
            for (framework, version), items in groups.items()]


def ai_status(request: Request, alert: dict) -> dict:
    """The "ai" part of the report that last updated this alert."""
    report = request.app.state.state_store.get_analysis(alert["analysis_id"]) or {}
    return report.get("ai") or {"status": "disabled", "reason": None}


def status_context(alert: dict, actor: str, message: str = "") -> dict:
    return {"alert": alert, "actor": actor, "statuses": ALERT_STATUSES, "message": message}


@router.get("/alerts/{finding_id}", response_class=HTMLResponse)
def alert_detail(request: Request, finding_id: str):
    alert = request.app.state.state_store.get_alert(finding_id)
    if alert is None:
        return error_page(request, 404, "No alert with this ID. It may have been removed.")
    return render(request, "alert.html", {
        **status_context(alert, actor_of(request)),
        "groups": controls_by_framework(alert["controls"]),
        "ai": ai_status(request, alert),
        "home": load_home_text().get(alert["rule_id"]),
    })


@router.patch("/alerts/{finding_id}/status", response_class=HTMLResponse)
async def change_status(request: Request, finding_id: str):
    """Called by the htmx form on the alert page; returns the form again (a fragment).
    The first time, the form also sends the person's display name ("actor"), which
    is stored in the mg_actor cookie so the page does not ask again."""
    form = await request.form()
    actor = actor_of(request) or str(form.get("actor", "")).strip()
    store = request.app.state.state_store
    alert = store.get_alert(finding_id)
    if alert is None:
        return error_page(request, 404, "No alert with this ID.")
    if not valid_name(actor):
        return render(request, "_status.html", status_context(
            alert, "", f"Type your name (1 to {MAX_NAME_LENGTH} characters) first."), 400)
    try:
        alert = store.update_alert(
            finding_id, actor=actor, at=now(),
            status=empty_to_none(str(form.get("status", ""))),
            assignee=str(form.get("assignee", "")).strip()[:MAX_NAME_LENGTH])
    except ValueError as err:  # unknown status
        return render(request, "_status.html", status_context(alert, actor, str(err)), 400)
    notify_change(request.app)  # open queues refresh themselves
    response = render(request, "_status.html", status_context(alert, actor, "Saved."))
    # Percent-encoded ("Jos%C3%A9"): a cookie value may only hold plain ASCII
    # (RFC 6265 section 4.1.1), and names such as "José" or "Łukasz" are not.
    response.set_cookie("mg_actor", quote(actor, safe=""), max_age=YEAR_SECONDS, path="/",
                        samesite="lax", httponly=True)
    return response


# ---------- AHM-06: timeline and assets ----------

def alerts_for_ip(request: Request, ip: str) -> list[dict]:
    """Alerts where this address is the source or the destination."""
    alerts = request.app.state.state_store.list_alerts(limit=1000)
    return [a for a in alerts if ip in (a["src_ip"], a["dst_ip"])]


def evidence_links(alerts: list[dict]) -> dict[str, list[dict]]:
    """record_id, Zeek uid or Community ID -> the alerts whose evidence names it.

    A finding often cites a record that is not a timeline event (for example a
    maxguard_cleartext.log line); the connection's conn.log event shares its uid,
    so matching the uid too links the event to the alert."""
    links: dict[str, list[dict]] = {}
    for alert in alerts:
        for evidence in alert["evidence"]:
            for key in (evidence.get("record_id"), evidence.get("uid")):
                if key:
                    links.setdefault(key, []).append(alert)
    return links


def same_connection(event: dict, alert: dict) -> bool:
    """Zeek uids are not unique across captures: `zeek -D` (used for uploads, so results
    repeat) gives the first connection of every capture the same uid. So a uid match
    only counts when the event is also between the alert's two hosts, on its port."""
    return ({event["src_ip"], event["dst_ip"]} == {alert["src_ip"], alert["dst_ip"]}
            and event["dst_port"] == alert["dst_port"])


def alert_for_event(event: dict, links: dict[str, list[dict]]) -> dict | None:
    for key in (event["event_id"], event["uid"], event["community_id"]):
        for alert in links.get(key, []) if key else []:
            if same_connection(event, alert):
                return alert
    return None


# The last second Python's datetime can show (9999-12-31 23:59:59 UTC). A larger
# end=, or "nan" or "inf", gets FastAPI's 422 instead of crashing the page.
LAST_TIME = 253402300799


@router.get("/timeline", response_class=HTMLResponse)
def timeline(request: Request, ip: str = "", hours: int = Query(24, ge=1, le=168),
             end: float | None = Query(None, ge=0, le=LAST_TIME)):
    """Everything one address did in a time window (default: the last 24 hours).
    end (Unix seconds) moves the window back, for captures recorded earlier."""
    context = {"ip": ip, "hours": hours, "hour_choices": TIMELINE_HOURS, "end": end,
               "events": [], "alerts": []}
    if not ip:
        return render(request, "timeline.html", context)  # just the "which address?" form
    try:
        ip = str(ipaddress.ip_address(ip))  # also writes IPv6 the way Zeek does
    except ValueError:
        return error_page(request, 400, "That is not an IP address.")
    until = end if end is not None else now()
    events = request.app.state.event_store.query(ip=ip, since=until - hours * 3600,
                                                 until=until, limit=TIMELINE_LIMIT)
    alerts = alerts_for_ip(request, ip)
    links = evidence_links(alerts)
    rows = [{"event": event, "alert": alert_for_event(event, links)} for event in events]
    context.update(ip=ip, until=until, rows=rows, alerts=alerts, limit=TIMELINE_LIMIT)
    return render(request, "timeline.html", context)


def join_devices(assets: list[dict], devices: list[dict]) -> list[dict]:
    """Each asset plus mac, host_name and dns_names from the device table (JAK-08).

    A full join: a device seen only in DHCP or DNS (for example a phone that
    asked for an address and did nothing else yet) is still a device on the
    network, so it gets a row too. Sorted by IP address, like both inputs."""
    by_ip = {device["ip"]: device for device in devices}
    rows = {asset["ip"]: {**asset, "mac": "", "host_name": "", "dns_names": []}
            for asset in assets}
    for ip, device in by_ip.items():
        row = rows.setdefault(ip, {"ip": ip, "first_seen": device["first_seen"],
                                   "services": [], "software": [], "finding_count": 0})
        row.update(mac=device["mac"], host_name=device["host_name"],
                   dns_names=device["dns_names"])
    return [rows[ip] for ip in sorted(rows, key=ip_sort_key)]


@router.get("/assets", response_class=HTMLResponse)
def assets(request: Request):
    store = request.app.state.state_store
    newest = store.list_analyses(limit=1)
    analysis = newest[0] if newest else None
    report = store.get_analysis(analysis["analysis_id"]) if analysis else {}
    rows = join_devices(report.get("assets", []), report.get("devices", []))
    return render(request, "assets.html", {"analysis": analysis, "rows": rows})


@router.get("/favicon.ico", include_in_schema=False)
def favicon() -> Response:
    """Browsers ask for this on every page; answer "nothing" instead of a 404 log line."""
    return Response(status_code=204)
```

Two traps this code avoids. First, Zeek uids are not unique across captures: `zeek -D`, used for uploads so results repeat, gives the first connection of *every* capture the same uid, so linking an event to an alert by uid alone linked the Telnet connection to "Expired certificate". An event links to an alert only when its record ID, uid or Community ID is in the alert's evidence **and** it is between the alert's two hosts on the alert's port. Second, a finding often cites a record that is not a timeline event (a `maxguard_cleartext.log` line, for example); the connection's `conn.log` event shares its uid, which is why the uid is matched too. The window is 1, 6, 24, 72 or 168 hours; the optional `end` (Unix seconds) moves it back, so the alert page can link to the time of an old capture. The devices page is a full join: a phone seen only in DHCP still gets a row.

**Step 4.** Create `maxguard/web/templates/timeline.html` and `assets.html`:

```html
{% extends "base.html" %}
{# IP timeline (Ahmad, AHM-06): everything one address did, in time order, and the
   alerts (with their ATT&CK techniques) that involve it. #}
{% block title %}Timeline{% if ip %} {{ ip }}{% endif %}{% endblock %}
{% block content %}
<h1>Timeline{% if ip %} for <span class="mono">{{ ip }}</span>{% endif %}</h1>

<form class="filters" method="get" action="/timeline">
  <label for="ip">IP address</label>
  <input id="ip" name="ip" type="text" value="{{ ip }}" required inputmode="text"
         autocomplete="off" spellcheck="false" placeholder="192.0.2.10">
  <label for="hours">Window</label>
  <select id="hours" name="hours">
    {% for choice, label in hour_choices.items() %}
    <option value="{{ choice }}" {% if choice == hours %}selected{% endif %}>{{ label }}</option>
    {% endfor %}
  </select>
  {% if end is not none %}<input type="hidden" name="end" value="{{ end }}">{% endif %}
  <button type="submit">Show</button>
</form>

{% if ip %}
<p class="muted">From {{ (until - hours * 3600) | utc_time }} to {{ until | utc_time }}.
  {% if end is not none %}<a href="/timeline?ip={{ ip | urlencode }}&amp;hours={{ hours }}">Show the window up to now instead</a>.{% endif %}</p>

<section aria-labelledby="alerts-heading">
  <h2 id="alerts-heading">Alerts involving this address</h2>
  {% if alerts %}
  <ul class="controls">
    {% for alert in alerts %}
    <li>{% with severity = alert.severity %}{% include "_severity.html" %}{% endwith %}
      <a href="/alerts/{{ alert.finding_id }}">{{ alert.title }}</a>
      {% for technique in alert.attack %}
      <span class="chip mono" title="{{ technique.name }}, tactic {{ technique.tactic }}">{{ technique.technique_id }} {{ technique.name }} ({{ technique.tactic }})</span>
      {% endfor %}
    </li>
    {% endfor %}
  </ul>
  {% else %}
  <p class="muted">No alert involves this address.</p>
  {% endif %}
</section>

<section aria-labelledby="events-heading">
  <h2 id="events-heading">Events</h2>
  {% if rows %}
  <table class="stack">
    <caption>{{ rows | length }} event{{ "" if rows | length == 1 else "s" }}, oldest first{% if rows | length >= limit %} (only the first {{ limit }}: pick a shorter window){% endif %}</caption>
    <thead><tr><th scope="col">Time</th><th scope="col">Kind</th><th scope="col">Connection</th><th scope="col">Summary</th><th scope="col">Alert</th></tr></thead>
    <tbody>
      {% for row in rows %}
      {% set event = row.event %}
      <tr>
        <td data-label="Time">{{ event.ts | utc_time }}</td>
        <td data-label="Kind">{{ event.kind }}</td>
        <td data-label="Connection" class="mono">{{ event.src_ip }}{% if event.src_port is not none %}:{{ event.src_port }}{% endif %} → {{ event.dst_ip }}{% if event.dst_port is not none %}:{{ event.dst_port }}{% endif %}</td>
        <td data-label="Summary" class="mono">{{ event.summary }}</td>
        <td data-label="Alert">{% if row.alert %}<a href="/alerts/{{ row.alert.finding_id }}">{{ row.alert.title }}</a>{% else %}—{% endif %}</td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
  {% else %}
  <p class="empty">No events for this address in this window. Events are kept for 7 days;
    for an older capture, open the timeline from the alert page.</p>
  {% endif %}
</section>
{% endif %}
{% endblock %}
```

```html
{% extends "base.html" %}
{# Device inventory (Ahmad, AHM-06): the assets of the newest analysis joined with
   the device table from device attribution (MAC, host name, DNS names). #}
{% block title %}Devices{% endblock %}
{% block content %}
<h1>Devices</h1>
{% if analysis %}
<p class="muted">From the newest analysis: {{ analysis.input_name }}, received {{ analysis.received_at | utc_time }}.</p>
{% endif %}
{% if rows %}
<table class="stack">
  <caption>{{ rows | length }} device{{ "" if rows | length == 1 else "s" }}, by IP address</caption>
  <thead>
    <tr>
      <th scope="col">IP address</th>
      <th scope="col">MAC</th>
      <th scope="col">Host name</th>
      <th scope="col">DNS names asked for</th>
      <th scope="col">Services</th>
      <th scope="col">Software</th>
      <th scope="col">Alerts</th>
      <th scope="col">First seen</th>
    </tr>
  </thead>
  <tbody>
    {% for row in rows %}
    <tr>
      <td data-label="IP address" class="mono"><a href="/timeline?ip={{ row.ip | urlencode }}">{{ row.ip }}</a></td>
      <td data-label="MAC" class="mono">{{ row.mac or "—" }}</td>
      <td data-label="Host name">{{ row.host_name or "—" }}</td>
      <td data-label="DNS names" class="mono">{{ row.dns_names | join(", ") or "—" }}</td>
      <td data-label="Services" class="mono">{{ row.services | join(", ") or "—" }}</td>
      <td data-label="Software">{{ row.software | join(", ") or "—" }}</td>
      <td data-label="Alerts">{{ row.finding_count }}</td>
      <td data-label="First seen">{{ row.first_seen | utc_time }}</td>
    </tr>
    {% endfor %}
  </tbody>
</table>
{% else %}
<p class="empty">No devices yet. <a href="/upload">Upload a capture</a> to build the inventory.</p>
{% endif %}
{% endblock %}
```

**Step 5.** Add Timeline and Devices to the navigation in `base.html`, and link the alert page's addresses to their timelines in `alert.html`:

```html
<!doctype html>
{# The layout every page extends (Ahmad, AHM-02). Everything is served by this
   computer: no CDN, no web fonts. Jinja2 escapes every {{ value }}. #}
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  {# htmx settings: no inline <style> (our CSP blocks it), never run scripts or eval
     from a response, only talk to this site, and show 400 answers (form errors). #}
  <meta name="htmx-config" content='{"includeIndicatorStyles": false, "allowEval": false, "allowScriptTags": false, "selfRequestsOnly": true, "responseHandling": [{"code": "204", "swap": false}, {"code": "[23]..", "swap": true}, {"code": "400", "swap": true, "error": false}, {"code": "[45]..", "swap": false, "error": true}]}'>
  <title>{% block title %}MaxGuard{% endblock %} · MaxGuard</title>
  <link rel="stylesheet" href="/static/app.css">
  <script src="/static/htmx-2.0.11.min.js" defer></script>
  <script src="/static/app.js" defer></script>
</head>
<body class="mode-{{ mode }}">
  <a class="skip" href="#main">Skip to content</a>
  <header class="top">
    <div class="brand">MaxGuard</div>
    <nav aria-label="Main">
      <a href="/">Alerts</a>
      <a href="/upload">Upload</a>
      <a href="/timeline">Timeline</a>
      <a href="/assets">Devices</a>
    </nav>
    <form class="mode-switch" method="post" action="/mode">
      <input type="hidden" name="next" value="{{ request.url.path }}{% if request.url.query %}?{{ request.url.query }}{% endif %}">
      <span id="mode-label">View:</span>
      <button type="submit" name="mode" value="analyst" aria-describedby="mode-label"
              aria-pressed="{{ 'true' if mode == 'analyst' else 'false' }}">Analyst</button>
      <button type="submit" name="mode" value="home" aria-describedby="mode-label"
              aria-pressed="{{ 'true' if mode == 'home' else 'false' }}">Home</button>
    </form>
  </header>
  <p class="privacy">Your data never leaves this computer.</p>
  <main id="main" tabindex="-1">
    {% block content %}{% endblock %}
  </main>
</body>
</html>
```

```html
{% extends "base.html" %}
{# One alert (Ahmad, AHM-03). Analyst mode: facts, AI sentences with citation links,
   evidence, controls, techniques, and the status form. Home mode: the human-written
   headline and action, and the severity in words; no IDs and no framework names.
   AI text and anything from traffic is plain, escaped text: never |safe. #}
{% block title %}{{ alert.title }}{% endblock %}
{% block content %}
<p class="back"><a href="/">← All alerts</a></p>

{% if mode == "home" %}
<article class="home-view card">
  <h1>{{ home.headline if home else alert.title }}</h1>
  <p class="home-severity">{% with severity = alert.severity %}{% include "_severity.html" %}{% endwith %}</p>
  <h2>What to do</h2>
  <p class="home-action">{{ home.action if home else "Ask the person who looks after your network to look at this alert." }}</p>
  <p class="muted">Device involved: {{ alert.src_ip }}. Last seen {{ alert.last_seen | utc_time }}.</p>
</article>
{% else %}
<h1>{{ alert.title }}</h1>
<dl class="facts">
  <dt>Severity</dt><dd>{% with severity = alert.severity %}{% include "_severity.html" %}{% endwith %} <span class="muted">(set by the rule, never by the AI)</span></dd>
  <dt>Rule</dt><dd class="mono">{{ alert.rule_id }}</dd>
  <dt>Source → destination</dt>
  <dd class="mono"><a href="/timeline?ip={{ alert.src_ip | urlencode }}&amp;end={{ (alert.last_seen + 1) | int }}">{{ alert.src_ip }}</a>
    → <a href="/timeline?ip={{ alert.dst_ip | urlencode }}&amp;end={{ (alert.last_seen + 1) | int }}">{{ alert.dst_ip }}</a>:{{ alert.dst_port }} ({{ alert.protocol }})</dd>
  <dt>Seen</dt><dd>{{ alert.count }} time{{ "" if alert.count == 1 else "s" }}, first {{ alert.first_seen | utc_time }}, last {{ alert.last_seen | utc_time }}</dd>
  <dt>Detected by</dt><dd>{{ alert.source }}</dd>
  {% for key, value in alert.details | dictsort %}
  <dt>{{ key }}</dt><dd class="mono">{{ value }}</dd>
  {% endfor %}
</dl>

<section aria-labelledby="ai-heading">
  <h2 id="ai-heading">What the local AI says</h2>
  {% if ai.status == "unavailable" %}
  <div class="banner" role="alert">
    <strong>The AI explanation is not available.</strong>
    {{ ai.reason or "The local AI (Ollama) could not be reached." }}
    The alert itself is complete: the rules, not the AI, decide what is an alert.
  </div>
  {% endif %}
  {% if alert.explanation_sentences %}
  <p class="muted">About: <strong>{{ alert.title }}</strong>, severity {{ alert.severity | capitalize }} (from the rule).
    Each sentence links to the records it cites; check them before you trust it.</p>
  <ul class="ai-sentences">
    {% for sentence in alert.explanation_sentences %}
    <li>{{ sentence.text }}
      {% for record_id in sentence.evidence_ids %}<a class="chip mono" href="#ev-{{ record_id }}" title="Evidence record {{ record_id }}">{{ record_id }}</a>{% endfor %}
    </li>
    {% endfor %}
  </ul>
  {% elif ai.status != "unavailable" %}
  <p class="muted">No AI explanation for this alert{% if ai.status == "disabled" %} (the AI was switched off for this analysis){% endif %}.</p>
  {% endif %}
</section>

<section aria-labelledby="ev-heading">
  <h2 id="ev-heading">Evidence</h2>
  <div class="table-wrap">
  <table>
    <thead><tr><th scope="col">Record ID</th><th scope="col">Log</th><th scope="col">UID</th><th scope="col">Time</th></tr></thead>
    <tbody>
      {% for evidence in alert.evidence %}
      <tr id="ev-{{ evidence.record_id }}" tabindex="-1">
        <td class="mono">{{ evidence.record_id }}</td>
        <td class="mono">{{ evidence.log }}</td>
        <td class="mono">{{ evidence.uid }}</td>
        <td>{{ evidence.ts | utc_time }}</td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
  </div>
</section>

<section aria-labelledby="controls-heading">
  <h2 id="controls-heading">Compliance controls</h2>
  {% for group in groups %}
  <h3>{{ group.framework }} <span class="version">{{ group.version }}</span></h3>
  <ul class="controls">
    {% for control in group.controls %}
    <li><span class="mono">{{ control.control_id }}</span> {{ control.title }}
      <div class="muted">{{ control.rationale }}</div></li>
    {% endfor %}
  </ul>
  {% else %}
  <p class="muted">No compliance controls are mapped to this rule.</p>
  {% endfor %}
</section>

<section aria-labelledby="attack-heading">
  <h2 id="attack-heading">MITRE ATT&amp;CK techniques</h2>
  {% if alert.attack %}
  <ul class="controls">
    {% for technique in alert.attack %}
    <li><span class="mono">{{ technique.technique_id }}</span> {{ technique.name }}
      <span class="muted">tactic: {{ technique.tactic }} · ATT&amp;CK {{ technique.version }}</span></li>
    {% endfor %}
  </ul>
  {% else %}
  <p class="muted">No ATT&amp;CK technique is mapped to this rule.</p>
  {% endif %}
</section>

<section aria-labelledby="status-heading">
  <h2 id="status-heading">Status and assignee</h2>
  {% include "_status.html" %}
</section>
{% endif %}
{% endblock %}
```

**Step 6.** Add the AHM-06 tests to `tests/unit/test_web.py` (the new section is `# ---------- AHM-06`). They never depend on the real clock: they replace `routes.now` or pass `end=`:

```python
"""Tests for the dashboard pages (Ahmad, AHM-02, AHM-03, AHM-06).

Reports come from maxguard.pipeline.analyze on the Zeek log fixtures (no Zeek,
no AI) and are saved through the stores, exactly as the upload endpoint does.
"""

from __future__ import annotations

import copy
import hashlib
import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from maxguard.api.app import STATIC_DIR, create_app
from maxguard.events.normalize import EVENT_KEYS
from maxguard.pipeline import analyze
from maxguard.sensor.attribution import build_device_table
from maxguard.web import routes

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures" / "zeek"
HTMX_SHA256 = "d6fdc75f204e6bdefa99b69bf1e6d4ac69b8a364f77929f45c13476b4000f717"
RECEIVED_AT = 1791300000.0  # a fixed "upload time" (Oct 2026), so tests never read the clock
HOSTILE = "<script>alert('xss')</script>"


@pytest.fixture(scope="module")
def telnet_report(tmp_path_factory) -> dict:
    return analyze(FIXTURES / "telnet", tmp_path_factory.mktemp("telnet"), explain=False)


@pytest.fixture(scope="module")
def ftp_report(tmp_path_factory) -> dict:
    return analyze(FIXTURES / "ftp", tmp_path_factory.mktemp("ftp"), explain=False)


@pytest.fixture
def app(tmp_path):
    return create_app(tmp_path / "data", explain=False)


@pytest.fixture
def client(app) -> TestClient:
    return TestClient(app)


def save(app, report: dict, received_at: float = RECEIVED_AT) -> str:
    """Store a report the way POST /api/analyses does."""
    analysis_id = app.state.state_store.save_analysis(report, received_at=received_at)
    app.state.event_store.write(report.get("events", []))
    return analysis_id


def with_ai_sentences(report: dict) -> dict:
    """A copy of the report with one AI sentence per finding, citing its evidence."""
    report = copy.deepcopy(report)
    for finding in report["findings"]:
        ids = [e["record_id"] for e in finding["evidence"]]
        finding["explanation_sentences"] = [
            {"text": "A device logged in with Telnet, so the session was readable.",
             "evidence_ids": ids}]
        finding["explanation"] = finding["explanation_sentences"][0]["text"]
    report["ai"] = {"status": "ok", "model": "qwen3:4b", "explained": len(report["findings"]),
                    "dropped_sentences": 0, "reason": None}
    return report


def telnet_id(report: dict) -> str:
    return report["findings"][0]["finding_id"]


# ---------- AHM-02: layout, queue, upload ----------

def test_htmx_file_is_the_reviewed_one():
    data = (STATIC_DIR / "htmx-2.0.11.min.js").read_bytes()
    assert hashlib.sha256(data).hexdigest() == HTMX_SHA256


@pytest.mark.parametrize("path", ["/", "/upload", "/timeline", "/assets"])
def test_pages_return_200_with_the_layout(client, path):
    page = client.get(path)
    assert page.status_code == 200
    assert "Your data never leaves this computer." in page.text
    assert '<script src="/static/htmx-2.0.11.min.js"' in page.text
    assert 'href="/static/app.css"' in page.text
    csp = page.headers["content-security-policy"]
    assert "default-src 'self'" in csp and "script-src 'self';" in csp
    assert "unsafe" not in csp  # no inline scripts, no eval: a second wall behind escaping
    # not "no-referrer": Chrome then sends "Origin: null" on form posts, which the API refuses
    assert page.headers["referrer-policy"] == "same-origin"


def test_static_files_are_served(client):
    assert client.get("/static/app.js").status_code == 200
    assert client.get("/static/app.css").status_code == 200


def test_queue_lists_the_telnet_alert(app, client, telnet_report):
    save(app, telnet_report)
    page = client.get("/")
    assert "Telnet session in cleartext" in page.text
    assert f'href="/alerts/{telnet_id(telnet_report)}"' in page.text
    assert "172.18.0.3 → 172.18.0.2:23" in page.text
    # severity as text and color: the word is in the badge with the color class
    assert '<span class="sev sev-high">High</span>' in page.text


def test_queue_has_the_htmx_wiring(client):
    page = client.get("/")
    assert 'hx-trigger="refresh, every 30s"' in page.text
    assert page.text.count('hx-get="/" hx-target="#alerts" hx-select="#alerts"') == 2
    assert 'new EventSource("/api/stream")' in client.get("/static/app.js").text


def test_queue_filters(app, client, telnet_report, ftp_report):
    save(app, telnet_report)
    save(app, ftp_report, received_at=RECEIVED_AT + 1)
    app.state.state_store.update_alert(telnet_id(telnet_report), actor="test",
                                       at=RECEIVED_AT + 2, status="resolved")
    resolved = client.get("/?status=resolved&severity=").text
    assert "Telnet session in cleartext" in resolved
    assert "FTP" not in resolved.split('id="alerts"')[1]
    new = client.get("/", params={"status": "new"}).text
    assert "Telnet session in cleartext" not in new
    low = client.get("/", params={"severity": "low"}).text
    assert "No alerts match these filters" in low


def test_unknown_filter_value_is_a_400_page(client):
    page = client.get("/?status=bogus")
    assert page.status_code == 400
    assert "status must be one of" in page.text


def test_hostile_values_are_escaped(app, client, telnet_report):
    report = with_ai_sentences(telnet_report)
    finding = report["findings"][0]
    finding["title"] = HOSTILE
    finding["details"] = {"user": HOSTILE}
    finding["explanation_sentences"][0]["text"] = HOSTILE
    save(app, report)
    app.state.state_store.update_alert(finding["finding_id"], actor="test",
                                       at=RECEIVED_AT, assignee=HOSTILE)
    for path in ("/", f"/alerts/{finding['finding_id']}", "/timeline?ip=172.18.0.3"):
        page = client.get(path).text
        assert HOSTILE not in page
        assert "&lt;script&gt;" in page


@pytest.mark.parametrize("mode", ["analyst", "home"])
def test_no_page_loads_anything_from_outside(app, client, telnet_report, mode):
    save(app, with_ai_sentences(telnet_report))
    client.cookies.set("mg_mode", mode)
    pages = ["/", "/upload", "/assets", "/timeline?ip=172.18.0.3",
             f"/alerts/{telnet_id(telnet_report)}"]
    for path in pages:
        for url in re.findall(r'(?:src|href|action|hx-[a-z]+)="([^"]*)"', client.get(path).text):
            assert not url.startswith(("http:", "https:", "//")), (path, url)


def test_mode_switch_sets_the_cookie(client):
    answer = client.post("/mode", data={"mode": "home", "next": "/assets"},
                         follow_redirects=False)
    assert answer.status_code == 303
    assert answer.headers["location"] == "/assets"
    cookie = answer.headers["set-cookie"].lower()
    assert "mg_mode=home" in cookie and "httponly" in cookie and "samesite=lax" in cookie


# Browsers read /\evil.example like //evil.example: another website.
@pytest.mark.parametrize("next_path", ["//evil.example/", "/\\evil.example/",
                                       "https://evil.example/", "javascript:alert(1)"])
def test_mode_switch_never_redirects_off_site(client, next_path):
    answer = client.post("/mode", data={"mode": "home", "next": next_path},
                         follow_redirects=False)
    assert answer.headers["location"] == "/"


def test_cross_site_mode_switch_is_refused(client):
    answer = client.post("/mode", data={"mode": "home"},
                         headers={"Sec-Fetch-Site": "cross-site"})
    assert answer.status_code == 403


def test_upload_page_posts_to_the_api(client):
    page = client.get("/upload").text
    assert 'hx-post="/api/analyses"' in page
    assert 'hx-encoding="multipart/form-data"' in page
    assert 'href="/"' in page


# ---------- AHM-03: alert detail ----------

def test_alert_detail_analyst_mode(app, client, telnet_report):
    report = with_ai_sentences(telnet_report)
    save(app, report)
    page = client.get(f"/alerts/{telnet_id(report)}").text
    finding = report["findings"][0]
    assert finding["evidence"][0]["record_id"] in page
    assert "NIST SP 800-53" in page
    assert "Rev. 5 (Release 5.2.0)" in page  # the version next to the framework
    assert "T1040" in page and "credential-access" in page
    assert "A device logged in with Telnet" in page
    assert 'id="status-form"' in page


def test_controls_are_grouped_by_framework():
    controls = [
        {"framework": "PCI DSS", "version": "4.0.1", "control_id": "4.2.1"},
        {"framework": "NIST SP 800-53", "version": "Rev. 5 (Release 5.2.0)", "control_id": "SC-8"},
        {"framework": "PCI DSS", "version": "4.0.1", "control_id": "8.3.2"},
    ]
    groups = routes.controls_by_framework(controls)
    assert [(g["framework"], len(g["controls"])) for g in groups] == [
        ("PCI DSS", 2), ("NIST SP 800-53", 1)]


def test_citation_links_point_to_evidence_rows(app, client, telnet_report):
    report = with_ai_sentences(telnet_report)
    save(app, report)
    page = client.get(f"/alerts/{telnet_id(report)}").text
    cited = re.findall(r'href="#ev-([0-9a-f]+)"', page)
    assert cited  # at least one citation chip
    for record_id in cited:
        assert f'id="ev-{record_id}"' in page


def test_alert_detail_home_mode(app, client, telnet_report):
    report = with_ai_sentences(telnet_report)
    save(app, report)
    finding = report["findings"][0]
    client.cookies.set("mg_mode", "home")
    page = client.get(f"/alerts/{finding['finding_id']}").text
    home = routes.load_home_text()["cleartext.telnet"]
    assert home["headline"] in page
    assert home["action"] in page
    assert "High: fix this week" in page
    main = page.split('<main id="main"', 1)[1]  # the page body, not the URLs in the nav
    for jargon in (finding["evidence"][0]["record_id"], "cleartext.telnet", "NIST",
                   "PCI DSS", "CISA", "CJIS", "T1040", "ATT&amp;CK"):
        assert jargon not in main.replace(f"/alerts/{finding['finding_id']}", "")


def test_unknown_alert_is_a_404_page(client):
    page = client.get("/alerts/0000000000000000")
    assert page.status_code == 404
    assert "No alert with this ID" in page.text


def test_ai_unavailable_banner_shows_the_reason(app, client, telnet_report):
    report = copy.deepcopy(telnet_report)
    reason = "model 'qwen3:4b' not found: run ollama pull qwen3:4b"
    report["ai"] = {"status": "unavailable", "model": "qwen3:4b", "explained": 0,
                    "dropped_sentences": 0, "reason": reason}
    save(app, report)
    page = client.get(f"/alerts/{telnet_id(report)}").text
    assert 'class="banner" role="alert"' in page
    assert "model &#39;qwen3:4b&#39; not found: run ollama pull qwen3:4b" in page


def test_no_banner_when_the_ai_worked(app, client, telnet_report):
    save(app, with_ai_sentences(telnet_report))
    assert 'class="banner"' not in client.get(f"/alerts/{telnet_id(telnet_report)}").text


def test_status_change_is_saved_and_audited(app, client, telnet_report):
    save(app, telnet_report)
    finding_id = telnet_id(telnet_report)
    answer = client.patch(f"/alerts/{finding_id}/status",
                          data={"actor": "Ahmad", "status": "investigating",
                                "assignee": "Fiona"})
    assert answer.status_code == 200
    assert "Saved." in answer.text
    assert "mg_actor=Ahmad" in answer.headers["set-cookie"]
    alert = app.state.state_store.get_alert(finding_id)
    assert (alert["status"], alert["assignee"]) == ("investigating", "Fiona")
    audit = app.state.state_store.list_audit()
    assert audit[0]["actor"] == "Ahmad"
    assert audit[0]["target"] == finding_id
    assert audit[0]["details"]["status"] == {"from": "new", "to": "investigating"}


def test_status_change_uses_the_name_cookie(app, client, telnet_report):
    save(app, telnet_report)
    client.cookies.set("mg_actor", "Jaiden")
    answer = client.patch(f"/alerts/{telnet_id(telnet_report)}/status",
                          data={"status": "resolved", "assignee": ""})
    assert answer.status_code == 200
    assert app.state.state_store.list_audit()[0]["actor"] == "Jaiden"


def test_status_change_needs_a_name(app, client, telnet_report):
    save(app, telnet_report)
    answer = client.patch(f"/alerts/{telnet_id(telnet_report)}/status",
                          data={"status": "resolved"})
    assert answer.status_code == 400
    assert "Type your name" in answer.text
    assert app.state.state_store.list_audit() == []


def test_unknown_status_is_refused(app, client, telnet_report):
    save(app, telnet_report)
    answer = client.patch(f"/alerts/{telnet_id(telnet_report)}/status",
                          data={"actor": "Ahmad", "status": "deleted"})
    assert answer.status_code == 400


def test_status_change_refreshes_open_queues(app, client, telnet_report):
    save(app, telnet_report)
    before = app.state.changes  # /api/stream sends alerts-changed when this goes up
    client.patch(f"/alerts/{telnet_id(telnet_report)}/status",
                 data={"actor": "Ahmad", "status": "investigating"})
    assert app.state.changes == before + 1


@pytest.mark.parametrize("name", ["José", "Łukasz", "علي", "Ann Lee"])
def test_any_name_works_and_is_remembered(app, client, telnet_report, name):
    save(app, telnet_report)
    path = f"/alerts/{telnet_id(telnet_report)}/status"
    first = client.patch(path, data={"actor": name, "status": "investigating"})
    assert first.status_code == 200
    second = client.patch(path, data={"status": "resolved"})  # the name now comes from the cookie
    assert second.status_code == 200
    assert [row["actor"] for row in app.state.state_store.list_audit()] == [name, name]


@pytest.mark.parametrize("name", ["Ann\nAdmin approved", "Ann\x00", " ", "x" * 101])
def test_bad_names_are_refused(app, client, telnet_report, name):
    save(app, telnet_report)
    answer = client.patch(f"/alerts/{telnet_id(telnet_report)}/status",
                          data={"actor": name, "status": "resolved"})
    assert answer.status_code == 400
    assert app.state.state_store.list_audit() == []


def test_cross_site_status_change_is_refused(app, client, telnet_report):
    save(app, telnet_report)
    answer = client.patch(f"/alerts/{telnet_id(telnet_report)}/status",
                          data={"actor": "x", "status": "resolved"},
                          headers={"Origin": "http://evil.example"})
    assert answer.status_code == 403
    assert app.state.state_store.get_alert(telnet_id(telnet_report))["status"] == "new"


# ---------- AHM-06: timeline and assets ----------

def test_timeline_rejects_a_bad_address(client):
    page = client.get("/timeline", params={"ip": "not-an-ip"})
    assert page.status_code == 400
    assert "not an IP address" in page.text


def test_timeline_lists_events_and_links_the_alert(app, client, telnet_report, monkeypatch):
    save(app, telnet_report)
    last_seen = telnet_report["findings"][0]["last_seen"]
    monkeypatch.setattr(routes, "now", lambda: last_seen + 3600)  # one hour after the capture
    page = client.get("/timeline", params={"ip": "172.18.0.3"}).text
    assert "tcp/23 SF out=23 in=40" in page  # the conn.log event's summary
    # the event shares the finding's Zeek uid, so its row links to the alert
    assert page.count(f'href="/alerts/{telnet_id(telnet_report)}"') >= 2
    assert "T1040" in page  # techniques of the alerts that involve this address


def test_timeline_links_survive_repeated_zeek_uids(app, client, telnet_report, tmp_path):
    """zeek -D gives the first connection of every capture the same uid, so the
    telnet and cert_expired captures share one; each row must still link its own alert."""
    cert_report = analyze(FIXTURES / "cert_expired", tmp_path / "cert", explain=False)
    cert_uids = {e["uid"] for f in cert_report["findings"] for e in f["evidence"]}
    assert telnet_report["findings"][0]["evidence"][0]["uid"] in cert_uids  # the collision
    save(app, telnet_report)
    save(app, cert_report, received_at=RECEIVED_AT + 1)
    end = int(cert_report["findings"][0]["last_seen"]) + 1
    page = client.get("/timeline", params={"ip": "172.18.0.3", "end": end}).text
    telnet_row = next(row for row in page.split("<tr>") if "tcp/23 SF" in row)
    assert f'href="/alerts/{telnet_id(telnet_report)}"' in telnet_row
    assert cert_report["findings"][0]["finding_id"] not in telnet_row


def test_timeline_default_window_is_24_hours(app, client, telnet_report, monkeypatch):
    save(app, telnet_report)
    last_seen = telnet_report["findings"][0]["last_seen"]
    monkeypatch.setattr(routes, "now", lambda: last_seen + 2 * 24 * 3600)
    page = client.get("/timeline", params={"ip": "172.18.0.3"}).text
    assert "No events for this address in this window" in page
    week = client.get("/timeline", params={"ip": "172.18.0.3", "hours": 168}).text
    assert "tcp/23 SF out=23 in=40" in week


def test_timeline_end_moves_the_window(app, client, telnet_report):
    save(app, telnet_report)
    end = int(telnet_report["findings"][0]["last_seen"]) + 1
    page = client.get("/timeline", params={"ip": "172.18.0.3", "end": end}).text
    assert "tcp/23 SF out=23 in=40" in page


def test_timeline_finds_ipv6_typed_in_any_form(app, client):
    """Zeek writes IPv6 in short lower-case form; a user may type 2001:DB8:0::1."""
    event = dict.fromkeys(EVENT_KEYS, "")
    event.update(event_id="v6-1", ts=RECEIVED_AT, sensor_id="lab", source="zeek",
                 log="conn.log", kind="conn", uid="Cv6", src_ip="2001:db8::1",
                 dst_ip="2001:db8::2", src_port=50000, dst_port=22, proto="tcp",
                 service="ssh", bytes_out=10, bytes_in=20, summary="tcp/22 ipv6 test")
    app.state.event_store.write([event])
    page = client.get("/timeline", params={"ip": "2001:DB8:0::1", "end": RECEIVED_AT + 1}).text
    assert "tcp/22 ipv6 test" in page


def test_timeline_window_is_at_most_7_days(client):
    assert client.get("/timeline", params={"ip": "192.0.2.1", "hours": 169}).status_code == 422


@pytest.mark.parametrize("end", ["nan", "inf", "-1", "1e20"])
def test_timeline_refuses_an_impossible_end(client, end):
    assert client.get("/timeline", params={"ip": "192.0.2.1", "end": end}).status_code == 422


def test_assets_join_the_device_table(app, client, tmp_path):
    report = analyze(FIXTURES / "_handmade" / "dns_dhcp", tmp_path / "work", explain=False)
    report["devices"] = build_device_table(FIXTURES / "_handmade" / "dns_dhcp")
    save(app, report)
    page = client.get("/assets").text
    assert "02:00:00:aa:bb:cc" in page
    assert "laptop-lab" in page
    assert 'href="/timeline?ip=192.168.56.50"' in page


def test_join_devices_is_a_full_join_sorted_by_ip():
    assets = [{"ip": "192.0.2.10", "first_seen": 1.0, "services": ["23/tcp"], "software": [],
               "finding_count": 1}]
    devices = [{"ip": "192.0.2.9", "mac": "02:00:00:00:00:09", "host_name": "printer",
                "dns_names": ["printer.lab.invalid"], "first_seen": 2.0}]
    joined = routes.join_devices(assets, devices)
    assert [row["ip"] for row in joined] == ["192.0.2.9", "192.0.2.10"]  # by number, not text
    assert joined[0] == {"ip": "192.0.2.9", "first_seen": 2.0, "services": [], "software": [],
                         "finding_count": 0, "mac": "02:00:00:00:00:09",
                         "host_name": "printer", "dns_names": ["printer.lab.invalid"]}
    assert joined[1] == {**assets[0], "mac": "", "host_name": "", "dns_names": []}
```

Run the dashboard and pipeline tests:

```bash
pytest tests/unit/test_web.py tests/unit/test_pipeline.py -q
```

Expected output:

```text
.............................................................                                [100%]
61 passed in 3.65s
```

**Step 7.** Check both pages at 375 px and with the keyboard only.

**Step 8.** Commit, push, and open the pull request:

```bash
git add -A
git status          # only this task's files: nothing from .venv/, data/ or lab/captures/
git commit -m "feat: IP timeline and device inventory pages (AHM-06)"
git push -u origin HEAD
```

`HEAD` means "the branch I am on", so you do not have to retype its name. Open the repository on github.com: a yellow bar shows your branch with a **Compare & pull request** button. Click it, keep the title `feat: IP timeline and device inventory pages (AHM-06)`, fill in the template (paste the real output of the commands above under **How I tested it**), write `Closes #<issue number>` (this task's issue), and pick **@JWinborne1** under **Reviewers**. Click **Create pull request**, then fix anything CI or the reviewer finds with new commits on the same branch.

#### How to test

The new tests pass and the pages work at 375 px.

#### What you just did and why

Alerts say *what* happened; the timeline says *what else that device did*, which is how an analyst decides whether an alert is a one-off or part of something bigger.

#### Pull request checklist

- [ ] `ruff check .` prints `All checks passed!`
- [ ] `pytest -m "not integration" -q` passes on your laptop
- [ ] The pull request title has the form `type: summary (TASK-ID)` and the body says `Closes #<issue number>`
- [ ] No secrets, passwords, email addresses, personal data, or captures from a real network (CLAUDE.md rule 6)
- [ ] Any new dependency has a row in `docs/DEPENDENCIES.md` with its license
- [ ] CI is green and your reviewer approved
- [ ] Timeline links check hosts and port, not the uid alone

### AHM-07: Response: block proposals, generated rules, and preview before you block

**Due:** Spring S5-S8 (due Fri Mar 12, 2027) · **Milestone:** `S5-S8 Respond` · **Needs first:** [JAI-06](jaiden.md#jai-06-storage-alerts-in-sqlite-events-in-hourly-parquet-files), [JAI-07](jaiden.md#jai-07-the-api-uploads-alerts-events-live-updates-sensor-ingest) · **Kind:** code, tested

**Issue labels:** `type:task` `phase:spring` `owner:ahmad` `area:response`

#### Goal

Let an analyst propose blocking one IP address and see, before anything happens, the exact firewall commands (with their undo commands) and what the block would have stopped in the last 7 days (`docs/ARCHITECTURE.md` section 13).

#### Prerequisites

JAI-06 and JAI-07 are merged.

#### Steps

**Step 1.** Update `main` and create your branch for this task (one branch per task):

```bash
cd ~/projects/maxguard
source .venv/bin/activate
git checkout main && git pull
git checkout -b ahmad/response-generate
```

If `source .venv/bin/activate` fails, you have not made the virtual environment yet: do Week 0 section 0.11 first.

**Step 2.** Create `maxguard/response/__init__.py` (one line):

```python
"""Response module: block proposals, preview, approval, enforcers (Ahmad, AHM-07/AHM-08)."""
```

and `maxguard/response/generate.py`:

```python
"""Firewall commands for blocking one IP address, with their undo (Ahmad, AHM-07).

CLAUDE.md rule 4: blocking is defensive only, needs a person's approval, and must
be reversible. This module only *writes text*: it never runs a command and never
sends anything toward the address. A person (or an approved Enforcer) uses it.

Safety: the address is parsed with Python's ipaddress module and only the parsed
address is ever put into a command. Anything that is not a plain IP address, such
as "1.2.3.4; rm -rf /", raises ValueError before a command is built.

What "direction" means (the same in the preview, so the numbers match):
- inbound:  connections the address starts toward us (it is the originator),
- outbound: connections we start toward the address,
- both:     either of them.
The rules match the connection's *original* direction (conntrack), so an
inbound-only block still lets our own connections to that address work.

nftables keeps blocked addresses in named sets, so blocking and undoing are one
command each. A set holds one address family, so there is one set per direction
and family: maxguard_block_in_v4, maxguard_block_in_v6, maxguard_block_out_v4,
maxguard_block_out_v6. NFT_SETUP creates them once (safe to run again: it keeps
the addresses already in the sets).
"""

from __future__ import annotations

import ipaddress

DIRECTIONS = ("inbound", "outbound", "both")
NFT_TABLE = "inet maxguard"
LIMITED_BROADCAST = ipaddress.ip_address("255.255.255.255")

# Run once on the Linux firewall with:  sudo nft -f maxguard-setup.nft
# "add" does nothing when the table, set or chain exists already; "flush chain"
# then removes the old rules so running the file twice never doubles them.
NFT_SETUP = """\
add table inet maxguard
add set inet maxguard maxguard_block_in_v4 { type ipv4_addr; }
add set inet maxguard maxguard_block_in_v6 { type ipv6_addr; }
add set inet maxguard maxguard_block_out_v4 { type ipv4_addr; }
add set inet maxguard maxguard_block_out_v6 { type ipv6_addr; }
add chain inet maxguard input { type filter hook input priority filter; policy accept; }
add chain inet maxguard forward { type filter hook forward priority filter; policy accept; }
add chain inet maxguard output { type filter hook output priority filter; policy accept; }
flush chain inet maxguard input
flush chain inet maxguard forward
flush chain inet maxguard output
add rule inet maxguard input ct original ip saddr @maxguard_block_in_v4 drop
add rule inet maxguard input ct original ip6 saddr @maxguard_block_in_v6 drop
add rule inet maxguard forward ct original ip saddr @maxguard_block_in_v4 drop
add rule inet maxguard forward ct original ip6 saddr @maxguard_block_in_v6 drop
add rule inet maxguard forward ct original ip daddr @maxguard_block_out_v4 drop
add rule inet maxguard forward ct original ip6 daddr @maxguard_block_out_v6 drop
add rule inet maxguard output ct original ip daddr @maxguard_block_out_v4 drop
add rule inet maxguard output ct original ip6 daddr @maxguard_block_out_v6 drop
"""

# OPNsense: one firewall alias per direction (an alias holds IPv4 and IPv6).
OPNSENSE_ALIASES = {"inbound": "maxguard_block_in", "outbound": "maxguard_block_out"}


def parse_ip(text: str) -> ipaddress.IPv4Address | ipaddress.IPv6Address:
    """Parse one address the user typed, or raise ValueError saying why not."""
    if not isinstance(text, str):
        # ip_address(16909060) would quietly mean 1.2.3.4
        raise ValueError("the IP address must be text")
    ip = ipaddress.ip_address(text)  # "1.2.3.4; rm -rf /" raises ValueError here
    if getattr(ip, "scope_id", None):
        # "2001:db8::1%$(id)" is a valid address with a scope: refuse the scope.
        raise ValueError(f"{text!r}: an address with a %scope cannot be blocked")
    if getattr(ip, "ipv4_mapped", None):
        raise ValueError(f"{text!r}: write the IPv4 address {ip.ipv4_mapped} instead")
    refuse_special(ip)
    return ip


def refuse_special(ip: ipaddress.IPv4Address | ipaddress.IPv6Address) -> None:
    """Blocking these would cut off this machine or the whole network segment."""
    if ip.is_loopback:
        raise ValueError(f"{ip} is a loopback address (this machine)")
    if ip.is_multicast:
        raise ValueError(f"{ip} is a multicast address")
    if ip.is_unspecified:
        raise ValueError(f"{ip} is the unspecified address")
    if ip.is_link_local:
        raise ValueError(f"{ip} is a link-local address")
    if ip == LIMITED_BROADCAST:
        raise ValueError(f"{ip} is the broadcast address")


def check_direction(direction: str) -> str:
    if direction not in DIRECTIONS:
        raise ValueError(f"direction must be one of {', '.join(DIRECTIONS)}")
    return direction


def sides(direction: str) -> list[str]:
    """'both' -> ['inbound', 'outbound']; the others stay as they are."""
    return ["inbound", "outbound"] if direction == "both" else [direction]


def rules_for(ip: str, direction: str) -> dict:
    """All the ways to block ip (and undo it): nftables, iptables, OPNsense, home router."""
    address = parse_ip(ip)
    check_direction(direction)
    return {
        "ip": str(address),
        "version": address.version,
        "direction": direction,
        "nftables": nftables_rules(address, direction),
        "iptables": iptables_rules(address, direction),
        "opnsense": opnsense_steps(address, direction),
        "home_router": home_router_steps(address, direction),
    }


def nft_set_name(side: str, version: int) -> str:
    short = "in" if side == "inbound" else "out"
    return f"maxguard_block_{short}_v{version}"


def nftables_rules(ip, direction: str) -> dict:
    block, undo = [], []
    for side in sides(direction):
        target = f"{NFT_TABLE} {nft_set_name(side, ip.version)} {{ {ip} }}"
        # One quoted argument, so the shell never interprets the braces.
        block.append(f"sudo nft 'add element {target}'")
        undo.append(f"sudo nft 'delete element {target}'")
    return {"setup": NFT_SETUP, "block": block, "undo": undo}


def iptables_rules(ip, direction: str) -> dict:
    program = "iptables" if ip.version == 4 else "ip6tables"
    matches = []
    for side in sides(direction):
        if side == "inbound":   # connections the address starts
            matches += [("INPUT", f"--ctorigsrc {ip}"), ("FORWARD", f"--ctorigsrc {ip}")]
        else:                   # connections we start toward the address
            matches += [("OUTPUT", f"--ctorigdst {ip}"), ("FORWARD", f"--ctorigdst {ip}")]
    rule = "-m conntrack {match} -m comment --comment maxguard -j DROP"
    block = [f"sudo {program} -I {chain} {rule.format(match=m)}" for chain, m in matches]
    undo = [f"sudo {program} -D {chain} {rule.format(match=m)}" for chain, m in matches]
    return {"block": block, "undo": undo}


def opnsense_steps(ip, direction: str) -> dict:
    block, undo = [], []
    for side in sides(direction):
        alias = OPNSENSE_ALIASES[side]
        block.append(f"Firewall > Aliases: add {ip} to the content of the alias {alias}, "
                     "click Save, then Apply.")
        undo.append(f"Firewall > Aliases: remove {ip} from the alias {alias}, "
                    "click Save, then Apply.")
    setup = [
        "Once: Firewall > Aliases: create the aliases maxguard_block_in and "
        "maxguard_block_out, type Host(s), empty.",
        "Once: Firewall > Rules > WAN: a Block rule with source maxguard_block_in "
        "(stops connections an address on the internet starts).",
        "Once: Firewall > Rules > LAN: a Block rule with source maxguard_block_in "
        "(stops connections a device on your network starts through the firewall), and "
        "a Block rule with destination maxguard_block_out (stops connections your devices "
        "start toward that address).",
        # Rules are "quick" by default: the first rule that matches wins. A Block rule
        # below the LAN page's default allow rule would never match anything.
        "Once: on both pages, move these Block rules above every Pass rule "
        "(OPNsense uses the first rule that matches), then click Apply.",
    ]
    return {"setup": setup, "block": block, "undo": undo}


def home_router_steps(ip, direction: str) -> dict:
    wording = {
        "inbound": f"incoming connections from {ip}",
        "outbound": f"connections from your devices to {ip}",
        "both": f"all connections to and from {ip}",
    }[direction]
    block = [
        "Open your router's admin page (often printed on a sticker on the router).",
        "Find the firewall, 'access control', or 'IP filter' settings "
        "(the name differs between brands).",
        f"Add a rule that blocks {wording}, and save it.",
        "Write down where you added it, so you can find it again to undo it.",
    ]
    undo = [f"Open the same settings page, delete the rule for {ip}, and save."]
    return {"block": block, "undo": undo}
```

Four things to notice. `parse_ip()` is the only way an address gets into a command, and `ipaddress.ip_address()` alone is not enough: it accepts `2001:db8::1%$(id)` (an IPv6 *scope*, which can hold shell syntax) and plain integers (`16909060` means `1.2.3.4`), so those are refused too. An nftables set holds one address family, and a block has a direction, so there are four sets, created once by `NFT_SETUP`. *Direction* means who starts the connection: `inbound` blocks connections the address starts, `outbound` blocks connections your devices start toward it; the rules match conntrack's *original* direction, so an inbound block still lets your own connections to that address work. And each `nft` command is one quoted argument, so the shell never reads the braces.

**Step 3.** Check the generated commands for real. `nicolaka/netshoot:v0.15` has `nft` and `iptables`; `--network none` gives the container only its own loopback, so nothing can leave it. The setup file is loaded twice to show that running it again never doubles the rules:

```bash
mkdir -p data/nft-check
python - <<'EOF'
from pathlib import Path
from maxguard.response.generate import NFT_SETUP, rules_for
Path("data/nft-check/maxguard-setup.nft").write_text(NFT_SETUP)
r = rules_for("203.0.113.7", "both")
commands = (r["nftables"]["block"] + r["iptables"]["block"]
            + ["nft list set inet maxguard maxguard_block_in_v4 | grep elements",
               "iptables -S | grep maxguard"]
            + r["nftables"]["undo"] + r["iptables"]["undo"]
            + ['echo "rules left: $(iptables -S | grep -c maxguard)"'])
# The container runs as root, so sudo is not needed there.
Path("data/nft-check/run.sh").write_text("\n".join(commands).replace("sudo ", "") + "\n")
EOF
docker run --rm --network none --cap-add NET_ADMIN --cap-add NET_RAW \
  -v "$PWD/data/nft-check:/w:ro" nicolaka/netshoot:v0.15 sh -c '
  nft -c -f /w/maxguard-setup.nft && echo "syntax check: ok"
  nft -f /w/maxguard-setup.nft && nft -f /w/maxguard-setup.nft
  echo "drop rules in input after loading twice: $(nft list chain inet maxguard input | grep -c drop)"
  bash -e /w/run.sh'
```

Expected output:

```text
syntax check: ok
drop rules in input after loading twice: 2
		elements = { 203.0.113.7 }
-A INPUT -m conntrack --ctorigsrc 203.0.113.7 -m comment --comment maxguard -j DROP
-A FORWARD -m conntrack --ctorigdst 203.0.113.7 -m comment --comment maxguard -j DROP
-A FORWARD -m conntrack --ctorigsrc 203.0.113.7 -m comment --comment maxguard -j DROP
-A OUTPUT -m conntrack --ctorigdst 203.0.113.7 -m comment --comment maxguard -j DROP
rules left: 0
```

*`nicolaka/netshoot` is for testing only, never shipped (`docs/DEPENDENCIES.md`). Not checked here: the older iptables-legacy backend, and a real router forwarding traffic (the `forward` chain loads, but no routed packets went through it).*

**Step 4.** Create `maxguard/response/preview.py`:

```python
"""Preview before you block: what would this block have stopped? (Ahmad, AHM-07)

Before a person approves a block they see the connections of the last 7 days
that the block would have stopped: how many, which of our devices, which
services and ports, first and last seen, and up to 10 sample events.

window_end is passed in by the caller, never read from the clock here, so the
same events and the same window_end always give the same preview (and the tests
do not depend on today's date). Every list is sorted, so the order is fixed.

"inbound" means the address started the connection (it is the event's src_ip);
"outbound" means one of our devices started it (the address is the dst_ip).
This matches the generated firewall rules in generate.py.
"""

from __future__ import annotations

from maxguard.response.generate import check_direction, parse_ip, sides

WINDOW_SECONDS = 7 * 24 * 3600
MAX_SAMPLES = 10
MAX_EVENTS = 100_000  # a preview reads at most this many events (see "truncated")


def preview(ip: str, direction: str, event_store, *, window_end: float) -> dict:
    """Summarize the events in [window_end - 7 days, window_end) that the block matches."""
    address = str(parse_ip(ip))  # the same spelling as Zeek, e.g. "2001:db8::7"
    check_direction(direction)
    window_start = window_end - WINDOW_SECONDS
    events = event_store.query(ip=address, since=window_start, until=window_end,
                               limit=MAX_EVENTS)
    matched = [e for e in events if matches(e, address, direction)]
    matched.sort(key=lambda e: (e["ts"], e["event_id"]))
    return {
        "ip": address,
        "direction": direction,
        "window_start": window_start,
        "window_end": window_end,
        "connections": len({connection_key(e) for e in matched}),
        "events": len(matched),
        "devices": sorted({other_side(e, address) for e in matched}),
        "services": services(matched),
        "first_seen": matched[0]["ts"] if matched else None,
        "last_seen": matched[-1]["ts"] if matched else None,
        "samples": matched[:MAX_SAMPLES],
        "truncated": len(events) == MAX_EVENTS,  # there may be more than we read
    }


def matches(event: dict, address: str, direction: str) -> bool:
    """Would a block in this direction have stopped the connection of this event?"""
    wanted = sides(direction)
    if "inbound" in wanted and event["src_ip"] == address:
        return True
    return "outbound" in wanted and event["dst_ip"] == address


def connection_key(event: dict) -> str:
    """Zeek and Suricata events of one connection share a community_id (or a Zeek uid).

    Counting keys instead of events stops one connection counting three times
    (conn.log + ssl.log + eve.json)."""
    return event["community_id"] or event["uid"] or event["event_id"]


def other_side(event: dict, address: str) -> str:
    """The device at the other end of the connection: the one the block protects."""
    return event["dst_ip"] if event["src_ip"] == address else event["src_ip"]


def services(events: list[dict]) -> list[dict]:
    """Distinct (proto, dst_port, service) with how many events used each."""
    counts: dict[tuple, int] = {}
    for event in events:
        key = (event["proto"], event["dst_port"], event["service"])
        counts[key] = counts.get(key, 0) + 1
    rows = [{"proto": proto, "port": port, "service": service, "events": n}
            for (proto, port, service), n in counts.items()]
    return sorted(rows, key=service_order)


def service_order(row: dict) -> tuple:
    # A port can be None (e.g. DHCP) and None cannot be compared with a number,
    # so those rows sort first by using -1 in their place.
    port = -1 if row["port"] is None else row["port"]
    return (row["proto"], port, row["service"])
```

`window_end` comes from the caller, never from the clock, so the same events always give the same preview. One connection seen in `conn.log`, `ssl.log` and `eve.json` counts once (by `community_id`).

**Step 5.** Create the tests `tests/unit/test_response_generate.py`:

```python
"""Tests for maxguard.response.generate (Ahmad, AHM-07)."""

import pytest

from maxguard.response.generate import NFT_SETUP, parse_ip, rules_for

HOSTILE = [
    "1.2.3.4; rm -rf /",
    "1.2.3.4 && reboot",
    "$(reboot)",
    " 203.0.113.7",          # leading space
    "203.0.113.7\n",         # trailing newline
    "203.0.113.0/24",        # a network, not one address
    "203.0.113",
    "",
    "2001:db8::1%$(id)",     # ipaddress accepts this scope: it must still be refused
    "2001:db8::1%eth0",
]

REFUSED = [
    "127.0.0.1", "127.0.0.2", "::1",            # loopback
    "224.0.0.1", "ff02::1",                     # multicast
    "0.0.0.0", "::",                            # unspecified
    "169.254.10.1", "fe80::1", "fe80::1%eth0",  # link-local
    "255.255.255.255",                          # broadcast
    "::ffff:203.0.113.7",                       # IPv4 written as IPv6
]


def all_text(rules: dict) -> str:
    """Every command and step in one string, to search for leaked input."""
    parts = []
    for method in ("nftables", "iptables", "opnsense", "home_router"):
        for key in ("block", "undo"):
            parts.extend(rules[method][key])
    return "\n".join(parts)


@pytest.mark.parametrize("text", HOSTILE)
def test_hostile_input_never_reaches_a_command(text):
    with pytest.raises(ValueError):
        rules_for(text, "both")


@pytest.mark.parametrize("text", REFUSED)
def test_special_addresses_are_refused(text):
    with pytest.raises(ValueError):
        rules_for(text, "inbound")


def test_a_number_is_not_an_address():
    with pytest.raises(ValueError):
        parse_ip(16909060)  # ipaddress alone would read this as 1.2.3.4


def test_unknown_direction_is_refused():
    with pytest.raises(ValueError, match="direction"):
        rules_for("203.0.113.7", "sideways")


def test_inbound_ipv4_rules_and_undo():
    rules = rules_for("203.0.113.7", "inbound")
    assert rules["ip"] == "203.0.113.7" and rules["version"] == 4
    assert rules["nftables"]["block"] == [
        "sudo nft 'add element inet maxguard maxguard_block_in_v4 { 203.0.113.7 }'"]
    assert rules["nftables"]["undo"] == [
        "sudo nft 'delete element inet maxguard maxguard_block_in_v4 { 203.0.113.7 }'"]
    assert rules["iptables"]["block"] == [
        "sudo iptables -I INPUT -m conntrack --ctorigsrc 203.0.113.7 "
        "-m comment --comment maxguard -j DROP",
        "sudo iptables -I FORWARD -m conntrack --ctorigsrc 203.0.113.7 "
        "-m comment --comment maxguard -j DROP",
    ]


def test_every_block_command_has_an_undo():
    rules = rules_for("198.51.100.20", "both")
    for method in ("nftables", "opnsense"):
        assert len(rules[method]["block"]) == len(rules[method]["undo"]) == 2  # in + out
    assert len(rules["iptables"]["block"]) == len(rules["iptables"]["undo"]) == 4
    assert all(" -D " in c for c in rules["iptables"]["undo"])  # -D deletes, -I inserts
    undo = [c.replace(" -D ", " -I ") for c in rules["iptables"]["undo"]]
    assert undo == rules["iptables"]["block"]  # the same rule, deleted instead of inserted
    assert all("'delete element " in c for c in rules["nftables"]["undo"])


def test_ipv6_uses_the_v6_sets_and_ip6tables():
    rules = rules_for("2001:DB8:0:0:0:0:0:7", "outbound")
    assert rules["ip"] == "2001:db8::7"  # one spelling, the same as Zeek writes
    assert "maxguard_block_out_v6 { 2001:db8::7 }" in rules["nftables"]["block"][0]
    assert all(c.startswith("sudo ip6tables -I ") for c in rules["iptables"]["block"])
    assert all("--ctorigdst 2001:db8::7" in c for c in rules["iptables"]["block"])


def test_private_addresses_can_be_blocked():
    # A compromised device on the user's own network is a valid thing to block.
    assert rules_for("192.168.1.50", "both")["ip"] == "192.168.1.50"


def test_only_the_parsed_address_appears():
    rules = rules_for("203.0.113.7", "both")
    text = all_text(rules)
    assert ";" not in text.replace("Save, then", "")  # no shell separators
    assert "$(" not in text and "`" not in text


def test_setup_declares_every_set_the_commands_use():
    for ip in ("203.0.113.7", "2001:db8::7"):
        for command in rules_for(ip, "both")["nftables"]["block"]:
            set_name = command.split()[6]  # sudo nft 'add element inet maxguard <set> ...
            assert f"add set inet maxguard {set_name} " in NFT_SETUP


def test_same_input_same_output():
    assert rules_for("203.0.113.7", "both") == rules_for("203.0.113.7", "both")


def test_opnsense_setup_puts_the_block_rules_first():
    # OPNsense rules are "quick": the first match wins, so a Block rule below the
    # default allow rule would never match.
    setup = rules_for("203.0.113.7", "both")["opnsense"]["setup"]
    assert any("above every Pass rule" in step for step in setup)
```

and `tests/unit/test_response_preview.py`:

```python
"""Tests for maxguard.response.preview (Ahmad, AHM-07). Synthetic events only."""

import pytest

from maxguard.events.normalize import EVENT_KEYS
from maxguard.response.preview import WINDOW_SECONDS, preview
from maxguard.storage.events import EventStore

WINDOW_END = 1791331200.0   # 2026-10-07 00:00:00 UTC
BAD = "203.0.113.7"          # the address we want to block
LAPTOP = "192.168.1.20"
PRINTER = "192.168.1.30"


def event(n: int, ts: float, src: str, dst: str, port: int, service: str = "",
          community_id: str = "") -> dict:
    row = dict.fromkeys(EVENT_KEYS, "")
    row.update(event_id=f"ev{n:04d}", ts=ts, sensor_id="pcap", source="zeek", log="conn.log",
               kind="conn", community_id=community_id or f"1:c{n}=", src_ip=src, dst_ip=dst,
               src_port=40000 + n, dst_port=port, proto="tcp", service=service,
               bytes_out=10, bytes_in=20)
    return row


@pytest.fixture
def store(tmp_path):
    events = [
        # inbound: the bad address starts connections to our devices
        event(1, WINDOW_END - 3600, BAD, LAPTOP, 22, "ssh"),
        event(2, WINDOW_END - 1800, BAD, PRINTER, 23),
        # outbound: our laptop starts a connection to it (two events of one connection)
        event(3, WINDOW_END - 7200, LAPTOP, BAD, 443, "ssl", community_id="1:same="),
        event(4, WINDOW_END - 7199, LAPTOP, BAD, 443, "ssl", community_id="1:same="),
        # outside the 7-day window, and exactly at window_end (the end is not included)
        event(5, WINDOW_END - WINDOW_SECONDS - 1, BAD, LAPTOP, 22, "ssh"),
        event(6, WINDOW_END, BAD, LAPTOP, 22, "ssh"),
        # another address: never part of the preview
        event(7, WINDOW_END - 60, "198.51.100.9", LAPTOP, 80, "http"),
    ]
    events += [event(100 + i, WINDOW_END - 100 + i, BAD, LAPTOP, 22, "ssh") for i in range(12)]
    target = EventStore(tmp_path / "events")
    target.write(events)
    return target


def test_inbound_counts_only_connections_the_address_starts(store):
    result = preview(BAD, "inbound", store, window_end=WINDOW_END)
    assert result["connections"] == 14            # events 1, 2 and the 12 extra ones
    assert result["devices"] == [LAPTOP, PRINTER]
    assert result["first_seen"] == WINDOW_END - 3600
    assert result["last_seen"] == WINDOW_END - 100 + 11
    assert [s["port"] for s in result["services"]] == [22, 23]


def test_outbound_counts_one_connection_once(store):
    result = preview(BAD, "outbound", store, window_end=WINDOW_END)
    assert result["events"] == 2
    assert result["connections"] == 1             # the two events share a community_id
    assert result["devices"] == [LAPTOP]
    assert result["services"] == [{"proto": "tcp", "port": 443, "service": "ssl", "events": 2}]


def test_samples_are_ten_in_time_order(store):
    result = preview(BAD, "both", store, window_end=WINDOW_END)
    assert result["connections"] == 15
    samples = result["samples"]
    assert len(samples) == 10
    assert [s["ts"] for s in samples] == sorted(s["ts"] for s in samples)
    assert samples[0]["event_id"] == "ev0003"     # the oldest event in the window


def test_window_end_comes_from_the_caller(store):
    result = preview(BAD, "both", store, window_end=WINDOW_END - 5000)
    assert result["window_start"] == WINDOW_END - 5000 - WINDOW_SECONDS
    # The window moved back: events 3, 4 (outbound) and 5 are inside it now.
    assert [s["event_id"] for s in result["samples"]] == ["ev0005", "ev0003", "ev0004"]


def test_same_input_same_preview(store):
    first = preview(BAD, "both", store, window_end=WINDOW_END)
    assert preview(BAD, "both", store, window_end=WINDOW_END) == first


def test_no_events_gives_an_empty_preview(tmp_path):
    result = preview(BAD, "both", EventStore(tmp_path / "empty"), window_end=WINDOW_END)
    assert result["connections"] == 0 and result["samples"] == []
    assert result["first_seen"] is None and result["last_seen"] is None


def test_hostile_input_is_refused_before_any_query(store):
    with pytest.raises(ValueError):
        preview("1.2.3.4; rm -rf /", "both", store, window_end=WINDOW_END)
    with pytest.raises(ValueError):
        preview("127.0.0.1", "both", store, window_end=WINDOW_END)
```

Run them:

```bash
pytest tests/unit/test_response_generate.py tests/unit/test_response_preview.py -q
```

Expected output:

```text
.......................................                                                      [100%]
39 passed in 0.73s
```

**Step 6.** Commit, push, and open the pull request:

```bash
git add -A
git status          # only this task's files: nothing from .venv/, data/ or lab/captures/
git commit -m "feat: block proposals with generated rules and preview (AHM-07)"
git push -u origin HEAD
```

`HEAD` means "the branch I am on", so you do not have to retype its name. Open the repository on github.com: a yellow bar shows your branch with a **Compare & pull request** button. Click it, keep the title `feat: block proposals with generated rules and preview (AHM-07)`, fill in the template (paste the real output of the commands above under **How I tested it**), write `Closes #<issue number>` (this task's issue), and pick **@JWinborne1** under **Reviewers**. Click **Create pull request**, then fix anything CI or the reviewer finds with new commits on the same branch.

#### How to test

The tests pass, and the nftables commands pass `nft -c`.

#### What you just did and why

Blocking the wrong address can cut off a printer, a phone, or the whole office. Showing exactly what would have been blocked last week, and the undo command before the block, is how MaxGuard keeps blocking safe and reversible (CLAUDE.md rule 4).

#### Pull request checklist

- [ ] `ruff check .` prints `All checks passed!`
- [ ] `pytest -m "not integration" -q` passes on your laptop
- [ ] The pull request title has the form `type: summary (TASK-ID)` and the body says `Closes #<issue number>`
- [ ] No secrets, passwords, email addresses, personal data, or captures from a real network (CLAUDE.md rule 6)
- [ ] Any new dependency has a row in `docs/DEPENDENCIES.md` with its license
- [ ] CI is green and your reviewer approved
- [ ] A hostile input test exists

### AHM-08: Response: approvals, audit, revert, and the OPNsense connector

**Due:** Spring S5-S8 (due Fri Mar 12, 2027) · **Milestone:** `S5-S8 Respond` · **Needs first:** [AHM-07](#ahm-07-response-block-proposals-generated-rules-and-preview-before-you-block), [JON-03](jonattan.md#jon-03-offline-guard-make-accidental-network-access-fail-loudly) · **Kind:** code, tested

**Issue labels:** `type:task` `phase:spring` `owner:ahmad` `area:response` `needs-hardware`

> **Needs hardware.** Steps that use the Raspberry Pi, the switch or other devices were not run during planning; they are marked *not run — verify on hardware*.

#### Goal

Add the approval workflow (propose → preview → approve with the IP typed again → applied → reverted, every step audited) and the first `Enforcer`, which applies an approved block on an OPNsense firewall through its API.

#### Prerequisites

AHM-07 is merged. For the last step you need an OPNsense test firewall in a VM, never a real one.

#### Steps

**Step 1.** Update `main` and create your branch for this task (one branch per task):

```bash
cd ~/projects/maxguard
source .venv/bin/activate
git checkout main && git pull
git checkout -b ahmad/response-approvals
```

If `source .venv/bin/activate` fails, you have not made the virtual environment yet: do Week 0 section 0.11 first.

**Step 2.** Create `maxguard/response/approvals.py`:

```python
"""Block proposals and their approval workflow (Ahmad, AHM-08).

CLAUDE.md rule 4: a block always needs explicit human approval, is reversible,
and is logged. The steps (docs/ARCHITECTURE.md section 13):

    proposed -> previewed -> approved -> applied -> reverted
    proposed or previewed -> rejected

- Approve only after a preview: the person must have seen what the block stops.
- Approve needs the person's name and the IP address typed again (confirm_ip),
  so a block is never approved by a stray click.
- Every step, and every refused approval, writes a row to the audit table
  (action "response.<step>", target = the proposal id). A state change and its
  audit row are written in ONE transaction (storage.state.insert_audit), so a
  crash can never leave a change without its audit row.
- One open proposal per address: a second proposal for an address that is still
  proposed, previewed, approved or applied is refused. Otherwise reverting one of
  them would quietly remove the block the other one still shows as applied.
- If an enforcer fails half way, the address is taken off the firewall again, so
  the firewall never keeps a block that MaxGuard does not show as applied.
- Times are passed in by the caller (the API reads the clock, this module never does).

Proposals live in their own table in state.db, created here with
CREATE TABLE IF NOT EXISTS, so storage/state.py does not change.
"""

from __future__ import annotations

import ipaddress
import json
import sqlite3
import threading
from collections.abc import Iterator, Sequence
from contextlib import contextmanager

from maxguard.response.enforcers.base import Enforcer
from maxguard.response.generate import check_direction, parse_ip, rules_for
from maxguard.storage.state import StateStore, insert_audit

STATES = ("proposed", "previewed", "approved", "applied", "reverted", "rejected")
OPEN_STATES = ("proposed", "previewed", "approved", "applied")  # not finished yet

# One firewall change at a time. Without it, a double click on "apply" sends the
# address to the firewall twice before either request can change the state, and
# OPNsense can then keep a second copy that a later revert leaves behind.
FIREWALL_LOCK = threading.Lock()

SCHEMA = """
CREATE TABLE IF NOT EXISTS response_proposals (
    proposal_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    ip           TEXT NOT NULL,
    direction    TEXT NOT NULL,
    reason       TEXT NOT NULL,
    finding_id   TEXT,
    state        TEXT NOT NULL,
    created_by   TEXT NOT NULL,
    created_at   REAL NOT NULL,
    updated_at   REAL NOT NULL,
    approved_by  TEXT,
    method       TEXT,      -- how it was applied: "manual" or "enforcer"
    preview_json TEXT       -- the last preview the person saw
);
"""


class WrongState(Exception):
    """This step is not allowed from the proposal's current state (the API answers 409)."""


class ProposalStore:
    def __init__(self, state_store: StateStore):
        self.state_store = state_store
        with self._connect() as conn:
            conn.executescript(SCHEMA)

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        # A new connection per call, like StateStore: the API uses several threads.
        conn = sqlite3.connect(self.state_store.path, timeout=5.0)
        conn.row_factory = sqlite3.Row
        try:
            with conn:  # commit on success, roll back on an exception
                yield conn
        finally:
            conn.close()

    # ---------- reading ----------

    def get(self, proposal_id: int) -> dict:
        """One proposal with its generated commands. KeyError if it does not exist."""
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM response_proposals WHERE proposal_id = ?",
                               (proposal_id,)).fetchone()
        if row is None:
            raise KeyError(proposal_id)
        return row_to_proposal(row)

    def list_proposals(self, limit: int = 200) -> list[dict]:
        """Newest first."""
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM response_proposals "
                                "ORDER BY proposal_id DESC LIMIT ?", (limit,)).fetchall()
        return [row_to_proposal(row) for row in rows]

    # ---------- the steps ----------

    def propose(self, *, ip: str, direction: str, actor: str, at: float, reason: str = "",
                finding_id: str | None = None) -> dict:
        address = str(parse_ip(ip))  # ValueError for anything that is not a plain address
        check_direction(direction)
        open_states = ", ".join("?" for _ in OPEN_STATES)
        with self._connect() as conn:  # the proposal and its audit row: one transaction
            # INSERT ... WHERE NOT EXISTS checks and inserts in one statement, so two
            # people proposing the same address at the same moment cannot both succeed.
            cur = conn.execute(
                "INSERT INTO response_proposals (ip, direction, reason, finding_id, state, "
                "created_by, created_at, updated_at) "
                "SELECT ?, ?, ?, ?, 'proposed', ?, ?, ? WHERE NOT EXISTS ("
                "SELECT 1 FROM response_proposals "
                f"WHERE ip = ? AND state IN ({open_states}))",
                (address, direction, reason, finding_id, actor, at, at, address, *OPEN_STATES))
            if cur.rowcount == 1:
                proposal_id = cur.lastrowid
                audit(conn, actor, "proposed", proposal_id, at,
                      {"ip": address, "direction": direction, "finding_id": finding_id})
        if cur.rowcount == 0:
            raise WrongState(f"{address} already has an open proposal: "
                             "revert or reject it before proposing it again")
        return self.get(proposal_id)

    def record_preview(self, proposal_id: int, *, actor: str, preview: dict,
                       at: float) -> dict:
        """Keep the preview the person saw. A previewed proposal may be previewed again."""
        self.move(proposal_id, ("proposed", "previewed"), "previewed", at, actor,
                  {"connections": preview["connections"], "devices": len(preview["devices"]),
                   "window_end": preview["window_end"]},
                  preview_json=json.dumps(preview, sort_keys=True))
        return self.get(proposal_id)

    def approve(self, proposal_id: int, *, actor: str, confirm_ip: str, at: float) -> dict:
        """The person types the address again; a missing or different address is refused."""
        proposal = self.get(proposal_id)
        if not actor.strip():
            raise ValueError("enter your name to approve a block")
        if not same_address(confirm_ip, proposal["ip"]):
            self.audit_only(actor, "approve_refused", proposal_id, at,
                            {"reason": "typed IP does not match"})
            raise ValueError("the IP address you typed does not match the proposal")
        self.move(proposal_id, ("previewed",), "approved", at, actor, {"ip": proposal["ip"]},
                  approved_by=actor)
        return self.get(proposal_id)

    def mark_applied(self, proposal_id: int, *, actor: str, at: float,
                     enforcers: Sequence[Enforcer] = ()) -> dict:
        """Apply an approved block: by the enforcers if given, else the person ran the
        commands by hand and says so. If an enforcer fails, the state stays 'approved'
        and the address is taken off every enforcer again (nothing stays half-blocked)."""
        with FIREWALL_LOCK:
            proposal = self.require_state(proposal_id, "approved")
            method = "enforcer" if enforcers else "manual"
            try:
                for enforcer in enforcers:
                    enforcer.add(proposal["ip"])
                    enforcer.apply()
            except Exception as err:
                undone = remove_everywhere(enforcers, proposal["ip"])
                self.audit_only(actor, "apply_failed", proposal_id, at,
                                {"error": str(err), "undone": undone})
                raise
            self.move(proposal_id, ("approved",), "applied", at, actor,
                      {"ip": proposal["ip"], "method": method}, method=method)
        return self.get(proposal_id)

    def revert(self, proposal_id: int, *, actor: str, at: float,
               enforcers: Sequence[Enforcer] = ()) -> dict:
        """Undo the block the same way it was applied."""
        with FIREWALL_LOCK:
            proposal = self.require_state(proposal_id, "applied")
            if proposal["method"] == "enforcer":
                if not enforcers:
                    raise ValueError("this block was applied by the firewall connector, "
                                     "which is not configured now")
                try:
                    for enforcer in enforcers:
                        enforcer.remove(proposal["ip"])
                        enforcer.apply()
                except Exception as err:
                    self.audit_only(actor, "revert_failed", proposal_id, at,
                                    {"error": str(err)})
                    raise
            self.move(proposal_id, ("applied",), "reverted", at, actor,
                      {"ip": proposal["ip"], "method": proposal["method"]})
        return self.get(proposal_id)

    def reject(self, proposal_id: int, *, actor: str, at: float, reason: str = "") -> dict:
        self.move(proposal_id, ("proposed", "previewed"), "rejected", at, actor,
                  {"reason": reason})
        return self.get(proposal_id)

    # ---------- helpers ----------

    def require_state(self, proposal_id: int, state: str) -> dict:
        proposal = self.get(proposal_id)
        if proposal["state"] != state:
            raise WrongState(f"proposal {proposal_id} is {proposal['state']}, not {state}")
        return proposal

    def move(self, proposal_id: int, allowed: tuple[str, ...], new_state: str, at: float,
             actor: str, details: dict, **columns: str) -> None:
        """Change the state only if it is still one of `allowed`, and audit it.

        The check and the change are one UPDATE, so two people clicking at the same
        moment cannot both approve (or both revert) the same proposal. The audit row
        (action "response.<new_state>") is written in the same transaction."""
        self.get(proposal_id)  # KeyError first, so a missing proposal is a 404, not a 409
        sets = "".join(f", {name} = ?" for name in columns)  # names come from our code only
        placeholders = ", ".join("?" for _ in allowed)
        with self._connect() as conn:
            cur = conn.execute(
                f"UPDATE response_proposals SET state = ?, updated_at = ?{sets} "
                f"WHERE proposal_id = ? AND state IN ({placeholders})",
                (new_state, at, *columns.values(), proposal_id, *allowed))
            if cur.rowcount == 1:
                audit(conn, actor, new_state, proposal_id, at, details)
        if cur.rowcount == 0:
            state = self.get(proposal_id)["state"]
            raise WrongState(f"proposal {proposal_id} is {state}; cannot become {new_state}")

    def audit_only(self, actor: str, step: str, proposal_id: int, at: float,
                   details: dict) -> None:
        """Audit a refused or failed step, which changes nothing else."""
        with self._connect() as conn:
            audit(conn, actor, step, proposal_id, at, details)


def audit(conn: sqlite3.Connection, actor: str, step: str, proposal_id: int, at: float,
          details: dict) -> None:
    """One audit row (action "response.<step>"), inside the caller's transaction."""
    insert_audit(conn, actor=actor, action=f"response.{step}", target=str(proposal_id),
                 details=details, at=at)


def remove_everywhere(enforcers: Sequence[Enforcer], ip: str) -> bool:
    """After a failed apply, take ip off every enforcer again, so a retry starts clean.

    Removing an address that is not there is harmless (OPNsense answers "done").
    Returns False when this failed too (for example, the firewall is unreachable):
    the audit row then tells the person to check the firewall by hand."""
    try:
        for enforcer in enforcers:
            enforcer.remove(ip)
            enforcer.apply()
    except Exception:
        return False
    return True


def same_address(typed: str | None, expected: str) -> bool:
    """'2001:DB8::7' and '2001:db8::7' are the same address; '' or 'abc' never match."""
    try:
        return str(ipaddress.ip_address((typed or "").strip())) == expected
    except ValueError:
        return False


def row_to_proposal(row: sqlite3.Row) -> dict:
    proposal = {key: row[key] for key in row.keys() if key != "preview_json"}
    proposal["preview"] = json.loads(row["preview_json"]) if row["preview_json"] else None
    proposal["rules"] = rules_for(row["ip"], row["direction"])  # commands + undo, always shown
    return proposal
```

The steps are `proposed → previewed → approved → applied → reverted`, and a proposed or previewed block can be `rejected`. Approve is allowed only after a preview, needs the person's name and the IP address typed again, and a refused approval is audited too. Each check and state change is **one** SQL `UPDATE ... WHERE state IN (...)`, so two people clicking at the same moment cannot both approve. The proposals table is created here with `CREATE TABLE IF NOT EXISTS`, so `storage/state.py` does not change. Each state change and its audit row are written in **one** transaction (`insert_audit(conn, ...)` from `storage/state.py`), so a crash can never leave a block without its record; the last test proves it by making the audit write fail.

Three more guards came out of the security review. Only **one** open proposal per address: `propose()` checks and inserts in a single `INSERT ... SELECT ... WHERE NOT EXISTS`, because reverting one of two blocks on the same address would take it off the firewall while the other still said *applied*. Only **one** firewall change at a time (`FIREWALL_LOCK`), so a double click on Apply reaches the firewall once. And if a block with direction `both` fails half-way, `remove_everywhere()` takes the address off every list again, so the firewall never stays half-blocked while MaxGuard says *approved*.

**Step 3.** Create the enforcer interface `maxguard/response/enforcers/__init__.py` and `maxguard/response/enforcers/base.py`:

```python
"""Enforcers: connectors that apply an approved block on a firewall (Ahmad, AHM-08)."""
```

```python
"""The Enforcer protocol (Ahmad, AHM-08).

An Enforcer applies an *approved* block on a firewall the user owns, and undoes
it. It only ever talks to that firewall: nothing is sent toward the blocked
address (CLAUDE.md rule 4). maxguard.response.approvals decides when an enforcer
may run; an enforcer never decides anything by itself.

Any class with these three methods is an Enforcer (typing.Protocol checks the
shape, no base class needed), so a test can pass a small fake one.
"""

from __future__ import annotations

from typing import Protocol


class EnforcerError(RuntimeError):
    """The firewall refused or could not be reached; the block state did not change."""


class Enforcer(Protocol):
    def add(self, ip: str) -> None:
        """Put ip on the firewall's block list."""

    def remove(self, ip: str) -> None:
        """Take ip off the firewall's block list."""

    def apply(self) -> None:
        """Make the firewall use the changed list (some firewalls need this step)."""
```

and the OPNsense client `maxguard/response/enforcers/opnsense.py`:

```python
"""OPNsense enforcer: put an approved address in a firewall alias (Ahmad, AHM-08).

Optional. Without it, MaxGuard shows the commands and a person applies them by
hand. With it, MaxGuard asks the user's own OPNsense firewall, through its API,
to add the address to an alias that the user's block rules already use.

The endpoints, read from the OPNsense source (opnsense/core, commit
1177021c22d6dedb63ff9bffd6300e789a8822e2, 2026-10-06):
- POST /api/firewall/alias_util/add/<alias>     body {"address": "<ip>"} -> {"status": "done"}
- POST /api/firewall/alias_util/delete/<alias>  body {"address": "<ip>"} -> {"status": "done"}
  src/opnsense/mvc/app/controllers/OPNsense/Firewall/Api/AliasUtilController.php
  (addAction, deleteAction). Both update the alias in the configuration AND the
  live pf table at once ("pfctl -t <alias> -T add <ip>",
  src/opnsense/service/conf/actions.d/actions_filter.conf, [add.table]).
- POST /api/firewall/alias/reconfigure                                 -> {"status": "ok"}
  src/opnsense/mvc/app/controllers/OPNsense/Firewall/Api/AliasController.php
  (reconfigureAction): the "Apply" button for aliases.
- A JSON body is read like a form (ApiControllerBase.php, parseJsonBodyData).
- API key: a file with the lines "key=..." and "secret=...", sent with HTTP basic
  auth (opnsense/docs repository, source/development/how-tos/api.rst).
- Least privilege for the API user (src/opnsense/mvc/app/models/OPNsense/Core/ACL/ACL.xml):
  "Diagnostics: PF Table IP addresses" (api/firewall/alias_util/*) and
  "Firewall: Alias: Edit" (api/firewall/alias/*).

Safety:
- https only, TLS verification always on. A firewall with its own certificate
  authority: give its CA file (MAXGUARD_OPNSENSE_CA).
- The API key lives in the data folder (data/opnsense/apikey.txt), never in the
  repository. Proxy settings from the environment are ignored: the request goes
  straight to the firewall on the user's own network.
- With the offline guard on (MAXGUARD_OFFLINE=1), add the firewall's host name or
  IP to MAXGUARD_OFFLINE_ALLOW, or every request fails with OfflineViolation.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from urllib.parse import urlparse

import requests

from maxguard.offline import OfflineViolation
from maxguard.response.enforcers.base import EnforcerError
from maxguard.response.generate import parse_ip

TIMEOUT = (5.0, 20.0)  # seconds to connect, seconds to wait for an answer
ALIAS_NAME = re.compile(r"[A-Za-z0-9_]{1,32}")  # OPNsense alias names: letters, digits, _
KEY_FILE = Path("opnsense") / "apikey.txt"      # inside the data folder


class OPNsenseEnforcer:
    """Adds and removes addresses in one OPNsense alias."""

    def __init__(self, base_url: str, key: str, secret: str, *, alias: str,
                 ca_file: str | None = None):
        if urlparse(base_url).scheme != "https":
            raise ValueError("the OPNsense URL must start with https://")
        if not ALIAS_NAME.fullmatch(alias):
            raise ValueError(f"not an OPNsense alias name: {alias!r}")
        self.base_url = base_url.rstrip("/")
        self.alias = alias
        self.session = requests.Session()
        self.session.auth = (key, secret)
        self.session.verify = ca_file or True   # never False
        self.session.trust_env = False          # no proxy, no ~/.netrc: straight to the firewall

    def add(self, ip: str) -> None:
        address = str(parse_ip(ip))  # checked again here: only a clean address is sent
        self.post(f"/api/firewall/alias_util/add/{self.alias}", {"address": address}, "done")

    def remove(self, ip: str) -> None:
        address = str(parse_ip(ip))
        self.post(f"/api/firewall/alias_util/delete/{self.alias}", {"address": address},
                  "done")

    def apply(self) -> None:
        self.post("/api/firewall/alias/reconfigure", {}, "ok")

    def post(self, path: str, body: dict, expected: str) -> None:
        """POST JSON and check OPNsense's {"status": ...} answer."""
        try:
            response = self.session.post(self.base_url + path, json=body, timeout=TIMEOUT,
                                         allow_redirects=False)
        except OfflineViolation as err:
            raise EnforcerError(f"{err} (add the firewall to MAXGUARD_OFFLINE_ALLOW)") from err
        except requests.RequestException as err:
            raise EnforcerError(f"OPNsense not reachable: {err}") from err
        if response.status_code != 200:
            raise EnforcerError(f"OPNsense answered HTTP {response.status_code} for {path}")
        try:
            status = response.json().get("status")
        except (ValueError, AttributeError):
            raise EnforcerError(f"OPNsense sent an answer that is not JSON for {path}") from None
        if status != expected:
            raise EnforcerError(f"OPNsense said {status!r} for {path} (expected {expected!r})")


def read_api_key(path: Path) -> tuple[str, str]:
    """Read the key file OPNsense lets you download once: lines key=... and secret=..."""
    values = {}
    for line in Path(path).read_text().splitlines():
        name, sep, value = line.strip().partition("=")  # the secret itself may end in "="
        if sep:
            values[name] = value
    if not values.get("key") or not values.get("secret"):
        raise EnforcerError(f"{path} needs a key=... line and a secret=... line")
    return values["key"], values["secret"]


def from_env(data_dir: Path, alias: str) -> OPNsenseEnforcer | None:
    """The enforcer the user configured, or None when MAXGUARD_OPNSENSE_URL is not set."""
    url = os.environ.get("MAXGUARD_OPNSENSE_URL")
    if not url:
        return None
    key_file = Path(data_dir) / KEY_FILE
    if not key_file.is_file():
        raise EnforcerError(f"MAXGUARD_OPNSENSE_URL is set but {key_file} does not exist")
    key, secret = read_api_key(key_file)
    return OPNsenseEnforcer(url, key, secret, alias=alias,
                            ca_file=os.environ.get("MAXGUARD_OPNSENSE_CA") or None)
```

The endpoints come from OPNsense's own source code (`opnsense/core`, commit `1177021c22d6dedb63ff9bffd6300e789a8822e2`, October 6, 2026): `POST /api/firewall/alias_util/add/<alias>` and `.../delete/<alias>` with `{"address": ip}` (`AliasUtilController.php`; they change the live `pf` table at once through `pfctl -t <alias> -T add`) and `POST /api/firewall/alias/reconfigure` (`AliasController.php`, the "Apply" step). The key file has `key=` and `secret=` lines and is sent with HTTP basic auth (OPNsense's API how-to, `api.rst`). The client accepts only `https://`, always verifies the certificate (your CA file or the system's), uses short timeouts, follows no redirects, and ignores proxy settings (`trust_env = False`): the request goes straight to your firewall, and never toward the blocked address.

**Step 4.** Create `maxguard/response/routes.py`, the API under `/api/response`:

```python
"""JSON API for block proposals under /api/response (Ahmad, AHM-08).

create_app() in maxguard/api/app.py includes this router when it imports. The
routes read the stores from request.app.state and read the clock (time.time())
like the rest of the API; approvals.py and preview.py never do.

    POST /api/response/proposals                  {actor, ip, direction, reason?, finding_id?}
    GET  /api/response/proposals
    GET  /api/response/proposals/{id}
    POST /api/response/proposals/{id}/preview     {actor}
    POST /api/response/proposals/{id}/approve     {actor, confirm_ip}
    POST /api/response/proposals/{id}/apply       {actor}
    POST /api/response/proposals/{id}/revert      {actor}
    POST /api/response/proposals/{id}/reject      {actor, reason?}

apply uses the OPNsense enforcer when MAXGUARD_OPNSENSE_URL is set; otherwise
it records that the person ran the generated commands by hand.
Errors: 400 bad input or wrong typed IP, 404 no such proposal, 409 step not
allowed now (or the address already has an open proposal), 502 the firewall
refused or could not be reached.
"""

from __future__ import annotations

import time

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel, Field

from maxguard.response.approvals import ProposalStore, WrongState
from maxguard.response.enforcers import opnsense
from maxguard.response.enforcers.base import EnforcerError
from maxguard.response.generate import OPNSENSE_ALIASES, sides
from maxguard.response.preview import preview

router = APIRouter(prefix="/api/response")


class NewProposal(BaseModel):
    actor: str = Field(min_length=1, max_length=100)
    ip: str = Field(min_length=1, max_length=100)
    direction: str = "both"
    reason: str = Field(default="", max_length=1000)
    finding_id: str | None = Field(default=None, max_length=100)


class Step(BaseModel):
    actor: str = Field(min_length=1, max_length=100)
    reason: str = Field(default="", max_length=1000)


class Approval(BaseModel):
    actor: str = Field(min_length=1, max_length=100)
    confirm_ip: str = Field(default="", max_length=100)  # missing -> refused, and audited


def proposals(request: Request) -> ProposalStore:
    """One ProposalStore per app, made on first use (it creates its table once)."""
    state = request.app.state
    if getattr(state, "proposal_store", None) is None:
        state.proposal_store = ProposalStore(state.state_store)
    return state.proposal_store


def enforcers_for(request: Request, direction: str) -> list:
    """The configured OPNsense enforcers (one alias per side), or [] when none is set up."""
    enforcers = []
    for side in sides(direction):
        enforcer = opnsense.from_env(request.app.state.data_dir, OPNSENSE_ALIASES[side])
        if enforcer is not None:
            enforcers.append(enforcer)
    return enforcers


def run_step(step):
    """Call one workflow step and turn its errors into HTTP answers."""
    try:
        return step()
    except KeyError:
        raise HTTPException(404, "no such proposal") from None
    except WrongState as err:
        raise HTTPException(409, str(err)) from None
    except EnforcerError as err:
        raise HTTPException(502, str(err)) from None
    except ValueError as err:
        raise HTTPException(400, str(err)) from None


@router.post("/proposals")
def create_proposal(request: Request, body: NewProposal) -> dict:
    return run_step(lambda: proposals(request).propose(
        ip=body.ip, direction=body.direction, actor=body.actor, at=time.time(),
        reason=body.reason, finding_id=body.finding_id))


@router.get("/proposals")
def list_proposals(request: Request, limit: int = Query(200, ge=1, le=1000)) -> list[dict]:
    return proposals(request).list_proposals(limit=limit)


@router.get("/proposals/{proposal_id}")
def get_proposal(request: Request, proposal_id: int) -> dict:
    return run_step(lambda: proposals(request).get(proposal_id))


@router.post("/proposals/{proposal_id}/preview")
def preview_proposal(request: Request, proposal_id: int, body: Step) -> dict:
    store = proposals(request)
    proposal = run_step(lambda: store.get(proposal_id))
    now = time.time()
    summary = preview(proposal["ip"], proposal["direction"], request.app.state.event_store,
                      window_end=now)
    return run_step(lambda: store.record_preview(proposal_id, actor=body.actor,
                                                 preview=summary, at=now))


@router.post("/proposals/{proposal_id}/approve")
def approve_proposal(request: Request, proposal_id: int, body: Approval) -> dict:
    return run_step(lambda: proposals(request).approve(
        proposal_id, actor=body.actor, confirm_ip=body.confirm_ip, at=time.time()))


@router.post("/proposals/{proposal_id}/apply")
def apply_proposal(request: Request, proposal_id: int, body: Step) -> dict:
    store = proposals(request)

    def step():
        proposal = store.get(proposal_id)
        enforcers = enforcers_for(request, proposal["direction"])
        return store.mark_applied(proposal_id, actor=body.actor, at=time.time(),
                                  enforcers=enforcers)
    return run_step(step)


@router.post("/proposals/{proposal_id}/revert")
def revert_proposal(request: Request, proposal_id: int, body: Step) -> dict:
    store = proposals(request)

    def step():
        proposal = store.get(proposal_id)
        # Undo the same way it was applied: a block applied by hand is undone by hand.
        enforcers = []
        if proposal["method"] == "enforcer":
            enforcers = enforcers_for(request, proposal["direction"])
        return store.revert(proposal_id, actor=body.actor, at=time.time(), enforcers=enforcers)
    return run_step(step)


@router.post("/proposals/{proposal_id}/reject")
def reject_proposal(request: Request, proposal_id: int, body: Step) -> dict:
    return run_step(lambda: proposals(request).reject(
        proposal_id, actor=body.actor, at=time.time(), reason=body.reason))
```

`create_app()` (JAI-07) includes this router automatically now that the module exists. It is part of the dashboard's app on `127.0.0.1` only, never the ingest-only app that sensors reach. Errors: 400 bad input or a wrong typed IP, 404 no such proposal, 409 a step that is not allowed now (or the address already has an open proposal), 502 the firewall refused or could not be reached. The `actor` name is typed by the person, not checked by a login: that is acceptable only because this API listens on `127.0.0.1`.

**Step 5.** Create the tests `tests/unit/test_response_approvals.py`:

```python
"""Tests for maxguard.response.approvals (Ahmad, AHM-08)."""

import sqlite3
import threading

import pytest

from maxguard.response import approvals
from maxguard.response.approvals import ProposalStore, WrongState
from maxguard.response.enforcers.base import EnforcerError
from maxguard.storage.state import StateStore

T0 = 1791331200.0  # times are passed in; the store never reads the clock
PREVIEW = {"connections": 3, "devices": ["192.168.1.20"], "window_end": T0}


class FakeEnforcer:
    """Keeps a block list in memory, like a firewall alias."""

    def __init__(self, fail: bool = False):
        self.blocked: set[str] = set()
        self.applied = 0
        self.removed = 0
        self.fail = fail

    def add(self, ip: str) -> None:
        if self.fail:
            raise EnforcerError("firewall said no")
        self.blocked.add(ip)

    def remove(self, ip: str) -> None:
        self.removed += 1
        self.blocked.discard(ip)

    def apply(self) -> None:
        self.applied += 1


@pytest.fixture
def state(tmp_path):
    return StateStore(tmp_path / "state.db")


@pytest.fixture
def store(state):
    return ProposalStore(state)


def approved(store: ProposalStore, ip: str = "203.0.113.7") -> int:
    proposal_id = store.propose(ip=ip, direction="both", actor="ahmad", at=T0)["proposal_id"]
    store.record_preview(proposal_id, actor="ahmad", preview=PREVIEW, at=T0 + 1)
    store.approve(proposal_id, actor="fiona", confirm_ip=ip, at=T0 + 2)
    return proposal_id


def actions(state: StateStore) -> list[str]:
    return [row["action"] for row in reversed(state.list_audit())]


def test_full_workflow_is_audited(store, state):
    proposal_id = approved(store)
    firewall = FakeEnforcer()
    applied = store.mark_applied(proposal_id, actor="fiona", at=T0 + 3, enforcers=[firewall])
    assert applied["state"] == "applied" and applied["method"] == "enforcer"
    assert firewall.blocked == {"203.0.113.7"} and firewall.applied == 1
    reverted = store.revert(proposal_id, actor="ahmad", at=T0 + 4, enforcers=[firewall])
    assert reverted["state"] == "reverted"
    assert firewall.blocked == set()  # revert removed the address
    assert actions(state) == ["response.proposed", "response.previewed", "response.approved",
                              "response.applied", "response.reverted"]
    rows = list(reversed(state.list_audit()))
    assert {row["target"] for row in rows} == {str(proposal_id)}
    assert [row["at"] for row in rows] == [T0, T0 + 1, T0 + 2, T0 + 3, T0 + 4]
    assert rows[2]["actor"] == "fiona"


def test_proposal_shows_the_commands_and_their_undo(store):
    proposal = store.propose(ip="2001:DB8::7", direction="inbound", actor="ahmad", at=T0)
    assert proposal["ip"] == "2001:db8::7"
    assert proposal["rules"]["nftables"]["undo"]
    assert proposal["state"] == "proposed" and proposal["preview"] is None


@pytest.mark.parametrize("text", ["1.2.3.4; rm -rf /", "127.0.0.1", "ff02::1", "0.0.0.0",
                                  "169.254.1.1", "2001:db8::1%$(id)"])
def test_bad_addresses_cannot_be_proposed(store, state, text):
    with pytest.raises(ValueError):
        store.propose(ip=text, direction="both", actor="ahmad", at=T0)
    assert store.list_proposals() == [] and state.list_audit() == []


@pytest.mark.parametrize("typed", [None, "", "203.0.113.8", "203.0.113.7; rm -rf /"])
def test_approval_needs_the_same_ip_typed_again(store, state, typed):
    proposal_id = store.propose(ip="203.0.113.7", direction="both", actor="a", at=T0)[
        "proposal_id"]
    store.record_preview(proposal_id, actor="a", preview=PREVIEW, at=T0)
    with pytest.raises(ValueError, match="does not match"):
        store.approve(proposal_id, actor="fiona", confirm_ip=typed, at=T0 + 1)
    assert store.get(proposal_id)["state"] == "previewed"
    assert actions(state)[-1] == "response.approve_refused"  # refusals are logged too


def test_ipv6_typed_in_another_spelling_matches(store):
    proposal_id = approved(store, ip="2001:db8::7")
    assert store.get(proposal_id)["approved_by"] == "fiona"
    other = store.propose(ip="2001:db8::8", direction="both", actor="a", at=T0)["proposal_id"]
    store.record_preview(other, actor="a", preview=PREVIEW, at=T0)
    assert store.approve(other, actor="b", confirm_ip="2001:DB8:0::8", at=T0)["state"] == \
        "approved"


def test_no_approval_without_a_preview(store):
    proposal_id = store.propose(ip="203.0.113.7", direction="both", actor="a", at=T0)[
        "proposal_id"]
    with pytest.raises(WrongState):
        store.approve(proposal_id, actor="a", confirm_ip="203.0.113.7", at=T0)


def test_steps_out_of_order_are_refused(store):
    proposal_id = store.propose(ip="203.0.113.7", direction="both", actor="a", at=T0)[
        "proposal_id"]
    with pytest.raises(WrongState):
        store.mark_applied(proposal_id, actor="a", at=T0)       # not approved yet
    with pytest.raises(WrongState):
        store.revert(proposal_id, actor="a", at=T0)             # not applied yet
    with pytest.raises(KeyError):
        store.approve(999, actor="a", confirm_ip="203.0.113.7", at=T0)


def test_approved_twice_is_refused(store):
    proposal_id = approved(store)
    with pytest.raises(WrongState):
        store.approve(proposal_id, actor="b", confirm_ip="203.0.113.7", at=T0 + 5)


def test_manual_apply_and_revert(store, state):
    proposal_id = approved(store)
    assert store.mark_applied(proposal_id, actor="a", at=T0 + 3)["method"] == "manual"
    assert store.revert(proposal_id, actor="a", at=T0 + 4)["state"] == "reverted"
    assert state.list_audit()[0]["details"] == {"ip": "203.0.113.7", "method": "manual"}


def test_enforcer_failure_keeps_it_approved_and_is_audited(store, state):
    proposal_id = approved(store)
    with pytest.raises(EnforcerError):
        store.mark_applied(proposal_id, actor="a", at=T0 + 3, enforcers=[FakeEnforcer(True)])
    assert store.get(proposal_id)["state"] == "approved"
    assert actions(state)[-1] == "response.apply_failed"


def test_enforcer_block_needs_the_enforcer_to_revert(store):
    proposal_id = approved(store)
    store.mark_applied(proposal_id, actor="a", at=T0 + 3, enforcers=[FakeEnforcer()])
    with pytest.raises(ValueError, match="connector"):
        store.revert(proposal_id, actor="a", at=T0 + 4)
    assert store.get(proposal_id)["state"] == "applied"


def test_reject(store, state):
    proposal_id = store.propose(ip="203.0.113.7", direction="both", actor="a", at=T0)[
        "proposal_id"]
    assert store.reject(proposal_id, actor="b", at=T0 + 1, reason="our VPN")["state"] == \
        "rejected"
    with pytest.raises(WrongState):
        store.reject(proposal_id, actor="b", at=T0 + 2)
    assert actions(state)[-1] == "response.rejected"


def test_preview_is_kept_with_the_proposal(store):
    proposal_id = approved(store)
    assert store.get(proposal_id)["preview"] == PREVIEW


def test_a_state_change_and_its_audit_row_are_one_transaction(store, state, monkeypatch):
    proposal_id = store.propose(ip="203.0.113.7", direction="both", actor="ahmad",
                                at=T0)["proposal_id"]

    def broken_audit(*args, **kwargs):  # as if the disk filled up at this moment
        raise sqlite3.OperationalError("disk I/O error")

    monkeypatch.setattr(approvals, "insert_audit", broken_audit)
    with pytest.raises(sqlite3.OperationalError):
        store.reject(proposal_id, actor="ahmad", at=T0 + 1)
    # The UPDATE was rolled back with the failed audit row: no change without its record.
    assert store.get(proposal_id)["state"] == "proposed"
    assert actions(state) == ["response.proposed"]


def test_one_open_proposal_per_address(store, state):
    first = store.propose(ip="203.0.113.7", direction="inbound", actor="a", at=T0)
    # Two open proposals for one address: reverting one would silently remove the
    # block the other still shows as applied. So the second one is refused.
    with pytest.raises(WrongState, match="open proposal"):
        store.propose(ip="203.0.113.7", direction="both", actor="b", at=T0 + 1)
    store.reject(first["proposal_id"], actor="a", at=T0 + 2)
    again = store.propose(ip="203.0.113.7", direction="both", actor="b", at=T0 + 3)
    assert again["state"] == "proposed"
    assert actions(state) == ["response.proposed", "response.rejected", "response.proposed"]


def test_a_failed_apply_takes_the_address_off_the_other_firewall_lists(store, state):
    proposal_id = approved(store)
    inbound, outbound = FakeEnforcer(), FakeEnforcer(fail=True)
    with pytest.raises(EnforcerError):
        store.mark_applied(proposal_id, actor="a", at=T0 + 3, enforcers=[inbound, outbound])
    # The first list had the address; it was removed again, so nothing stays half-blocked.
    assert inbound.blocked == set() and inbound.removed == 1
    assert store.get(proposal_id)["state"] == "approved"
    assert state.list_audit()[0]["details"] == {"error": "firewall said no", "undone": True}


class SlowEnforcer(FakeEnforcer):
    """add() waits until the test says go, like a slow firewall."""

    def __init__(self):
        super().__init__()
        self.adds = 0
        self.entered = threading.Event()
        self.go = threading.Event()

    def add(self, ip: str) -> None:
        self.adds += 1
        self.entered.set()
        self.go.wait(5)
        super().add(ip)


def test_a_double_click_on_apply_reaches_the_firewall_once(store):
    proposal_id = approved(store)
    firewall = SlowEnforcer()
    results = []

    def click():
        try:
            store.mark_applied(proposal_id, actor="a", at=T0 + 3, enforcers=[firewall])
            results.append("applied")
        except WrongState:
            results.append("refused")

    first, second = threading.Thread(target=click), threading.Thread(target=click)
    first.start()
    assert firewall.entered.wait(5)  # the first click is talking to the firewall
    second.start()
    second.join(0.2)                 # the second click waits for the first one
    firewall.go.set()
    first.join(5)
    second.join(5)
    assert firewall.adds == 1
    assert sorted(results) == ["applied", "refused"]
```

`tests/unit/test_opnsense.py` (a fake OPNsense: `http.server` on `127.0.0.1` wrapped in TLS with a throwaway test CA, so the tests also prove that an untrusted certificate is refused):

```python
"""Tests for the OPNsense enforcer (Ahmad, AHM-08).

Never a real firewall: FakeOPNsense is a small HTTPS server on 127.0.0.1 that
answers the three alias endpoints the way OPNsense's AliasUtilController and
AliasController do. Its certificate comes from a test CA made here, so the tests
also prove that TLS verification is on. test_response_routes.py reuses it.
"""

from __future__ import annotations

import base64
import datetime
import ipaddress
import json
import socket
import ssl
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID

from maxguard import offline
from maxguard.offline import OfflineViolation
from maxguard.response.enforcers.base import EnforcerError
from maxguard.response.enforcers.opnsense import OPNsenseEnforcer, from_env, read_api_key

KEY = "test-key"
SECRET = "test-secret=="          # real secrets are base64 and may end in "="
FIREWALL_NAME = "fw.home.arpa"    # home.arpa is reserved for home networks (RFC 8375)


# ---------- a test certificate authority and server certificate ----------

def name(common_name: str) -> x509.Name:
    return x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, common_name)])


def make_certificates(folder: Path) -> tuple[Path, Path, Path]:
    """Returns (ca_file, server_cert_file, server_key_file)."""
    now = datetime.datetime.now(datetime.UTC)
    ca_key = ec.generate_private_key(ec.SECP256R1())
    ca_cert = (
        x509.CertificateBuilder().subject_name(name("MaxGuard test CA"))
        .issuer_name(name("MaxGuard test CA")).public_key(ca_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - datetime.timedelta(minutes=5))
        .not_valid_after(now + datetime.timedelta(days=1))
        .add_extension(x509.BasicConstraints(ca=True, path_length=0), critical=True)
        .add_extension(x509.KeyUsage(digital_signature=False, content_commitment=False,
                                     key_encipherment=False, data_encipherment=False,
                                     key_agreement=False, key_cert_sign=True, crl_sign=True,
                                     encipher_only=False, decipher_only=False), critical=True)
        .add_extension(x509.SubjectKeyIdentifier.from_public_key(ca_key.public_key()),
                       critical=False)
        .sign(ca_key, hashes.SHA256()))
    server_key = ec.generate_private_key(ec.SECP256R1())
    server_cert = (
        x509.CertificateBuilder().subject_name(name(FIREWALL_NAME))
        .issuer_name(ca_cert.subject).public_key(server_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - datetime.timedelta(minutes=5))
        .not_valid_after(now + datetime.timedelta(days=1))
        .add_extension(x509.SubjectAlternativeName([
            x509.DNSName(FIREWALL_NAME), x509.IPAddress(ipaddress.ip_address("127.0.0.1"))]),
            critical=False)
        .add_extension(x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH]), critical=False)
        .add_extension(x509.AuthorityKeyIdentifier.from_issuer_public_key(ca_key.public_key()),
                       critical=False)
        .sign(ca_key, hashes.SHA256()))
    ca_file, cert_file, key_file = folder / "ca.pem", folder / "server.pem", folder / "key.pem"
    ca_file.write_bytes(ca_cert.public_bytes(serialization.Encoding.PEM))
    cert_file.write_bytes(server_cert.public_bytes(serialization.Encoding.PEM))
    key_file.write_bytes(server_key.private_bytes(serialization.Encoding.PEM,
                                                  serialization.PrivateFormat.PKCS8,
                                                  serialization.NoEncryption()))
    return ca_file, cert_file, key_file


# ---------- the fake firewall ----------

class FakeOPNsense:
    """Remembers the alias contents and every request it was sent."""

    def __init__(self, folder: Path):
        self.aliases: dict[str, set[str]] = {"maxguard_block_in": set(),
                                             "maxguard_block_out": set()}
        self.requests: list[tuple[str, dict]] = []
        self.reconfigures = 0
        self.redirects: dict[str, str] = {}  # path -> where to send the client instead
        self.ca_file, cert_file, key_file = make_certificates(folder)
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(cert_file, key_file)
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), self.handler_class())
        self.server.socket = context.wrap_socket(self.server.socket, server_side=True)
        self.port = self.server.server_address[1]
        self.url = f"https://127.0.0.1:{self.port}"
        # A short poll interval makes stop() quick (the default waits up to 0.5 s).
        self.thread = threading.Thread(target=self.server.serve_forever, args=(0.05,),
                                       daemon=True)
        self.thread.start()

    def stop(self) -> None:
        self.server.shutdown()
        self.server.server_close()

    def answer(self, path: str, body: dict) -> tuple[int, dict]:
        """What OPNsense would answer (see AliasUtilController.php / AliasController.php)."""
        self.requests.append((path, body))
        parts = path.strip("/").split("/")
        if parts[:3] == ["api", "firewall", "alias_util"] and len(parts) == 5:
            action, alias = parts[3], parts[4]
            if alias not in self.aliases or "address" not in body:
                return 200, {"status": "failed"}
            if action == "add":
                self.aliases[alias].add(body["address"])
                return 200, {"status": "done"}
            if action == "delete":
                self.aliases[alias].discard(body["address"])
                return 200, {"status": "done"}
        if parts == ["api", "firewall", "alias", "reconfigure"]:
            self.reconfigures += 1
            return 200, {"status": "ok"}
        return 404, {"message": "not found"}

    def handler_class(self):
        fake = self
        expected = "Basic " + base64.b64encode(f"{KEY}:{SECRET}".encode()).decode()

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):  # noqa: N802 (the name http.server expects)
                length = int(self.headers.get("Content-Length", 0))
                body = json.loads(self.rfile.read(length) or b"{}")
                if self.path in fake.redirects:
                    fake.requests.append((self.path, body))
                    self.send_response(307)
                    self.send_header("Location", fake.redirects[self.path])
                    self.send_header("Content-Length", "0")
                    self.end_headers()
                    return
                if self.headers.get("Authorization") != expected:
                    status, answer = 401, {"message": "Authentication Failed"}
                else:
                    status, answer = fake.answer(self.path, body)
                data = json.dumps(answer).encode()
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def log_message(self, *args):  # keep the test output quiet
                pass

        return Handler


@pytest.fixture
def firewall(tmp_path):
    fake = FakeOPNsense(tmp_path)
    yield fake
    fake.stop()


def enforcer(fake: FakeOPNsense, alias: str = "maxguard_block_in", **kwargs):
    options = {"ca_file": str(fake.ca_file), **kwargs}
    return OPNsenseEnforcer(fake.url, KEY, SECRET, alias=alias, **options)


# ---------- tests ----------

def test_add_apply_remove(firewall):
    client = enforcer(firewall)
    client.add("203.0.113.7")
    client.apply()
    assert firewall.aliases["maxguard_block_in"] == {"203.0.113.7"}
    assert firewall.reconfigures == 1
    client.remove("203.0.113.7")
    client.apply()
    assert firewall.aliases["maxguard_block_in"] == set()
    assert [path for path, _ in firewall.requests] == [
        "/api/firewall/alias_util/add/maxguard_block_in",
        "/api/firewall/alias/reconfigure",
        "/api/firewall/alias_util/delete/maxguard_block_in",
        "/api/firewall/alias/reconfigure",
    ]


def test_ipv6_is_sent_in_its_short_lower_case_form(firewall):
    # OPNsense's addAction refuses characters outside [0-9a-f:./_] (no upper case).
    enforcer(firewall, alias="maxguard_block_out").add("2001:DB8:0:0:0:0:0:7")
    assert firewall.aliases["maxguard_block_out"] == {"2001:db8::7"}


def test_tls_is_verified(firewall):
    # Without the firewall's CA file the certificate is not trusted: refused.
    client = OPNsenseEnforcer(firewall.url, KEY, SECRET, alias="maxguard_block_in")
    with pytest.raises(EnforcerError, match="CERTIFICATE_VERIFY_FAILED|certificate verify"):
        client.add("203.0.113.7")
    assert firewall.requests == []


def test_plain_http_is_refused():
    with pytest.raises(ValueError, match="https"):
        OPNsenseEnforcer("http://127.0.0.1:8443", KEY, SECRET, alias="maxguard_block_in")


def test_bad_alias_name_is_refused():
    with pytest.raises(ValueError):
        OPNsenseEnforcer("https://127.0.0.1", KEY, SECRET, alias="x/../../core")


def test_wrong_secret_is_an_error(firewall):
    client = OPNsenseEnforcer(firewall.url, KEY, "wrong", alias="maxguard_block_in",
                              ca_file=str(firewall.ca_file))
    with pytest.raises(EnforcerError, match="401"):
        client.add("203.0.113.7")
    assert firewall.aliases["maxguard_block_in"] == set()


def test_redirects_are_not_followed(firewall):
    # A redirect could send the request (and the API key) somewhere else: refuse it.
    firewall.redirects["/api/firewall/alias_util/add/maxguard_block_in"] = (
        firewall.url + "/api/firewall/alias_util/add/maxguard_block_out")
    with pytest.raises(EnforcerError, match="307"):
        enforcer(firewall).add("203.0.113.7")
    assert len(firewall.requests) == 1
    assert firewall.aliases["maxguard_block_out"] == set()


def test_unknown_alias_is_an_error(firewall):
    with pytest.raises(EnforcerError, match="failed"):
        enforcer(firewall, alias="not_there").add("203.0.113.7")


@pytest.mark.parametrize("text", ["1.2.3.4; rm -rf /", "127.0.0.1", "2001:db8::1%$(id)"])
def test_hostile_input_never_reaches_the_firewall(firewall, text):
    with pytest.raises(ValueError):
        enforcer(firewall).add(text)
    assert firewall.requests == []


def test_unreachable_firewall_is_an_error(tmp_path):
    with socket.socket() as probe:  # a port with nothing listening
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]
    client = OPNsenseEnforcer(f"https://127.0.0.1:{port}", KEY, SECRET,
                              alias="maxguard_block_in")
    with pytest.raises(EnforcerError, match="not reachable"):
        client.add("203.0.113.7")


def test_read_api_key(tmp_path):
    key_file = tmp_path / "apikey.txt"
    key_file.write_text(f"key={KEY}\nsecret={SECRET}\n")
    assert read_api_key(key_file) == (KEY, SECRET)
    key_file.write_text(f"key={KEY}\n")
    with pytest.raises(EnforcerError, match="secret"):
        read_api_key(key_file)


def test_from_env(tmp_path, monkeypatch, firewall):
    monkeypatch.delenv("MAXGUARD_OPNSENSE_URL", raising=False)
    assert from_env(tmp_path, "maxguard_block_in") is None  # not configured: manual steps

    monkeypatch.setenv("MAXGUARD_OPNSENSE_URL", firewall.url)
    monkeypatch.setenv("MAXGUARD_OPNSENSE_CA", str(firewall.ca_file))
    with pytest.raises(EnforcerError, match="apikey.txt"):
        from_env(tmp_path, "maxguard_block_in")              # the key file is missing

    (tmp_path / "opnsense").mkdir()
    (tmp_path / "opnsense" / "apikey.txt").write_text(f"key={KEY}\nsecret={SECRET}\n")
    from_env(tmp_path, "maxguard_block_in").add("198.51.100.20")
    assert firewall.aliases["maxguard_block_in"] == {"198.51.100.20"}


# ---------- with the offline guard on ----------

@pytest.fixture
def firewall_name(monkeypatch):
    """Make fw.home.arpa resolve to 127.0.0.1 (as a home router's DNS would)."""
    real_getaddrinfo = socket.getaddrinfo

    def fake_getaddrinfo(host, *args, **kwargs):
        if host == FIREWALL_NAME:
            host = "127.0.0.1"
        return real_getaddrinfo(host, *args, **kwargs)

    monkeypatch.setattr(socket, "getaddrinfo", fake_getaddrinfo)
    yield
    offline.disable()  # before monkeypatch puts the real getaddrinfo back


def test_works_with_the_guard_on_when_the_firewall_is_allowed(firewall, firewall_name):
    # The same as MAXGUARD_OFFLINE=1 with MAXGUARD_OFFLINE_ALLOW=fw.home.arpa
    offline.enable("http://127.0.0.1:11434", extra_allowed=[FIREWALL_NAME])
    client = OPNsenseEnforcer(f"https://{FIREWALL_NAME}:{firewall.port}", KEY, SECRET,
                              alias="maxguard_block_in", ca_file=str(firewall.ca_file))
    client.add("203.0.113.7")  # only the firewall is contacted, never 203.0.113.7
    client.apply()
    assert firewall.aliases["maxguard_block_in"] == {"203.0.113.7"}


def test_guard_stops_a_firewall_that_is_not_allowed(firewall, firewall_name):
    offline.enable("http://127.0.0.1:11434")  # MAXGUARD_OFFLINE_ALLOW not set
    client = OPNsenseEnforcer(f"https://{FIREWALL_NAME}:{firewall.port}", KEY, SECRET,
                              alias="maxguard_block_in", ca_file=str(firewall.ca_file))
    with pytest.raises(EnforcerError, match="MAXGUARD_OFFLINE_ALLOW") as caught:
        client.add("203.0.113.7")
    assert isinstance(caught.value.__cause__, OfflineViolation)
    assert firewall.requests == []
```

and `tests/unit/test_response_routes.py`:

```python
"""Tests for the /api/response routes (Ahmad, AHM-08).

The whole app from maxguard/api/app.py, with TestClient, and the fake OPNsense
server from test_opnsense.py (never a real firewall).
"""

import time

import pytest
from fastapi.testclient import TestClient
from test_opnsense import KEY, SECRET, FakeOPNsense

from maxguard.api.app import create_app
from maxguard.events.normalize import EVENT_KEYS

BAD = "203.0.113.7"


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.delenv("MAXGUARD_OPNSENSE_URL", raising=False)
    monkeypatch.delenv("MAXGUARD_OFFLINE", raising=False)
    return TestClient(create_app(tmp_path / "data", explain=False))


@pytest.fixture
def firewall(tmp_path, monkeypatch):
    """A fake OPNsense, configured the way a user would: URL, CA file, key file."""
    fake = FakeOPNsense(tmp_path)
    monkeypatch.setenv("MAXGUARD_OPNSENSE_URL", fake.url)
    monkeypatch.setenv("MAXGUARD_OPNSENSE_CA", str(fake.ca_file))
    key_dir = tmp_path / "data" / "opnsense"
    key_dir.mkdir(parents=True)
    (key_dir / "apikey.txt").write_text(f"key={KEY}\nsecret={SECRET}\n")
    yield fake
    fake.stop()


def propose(client, ip=BAD, direction="both") -> dict:
    response = client.post("/api/response/proposals",
                           json={"actor": "ahmad", "ip": ip, "direction": direction})
    assert response.status_code == 200, response.text
    return response.json()


def step(client, proposal_id: int, name: str, **body):
    return client.post(f"/api/response/proposals/{proposal_id}/{name}",
                       json={"actor": "ahmad", **body})


def response_audit(client) -> list[dict]:
    rows = client.get("/api/audit").json()
    return [row for row in reversed(rows) if row["action"].startswith("response.")]


def test_manual_workflow(client):
    proposal = propose(client)
    pid = proposal["proposal_id"]
    assert proposal["rules"]["nftables"]["block"]       # the commands are shown at once
    assert step(client, pid, "preview").json()["preview"]["connections"] == 0
    assert step(client, pid, "approve", confirm_ip=BAD).json()["state"] == "approved"
    applied = step(client, pid, "apply").json()
    assert applied["state"] == "applied" and applied["method"] == "manual"
    assert step(client, pid, "revert").json()["state"] == "reverted"
    assert [row["action"] for row in response_audit(client)] == [
        "response.proposed", "response.previewed", "response.approved",
        "response.applied", "response.reverted"]
    assert {row["target"] for row in response_audit(client)} == {str(pid)}


def test_approval_without_the_typed_ip_fails(client):
    pid = propose(client)["proposal_id"]
    step(client, pid, "preview")
    assert step(client, pid, "approve").status_code == 400                  # missing
    assert step(client, pid, "approve", confirm_ip="203.0.113.8").status_code == 400
    assert client.post(f"/api/response/proposals/{pid}/approve",
                       json={"confirm_ip": BAD}).status_code == 422          # no actor
    assert client.get(f"/api/response/proposals/{pid}").json()["state"] == "previewed"
    refused = [r for r in response_audit(client) if r["action"] == "response.approve_refused"]
    assert len(refused) == 2


@pytest.mark.parametrize("ip", ["1.2.3.4; rm -rf /", "127.0.0.1", "::1", "224.0.0.251",
                                "0.0.0.0", "fe80::1", "2001:db8::1%$(id)"])
def test_bad_addresses_are_refused(client, ip):
    response = client.post("/api/response/proposals",
                           json={"actor": "ahmad", "ip": ip, "direction": "both"})
    assert response.status_code == 400
    assert client.get("/api/response/proposals").json() == []


def test_unknown_direction_is_refused(client):
    response = client.post("/api/response/proposals",
                           json={"actor": "ahmad", "ip": BAD, "direction": "sideways"})
    assert response.status_code == 400


def test_missing_proposal_and_wrong_order(client):
    assert client.get("/api/response/proposals/42").status_code == 404
    assert step(client, 42, "approve", confirm_ip=BAD).status_code == 404
    pid = propose(client)["proposal_id"]
    assert step(client, pid, "approve", confirm_ip=BAD).status_code == 409   # no preview yet
    assert step(client, pid, "revert").status_code == 409                    # not applied


def test_reject(client):
    pid = propose(client)["proposal_id"]
    assert step(client, pid, "reject", reason="our own VPN").json()["state"] == "rejected"
    assert step(client, pid, "preview").status_code == 409


def test_preview_counts_events_from_the_event_store(client):
    now = time.time()
    event = dict.fromkeys(EVENT_KEYS, "")
    event.update(event_id="ev1", ts=now - 3600, sensor_id="pcap", source="zeek",
                 log="conn.log", kind="conn", community_id="1:x=", src_ip=BAD,
                 dst_ip="192.168.1.20", src_port=40000, dst_port=22, proto="tcp",
                 service="ssh", bytes_out=1, bytes_in=1)
    client.app.state.event_store.write([event])
    pid = propose(client, direction="inbound")["proposal_id"]
    summary = step(client, pid, "preview").json()["preview"]
    assert summary["connections"] == 1 and summary["devices"] == ["192.168.1.20"]


def test_cross_site_requests_are_refused(client):
    response = client.post("/api/response/proposals",
                           json={"actor": "x", "ip": BAD, "direction": "both"},
                           headers={"Sec-Fetch-Site": "cross-site"})
    assert response.status_code == 403


def test_opnsense_apply_and_revert(client, firewall):
    pid = propose(client, direction="both")["proposal_id"]
    step(client, pid, "preview")
    step(client, pid, "approve", confirm_ip=BAD)
    applied = step(client, pid, "apply")
    assert applied.status_code == 200, applied.text
    assert applied.json()["method"] == "enforcer"
    assert firewall.aliases == {"maxguard_block_in": {BAD}, "maxguard_block_out": {BAD}}
    assert firewall.reconfigures == 2
    assert step(client, pid, "revert").json()["state"] == "reverted"
    assert firewall.aliases == {"maxguard_block_in": set(), "maxguard_block_out": set()}
    assert [row["action"] for row in response_audit(client)][-2:] == [
        "response.applied", "response.reverted"]


def test_firewall_error_is_502_and_nothing_changes(client, firewall):
    firewall.aliases = {}  # the user has not created the aliases on the firewall
    pid = propose(client)["proposal_id"]
    step(client, pid, "preview")
    step(client, pid, "approve", confirm_ip=BAD)
    response = step(client, pid, "apply")
    assert response.status_code == 502
    assert client.get(f"/api/response/proposals/{pid}").json()["state"] == "approved"
    assert response_audit(client)[-1]["action"] == "response.apply_failed"


def test_a_second_open_proposal_for_the_same_address_is_409(client):
    propose(client)
    response = client.post("/api/response/proposals",
                           json={"actor": "fiona", "ip": BAD, "direction": "inbound"})
    assert response.status_code == 409
    assert len(client.get("/api/response/proposals").json()) == 1
```

Run them:

```bash
pytest tests/unit/test_response_approvals.py tests/unit/test_opnsense.py tests/unit/test_response_routes.py -q
```

Expected output:

```text
..........................................................                                   [100%]
58 passed in 3.68s
```

**Step 6.** Walk through the whole workflow against the API. Start the server in one terminal, then run the rest in a second one:

```bash
# terminal 1:
uvicorn maxguard.api.app:create_app --factory --host 127.0.0.1 --port 8000
# terminal 2:
python -c "import shutil; shutil.make_archive('data/telnet', 'zip', 'tests/fixtures/zeek/telnet')"
curl -s -F file=@data/telnet.zip http://127.0.0.1:8000/api/analyses; echo
python - <<'EOF'
import requests

B = "http://127.0.0.1:8000/api/response/proposals"


def step(path, **body):
    """POST one step and print the answer in one line."""
    answer = requests.post(B + path, json=body, timeout=60)
    data = answer.json()
    print(answer.status_code, data.get("detail") or f"proposal {data['proposal_id']}: {data['state']}")
    return data


step("", actor="ahmad", ip="1.2.3.4; rm -rf /", direction="both")
p = step("", actor="ahmad", ip="172.18.0.3", direction="both", reason="Telnet client")
print("\n".join(p["rules"]["nftables"]["block"] + p["rules"]["nftables"]["undo"]))
seen = step("/1/preview", actor="ahmad")["preview"]
print("preview:", seen["connections"], "connection(s), devices", seen["devices"],
      "ports", [s["port"] for s in seen["services"]])
step("/1/approve", actor="fiona")                          # the IP was not typed again
step("/1/approve", actor="fiona", confirm_ip="172.18.0.3")
step("/1/apply", actor="fiona")                            # no firewall connector: by hand
step("/1/revert", actor="ahmad")
for row in reversed(requests.get("http://127.0.0.1:8000/api/audit", timeout=10).json()):
    print(row["actor"], row["action"], row["target"])
EOF
```

Expected output:

```text
{"analysis_id":"37b6bfbdbdf5f1fb","findings":1}
400 '1.2.3.4; rm -rf /' does not appear to be an IPv4 or IPv6 address
200 proposal 1: proposed
sudo nft 'add element inet maxguard maxguard_block_in_v4 { 172.18.0.3 }'
sudo nft 'add element inet maxguard maxguard_block_out_v4 { 172.18.0.3 }'
sudo nft 'delete element inet maxguard maxguard_block_in_v4 { 172.18.0.3 }'
sudo nft 'delete element inet maxguard maxguard_block_out_v4 { 172.18.0.3 }'
200 proposal 1: previewed
preview: 1 connection(s), devices ['172.18.0.2'] ports [23]
400 the IP address you typed does not match the proposal
200 proposal 1: approved
200 proposal 1: applied
200 proposal 1: reverted
ahmad response.proposed 1
ahmad response.previewed 1
fiona response.approve_refused 1
fiona response.approved 1
fiona response.applied 1
ahmad response.reverted 1
```

*The analysis ID depends on the moment of the upload, so yours differs. The preview counts only the 7 days before now: the fixture's traffic is from October 6, 2026, so on a later date your preview shows 0 connections. `apply` records a block made by hand because no firewall connector is configured.*

**Step 7.** **On an OPNsense test VM** (*not run — verify on hardware*; never a real firewall):

1. **Firewall > Aliases**: create `maxguard_block_in` and `maxguard_block_out`, type *Host(s)*, empty.
2. **Firewall > Rules > WAN**: a *Block* rule with source `maxguard_block_in`. **Firewall > Rules > LAN**: a *Block* rule with source `maxguard_block_in` (a device on your own network) and one with destination `maxguard_block_out`. On both pages, drag these Block rules **above** every Pass rule (such as *Default allow LAN to any rule*): OPNsense uses the first rule that matches, so a Block rule below a Pass rule never blocks anything. Apply.
3. **System > Access > Users**: a user `maxguard` with only the privileges *Diagnostics: PF Table IP addresses* and *Firewall: Alias: Edit* (OPNsense's `ACL.xml`). In its API keys section click **+**; the browser downloads the key file once.
4. On the MaxGuard machine, keep the key in the data folder (never in the repository) and point MaxGuard at the firewall:

```bash
mkdir -p data/opnsense
mv ~/Downloads/<the downloaded key file>.txt data/opnsense/apikey.txt
chmod 600 data/opnsense/apikey.txt
export MAXGUARD_OPNSENSE_URL=https://fw.home.arpa      # your test firewall
export MAXGUARD_OPNSENSE_CA=$PWD/data/opnsense/ca.pem  # if it uses its own CA
export MAXGUARD_OFFLINE_ALLOW=fw.home.arpa             # with MAXGUARD_OFFLINE=1
```

5. Repeat the walk-through: `apply` now adds the address to the alias (check **Firewall > Diagnostics > Aliases**), and `revert` removes it. Without `MAXGUARD_OFFLINE_ALLOW`, apply answers 502 with the hint to add the firewall there. Two limits to know: `pf` is stateful, so a connection that was already open keeps working until its state ends (check **Firewall > Diagnostics > States**); and a port forward whose *Filter rule association* is *Pass* skips all filter rules (OPNsense manual, *Firewall: Processing order*).

**Step 8.** Commit, push, and open the pull request:

```bash
git add -A
git status          # only this task's files: nothing from .venv/, data/ or lab/captures/
git commit -m "feat: approvals, audit and OPNsense enforcer (AHM-08)"
git push -u origin HEAD
```

`HEAD` means "the branch I am on", so you do not have to retype its name. Open the repository on github.com: a yellow bar shows your branch with a **Compare & pull request** button. Click it, keep the title `feat: approvals, audit and OPNsense enforcer (AHM-08)`, fill in the template (paste the real output of the commands above under **How I tested it**), write `Closes #<issue number>` (this task's issue), and pick **@JWinborne1** under **Reviewers**. Click **Create pull request**, then fix anything CI or the reviewer finds with new commits on the same branch.

#### How to test

The tests pass, and on a test OPNsense VM an approved block and its revert work.

#### What you just did and why

Typing the address again is a deliberate speed bump: it makes the person read what they are about to block. The audit trail and revert make every block accountable and reversible, and testing against a fake server means no test can ever change a real firewall.

#### Pull request checklist

- [ ] `ruff check .` prints `All checks passed!`
- [ ] `pytest -m "not integration" -q` passes on your laptop
- [ ] The pull request title has the form `type: summary (TASK-ID)` and the body says `Closes #<issue number>`
- [ ] No secrets, passwords, email addresses, personal data, or captures from a real network (CLAUDE.md rule 6)
- [ ] Any new dependency has a row in `docs/DEPENDENCIES.md` with its license
- [ ] CI is green and your reviewer approved
- [ ] No test talks to a real firewall
- [ ] The API key is read from the data folder

### AHM-09: v2.0 acceptance test

**Due:** Spring S14 (due Fri May 7, 2027) · **Milestone:** `S14 v2.0` · **Needs first:** [JAI-12](jaiden.md#jai-12-release-v20-rc1-and-v20) · **Kind:** process

**Issue labels:** `type:task` `phase:spring` `owner:ahmad` `area:program` `critical-path`

#### Goal

Run the `v2.0` acceptance test: the alpha test plus the live sensor on the reference lab, a blocked IP with preview and approval, a verified intel bundle, and the chain-of-custody check.

#### Prerequisites

JAI-12 has tagged `v2.0`.

#### Steps

**Step 1.** Follow the v2.0 acceptance test in `docs/roadmap/README.md` with someone who did not build the release, and record each result.

#### How to test

Every step passes or has an issue.

#### What you just did and why

The same rule as the alpha: done means someone else can use it.

#### Pull request checklist

- [ ] Acceptance results recorded
