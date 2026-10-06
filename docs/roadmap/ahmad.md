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
| [AHM-07](#ahm-07-response-block-proposals-generated-rules-and-preview-before-you-block) | S8 | Response: block proposals, generated rules, and preview before you block | [JAI-06](jaiden.md#jai-06-storage-alerts-in-sqlite-events-in-hourly-parquet-files), [JAI-07](jaiden.md#jai-07-the-api-uploads-alerts-events-live-updates-sensor-ingest) | design |
| [AHM-08](#ahm-08-response-approvals-audit-revert-and-the-opnsense-connector) | S8 | Response: approvals, audit, revert, and the OPNsense connector | [AHM-07](#ahm-07-response-block-proposals-generated-rules-and-preview-before-you-block), [JON-03](jonattan.md#jon-03-offline-guard-make-accidental-network-access-fail-loudly) | design |
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

**Step 3.** **Security reports.** **Settings → Security → Private vulnerability reporting**: **Enable**, so outsiders can report a problem without a public issue.

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

**Due:** Spring S5-S8 (due Fri Mar 12, 2027) · **Milestone:** `S5-S8 Respond` · **Needs first:** [JAI-06](jaiden.md#jai-06-storage-alerts-in-sqlite-events-in-hourly-parquet-files), [JAI-07](jaiden.md#jai-07-the-api-uploads-alerts-events-live-updates-sensor-ingest) · **Kind:** design

**Issue labels:** `type:task` `phase:spring` `owner:ahmad` `area:response`

> **Design task.** The code for this task was not written during planning. The steps give the files, the interfaces and the tests to write; the code is yours. Ask in GitHub Discussions when something is unclear, and update this section in your pull request with what you built.

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

**Step 2.** `maxguard/response/generate.py`: `rules_for(ip: str, direction: str) -> dict` parses the address with `ipaddress.ip_address` (anything else raises `ValueError`, so nothing else can reach a command), refuses loopback, multicast, unspecified and link-local addresses, and returns nftables commands that add the address to a named set `maxguard_block` plus the matching delete command, iptables commands with their undo, the OPNsense alias steps, and plain steps for a home router.

**Step 3.** Check the nftables syntax for real with `nft -c -f <file>` (find a container image that has `nft`, or a Linux machine) and record the output in the pull request.

**Step 4.** `maxguard/response/preview.py`: `preview(ip, direction, event_store, *, window_end)` looks back 7 days from `window_end` (passed in, never the clock) and returns the number of connections, the internal devices affected, services and ports, first and last seen, and up to 10 sample events in a fixed order.

**Step 5.** Tests `tests/unit/test_response_generate.py` and `test_response_preview.py`, including a hostile input such as `"1.2.3.4; rm -rf /"`.

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

**Due:** Spring S5-S8 (due Fri Mar 12, 2027) · **Milestone:** `S5-S8 Respond` · **Needs first:** [AHM-07](#ahm-07-response-block-proposals-generated-rules-and-preview-before-you-block), [JON-03](jonattan.md#jon-03-offline-guard-make-accidental-network-access-fail-loudly) · **Kind:** design

**Issue labels:** `type:task` `phase:spring` `owner:ahmad` `area:response`

> **Design task.** The code for this task was not written during planning. The steps give the files, the interfaces and the tests to write; the code is yours. Ask in GitHub Discussions when something is unclear, and update this section in your pull request with what you built.

#### Goal

Add the approval workflow (propose → preview → approve with the IP typed again → applied → reverted, every step audited) and the first `Enforcer`, which applies an approved block on an OPNsense firewall through its API.

#### Prerequisites

AHM-07 is merged. You need an OPNsense test firewall in a VM, never a real one.

#### Steps

**Step 1.** Update `main` and create your branch for this task (one branch per task):

```bash
cd ~/projects/maxguard
source .venv/bin/activate
git checkout main && git pull
git checkout -b ahmad/response-approvals
```

If `source .venv/bin/activate` fails, you have not made the virtual environment yet: do Week 0 section 0.11 first.

**Step 2.** `maxguard/response/approvals.py`: proposals stored in `state.db` (create the tables with `CREATE TABLE IF NOT EXISTS` in this module; ask Jaiden before changing `state.py`); each state change calls `StateStore.add_audit`.

**Step 3.** `maxguard/response/routes.py`: `APIRouter` under `/api/response`: `POST /proposals`, `GET /proposals`, `POST /proposals/{id}/preview`, `POST /proposals/{id}/approve` (needs `actor` and `confirm_ip` equal to the proposal's IP), `POST /proposals/{id}/revert`.

**Step 4.** `maxguard/response/enforcers/base.py` (the `Enforcer` protocol: `add(ip)`, `remove(ip)`, `apply()`) and `enforcers/opnsense.py`: look up the alias endpoints (`/api/firewall/alias_util/add/<alias>`, `.../delete/<alias>`, and `/api/firewall/alias/reconfigure`) in the OPNsense documentation and cite it; HTTP basic auth with an API key and secret from a file in the data folder; TLS verification on. Document adding the firewall to `MAXGUARD_OFFLINE_ALLOW`.

**Step 5.** Tests with a fake OPNsense server (`http.server` on `127.0.0.1`) and TestClient: approval without the typed IP fails, every step is audited, revert removes the address.

**Step 6.** Commit, push, and open the pull request:

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
