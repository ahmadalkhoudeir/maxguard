# Ahmad: Security Lead

**Ahmad Al Khoudeir** (@ahmadalkhoudeir) · Module: Dashboard, response module · Reviewer for your pull requests: @JWinborne1 (Jaiden) · Ask first when stuck: Jaiden

This is your part of the MaxGuard v2.0 roadmap. Read [the roadmap overview](README.md) once, then work top to bottom: Week 0 first, then your tasks in order. Each task's ID is also the start of its GitHub issue's title.

## Your tasks

| Task | Due | Title | Needs first | Kind |
|---|---|---|---|---|
| [AHM-00](#week-0--onboarding-due-friday-october-9-2026) | W0 | Week 0 onboarding (Ahmad) | — | process |
| [AHM-01](#ahm-01-set-up-github-for-the-team-access-discussions-labels-milestones-issues) | W0 | Set up GitHub for the team: access, Discussions, labels, milestones, issues | — | process |
| [AHM-02](#ahm-02-dashboard-layout-alert-queue-and-upload-page) | W3 | Dashboard: layout, alert queue, and upload page | [JAI-07](jaiden.md#jai-07-the-api-uploads-alerts-events-live-updates-sensor-ingest) | design |
| [AHM-03](#ahm-03-alert-detail-page-with-analyst-and-home-modes) | W4 | Alert detail page with Analyst and Home modes | [AHM-02](#ahm-02-dashboard-layout-alert-queue-and-upload-page), [JON-02](jonattan.md#jon-02-ollama-client-one-evidence-citing-explanation-per-finding), [JON-04](jonattan.md#jon-04-home-mode-text-for-every-rule) | design |
| [AHM-04](#ahm-04-security-review-of-the-alpha) | W5 | Security review of the alpha | [AHM-03](#ahm-03-alert-detail-page-with-analyst-and-home-modes), [JON-03](jonattan.md#jon-03-offline-guard-make-accidental-network-access-fail-loudly), [AMO-03](amory.md#amo-03-report-export-json-csv-and-html) | process |
| [AHM-05](#ahm-05-alpha-acceptance-test-and-presentation) | W8 | Alpha acceptance test and presentation | [JAI-10](jaiden.md#jai-10-release-v20-alpha), [KAR-05](karthik.md#kar-05-release-candidate-test-with-an-outside-tester) | process |
| [AHM-06](#ahm-06-ip-timeline-and-device-inventory-pages) | S4 | IP timeline and device inventory pages | [AHM-03](#ahm-03-alert-detail-page-with-analyst-and-home-modes), [JAK-08](jakub.md#jak-08-device-attribution-which-device-is-behind-each-ip-address), [JAI-07](jaiden.md#jai-07-the-api-uploads-alerts-events-live-updates-sensor-ingest) | design |
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

**Due:** Week 3 (due Fri Oct 30) · **Milestone:** `W3 API and alert queue` · **Needs first:** [JAI-07](jaiden.md#jai-07-the-api-uploads-alerts-events-live-updates-sensor-ingest) · **Kind:** design

**Issue labels:** `type:task` `phase:alpha` `owner:ahmad` `area:ui` `critical-path`

> **Design task.** The code for this task was not written during planning. The steps give the files, the interfaces and the tests to write; the code is yours. Ask in GitHub Discussions when something is unclear, and update this section in your pull request with what you built.

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

On macOS use `shasum -a 256` instead of `sha256sum`. Add a row for htmx to `docs/DEPENDENCIES.md` if it is not there.

**Step 3.** Create `maxguard/web/__init__.py` (empty) and `maxguard/web/routes.py` with `router = APIRouter()`. `create_app()` already includes this router when the module exists. Read stores only through `request.app.state.state_store` and `request.app.state.event_store`; templates come from `maxguard/web/templates/` with `Jinja2Templates` (autoescaping is on by default for `.html`).

**Step 4.** `templates/base.html`: a `<nav>` (Alerts, Upload; Timeline and Devices come in AHM-06), the line **"Your data never leaves this computer."**, the Analyst/Home switch stored in a cookie `mg_mode`, `<script src="/static/htmx-2.0.11.min.js">` (never a CDN), and `/static/app.css`.

**Step 5.** `GET /` → `templates/queue.html`: the alert table from `state_store.list_alerts(status=..., severity=...)`; the two filters are `<select>`s with `hx-get="/" hx-target="#alerts" hx-select="#alerts"`. Severity is shown as text *and* color, never color alone.

**Step 6.** Live refresh: `static/app.js` opens `new EventSource("/api/stream")` and on each `alerts-changed` message calls `htmx.trigger("#alerts", "refresh")`; the table also has `hx-trigger="refresh, every 30s"` as a fallback.

**Step 7.** `GET /upload` → a form that posts the file to `/api/analyses` (`hx-post`, `hx-encoding="multipart/form-data"`) and then links to the queue.

**Step 8.** Tests `tests/unit/test_web.py` with `TestClient(create_app(tmp_path, explain=False))` and alerts saved through `StateStore.save_analysis()` from a fixture report: the pages return 200, the queue lists the Telnet alert, the filters work, a value with `<script>` in it is shown escaped, and no page loads anything from outside (no `http://` or `https://` in any `src` or `href` except links in text).

**Step 9.** Check the pages on a 375-pixel-wide window and with the keyboard only.

**Step 10.** Commit, push, and open the pull request:

```bash
git add -A
git status          # only this task's files: nothing from .venv/, data/ or lab/captures/
git commit -m "feat: dashboard layout, alert queue and upload page (AHM-02)"
git push -u origin HEAD
```

`HEAD` means "the branch I am on", so you do not have to retype its name. Open the repository on github.com: a yellow bar shows your branch with a **Compare & pull request** button. Click it, keep the title `feat: dashboard layout, alert queue and upload page (AHM-02)`, fill in the template (paste the real output of the commands above under **How I tested it**), write `Closes #<issue number>` (this task's issue), and pick **@JWinborne1** under **Reviewers**. Click **Create pull request**, then fix anything CI or the reviewer finds with new commits on the same branch.

#### How to test

`pytest tests/unit/test_web.py -q` passes. With `docker compose -f docker/compose.yaml -f docker/compose.dev.yaml up --build`, uploading `tests/pcaps/telnet.pcap` on http://127.0.0.1:8000/upload makes the Telnet alert appear in the queue without reloading the page.

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

**Due:** Week 4 (due Fri Nov 6) · **Milestone:** `W4 Full offline report` · **Needs first:** [AHM-02](#ahm-02-dashboard-layout-alert-queue-and-upload-page), [JON-02](jonattan.md#jon-02-ollama-client-one-evidence-citing-explanation-per-finding), [JON-04](jonattan.md#jon-04-home-mode-text-for-every-rule) · **Kind:** design

**Issue labels:** `type:task` `phase:alpha` `owner:ahmad` `area:ui` `critical-path`

> **Design task.** The code for this task was not written during planning. The steps give the files, the interfaces and the tests to write; the code is yours. Ask in GitHub Discussions when something is unclear, and update this section in your pull request with what you built.

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

**Step 2.** `GET /alerts/{finding_id}` → `templates/alert.html` from `state_store.get_alert(finding_id)` (404 page if missing).

**Step 3.** Analyst mode: an evidence table (`record_id`, log, uid, time) where each row has `id="ev-<record_id>"`; controls grouped by framework, showing the version next to each framework name; techniques with their tactic; then the AI sentences, each followed by small links `#ev-<record_id>` (the citation chips).

**Step 4.** If the stored report's `ai.status` is `unavailable`, show a clear banner with `ai.reason` (for example "model 'qwen3:4b' not found: run ollama pull qwen3:4b").

**Step 5.** Home mode (cookie `mg_mode=home`): the headline and action from `maxguard.ai.load_home_text()[rule_id]`, the severity as words ("High: fix this week"), and no IDs or framework names.

**Step 6.** Status and assignee: a small form that sends `hx-patch` to an HTML endpoint `/alerts/{finding_id}/status`, which calls `state_store.update_alert(finding_id, actor=<name from the mg_actor cookie>, at=time.time(), status=..., assignee=...)` and returns the updated fragment. The page asks for a display name once and stores it in `mg_actor`.

**Step 7.** AI text and everything from traffic is plain text in the templates: never `|safe`.

**Step 8.** Tests in `tests/unit/test_web.py`: both modes render, the citation links point to existing evidence rows, a status change is saved and appears in `list_audit()`, and the banner shows when the AI was unavailable.

**Step 9.** Commit, push, and open the pull request:

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

**Due:** Spring S1-S4 (due Fri Feb 12, 2027) · **Milestone:** `S1-S4 Live sensor` · **Needs first:** [AHM-03](#ahm-03-alert-detail-page-with-analyst-and-home-modes), [JAK-08](jakub.md#jak-08-device-attribution-which-device-is-behind-each-ip-address), [JAI-07](jaiden.md#jai-07-the-api-uploads-alerts-events-live-updates-sensor-ingest) · **Kind:** design

**Issue labels:** `type:task` `phase:spring` `owner:ahmad` `area:ui`

> **Design task.** The code for this task was not written during planning. The steps give the files, the interfaces and the tests to write; the code is yours. Ask in GitHub Discussions when something is unclear, and update this section in your pull request with what you built.

#### Goal

Add `/timeline?ip=` (everything one address did, in time order, with the ATT&CK techniques of findings that involve it) and `/assets` (the device inventory with MAC addresses and names from device attribution).

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

**Step 2.** `GET /timeline?ip=<address>`: validate the address with `ipaddress.ip_address` (400 if invalid); events from `event_store.query(ip=..., since=..., until=...)` (default the last 24 hours, with a selector up to 7 days); each row shows time, kind, summary, and a link to the alert if a finding cites that event.

**Step 3.** `GET /assets`: the inventory of the latest analysis joined with the device table (MAC, host name, DNS names); each IP links to its timeline.

**Step 4.** Tests in `tests/unit/test_web.py` with events written through `EventStore.write()`.

**Step 5.** Commit, push, and open the pull request:

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
    undo = [c.replace(" -D ", " -I ") for c in rules["iptables"]["undo"]]
    assert undo == rules["iptables"]["block"]  # the same rule, deleted instead of inserted


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
......................................                                                       [100%]
38 passed in 0.78s
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
- Times are passed in by the caller (the API reads the clock, this module never does).

Proposals live in their own table in state.db, created here with
CREATE TABLE IF NOT EXISTS, so storage/state.py does not change.
"""

from __future__ import annotations

import ipaddress
import json
import sqlite3
from collections.abc import Iterator, Sequence
from contextlib import contextmanager

from maxguard.response.enforcers.base import Enforcer
from maxguard.response.generate import check_direction, parse_ip, rules_for
from maxguard.storage.state import StateStore, insert_audit

STATES = ("proposed", "previewed", "approved", "applied", "reverted", "rejected")

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
        with self._connect() as conn:  # the proposal and its audit row: one transaction
            cur = conn.execute(
                "INSERT INTO response_proposals (ip, direction, reason, finding_id, state, "
                "created_by, created_at, updated_at) VALUES (?, ?, ?, ?, 'proposed', ?, ?, ?)",
                (address, direction, reason, finding_id, actor, at, at))
            proposal_id = cur.lastrowid
            audit(conn, actor, "proposed", proposal_id, at,
                  {"ip": address, "direction": direction, "finding_id": finding_id})
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
        commands by hand and says so. If an enforcer fails, the state stays 'approved'."""
        proposal = self.require_state(proposal_id, "approved")
        method = "enforcer" if enforcers else "manual"
        try:
            for enforcer in enforcers:
                enforcer.add(proposal["ip"])
                enforcer.apply()
        except Exception as err:
            self.audit_only(actor, "apply_failed", proposal_id, at, {"error": str(err)})
            raise
        self.move(proposal_id, ("approved",), "applied", at, actor,
                  {"ip": proposal["ip"], "method": method}, method=method)
        return self.get(proposal_id)

    def revert(self, proposal_id: int, *, actor: str, at: float,
               enforcers: Sequence[Enforcer] = ()) -> dict:
        """Undo the block the same way it was applied."""
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
                self.audit_only(actor, "revert_failed", proposal_id, at, {"error": str(err)})
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
allowed now, 502 the firewall refused or could not be reached.
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

`create_app()` (JAI-07) includes this router automatically now that the module exists. It is part of the dashboard's app on `127.0.0.1` only, never the ingest-only app that sensors reach. Errors: 400 bad input or a wrong typed IP, 404 no such proposal, 409 a step that is not allowed now, 502 the firewall refused or could not be reached.

**Step 5.** Create the tests `tests/unit/test_response_approvals.py`:

```python
"""Tests for maxguard.response.approvals (Ahmad, AHM-08)."""

import sqlite3

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
        self.fail = fail

    def add(self, ip: str) -> None:
        if self.fail:
            raise EnforcerError("firewall said no")
        self.blocked.add(ip)

    def remove(self, ip: str) -> None:
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
```

Run them:

```bash
pytest tests/unit/test_response_approvals.py tests/unit/test_opnsense.py tests/unit/test_response_routes.py -q
```

Expected output:

```text
.....................................................                                        [100%]
53 passed in 3.40s
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
{"analysis_id":"4423386c532f1b46","findings":1}
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
2. **Firewall > Rules > WAN**: a *Block* rule with source `maxguard_block_in`. **Firewall > Rules > LAN**: a *Block* rule with source `maxguard_block_in` (a device on your own network) and one with destination `maxguard_block_out`. Apply.
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

5. Repeat the walk-through: `apply` now adds the address to the alias (check **Firewall > Diagnostics > Aliases**), and `revert` removes it. Without `MAXGUARD_OFFLINE_ALLOW`, apply answers 502 with the hint to add the firewall there.

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
