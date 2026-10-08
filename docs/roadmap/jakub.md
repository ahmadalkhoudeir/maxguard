# Jakub: Protocol Coverage Engineer

**Jakub Kania** (@SXafir-byte) · Module: Sensor · Reviewer for your pull requests: @flau0306 (Fiona) · Ask first when stuck: Fiona

This is your part of the MaxGuard v2.0 roadmap. Read [the roadmap overview](README.md) once, then work top to bottom: Week 0 first, then your tasks in order. Each task's ID is also the start of its GitHub issue's title.

## Your tasks

| Task | Due | Title | Needs first | Kind |
|---|---|---|---|---|
| [JAK-00](#week-0--onboarding-due-friday-october-9-2026) | W0 | Week 0 onboarding (Jakub) | — | process |
| [JAK-01](#jak-01-maxguards-zeek-scripts-cleartext-sessions-and-asset-tracking) | W1 | MaxGuard's Zeek scripts: cleartext sessions and asset tracking | [JAI-01](jaiden.md#jai-01-restructure-the-repository-add-packaging-and-ci), [KAR-01](karthik.md#kar-01-traffic-lab-and-the-14-test-captures) | code, tested |
| [JAK-02](#jak-02-suricata-configuration-community-id-and-ja4) | W1 | Suricata configuration: Community ID and JA4 | [KAR-01](karthik.md#kar-01-traffic-lab-and-the-14-test-captures) | code, tested |
| [JAK-03](#jak-03-cleartext-and-rdp-rules-the-rule-set-is-complete) | W1 | Cleartext and RDP rules (the rule set is complete) | [FIO-02](fiona.md#fio-02-tls-and-certificate-rules), [JAK-01](#jak-01-maxguards-zeek-scripts-cleartext-sessions-and-asset-tracking), [KAR-02](karthik.md#kar-02-test-fixtures-zeek-and-suricata-output-for-every-capture) | code, tested |
| [JAK-04](#jak-04-asset-inventory) | W1 | Asset inventory | [JAK-03](#jak-03-cleartext-and-rdp-rules-the-rule-set-is-complete), [KAR-02](karthik.md#kar-02-test-fixtures-zeek-and-suricata-output-for-every-capture) | code, tested |
| [JAK-05](#jak-05-suricata-in-the-pipeline) | W4 | Suricata in the pipeline | [JAK-02](#jak-02-suricata-configuration-community-id-and-ja4), [FIO-01](fiona.md#fio-01-zeek-runner-and-the-two-input-adapters), [JAI-05](jaiden.md#jai-05-the-pipeline-one-function-from-input-to-report), [JAI-07](jaiden.md#jai-07-the-api-uploads-alerts-events-live-updates-sensor-ingest) | code, tested |
| [JAK-06](#jak-06-build-the-reference-lab-and-prove-the-mirror-works) | W8 | Build the reference lab and prove the mirror works | [JAK-02](#jak-02-suricata-configuration-community-id-and-ja4) | process |
| [JAK-08](#jak-08-device-attribution-which-device-is-behind-each-ip-address) | S4 | Device attribution: which device is behind each IP address | [JAK-04](#jak-04-asset-inventory), [KAR-02](karthik.md#kar-02-test-fixtures-zeek-and-suricata-output-for-every-capture) | code, tested |
| [JAK-07](#jak-07-live-sensor-capture-rotation-and-shipping-to-the-console) | S4 | Live sensor: capture, rotation, and shipping to the console | [JAK-06](#jak-06-build-the-reference-lab-and-prove-the-mirror-works), [JAI-07](jaiden.md#jai-07-the-api-uploads-alerts-events-live-updates-sensor-ingest), [JAK-08](#jak-08-device-attribution-which-device-is-behind-each-ip-address) | code, tested |
| [JAK-09](#jak-09-ja4-watchlist-rule) | S8 | JA4 watchlist rule | [JAK-05](#jak-05-suricata-in-the-pipeline) | code, tested |
| [JAK-10](#jak-10-netflow-and-ipfix-input) | S11 | NetFlow and IPFIX input | [JAI-07](jaiden.md#jai-07-the-api-uploads-alerts-events-live-updates-sensor-ingest), [JAI-03](jaiden.md#jai-03-common-event-schema-the-normalizer-and-record-lookup), [AHM-06](ahmad.md#ahm-06-ip-timeline-and-device-inventory-pages) | code, tested |
| [JAK-11](#jak-11-host-agent-for-one-computer) | S12 | Host agent for one computer | [JAI-07](jaiden.md#jai-07-the-api-uploads-alerts-events-live-updates-sensor-ingest) | code, tested |

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
git config --global user.name "Jakub Kania"
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
git checkout -b jakub/week0-team-row
```

2. **Make the change.** Run `code .`, open `docs/TEAM.md`, and add this line at
   the end (keep the `|` characters):

```markdown
| Jakub Kania | Protocol Coverage Engineer | SXafir-byte | Sensor |
```

3. **Commit** (the message says *what changed*, starting with a type such as
   `docs:`, `feat:`, `fix:` or `test:`; see `docs/CONTRIBUTING.md`):

```bash
git add docs/TEAM.md
git commit -m "docs: add Jakub to TEAM.md"
```

4. **Push** your branch to GitHub:

```bash
git push -u origin jakub/week0-team-row
```

Expected (from the planning simulation; the first lines differ on GitHub):

```text
 * [new branch]      jakub/week0-team-row -> jakub/week0-team-row
branch 'jakub/week0-team-row' set up to track 'origin/jakub/week0-team-row'.
```

5. **Open the pull request** and ask for a review:

```bash
gh pr create --base main --title "docs: add Jakub to TEAM.md" --body "Week 0 onboarding." --reviewer flau0306
```

`gh` prints the pull request's web address. (You can also click the link Git
printed after the push and press **Create pull request**.)

6. **After approval**, click **Squash and merge** on GitHub, then update your laptop:

```bash
git checkout main && git pull
git branch -d jakub/week0-team-row
```

**If GitHub says "This branch has conflicts":** eight people are adding a line
to the same file this week, so this is expected. Bring `main` into your branch
and keep both lines:

```bash
git checkout main && git pull
git checkout jakub/week0-team-row
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
   `JAK-01: pytest cannot import maxguard`). In the body, paste the
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

### JAK-01: MaxGuard's Zeek scripts: cleartext sessions and asset tracking

**Due:** Week 1 (due Fri Oct 16) · **Milestone:** `W1 Building blocks` · **Needs first:** [JAI-01](jaiden.md#jai-01-restructure-the-repository-add-packaging-and-ci), [KAR-01](karthik.md#kar-01-traffic-lab-and-the-14-test-captures) · **Kind:** code, tested

**Issue labels:** `type:task` `phase:alpha` `owner:jakub` `area:engine` `critical-path`

#### Goal

Write the two Zeek scripts MaxGuard loads on every run. `cleartext.zeek` writes `maxguard_cleartext.log`, one line per real Telnet, POP3 or IMAP session that was not upgraded to TLS. `inventory.zeek` turns on Zeek's host, service and software tracking for every address, which the asset inventory (JAK-04) reads. `site.zeek` replaces Zeek's own `local` policy, without the scripts that make DNS lookups.

#### Prerequisites

JAI-01 and KAR-01 (the lab captures) are merged.

#### Steps

**Step 1.** Update `main` and create your branch for this task (one branch per task):

```bash
cd ~/projects/maxguard
source .venv/bin/activate
git checkout main && git pull
git checkout -b jakub/zeek-scripts
```

If `source .venv/bin/activate` fails, you have not made the virtual environment yet: do Week 0 section 0.11 first.

**Step 2.** Create `maxguard/zeek/scripts/cleartext.zeek`:

```zeek
module MaxGuard;

export {
    redef enum Log::ID += { LOG };

    type Info: record {
        ts:      time    &log;
        uid:     string  &log;
        id:      conn_id &log;
        service: string  &log &optional;
        proto:   string  &log;
    };

    const cleartext_ports: table[port] of string = {
        [23/tcp]  = "telnet",
        [110/tcp] = "pop3",
        [143/tcp] = "imap",
    } &redef;
}

event zeek_init()
    {
    Log::create_stream(MaxGuard::LOG, [$columns=Info, $path="maxguard_cleartext"]);
    }

event connection_state_remove(c: connection)
    {
    if ( c$id$resp_p !in cleartext_ports )
        return;
    if ( c$resp$size == 0 )          # no data from server: a scan, not a session
        return;
    local svc = "";
    if ( c?$service && |c$service| > 0 )
        svc = join_string_set(c$service, ",");
    # c$service holds upper-case analyzer names ("SSL", "IMAP"); conn.log only
    # looks lower-case because Zeek lowers it when writing. Compare lower-case,
    # or a STARTTLS-upgraded session would be reported as cleartext.
    if ( /ssl|tls/ in to_lower(svc) )  # STARTTLS upgraded: encrypted, skip
        return;
    Log::write(MaxGuard::LOG, [$ts=network_time(), $uid=c$uid, $id=c$id,
                               $service=svc, $proto=cleartext_ports[c$id$resp_p]]);
    }
```

Two details matter. `c$resp$size == 0` skips connections where the server never sent anything (a port scan is not a session). And Zeek stores analyzer names in upper case (`SSL`), so the STARTTLS check compares lower-case text; without `to_lower` an IMAP session upgraded to TLS would be reported as cleartext.

**Step 3.** Create `maxguard/zeek/scripts/inventory.zeek`:

```zeek
@load protocols/conn/known-hosts
@load protocols/conn/known-services
@load frameworks/software/version-changes

redef Known::host_tracking = ALL_HOSTS;
redef Known::service_tracking = ALL_HOSTS;
redef Software::asset_tracking = ALL_HOSTS;
```

**Step 4.** Create `maxguard/zeek/site.zeek`, MaxGuard's site policy. It is outside `scripts/` on purpose: everything in `scripts/` is loaded on every run, and this file replaces the `local` argument instead:

```zeek
##! MaxGuard's Zeek site policy (Jakub, JAK-01). MaxGuard loads this file
##! instead of Zeek's own "local" policy, on capture files and on the live sensor.
##!
##! It is Zeek 9.0.0's share/zeek/site/local.zeek without the three scripts that
##! send network traffic of their own. MaxGuard never contacts anything
##! (CLAUDE.md rule 1) and a sensor only listens (rule 5):
##!
##! - frameworks/files/detect-MHR asks Team Cymru's Malware Hash Registry, with a
##!   DNS query, about the SHA-1 of every executable, PDF, video ... seen on the
##!   network. That also tells an outside service what people downloaded.
##! - protocols/ssh/interesting-hostnames makes a reverse DNS lookup of both ends
##!   of every successful SSH login.
##! - frameworks/notice/extend-email/hostnames makes reverse DNS lookups for
##!   notice e-mails.
##!
##! Zeek runs as its own program, so the Python offline guard (maxguard/offline.py)
##! cannot stop it: leaving these scripts out is the fix. Everything else is the
##! same as local.zeek, so the logs MaxGuard reads do not change.

# Kept as in local.zeek: it only salts file IDs (fuid), and a different value
# would change every file ID in the test fixtures.
redef digest_salt = "Please change this value.";

@load misc/loaded-scripts
@load misc/capture-loss
@load misc/stats

@load frameworks/software/vulnerable
@load frameworks/software/version-changes
@load-sigs frameworks/signatures/detect-windows-shells

@load protocols/ftp/software
@load protocols/smtp/software
@load protocols/ssh/software
@load protocols/http/software

@load protocols/dns/detect-external-names
@load protocols/ftp/detect

@load protocols/conn/known-hosts
@load protocols/conn/known-services
@load protocols/ssl/known-certs

@load protocols/ssl/validate-certs
@load protocols/ssl/log-hostcerts-only

@load protocols/ssh/geo-data
@load protocols/ssh/detect-bruteforcing

@load protocols/http/detect-sql-injection

@load frameworks/files/hash-all-files
```

Zeek's own `local` policy is fine on an analyst's laptop that is meant to be online, but MaxGuard must never contact anything (CLAUDE.md rule 1), and Zeek runs as its own program, so MaxGuard's Python offline guard cannot stop its DNS queries. This was found while building the live sensor in planning.

**Step 5.** Run Zeek on the Telnet capture with your script (the Zeek image has everything; `--network none` proves it needs no network):

```bash
docker run --rm --network none -v "$PWD:/src:ro" -w /tmp zeek/zeek:9.0.0 sh -c "zeek -D -C -r /src/tests/pcaps/telnet.pcap /src/maxguard/zeek/site.zeek LogAscii::use_json=T /src/maxguard/zeek/scripts/cleartext.zeek && cat maxguard_cleartext.log"
```

Expected output:

```text
{"ts":1791250285.789302,"uid":"CJKFoj4bpHEhTeaRoj","id.orig_h":"172.18.0.3","id.orig_p":55398,"id.resp_h":"172.18.0.2","id.resp_p":23,"service":"","proto":"telnet"}
```

**Step 6.** Run it on the clean TLS 1.3 capture: there must be **no** cleartext log, and the inventory logs must appear:

```bash
docker run --rm --network none -v "$PWD:/src:ro" -w /tmp zeek/zeek:9.0.0 sh -c "zeek -D -C -r /src/tests/pcaps/clean_tls13.pcap /src/maxguard/zeek/site.zeek LogAscii::use_json=T /src/maxguard/zeek/scripts/*.zeek && ls *.log"
```

Expected output:

```text
capture_loss.log
conn.log
known_hosts.log
known_services.log
loaded_scripts.log
packet_filter.log
ssl.log
stats.log
```

**Step 7.** Compare the scripts that `site.zeek` and Zeek's `local` load: `loaded_scripts.log` names every script, and the first count must be 0:

```bash
docker run --rm --network none -v "$PWD:/src:ro" -w /tmp zeek/zeek:9.0.0 sh -c "zeek -D -C -r /src/tests/pcaps/plain_http.pcap /src/maxguard/zeek/site.zeek; grep -c 'detect-MHR\|interesting-hostnames\|extend-email' loaded_scripts.log; rm -f *.log; zeek -D -C -r /src/tests/pcaps/plain_http.pcap local; grep -c 'detect-MHR\|interesting-hostnames\|extend-email' loaded_scripts.log"
```

Expected output:

```text
0
3
```

**Step 8.** Commit, push, and open the pull request:

```bash
git add -A
git status          # only this task's files: nothing from .venv/, data/ or lab/captures/
git commit -m "feat: Zeek scripts for cleartext sessions and asset tracking (JAK-01)"
git push -u origin HEAD
```

`HEAD` means "the branch I am on", so you do not have to retype its name. Open the repository on github.com: a yellow bar shows your branch with a **Compare & pull request** button. Click it, keep the title `feat: Zeek scripts for cleartext sessions and asset tracking (JAK-01)`, fill in the template (paste the real output of the commands above under **How I tested it**), write `Closes #<issue number>` (this task's issue), and pick **@flau0306** under **Reviewers**. Click **Create pull request**, then fix anything CI or the reviewer finds with new commits on the same branch.

#### How to test

The Telnet run prints one JSON line with `"proto":"telnet"`. The clean run lists `known_hosts.log` and `known_services.log` but no `maxguard_cleartext.log`. The lookups check prints `0` for `site.zeek` and `3` for `local`. KAR-02 then bakes both scripts into the test fixtures.

#### What you just did and why

Zeek already logs FTP and HTTP in detail, but it has no Telnet log, and its POP3/IMAP support does not say clearly whether a session stayed unencrypted. A small script that watches the port and the analyzers gives one clear line per cleartext session, with the connection `uid` that links it to `conn.log`. By default Zeek tracks known hosts only inside its `Site::local_nets` list, which is empty in a container, so without `ALL_HOSTS` the inventory would always be empty. And a sensor that quietly asks an outside DNS service about the files people download would break the promise MaxGuard makes in every report: your data never leaves this computer.

#### Pull request checklist

- [ ] `ruff check .` prints `All checks passed!`
- [ ] `pytest -m "not integration" -q` passes on your laptop
- [ ] The pull request title has the form `type: summary (TASK-ID)` and the body says `Closes #<issue number>`
- [ ] No secrets, passwords, email addresses, personal data, or captures from a real network (CLAUDE.md rule 6)
- [ ] Any new dependency has a row in `docs/DEPENDENCIES.md` with its license
- [ ] CI is green and your reviewer approved
- [ ] Both commands above give the expected output

### JAK-02: Suricata configuration: Community ID and JA4

**Due:** Week 1 (due Fri Oct 16) · **Milestone:** `W1 Building blocks` · **Needs first:** [KAR-01](karthik.md#kar-01-traffic-lab-and-the-14-test-captures) · **Kind:** code, tested

**Issue labels:** `type:task` `phase:alpha` `owner:jakub` `area:engine` `critical-path`

#### Goal

Add MaxGuard's Suricata settings for reading captures: `eve.json` with flow, alert, DNS, HTTP, TLS (with the JA4 client fingerprint) and DHCP events, and the same Community ID that Zeek writes. Add the (empty) MaxGuard rules file that signed intel bundles fill later.

#### Prerequisites

KAR-01 (the lab captures) is merged.

#### Steps

**Step 1.** Update `main` and create your branch for this task (one branch per task):

```bash
cd ~/projects/maxguard
source .venv/bin/activate
git checkout main && git pull
git checkout -b jakub/suricata-config
```

If `source .venv/bin/activate` fails, you have not made the virtual environment yet: do Week 0 section 0.11 first.

**Step 2.** Create `maxguard/suricata/maxguard-suricata.yaml`:

```yaml
%YAML 1.1
---
# MaxGuard's Suricata settings for reading capture files (pcap mode).
# Only the parts MaxGuard needs: eve.json with flows, alerts, DNS, HTTP, TLS
# (with JA4, BSD-3-Clause), and DHCP. Suricata fills in defaults for the rest.
vars:
  address-groups:
    HOME_NET: "[10.0.0.0/8,172.16.0.0/12,192.168.0.0/16,fc00::/7]"
    EXTERNAL_NET: "!$HOME_NET"
  port-groups:
    HTTP_PORTS: "80"
    SHELLCODE_PORTS: "!80"
    ORACLE_PORTS: 1521
    SSH_PORTS: 22
    DNP3_PORTS: 20000
    MODBUS_PORTS: 502
    FILE_DATA_PORTS: "[$HTTP_PORTS,110,143]"
    FTP_PORTS: 21
    GENEVE_PORTS: 6081
    VXLAN_PORTS: 4789
    TEREDO_PORTS: 3544

default-log-dir: /var/log/suricata/

outputs:
  - eve-log:
      enabled: yes
      filetype: regular
      filename: eve.json
      community-id: yes
      community-id-seed: 0
      types:
        - alert
        - dns
        - http:
            extended: yes
        - tls:
            extended: yes
            ja4: on
        - dhcp:
            enabled: yes
        - flow

app-layer:
  protocols:
    tls:
      enabled: yes
      detection-ports:
        dp: 443
      ja4-fingerprints: yes
    http:
      enabled: yes
    dns:
      tcp:
        enabled: yes
      udp:
        enabled: yes
    dhcp:
      enabled: yes

logging:
  default-log-level: notice
  outputs:
    - console:
        enabled: yes
```

Suricata fills in its defaults for everything not listed. JA4 needs two switches: `app-layer.protocols.tls.ja4-fingerprints: yes` computes it, and `ja4: on` under the `tls` event type writes it.

**Step 3.** Create an **empty** file `maxguard/suricata/__init__.py` (it makes the folder part of the Python package, so `pip install` ships the YAML file), then `maxguard/suricata/rules/maxguard.rules`:

```text
# MaxGuard Suricata rules. Empty in v2.0-alpha; signed intel bundles add rules later.
```

**Step 4.** Run Suricata 7.0.10 (the version in the engine image) on the weak-TLS capture and pull out the two fields MaxGuard needs:

```bash
docker run --rm --network none -v "$PWD:/src:ro" --entrypoint sh jasonish/suricata:7.0.10 -c "suricata -c /src/maxguard/suricata/maxguard-suricata.yaml -r /src/tests/pcaps/tls_weak_version.pcap -l /tmp -k none --runmode single -S /src/maxguard/suricata/rules/maxguard.rules > /dev/null && grep '\"event_type\":\"tls\"' /tmp/eve.json | grep -o '\"community_id\":\"[^\"]*\"\|\"ja4\":\"[^\"]*\"'"
```

Expected output:

```text
"community_id":"1:pRvdZyOxcG+AIDBGMFce8LVpI/I="
"ja4":"t10d230600_44099cda8a52_242d16716555"
```

**Step 5.** Compare with Zeek's Community ID for the same connection (it must be identical):

```bash
docker run --rm --network none -v "$PWD:/src:ro" -w /tmp zeek/zeek:9.0.0 sh -c "zeek -D -C -r /src/tests/pcaps/tls_weak_version.pcap LogAscii::use_json=T policy/protocols/conn/community-id-logging && grep -o '\"community_id\":\"[^\"]*\"' conn.log"
```

Expected output:

```text
"community_id":"1:pRvdZyOxcG+AIDBGMFce8LVpI/I="
```

**Step 6.** Commit, push, and open the pull request:

```bash
git add -A
git status          # only this task's files: nothing from .venv/, data/ or lab/captures/
git commit -m "feat: Suricata config with Community ID and JA4 (JAK-02)"
git push -u origin HEAD
```

`HEAD` means "the branch I am on", so you do not have to retype its name. Open the repository on github.com: a yellow bar shows your branch with a **Compare & pull request** button. Click it, keep the title `feat: Suricata config with Community ID and JA4 (JAK-02)`, fill in the template (paste the real output of the commands above under **How I tested it**), write `Closes #<issue number>` (this task's issue), and pick **@flau0306** under **Reviewers**. Click **Create pull request**, then fix anything CI or the reviewer finds with new commits on the same branch.

#### How to test

Suricata prints a `community_id` and a `ja4` value starting with `t10` (TLS 1.0, the weak version in this capture); Zeek prints the same `community_id`.

#### What you just did and why

Zeek and Suricata see the same traffic but describe it differently. The Community ID is a hash of the connection's addresses, ports and protocol that both tools compute the same way, so the normalizer (JAI-03) can show a Zeek event and a Suricata event about one connection side by side. JA4 identifies the TLS client software from its first message, even when everything after it is encrypted; MaxGuard uses only JA4 from the JA4+ family because only JA4 is BSD-licensed (CLAUDE.md rule 7). Suricata's own `flow_id` is random on every run, which is why MaxGuard never uses it.

#### Pull request checklist

- [ ] `ruff check .` prints `All checks passed!`
- [ ] `pytest -m "not integration" -q` passes on your laptop
- [ ] The pull request title has the form `type: summary (TASK-ID)` and the body says `Closes #<issue number>`
- [ ] No secrets, passwords, email addresses, personal data, or captures from a real network (CLAUDE.md rule 6)
- [ ] Any new dependency has a row in `docs/DEPENDENCIES.md` with its license
- [ ] CI is green and your reviewer approved
- [ ] Both commands print the same Community ID

### JAK-03: Cleartext and RDP rules (the rule set is complete)

**Due:** Week 1 (due Fri Oct 16) · **Milestone:** `W1 Building blocks` · **Needs first:** [FIO-02](fiona.md#fio-02-tls-and-certificate-rules), [JAK-01](#jak-01-maxguards-zeek-scripts-cleartext-sessions-and-asset-tracking), [KAR-02](karthik.md#kar-02-test-fixtures-zeek-and-suricata-output-for-every-capture) · **Kind:** code, tested

**Issue labels:** `type:task` `phase:alpha` `owner:jakub` `area:engine` `critical-path`

#### Goal

Write the seven remaining Fall 2026 rules: FTP, Telnet, HTTP, HTTP on port 8080, POP3 and IMAP in cleartext, and RDP with only "standard RDP security". With them, all 13 rules are registered and every lab capture triggers exactly its own rule.

#### Prerequisites

FIO-02 (it creates the rule package layout), JAK-01 and KAR-02 are merged.

#### Steps

**Step 1.** Update `main` and create your branch for this task (one branch per task):

```bash
cd ~/projects/maxguard
source .venv/bin/activate
git checkout main && git pull
git checkout -b jakub/cleartext-rules
```

If `source .venv/bin/activate` fails, you have not made the virtual environment yet: do Week 0 section 0.11 first.

**Step 2.** Create `maxguard/rules/cleartext.py`:

```python
"""Cleartext protocol rules (Jakub). Field names checked against Zeek 9.0.0."""

from maxguard.adapters.base import read_log
from maxguard.ids import evidence
from maxguard.models import Finding
from maxguard.rules.base import rule


def _f(rec, rule_id, title, sev, proto, log, details=None):
    ts = float(rec["ts"])
    return Finding(rule_id=rule_id, title=title, severity=sev,
                   src_ip=rec["id.orig_h"], dst_ip=rec["id.resp_h"],
                   dst_port=int(rec["id.resp_p"]), protocol=proto,
                   first_seen=ts, last_seen=ts, details=details or {},
                   evidence=[evidence(log, rec)])


@rule("cleartext.ftp")
def ftp(d):
    return [_f(r, "cleartext.ftp", "FTP login and data sent unencrypted", "high",
               "ftp", "ftp.log", {"user": r.get("user"), "command": r.get("command")})
            for r in read_log(d, "ftp.log")]


@rule("cleartext.http")
def http(d):
    return [_f(r, "cleartext.http", "Unencrypted HTTP", "medium", "http", "http.log",
               {"host": r.get("host"), "uri": r.get("uri"), "basic_auth_user": r.get("username")})
            for r in read_log(d, "http.log") if int(r["id.resp_p"]) != 8080]


@rule("cleartext.http_alt")
def http_alt(d):
    return [_f(r, "cleartext.http_alt", "Unencrypted HTTP on port 8080", "medium",
               "http", "http.log", {"host": r.get("host")})
            for r in read_log(d, "http.log") if int(r["id.resp_p"]) == 8080]


def _from_script(proto, rule_id, title):
    def check(d):
        return [_f(r, rule_id, title, "high", proto, "maxguard_cleartext.log")
                for r in read_log(d, "maxguard_cleartext.log") if r["proto"] == proto]
    return check


rule("cleartext.telnet")(_from_script("telnet", "cleartext.telnet", "Telnet session in cleartext"))
rule("cleartext.pop3")(_from_script("pop3", "cleartext.pop3", "POP3 mail retrieval in cleartext"))
rule("cleartext.imap")(_from_script("imap", "cleartext.imap", "IMAP mail access in cleartext"))


@rule("rdp.standard_security")
def rdp(d):
    return [_f(r, "rdp.standard_security", "RDP using legacy Standard RDP Security", "high",
               "rdp", "rdp.log", {"security_protocol": r.get("security_protocol")})
            for r in read_log(d, "rdp.log") if r.get("security_protocol") == "RDP"]
```

**Step 3.** Register it: replace the contents of `maxguard/rules/__init__.py` with

```python
"""Importing this package registers every rule module with the registry."""

from . import certs, cleartext, tls  # noqa: F401
```

**Step 4.** Create the rule tests `tests/unit/test_rules_cleartext.py`:

```python
"""Cleartext and RDP rule tests (Jakub, JAK-02): positive and negative for each rule.

RDP has no lab capture: tests/fixtures/zeek/_handmade/rdp/ has a synthetic
capture and its real Zeek output (one "RDP" and one "HYBRID" connection).
"""

import json
import re
from pathlib import Path

import pytest

import maxguard.rules  # noqa: F401  (importing registers every rule)
from maxguard.adapters.base import read_log
from maxguard.ids import record_id
from maxguard.rules.base import RULES, run_all

REPO = Path(__file__).resolve().parents[2]
FIXTURES = REPO / "tests" / "fixtures" / "zeek"
RDP_DIR = FIXTURES / "_handmade" / "rdp"

EXPECTED = {
    "ftp": "cleartext.ftp",
    "telnet": "cleartext.telnet",
    "plain_http": "cleartext.http",
    "plain_http_alt": "cleartext.http_alt",
    "pop3": "cleartext.pop3",
    "imap": "cleartext.imap",
}

NEAR_MISS = {
    "cleartext.ftp": "plain_http",  # cleartext, but not FTP
    "cleartext.telnet": "pop3",  # same maxguard_cleartext.log, other protocol
    "cleartext.pop3": "imap",
    "cleartext.imap": "telnet",
    "cleartext.http": "plain_http_alt",  # HTTP, but on port 8080
    "cleartext.http_alt": "plain_http",  # HTTP, but on port 80
}

CLEARTEXT_RULES = {*EXPECTED.values(), "rdp.standard_security"}


def write_log(log_dir: Path, log_name: str, records: list[dict]) -> Path:
    """Write records as a Zeek JSON log (one object per line) and return the folder."""
    (log_dir / log_name).write_text("".join(json.dumps(rec) + "\n" for rec in records))
    return log_dir


def rdp_record(security_protocol: str) -> dict:
    """The rdp.log record from the hand-made capture with this security_protocol."""
    for rec in read_log(RDP_DIR, "rdp.log"):
        if rec["security_protocol"] == security_protocol:
            return rec
    raise AssertionError(f"no {security_protocol} record in {RDP_DIR / 'rdp.log'}")


def test_the_seven_cleartext_and_rdp_rules_are_registered():
    assert CLEARTEXT_RULES <= set(RULES)


@pytest.mark.parametrize(("capture", "rule_id"), sorted(EXPECTED.items()))
def test_rule_fires_on_its_capture(capture, rule_id):
    findings = RULES[rule_id](FIXTURES / capture)

    assert len(findings) >= 1
    for finding in findings:
        assert finding.rule_id == rule_id
        assert finding.evidence, "every finding needs evidence the AI can cite"


@pytest.mark.parametrize(("capture", "rule_id"), sorted(EXPECTED.items()))
def test_evidence_points_at_real_log_records(capture, rule_id):
    log_dir = FIXTURES / capture
    for finding in RULES[rule_id](log_dir):
        for ev in finding.evidence:
            ids_in_log = {record_id(ev.log, rec) for rec in read_log(log_dir, ev.log)}
            assert ev.record_id in ids_in_log


@pytest.mark.parametrize(("rule_id", "capture"), sorted(NEAR_MISS.items()))
def test_rule_is_silent_on_near_miss(rule_id, capture):
    assert RULES[rule_id](FIXTURES / capture) == []


@pytest.mark.parametrize("rule_id", sorted(CLEARTEXT_RULES))
def test_rule_is_silent_on_clean_tls13(rule_id):
    assert RULES[rule_id](FIXTURES / "clean_tls13") == []


def test_ftp_password_is_never_in_the_finding():
    # Zeek writes "<hidden>" instead of the FTP password; the finding keeps only
    # the user name and command, so a report never shows a password.
    [finding] = RULES["cleartext.ftp"](FIXTURES / "ftp")
    assert "password" not in finding.details


def test_rdp_standard_security_fires_for_security_protocol_rdp(tmp_path):
    log_dir = write_log(tmp_path, "rdp.log", [rdp_record("RDP")])

    [finding] = RULES["rdp.standard_security"](log_dir)

    assert (finding.dst_ip, finding.dst_port) == ("192.168.56.30", 3389)
    assert finding.details == {"security_protocol": "RDP"}
    assert [ev.log for ev in finding.evidence] == ["rdp.log"]


def test_rdp_standard_security_is_silent_for_hybrid(tmp_path):
    # HYBRID = CredSSP / Network Level Authentication: the secure choice.
    log_dir = write_log(tmp_path, "rdp.log", [rdp_record("HYBRID")])
    assert RULES["rdp.standard_security"](log_dir) == []


def test_rdp_fixture_folder_flags_only_the_old_server():
    found = [(f.rule_id, f.dst_ip) for f in run_all(RDP_DIR)]
    assert found == [("rdp.standard_security", "192.168.56.30")]


# Telnet, POP3 and IMAP have no Zeek log of their own, so cleartext.zeek writes
# maxguard_cleartext.log and the rules trust every line of it. The script, not
# the Python rule, decides what counts as cleartext (ports 23/110/143, the server
# sent data, and no TLS was seen). Zeek's service set holds upper-case names such
# as "SSL", so the script compares lower-case; tests/integration checks it with Zeek.

def cleartext_script_protocols() -> set[str]:
    """Protocol names in cleartext.zeek's port table, e.g. [23/tcp] = "telnet"."""
    script = (REPO / "maxguard" / "zeek" / "scripts" / "cleartext.zeek").read_text()
    return set(re.findall(r'\[\d+/tcp\]\s*=\s*"(\w+)"', script))


def test_script_and_rules_use_the_same_protocol_names():
    # If the script wrote "pop" instead of "pop3", cleartext.pop3 would silently
    # never fire. Each rule filters maxguard_cleartext.log on one of these names.
    assert cleartext_script_protocols() == {"telnet", "pop3", "imap"}
    for proto in ("telnet", "pop3", "imap"):
        assert f"cleartext.{proto}" in RULES


def test_script_ignores_case_when_checking_for_tls():
    script = (REPO / "maxguard" / "zeek" / "scripts" / "cleartext.zeek").read_text()
    assert "to_lower(svc)" in script
```

and the whole-rule-set test `tests/unit/test_rule_registry.py`:

```python
"""The whole Fall 2026 rule set (JAK-02 completes it): 13 rules, one per capture."""

from pathlib import Path

import pytest

import maxguard.rules  # noqa: F401  (importing registers every rule)
from maxguard.rules.base import RULES, run_all

FIXTURES = Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "zeek"

EXPECTED = {
    "ftp": "cleartext.ftp", "telnet": "cleartext.telnet", "plain_http": "cleartext.http",
    "plain_http_alt": "cleartext.http_alt", "pop3": "cleartext.pop3", "imap": "cleartext.imap",
    "tls_weak_version": "tls.weak_version", "tls_weak_cipher": "tls.weak_cipher",
    "cert_expired": "cert.expired", "cert_self_signed": "cert.self_signed",
    "cert_weak_key": "cert.weak_key", "cert_sha1": "cert.sha1_signature",
}
CLEAN_CAPTURES = ["clean_tls13", "dns_lookup"]
FALL_2026_RULES = {*EXPECTED.values(), "rdp.standard_security"}


def test_all_13_fall_2026_rules_are_registered():
    # Spring rules (tls.ja4_watchlist, decoy.contact, ...) register only when their
    # module is imported, so this checks that the 13 are there, not that nothing else is.
    assert len(FALL_2026_RULES) == 13
    assert FALL_2026_RULES <= set(RULES)


@pytest.mark.parametrize("capture", sorted(EXPECTED) + CLEAN_CAPTURES)
def test_each_capture_triggers_exactly_its_rule(capture):
    expected = {EXPECTED[capture]} if capture in EXPECTED else set()
    assert {f.rule_id for f in run_all(FIXTURES / capture)} == expected
```

**Step 5.** Run them:

```bash
pytest tests/unit/test_rules_cleartext.py tests/unit/test_rule_registry.py -q
```

Expected output:

```text
...............................................                                              [100%]
47 passed in 0.08s
```

**Step 6.** Run every rule on every lab fixture and count the findings:

```bash
python -c "from pathlib import Path; import maxguard.rules; from maxguard.rules.base import RULES, run_all; print(len(RULES), 'rules'); [print(d.name, [f.rule_id for f in run_all(d)]) for d in sorted(Path('tests/fixtures/zeek').iterdir()) if not d.name.startswith('_')]"
```

Expected output:

```text
13 rules
cert_expired ['cert.expired']
cert_self_signed ['cert.self_signed']
cert_sha1 ['cert.sha1_signature']
cert_weak_key ['cert.weak_key']
clean_tls13 []
dns_lookup []
ftp ['cleartext.ftp']
imap ['cleartext.imap']
plain_http ['cleartext.http']
plain_http_alt ['cleartext.http_alt']
pop3 ['cleartext.pop3']
telnet ['cleartext.telnet']
tls_weak_cipher ['tls.weak_cipher']
tls_weak_version ['tls.weak_version']
```

**Step 7.** Commit, push, and open the pull request:

```bash
git add -A
git status          # only this task's files: nothing from .venv/, data/ or lab/captures/
git commit -m "feat: cleartext and RDP rules, all 13 rules registered (JAK-03)"
git push -u origin HEAD
```

`HEAD` means "the branch I am on", so you do not have to retype its name. Open the repository on github.com: a yellow bar shows your branch with a **Compare & pull request** button. Click it, keep the title `feat: cleartext and RDP rules, all 13 rules registered (JAK-03)`, fill in the template (paste the real output of the commands above under **How I tested it**), write `Closes #<issue number>` (this task's issue), and pick **@flau0306** under **Reviewers**. Click **Create pull request**, then fix anything CI or the reviewer finds with new commits on the same branch.

#### How to test

Both files pass; the one-liner prints `13 rules`, then one rule per capture and an empty list for `clean_tls13` and `dns_lookup`.

#### What you just did and why

Splitting the rules by file (`tls.py`, `certs.py`, `cleartext.py`) lets two people write rules in the same week without editing the same file. The registry test is the safety net for the whole set: it fails if a rule is forgotten in `__init__.py`, if a capture starts triggering a second rule, or if a clean capture triggers anything. HTTP on 8080 is its own rule because the same weakness on an "admin" port usually means a device's management page.

#### Pull request checklist

- [ ] `ruff check .` prints `All checks passed!`
- [ ] `pytest -m "not integration" -q` passes on your laptop
- [ ] The pull request title has the form `type: summary (TASK-ID)` and the body says `Closes #<issue number>`
- [ ] No secrets, passwords, email addresses, personal data, or captures from a real network (CLAUDE.md rule 6)
- [ ] Any new dependency has a row in `docs/DEPENDENCIES.md` with its license
- [ ] CI is green and your reviewer approved
- [ ] Ahmad approved the severities

### JAK-04: Asset inventory

**Due:** Week 1 (due Fri Oct 16) · **Milestone:** `W1 Building blocks` · **Needs first:** [JAK-03](#jak-03-cleartext-and-rdp-rules-the-rule-set-is-complete), [KAR-02](karthik.md#kar-02-test-fixtures-zeek-and-suricata-output-for-every-capture) · **Kind:** code, tested

**Issue labels:** `type:task` `phase:alpha` `owner:jakub` `area:engine`

#### Goal

Write `maxguard/inventory.py`: one row per IP address seen in the logs, with when it was first seen, the services it offered (`80/http`), the software named in its traffic, and how many findings involve it. The pipeline adds this list to every report, and the device inventory page shows it.

#### Prerequisites

JAK-03 and KAR-02 are merged.

#### Steps

**Step 1.** Update `main` and create your branch for this task (one branch per task):

```bash
cd ~/projects/maxguard
source .venv/bin/activate
git checkout main && git pull
git checkout -b jakub/inventory
```

If `source .venv/bin/activate` fails, you have not made the virtual environment yet: do Week 0 section 0.11 first.

**Step 2.** Create `maxguard/inventory.py`:

```python
"""Asset inventory (Jakub): one row per IP address seen in the logs.

Zeek writes three "asset" logs because maxguard/zeek/scripts/inventory.zeek
turns on tracking for ALL_HOSTS (by default Zeek only tracks hosts in its
local-networks list, which is empty in our setup):

- known_hosts.log    hosts that completed a TCP handshake
- known_services.log servers that answered on a port (TCP or UDP)
- software.log       client and server software named in the traffic

build() merges them into one dict per IP:

    {"ip": "172.18.0.2", "first_seen": 1791250493.372808,
     "services": ["80/http"], "software": ["SimpleHTTP 0.6-Python/3"],
     "finding_count": 1}

Like the rules, it never reads the clock, so the same logs always give the
same inventory in the same order.
"""

from __future__ import annotations

import ipaddress
from pathlib import Path

from maxguard.adapters.base import read_log
from maxguard.models import Finding


def ip_sort_key(ip: str) -> tuple[int, ipaddress.IPv4Address | ipaddress.IPv6Address]:
    """Sort IPs by number, so 172.18.0.10 comes after 172.18.0.2 (text order would not).

    The IP version comes first because Python cannot compare an IPv4 address
    with an IPv6 address directly.
    """
    address = ipaddress.ip_address(ip)
    return (address.version, address)


def service_names(rec: dict) -> list[str]:
    """Turn one known_services.log record into ["80/http", ...].

    Zeek writes service names in capitals ("HTTP") and an empty name when it
    could not tell the protocol; then we show the transport instead ("8080/tcp").
    """
    port = rec["port_num"]
    names = [name.lower() for name in rec.get("service") or [] if name]
    if not names:
        names = [rec.get("port_proto") or "unknown"]
    return [f"{port}/{name}" for name in names]


def software_version(rec: dict) -> str:
    """Rebuild the version text the way Zeek's software_fmt_version() does.

    Example: major 0, minor 6, addl "Python/3" -> "0.6-Python/3".
    """
    parts = [rec.get(f"version.{key}") for key in ("major", "minor", "minor2", "minor3")]
    numbers = [str(p) for p in parts if p is not None]
    if not numbers:
        return ""
    text = ".".join(numbers)
    if rec.get("version.addl"):
        text += f"-{rec['version.addl']}"
    return text


def software_name(rec: dict) -> str:
    """'name version', or just the name when Zeek found no version."""
    version = software_version(rec)
    return f"{rec['name']} {version}" if version else rec["name"]


def new_asset(ip: str, ts: float) -> dict:
    # sets while collecting (no duplicates); turned into sorted lists at the end
    return {"ip": ip, "first_seen": ts, "services": set(), "software": set(),
            "finding_count": 0}


def asset_for(assets: dict[str, dict], ip: str, ts: float) -> dict:
    """Get (or create) the asset for ip and keep its earliest timestamp."""
    if ip not in assets:
        assets[ip] = new_asset(ip, ts)
    assets[ip]["first_seen"] = min(assets[ip]["first_seen"], ts)
    return assets[ip]


def count_findings(assets: dict[str, dict], findings: list[Finding]) -> None:
    """Add one to finding_count for each finding an IP takes part in (as source or target).

    A host that appears only in a finding is still added, because imported Zeek
    logs may not include the known_*.log files.
    """
    for f in findings:
        for ip in {f.src_ip, f.dst_ip}:  # a set, so src == dst counts once
            asset_for(assets, ip, f.first_seen)["finding_count"] += 1


def finish(asset: dict) -> dict:
    """Turn the working sets into sorted lists (ports in number order)."""
    services = sorted(asset["services"], key=lambda s: (int(s.split("/")[0]), s))
    return {"ip": asset["ip"], "first_seen": asset["first_seen"], "services": services,
            "software": sorted(asset["software"]), "finding_count": asset["finding_count"]}


def build(log_dir: Path, findings: list[Finding]) -> list[dict]:
    """One asset dict per IP, sorted by IP. See the module docstring for the keys."""
    assets: dict[str, dict] = {}
    for rec in read_log(log_dir, "known_hosts.log"):
        asset_for(assets, rec["host"], float(rec["ts"]))
    for rec in read_log(log_dir, "known_services.log"):
        asset = asset_for(assets, rec["host"], float(rec["ts"]))
        asset["services"].update(service_names(rec))
    for rec in read_log(log_dir, "software.log"):
        asset = asset_for(assets, rec["host"], float(rec["ts"]))
        asset["software"].add(software_name(rec))
    count_findings(assets, findings)
    return [finish(assets[ip]) for ip in sorted(assets, key=ip_sort_key)]
```

**Step 3.** Create the tests `tests/unit/test_inventory.py`:

```python
"""Tests for maxguard.inventory (asset inventory)."""

import json
from pathlib import Path

import pytest

import maxguard.rules  # noqa: F401  (registers the rules used by run_all)
from maxguard.inventory import build, ip_sort_key, service_names, software_name
from maxguard.models import Finding
from maxguard.rules.base import run_all

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "zeek"
CAPTURES = sorted(p for p in FIXTURES.iterdir() if p.is_dir() and not p.name.startswith("_"))
ASSET_KEYS = ("ip", "first_seen", "services", "software", "finding_count")


def write_log(log_dir: Path, name: str, records: list[dict]) -> None:
    """Write a tiny Zeek JSON log (one object per line) for a test."""
    log_dir.mkdir(parents=True, exist_ok=True)
    (log_dir / name).write_text("".join(json.dumps(r) + "\n" for r in records))


def finding(src: str, dst: str, ts: float = 100.0) -> Finding:
    return Finding(rule_id="cleartext.telnet", title="Telnet", severity="high",
                   src_ip=src, dst_ip=dst, dst_port=23, protocol="telnet",
                   first_seen=ts, last_seen=ts)


def test_plain_http_capture():
    log_dir = FIXTURES / "plain_http"
    assets = build(log_dir, run_all(log_dir))
    assert assets == [
        {"ip": "172.18.0.2", "first_seen": 1791250493.372808, "services": ["80/http"],
         "software": ["SimpleHTTP 0.6-Python/3"], "finding_count": 1},
        {"ip": "172.18.0.3", "first_seen": 1791250493.372808, "services": [],
         "software": ["Python-urllib 3.11"], "finding_count": 1},
    ]


def test_udp_only_client_is_not_in_known_hosts():
    # known_hosts.log needs a finished TCP handshake; the DNS capture is UDP only,
    # so only the DNS server shows up (through known_services.log).
    assets = build(FIXTURES / "dns_lookup", [])
    assert assets == [{"ip": "172.18.0.2", "first_seen": 1791252458.740764,
                       "services": ["53/dns"], "software": [], "finding_count": 0}]


@pytest.mark.parametrize("log_dir", CAPTURES, ids=lambda p: p.name)
def test_every_capture_same_keys_same_result(log_dir):
    findings = run_all(log_dir)
    first = build(log_dir, findings)
    assert first == build(log_dir, findings)
    assert first, "every lab capture has at least one host"
    for asset in first:
        assert tuple(asset) == ASSET_KEYS
        assert asset["services"] == sorted(asset["services"], key=lambda s: int(s.split("/")[0]))
        assert asset["software"] == sorted(asset["software"])
    # every finding is counted on both of its hosts
    assert sum(a["finding_count"] for a in first) == 2 * len(findings)


def test_sorted_by_ip_number_ipv4_before_ipv6(tmp_path):
    write_log(tmp_path, "known_hosts.log", [
        {"ts": 3.0, "host": "fd00::1"},
        {"ts": 2.0, "host": "10.0.0.10"},
        {"ts": 1.0, "host": "10.0.0.9"},
    ])
    assert [a["ip"] for a in build(tmp_path, [])] == ["10.0.0.9", "10.0.0.10", "fd00::1"]


def test_first_seen_is_the_earliest_record(tmp_path):
    write_log(tmp_path, "known_hosts.log", [{"ts": 50.0, "host": "10.0.0.1"}])
    write_log(tmp_path, "known_services.log", [
        {"ts": 20.0, "host": "10.0.0.1", "port_num": 22, "port_proto": "tcp", "service": ["SSH"]},
    ])
    [asset] = build(tmp_path, [])
    assert asset["first_seen"] == 20.0


def test_services_sorted_by_port_number_and_deduplicated(tmp_path):
    write_log(tmp_path, "known_services.log", [
        {"ts": 1.0, "host": "10.0.0.1", "port_num": 443, "port_proto": "tcp", "service": ["SSL"]},
        {"ts": 2.0, "host": "10.0.0.1", "port_num": 80, "port_proto": "tcp", "service": ["HTTP"]},
        {"ts": 3.0, "host": "10.0.0.1", "port_num": 80, "port_proto": "tcp", "service": ["HTTP"]},
    ])
    [asset] = build(tmp_path, [])
    assert asset["services"] == ["80/http", "443/ssl"]


def test_service_without_a_name_shows_the_transport():
    rec = {"host": "10.0.0.1", "port_num": 8443, "port_proto": "tcp", "service": [""]}
    assert service_names(rec) == ["8443/tcp"]
    rec["service"] = ["SSL", "HTTP"]
    assert service_names(rec) == ["8443/ssl", "8443/http"]


def test_software_name_follows_zeek_version_format():
    assert software_name({"name": "OpenSSH", "version.major": 9, "version.minor": 6,
                          "version.addl": "p1"}) == "OpenSSH 9.6-p1"
    assert software_name({"name": "nginx", "version.major": 1, "version.minor": 24,
                          "version.minor2": 0}) == "nginx 1.24.0"
    assert software_name({"name": "curl"}) == "curl"


def test_findings_are_counted_and_finding_only_hosts_are_added(tmp_path):
    write_log(tmp_path, "known_hosts.log", [{"ts": 10.0, "host": "10.0.0.2"}])
    findings = [finding("10.0.0.3", "10.0.0.2", ts=5.0), finding("10.0.0.4", "10.0.0.2")]
    assets = {a["ip"]: a for a in build(tmp_path, findings)}
    assert assets["10.0.0.2"]["finding_count"] == 2
    assert assets["10.0.0.2"]["first_seen"] == 5.0  # the finding is older than the log line
    assert assets["10.0.0.3"] == {"ip": "10.0.0.3", "first_seen": 5.0, "services": [],
                                  "software": [], "finding_count": 1}


def test_no_logs_no_findings_gives_empty_inventory(tmp_path):
    assert build(tmp_path, []) == []


def test_ip_sort_key():
    ips = ["192.168.1.20", "fe80::1", "192.168.1.3", "10.1.1.1"]
    assert sorted(ips, key=ip_sort_key) == ["10.1.1.1", "192.168.1.3", "192.168.1.20", "fe80::1"]
```

**Step 4.** Run them:

```bash
pytest tests/unit/test_inventory.py -q
```

Expected output:

```text
........................                                                                     [100%]
24 passed in 0.07s
```

**Step 5.** Build the inventory for the plain-HTTP fixture:

```bash
python -c "import json; from pathlib import Path; import maxguard.rules; from maxguard.inventory import build; from maxguard.rules.base import run_all; d = Path('tests/fixtures/zeek/plain_http'); [print(json.dumps(a)) for a in build(d, run_all(d))]"
```

Expected output:

```text
{"ip": "172.18.0.2", "first_seen": 1791250493.372808, "services": ["80/http"], "software": ["SimpleHTTP 0.6-Python/3"], "finding_count": 1}
{"ip": "172.18.0.3", "first_seen": 1791250493.372808, "services": [], "software": ["Python-urllib 3.11"], "finding_count": 1}
```

**Step 6.** Commit, push, and open the pull request:

```bash
git add -A
git status          # only this task's files: nothing from .venv/, data/ or lab/captures/
git commit -m "feat: asset inventory from Zeek's known-hosts, services and software logs (JAK-04)"
git push -u origin HEAD
```

`HEAD` means "the branch I am on", so you do not have to retype its name. Open the repository on github.com: a yellow bar shows your branch with a **Compare & pull request** button. Click it, keep the title `feat: asset inventory from Zeek's known-hosts, services and software logs (JAK-04)`, fill in the template (paste the real output of the commands above under **How I tested it**), write `Closes #<issue number>` (this task's issue), and pick **@flau0306** under **Reviewers**. Click **Create pull request**, then fix anything CI or the reviewer finds with new commits on the same branch.

#### How to test

`pytest` passes, and the one-liner prints the lab server with `80/http` and Python's web server software, and the client with one finding.

#### What you just did and why

An alert says "172.18.0.2 offers Telnet"; the inventory answers "what is 172.18.0.2?". Sorting IPs by their numeric value (`ip_sort_key`) keeps `.10` after `.2`, and never reading the clock keeps the list identical on every run. Later the live sensor adds MAC addresses and host names to the same rows (JAK-07).

#### Pull request checklist

- [ ] `ruff check .` prints `All checks passed!`
- [ ] `pytest -m "not integration" -q` passes on your laptop
- [ ] The pull request title has the form `type: summary (TASK-ID)` and the body says `Closes #<issue number>`
- [ ] No secrets, passwords, email addresses, personal data, or captures from a real network (CLAUDE.md rule 6)
- [ ] Any new dependency has a row in `docs/DEPENDENCIES.md` with its license
- [ ] CI is green and your reviewer approved

### JAK-05: Suricata in the pipeline

**Due:** Week 4 (due Fri Nov 6) · **Milestone:** `W4 Full offline report` · **Needs first:** [JAK-02](#jak-02-suricata-configuration-community-id-and-ja4), [FIO-01](fiona.md#fio-01-zeek-runner-and-the-two-input-adapters), [JAI-05](jaiden.md#jai-05-the-pipeline-one-function-from-input-to-report), [JAI-07](jaiden.md#jai-07-the-api-uploads-alerts-events-live-updates-sensor-ingest) · **Kind:** code, tested

**Issue labels:** `type:task` `phase:alpha` `owner:jakub` `area:engine`

#### Goal

When Suricata is installed (it is, in the engine image), run it next to Zeek on every capture so `eve.json` lands in the same log folder. The normalizer already reads it, so Suricata's events and JA4 fingerprints appear in the report and the event store. On a laptop without Suricata nothing changes.

#### Prerequisites

JAK-02, FIO-01, JAI-05 and JAI-07 (the API) are merged.

#### Steps

**Step 1.** Update `main` and create your branch for this task (one branch per task):

```bash
cd ~/projects/maxguard
source .venv/bin/activate
git checkout main && git pull
git checkout -b jakub/suricata-pipeline
```

If `source .venv/bin/activate` fails, you have not made the virtual environment yet: do Week 0 section 0.11 first.

**Step 2.** Create `maxguard/suricata/runner.py`:

```python
"""Run Suricata on one capture file and add eve.json to the log folder (v2.0).

Suricata is optional for reading captures: if the `suricata` program is not
installed (for example on a laptop running only the unit tests), the pipeline
continues with Zeek logs alone and the report says so.
"""

import shutil
import subprocess
from pathlib import Path

HERE = Path(__file__).parent
CONFIG = HERE / "maxguard-suricata.yaml"
RULES = HERE / "rules" / "maxguard.rules"


class SuricataError(RuntimeError):
    pass


def run_suricata(pcap: Path, log_dir: Path, timeout: int = 1800) -> Path:
    """Write log_dir/eve.json for one capture. Returns the eve.json path."""
    log_dir.mkdir(parents=True, exist_ok=True)
    cmd = ["suricata", "-c", str(CONFIG), "-r", str(pcap.resolve()),
           "-l", str(log_dir), "-k", "none", "--runmode", "single", "-S", str(RULES)]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, check=False)
    except subprocess.TimeoutExpired:
        raise SuricataError(f"Suricata took longer than {timeout} seconds") from None
    if res.returncode != 0:
        raise SuricataError(res.stderr.strip() or "suricata failed")
    for extra in ("fast.log", "stats.log", "suricata.log"):  # keep only eve.json
        (log_dir / extra).unlink(missing_ok=True)
    return log_dir / "eve.json"


def run_suricata_if_available(pcap: Path, log_dir: Path) -> Path | None:
    if shutil.which("suricata") is None:
        return None
    return run_suricata(pcap, log_dir)
```

**Step 3.** Replace `maxguard/adapters/pcap.py` with the version that calls it:

```python
"""PcapAdapter: a .pcap or .pcapng file -> Zeek logs (+ Suricata eve.json)."""

from pathlib import Path

from maxguard.suricata.runner import run_suricata_if_available
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
        log_dir = run_zeek(path, workdir / "zeek_logs")
        run_suricata_if_available(path, log_dir)  # v2.0: adds eve.json when installed
        return log_dir
```

**Step 4.** A Suricata failure must reach the dashboard like a Zeek failure: as HTTP 422 with the error message. In `maxguard/api/app.py` (JAI-07), import the new error next to `ZeekError` and catch both in `run_pipeline()`:

```python
from maxguard.suricata.runner import SuricataError
...
        except (ZeekError, SuricataError) as err:
            raise HTTPException(422, str(err)) from None
```

Ask Jaiden to review this part: the API is his module.

**Step 5.** Create the tests `tests/unit/test_suricata_runner.py`. They put a tiny fake `suricata` program on the `PATH`, so they run without the real one:

```python
"""Suricata runner tests (Jakub, JAK-05). No real Suricata is needed.

A tiny fake `suricata` program is put first on the PATH. It writes the files
the real one writes, so the tests check what MaxGuard does with them.
"""

import os
import stat
from pathlib import Path

import pytest

from maxguard.suricata import runner

FAKE_SURICATA = """#!/bin/sh
# Fake suricata: find the folder after -l and write what Suricata would write.
while [ $# -gt 0 ]; do
  if [ "$1" = "-l" ]; then out="$2"; fi
  shift
done
echo '{"event_type":"flow"}' > "$out/eve.json"
for extra in fast.log stats.log suricata.log; do echo x > "$out/$extra"; done
exit ${FAKE_EXIT:-0}
"""


@pytest.fixture
def fake_suricata(tmp_path, monkeypatch):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    program = bin_dir / "suricata"
    program.write_text(FAKE_SURICATA)
    program.chmod(program.stat().st_mode | stat.S_IEXEC)
    monkeypatch.setenv("PATH", f"{bin_dir}{os.pathsep}{os.environ['PATH']}")
    return program


def test_without_suricata_nothing_happens(tmp_path, monkeypatch):
    monkeypatch.setenv("PATH", str(tmp_path / "empty"))  # no suricata anywhere

    assert runner.run_suricata_if_available(Path("x.pcap"), tmp_path) is None
    assert list(tmp_path.iterdir()) == []


def test_eve_json_is_written_and_the_other_files_removed(tmp_path, fake_suricata):
    log_dir = tmp_path / "logs"

    eve = runner.run_suricata_if_available(Path("capture.pcap"), log_dir)

    assert eve == log_dir / "eve.json"
    assert sorted(p.name for p in log_dir.iterdir()) == ["eve.json"]


def test_a_failing_suricata_raises(tmp_path, fake_suricata, monkeypatch):
    monkeypatch.setenv("FAKE_EXIT", "1")

    with pytest.raises(runner.SuricataError):
        runner.run_suricata(Path("capture.pcap"), tmp_path / "logs")
```

**Step 6.** Run them, then the whole unit suite:

```bash
pytest tests/unit/test_suricata_runner.py -q
```

Expected output:

```text
...                                                                                          [100%]
3 passed in 0.06s
```

```bash
pytest -m "not integration" -q
```

Expected output:

```text
............................................................................................ [ 19%]
..........................................................................................s. [ 38%]
............................................................................................ [ 57%]
............................................................................................ [ 77%]
............................................................................................ [ 96%]
................                                                                             [100%]
475 passed, 1 skipped, 31 deselected in 7.17s
```

**Step 7.** Add the integration test that proves Suricata now runs next to Zeek, `tests/integration/test_suricata_pipeline.py`. Where Suricata is missing it shows as skipped, with the reason, instead of passing:

```python
"""Suricata runs next to Zeek in the pipeline (Jakub, JAK-05).

Once JAK-05 is merged, analyze() runs Suricata on every capture whenever Suricata
is installed. The engine image has it, so CI runs this test. Where Suricata is
missing (a laptop, or the Zeek-only image used in planning) the test shows as
"skipped" with the reason, never silently passed, and CI's "suricata -V" step
fails if the engine image ever loses Suricata.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from maxguard.pipeline import analyze

PCAPS = Path(__file__).resolve().parents[1] / "pcaps"


@pytest.mark.integration
@pytest.mark.skipif(shutil.which("suricata") is None,
                    reason="suricata is not installed here; the engine image has it")
def test_zeek_and_suricata_both_ran(tmp_path):
    report = analyze(PCAPS / "tls_weak_version.pcap", tmp_path, explain=False)

    assert report["tools"] == {"zeek": True, "suricata": True}
    # Suricata ran with MaxGuard's settings: its TLS event carries a JA4, and the
    # same Community ID as Zeek's event for that connection, so the two can be joined.
    [suricata_tls] = [e for e in report["events"]
                      if e["source"] == "suricata" and e["kind"] == "tls"]
    [zeek_tls] = [e for e in report["events"] if e["source"] == "zeek" and e["kind"] == "tls"]
    assert suricata_tls["ja4"] != ""
    assert zeek_tls["community_id"] != ""
    assert suricata_tls["community_id"] == zeek_tls["community_id"]
```

```bash
docker build -f docker/Dockerfile --target test -t maxguard:test .
docker run --rm --network none maxguard:test pytest -m integration tests/integration/test_suricata_pipeline.py -q -rs
```

Expected output:

```text
s                                                                        [100%]
=========================== short test summary info ============================
SKIPPED [1] tests/integration/test_suricata_pipeline.py:22: suricata is not installed here; the engine image has it
1 skipped in 0.06s
```

*In planning this ran in `zeek/zeek:9.0.0`, which has no Suricata, so it was skipped as shown. With Zeek and Suricata both available it passed: the Suricata TLS event had a JA4 and the same Community ID as Zeek's. In the engine image you should see `1 passed`.*

**Step 8.** The real check runs in the engine image, where Suricata is installed:

```bash
docker run --rm --network none -v "$PWD/tests/pcaps:/pcaps:ro" maxguard:dev python -c "import json, tempfile; from pathlib import Path; from maxguard.pipeline import analyze; r = analyze(Path('/pcaps/tls_weak_version.pcap'), Path(tempfile.mkdtemp()), explain=False); print(r['tools']); print(sorted({e['source'] for e in r['events']})); print([e['ja4'] for e in r['events'] if e['ja4']])"
```

Expected output (not run in planning):

```text
{'zeek': True, 'suricata': True}
['suricata', 'zeek']
['t10d230600_44099cda8a52_242d16716555']
```

*Not run in planning: the engine image needs Debian's package servers to build. The expected output is what the same pipeline gives on this capture's fixture (its JA4 came from Suricata 7.0.10 with MaxGuard's settings).*

**Step 9.** Commit, push, and open the pull request:

```bash
git add -A
git status          # only this task's files: nothing from .venv/, data/ or lab/captures/
git commit -m "feat: run Suricata next to Zeek on captures (JAK-05)"
git push -u origin HEAD
```

`HEAD` means "the branch I am on", so you do not have to retype its name. Open the repository on github.com: a yellow bar shows your branch with a **Compare & pull request** button. Click it, keep the title `feat: run Suricata next to Zeek on captures (JAK-05)`, fill in the template (paste the real output of the commands above under **How I tested it**), write `Closes #<issue number>` (this task's issue), and pick **@flau0306** under **Reviewers**. Click **Create pull request**, then fix anything CI or the reviewer finds with new commits on the same branch.

#### How to test

The unit tests pass without Suricata installed. In the image, `tools` lists both Zeek and Suricata, events come from both `zeek` and `suricata`, and the TLS client hello has a JA4 fingerprint.

#### What you just did and why

Zeek and Suricata are good at different things: Zeek describes every connection, Suricata matches signatures and computes JA4. Running both on the same capture costs a few seconds and gives the analyst both views, joined by Community ID. Making Suricata optional keeps the unit tests fast on any laptop, while the report's `tools` section says honestly which tools ran.

#### Pull request checklist

- [ ] `ruff check .` prints `All checks passed!`
- [ ] `pytest -m "not integration" -q` passes on your laptop
- [ ] The pull request title has the form `type: summary (TASK-ID)` and the body says `Closes #<issue number>`
- [ ] No secrets, passwords, email addresses, personal data, or captures from a real network (CLAUDE.md rule 6)
- [ ] Any new dependency has a row in `docs/DEPENDENCIES.md` with its license
- [ ] CI is green and your reviewer approved
- [ ] The image check lists events from both tools

### JAK-06: Build the reference lab and prove the mirror works

**Due:** Week 8 (due Fri Dec 4) · **Milestone:** `W8 v2.0-alpha` · **Needs first:** [JAK-02](#jak-02-suricata-configuration-community-id-and-ja4) · **Kind:** process

**Issue labels:** `type:task` `phase:alpha` `owner:jakub` `area:sensor` `needs-hardware`

> **Needs hardware.** Steps that use the Raspberry Pi, the switch or other devices were not run during planning; they are marked *not run — verify on hardware*.

#### Goal

Build the hardware lab from `docs/HARDWARE.md` — router, TL-SG105E mirror, mesh in bridge mode, Raspberry Pi 5 with a silent capture port, USB SSD, Docker, Zeek and Suricata — and run its five tests. This makes the spring live-sensor work possible and replaces every "not run — verify on hardware" in that guide with what really happened.

#### Prerequisites

The parts in `docs/HARDWARE.md` section 2 have arrived (ask Ahmad). If they arrive after December 4, do this task in the first spring week.

#### Steps

**Step 1.** Update `main` and create your branch for this task (one branch per task):

```bash
cd ~/projects/maxguard
source .venv/bin/activate
git checkout main && git pull
git checkout -b jakub/lab-build
```

If `source .venv/bin/activate` fails, you have not made the virtual environment yet: do Week 0 section 0.11 first.

**Step 2.** Follow `docs/HARDWARE.md` sections 3 to 11 in order. Keep a text file of every command you ran and its output (no real addresses or MAC addresses: replace them with the guide's example addresses before committing).

**Step 3.** Run the five tests in section 12 and fill in the throughput table of test 4.

**Step 4.** Edit `docs/HARDWARE.md`: for each step you ran, replace "not run — verify on hardware" with "verified on <date>" and fix every menu name, output, or command that was different on the real devices. Fill in section 11.3 with the Suricata command that worked.

**Step 5.** Commit, push, and open the pull request:

```bash
git add -A
git status          # only this task's files: nothing from .venv/, data/ or lab/captures/
git commit -m "docs: verify HARDWARE.md on the reference lab (JAK-06)"
git push -u origin HEAD
```

`HEAD` means "the branch I am on", so you do not have to retype its name. Open the repository on github.com: a yellow bar shows your branch with a **Compare & pull request** button. Click it, keep the title `docs: verify HARDWARE.md on the reference lab (JAK-06)`, fill in the template (paste the real output of the commands above under **How I tested it**), write `Closes #<issue number>` (this task's issue), and pick **@flau0306** under **Reviewers**. Click **Create pull request**, then fix anything CI or the reviewer finds with new commits on the same branch.

#### How to test

Test 1 prints `PASS: both directions are reaching the sensor.`, test 5 prints `FAIL` with mirroring off and `PASS` again after turning it back on, and stage 5 of test 4 shows loss (if it shows none, the measurement is wrong).

#### What you just did and why

Everything in the hardware guide was checked against manuals, not devices, so some details will be wrong. Running it once, carefully, and fixing the guide is what makes it safe for the next student. The throughput table tells users honestly how much traffic a Pi sensor can watch.

#### Pull request checklist

- [ ] `ruff check .` prints `All checks passed!`
- [ ] `pytest -m "not integration" -q` passes on your laptop
- [ ] The pull request title has the form `type: summary (TASK-ID)` and the body says `Closes #<issue number>`
- [ ] No secrets, passwords, email addresses, personal data, or captures from a real network (CLAUDE.md rule 6)
- [ ] Any new dependency has a row in `docs/DEPENDENCIES.md` with its license
- [ ] CI is green and your reviewer approved
- [ ] No real IP addresses, MAC addresses, Wi-Fi names or passwords in the pull request
- [ ] Test 4's table is filled in

## Spring 2027: v2.0

### JAK-08: Device attribution: which device is behind each IP address

**Due:** Spring S1-S4 (due Fri Feb 12, 2027) · **Milestone:** `S1-S4 Live sensor` · **Needs first:** [JAK-04](#jak-04-asset-inventory), [KAR-02](karthik.md#kar-02-test-fixtures-zeek-and-suricata-output-for-every-capture) · **Kind:** code, tested

**Issue labels:** `type:task` `phase:spring` `owner:jakub` `area:sensor`

#### Goal

Join DHCP leases (MAC address and host name) and DNS questions with IP addresses, so the timeline and inventory pages can say "laptop-lab (02:00:00:aa:bb:cc)" instead of only an address.

#### Prerequisites

JAK-04 and KAR-02 are merged.

#### Steps

**Step 1.** Update `main` and create your branch for this task (one branch per task):

```bash
cd ~/projects/maxguard
source .venv/bin/activate
git checkout main && git pull
git checkout -b jakub/attribution
```

If `source .venv/bin/activate` fails, you have not made the virtual environment yet: do Week 0 section 0.11 first.

**Step 2.** Create `maxguard/sensor/__init__.py`:

```python
"""Sensor-side helpers (Jakub).

attribution.py  device table: which MAC / host name / DNS names belong to each IP
"""
```

and `maxguard/sensor/attribution.py`:

```python
"""Device attribution (Jakub): which device is behind each IP address.

Two Zeek logs say who a device is:
- dhcp.log: the DHCP server gave address `assigned_addr` to the network card
  `mac`, and the device called itself `host_name`.
- dns.log: the device at `id.orig_h` asked for the name `query`.

build_device_table() joins them on the IP address, one row per IP:

    {"ip": "192.168.56.50", "mac": "02:00:00:aa:bb:cc", "host_name": "laptop-lab",
     "dns_names": ["printer.lab.invalid"], "first_seen": 1791252600.0}

mac and host_name are "" when no DHCP lease was seen (for example a device
with a fixed address). Like the rules, this never reads the clock, so the same
logs always give the same table in the same order.
"""

from __future__ import annotations

from pathlib import Path

from maxguard.adapters.base import read_log
from maxguard.inventory import ip_sort_key


def new_device(ip: str, ts: float) -> dict:
    return {"ip": ip, "mac": "", "host_name": "", "dns_names": set(), "first_seen": ts}


def device_for(devices: dict[str, dict], ip: str, ts: float) -> dict:
    """Get (or create) the device row for ip and keep its earliest timestamp."""
    if ip not in devices:
        devices[ip] = new_device(ip, ts)
    devices[ip]["first_seen"] = min(devices[ip]["first_seen"], ts)
    return devices[ip]


def leases(log_dir: Path) -> list[dict]:
    """dhcp.log records that handed out an address, oldest first.

    Sorting makes "the latest lease wins" well defined even if records are
    out of order (the MAC breaks ties so the order never depends on luck).
    """
    found = [r for r in read_log(log_dir, "dhcp.log") if r.get("assigned_addr")]
    return sorted(found, key=lambda r: (float(r["ts"]), r.get("mac") or ""))


def apply_lease(device: dict, rec: dict) -> None:
    """Record who holds the address now. A later lease replaces an earlier one."""
    mac = rec.get("mac") or ""
    if mac != device["mac"]:
        device["host_name"] = ""  # another card took the address: forget the old name
    device["mac"] = mac
    # renewals often leave out the host name, so keep the one we already know
    device["host_name"] = rec.get("host_name") or device["host_name"]


def finish(device: dict) -> dict:
    return {**device, "dns_names": sorted(device["dns_names"])}


def build_device_table(log_dir: Path) -> list[dict]:
    """One row per IP seen in a DHCP lease or as a DNS client, sorted by IP."""
    devices: dict[str, dict] = {}
    for rec in leases(log_dir):
        apply_lease(device_for(devices, rec["assigned_addr"], float(rec["ts"])), rec)
    for rec in read_log(log_dir, "dns.log"):
        if rec.get("query"):  # optional in dns.log: a message with no question has none
            device = device_for(devices, rec["id.orig_h"], float(rec["ts"]))
            device["dns_names"].add(rec["query"].lower())  # DNS names ignore case
    return [finish(devices[ip]) for ip in sorted(devices, key=ip_sort_key)]
```

**Step 3.** Create the tests `tests/unit/test_attribution.py`:

```python
"""Tests for maxguard.sensor.attribution (device table from DHCP + DNS)."""

import json
from pathlib import Path

from maxguard.sensor.attribution import build_device_table

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "zeek"
DEVICE_KEYS = ("ip", "mac", "host_name", "dns_names", "first_seen")


def write_log(log_dir: Path, name: str, records: list[dict]) -> None:
    """Write a tiny Zeek JSON log (one object per line) for a test."""
    log_dir.mkdir(parents=True, exist_ok=True)
    (log_dir / name).write_text("".join(json.dumps(r) + "\n" for r in records))


def lease(ts: float, ip: str, mac: str, host_name: str | None = None) -> dict:
    rec = {"ts": ts, "mac": mac, "assigned_addr": ip, "msg_types": ["REQUEST", "ACK"]}
    if host_name:
        rec["host_name"] = host_name
    return rec


def query(ts: float, ip: str, name: str | None) -> dict:
    rec = {"ts": ts, "id.orig_h": ip, "id.resp_h": "10.0.0.1", "id.resp_p": 53}
    if name:
        rec["query"] = name
    return rec


def test_dhcp_and_dns_joined_on_the_ip():
    # Zeek 9.0.0 logs of a synthetic DHCP lease followed by one DNS lookup
    table = build_device_table(FIXTURES / "_handmade" / "dns_dhcp")
    assert table == [{"ip": "192.168.56.50", "mac": "02:00:00:aa:bb:cc",
                      "host_name": "laptop-lab", "dns_names": ["printer.lab.invalid"],
                      "first_seen": 1791252600.0}]


def test_dns_only_device_from_the_lab_capture():
    # The lab uses fixed addresses (no DHCP), so MAC and host name stay empty.
    table = build_device_table(FIXTURES / "dns_lookup")
    assert table == [{"ip": "172.18.0.3", "mac": "", "host_name": "",
                      "dns_names": ["camera.lab.invalid", "nas.lab.invalid",
                                    "printer.lab.invalid"],
                      "first_seen": 1791252458.738595}]


def test_latest_lease_wins_and_a_new_mac_forgets_the_old_name(tmp_path):
    write_log(tmp_path, "dhcp.log", [
        lease(30.0, "10.0.0.5", "02:00:00:00:00:02"),  # new card, no host name sent
        lease(10.0, "10.0.0.5", "02:00:00:00:00:01", "old-laptop"),
    ])
    [device] = build_device_table(tmp_path)
    assert (device["mac"], device["host_name"], device["first_seen"]) == (
        "02:00:00:00:00:02", "", 10.0)


def test_renewal_without_host_name_keeps_the_name(tmp_path):
    write_log(tmp_path, "dhcp.log", [
        lease(10.0, "10.0.0.5", "02:00:00:00:00:01", "printer"),
        lease(20.0, "10.0.0.5", "02:00:00:00:00:01"),
    ])
    [device] = build_device_table(tmp_path)
    assert device["host_name"] == "printer"


def test_dns_names_are_unique_lower_case_and_sorted(tmp_path):
    write_log(tmp_path, "dns.log", [
        query(1.0, "10.0.0.7", "NAS.lab.invalid"),
        query(2.0, "10.0.0.7", "nas.lab.invalid"),
        query(3.0, "10.0.0.7", "camera.lab.invalid"),
        query(4.0, "10.0.0.7", None),  # no question in this message: skipped
    ])
    [device] = build_device_table(tmp_path)
    assert device["dns_names"] == ["camera.lab.invalid", "nas.lab.invalid"]


def test_rows_sorted_by_ip_and_line_order_does_not_matter(tmp_path):
    records = [query(1.0, "10.0.0.10", "a.lab.invalid"), query(2.0, "10.0.0.9", "b.lab.invalid")]
    write_log(tmp_path / "one", "dns.log", records)
    write_log(tmp_path / "two", "dns.log", list(reversed(records)))
    one = build_device_table(tmp_path / "one")
    assert [d["ip"] for d in one] == ["10.0.0.9", "10.0.0.10"]
    assert one == build_device_table(tmp_path / "two")
    assert all(tuple(d) == DEVICE_KEYS for d in one)


def test_dhcp_record_without_an_address_is_ignored(tmp_path):
    write_log(tmp_path, "dhcp.log", [{"ts": 1.0, "mac": "02:00:00:00:00:09",
                                      "msg_types": ["DISCOVER"]}])
    assert build_device_table(tmp_path) == []


def test_no_logs_gives_empty_table(tmp_path):
    assert build_device_table(tmp_path) == []
```

**Step 4.** Run them:

```bash
pytest tests/unit/test_attribution.py -q
```

Expected output:

```text
........                                                                                     [100%]
8 passed in 0.04s
```

**Step 5.** Build the device table for the hand-made DNS and DHCP fixture:

```bash
python -c "import json; from pathlib import Path; from maxguard.sensor.attribution import build_device_table; [print(json.dumps(d)) for d in build_device_table(Path('tests/fixtures/zeek/_handmade/dns_dhcp'))]"
```

Expected output:

```text
{"ip": "192.168.56.50", "mac": "02:00:00:aa:bb:cc", "host_name": "laptop-lab", "dns_names": ["printer.lab.invalid"], "first_seen": 1791252600.0}
```

**Step 6.** Commit, push, and open the pull request:

```bash
git add -A
git status          # only this task's files: nothing from .venv/, data/ or lab/captures/
git commit -m "feat: device attribution from DHCP and DNS logs (JAK-08)"
git push -u origin HEAD
```

`HEAD` means "the branch I am on", so you do not have to retype its name. Open the repository on github.com: a yellow bar shows your branch with a **Compare & pull request** button. Click it, keep the title `feat: device attribution from DHCP and DNS logs (JAK-08)`, fill in the template (paste the real output of the commands above under **How I tested it**), write `Closes #<issue number>` (this task's issue), and pick **@flau0306** under **Reviewers**. Click **Create pull request**, then fix anything CI or the reviewer finds with new commits on the same branch.

#### How to test

`pytest` passes and the one-liner prints the lab laptop with its MAC address, host name, and the name it looked up.

#### What you just did and why

IP addresses change when DHCP leases expire, and phones use random Wi-Fi MAC addresses, so an IP alone does not identify a device for long. DHCP is the one moment a device announces its MAC address and often its name; that is why the hardware guide makes sure DHCP crosses the mirrored port. Attribution only reads logs and never asks the network, so it stays passive.

#### Pull request checklist

- [ ] `ruff check .` prints `All checks passed!`
- [ ] `pytest -m "not integration" -q` passes on your laptop
- [ ] The pull request title has the form `type: summary (TASK-ID)` and the body says `Closes #<issue number>`
- [ ] No secrets, passwords, email addresses, personal data, or captures from a real network (CLAUDE.md rule 6)
- [ ] Any new dependency has a row in `docs/DEPENDENCIES.md` with its license
- [ ] CI is green and your reviewer approved

### JAK-07: Live sensor: capture, rotation, and shipping to the console

**Due:** Spring S1-S4 (due Fri Feb 12, 2027) · **Milestone:** `S1-S4 Live sensor` · **Needs first:** [JAK-06](#jak-06-build-the-reference-lab-and-prove-the-mirror-works), [JAI-07](jaiden.md#jai-07-the-api-uploads-alerts-events-live-updates-sensor-ingest), [JAK-08](#jak-08-device-attribution-which-device-is-behind-each-ip-address) · **Kind:** code, tested

**Issue labels:** `type:task` `phase:spring` `owner:jakub` `area:sensor` `critical-path` `needs-hardware`

> **Needs hardware.** Steps that use the Raspberry Pi, the switch or other devices were not run during planning; they are marked *not run — verify on hardware*.

#### Goal

Turn the lab into MaxGuard's live sensor (`docs/ARCHITECTURE.md` section 4): Zeek and Suricata run all the time on the capture port and write their logs into one folder per 15-minute interval on the SSD, and a small shipper sends each completed folder to the console's `POST /api/ingest`. The console analyzes it like an upload, with `sensor_id` set to the sensor's name.

#### Prerequisites

JAK-06 (the lab works), JAI-07 (the API with `/api/ingest`) and JAK-08 (which creates `maxguard/sensor/`) are merged.

#### Steps

**Step 1.** Update `main` and create your branch for this task (one branch per task):

```bash
cd ~/projects/maxguard
source .venv/bin/activate
git checkout main && git pull
git checkout -b jakub/live-sensor
```

If `source .venv/bin/activate` fails, you have not made the virtual environment yet: do Week 0 section 0.11 first.

**Step 2.** **Zeek rotation.** Zeek 9 rotates its own logs, without `zeekctl`, when `Log::default_rotation_interval` is set. `Log::rotation_format_func` decides where each closed file goes. Create `maxguard/zeek/scripts/live/rotate.zeek`:

```zeek
##! Live sensor log rotation (Jakub, JAK-07).
##!
##! Zeek writes the logs of the interval in progress into its working folder
##! (/data/spool/zeek in docker/sensor-compose.yaml). At the end of every
##! interval it closes them and moves them into one folder per interval:
##!
##!     /data/zeek/2026-10-06-1415/conn.log, dns.log, http.log, ...
##!
##! The folder is named after the interval's START, in UTC (the container runs
##! with TZ=UTC). The files keep their plain names, so a finished folder is an
##! ordinary Zeek log folder that MaxGuard can analyze or ship as it is.
##!
##! No zeekctl is needed: Zeek 9's logging framework rotates by itself when
##! Log::default_rotation_interval is set, and Log::rotation_format_func decides
##! where each rotated file goes.
##!
##! This file lives in scripts/live/ on purpose: maxguard/zeek/runner.py loads only
##! scripts/*.zeek, so reading a capture file never rotates anything.

module MaxGuardLive;

export {
    ## Where the interval folders are created. It must be on the same disk as
    ## Zeek's working folder: rotation renames files, and a rename cannot move
    ## a file to another disk.
    const archive_dir = "/data/zeek" &redef;
}

# One folder every 15 minutes. The sensor's compose file overrides this from the
# command line (Log::default_rotation_interval=1min for a quick test). Use a whole
# number of minutes that divides 60 (1, 5, 15, 30, 60 ...): Zeek rotates at
# multiples of the interval counted from midnight, and the folder names assume it.
redef Log::default_rotation_interval = 15 min;

# After a crash or a power cut the logs of the unfinished interval are left in
# the working folder. Rotate them into their interval folder at the next start.
redef LogAscii::enable_leftover_log_rotation = T;

## The start of the interval that contains time t, e.g. 14:22:10 -> 14:15:00.
function interval_start(t: time): time
    {
    local seconds = interval_to_double(Log::default_rotation_interval);
    return double_to_time(floor(time_to_double(t) / seconds) * seconds);
    }

## Called by Zeek once for every log file it rotates (conn, dns, http, ...).
function folder_per_interval(ri: Log::RotationFmtInfo): Log::RotationPath
    {
    local start = interval_start(ri$open);
    local dir = fmt("%s/%s", archive_dir, strftime("%Y-%m-%d-%H%M", start));
    local base = ri$path;  # "conn": Zeek adds ".log"

    # Zeek was restarted during this interval, so the folder already has a
    # conn.log from before the restart. Keep both: conn.141502.log is read as
    # conn.log too (maxguard/adapters/zeeklogs.py appends them).
    if ( file_size(fmt("%s/%s.log", dir, base)) >= 0 )
        base = fmt("%s.%s", ri$path, strftime("%H%M%S", ri$open));

    return Log::RotationPath($dir=dir, $file_basename=base);
    }

redef Log::rotation_format_func = folder_per_interval;
```

The folder is named after the interval's **start** in UTC, and the files keep their plain names, so a finished folder is an ordinary Zeek log folder. The script sits in `scripts/live/` on purpose: `maxguard/zeek/runner.py` loads only `scripts/*.zeek`, so analyzing a capture file never rotates anything.

**Step 3.** **Suricata live settings.** Create `maxguard/suricata/maxguard-suricata-live.yaml`, a copy of `maxguard-suricata.yaml` with three changes (Community ID and JA4 are unchanged):

```yaml
%YAML 1.1
---
# MaxGuard's Suricata settings for the LIVE sensor (Jakub, JAK-07).
# A copy of maxguard-suricata.yaml (capture files) with three changes:
#   1. af-packet: listen on the capture port named on the command line
#      (--af-packet=eth0). Listening only: no copy-mode, so Suricata never sends.
#   2. eve-log: a new file every minute, eve-YYYY-MM-DD-HHMM.json (UTC), so the
#      minutes of each interval can be merged into that interval's Zeek folder.
#   3. unix-command off: nothing on the sensor needs Suricata's control socket.
# Community ID and JA4 are exactly as in maxguard-suricata.yaml.
vars:
  address-groups:
    HOME_NET: "[10.0.0.0/8,172.16.0.0/12,192.168.0.0/16,fc00::/7]"
    EXTERNAL_NET: "!$HOME_NET"
  port-groups:
    HTTP_PORTS: "80"
    SHELLCODE_PORTS: "!80"
    ORACLE_PORTS: 1521
    SSH_PORTS: 22
    DNP3_PORTS: 20000
    MODBUS_PORTS: 502
    FILE_DATA_PORTS: "[$HTTP_PORTS,110,143]"
    FTP_PORTS: 21
    GENEVE_PORTS: 6081
    VXLAN_PORTS: 4789
    TEREDO_PORTS: 3544

default-log-dir: /var/log/suricata/

af-packet:
  # "default" applies to whichever interface the command line names, so the
  # same file works for eth0 on a Raspberry Pi and enp1s0 on a mini PC.
  - interface: default
    # Spread the work over all cores, keeping each connection on one thread.
    cluster-id: 99
    cluster-type: cluster_flow
    defrag: yes
    # Never add copy-mode or copy-iface here: they turn Suricata into an inline
    # device that sends packets, and a MaxGuard sensor only listens (CLAUDE.md rule 5).

outputs:
  - eve-log:
      enabled: yes
      filetype: regular
      # A new file each minute, named after the minute it starts in.
      # rotate-interval "minute" (Suricata 8.0 user guide, "Rotate log file").
      filename: eve-%Y-%m-%d-%H%M.json
      rotate-interval: minute
      community-id: yes
      community-id-seed: 0
      types:
        - alert
        - dns
        - http:
            extended: yes
        - tls:
            extended: yes
            ja4: on
        - dhcp:
            enabled: yes
        - flow

app-layer:
  protocols:
    tls:
      enabled: yes
      detection-ports:
        dp: 443
      ja4-fingerprints: yes
    http:
      enabled: yes
    dns:
      tcp:
        enabled: yes
      udp:
        enabled: yes
    dhcp:
      enabled: yes

unix-command:
  enabled: no

logging:
  default-log-level: notice
  outputs:
    - console:
        enabled: yes
```

Why a file per **minute** and not per 15 minutes: Suricata 8.0's `rotate-interval` accepts `minute`, `hour` and `day`, which start at the next whole minute, hour or day, or a relative value such as `15m`, which counts from the moment Suricata started (user guide, "Rotate log file"; source: `src/util-logopenfile.c`). A relative 15 minutes would not line up with Zeek's folders, so Suricata writes minute files and the adapter merges each interval's minutes into that interval's folder. Never add `copy-mode` to the `af-packet` section: it turns Suricata into an inline device that sends packets (CLAUDE.md rule 5).

**Step 4.** **Compose file.** Create `docker/sensor-compose.yaml`:

```yaml
# MaxGuard live sensor (Jakub, JAK-07): Zeek and Suricata listen on the capture
# port, and the shipper sends each finished interval folder to the console.
#
# Start:  docker compose -f docker/sensor-compose.yaml up -d
# Check:  docker compose -f docker/sensor-compose.yaml ps
# Stop:   docker compose -f docker/sensor-compose.yaml down   (the logs in /data stay)
#
# Before the first start (docs/HARDWARE.md sections 8-10): the capture port is up
# with NO IP address, the SSD is mounted at /data, and /data/shipper.toml holds
# the console's address and token (never put them in this repository).
#
# Settings: export them before "docker compose", or put them in docker/.env.
#   MAXGUARD_CAPTURE_IFACE     the capture port (default eth0)
#   MAXGUARD_INTERVAL_MINUTES  minutes per log folder (default 15; 1 for a quick test)
#   MAXGUARD_SENSOR_DATA       the data folder on the SSD (default /data)
#
# Layout on the SSD:
#   /data/zeek/<YYYY-MM-DD-HHMM>/   one finished folder per interval (UTC start time)
#   /data/spool/zeek/               Zeek's logs of the interval in progress
#   /data/spool/suricata/           Suricata's eve-<YYYY-MM-DD-HHMM>.json, one per minute
#   /data/shipper.toml              where the shipper sends the folders
#
# The containers use host networking so they see the real capture port. They
# only listen: the capture port has no IP address, and nothing here sends
# packets on it (CLAUDE.md rule 5). The shipper's uploads leave through the
# management port, the only port with an address.
name: maxguard-sensor

services:
  zeek:
    image: zeek/zeek:9.0.0
    network_mode: host
    cap_drop: [ALL]
    cap_add:
      - NET_RAW     # read packets from the capture port
      - NET_ADMIN   # switch the port to promiscuous mode
    security_opt: [no-new-privileges:true]
    environment:
      TZ: UTC       # rotation times and folder names are in UTC
    # Zeek writes the interval in progress here; rotate.zeek moves each finished
    # interval to /data/zeek/<YYYY-MM-DD-HHMM>/. Same disk, so moving is a rename.
    working_dir: /data/spool/zeek
    volumes:
      - ${MAXGUARD_SENSOR_DATA:-/data}:/data
      - ../maxguard:/opt/maxguard/maxguard:ro
    # The same scripts as maxguard/zeek/runner.py (site.zeek: Zeek's "local" policy
    # without its DNS lookups), plus live/rotate.zeek.
    # No -D: a live sensor keeps Zeek's random seeds (docs/ARCHITECTURE.md section 7).
    command: >-
      zeek -i ${MAXGUARD_CAPTURE_IFACE:-eth0} -C
      LogAscii::use_json=T
      Log::default_rotation_interval=${MAXGUARD_INTERVAL_MINUTES:-15}min
      /opt/maxguard/maxguard/zeek/site.zeek
      policy/protocols/conn/community-id-logging
      /opt/maxguard/maxguard/zeek/scripts/cleartext.zeek
      /opt/maxguard/maxguard/zeek/scripts/inventory.zeek
      /opt/maxguard/maxguard/zeek/scripts/live/rotate.zeek
    restart: unless-stopped

  suricata:
    image: jasonish/suricata:8.0.7
    network_mode: host
    cap_drop: [ALL]
    cap_add:
      # What Suricata needs to capture (Suricata user guide, "Packet capture"):
      - NET_ADMIN
      - NET_RAW
      - SYS_NICE
      # Only for starting up: the image's start script gives /var/log/suricata to
      # the "suricata" user, and Suricata then switches to that user. From then
      # on the running process holds only the three capabilities above.
      - CHOWN
      - DAC_OVERRIDE
      - SETUID
      - SETGID
      - SETPCAP
    security_opt: [no-new-privileges:true]
    environment:
      TZ: UTC       # the minute in each eve-<YYYY-MM-DD-HHMM>.json name is UTC
    volumes:
      - ${MAXGUARD_SENSOR_DATA:-/data}/spool/suricata:/var/log/suricata
      - ../maxguard:/opt/maxguard/maxguard:ro
    # Only MaxGuard's own rules file: Suricata starts in about a second. A large
    # rule set takes much longer to load (about 50 s for ET Open on a 4-core x86
    # machine), and Suricata captures nothing until it has finished.
    command: >-
      -c /opt/maxguard/maxguard/suricata/maxguard-suricata-live.yaml
      --af-packet=${MAXGUARD_CAPTURE_IFACE:-eth0}
      -S /opt/maxguard/maxguard/suricata/rules/maxguard.rules
    restart: unless-stopped

  shipper:
    # Used only for its Python 3.13: the shipper needs nothing but the standard library.
    image: zeek/zeek:9.0.0
    network_mode: host   # reaches the console through the management port
    cap_drop: [ALL]
    cap_add:
      - DAC_OVERRIDE     # delete Suricata's minute files, which belong to the "suricata" user
    security_opt: [no-new-privileges:true]
    environment:
      TZ: UTC
      PYTHONPATH: /opt/maxguard
      PYTHONDONTWRITEBYTECODE: "1"   # the code folder is mounted read-only
    volumes:
      - ${MAXGUARD_SENSOR_DATA:-/data}:/data
      - ../maxguard:/opt/maxguard/maxguard:ro
    command: >-
      python3 -m maxguard.sensor.shipper --data /data
      --interval-minutes ${MAXGUARD_INTERVAL_MINUTES:-15}
    restart: unless-stopped
```

Zeek runs **without `-D`**: random seeds protect a live sensor's tables against deliberate slow-down attacks. Every service drops all capabilities and adds back only what it needs. Suricata needs five more than `NET_ADMIN`, `NET_RAW` and `SYS_NICE` only while it starts: the image's start script hands its folders (such as `/var/log/suricata`) to the `suricata` user, and Suricata then switches to that user. The shipper uses the `zeek/zeek` image only for its Python 3: it needs nothing outside the standard library. Check the file:

```bash
docker compose -f docker/sensor-compose.yaml config --quiet && echo "compose file OK"
```

Expected output:

```text
compose file OK
```

**Step 5.** **Adapter.** Create `maxguard/adapters/live.py` with `LiveSensorAdapter` (Contract 3, unchanged):

```python
"""LiveSensorAdapter: the newest finished interval of a live sensor (Jakub, JAK-07).

The live sensor (docker/sensor-compose.yaml) keeps everything in one data
folder, /data on the sensor's SSD:

    /data/zeek/2026-10-06-1415/   one folder per interval, named after its start
                                  in UTC (maxguard/zeek/scripts/live/rotate.zeek)
    /data/spool/zeek/             Zeek's logs of the interval in progress
    /data/spool/suricata/         Suricata's events, one file per minute:
                                  eve-2026-10-06-1415.json, eve-2026-10-06-1416.json, ...

An interval folder is *complete* when its interval has ended and SETTLE_SECONDS
more have passed. By then Zeek has moved every log into it, and Suricata has
closed the last minute file that belongs to it. merge_eve() then joins that
interval's minute files into one eve.json inside the folder, so the folder
holds everything MaxGuard needs, like a folder made from a capture file.

The shipper (maxguard/sensor/shipper.py) uses the same functions before it
sends a folder to the console. This module uses only Python's standard library,
because the shipper runs in the zeek/zeek:9.0.0 image with nothing installed.
"""

from __future__ import annotations

import os
import re
import shutil
import tempfile
import time
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path

from maxguard.adapters.zeeklogs import ZeekLogAdapter

ZEEK_DIR = Path("zeek")                 # inside the data folder
EVE_DIR = Path("spool") / "suricata"    # inside the data folder
FOLDER_FORMAT = "%Y-%m-%d-%H%M"         # 2026-10-06-1415, always UTC
FOLDER_NAME = re.compile(r"\d{4}-\d{2}-\d{2}-\d{4}")
EVE_PART_NAME = re.compile(r"eve-(\d{4}-\d{2}-\d{2}-\d{4})\.json")
DEFAULT_INTERVAL_MINUTES = 15
# Suricata starts a new minute file with the first event after the minute ends,
# so the last minute file of an interval can still grow for up to a minute after
# the interval ends. Two minutes covers that, plus Zeek moving its logs.
SETTLE_SECONDS = 120


class NoCompletedInterval(RuntimeError):
    """The sensor has not finished any interval yet."""


def check_interval(minutes: int) -> int:
    """The interval must divide an hour evenly, like Zeek's rotation times do."""
    if minutes < 1 or 60 % minutes != 0:
        raise ValueError(f"interval must be 1, 2, 3, 4, 5, 6, 10, 12, 15, 20, 30 or 60 "
                         f"minutes, got {minutes}")
    return minutes


def interval_minutes_from_env() -> int:
    """MAXGUARD_INTERVAL_MINUTES (default 15): the same value Zeek rotates with."""
    text = os.environ.get("MAXGUARD_INTERVAL_MINUTES", str(DEFAULT_INTERVAL_MINUTES))
    if not text.isdigit():
        raise ValueError(f"MAXGUARD_INTERVAL_MINUTES must be a whole number, got {text!r}")
    return check_interval(int(text))


def folder_start(name: str) -> float:
    """'2026-10-06-1415' -> the Unix time of 14:15:00 UTC on that day."""
    return datetime.strptime(name, FOLDER_FORMAT).replace(tzinfo=UTC).timestamp()


def folder_name(start: float) -> str:
    """The opposite of folder_start(): a Unix time -> '2026-10-06-1415'."""
    return datetime.fromtimestamp(start, UTC).strftime(FOLDER_FORMAT)


def interval_folders(zeek_dir: Path) -> list[Path]:
    """Every interval folder, oldest first (the names sort in time order)."""
    if not zeek_dir.is_dir():
        return []
    return sorted(p for p in zeek_dir.iterdir() if p.is_dir() and FOLDER_NAME.fullmatch(p.name))


def is_complete(folder: Path, now: float, interval_minutes: int) -> bool:
    """True once the folder's interval ended at least SETTLE_SECONDS before now."""
    end = folder_start(folder.name) + interval_minutes * 60
    return now >= end + SETTLE_SECONDS


def completed_folders(zeek_dir: Path, now: float, interval_minutes: int) -> list[Path]:
    """The interval folders that are complete, oldest first."""
    return [f for f in interval_folders(zeek_dir) if is_complete(f, now, interval_minutes)]


def part_start(part: Path) -> float | None:
    """'eve-2026-10-06-1416.json' -> the Unix time of 14:16 UTC; None for other files."""
    match = EVE_PART_NAME.fullmatch(part.name)
    return folder_start(match.group(1)) if match else None


def eve_parts(eve_dir: Path, folder: Path, interval_minutes: int) -> list[Path]:
    """Suricata's minute files whose minute lies inside the folder's interval, in order."""
    start = folder_start(folder.name)
    end = start + interval_minutes * 60
    if not eve_dir.is_dir():
        return []
    parts = []
    for path in sorted(eve_dir.iterdir()):  # the names sort in time order
        minute = part_start(path)
        if minute is not None and start <= minute < end:
            parts.append(path)
    return parts


def merge_eve(folder: Path, eve_dir: Path, interval_minutes: int) -> None:
    """Join the interval's minute files into folder/eve.json, then delete them.

    Call it only for a complete folder. It is safe to run again after a crash:
    eve.json appears in one step (written to a hidden file first, then renamed),
    and once it exists it is never written again, so no event is added twice.
    """
    parts = eve_parts(eve_dir, folder, interval_minutes)
    target = folder / "eve.json"
    if parts and not target.exists():
        # Hidden (starts with "."), so nothing reads or ships a half-written file.
        with tempfile.NamedTemporaryFile(dir=folder, prefix=".eve-", suffix=".partial",
                                         delete=False) as out:
            for part in parts:
                with part.open("rb") as src:
                    shutil.copyfileobj(src, out)
        os.chmod(out.name, 0o644)  # readable by every user, like Zeek's own logs
        Path(out.name).replace(target)  # a rename on one disk is all-or-nothing
    for part in parts:  # merged now, or on an earlier run that stopped halfway
        part.unlink(missing_ok=True)


class LiveSensorAdapter:
    """Contract 3 adapter for a live sensor's data folder (for example /data).

    accepts() is true only for a folder that has zeek/<YYYY-MM-DD-HHMM>/ folders
    inside and no conn.log of its own, so it never takes a plain Zeek log folder
    away from ZeekLogAdapter (and ZeekLogAdapter never takes a sensor folder).
    """

    name = "live"

    def __init__(self, interval_minutes: int | None = None,
                 clock: Callable[[], float] = time.time) -> None:
        # None: read MAXGUARD_INTERVAL_MINUTES when a folder is analyzed, not here.
        # pipeline.py makes this adapter at import time, and a wrong setting must
        # not stop MaxGuard from analyzing uploads.
        self._interval_minutes = None if interval_minutes is None else check_interval(
            interval_minutes)
        self.clock = clock  # tests pass a fixed time; on a sensor it is the real clock

    @property
    def interval_minutes(self) -> int:
        if self._interval_minutes is None:
            return interval_minutes_from_env()
        return self._interval_minutes

    def accepts(self, path: Path) -> bool:
        if not path.is_dir() or (path / "conn.log").exists():
            return False
        return bool(interval_folders(path / ZEEK_DIR))

    def to_zeek_logs(self, path: Path, workdir: Path) -> Path:
        """Copy the newest complete interval (never the one still being written)."""
        done = completed_folders(path / ZEEK_DIR, self.clock(), self.interval_minutes)
        if not done:
            raise NoCompletedInterval(
                f"{path / ZEEK_DIR}: no interval has finished yet; the first one is complete "
                f"{self.interval_minutes} minutes plus {SETTLE_SECONDS} seconds after the "
                "sensor starts")
        newest = done[-1]
        merge_eve(newest, path / EVE_DIR, self.interval_minutes)
        # From here on it is an ordinary folder of Zeek logs plus eve.json. ZeekLogAdapter
        # copies it into workdir and joins conn.log with conn.<time>.log after a restart.
        return ZeekLogAdapter().to_zeek_logs(newest, workdir)
```

A folder is *complete* two minutes after its interval ends: by then Zeek has moved every log into it and Suricata has closed the last minute file that belongs to it. `merge_eve()` writes `eve.json` under a hidden name first and renames it, so a crash halfway never leaves a half-merged file. The adapter reads `MAXGUARD_INTERVAL_MINUTES` only when it analyzes a folder, because `pipeline.py` creates it when it is imported, and a wrong setting must not stop MaxGuard from analyzing uploads.

**Step 6.** Add it to `ADAPTERS` in `maxguard/pipeline.py` (two lines change):

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
        "events": events,
        "ai": ai,
    }
```

**Step 7.** Add one line to the docstring of `maxguard/sensor/__init__.py`:

```python
"""Sensor-side helpers (Jakub).

attribution.py  device table: which MAC / host name / DNS names belong to each IP
shipper.py      sends each finished interval folder of the live sensor to the console
"""
```

**Step 8.** **Shipper.** Create `maxguard/sensor/shipper.py`:

```python
"""Send each finished interval folder of a live sensor to the console (Jakub, JAK-07).

It runs on the sensor, in its own container (docker/sensor-compose.yaml):

    python3 -m maxguard.sensor.shipper --data /data --interval-minutes 15

Every minute it:
1. finds the interval folders under /data/zeek that are complete and not shipped
   yet, oldest first (maxguard/adapters/live.py decides what "complete" means);
2. merges that interval's Suricata minute files into the folder's eve.json;
3. packs the folder as a .tar.gz and POSTs it to <console>/api/ingest with the
   header "Authorization: Bearer <token>" and the form field sensor_id;
4. marks the folder shipped (a hidden ".shipped" file) only after a 2xx answer.
   After any failure it stops and tries again on the next round, so a console
   that is down only delays folders, and a shipped folder is never sent again;
5. deletes shipped folders whose interval started more than 7 days ago.

The console's address and token come from /data/shipper.toml on the sensor,
never from the repository (CLAUDE.md rule 6). Shipping is the sensor's only
network traffic: it goes out of the management port, only to the console the
user configured, and never through a proxy (CLAUDE.md rules 1 and 5).

Only main() reads the clock; every other function takes `now` (Unix seconds),
so the tests can say exactly which folders are ready. Like live.py, this module
uses only Python's standard library.
"""

from __future__ import annotations

import argparse
import gzip
import http.client
import io
import logging
import re
import secrets
import shutil
import ssl
import tarfile
import time
import tomllib
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from maxguard.adapters.live import (
    EVE_DIR,
    ZEEK_DIR,
    check_interval,
    completed_folders,
    folder_start,
    interval_folders,
    interval_minutes_from_env,
    merge_eve,
    part_start,
)

CONFIG_NAME = "shipper.toml"   # in the data folder, e.g. /data/shipper.toml
SHIPPED_MARKER = ".shipped"    # hidden, so it is never packed
KEEP_DAYS = 7                  # ARCHITECTURE.md section 4: 7 days on the sensor
LOOP_SECONDS = 60
# The console analyzes the folder before it answers, and explaining the findings
# with a local AI model can take minutes on a small machine.
POST_TIMEOUT_SECONDS = 900
SENSOR_ID = re.compile(r"[A-Za-z0-9._-]{1,64}")  # exactly what POST /api/ingest accepts

log = logging.getLogger("maxguard.shipper")


class ConfigError(ValueError):
    """shipper.toml is missing a setting or has a wrong one."""


@dataclass(frozen=True)
class ShipperConfig:
    console_url: str             # "http://192.168.50.20:8001", no trailing slash
    token: str                   # the console's MAXGUARD_INGEST_TOKEN
    sensor_id: str               # this sensor's name, e.g. "sensor-01"
    ca_file: str | None = None   # only for an https:// console with its own certificate


def load_config(path: Path) -> ShipperConfig:
    """Read shipper.toml (TOML: one `key = "value"` per line, # starts a comment)."""
    with path.open("rb") as f:
        raw = tomllib.load(f)
    url = str(raw.get("console_url", "")).rstrip("/")
    if not url.startswith(("http://", "https://")):
        raise ConfigError(f"{path}: console_url must start with http:// or https://")
    token = str(raw.get("token", ""))
    if not token:
        raise ConfigError(f"{path}: token is empty; copy the console's MAXGUARD_INGEST_TOKEN")
    sensor_id = str(raw.get("sensor_id", ""))
    if not SENSOR_ID.fullmatch(sensor_id):
        raise ConfigError(f"{path}: sensor_id must be 1-64 letters, digits, '.', '_' or '-'")
    ca_file = raw.get("ca_file")
    return ShipperConfig(url, token, sensor_id, str(ca_file) if ca_file else None)


# ---------- which folders, and remembering what was shipped ----------

def is_shipped(folder: Path) -> bool:
    return (folder / SHIPPED_MARKER).exists()


def mark_shipped(folder: Path, now: float) -> None:
    """Remember that the console accepted this folder (and when, for people)."""
    (folder / SHIPPED_MARKER).write_text(f"{now:.0f}\n")


def folders_to_ship(data_dir: Path, now: float, interval_minutes: int) -> list[Path]:
    """Complete folders the console has not accepted yet, oldest first."""
    done = completed_folders(data_dir / ZEEK_DIR, now, interval_minutes)
    return [folder for folder in done if not is_shipped(folder)]


# ---------- packing and sending ----------

def without_owner(info: tarfile.TarInfo) -> tarfile.TarInfo:
    """Leave the sensor's user and group names out of the archive."""
    info.uid = info.gid = 0
    info.uname = info.gname = ""
    return info


def pack_folder(folder: Path) -> bytes:
    """The folder as .tar.gz bytes (2026-10-06-1415/conn.log, ...), hidden files left out.

    Packing the same folder twice gives the same bytes (sorted names, no owner,
    gzip time 0). If the sensor crashes after sending but before writing
    .shipped, the folder is sent again, and the console sees the same SHA-256
    and does not count its alerts twice.
    """
    buffer = io.BytesIO()
    with gzip.GzipFile(fileobj=buffer, mode="wb", mtime=0) as gz:
        with tarfile.open(fileobj=gz, mode="w") as tar:
            for path in sorted(folder.iterdir()):
                if path.is_file() and not path.name.startswith("."):
                    tar.add(path, arcname=f"{folder.name}/{path.name}", filter=without_owner)
    return buffer.getvalue()


def multipart_body(fields: dict[str, str], file_name: str, data: bytes,
                   boundary: str) -> bytes:
    """Text fields plus one file as multipart/form-data (RFC 7578), the format a
    browser uses to upload a file, and the one the console's /api/ingest reads."""
    text = ""
    for name, value in fields.items():
        text += (f"--{boundary}\r\n"
                 f'Content-Disposition: form-data; name="{name}"\r\n\r\n'
                 f"{value}\r\n")
    text += (f"--{boundary}\r\n"
             f'Content-Disposition: form-data; name="file"; filename="{file_name}"\r\n'
             "Content-Type: application/gzip\r\n\r\n")
    return text.encode() + data + f"\r\n--{boundary}--\r\n".encode()


def opener(config: ShipperConfig) -> urllib.request.OpenerDirector:
    """An HTTP client that never uses a proxy: the logs and the token go straight
    to the console. https:// checks the certificate (with ca_file when given)."""
    context = ssl.create_default_context(cafile=config.ca_file)
    return urllib.request.build_opener(urllib.request.ProxyHandler({}),
                                       urllib.request.HTTPSHandler(context=context))


def post_archive(config: ShipperConfig, file_name: str, data: bytes,
                 timeout: float = POST_TIMEOUT_SECONDS) -> int:
    """POST one archive to <console>/api/ingest and return the HTTP status code.

    A console that cannot be reached raises OSError (connection refused, timeout)."""
    boundary = secrets.token_hex(16)
    request = urllib.request.Request(
        config.console_url + "/api/ingest", method="POST",
        data=multipart_body({"sensor_id": config.sensor_id}, file_name, data, boundary),
        headers={"Authorization": f"Bearer {config.token}",
                 "Content-Type": f"multipart/form-data; boundary={boundary}"})
    try:
        with opener(config).open(request, timeout=timeout) as response:
            return response.status
    except urllib.error.HTTPError as err:  # the console answered, with 4xx or 5xx
        err.close()
        return err.code


def ship_folder(folder: Path, data_dir: Path, config: ShipperConfig,
                interval_minutes: int, now: float) -> bool:
    """Merge, pack, send and mark one folder. True when the console answered 2xx."""
    merge_eve(folder, data_dir / EVE_DIR, interval_minutes)
    data = pack_folder(folder)
    try:
        status = post_archive(config, f"{folder.name}.tar.gz", data)
    except (OSError, http.client.HTTPException) as err:
        log.warning("%s: console not reachable (%s); will retry", folder.name, err)
        return False
    if not 200 <= status < 300:
        log.warning("%s: console answered HTTP %d; will retry", folder.name, status)
        return False
    mark_shipped(folder, now)
    log.info("%s: shipped (%d bytes, HTTP %d)", folder.name, len(data), status)
    return True


def ship_ready_folders(data_dir: Path, config: ShipperConfig, interval_minutes: int,
                       now: float) -> list[str]:
    """Ship every ready folder, oldest first; stop at the first failure."""
    shipped = []
    for folder in folders_to_ship(data_dir, now, interval_minutes):
        if not ship_folder(folder, data_dir, config, interval_minutes, now):
            break  # the console is down or refusing: keep the order, retry next round
        shipped.append(folder.name)
    return shipped


# ---------- retention ----------

def prune(data_dir: Path, now: float, keep_days: int = KEEP_DAYS) -> list[str]:
    """Delete shipped folders, and leftover Suricata minute files, older than keep_days.

    A folder that was never shipped is kept, so a console that was down for a
    week loses nothing; watch the disk if a sensor has no console."""
    cutoff = now - keep_days * 86400
    deleted = []
    for folder in interval_folders(data_dir / ZEEK_DIR):
        if is_shipped(folder) and folder_start(folder.name) < cutoff:
            shutil.rmtree(folder)
            deleted.append(folder.name)
    eve_dir = data_dir / EVE_DIR
    if eve_dir.is_dir():
        for part in sorted(eve_dir.iterdir()):
            minute = part_start(part)
            if minute is not None and minute < cutoff:  # no Zeek folder ever claimed it
                part.unlink()
                deleted.append(part.name)
    return deleted


# ---------- one round, and the loop ----------

def run_once(data_dir: Path, interval_minutes: int, now: float) -> dict:
    """Ship what is ready, then delete what is old. Returns what happened."""
    shipped: list[str] = []
    config_path = data_dir / CONFIG_NAME
    try:
        config = load_config(config_path)
    except FileNotFoundError:
        log.warning("%s not found: folders stay on the sensor until it exists", config_path)
    except (ConfigError, tomllib.TOMLDecodeError) as err:
        log.error("%s", err)
    else:
        shipped = ship_ready_folders(data_dir, config, interval_minutes, now)
    return {"shipped": shipped, "deleted": prune(data_dir, now)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Send finished interval folders to the MaxGuard console.")
    parser.add_argument("--data", type=Path, default=Path("/data"),
                        help="the sensor's data folder (default: /data)")
    parser.add_argument("--interval-minutes", type=int, default=None,
                        help="the same interval Zeek rotates with "
                             "(default: $MAXGUARD_INTERVAL_MINUTES, else 15)")
    parser.add_argument("--once", action="store_true", help="run one round, then exit")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    if args.interval_minutes is None:
        interval = interval_minutes_from_env()
    else:
        interval = check_interval(args.interval_minutes)
    log.info("shipping complete %d-minute folders from %s", interval, args.data / ZEEK_DIR)
    while True:
        run_once(args.data, interval, now=time.time())  # the only place that reads the clock
        if args.once:
            return 0
        time.sleep(LOOP_SECONDS)


if __name__ == "__main__":
    raise SystemExit(main())
```

Three choices to notice. It marks a folder shipped only after a `2xx` answer and stops at the first failure, so a console that is down only delays folders. It packs the same folder into the same bytes every time, so if the sensor crashes between sending and marking, the console sees the same SHA-256 and does not count the alerts twice. And it never uses a proxy: the token and the logs go straight to the console the user configured.

**Step 9.** **Tests.** Create `tests/unit/test_live_adapter.py`:

```python
"""LiveSensorAdapter tests (Jakub, JAK-07): pick the newest finished interval, never
the one still being written, and merge Suricata's minute files into it.

No Zeek, Suricata or Docker: each test builds a small sensor data folder by hand,
the way docker/sensor-compose.yaml lays it out, from the plain_http_alt fixture.
"""

import shutil
from pathlib import Path

import pytest

from maxguard import pipeline
from maxguard.adapters.base import read_log
from maxguard.adapters.live import (
    SETTLE_SECONDS,
    LiveSensorAdapter,
    NoCompletedInterval,
    check_interval,
    eve_parts,
    folder_name,
    folder_start,
    interval_minutes_from_env,
    merge_eve,
)
from maxguard.adapters.pcap import PcapAdapter
from maxguard.adapters.zeeklogs import ZeekLogAdapter

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "zeek" / "plain_http_alt"

# The sensor below has three 15-minute folders: 14:00, 14:15 and 14:30 (UTC).
# At NOW the 14:30 interval has ended (14:45) but is still settling until 14:47.
NOW = folder_start("2026-10-06-1430") + 15 * 60 + 60   # 14:46:00 UTC


def write_lines(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(line + "\n" for line in lines))


def make_sensor(root: Path) -> Path:
    """A sensor data folder: three interval folders and Suricata minute files."""
    zeek = root / "zeek"
    for name in ("2026-10-06-1400", "2026-10-06-1430"):
        write_lines(zeek / name / "conn.log", [f'{{"note": "conn from {name}"}}'])
    shutil.copytree(FIXTURE, zeek / "2026-10-06-1415", ignore=shutil.ignore_patterns("eve.json"))
    # The fixture's two Suricata events, as if written in minutes 14:15 and 14:22.
    eve_lines = (FIXTURE / "eve.json").read_text().splitlines()
    spool = root / "spool" / "suricata"
    write_lines(spool / "eve-2026-10-06-1415.json", eve_lines[:1])
    write_lines(spool / "eve-2026-10-06-1422.json", eve_lines[1:])
    write_lines(spool / "eve-2026-10-06-1430.json", ['{"event_type": "flow", "minute": "14:30"}'])
    write_lines(root / "spool" / "zeek" / "conn.log", ['{"note": "interval in progress"}'])
    return root


def adapter_at(now: float) -> LiveSensorAdapter:
    return LiveSensorAdapter(interval_minutes=15, clock=lambda: now)


# ---- folder names are UTC times -------------------------------------------------

def test_folder_names_are_utc_interval_starts():
    assert folder_start("2026-10-06-1415") == 1791296100.0   # 14:15:00 UTC
    assert folder_name(1791296100.0) == "2026-10-06-1415"


@pytest.mark.parametrize("minutes", [1, 5, 15, 30, 60])
def test_intervals_that_divide_an_hour_are_allowed(minutes):
    assert check_interval(minutes) == minutes


@pytest.mark.parametrize("minutes", [0, 7, 45, 90])
def test_other_intervals_are_refused(minutes):
    with pytest.raises(ValueError):
        check_interval(minutes)


def test_interval_comes_from_the_environment(monkeypatch):
    monkeypatch.delenv("MAXGUARD_INTERVAL_MINUTES", raising=False)
    assert interval_minutes_from_env() == 15
    monkeypatch.setenv("MAXGUARD_INTERVAL_MINUTES", "1")
    assert interval_minutes_from_env() == 1
    assert LiveSensorAdapter().interval_minutes == 1


def test_a_wrong_interval_setting_does_not_stop_the_pipeline_from_loading(monkeypatch):
    # pipeline.py builds the adapter when it is imported; the setting is read later.
    monkeypatch.setenv("MAXGUARD_INTERVAL_MINUTES", "7")
    adapter = LiveSensorAdapter()
    with pytest.raises(ValueError, match="interval must be"):
        _ = adapter.interval_minutes


# ---- accepts(): a sensor folder, and nothing ZeekLogAdapter accepts ------------------

def test_accepts_a_sensor_data_folder(tmp_path):
    root = make_sensor(tmp_path)
    assert adapter_at(NOW).accepts(root)
    assert not ZeekLogAdapter().accepts(root)   # no conn.log at the top
    assert not PcapAdapter().accepts(root)


def test_never_takes_a_plain_zeek_log_folder(tmp_path):
    assert not adapter_at(NOW).accepts(FIXTURE)          # conn.log at the top
    root = make_sensor(tmp_path)
    (root / "conn.log").write_text("{}\n")
    assert not adapter_at(NOW).accepts(root)             # conn.log wins, even here
    assert ZeekLogAdapter().accepts(root)


def test_refuses_folders_without_interval_folders(tmp_path):
    (tmp_path / "zeek" / "not-an-interval").mkdir(parents=True)
    assert not adapter_at(NOW).accepts(tmp_path)
    assert not adapter_at(NOW).accepts(tmp_path / "missing")
    assert not adapter_at(NOW).accepts(FIXTURE / "conn.log")   # a file


# ---- to_zeek_logs(): newest complete folder, eve.json merged in ----------------------

def test_picks_the_newest_complete_folder_not_the_one_being_written(tmp_path):
    root = make_sensor(tmp_path)
    log_dir = adapter_at(NOW).to_zeek_logs(root, tmp_path / "work")

    # 14:15 was picked: its conn.log is the fixture's, not 14:30's or 14:00's.
    assert list(read_log(log_dir, "conn.log")) == list(read_log(FIXTURE, "conn.log"))
    assert list(read_log(log_dir, "http.log")) == list(read_log(FIXTURE, "http.log"))
    # Its two Suricata minutes were merged in, in time order; 14:30's minute was not.
    assert list(read_log(log_dir, "eve.json")) == list(read_log(FIXTURE, "eve.json"))


def test_the_current_folder_is_used_once_it_has_settled(tmp_path):
    root = make_sensor(tmp_path)
    settled = folder_start("2026-10-06-1430") + 15 * 60 + SETTLE_SECONDS   # 14:47:00
    log_dir = adapter_at(settled).to_zeek_logs(root, tmp_path / "work")
    assert list(read_log(log_dir, "conn.log")) == [{"note": "conn from 2026-10-06-1430"}]
    assert list(read_log(log_dir, "eve.json")) == [{"event_type": "flow", "minute": "14:30"}]


def test_one_second_before_settling_the_folder_is_not_used(tmp_path):
    root = make_sensor(tmp_path)
    almost = folder_start("2026-10-06-1430") + 15 * 60 + SETTLE_SECONDS - 1
    log_dir = adapter_at(almost).to_zeek_logs(root, tmp_path / "work")
    assert list(read_log(log_dir, "conn.log")) == list(read_log(FIXTURE, "conn.log"))


def test_no_complete_folder_yet_is_a_clear_error(tmp_path):
    root = make_sensor(tmp_path)
    too_early = folder_start("2026-10-06-1400") + 60
    with pytest.raises(NoCompletedInterval, match="no interval has finished yet"):
        adapter_at(too_early).to_zeek_logs(root, tmp_path / "work")


def test_logs_from_before_a_zeek_restart_are_kept(tmp_path):
    root = make_sensor(tmp_path)
    folder = root / "zeek" / "2026-10-06-1415"
    write_lines(folder / "conn.141502.log", ['{"note": "after the restart"}'])
    log_dir = adapter_at(NOW).to_zeek_logs(root, tmp_path / "work")
    notes = [rec.get("note") for rec in read_log(log_dir, "conn.log")]
    assert notes.count("after the restart") == 1
    assert len(notes) == 2   # the fixture's connection plus the one after the restart


# ---- merge_eve(): the minute files of one interval ------------------------------------

def test_merge_moves_exactly_the_intervals_minutes(tmp_path):
    root = make_sensor(tmp_path)
    folder, spool = root / "zeek" / "2026-10-06-1415", root / "spool" / "suricata"
    assert [p.name for p in eve_parts(spool, folder, 15)] == [
        "eve-2026-10-06-1415.json", "eve-2026-10-06-1422.json"]

    merge_eve(folder, spool, 15)

    assert (folder / "eve.json").read_text() == (FIXTURE / "eve.json").read_text()
    assert sorted(p.name for p in spool.iterdir()) == ["eve-2026-10-06-1430.json"]
    assert not list(folder.glob(".eve-*"))   # no temporary file left behind


def test_merge_twice_adds_nothing(tmp_path):
    root = make_sensor(tmp_path)
    folder, spool = root / "zeek" / "2026-10-06-1415", root / "spool" / "suricata"
    merge_eve(folder, spool, 15)
    merge_eve(folder, spool, 15)
    assert (folder / "eve.json").read_text() == (FIXTURE / "eve.json").read_text()


def test_merge_after_a_crash_deletes_the_leftovers_without_adding_them_again(tmp_path):
    root = make_sensor(tmp_path)
    folder, spool = root / "zeek" / "2026-10-06-1415", root / "spool" / "suricata"
    merge_eve(folder, spool, 15)
    # A crash after eve.json was written but before the minute files were deleted:
    write_lines(spool / "eve-2026-10-06-1415.json", ['{"event_type": "flow"}'])
    merge_eve(folder, spool, 15)
    assert (folder / "eve.json").read_text() == (FIXTURE / "eve.json").read_text()
    assert not (spool / "eve-2026-10-06-1415.json").exists()


def test_a_folder_without_suricata_minutes_gets_no_eve_json(tmp_path):
    root = make_sensor(tmp_path)
    folder = root / "zeek" / "2026-10-06-1400"
    merge_eve(folder, root / "spool" / "suricata", 15)
    assert not (folder / "eve.json").exists()


# ---- the whole pipeline on a sensor folder --------------------------------------------

def test_pipeline_analyzes_the_newest_complete_interval(tmp_path, monkeypatch):
    root = make_sensor(tmp_path)
    live = adapter_at(NOW)
    monkeypatch.setattr(pipeline, "ADAPTERS", [PcapAdapter(), ZeekLogAdapter(), live])

    report = pipeline.analyze(root, tmp_path / "work", explain=False, sensor_id="lab-sensor")

    assert report["input"]["adapter"] == "live"
    assert [f["rule_id"] for f in report["findings"]] == ["cleartext.http_alt"]
    assert report["events"]
    assert {e["sensor_id"] for e in report["events"]} == {"lab-sensor"}
    assert report["tools"]["suricata"] is True   # eve.json was merged in
```

and `tests/unit/test_shipper.py` (a fake console: `http.server` in a thread on `127.0.0.1`):

```python
"""Shipper tests (Jakub, JAK-07): the right file with the right header, retries after a
failure, never twice, and 7-day retention.

The console is faked with Python's http.server in a thread on 127.0.0.1, so the
shipper's real HTTP code runs, and nothing leaves this computer. Every function
gets `now` from the test, so which folders are ready is exact.
"""

import io
import re
import socket
import tarfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

from maxguard.adapters.live import folder_start
from maxguard.sensor.shipper import (
    SHIPPED_MARKER,
    ConfigError,
    is_shipped,
    load_config,
    main,
    pack_folder,
    prune,
    run_once,
)

TOKEN = "fake-token-for-tests-0123456789abcdef"   # not a secret: only the fake console knows it
FOLDERS = ("2026-10-06-1400", "2026-10-06-1415", "2026-10-06-1430")
# 14:46 UTC: 14:00 and 14:15 are complete; 14:30 ended at 14:45 and is still settling.
NOW = folder_start("2026-10-06-1430") + 15 * 60 + 60
DAY = 86400


class FakeConsole:
    """Stands in for the console's POST /api/ingest. Answers with the codes in
    `statuses` first (one per request), then 200, and records every request."""

    def __init__(self) -> None:
        self.statuses: list[int] = []
        self.requests: list[dict] = []
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), self.handler_class())
        # poll_interval: how often serve_forever() checks for shutdown (fast teardown).
        self.thread = threading.Thread(target=self.server.serve_forever,
                                       kwargs={"poll_interval": 0.05}, daemon=True)

    @property
    def url(self) -> str:
        return f"http://127.0.0.1:{self.server.server_port}"

    def handler_class(self):
        console = self

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                body = self.rfile.read(int(self.headers["Content-Length"]))
                console.requests.append({"path": self.path, "headers": self.headers,
                                         "body": body})
                status = console.statuses.pop(0) if console.statuses else 200
                reply = b'{"analysis_id": "test", "findings": 1}'
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(reply)))
                self.end_headers()
                self.wfile.write(reply)

            def log_message(self, *args):  # keep the test output quiet
                pass

        return Handler


@pytest.fixture
def console():
    fake = FakeConsole()
    fake.thread.start()
    yield fake
    fake.server.shutdown()
    fake.server.server_close()


def unused_port() -> int:
    """A port on 127.0.0.1 where nothing listens: connecting is refused at once."""
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def write_config(data_dir: Path, url: str, sensor_id: str = "lab-sensor") -> None:
    (data_dir / "shipper.toml").write_text(
        "# test settings\n"
        f'console_url = "{url}"\n'
        f'token = "{TOKEN}"\n'
        f'sensor_id = "{sensor_id}"\n')


def make_sensor(data_dir: Path, folders=FOLDERS) -> Path:
    """Interval folders with one conn.log line each, and one Suricata minute file
    for the 14:15 interval (written in minute 14:20)."""
    for name in folders:
        folder = data_dir / "zeek" / name
        folder.mkdir(parents=True)
        (folder / "conn.log").write_text(f'{{"folder": "{name}"}}\n')
    spool = data_dir / "spool" / "suricata"
    spool.mkdir(parents=True)
    (spool / "eve-2026-10-06-1420.json").write_text('{"event_type": "tls"}\n')
    return data_dir


def parse_form(request: dict) -> dict[str, tuple[str | None, bytes]]:
    """multipart/form-data body -> {field name: (file name or None, value bytes)}."""
    boundary = request["headers"]["Content-Type"].split("boundary=")[1].encode()
    fields = {}
    for part in request["body"].split(b"--" + boundary)[1:-1]:
        head, _, value = part.removeprefix(b"\r\n").partition(b"\r\n\r\n")
        disposition = head.decode().splitlines()[0]
        name = re.search(r'; name="([^"]*)"', disposition).group(1)
        file_name = re.search(r'; filename="([^"]*)"', disposition)
        fields[name] = (file_name.group(1) if file_name else None, value.removesuffix(b"\r\n"))
    return fields


def tar_members(data: bytes) -> dict[str, bytes]:
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tar:
        return {m.name: tar.extractfile(m).read() for m in tar.getmembers()}


# ---- shipping -------------------------------------------------------------------------

def test_ships_the_right_file_with_the_right_header(tmp_path, console):
    data = make_sensor(tmp_path, folders=("2026-10-06-1415", "2026-10-06-1430"))
    write_config(data, console.url)

    result = run_once(data, 15, NOW)

    assert result["shipped"] == ["2026-10-06-1415"]
    [request] = console.requests
    assert request["path"] == "/api/ingest"
    assert request["headers"]["Authorization"] == f"Bearer {TOKEN}"
    form = parse_form(request)
    assert form["sensor_id"] == (None, b"lab-sensor")
    file_name, archive = form["file"]
    assert file_name == "2026-10-06-1415.tar.gz"
    assert tar_members(archive) == {
        "2026-10-06-1415/conn.log": b'{"folder": "2026-10-06-1415"}\n',
        "2026-10-06-1415/eve.json": b'{"event_type": "tls"}\n',   # merged before shipping
    }
    assert is_shipped(data / "zeek" / "2026-10-06-1415")


def test_the_folder_still_being_written_is_not_shipped(tmp_path, console):
    data = make_sensor(tmp_path)
    write_config(data, console.url)
    run_once(data, 15, NOW)
    assert not is_shipped(data / "zeek" / "2026-10-06-1430")
    # Two minutes later it has settled, and the next round ships it.
    assert run_once(data, 15, NOW + 120)["shipped"] == ["2026-10-06-1430"]


def test_never_ships_a_folder_twice(tmp_path, console):
    data = make_sensor(tmp_path)
    write_config(data, console.url)
    assert run_once(data, 15, NOW)["shipped"] == ["2026-10-06-1400", "2026-10-06-1415"]
    assert run_once(data, 15, NOW + 30)["shipped"] == []
    assert len(console.requests) == 2


def test_retries_after_the_console_answers_with_an_error(tmp_path, console):
    data = make_sensor(tmp_path, folders=("2026-10-06-1415",))
    write_config(data, console.url)
    console.statuses = [500]

    assert run_once(data, 15, NOW)["shipped"] == []
    assert not is_shipped(data / "zeek" / "2026-10-06-1415")

    assert run_once(data, 15, NOW + 60)["shipped"] == ["2026-10-06-1415"]
    assert len(console.requests) == 2
    # The same folder packs to the same bytes, so the console sees the same upload.
    assert parse_form(console.requests[0])["file"] == parse_form(console.requests[1])["file"]


def test_retries_when_the_console_cannot_be_reached(tmp_path, console):
    data = make_sensor(tmp_path, folders=("2026-10-06-1415",))
    write_config(data, f"http://127.0.0.1:{unused_port()}")
    assert run_once(data, 15, NOW)["shipped"] == []      # refused: no crash, not marked

    write_config(data, console.url)                      # the console is back
    assert run_once(data, 15, NOW + 60)["shipped"] == ["2026-10-06-1415"]


def test_stops_at_the_first_failure_and_keeps_the_order(tmp_path, console):
    data = make_sensor(tmp_path)
    write_config(data, console.url)
    console.statuses = [503]
    assert run_once(data, 15, NOW)["shipped"] == []
    assert len(console.requests) == 1                    # 14:15 was not even tried
    assert run_once(data, 15, NOW + 30)["shipped"] == ["2026-10-06-1400", "2026-10-06-1415"]


def test_a_proxy_setting_is_ignored(tmp_path, console, monkeypatch):
    for name in ("http_proxy", "HTTP_PROXY", "https_proxy", "HTTPS_PROXY", "all_proxy"):
        monkeypatch.setenv(name, f"http://127.0.0.1:{unused_port()}")
    monkeypatch.delenv("no_proxy", raising=False)
    monkeypatch.delenv("NO_PROXY", raising=False)
    data = make_sensor(tmp_path, folders=("2026-10-06-1415",))
    write_config(data, console.url)
    assert run_once(data, 15, NOW)["shipped"] == ["2026-10-06-1415"]


def test_without_a_config_file_nothing_is_shipped(tmp_path, console, caplog):
    data = make_sensor(tmp_path)
    assert run_once(data, 15, NOW)["shipped"] == []
    assert console.requests == []
    assert "shipper.toml not found" in caplog.text


def test_a_bad_config_file_is_reported_not_fatal(tmp_path, console, caplog):
    data = make_sensor(tmp_path)
    write_config(data, console.url, sensor_id="lab sensor!")
    assert run_once(data, 15, NOW)["shipped"] == []
    assert "sensor_id must be" in caplog.text


def test_main_runs_one_round(tmp_path, console):
    data = make_sensor(tmp_path, folders=("2026-10-06-1415",))
    write_config(data, console.url)
    assert main(["--data", str(data), "--interval-minutes", "15", "--once"]) == 0
    assert len(console.requests) == 1   # the real clock is long past 14:17 on Oct 6, 2026


# ---- settings ---------------------------------------------------------------------

def test_load_config_reads_the_settings(tmp_path):
    (tmp_path / "shipper.toml").write_text(
        f'console_url = "http://192.0.2.10:8001/"\ntoken = "{TOKEN}"\nsensor_id = "sensor-01"\n')
    config = load_config(tmp_path / "shipper.toml")
    assert config.console_url == "http://192.0.2.10:8001"   # trailing slash removed
    assert (config.token, config.sensor_id, config.ca_file) == (TOKEN, "sensor-01", None)


@pytest.mark.parametrize(("line", "message"), [
    ('console_url = "192.0.2.10:8001"', "console_url must start with"),
    ('token = ""', "token is empty"),
    ('sensor_id = "../etc"', "sensor_id must be"),
])
def test_load_config_refuses_wrong_settings(tmp_path, line, message):
    settings = {"console_url": '"http://192.0.2.10:8001"', "token": f'"{TOKEN}"',
                "sensor_id": '"sensor-01"'}
    key = line.split(" = ")[0]
    settings[key] = line.split(" = ")[1]
    (tmp_path / "shipper.toml").write_text(
        "".join(f"{k} = {v}\n" for k, v in settings.items()))
    with pytest.raises(ConfigError, match=message):
        load_config(tmp_path / "shipper.toml")


# ---- packing and retention ------------------------------------------------------------

def test_pack_folder_is_repeatable_and_leaves_out_hidden_files(tmp_path):
    folder = make_sensor(tmp_path) / "zeek" / "2026-10-06-1415"
    (folder / SHIPPED_MARKER).write_text("1\n")
    (folder / ".eve-abc.partial").write_text("half written\n")
    first = pack_folder(folder)
    assert pack_folder(folder) == first
    assert list(tar_members(first)) == ["2026-10-06-1415/conn.log"]


def test_prune_deletes_only_shipped_folders_older_than_7_days(tmp_path):
    data = make_sensor(tmp_path, folders=("2026-09-28-1400", "2026-09-28-1415",
                                          "2026-10-06-1400"))
    for name in ("2026-09-28-1400", "2026-10-06-1400"):
        (data / "zeek" / name / SHIPPED_MARKER).write_text("1\n")
    old_part = data / "spool" / "suricata" / "eve-2026-09-28-1401.json"
    old_part.write_text("{}\n")

    deleted = prune(data, now=NOW)

    assert deleted == ["2026-09-28-1400", "eve-2026-09-28-1401.json"]
    assert sorted(p.name for p in (data / "zeek").iterdir()) == [
        "2026-09-28-1415",   # never shipped: kept
        "2026-10-06-1400",   # shipped, but only today
    ]
    assert (data / "spool" / "suricata" / "eve-2026-10-06-1420.json").exists()


def test_prune_keeps_a_folder_until_it_is_older_than_7_days(tmp_path):
    data = make_sensor(tmp_path, folders=("2026-10-06-1400",))
    (data / "zeek" / "2026-10-06-1400" / SHIPPED_MARKER).write_text("1\n")
    start = folder_start("2026-10-06-1400")
    assert prune(data, now=start + 7 * DAY) == []
    assert prune(data, now=start + 7 * DAY + 1) == ["2026-10-06-1400"]
```

Run them:

```bash
pytest tests/unit/test_live_adapter.py tests/unit/test_shipper.py -q
```

Expected output:

```text
..........................................                                                   [100%]
42 passed in 1.28s
```

**Step 10.** **The console side.** The dashboard listens only on `127.0.0.1`, so nobody on the network can read alerts or approve a block. Sensors get their own door: a second container that serves nothing but `POST /api/ingest` on port 8001 of the console's LAN address (`create_ingest_app()` from JAI-07). Create `docker/compose.lan.yaml`:

```yaml
# Optional (Jakub, JAK-07): let live sensors and host agents on YOUR network send
# logs to this console. Without this file nothing on the network can reach MaxGuard.
#
# Start:  docker compose -f docker/compose.yaml -f docker/compose.lan.yaml up -d
#
# It adds one container, maxguard-ingest: the same image, serving ONLY
# POST /api/ingest on port 8001 of the console's LAN address. The dashboard and the
# rest of the API stay on 127.0.0.1:8000, so nobody on the network can read alerts
# or approve a block. Both containers share the maxguard-data volume.
#
# Put these two settings in docker/.env next to this file (never commit that file):
#   MAXGUARD_LAN_ADDRESS   this console's address on your network, e.g. 192.168.50.20
#   MAXGUARD_INGEST_TOKEN  at least 32 characters; make one with:
#                          python3 -c "import secrets; print(secrets.token_urlsafe(32))"
# Sensors then use console_url = "http://<MAXGUARD_LAN_ADDRESS>:8001" in /data/shipper.toml.
services:
  maxguard-ingest:
    image: maxguard:2.0.0a0
    command: ["uvicorn", "maxguard.api.app:create_ingest_app", "--factory",
              "--host", "0.0.0.0", "--port", "8001"]
    ports:
      # Only on the LAN address you name, never on every interface.
      - "${MAXGUARD_LAN_ADDRESS:?set MAXGUARD_LAN_ADDRESS in docker/.env}:8001:8001"
    volumes:
      - maxguard-data:/data
    environment:
      OLLAMA_HOST: http://ollama:11434
      MAXGUARD_OFFLINE: "1"
      MAXGUARD_INGEST_TOKEN: "${MAXGUARD_INGEST_TOKEN:?set MAXGUARD_INGEST_TOKEN in docker/.env}"
      # The Host header sensors send: the LAN address (DNS rebinding check, section 10).
      MAXGUARD_ALLOWED_HOSTS: "${MAXGUARD_LAN_ADDRESS}"
    networks:
      - ui
      - ai
    depends_on:
      - ollama
    restart: unless-stopped
```

Check both Compose files (the values here are examples; yours go in `docker/.env`, which `.gitignore` already keeps out of git):

```bash
MAXGUARD_LAN_ADDRESS=192.168.50.20 MAXGUARD_INGEST_TOKEN=example-token-of-32-characters-or-more \
  docker compose -f docker/compose.yaml -f docker/compose.lan.yaml config --format json | python3 -c "import json, sys; s = json.load(sys.stdin)['services']['maxguard-ingest']; print(s['command'][1], s['ports'][0]['host_ip'], s['ports'][0]['published'])"
docker compose -f docker/compose.yaml -f docker/compose.lan.yaml config --quiet
```

Expected output:

```text
maxguard.api.app:create_ingest_app 192.168.50.20 8001
error while interpolating services.maxguard-ingest.environment.MAXGUARD_INGEST_TOKEN: required variable MAXGUARD_INGEST_TOKEN is missing a value: set MAXGUARD_INGEST_TOKEN in docker/.env
```

*The first command shows the ingest app published only on the LAN address, port 8001. The second fails on purpose (exit code 1): without the two settings, Compose refuses to start the ingest container.*

**Step 11.** On the console machine (address `192.168.50.20` in the lab), make a token, then create `docker/.env` with your editor (for example `nano docker/.env`):

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

```text
MAXGUARD_LAN_ADDRESS=192.168.50.20
MAXGUARD_INGEST_TOKEN=<paste the token here>
```

Make it readable only by you and start MaxGuard with both files:

```bash
chmod 600 docker/.env
docker compose -f docker/compose.yaml -f docker/compose.lan.yaml up -d
```

Docker Compose reads `docker/.env` by itself because it sits next to the first Compose file.

**Step 12.** Then, on the sensor, put the console's ingest address and the same token in `/data/shipper.toml` (never in the repository) and make it readable only by root:

```toml
console_url = "http://192.168.50.20:8001"   # the console's LAN address, port 8001
token = "<MAXGUARD_INGEST_TOKEN from docker/.env on the console>"
sensor_id = "sensor-01"
```

```bash
sudo chmod 600 /data/shipper.toml
```

**Step 13.** Try the whole path on the Pi with 1-minute folders first. The test traffic must cross switch port 1, the only port the sensor watches (`docs/HARDWARE.md` section 1): run the lab service (`docker run -d --rm --name lab-service -p 23:23 -p 8080:8080 lab-server`) on a machine plugged into a LAN port of the router, and connect to it from a device on the mesh Wi-Fi. Stop it afterwards (`docker stop lab-service`): it is insecure on purpose.

```bash
# On the sensor: 1-minute folders for this test only
export MAXGUARD_INTERVAL_MINUTES=1
docker compose -f docker/sensor-compose.yaml up -d
# use the lab service's HTTP (port 8080) and Telnet from a lab machine, wait 4 minutes
ls /data/zeek
ls -A /data/zeek/2026-10-06-2103
docker compose -f docker/sensor-compose.yaml ps --format '{{.Service}} {{.State}}'
docker compose -f docker/sensor-compose.yaml logs --no-log-prefix shipper
# On the console:
curl -s http://127.0.0.1:8000/api/alerts | python3 -c "import json, sys; [print(a['rule_id'], a['severity'], a['count']) for a in json.load(sys.stdin)]"
curl -s 'http://127.0.0.1:8000/api/events?limit=1' | python3 -c "import json, sys; e = json.load(sys.stdin)[0]; print(e['sensor_id'], e['source'], e['log'])"
# Back on the sensor: stop the test
docker compose -f docker/sensor-compose.yaml down && unset MAXGUARD_INTERVAL_MINUTES
```

Expected output (not run in planning):

```text
2026-10-06-2102
2026-10-06-2103
2026-10-06-2104
2026-10-06-2105
.shipped
capture_loss.log
conn.log
eve.json
files.log
http.log
known_hosts.log
known_services.log
maxguard_cleartext.log
software.log
shipper running
suricata running
zeek running
2026-10-06 21:02:35,859 INFO shipping complete 1-minute folders from /data/zeek
2026-10-06 21:05:36,159 INFO 2026-10-06-2102: shipped (5066 bytes, HTTP 200)
2026-10-06 21:06:36,274 INFO 2026-10-06-2103: shipped (2612 bytes, HTTP 200)
2026-10-06 21:07:36,351 INFO 2026-10-06-2104: shipped (2218 bytes, HTTP 200)
cleartext.telnet high 5
cleartext.http_alt medium 6
lab-sensor-01 zeek conn.log
```

*Not run on a Raspberry Pi: verify on hardware. This output is from planning, where Zeek and Suricata listened inside a lab-server container's network namespace instead of on `eth0` (a two-line Compose override), the console ran on the same machine, and `shipper.toml` named `sensor_id = "lab-sensor-01"`. The first Telnet session was at 21:03:09 and its alert reached the console at 21:06:36: the 21:03 folder is complete at 21:06:00 (end of the interval plus two minutes), and the shipper checks once a minute. With 15-minute folders, expect up to about 18 minutes plus the analysis time. Your folder names are your own times.*

**Step 14.** Then start it for real (15-minute folders), run the sensor on the lab for one day, and check that alerts appear on the console within about 20 minutes of the traffic: `docker compose -f docker/sensor-compose.yaml up -d`.

**Step 15.** Commit, push, and open the pull request:

```bash
git add -A
git status          # only this task's files: nothing from .venv/, data/ or lab/captures/
git commit -m "feat: live sensor with rotation and shipping (JAK-07)"
git push -u origin HEAD
```

`HEAD` means "the branch I am on", so you do not have to retype its name. Open the repository on github.com: a yellow bar shows your branch with a **Compare & pull request** button. Click it, keep the title `feat: live sensor with rotation and shipping (JAK-07)`, fill in the template (paste the real output of the commands above under **How I tested it**), write `Closes #<issue number>` (this task's issue), and pick **@flau0306** under **Reviewers**. Click **Create pull request**, then fix anything CI or the reviewer finds with new commits on the same branch.

#### How to test

Both test files pass on your laptop. On the lab, `ls /data/zeek` shows a new folder every 15 minutes, `docker compose -f docker/sensor-compose.yaml ps` shows all three containers running after a reboot, and the console's alert queue shows the lab phone's traffic with the sensor's `sensor_id`. The capture port still has no IP address (`ip -br addr show eth0`).

#### What you just did and why

Shipping completed folders instead of streaming keeps the design simple: the console already knows how to analyze a folder of logs, and a network hiccup only delays a folder instead of losing events. A 15-minute interval is the trade-off between how quickly an alert appears and how many small Parquet files the console has to manage (each one costs about 3 KB). The sensor never transmits on the capture port; the shipper uses only the management port (CLAUDE.md rule 5).

#### Pull request checklist

- [ ] `ruff check .` prints `All checks passed!`
- [ ] `pytest -m "not integration" -q` passes on your laptop
- [ ] The pull request title has the form `type: summary (TASK-ID)` and the body says `Closes #<issue number>`
- [ ] No secrets, passwords, email addresses, personal data, or captures from a real network (CLAUDE.md rule 6)
- [ ] Any new dependency has a row in `docs/DEPENDENCIES.md` with its license
- [ ] CI is green and your reviewer approved
- [ ] Zeek runs without `-D`
- [ ] The token and console address are read from `/data`, not from the repository
- [ ] One full day of live data reached the console

### JAK-09: JA4 watchlist rule

**Due:** Spring S5-S8 (due Fri Mar 12, 2027) · **Milestone:** `S5-S8 Respond` · **Needs first:** [JAK-05](#jak-05-suricata-in-the-pipeline) · **Kind:** code, tested

**Issue labels:** `type:task` `phase:spring` `owner:jakub` `area:engine` `area:sensor`

#### Goal

Add rule `tls.ja4_watchlist`: a TLS client whose JA4 fingerprint is on MaxGuard's watchlist raises a high finding. The watchlist ships empty; entries come only from our own captures or sources whose license allows copying.

#### Prerequisites

JAK-05 (Suricata in the pipeline) is merged. The new rule ID needs the Security Lead's approval: ask Ahmad in the issue before you start.

#### Steps

**Step 1.** Update `main` and create your branch for this task (one branch per task):

```bash
cd ~/projects/maxguard
source .venv/bin/activate
git checkout main && git pull
git checkout -b jakub/ja4-watchlist
```

If `source .venv/bin/activate` fails, you have not made the virtual environment yet: do Week 0 section 0.11 first.

**Step 2.** Create `maxguard/intel/__init__.py`:

```python
"""Threat-intel data that ships with MaxGuard (read locally, never downloaded at runtime).

ja4_watchlist.yaml  JA4 fingerprints for the tls.ja4_watchlist rule (ships empty)
"""
```

and the empty watchlist `maxguard/intel/ja4_watchlist.yaml`:

```yaml
# JA4 watchlist for the tls.ja4_watchlist rule (maxguard/rules/ja4.py).
#
# A list of TLS client fingerprints (JA4 only, from Suricata's eve.json) that
# should raise a "high" finding when a device on the network uses them.
# Each entry needs three keys:
#   ja4:    the fingerprint, e.g. t13d1516h2_8daaf6152771_e5627efa2ab1
#   label:  what it is, in plain words
#   source: where it came from (our own capture, or a source whose license allows copying)
#
# The list ships EMPTY on purpose. Do not paste entries from third-party JA4
# databases unless their license allows it and you record that in "source".
#
# Example (from MaxGuard's own lab capture tests/pcaps/clean_tls13.pcap):
# - ja4: t13d041000_16476d049b0b_78f1d400d464
#   label: "MaxGuard lab client (Python ssl, TLS 1.3 only)"
#   source: "MaxGuard lab capture clean_tls13.pcap (Suricata 7.0.10)"
[]
```

**Step 3.** Create the rule `maxguard/rules/ja4.py`:

```python
"""JA4 watchlist rule (Jakub, proposed for v2.0 spring).

Suricata (checked on 7.0.10 and 8.0.7) writes a JA4 fingerprint of every TLS
client hello into eve.json ("event_type": "tls", field tls.ja4) when
maxguard-suricata.yaml turns it on. JA4 (TLS client fingerprinting) is
BSD-3-Clause; MaxGuard uses only JA4, no other JA4+ method (CLAUDE.md rule 7).

The rule compares each fingerprint with maxguard/intel/ja4_watchlist.yaml, a
list of {ja4, label, source} entries. We ship that list EMPTY: copying a
third-party fingerprint database with an unknown license into the repo is not
allowed, so every entry must come from our own captures or a source whose
license we have checked (write it in "source").

JAK-09 adds this module to maxguard/rules/__init__.py, which turns the rule on
(a new rule ID needs the Security Lead's approval).
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import yaml

from maxguard.adapters.base import read_log
from maxguard.ids import evidence
from maxguard.models import Finding
from maxguard.rules.base import rule

RULE_ID = "tls.ja4_watchlist"
WATCHLIST_PATH = Path(__file__).resolve().parent.parent / "intel" / "ja4_watchlist.yaml"
ENTRY_KEYS = ("ja4", "label", "source")


class WatchlistError(ValueError):
    """The watchlist file has a mistake (the message says which entry and what)."""


def looks_like_ja4(text: str) -> bool:
    """True for the JA4 shape 'a_b_c': 10 characters, then two 12-character hex hashes.

    Example from the JA4 spec: t13d1516h2_8daaf6152771_e5627efa2ab1
    This catches copy-paste mistakes in the watchlist (a JA3 hash, a JA4H, ...).
    """
    parts = text.split("_")
    if len(parts) != 3 or len(parts[0]) != 10:
        return False
    return all(len(p) == 12 and all(c in "0123456789abcdef" for c in p) for p in parts[1:])


def checked_ja4(entry: object, where: str) -> str:
    """Return the entry's JA4 (lower case) or raise WatchlistError saying what is wrong."""
    if not isinstance(entry, dict):
        raise WatchlistError(f"{where}: expected keys {ENTRY_KEYS}")
    missing = [key for key in ENTRY_KEYS if not str(entry.get(key) or "").strip()]
    if missing:
        raise WatchlistError(f"{where}: missing {missing}")
    ja4 = str(entry["ja4"]).strip().lower()  # Suricata writes JA4 in lower case
    if not looks_like_ja4(ja4):
        raise WatchlistError(f"{where}: {ja4!r} is not a JA4 fingerprint")
    return ja4


def load_watchlist(path: Path = WATCHLIST_PATH) -> dict[str, dict]:
    """Read the watchlist file into {ja4: entry}. Raises WatchlistError on a bad entry,
    so a typo in the file stops the analysis instead of silently matching nothing."""
    entries = yaml.safe_load(path.read_text()) or []  # a file with only comments -> None
    if not isinstance(entries, list):
        raise WatchlistError(f"{path.name}: expected a list of entries")
    watchlist: dict[str, dict] = {}
    for i, entry in enumerate(entries):
        watchlist[checked_ja4(entry, f"{path.name} entry {i}")] = entry
    return watchlist


def tls_events(log_dir: Path) -> Iterator[dict]:
    """Yield eve.json TLS events that carry a JA4 fingerprint."""
    for rec in read_log(log_dir, "eve.json"):
        if rec.get("event_type") == "tls" and (rec.get("tls") or {}).get("ja4"):
            yield rec


def watchlist_finding(rec: dict, entry: dict) -> Finding:
    ev = evidence("eve.json", rec)  # its ts is the eve timestamp as epoch seconds
    tls = rec["tls"]
    return Finding(rule_id=RULE_ID, title=f"TLS client matches JA4 watchlist: {entry['label']}",
                   severity="high", src_ip=rec["src_ip"], dst_ip=rec["dest_ip"],
                   dst_port=int(rec["dest_port"]), protocol="tls",
                   first_seen=ev.ts, last_seen=ev.ts, source="suricata",
                   details={"ja4": tls["ja4"], "label": entry["label"],
                            "watchlist_source": entry["source"], "sni": tls.get("sni")},
                   evidence=[ev])


@rule(RULE_ID)
def ja4_watchlist(log_dir: Path, watchlist_path: Path = WATCHLIST_PATH) -> list[Finding]:
    """One finding per TLS event whose JA4 is on the watchlist (merged per src/dst/port)."""
    watchlist = load_watchlist(watchlist_path)
    if not watchlist:  # the shipped list is empty: nothing to compare
        return []
    return [watchlist_finding(rec, watchlist[rec["tls"]["ja4"]])
            for rec in tls_events(log_dir) if rec["tls"]["ja4"] in watchlist]
```

**Step 4.** Register it: replace the contents of `maxguard/rules/__init__.py` with

```python
"""Importing this package registers every rule module with the registry."""

from . import certs, cleartext, ja4, tls  # noqa: F401
```

**Step 5.** Create the tests `tests/unit/test_ja4_rule.py`:

```python
"""Tests for the tls.ja4_watchlist rule.

The rule is not in maxguard/rules/__init__.py yet, so it is imported directly,
and every test writes its own temporary watchlist instead of editing the
shipped (empty) one.
"""

import re
from pathlib import Path

import pytest
import yaml

from maxguard.adapters.base import read_log
from maxguard.ids import record_id
from maxguard.rules import ja4
from maxguard.rules.base import RULES

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "zeek"
# The Python lab client's JA4 in clean_tls13/eve.json (Suricata 7.0.10).
LAB_JA4 = "t13d041000_16476d049b0b_78f1d400d464"


def write_watchlist(tmp_path: Path, entries) -> Path:
    path = tmp_path / "ja4_watchlist.yaml"
    path.write_text(yaml.safe_dump(entries))
    return path


def lab_entry(ja4_value: str = LAB_JA4) -> dict:
    return {"ja4": ja4_value, "label": "Lab Python client", "source": "MaxGuard lab capture"}


def test_matching_ja4_gives_one_high_finding(tmp_path):
    watchlist = write_watchlist(tmp_path, [lab_entry()])
    [f] = ja4.ja4_watchlist(FIXTURES / "clean_tls13", watchlist_path=watchlist)
    assert (f.rule_id, f.severity, f.source) == ("tls.ja4_watchlist", "high", "suricata")
    assert (f.src_ip, f.dst_ip, f.dst_port, f.protocol) == ("172.18.0.3", "172.18.0.2", 4436, "tls")
    assert f.title == "TLS client matches JA4 watchlist: Lab Python client"
    assert f.details == {"ja4": LAB_JA4, "label": "Lab Python client",
                         "watchlist_source": "MaxGuard lab capture",
                         "sni": "port4436.lab.invalid"}


def test_evidence_points_at_the_eve_tls_record(tmp_path):
    watchlist = write_watchlist(tmp_path, [lab_entry()])
    [f] = ja4.ja4_watchlist(FIXTURES / "clean_tls13", watchlist_path=watchlist)
    [tls_rec] = [r for r in read_log(FIXTURES / "clean_tls13", "eve.json")
                 if r["event_type"] == "tls"]
    [ev] = f.evidence
    assert ev.log == "eve.json"
    assert ev.uid == tls_rec["community_id"]  # links to Zeek's conn.log community_id
    assert ev.record_id == record_id("eve.json", tls_rec)
    assert f.first_seen == f.last_seen == ev.ts


def test_same_logs_same_finding_id_and_record_ids(tmp_path):
    watchlist = write_watchlist(tmp_path, [lab_entry()])
    first = ja4.ja4_watchlist(FIXTURES / "clean_tls13", watchlist_path=watchlist)
    again = ja4.ja4_watchlist(FIXTURES / "clean_tls13", watchlist_path=watchlist)
    assert [f.to_dict() for f in first] == [f.to_dict() for f in again]


def test_other_fingerprints_do_not_match(tmp_path):
    watchlist = write_watchlist(tmp_path, [lab_entry()])
    # cert_expired's client used TLS 1.2, so its JA4 is different
    assert ja4.ja4_watchlist(FIXTURES / "cert_expired", watchlist_path=watchlist) == []


def test_no_eve_json_means_no_findings(tmp_path):
    watchlist = write_watchlist(tmp_path, [lab_entry()])
    assert ja4.ja4_watchlist(FIXTURES / "telnet" / "missing", watchlist_path=watchlist) == []


def test_shipped_watchlist_is_empty_and_valid():
    assert ja4.load_watchlist() == {}
    assert ja4.ja4_watchlist(FIXTURES / "clean_tls13") == []


def test_rule_is_registered_under_its_id():
    assert RULES["tls.ja4_watchlist"] is ja4.ja4_watchlist


def test_upper_case_entry_still_matches(tmp_path):
    watchlist = write_watchlist(tmp_path, [lab_entry(LAB_JA4.upper())])
    assert len(ja4.ja4_watchlist(FIXTURES / "clean_tls13", watchlist_path=watchlist)) == 1


@pytest.mark.parametrize("entries, message", [
    ({"ja4": LAB_JA4}, "expected a list"),
    ([{"ja4": LAB_JA4, "label": "x"}], "missing ['source']"),
    (["t13d041000_16476d049b0b_78f1d400d464"], "expected keys"),
    ([lab_entry("0123456789abcdef0123456789abcdef")], "is not a JA4"),  # JA3-sized MD5
])
def test_bad_watchlist_entries_are_rejected(tmp_path, entries, message):
    watchlist = write_watchlist(tmp_path, entries)
    with pytest.raises(ja4.WatchlistError, match=re.escape(message)):
        ja4.load_watchlist(watchlist)


@pytest.mark.parametrize("text, ok", [
    ("t13d1516h2_8daaf6152771_e5627efa2ab1", True),  # example from the JA4 spec
    (LAB_JA4, True),
    ("t13d1516h2_8daaf6152771", False),  # only two parts
    ("t13d1516h2_8daaf615277_e5627efa2ab1", False),  # 11-character hash
    ("t13d1516h2_8daaf615277z_e5627efa2ab1", False),  # not hex
])
def test_looks_like_ja4(text, ok):
    assert ja4.looks_like_ja4(text) is ok
```

**Step 6.** Run them, then the whole unit suite (the registry test must still pass):

```bash
pytest tests/unit/test_ja4_rule.py -q
```

Expected output:

```text
.................                                                                            [100%]
17 passed in 0.14s
```

```bash
pytest -m "not integration" -q
```

Expected output:

```text
............................................................................................ [ 13%]
............................................................................................ [ 27%]
............................................................................................ [ 41%]
.........s.................................................................................. [ 55%]
............................................................................................ [ 69%]
............................................................................................ [ 83%]
............................................................................................ [ 97%]
...................                                                                          [100%]
662 passed, 1 skipped, 31 deselected in 12.43s
```

**Step 7.** Add the rule's Home text (Jonattan reviews it) and ask Amory and Fiona whether a mapping row or ATT&CK row fits; add them in the same pull request if so.

**Step 8.** Commit, push, and open the pull request:

```bash
git add -A
git status          # only this task's files: nothing from .venv/, data/ or lab/captures/
git commit -m "feat: tls.ja4_watchlist rule with an empty watchlist (JAK-09)"
git push -u origin HEAD
```

`HEAD` means "the branch I am on", so you do not have to retype its name. Open the repository on github.com: a yellow bar shows your branch with a **Compare & pull request** button. Click it, keep the title `feat: tls.ja4_watchlist rule with an empty watchlist (JAK-09)`, fill in the template (paste the real output of the commands above under **How I tested it**), write `Closes #<issue number>` (this task's issue), and pick **@flau0306** under **Reviewers**. Click **Create pull request**, then fix anything CI or the reviewer finds with new commits on the same branch.

#### How to test

Both commands pass. With the empty watchlist the rule finds nothing on any capture; the tests add a fingerprint to a temporary watchlist to prove it fires.

#### What you just did and why

A fingerprint list is only as trustworthy as its source, and copying a third-party database with an unknown license into a public repository is not allowed. Shipping the list empty and requiring a `source` for every entry keeps the rule honest. JA4 comes from Suricata, the only JA4+ method MaxGuard may use (CLAUDE.md rule 7).

#### Pull request checklist

- [ ] `ruff check .` prints `All checks passed!`
- [ ] `pytest -m "not integration" -q` passes on your laptop
- [ ] The pull request title has the form `type: summary (TASK-ID)` and the body says `Closes #<issue number>`
- [ ] No secrets, passwords, email addresses, personal data, or captures from a real network (CLAUDE.md rule 6)
- [ ] Any new dependency has a row in `docs/DEPENDENCIES.md` with its license
- [ ] CI is green and your reviewer approved
- [ ] Ahmad approved the new rule ID in the issue

### JAK-10: NetFlow and IPFIX input

**Due:** Spring S9-S11 (due Fri Apr 16, 2027) · **Milestone:** `S9-S11 Detect more` · **Needs first:** [JAI-07](jaiden.md#jai-07-the-api-uploads-alerts-events-live-updates-sensor-ingest), [JAI-03](jaiden.md#jai-03-common-event-schema-the-normalizer-and-record-lookup), [AHM-06](ahmad.md#ahm-06-ip-timeline-and-device-inventory-pages) · **Kind:** code, tested

**Issue labels:** `type:task` `phase:spring` `owner:jakub` `area:sensor` `contract-change` `needs-hardware`

> **Needs hardware.** Steps that use the Raspberry Pi, the switch or other devices were not run during planning; they are marked *not run — verify on hardware*.

#### Goal

Let a router that exports NetFlow v5/v9 or IPFIX feed MaxGuard: a collector container writes flow records, and `NetflowAdapter` (Contract 3) turns them into `conn.log`-shaped JSON records, so the normalizer, the timeline, and the flow-based checks work unchanged (payload rules simply find nothing).

#### Prerequisites

JAI-07 is merged. This task adds a `source` value to the event schema, a contract change: the pull request needs Jaiden's review and Ahmad's approval.

#### Steps

**Step 1.** Update `main` and create your branch for this task (one branch per task):

```bash
cd ~/projects/maxguard
source .venv/bin/activate
git checkout main && git pull
git checkout -b jakub/netflow
```

If `source .venv/bin/activate` fails, you have not made the virtual environment yet: do Week 0 section 0.11 first.

**Step 2.** The collector is `netsampler/goflow2` (BSD-3-Clause, already in `docs/DEPENDENCIES.md`). Pin the version **and** the digest: on Docker Hub the tag `latest` still points at the old v1.3.8, not v2. Check the newest tag with `git ls-remote --tags https://github.com/netsampler/goflow2` (on October 8, 2026 it was `v2.2.7`, published for `linux/amd64` and `linux/arm64`). Create `docker/netflow-compose.yaml`:

```yaml
# NetFlow / IPFIX collector for MaxGuard (Jakub, JAK-10).
#
# A router on YOUR network exports NetFlow v5, NetFlow v9 or IPFIX to UDP port
# 2055 of the computer that runs this file. goflow2 writes one JSON line per
# flow to /data/netflow/goflow2.json; MaxGuard reads that folder:
#
#   maxguard analyze /data/netflow          (NetflowAdapter, maxguard/adapters/netflow.py)
#
# or upload one finished flow file on the dashboard (it then shows on the timeline).
#
# Once:   sudo mkdir -p /data/netflow && sudo chown 1000:1000 /data/netflow
# Start:  MAXGUARD_NETFLOW_ADDRESS=192.168.50.20 docker compose -f docker/netflow-compose.yaml up -d
# Stop:   docker compose -f docker/netflow-compose.yaml down    (the flow files stay)
#
# Settings (environment variables or docker/.env, which git ignores):
#   MAXGUARD_NETFLOW_ADDRESS   this computer's LAN address that the router sends to (required)
#   MAXGUARD_NETFLOW_DATA      the folder for the flow files (default /data/netflow)
#   MAXGUARD_UID / MAXGUARD_GID  who owns the flow files (default 1000:1000, the first user)
#
# Start a new file (for example once an hour), so each analysis covers one period:
#   mv /data/netflow/goflow2.json /data/netflow-done/2026-10-06-1400.json
#   docker compose -f docker/netflow-compose.yaml kill -s HUP goflow2
# goflow2 closes and reopens its output file when it gets SIGHUP.
#
# The collector only listens: it never sends anything to the router or anywhere else
# (CLAUDE.md rules 1 and 5). Its built-in HTTP server (metrics) is switched off.

services:
  goflow2:
    # v2.2.7 for linux/amd64 and linux/arm64 (Raspberry Pi 5). BSD-3-Clause.
    # Pin the version tag: on Docker Hub "latest" is the old v1.3.8, not v2.
    image: netsampler/goflow2:v2.2.7@sha256:b8fdc8f3666b05b0022ada3a3c8c50dcde97f7d19e3f42d050695fa0571fb952
    command:
      - "-listen=netflow://:2055"    # NetFlow v5, v9 and IPFIX; no sFlow
      - "-format=json"
      - "-transport=file"
      - "-transport.file=/data/netflow/goflow2.json"
      - "-addr="                     # empty: no HTTP server
    ports:
      - "${MAXGUARD_NETFLOW_ADDRESS:?set MAXGUARD_NETFLOW_ADDRESS (this computer's LAN address)}:2055:2055/udp"
    volumes:
      - ${MAXGUARD_NETFLOW_DATA:-/data/netflow}:/data/netflow
    user: "${MAXGUARD_UID:-1000}:${MAXGUARD_GID:-1000}"
    read_only: true
    cap_drop: [ALL]
    security_opt: ["no-new-privileges:true"]
    restart: unless-stopped
```

It listens on UDP 2055 of the address you give it, writes one JSON line per flow, runs as a normal user with a read-only file system and no capabilities, and its HTTP metrics server is switched off (`-addr=`), because nothing should be listening that MaxGuard does not need. Check it; the second command fails on purpose, because the listening address has no default:

```bash
MAXGUARD_NETFLOW_ADDRESS=127.0.0.1 \
  docker compose -f docker/netflow-compose.yaml config --format json | python -c "import json, sys; s = json.load(sys.stdin)['services']['goflow2']; print(s['image'].split('@')[0], s['user'], s['read_only'], s['cap_drop'], [(p['host_ip'], p['published'], p['protocol']) for p in s['ports']])"
docker compose -f docker/netflow-compose.yaml config --quiet
```

Expected output:

```text
netsampler/goflow2:v2.2.7 1000:1000 True ['ALL'] [('127.0.0.1', '2055', 'udp')]
error while interpolating services.goflow2.ports.[]: required variable MAXGUARD_NETFLOW_ADDRESS is missing a value: set MAXGUARD_NETFLOW_ADDRESS (this computer's LAN address)
```

**Step 3.** Create `maxguard/adapters/netflow.py`:

```python
"""NetflowAdapter: flow records from a router -> conn.log (Jakub, JAK-10).

A router that exports NetFlow v5, NetFlow v9 or IPFIX sends its flow records
over UDP to the goflow2 collector (docker/netflow-compose.yaml). goflow2 v2.2.7
writes one JSON object per flow, one per line, for example (shortened):

    {"type": "NETFLOW_V5", "time_received_ns": 1791323155565530742,
     "sequence_num": 0, "sampling_rate": 0, "sampler_address": "203.0.113.1",
     "time_flow_start_ns": 1791295190000000000, "time_flow_end_ns": 1791295192000000000,
     "bytes": 900, "packets": 12, "src_addr": "192.0.2.10", "dst_addr": "198.51.100.20",
     "proto": "TCP", "src_port": 49152, "dst_port": 23, "icmp_type": 0, "icmp_code": 0, ...}

This adapter turns each flow into a record shaped like a line of Zeek's
conn.log, plus "mg_source": "netflow", so the normalizer, the timeline and the
inventory work unchanged. Rules that need the payload (cleartext protocols,
TLS versions, certificates, JA4) find nothing, because a flow record has no
payload.

It accepts a folder of goflow2 JSON files (for example /data/netflow) or one
such file (what the dashboard upload and POST /api/ingest receive).

Differences from Zeek's conn.log, on purpose:
- A flow is one direction only (A -> B); a Zeek connection has both. So
  orig_bytes is the flow's byte count and resp_bytes is always 0; the answer
  B -> A is a separate flow record.
- There is no "service" (Zeek guesses it from the payload) and no conn_state.
- Byte counts are what the router reported. With packet sampling
  ("sampling_rate" > 1) the real traffic is about that many times larger.
"""

from __future__ import annotations

import hashlib
import ipaddress
import json
from pathlib import Path

# goflow2's "type" values for NetFlow v5, NetFlow v9 and IPFIX (its pb/flow.proto).
# sFlow ("SFLOW_5") is left out: it carries sampled packets, not flow records.
FLOW_TYPES = ("NETFLOW_V5", "NETFLOW_V9", "IPFIX")

# goflow2 writes the protocol by name. Zeek's conn.log uses "tcp", "udp", "icmp"
# (also for ICMPv6) and "unknown_transport" for everything else.
ZEEK_PROTOS = {"TCP": "tcp", "UDP": "udp", "ICMP": "icmp", "IPv6-ICMP": "icmp"}

# When the collector received the record is not part of the flow itself. Leaving
# it out of the hash gives a flow the same uid however often it is read.
NOT_PART_OF_FLOW = ("time_received_ns",)

# A goflow2 line is about 1.2 KB. Reading at most this much of a first line means
# a large binary file (a capture without newlines) is never read into memory.
MAX_FIRST_LINE = 64 * 1024

# The largest whole number the event store (SQLite INTEGER) can hold. goflow2's
# counters and nanosecond times always fit; a bigger value was not written by goflow2.
MAX_NUMBER = 2**63 - 1
MAX_PORT = 65535


def is_flow_record(rec: object) -> bool:
    return isinstance(rec, dict) and rec.get("type") in FLOW_TYPES and "src_addr" in rec


def first_record(path: Path) -> object:
    """The first non-empty line of a file, parsed as JSON (None if it is not JSON)."""
    with path.open("rb") as f:
        for _ in range(10):  # skip a few blank lines, never scan a whole file
            line = f.readline(MAX_FIRST_LINE)
            if not line:
                return None
            if line.strip():
                try:
                    return json.loads(line)
                except (ValueError, RecursionError):  # not JSON, not text, or absurdly nested
                    return None
    return None


def is_flow_file(path: Path) -> bool:
    return path.is_file() and is_flow_record(first_record(path))


def flow_files(path: Path) -> list[Path]:
    """The collector's files: the file itself, or a folder's *.json files that hold flows.

    Sorted, so the order never depends on how the disk lists the folder."""
    if path.is_file():
        return [path]
    return sorted(p for p in path.glob("*.json") if is_flow_file(p))


def read_flows(path: Path) -> list[dict]:
    """Every flow record of one file. Other lines (sFlow, a half-written last line) are skipped."""
    flows = []
    with path.open(errors="replace") as f:
        for line in f:
            try:
                rec = json.loads(line)
            except (ValueError, RecursionError):
                continue  # the collector may still be writing the last line
            if is_flow_record(rec):
                flows.append(rec)
    return flows


def flow_uid(flow: dict) -> str:
    """A deterministic uid: the same flow record always gets the same uid.

    Zeek's uids are random ("C" + 17 characters); this one is "N" (for NetFlow)
    + the first 17 hex digits of a SHA-256 of the record, so it has the same length."""
    stable = {k: v for k, v in flow.items() if k not in NOT_PART_OF_FLOW}
    text = json.dumps(stable, sort_keys=True, separators=(",", ":"))
    return "N" + hashlib.sha256(text.encode()).hexdigest()[:17]


def whole_number(value: object, largest: int = MAX_NUMBER) -> int:
    """A count, port or time from a flow record: a whole number from 0 to largest.

    goflow2 always writes these as JSON numbers; a missing one counts as 0.
    Anything else (text, a list, 1e400, a negative or huge number) means the line
    was not written by goflow2. ValueError then makes the caller skip the record,
    so a damaged or hostile upload cannot crash the analysis."""
    if value is None:
        return 0
    if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= largest:
        raise ValueError(f"not a whole number from 0 to {largest}: {value!r}")
    return value


def ip_text(value: object) -> str:
    """An IPv4 or IPv6 address as text; ValueError for anything else.

    The isinstance check matters: ipaddress also turns a plain number into an address."""
    if not isinstance(value, str):
        raise ValueError(f"not an IP address: {value!r}")
    return str(ipaddress.ip_address(value))


def seconds(nanoseconds: object) -> float:
    """goflow2 times are nanoseconds since 1970; Zeek's are seconds with 6 decimals."""
    return round(whole_number(nanoseconds) / 1e9, 6)


def ports(flow: dict, proto: str) -> tuple[int, int]:
    """Like Zeek: for ICMP the "ports" are the ICMP type and code."""
    if proto != "icmp":
        return (whole_number(flow.get("src_port"), MAX_PORT),
                whole_number(flow.get("dst_port"), MAX_PORT))
    if flow.get("type") == "NETFLOW_V5":
        # NetFlow v5 has no ICMP fields: the usual exporter convention puts
        # type * 256 + code in the destination port, and goflow2 passes that
        # number on unchanged (its producer_nflegacy.go copies the port).
        dst_port = whole_number(flow.get("dst_port"), MAX_PORT)
        return dst_port // 256, dst_port % 256
    return (whole_number(flow.get("icmp_type"), 255),
            whole_number(flow.get("icmp_code"), 255))


def to_conn(flow: dict) -> dict:
    """One goflow2 flow record -> one conn.log-shaped record.

    Raises ValueError if a field is not what goflow2 writes (see whole_number)."""
    start = seconds(flow.get("time_flow_start_ns"))
    end = seconds(flow.get("time_flow_end_ns"))
    if start == 0:  # some exporters leave the flow times out
        start = end = seconds(flow.get("time_received_ns"))
    proto = ZEEK_PROTOS.get(str(flow.get("proto")), "unknown_transport")
    orig_p, resp_p = ports(flow, proto)
    return {
        "ts": start,
        "uid": flow_uid(flow),
        "id.orig_h": ip_text(flow.get("src_addr")),
        "id.orig_p": orig_p,
        "id.resp_h": ip_text(flow.get("dst_addr")),
        "id.resp_p": resp_p,
        "proto": proto,
        "duration": round(max(end - start, 0.0), 6),
        "orig_bytes": whole_number(flow.get("bytes")),
        "resp_bytes": 0,  # one direction only: the answer is its own flow record
        "mg_source": "netflow",
    }


class NetflowAdapter:
    name = "netflow"

    def accepts(self, path: Path) -> bool:
        """goflow2 output (a file, or a folder of files), and nothing else.

        A Zeek log folder (it has conn.log) and a live sensor folder (it has
        zeek/) belong to the other adapters, even if a .json file is in them.
        A capture or an eve.json file fails the first-line check."""
        if path.is_file():
            return is_flow_file(path)
        if not path.is_dir() or (path / "conn.log").exists() or (path / "zeek").is_dir():
            return False
        return bool(flow_files(path))

    def to_zeek_logs(self, path: Path, workdir: Path) -> Path:
        conns: dict[str, dict] = {}
        for flow_file in flow_files(path):
            for flow in read_flows(flow_file):
                try:
                    conn = to_conn(flow)
                except (ValueError, RecursionError):
                    continue  # not what goflow2 writes: skip it, like a half-written line
                conns[conn["uid"]] = conn  # a record that appears twice is kept once
        out = workdir / "zeek_logs"
        out.mkdir(parents=True, exist_ok=True)
        with (out / "conn.log").open("w") as f:
            # Sorted by time, then uid: the same files always give the same conn.log.
            for conn in sorted(conns.values(), key=lambda c: (c["ts"], c["uid"])):
                f.write(json.dumps(conn) + "\n")
        return out
```

Things to notice. A flow record has one direction, so `orig_bytes` is the flow's byte count and `resp_bytes` is 0; the answer is its own record. The `uid` is `N` plus 17 hex digits of a SHA-256 over the record without the time goflow2 received it, so the same flow always gets the same uid and a file copied twice is counted once. ICMP type and code go into the port fields, as Zeek does. `accepts()` also takes a single goflow2 file, recognised by its first line: the dashboard and `/api/ingest` save uploads under a random name with no `.json` suffix, so a folder can never arrive that way. It never takes a folder that has `conn.log` or `zeek/`, so it cannot steal a Zeek log folder or a sensor folder. An uploaded file is attacker-controlled, so every number and address is checked (`whole_number()`, `ip_text()`) and a damaged record is skipped, not fatal: before the security review, one bad line made the upload answer HTTP 500.

**Step 4.** Add the adapter **last** in `ADAPTERS` in `maxguard/pipeline.py` (the other three always get the first look):

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
from maxguard.adapters.netflow import NetflowAdapter
from maxguard.adapters.pcap import PcapAdapter
from maxguard.adapters.zeeklogs import ZeekLogAdapter
from maxguard.mapping.loader import ATTACK, apply, load_all
from maxguard.models import SEVERITIES, Finding
from maxguard.rules.base import run_all

# Order matters only for clarity: each adapter accepts a different kind of input
# (a capture file; a folder with conn.log; a sensor folder with zeek/<interval>/;
# a folder of goflow2 flow files without conn.log or zeek/). NetflowAdapter is last
# so the other three always get the first look.
ADAPTERS = [PcapAdapter(), ZeekLogAdapter(), LiveSensorAdapter(), NetflowAdapter()]
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
    raise UnsupportedInput(f"{path.name}: not a pcap/pcapng file, a Zeek log folder/archive, "
                           "or a goflow2 flow file")


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

and give flow records their own `source` in `maxguard/events/normalize.py` (the two new lines in `from_conn`):

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
    if rec.get("mg_source") == "netflow":  # a router's flow record (JAK-10), not Zeek
        event["source"] = "netflow"
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

**Step 5.** Create the test data `tests/fixtures/netflow/goflow2.json` (real goflow2 v2.2.7 output from the generator below, documentation addresses only):

```json
{"type":"NETFLOW_V5","time_received_ns":1791495640783352502,"sequence_num":0,"sampling_rate":0,"sampler_address":"203.0.113.1","time_flow_start_ns":1791295190000000000,"time_flow_end_ns":1791295192000000000,"bytes":900,"packets":12,"src_addr":"192.0.2.10","dst_addr":"198.51.100.20","etype":"IPv4","proto":"TCP","src_port":49152,"dst_port":23,"in_if":1,"out_if":2,"src_mac":"00:00:00:00:00:00","dst_mac":"00:00:00:00:00:00","src_vlan":0,"dst_vlan":0,"vlan_id":0,"ip_tos":0,"forwarding_status":0,"ip_ttl":0,"ip_flags":0,"tcp_flags":27,"icmp_type":0,"icmp_code":0,"ipv6_flow_label":0,"fragment_id":0,"fragment_offset":0,"src_as":0,"dst_as":0,"next_hop":"0.0.0.0","next_hop_as":0,"src_net":"192.0.2.0/24","dst_net":"198.51.100.0/24","bgp_next_hop":"","bgp_communities":[],"as_path":[],"mpls_ttl":[],"mpls_label":[],"mpls_ip":[],"observation_domain_id":0,"observation_point_id":0,"layer_stack":[],"layer_size":[],"ipv6_routing_header_addresses":[],"ipv6_routing_header_seg_left":0}
{"type":"NETFLOW_V5","time_received_ns":1791495640784165231,"sequence_num":2,"sampling_rate":0,"sampler_address":"203.0.113.1","time_flow_start_ns":1791295195000000000,"time_flow_end_ns":1791295195500000000,"bytes":640,"packets":6,"src_addr":"192.0.2.10","dst_addr":"198.51.100.20","etype":"IPv4","proto":"TCP","src_port":49153,"dst_port":80,"in_if":1,"out_if":2,"src_mac":"00:00:00:00:00:00","dst_mac":"00:00:00:00:00:00","src_vlan":0,"dst_vlan":0,"vlan_id":0,"ip_tos":0,"forwarding_status":0,"ip_ttl":0,"ip_flags":0,"tcp_flags":27,"icmp_type":0,"icmp_code":0,"ipv6_flow_label":0,"fragment_id":0,"fragment_offset":0,"src_as":0,"dst_as":0,"next_hop":"0.0.0.0","next_hop_as":0,"src_net":"192.0.2.0/24","dst_net":"198.51.100.0/24","bgp_next_hop":"","bgp_communities":[],"as_path":[],"mpls_ttl":[],"mpls_label":[],"mpls_ip":[],"observation_domain_id":0,"observation_point_id":0,"layer_stack":[],"layer_size":[],"ipv6_routing_header_addresses":[],"ipv6_routing_header_seg_left":0}
{"type":"NETFLOW_V5","time_received_ns":1791495640783352502,"sequence_num":0,"sampling_rate":0,"sampler_address":"203.0.113.1","time_flow_start_ns":1791295190010000000,"time_flow_end_ns":1791295192000000000,"bytes":1400,"packets":10,"src_addr":"198.51.100.20","dst_addr":"192.0.2.10","etype":"IPv4","proto":"TCP","src_port":23,"dst_port":49152,"in_if":1,"out_if":2,"src_mac":"00:00:00:00:00:00","dst_mac":"00:00:00:00:00:00","src_vlan":0,"dst_vlan":0,"vlan_id":0,"ip_tos":0,"forwarding_status":0,"ip_ttl":0,"ip_flags":0,"tcp_flags":27,"icmp_type":0,"icmp_code":0,"ipv6_flow_label":0,"fragment_id":0,"fragment_offset":0,"src_as":0,"dst_as":0,"next_hop":"0.0.0.0","next_hop_as":0,"src_net":"198.51.100.0/24","dst_net":"192.0.2.0/24","bgp_next_hop":"","bgp_communities":[],"as_path":[],"mpls_ttl":[],"mpls_label":[],"mpls_ip":[],"observation_domain_id":0,"observation_point_id":0,"layer_stack":[],"layer_size":[],"ipv6_routing_header_addresses":[],"ipv6_routing_header_seg_left":0}
{"type":"NETFLOW_V5","time_received_ns":1791495640784165231,"sequence_num":2,"sampling_rate":0,"sampler_address":"203.0.113.1","time_flow_start_ns":1791295196000000000,"time_flow_end_ns":1791295196000000000,"bytes":60,"packets":1,"src_addr":"192.0.2.10","dst_addr":"198.51.100.53","etype":"IPv4","proto":"UDP","src_port":40000,"dst_port":53,"in_if":1,"out_if":2,"src_mac":"00:00:00:00:00:00","dst_mac":"00:00:00:00:00:00","src_vlan":0,"dst_vlan":0,"vlan_id":0,"ip_tos":0,"forwarding_status":0,"ip_ttl":0,"ip_flags":0,"tcp_flags":0,"icmp_type":0,"icmp_code":0,"ipv6_flow_label":0,"fragment_id":0,"fragment_offset":0,"src_as":0,"dst_as":0,"next_hop":"0.0.0.0","next_hop_as":0,"src_net":"192.0.2.0/24","dst_net":"198.51.100.0/24","bgp_next_hop":"","bgp_communities":[],"as_path":[],"mpls_ttl":[],"mpls_label":[],"mpls_ip":[],"observation_domain_id":0,"observation_point_id":0,"layer_stack":[],"layer_size":[],"ipv6_routing_header_addresses":[],"ipv6_routing_header_seg_left":0}
{"type":"NETFLOW_V5","time_received_ns":1791495640784165231,"sequence_num":2,"sampling_rate":0,"sampler_address":"203.0.113.1","time_flow_start_ns":1791295197000000000,"time_flow_end_ns":1791295197000000000,"bytes":84,"packets":1,"src_addr":"192.0.2.10","dst_addr":"198.51.100.20","etype":"IPv4","proto":"ICMP","src_port":0,"dst_port":2048,"in_if":1,"out_if":2,"src_mac":"00:00:00:00:00:00","dst_mac":"00:00:00:00:00:00","src_vlan":0,"dst_vlan":0,"vlan_id":0,"ip_tos":0,"forwarding_status":0,"ip_ttl":0,"ip_flags":0,"tcp_flags":0,"icmp_type":0,"icmp_code":0,"ipv6_flow_label":0,"fragment_id":0,"fragment_offset":0,"src_as":0,"dst_as":0,"next_hop":"0.0.0.0","next_hop_as":0,"src_net":"192.0.2.0/24","dst_net":"198.51.100.0/24","bgp_next_hop":"","bgp_communities":[],"as_path":[],"mpls_ttl":[],"mpls_label":[],"mpls_ip":[],"observation_domain_id":0,"observation_point_id":0,"layer_stack":[],"layer_size":[],"ipv6_routing_header_addresses":[],"ipv6_routing_header_seg_left":0}
{"type":"NETFLOW_V9","time_received_ns":1791495640785328329,"sequence_num":0,"sampling_rate":0,"sampler_address":"203.0.113.1","time_flow_start_ns":1791295192000000000,"time_flow_end_ns":1791295199000000000,"bytes":4200,"packets":30,"src_addr":"192.0.2.12","dst_addr":"198.51.100.22","etype":"IPv4","proto":"TCP","src_port":50022,"dst_port":22,"in_if":0,"out_if":0,"src_mac":"00:00:00:00:00:00","dst_mac":"00:00:00:00:00:00","src_vlan":0,"dst_vlan":0,"vlan_id":0,"ip_tos":0,"forwarding_status":0,"ip_ttl":0,"ip_flags":0,"tcp_flags":0,"icmp_type":0,"icmp_code":0,"ipv6_flow_label":0,"fragment_id":0,"fragment_offset":0,"src_as":0,"dst_as":0,"next_hop":"","next_hop_as":0,"src_net":"0.0.0.0/0","dst_net":"0.0.0.0/0","bgp_next_hop":"","bgp_communities":[],"as_path":[],"mpls_ttl":[],"mpls_label":[],"mpls_ip":[],"observation_domain_id":1,"observation_point_id":0,"layer_stack":[],"layer_size":[],"ipv6_routing_header_addresses":[],"ipv6_routing_header_seg_left":0}
{"type":"IPFIX","time_received_ns":1791495640785661074,"sequence_num":0,"sampling_rate":0,"sampler_address":"203.0.113.1","time_flow_start_ns":1791295195000000000,"time_flow_end_ns":1791295198000000000,"bytes":5200,"packets":14,"src_addr":"192.0.2.11","dst_addr":"203.0.113.5","etype":"IPv4","proto":"TCP","src_port":50000,"dst_port":443,"in_if":0,"out_if":0,"src_mac":"00:00:00:00:00:00","dst_mac":"00:00:00:00:00:00","src_vlan":0,"dst_vlan":0,"vlan_id":0,"ip_tos":0,"forwarding_status":0,"ip_ttl":0,"ip_flags":0,"tcp_flags":0,"icmp_type":0,"icmp_code":0,"ipv6_flow_label":0,"fragment_id":0,"fragment_offset":0,"src_as":0,"dst_as":0,"next_hop":"","next_hop_as":0,"src_net":"0.0.0.0/0","dst_net":"0.0.0.0/0","bgp_next_hop":"","bgp_communities":[],"as_path":[],"mpls_ttl":[],"mpls_label":[],"mpls_ip":[],"observation_domain_id":1,"observation_point_id":0,"layer_stack":[],"layer_size":[],"ipv6_routing_header_addresses":[],"ipv6_routing_header_seg_left":0}
```

and the tests `tests/unit/test_netflow.py`:

```python
"""Tests for NetflowAdapter (Jakub, JAK-10).

tests/fixtures/netflow/goflow2.json is real goflow2 v2.2.7 output for flows sent
by a small generator (2 NetFlow v5 packets, 1 NetFlow v9, 1 IPFIX) with
documentation addresses only (RFC 5737). The collector's own container address
was replaced by 203.0.113.1.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from maxguard.adapters.base import read_log
from maxguard.adapters.netflow import NetflowAdapter, flow_uid, to_conn
from maxguard.events.normalize import normalize
from maxguard.pipeline import analyze, pick_adapter

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "netflow" / "goflow2.json"
TELNET_FLOW = {
    "type": "NETFLOW_V5", "time_received_ns": 1791323155565530742, "sequence_num": 0,
    "sampling_rate": 0, "sampler_address": "203.0.113.1",
    "time_flow_start_ns": 1791295190000000000, "time_flow_end_ns": 1791295192000000000,
    "bytes": 900, "packets": 12, "src_addr": "192.0.2.10", "dst_addr": "198.51.100.20",
    "etype": "IPv4", "proto": "TCP", "src_port": 49152, "dst_port": 23,
    "icmp_type": 0, "icmp_code": 0,
}


def flow_folder(tmp_path: Path) -> Path:
    folder = tmp_path / "netflow"
    folder.mkdir()
    shutil.copy(FIXTURE, folder / "goflow2.json")
    return folder


def test_one_flow_becomes_a_conn_record():
    assert to_conn(TELNET_FLOW) == {
        "ts": 1791295190.0,
        "uid": flow_uid(TELNET_FLOW),
        "id.orig_h": "192.0.2.10", "id.orig_p": 49152,
        "id.resp_h": "198.51.100.20", "id.resp_p": 23,
        "proto": "tcp", "duration": 2.0,
        "orig_bytes": 900, "resp_bytes": 0,
        "mg_source": "netflow",
    }


def test_uid_is_deterministic_and_ignores_the_receive_time():
    again = dict(TELNET_FLOW, time_received_ns=1791399999000000000)  # read again later
    other = dict(TELNET_FLOW, bytes=901)  # a different flow
    assert flow_uid(TELNET_FLOW) == flow_uid(dict(TELNET_FLOW)) == flow_uid(again)
    assert flow_uid(other) != flow_uid(TELNET_FLOW)
    assert flow_uid(TELNET_FLOW).startswith("N") and len(flow_uid(TELNET_FLOW)) == 18


def test_netflow_v5_icmp_type_and_code_come_from_the_destination_port():
    ping = dict(TELNET_FLOW, proto="ICMP", src_port=0, dst_port=8 * 256 + 0)  # echo request
    conn = to_conn(ping)
    assert (conn["proto"], conn["id.orig_p"], conn["id.resp_p"]) == ("icmp", 8, 0)


def test_ipfix_icmp_uses_the_icmp_fields():
    ping = dict(TELNET_FLOW, type="IPFIX", proto="ICMP", dst_port=0, icmp_type=3, icmp_code=1)
    conn = to_conn(ping)
    assert (conn["id.orig_p"], conn["id.resp_p"]) == (3, 1)


def test_accepts_a_goflow2_folder_and_a_single_file(tmp_path):
    folder = flow_folder(tmp_path)
    assert NetflowAdapter().accepts(folder)
    assert NetflowAdapter().accepts(folder / "goflow2.json")
    assert pick_adapter(folder).name == "netflow"


def test_does_not_steal_other_inputs(tmp_path, fixture_dir, pcap_file):
    adapter = NetflowAdapter()
    zeek_folder = fixture_dir("telnet")  # conn.log + eve.json
    assert not adapter.accepts(zeek_folder)
    assert not adapter.accepts(zeek_folder / "eve.json")
    assert not adapter.accepts(pcap_file("telnet"))
    # A Zeek log folder that also holds a goflow2 file still belongs to ZeekLogAdapter.
    mixed = flow_folder(tmp_path)
    shutil.copy(zeek_folder / "conn.log", mixed / "conn.log")
    assert not adapter.accepts(mixed)
    assert pick_adapter(mixed).name == "zeek-logs"
    # A live sensor folder (zeek/<interval>/) belongs to LiveSensorAdapter.
    sensor = tmp_path / "sensor"
    (sensor / "zeek" / "2026-10-06-1400").mkdir(parents=True)
    shutil.copy(FIXTURE, sensor / "goflow2.json")
    assert not adapter.accepts(sensor)
    assert pick_adapter(sensor).name == "live"
    # An empty folder and a folder of other JSON are not flows.
    other = tmp_path / "other"
    other.mkdir()
    assert not adapter.accepts(other)
    (other / "settings.json").write_text('{"type": "settings"}\n')
    assert not adapter.accepts(other)


def test_to_zeek_logs_writes_a_sorted_conn_log(tmp_path):
    log_dir = NetflowAdapter().to_zeek_logs(flow_folder(tmp_path), tmp_path / "work")
    records = list(read_log(log_dir, "conn.log"))
    assert len(records) == 7  # 5 NetFlow v5 + 1 NetFlow v9 + 1 IPFIX
    assert [r["ts"] for r in records] == sorted(r["ts"] for r in records)
    assert {r["mg_source"] for r in records} == {"netflow"}
    ssh = [r for r in records if r["id.resp_p"] == 22]  # the NetFlow v9 flow
    assert ssh[0]["id.orig_h"] == "192.0.2.12" and ssh[0]["orig_bytes"] == 4200


def test_same_files_give_the_same_conn_log(tmp_path):
    folder = flow_folder(tmp_path)
    first = NetflowAdapter().to_zeek_logs(folder, tmp_path / "a") / "conn.log"
    second = NetflowAdapter().to_zeek_logs(folder, tmp_path / "b") / "conn.log"
    assert first.read_bytes() == second.read_bytes()


def test_duplicates_and_a_half_written_line_are_skipped(tmp_path):
    folder = flow_folder(tmp_path)
    lines = FIXTURE.read_text().splitlines()
    # The same records again in a second file, then a line goflow2 is still writing.
    (folder / "goflow2-copy.json").write_text("\n".join(lines) + "\n" + lines[0][:40])
    log_dir = NetflowAdapter().to_zeek_logs(folder, tmp_path / "work")
    assert len(list(read_log(log_dir, "conn.log"))) == 7


def test_normalizer_reads_the_result_as_netflow(tmp_path):
    log_dir = NetflowAdapter().to_zeek_logs(flow_folder(tmp_path), tmp_path / "work")
    events = normalize(log_dir, sensor_id="router")
    assert len(events) == 7
    assert {(e["source"], e["kind"], e["sensor_id"]) for e in events} == {
        ("netflow", "conn", "router")}
    telnet = [e for e in events if e["dst_port"] == 23][0]
    assert (telnet["src_ip"], telnet["dst_ip"], telnet["proto"]) == (
        "192.0.2.10", "198.51.100.20", "tcp")
    assert (telnet["bytes_out"], telnet["bytes_in"]) == (900, 0)


def test_zeek_conn_records_stay_zeek(fixture_dir):
    events = normalize(fixture_dir("telnet"), sensor_id="pcap")
    assert {e["source"] for e in events if e["log"] == "conn.log"} == {"zeek"}


def test_analyze_flow_only_data(tmp_path):
    report = analyze(flow_folder(tmp_path), tmp_path / "work", explain=False)
    assert report["input"]["adapter"] == "netflow"
    assert report["findings"] == []  # no payload: no payload rule can fire
    assert len(report["events"]) == 7
    assert report["tools"] == {"zeek": False, "suricata": False}


def test_uploaded_flow_file_reaches_the_timeline(tmp_path):
    # The dashboard upload (and POST /api/ingest) store the file without its name,
    # so NetflowAdapter recognises one goflow2 file by its first line.
    from fastapi.testclient import TestClient

    from maxguard.api.app import create_app

    client = TestClient(create_app(tmp_path / "data", explain=False))
    with FIXTURE.open("rb") as f:
        reply = client.post("/api/analyses", files={"file": ("goflow2.json", f)})
    assert reply.status_code == 200, reply.text
    assert reply.json()["findings"] == 0
    events = client.get("/api/events", params={"ip": "192.0.2.10"}).json()
    assert len(events) == 5 and {e["source"] for e in events} == {"netflow"}  # 4 out, 1 in


def test_damaged_records_are_skipped_not_fatal(tmp_path):
    # An upload is untrusted: a record goflow2 would never write is skipped, the
    # good records still arrive, and nothing raises (a crash would be a 500).
    bad_records = [
        dict(TELNET_FLOW, bytes="900"),                 # text, not a number
        dict(TELNET_FLOW, dst_port=[23]),               # a list
        dict(TELNET_FLOW, bytes=2**70),                 # too large for the event store
        dict(TELNET_FLOW, time_flow_start_ns=-5),       # negative time
        dict(TELNET_FLOW, src_addr={"ip": "192.0.2.10"}),
        dict(TELNET_FLOW, dst_addr=None),
        dict(TELNET_FLOW, src_addr="not an address"),
    ]
    lines = [json.dumps(TELNET_FLOW)] + [json.dumps(r) for r in bad_records]
    lines += ['{"type": "IPFIX", "src_addr": "192.0.2.1", "bytes": 1e400}',
              "[" * 100_000 + "]" * 100_000]  # deeper than Python's recursion limit
    upload = tmp_path / "upload"
    upload.write_text("\n".join(lines) + "\n")
    assert NetflowAdapter().accepts(upload)
    records = list(read_log(NetflowAdapter().to_zeek_logs(upload, tmp_path / "w"), "conn.log"))
    assert [r["uid"] for r in records] == [flow_uid(TELNET_FLOW)]


def test_icmp_type_and_code_must_fit_in_a_byte():
    with pytest.raises(ValueError):
        to_conn(dict(TELNET_FLOW, type="IPFIX", proto="ICMP", icmp_type=300))


def test_uid_does_not_depend_on_the_order_of_the_fields():
    # Another goflow2 version may write the same fields in another order.
    reordered = dict(reversed(list(TELNET_FLOW.items())))
    assert flow_uid(reordered) == flow_uid(TELNET_FLOW)


def test_flow_without_flow_times_uses_the_receive_time():
    no_times = dict(TELNET_FLOW, time_flow_start_ns=0, time_flow_end_ns=0)
    conn = to_conn(no_times)
    assert (conn["ts"], conn["duration"]) == (1791323155.565531, 0.0)


def test_sflow_and_other_json_with_src_addr_are_not_flows(tmp_path):
    sflow = dict(TELNET_FLOW, type="SFLOW_5")  # sampled packets, not flow records
    for name, record in [("sflow", sflow), ("other", {"src_addr": "192.0.2.10"})]:
        path = tmp_path / name
        path.write_text(json.dumps(record) + "\n")
        assert not NetflowAdapter().accepts(path)
```

Run them with the tests of the two files you changed:

```bash
pytest tests/unit/test_netflow.py tests/unit/test_normalize.py tests/unit/test_pipeline.py -q
```

Expected output:

```text
....................................................................                         [100%]
68 passed in 1.21s
```

**Step 6.** Create the flow generator `scripts/send_test_flows.py`. It packs NetFlow v5, v9 and IPFIX packets by hand with `struct`, so you can see exactly what a router sends:

```python
"""Send a few made-up flow records to a NetFlow collector (Jakub, JAK-10 step 6).

NetFlow v5, NetFlow v9 and IPFIX, each with its own header. Only documentation
addresses (RFC 5737). Fixed times, so every run sends the same bytes. Send them
only to your own collector (docker/netflow-compose.yaml): the records are fake.

    python3 scripts/send_test_flows.py <collector-host> [port]
"""

from __future__ import annotations

import socket
import struct
import sys

EXPORT_TIME = 1791295200  # 2026-10-06 14:00:00 UTC
UPTIME_MS = 600_000       # the router has been up for 10 minutes
TCP, UDP, ICMP = 6, 17, 1


def ip(text: str) -> bytes:
    return socket.inet_aton(text)


# ---------- NetFlow v5 (fixed layout: 24-byte header, 48-byte records) ----------

def v5_record(src: str, dst: str, sport: int, dport: int, proto: int,
              packets: int, octets: int, first_ms: int, last_ms: int) -> bytes:
    """One NetFlow v5 flow record. first/last are router uptimes in milliseconds."""
    tcp_flags = 0x1B if proto == TCP else 0  # FIN SYN PSH ACK
    return struct.pack("!4s4s4sHHIIIIHHBBBBHHBBH",
                       ip(src), ip(dst), ip("0.0.0.0"), 1, 2,  # next hop, in/out interface
                       packets, octets, first_ms, last_ms,
                       sport, dport, 0, tcp_flags, proto, 0,   # pad, flags, protocol, ToS
                       0, 0, 24, 24, 0)                        # AS numbers, masks, pad


def v5_packet(records: list[bytes], sequence: int) -> bytes:
    header = struct.pack("!HHIIIIBBH", 5, len(records), UPTIME_MS, EXPORT_TIME, 0,
                         sequence, 0, 0, 0)
    return header + b"".join(records)


# ---------- NetFlow v9 (RFC 3954) and IPFIX (RFC 7011): template, then data ----------

# (field type, length): IPv4 src, IPv4 dst, src port, dst port, protocol, bytes, packets
V9_FIELDS = [(8, 4), (12, 4), (7, 2), (11, 2), (4, 1), (1, 4), (2, 4), (22, 4), (21, 4)]
#                                                        FIRST_SWITCHED^  ^LAST_SWITCHED
IPFIX_FIELDS = [(8, 4), (12, 4), (7, 2), (11, 2), (4, 1), (1, 8), (2, 8), (152, 8), (153, 8)]
#                                              flowStartMilliseconds^    ^flowEndMilliseconds


def template_body(template_id: int, fields: list[tuple[int, int]]) -> bytes:
    body = struct.pack("!HH", template_id, len(fields))
    return body + b"".join(struct.pack("!HH", t, n) for t, n in fields)


def flow_set(set_id: int, body: bytes) -> bytes:
    return struct.pack("!HH", set_id, 4 + len(body)) + body


def v9_packet(sequence: int) -> bytes:
    """Template 256 (flowset id 0), then one data record: an SSH flow."""
    data = struct.pack("!4s4sHHBIIII", ip("192.0.2.12"), ip("198.51.100.22"), 50022, 22,
                       TCP, 4200, 30, UPTIME_MS - 8000, UPTIME_MS - 1000)
    flowsets = flow_set(0, template_body(256, V9_FIELDS)) + flow_set(256, data)
    # version, count (records incl. template), sysUptime, unix secs, sequence, source id
    return struct.pack("!HHIIII", 9, 2, UPTIME_MS, EXPORT_TIME, sequence, 1) + flowsets


def ipfix_packet(sequence: int) -> bytes:
    """Template 256 (set id 2), then one data record: an HTTPS flow."""
    start_ms = EXPORT_TIME * 1000 - 5000
    data = struct.pack("!4s4sHHBQQQQ", ip("192.0.2.11"), ip("203.0.113.5"), 50000, 443,
                       TCP, 5200, 14, start_ms, start_ms + 3000)
    sets = flow_set(2, template_body(256, IPFIX_FIELDS)) + flow_set(256, data)
    return struct.pack("!HHIII", 10, 16 + len(sets), EXPORT_TIME, sequence, 1) + sets


def main() -> None:
    host = sys.argv[1]
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 2055
    telnet = v5_record("192.0.2.10", "198.51.100.20", 49152, 23, TCP, 12, 900, 590_000, 592_000)
    answer = v5_record("198.51.100.20", "192.0.2.10", 23, 49152, TCP, 10, 1400, 590_010, 592_000)
    web = v5_record("192.0.2.10", "198.51.100.20", 49153, 80, TCP, 6, 640, 595_000, 595_500)
    dns = v5_record("192.0.2.10", "198.51.100.53", 40000, 53, UDP, 1, 60, 596_000, 596_000)
    ping = v5_record("192.0.2.10", "198.51.100.20", 0, 8 * 256 + 0, ICMP, 1, 84,
                     597_000, 597_000)  # echo request: type 8, code 0
    packets = [v5_packet([telnet, answer], 0), v5_packet([web, dns, ping], 2),
               v9_packet(0), ipfix_packet(0)]
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        for packet in packets:
            sock.sendto(packet, (host, port))
    print(f"sent {len(packets)} packets (2 NetFlow v5, 1 NetFlow v9, 1 IPFIX) to {host}:{port}")


if __name__ == "__main__":
    main()
```

**Step 7.** Prove it end to end: start the collector on `127.0.0.1`, send the test flows, start a new file the way you would every hour (`mv`, then `SIGHUP`), and analyze the finished file:

```bash
mkdir -p data/netflow data/netflow-done
export MAXGUARD_NETFLOW_ADDRESS=127.0.0.1 MAXGUARD_NETFLOW_DATA="$PWD/data/netflow"
export MAXGUARD_UID=$(id -u) MAXGUARD_GID=$(id -g)
NF="docker compose -p maxguard-netflow-test -f docker/netflow-compose.yaml"
$NF up -d 2> /dev/null
for i in $(seq 1 40); do $NF logs goflow2 | grep -q 'starting collection' && break; sleep 0.5; done
python scripts/send_test_flows.py 127.0.0.1
for i in $(seq 1 40); do [ "$(wc -l < data/netflow/goflow2.json)" -ge 7 ] && break; sleep 0.5; done
echo "flows written: $(wc -l < data/netflow/goflow2.json)"
mv data/netflow/goflow2.json data/netflow-done/2026-10-06-1400.json
$NF kill -s HUP goflow2 2> /dev/null
for i in $(seq 1 20); do [ -f data/netflow/goflow2.json ] && break; sleep 0.5; done
ls data/netflow
$NF down 2> /dev/null
maxguard analyze data/netflow-done --no-ai -o data/netflow-report.json
python - <<'EOF'
import json
from pathlib import Path
from maxguard.adapters.netflow import NetflowAdapter
from maxguard.events.normalize import normalize

report = json.loads(Path("data/netflow-report.json").read_text())
print("findings:", len(report["findings"]), "| zeek and suricata ran:", report["tools"])
logs = NetflowAdapter().to_zeek_logs(Path("data/netflow-done"), Path("data/netflow-work"))
for e in normalize(logs, "router"):
    print(e["source"], e["uid"], e["src_ip"], e["src_port"], "->", e["dst_ip"], e["dst_port"], e["summary"])
EOF
```

Expected output:

```text
sent 4 packets (2 NetFlow v5, 1 NetFlow v9, 1 IPFIX) to 127.0.0.1:2055
flows written: 7
goflow2.json
maxguard: 0 finding(s), report written to data/netflow-report.json
findings: 0 | zeek and suricata ran: {'suricata': False, 'zeek': False}
netflow N21c703d6223fff025 192.0.2.10 49152 -> 198.51.100.20 23 tcp/23 out=900 in=0
netflow Nd75eaed68a20131ed 198.51.100.20 23 -> 192.0.2.10 49152 tcp/49152 out=1400 in=0
netflow Nf80b3e8c076fe446f 192.0.2.12 50022 -> 198.51.100.22 22 tcp/22 out=4200 in=0
netflow N328b3296b8be401c5 192.0.2.11 50000 -> 203.0.113.5 443 tcp/443 out=5200 in=0
netflow N775574a24a9332000 192.0.2.10 49153 -> 198.51.100.20 80 tcp/80 out=640 in=0
netflow Ne403487b7714c8d0a 192.0.2.10 40000 -> 198.51.100.53 53 udp/53 out=60 in=0
netflow N6d97c91022c3a171a 192.0.2.10 8 -> 198.51.100.20 0 icmp/0 out=84 in=0
```

*goflow2 runs with your user ID here, so you can read the files without `sudo`; on the console the default is 1000:1000, the first user.*

No rule fires, and that is correct. The cleartext, TLS and certificate rules read Zeek's protocol logs (`ftp.log`, `ssl.log`, ...), which only exist when someone looked inside the packets. A flow to port 23 is not proof of Telnet, and MaxGuard only reports what it can prove. What flows do give is the timeline (who talked to whom, how much, when): upload the finished `.json` file on the dashboard and open the timeline for `192.0.2.10`.

**Step 8.** **On the lab** (*not run — verify on hardware*): if your router can export NetFlow or IPFIX, point it at the console's LAN address, UDP port 2055, start the collector with `MAXGUARD_NETFLOW_ADDRESS=<console address>`, and check that `/data/netflow/goflow2.json` grows. Also run the collector once on the Raspberry Pi 5 (the arm64 image was not run in planning). Many home routers cannot export flows at all; write down what yours can do in the issue.

**Step 9.** Commit, push, and open the pull request:

```bash
git add -A
git status          # only this task's files: nothing from .venv/, data/ or lab/captures/
git commit -m "feat: NetFlow/IPFIX input through goflow2 (JAK-10)"
git push -u origin HEAD
```

`HEAD` means "the branch I am on", so you do not have to retype its name. Open the repository on github.com: a yellow bar shows your branch with a **Compare & pull request** button. Click it, keep the title `feat: NetFlow/IPFIX input through goflow2 (JAK-10)`, fill in the template (paste the real output of the commands above under **How I tested it**), write `Closes #<issue number>` (this task's issue), and pick **@JWinborne1** under **Reviewers**. Click **Create pull request**, then fix anything CI or the reviewer finds with new commits on the same branch.

#### How to test

The tests pass, the proof prints seven flows and zero findings, and an uploaded flow file shows on the timeline page.

#### What you just did and why

Many small offices have a router that can export flows but no mirror port. Flow records carry no payload, so they cannot show a cleartext password, but they do show who talked to whom, how much, and when, which is enough for the timeline, baselines, and preview-before-you-block. Converting them to Zeek's `conn.log` shape means no rule or page needs to know they came from NetFlow.

#### Pull request checklist

- [ ] `ruff check .` prints `All checks passed!`
- [ ] `pytest -m "not integration" -q` passes on your laptop
- [ ] The pull request title has the form `type: summary (TASK-ID)` and the body says `Closes #<issue number>`
- [ ] No secrets, passwords, email addresses, personal data, or captures from a real network (CLAUDE.md rule 6)
- [ ] Any new dependency has a row in `docs/DEPENDENCIES.md` with its license
- [ ] CI is green and your reviewer approved
- [ ] The collector image is pinned by version and digest
- [ ] Test data uses only documentation addresses (RFC 5737)
- [ ] Jaiden reviewed the new `source` value

### JAK-11: Host agent for one computer

**Due:** Spring S12 (due Fri Apr 23, 2027) · **Milestone:** `S12 v2.0 feature freeze` · **Needs first:** [JAI-07](jaiden.md#jai-07-the-api-uploads-alerts-events-live-updates-sensor-ingest) · **Kind:** code, tested

**Issue labels:** `type:task` `phase:spring` `owner:jakub` `area:sensor` `needs-hardware`

> **Needs hardware.** Steps that use the Raspberry Pi, the switch or other devices were not run during planning; they are marked *not run — verify on hardware*.

#### Goal

For a home with no mirror port: a small agent on one computer captures that computer's own traffic with the operating system's built-in tools, in rotating files, and uploads each finished file to the console's `POST /api/ingest`.

#### Prerequisites

JAI-07 is merged (ingest endpoint and the ingest-only app on port 8001).

#### Steps

**Step 1.** Update `main` and create your branch for this task (one branch per task):

```bash
cd ~/projects/maxguard
source .venv/bin/activate
git checkout main && git pull
git checkout -b jakub/host-agent
```

If `source .venv/bin/activate` fails, you have not made the virtual environment yet: do Week 0 section 0.11 first.

**Step 2.** Create `maxguard/sensor/agent.py`:

```python
"""Host agent: capture this computer's own traffic and upload it (Jakub, JAK-11).

For a home with no mirror port. The agent runs on one computer, captures only
that computer's traffic with the operating system's built-in tools (no extra
driver), writes one capture file per interval, and uploads every finished file
to the console's POST /api/ingest (the LAN port 8001, docker/compose.lan.yaml).

    sudo python -m maxguard.sensor.agent --config ~/.config/maxguard/agent.toml

Safety rules:
- The console must be YOUR OWN computer running MaxGuard. The agent sends your
  traffic to it, so never point console_url at anyone else's machine.
- Ingest is off on the console unless MAXGUARD_INGEST_TOKEN is set there
  (POST /api/ingest answers 404); the agent's token must be the same value.
- The token lives in a config file outside the repository (default
  ~/.config/maxguard/agent.toml, or %APPDATA%\\MaxGuard\\agent.toml on Windows),
  and the agent refuses a config file other users can read.
- The capture only listens (CLAUDE.md rule 5). Port 8001 is plain HTTP, so the
  token and the captures cross your LAN unencrypted: use a wired or trusted network.
- The upload goes straight to console_url: proxy variables (HTTP_PROXY ...) and
  ~/.netrc are ignored, so your traffic never leaves through a proxy (rule 1).

Capture commands, every flag checked against the manuals:
- Linux and macOS: tcpdump (tcpdump(1), https://www.tcpdump.org/manpages/tcpdump.1.html)
    -i <interface>  capture on this interface (left out: tcpdump picks the lowest
                    numbered interface that is up, not loopback)
    -n              do not turn addresses into names (no DNS lookups of its own)
    -G <seconds>    rotate the file given with -w every <seconds> seconds
    -w <pattern>    write raw packets to a file; with -G the name is a strftime(3)
                    pattern, e.g. capture-%Y%m%d-%H%M%S.pcap
    -Z <user>       after opening the capture device, but before opening any
                    output file, drop root and run as <user>. So the files belong to
                    <user>, and <user> must be able to write the spool folder.
  tcpdump fills the time pattern with localtime(); the agent starts it with TZ=UTC
  so the names are UTC and sort in time order all year (no daylight saving jumps).
  tcpdump starts the next file only when a packet arrives after the interval, so
  the newest file is always the one still being written: it is never uploaded.
- Windows: pktmon (built in since Windows 10 1809; run as Administrator)
    https://learn.microsoft.com/windows-server/administration/windows-commands/pktmon-start
    https://learn.microsoft.com/windows-server/administration/windows-commands/pktmon-etl2pcap
    pktmon start --capture --comp nics --pkt-size 0 --file-name <file.etl>
        --capture: capture packets; --comp nics: only at the network cards (pktmon
        otherwise logs a packet once for every component it passes through);
        --pkt-size 0: the whole packet (the default keeps only 128 bytes)
    pktmon stop
    pktmon etl2pcap <file.etl> --out <file.pcapng>
  pktmon rotates only by size, not by time, so the agent stops and restarts it
  every interval; a stopped .etl file is finished and is converted to pcapng.
  pktmon's default log mode is "circular" with a 512 MB file (--file-size): if
  one interval holds more than that, its oldest packets are overwritten.
"""

from __future__ import annotations

import argparse
import os
import platform
import re
import shutil
import stat
import subprocess
import sys
import time
import tomllib
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import requests

SENSOR_ID = re.compile(r"[A-Za-z0-9._-]{1,64}")  # what POST /api/ingest accepts
CAPTURE_PATTERN = "capture-%Y%m%d-%H%M%S"        # strftime pattern; UTC
UPLOAD_TIMEOUT = (10, 600)  # seconds to connect, seconds to wait for the analysis
CHECK_EVERY = 10            # seconds between looks at the spool folder (Linux, macOS)
KEEP_UPLOADED = 4           # uploaded files kept on this computer, newest first
UPLOADED_DIR = "uploaded"   # inside the spool folder
REJECTED_DIR = "rejected"   # files the console refused: not sent again
REJECTED_STATUSES = (400, 413, 422)  # answers that will be the same next time


@dataclass
class AgentConfig:
    console_url: str          # e.g. "http://192.168.50.20:8001" (your own console)
    token: str                # the console's MAXGUARD_INGEST_TOKEN
    spool_dir: Path           # where capture files wait for upload
    sensor_id: str = "agent"  # this computer's name in every event
    interface: str = ""       # "" = the capture tool's default
    rotate_seconds: int = 900  # 15 minutes, like the live sensor
    capture_user: str = ""    # tcpdump -Z: who owns the files (Linux, macOS)


# ---------- Config file ----------

def default_config_path() -> Path:
    """Outside the repository, in the user's own settings folder."""
    if platform.system() == "Windows":
        return Path(os.environ.get("APPDATA", Path.home())) / "MaxGuard" / "agent.toml"
    return Path.home() / ".config" / "maxguard" / "agent.toml"


def check_private(path: Path) -> None:
    """The file holds the token: refuse it if other users may read it (Linux, macOS)."""
    if platform.system() == "Windows":
        return  # Windows uses ACLs, not mode bits; %APPDATA% is private by default
    if path.stat().st_mode & (stat.S_IRWXG | stat.S_IRWXO):
        raise ValueError(f"{path} can be read by other users: run  chmod 600 {path}")


def load_config(path: Path) -> AgentConfig:
    check_private(path)
    with path.open("rb") as f:
        raw = tomllib.load(f)
    config = AgentConfig(
        console_url=str(raw["console_url"]).rstrip("/"),
        token=str(raw["token"]),
        spool_dir=Path(raw["spool_dir"]).expanduser(),
        sensor_id=str(raw.get("sensor_id", "agent")),
        interface=str(raw.get("interface", "")),
        rotate_seconds=int(raw.get("rotate_seconds", 900)),
        capture_user=str(raw.get("capture_user", "")),
    )
    check_config(config)
    return config


def check_config(config: AgentConfig) -> None:
    if not config.console_url.startswith(("http://", "https://")):
        raise ValueError("console_url must start with http:// or https://")
    if not SENSOR_ID.fullmatch(config.sensor_id):
        raise ValueError("sensor_id: 1-64 characters, letters, digits, '.', '_' or '-'")
    if not config.token:
        raise ValueError("token is empty: copy the console's MAXGUARD_INGEST_TOKEN")
    if config.rotate_seconds < 60:
        raise ValueError("rotate_seconds must be at least 60")


# ---------- Capture commands ----------

def tcpdump_command(config: AgentConfig) -> list[str]:
    """Linux and macOS. Run it with TZ=UTC in its environment (see capture_env)."""
    if not config.capture_user:
        raise ValueError("set capture_user: tcpdump -Z drops root to that user")
    command = ["tcpdump"]
    if config.interface:
        command += ["-i", config.interface]
    # tcpdump runs the WHOLE -w name through strftime, so a "%" in the folder
    # name must be written "%%" to stay a plain "%".
    folder = str(config.spool_dir).replace("%", "%%")
    pattern = f"{folder}{os.sep}{CAPTURE_PATTERN}.pcap"
    command += ["-n", "-G", str(config.rotate_seconds), "-w", pattern,
                "-Z", config.capture_user]
    return command


def capture_env() -> dict[str, str]:
    """tcpdump fills the file name with local time: make that UTC."""
    return {**os.environ, "TZ": "UTC"}


def pktmon_start_command(etl_file: Path) -> list[str]:
    return ["pktmon", "start", "--capture", "--comp", "nics", "--pkt-size", "0",
            "--file-name", str(etl_file)]


def pktmon_stop_command() -> list[str]:
    return ["pktmon", "stop"]


def pktmon_convert_command(etl_file: Path) -> list[str]:
    return ["pktmon", "etl2pcap", str(etl_file), "--out", str(etl_file.with_suffix(".pcapng"))]


def capture_command(system: str, config: AgentConfig, now: float) -> list[str]:
    """The command that starts the capture on this operating system (platform.system())."""
    if system in ("Linux", "Darwin"):
        return tcpdump_command(config)
    if system == "Windows":
        return pktmon_start_command(etl_name(config.spool_dir, now))
    raise ValueError(f"no built-in capture tool known for {system!r}")


def etl_name(spool_dir: Path, now: float) -> Path:
    stamp = datetime.fromtimestamp(now, UTC).strftime(CAPTURE_PATTERN)
    return spool_dir / f"{stamp}.etl"


# ---------- Which files are finished ----------

def finished_files(spool_dir: Path, *, capture_running: bool) -> list[Path]:
    """Capture files that are complete, oldest first.

    The names are UTC times, so sorting by name sorts by time. While the capture
    runs, the newest file is still being written: never upload it."""
    files = sorted(p for p in spool_dir.glob("capture-*") if p.suffix in (".pcap", ".pcapng"))
    if capture_running and files:
        files = files[:-1]
    return files


# ---------- Upload ----------

def console_session() -> requests.Session:
    """A requests session that talks only to console_url.

    trust_env=False: requests would otherwise send the upload through a proxy named
    in HTTP_PROXY/HTTPS_PROXY, and replace our Bearer header with a password from
    ~/.netrc. Both were seen in a test; neither may happen to your captures."""
    session = requests.Session()
    session.trust_env = False
    return session


def upload(path: Path, config: AgentConfig, session=None) -> int | None:
    """POST one file to the console. Returns the HTTP status, or None if unreachable."""
    session = session or console_session()
    url = f"{config.console_url}/api/ingest"
    headers = {"Authorization": f"Bearer {config.token}"}
    try:
        with path.open("rb") as f:
            reply = session.post(url, headers=headers, data={"sensor_id": config.sensor_id},
                                 files={"file": (path.name, f, "application/octet-stream")},
                                 timeout=UPLOAD_TIMEOUT)
    except requests.RequestException as err:
        print(f"console not reachable, will retry {path.name}: {err}", file=sys.stderr)
        return None
    return reply.status_code


def upload_finished(config: AgentConfig, *, capture_running: bool, session=None) -> int:
    """Upload every finished file. Returns how many the console accepted.

    A file counts as uploaded only after a 2xx answer; then it moves to uploaded/.
    400 (not a capture), 413 (too large) and 422 (Zeek or Suricata failed on this
    file) will never work: the file moves to rejected/, so one bad file cannot
    block every later one. Anything else (console down, 401 wrong token, 5xx) is
    tried again later."""
    session = session or console_session()
    accepted = 0
    for path in finished_files(config.spool_dir, capture_running=capture_running):
        status = upload(path, config, session)
        if status is not None and 200 <= status < 300:
            move_into(path, config.spool_dir / UPLOADED_DIR)
            accepted += 1
        elif status in REJECTED_STATUSES:
            print(f"console refused {path.name} ({status}): moved to {REJECTED_DIR}/",
                  file=sys.stderr)
            move_into(path, config.spool_dir / REJECTED_DIR)
        else:
            if status is not None:
                print(f"upload of {path.name} failed ({status}), will retry", file=sys.stderr)
            break  # keep the order: try the oldest file again next time
    prune_uploaded(config.spool_dir / UPLOADED_DIR)
    return accepted


def move_into(path: Path, folder: Path) -> Path:
    folder.mkdir(exist_ok=True)
    return path.replace(folder / path.name)


def prune_uploaded(folder: Path, keep: int = KEEP_UPLOADED) -> None:
    """The console has the data now; keep only the newest few files here."""
    if not folder.is_dir():
        return
    files = sorted(p for p in folder.iterdir() if p.is_file())
    for old in files[:-keep] if keep else files:
        old.unlink()


# ---------- Main loops (they start a real capture: never called by tests) ----------

def prepare_spool(config: AgentConfig, system: str) -> None:
    """Create the spool folder if it is missing.

    tcpdump -Z writes the files as capture_user, but the agent runs as root (sudo),
    so a folder it creates would belong to root and tcpdump could not write into
    it. A folder the agent creates is therefore given to capture_user. An existing
    folder is never changed: it may be shared, and it is yours to set up."""
    if config.spool_dir.is_dir():
        return
    config.spool_dir.mkdir(parents=True)
    if system in ("Linux", "Darwin") and config.capture_user and os.geteuid() == 0:
        shutil.chown(config.spool_dir, user=config.capture_user)


def run_tcpdump(config: AgentConfig) -> int:
    """Capture and upload until tcpdump stops. Returns tcpdump's exit code.

    Not 0 means tcpdump could not capture (it printed why, for example a spool
    folder capture_user cannot write)."""
    capture = subprocess.Popen(tcpdump_command(config), env=capture_env())
    try:
        while capture.poll() is None:
            upload_finished(config, capture_running=True)
            time.sleep(CHECK_EVERY)
    finally:
        capture.terminate()  # SIGTERM: tcpdump closes the current file cleanly
        capture.wait()
        upload_finished(config, capture_running=False)
    return capture.returncode


def run_pktmon(config: AgentConfig) -> None:
    while True:
        etl_file = etl_name(config.spool_dir, time.time())
        subprocess.run(pktmon_start_command(etl_file), check=True)
        try:
            time.sleep(config.rotate_seconds)
        finally:
            subprocess.run(pktmon_stop_command(), check=True)
            convert_etl(etl_file)
        upload_finished(config, capture_running=False)


def convert_etl(etl_file: Path) -> None:
    """ETL -> pcapng (MaxGuard reads pcapng), then delete the ETL file."""
    subprocess.run(pktmon_convert_command(etl_file), check=True)
    etl_file.unlink()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="MaxGuard host agent (capture + upload)")
    parser.add_argument("--config", type=Path, default=default_config_path())
    parser.add_argument("--upload-only", action="store_true",
                        help="upload every capture file once and exit (no capture); "
                             "only while the agent is stopped, because it also sends "
                             "the newest file")
    args = parser.parse_args(argv)
    config = load_config(args.config)
    system = platform.system()
    prepare_spool(config, system)
    if args.upload_only:
        print(f"uploaded {upload_finished(config, capture_running=False)} file(s)")
        return 0
    if system == "Windows":
        run_pktmon(config)
    elif system in ("Linux", "Darwin"):
        return run_tcpdump(config)
    else:
        print(f"no built-in capture tool known for {system}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

The docstring lists every capture flag with the manual it comes from. Four decisions to understand. tcpdump runs as root only long enough to open the network card, then `-Z` drops to your normal user before it writes any file. tcpdump names files with the *local* time, so the agent starts it with `TZ=UTC`: the names then sort in time order all year. The newest file is the one tcpdump is still writing, so it is never uploaded; a file counts as uploaded only after a `2xx` answer, goes to `rejected/` on 400, 413 or 422 (answers that would be the same next time, so one bad file cannot block the rest), and is retried (oldest first) on anything else. Windows' `pktmon` rotates only by size, so the agent stops and restarts it every interval and converts each finished `.etl` file to pcapng.

The security review added three more details. The upload uses a session with `trust_env = False`: by default `requests` would send your captures through any proxy in `HTTP_PROXY` and replace the token with a password from `~/.netrc`. A `%` in the spool folder's name is doubled, because tcpdump runs the whole `-w` name through `strftime`. And a spool folder the agent creates as root is given to `capture_user`, because tcpdump opens its files only after `-Z` dropped root.

**Step 3.** Create the tests `tests/unit/test_agent.py`. They check the command for each operating system and upload to a fake server and to the real ingest app through `TestClient`; no test ever starts a capture:

```python
"""Tests for the host agent (Jakub, JAK-11).

No test starts a capture: the commands are only built and compared. Uploads go
to a fake HTTP server on 127.0.0.1 and to the real ingest app through TestClient.
"""

from __future__ import annotations

import os
import shutil
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

from maxguard.sensor import agent
from maxguard.sensor.agent import AgentConfig

TOKEN = "test-token-" + "x" * 32  # made up; the API wants at least 32 characters
FLOW_FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "netflow" / "goflow2.json"


def make_config(spool: Path, **changes) -> AgentConfig:
    settings = {"console_url": "http://127.0.0.1:8001", "token": TOKEN, "spool_dir": spool,
                "sensor_id": "laptop", "interface": "eth0", "rotate_seconds": 900,
                "capture_user": "alex"}
    settings.update(changes)
    return AgentConfig(**settings)


def make_captures(spool: Path, *names: str) -> None:
    spool.mkdir(parents=True, exist_ok=True)
    for name in names:
        (spool / name).write_bytes(b"\xd4\xc3\xb2\xa1" + b"\0" * 20)  # a pcap header


# ---------- capture commands ----------

@pytest.mark.parametrize("system", ["Linux", "Darwin"])
def test_tcpdump_command(system, tmp_path):
    command = agent.capture_command(system, make_config(tmp_path), now=0)
    assert command == ["tcpdump", "-i", "eth0", "-n", "-G", "900",
                       "-w", str(tmp_path / "capture-%Y%m%d-%H%M%S.pcap"), "-Z", "alex"]


def test_tcpdump_without_interface_uses_its_default(tmp_path):
    command = agent.tcpdump_command(make_config(tmp_path, interface=""))
    assert "-i" not in command


def test_tcpdump_needs_a_user_to_drop_root_to(tmp_path):
    with pytest.raises(ValueError, match="capture_user"):
        agent.tcpdump_command(make_config(tmp_path, capture_user=""))


def test_percent_in_the_spool_folder_is_not_a_time_pattern(tmp_path):
    # tcpdump runs the whole -w name through strftime: "%d" in a folder name
    # would become the day of the month unless it is written "%%d".
    command = agent.tcpdump_command(make_config(tmp_path / "100%done"))
    assert command[command.index("-w") + 1] == str(
        tmp_path / "100%%done" / "capture-%Y%m%d-%H%M%S.pcap")


def test_tcpdump_names_files_in_utc():
    assert agent.capture_env()["TZ"] == "UTC"


def test_windows_commands(tmp_path):
    now = 1791295200.0  # 2026-10-06 14:00:00 UTC
    etl = tmp_path / "capture-20261006-140000.etl"
    assert agent.capture_command("Windows", make_config(tmp_path), now) == [
        "pktmon", "start", "--capture", "--comp", "nics", "--pkt-size", "0",
        "--file-name", str(etl)]
    assert agent.pktmon_stop_command() == ["pktmon", "stop"]
    assert agent.pktmon_convert_command(etl) == [
        "pktmon", "etl2pcap", str(etl), "--out", str(tmp_path / "capture-20261006-140000.pcapng")]


def test_unknown_system_is_refused(tmp_path):
    with pytest.raises(ValueError, match="no built-in capture tool"):
        agent.capture_command("Plan9", make_config(tmp_path), now=0)


# ---------- config file ----------

CONFIG_TEXT = f"""
console_url = "http://192.0.2.20:8001/"
token = "{TOKEN}"
spool_dir = "SPOOL"
sensor_id = "laptop"
capture_user = "alex"
"""


@pytest.mark.skipif(os.name == "nt", reason="mode bits are POSIX only")
def test_load_config(tmp_path):
    path = tmp_path / "agent.toml"
    path.write_text(CONFIG_TEXT.replace("SPOOL", str(tmp_path / "spool")))
    path.chmod(0o600)
    config = agent.load_config(path)
    assert config.console_url == "http://192.0.2.20:8001"  # trailing / removed
    assert (config.sensor_id, config.rotate_seconds, config.interface) == ("laptop", 900, "")


@pytest.mark.skipif(os.name == "nt", reason="mode bits are POSIX only")
def test_config_readable_by_others_is_refused(tmp_path):
    path = tmp_path / "agent.toml"
    path.write_text(CONFIG_TEXT.replace("SPOOL", str(tmp_path)))
    path.chmod(0o644)
    with pytest.raises(ValueError, match="chmod 600"):
        agent.load_config(path)


@pytest.mark.parametrize("change, message", [
    ({"sensor_id": "my laptop"}, "sensor_id"),
    ({"console_url": "192.0.2.20:8001"}, "http"),
    ({"token": ""}, "token"),
    ({"rotate_seconds": 5}, "rotate_seconds"),
])
def test_bad_settings_are_refused(tmp_path, change, message):
    with pytest.raises(ValueError, match=message):
        agent.check_config(make_config(tmp_path, **change))


# ---------- which files are finished ----------

def test_newest_file_is_not_finished_while_capturing(tmp_path):
    make_captures(tmp_path, "capture-20261006-141500.pcap", "capture-20261006-140000.pcap",
                  "capture-20261006-143000.pcap")
    (tmp_path / "capture-20261006-144500.etl").write_bytes(b"")  # pktmon still writing
    running = agent.finished_files(tmp_path, capture_running=True)
    assert [p.name for p in running] == ["capture-20261006-140000.pcap",
                                         "capture-20261006-141500.pcap"]
    stopped = agent.finished_files(tmp_path, capture_running=False)
    assert len(stopped) == 3


# ---------- uploads to a fake console on 127.0.0.1 ----------

class FakeConsole(BaseHTTPRequestHandler):
    status = 200
    requests: list[dict] = []

    def do_POST(self):
        body = self.rfile.read(int(self.headers["Content-Length"]))
        FakeConsole.requests.append({"path": self.path, "auth": self.headers["Authorization"],
                                     "type": self.headers["Content-Type"], "body": body})
        self.send_response(FakeConsole.status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"analysis_id": "a1", "findings": 0}')

    def log_message(self, *args):  # keep test output quiet
        pass


@pytest.fixture
def console():
    """A fake console on 127.0.0.1 (a free port). Yields its URL."""
    FakeConsole.status, FakeConsole.requests = 200, []
    server = ThreadingHTTPServer(("127.0.0.1", 0), FakeConsole)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_port}"
    server.shutdown()
    server.server_close()


def test_upload_sends_file_sensor_id_and_token(tmp_path, console):
    spool = tmp_path / "spool"
    make_captures(spool, "capture-20261006-140000.pcap", "capture-20261006-141500.pcap")
    config = make_config(spool, console_url=console)
    assert agent.upload_finished(config, capture_running=True) == 1
    sent = FakeConsole.requests[0]
    assert sent["path"] == "/api/ingest"
    assert sent["auth"] == f"Bearer {TOKEN}"
    assert sent["type"].startswith("multipart/form-data")
    assert b'name="sensor_id"\r\n\r\nlaptop' in sent["body"]
    assert b'name="file"; filename="capture-20261006-140000.pcap"' in sent["body"]
    # Uploaded after the 2xx; the file tcpdump is still writing was not touched.
    assert (spool / "uploaded" / "capture-20261006-140000.pcap").exists()
    assert (spool / "capture-20261006-141500.pcap").exists()
    assert len(FakeConsole.requests) == 1


def test_failed_upload_keeps_the_file(tmp_path, console):
    spool = tmp_path / "spool"
    make_captures(spool, "capture-20261006-140000.pcap", "capture-20261006-141500.pcap")
    FakeConsole.status = 401  # wrong token
    config = make_config(spool, console_url=console)
    assert agent.upload_finished(config, capture_running=False) == 0
    assert len(FakeConsole.requests) == 1  # stopped at the oldest file, keeps the order
    assert sorted(p.name for p in spool.glob("*.pcap")) == [
        "capture-20261006-140000.pcap", "capture-20261006-141500.pcap"]


@pytest.mark.parametrize("status", [400, 413, 422])
def test_refused_file_moves_to_rejected(tmp_path, console, status):
    """400 not a capture, 413 too large, 422 Zeek failed on it: the same next time."""
    spool = tmp_path / "spool"
    make_captures(spool, "capture-20261006-140000.pcap")
    FakeConsole.status = status
    agent.upload_finished(make_config(spool, console_url=console), capture_running=False)
    assert (spool / "rejected" / "capture-20261006-140000.pcap").exists()


def test_console_down_keeps_the_file(tmp_path, console):
    spool = tmp_path / "spool"
    make_captures(spool, "capture-20261006-140000.pcap")
    closed_port = make_config(spool, console_url="http://127.0.0.1:9")  # nothing listens
    assert agent.upload_finished(closed_port, capture_running=False) == 0
    assert (spool / "capture-20261006-140000.pcap").exists()


def test_upload_ignores_proxy_settings_and_netrc(tmp_path, console, monkeypatch):
    # A proxy variable must not reroute the captures, and a ~/.netrc entry for
    # the console must not replace the Bearer token with a password.
    home = tmp_path / "home"
    home.mkdir()
    (home / ".netrc").write_text("machine 127.0.0.1 login someone password not-the-token\n")
    (home / ".netrc").chmod(0o600)
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("NETRC", str(home / ".netrc"))
    for name in ("HTTP_PROXY", "http_proxy", "ALL_PROXY", "all_proxy"):
        monkeypatch.setenv(name, "http://127.0.0.1:9")  # nothing listens there
    for name in ("NO_PROXY", "no_proxy"):
        monkeypatch.delenv(name, raising=False)
    spool = tmp_path / "spool"
    make_captures(spool, "capture-20261006-140000.pcap")
    assert agent.upload_finished(make_config(spool, console_url=console),
                                 capture_running=False) == 1
    assert FakeConsole.requests[0]["auth"] == f"Bearer {TOKEN}"


def test_spool_folder_the_agent_creates_goes_to_capture_user(tmp_path, monkeypatch):
    # sudo: the agent is root, but tcpdump -Z writes as capture_user.
    given = []
    monkeypatch.setattr(agent.os, "geteuid", lambda: 0, raising=False)
    monkeypatch.setattr(agent.shutil, "chown", lambda path, user: given.append((path, user)))
    config = make_config(tmp_path / "spool")
    agent.prepare_spool(config, "Linux")
    assert config.spool_dir.is_dir() and given == [(config.spool_dir, "alex")]
    agent.prepare_spool(config, "Linux")  # it exists now: left alone
    assert len(given) == 1


def test_only_the_newest_uploaded_files_are_kept(tmp_path):
    folder = tmp_path / "uploaded"
    make_captures(folder, *[f"capture-20261006-14{m:02d}00.pcap" for m in range(0, 60, 10)])
    agent.prune_uploaded(folder, keep=2)
    assert sorted(p.name for p in folder.iterdir()) == [
        "capture-20261006-144000.pcap", "capture-20261006-145000.pcap"]


# ---------- the real ingest app ----------

# The agent passes timeout= like any requests call; TestClient warns that it ignores it.
@pytest.mark.filterwarnings("ignore:You should not use the 'timeout' argument")
def test_upload_to_the_real_ingest_app(tmp_path, monkeypatch):
    """The agent's request, answered by create_ingest_app (no network: TestClient).

    The console recognises a file by its content, not its name, so a goflow2 flow
    file stands in for a capture here (a real capture would need Zeek)."""
    from fastapi.testclient import TestClient

    from maxguard.api.app import create_ingest_app

    monkeypatch.setenv("MAXGUARD_INGEST_TOKEN", TOKEN)
    client = TestClient(create_ingest_app(tmp_path / "data", explain=False))
    spool = tmp_path / "spool"
    spool.mkdir()
    shutil.copy(FLOW_FIXTURE, spool / "capture-20261006-140000.pcap")
    config = make_config(spool, console_url="http://testserver")
    assert agent.upload_finished(config, capture_running=False, session=client) == 1
    assert agent.upload(spool / "uploaded" / "capture-20261006-140000.pcap",
                        make_config(spool, console_url="http://testserver", token="wrong"),
                        session=client) == 401
```

Run them:

```bash
pytest tests/unit/test_agent.py -q
```

Expected output:

```text
.........................                                                                    [100%]
25 passed in 4.33s
```

**Step 4.** See the capture flags work. This runs tcpdump inside a container that has no network, on its own loopback, with 2-second files: the names are UTC and the files belong to `nobody` (user 65534), which shows that `-Z` dropped root:

```bash
docker run --rm --network none --cap-add NET_RAW --cap-add NET_ADMIN -e TZ=UTC nicolaka/netshoot:v0.15 sh -c '
  mkdir -p /spool && chown nobody /spool
  tcpdump -i lo -n -G 2 -w "/spool/capture-%Y%m%d-%H%M%S.pcap" -Z nobody 2> /dev/null & P=$!
  ping -i 0.5 -c 9 127.0.0.1 > /dev/null; kill -INT $P; wait $P
  ls -ln /spool'
```

Expected output:

```text
total 12
-rw-r--r--    1 65534    65534          252 Oct  8 22:55 capture-20261008-225520.pcap
-rw-r--r--    1 65534    65534          936 Oct  8 22:55 capture-20261008-225522.pcap
-rw-r--r--    1 65534    65534          480 Oct  8 22:55 capture-20261008-225524.pcap
```

*The file names carry the time you run it, so yours differ.*

**Step 5.** Upload for real: the ingest-only app (the one sensors reach on port 8001) and the agent in `--upload-only` mode, with the Telnet capture standing in for a finished file. The config file must be private (`chmod 600`), because it holds the token:

```bash
mkdir -p data/agent/spool
cp tests/pcaps/telnet.pcap data/agent/spool/capture-20261006-140000.pcap
T=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
cat > data/agent/agent.toml <<EOF
console_url = "http://127.0.0.1:8001"
token = "$T"
spool_dir = "data/agent/spool"
sensor_id = "laptop"
capture_user = "nobody"
EOF
chmod 600 data/agent/agent.toml
MAXGUARD_INGEST_TOKEN=$T MAXGUARD_DATA_DIR=data/console \
  uvicorn --factory maxguard.api.app:create_ingest_app --host 127.0.0.1 --port 8001 > data/agent/console.log 2>&1 & U=$!
for i in $(seq 1 50); do python -c "import socket; socket.create_connection(('127.0.0.1', 8001), 1)" 2> /dev/null && break; sleep 0.2; done
python -m maxguard.sensor.agent --config data/agent/agent.toml --upload-only
ls data/agent/spool/uploaded
grep -o '"POST /api/ingest HTTP/1.1" [0-9]* [A-Za-z]*' data/agent/console.log
python -c "from maxguard.storage.events import EventStore; e = EventStore('data/console/events').query(ip='172.18.0.3', since=0); print(len(e), 'event(s) from sensor', sorted({x['sensor_id'] for x in e}))"
kill $U
```

Expected output:

```text
uploaded 1 file(s)
capture-20261006-140000.pcap
"POST /api/ingest HTTP/1.1" 200 OK
1 event(s) from sensor ['laptop']
```

*`uvicorn` and the agent run inside the `zeek/zeek:9.0.0` image here, because the console needs Zeek to read a capture. The console refuses a token shorter than 32 characters.*

**Step 6.** **On your own laptop** (*not run — verify on hardware*). On the console set `MAXGUARD_INGEST_TOKEN` (make one with `python -c "import secrets; print(secrets.token_urlsafe(32))"`) and start `docker/compose.lan.yaml`. On the laptop write `~/.config/maxguard/agent.toml` (Windows: `%APPDATA%\MaxGuard\agent.toml`) with `console_url = "http://<console address>:8001"`, the same token, `spool_dir`, `sensor_id`, `capture_user` (your login name) and `rotate_seconds = 900`; `chmod 600` it; then `sudo python -m maxguard.sensor.agent` (Windows: an Administrator terminal). After 15 minutes the first file appears on the console. Port 8001 is plain HTTP, so the token and your captures cross the LAN unencrypted: use a wired or trusted network. Check macOS's `tcpdump -Z` and Windows' `pktmon` too; neither could be run in planning.

**Step 7.** Commit, push, and open the pull request:

```bash
git add -A
git status          # only this task's files: nothing from .venv/, data/ or lab/captures/
git commit -m "feat: host agent with OS-native capture (JAK-11)"
git push -u origin HEAD
```

`HEAD` means "the branch I am on", so you do not have to retype its name. Open the repository on github.com: a yellow bar shows your branch with a **Compare & pull request** button. Click it, keep the title `feat: host agent with OS-native capture (JAK-11)`, fill in the template (paste the real output of the commands above under **How I tested it**), write `Closes #<issue number>` (this task's issue), and pick **@JWinborne1** under **Reviewers**. Click **Create pull request**, then fix anything CI or the reviewer finds with new commits on the same branch.

#### How to test

The tests pass, the upload check prints `uploaded 1 file(s)` and `200 OK`, and a manual run on your own laptop uploads one file that appears on the console.

#### What you just did and why

A host agent sees only its own computer, but it needs no extra hardware, which makes it the easiest way for a home user to try MaxGuard on live traffic. Using the built-in capture tools avoids installing a driver, and uploading finished files reuses the exact upload path the dashboard already tests.

#### Pull request checklist

- [ ] `ruff check .` prints `All checks passed!`
- [ ] `pytest -m "not integration" -q` passes on your laptop
- [ ] The pull request title has the form `type: summary (TASK-ID)` and the body says `Closes #<issue number>`
- [ ] No secrets, passwords, email addresses, personal data, or captures from a real network (CLAUDE.md rule 6)
- [ ] Any new dependency has a row in `docs/DEPENDENCIES.md` with its license
- [ ] CI is green and your reviewer approved
- [ ] No test starts a real capture
- [ ] The token is read from a private config file
