# Amory: Compliance Mapping Analyst

**Amory B.** (@gettalife) · Module: Mapping and reports · Reviewer for your pull requests: @ahmadalkhoudeir (Ahmad) · Ask first when stuck: Ahmad

This is your part of the MaxGuard v2.0 roadmap. Read [the roadmap overview](README.md) once, then work top to bottom: Week 0 first, then your tasks in order. Each task's ID is also the start of its GitHub issue's title.

## Your tasks

| Task | Due | Title | Needs first | Kind |
|---|---|---|---|---|
| [AMO-00](#week-0--onboarding-due-friday-october-9-2026) | W0 | Week 0 onboarding (Amory) | — | process |
| [AMO-01](#amo-01-nist-sp-800-53-mapping-file-and-the-mapping-checks) | W1 | NIST SP 800-53 mapping file and the mapping checks | [JAI-02](jaiden.md#jai-02-merge-the-three-contracts-in-their-v20-form), [FIO-02](fiona.md#fio-02-tls-and-certificate-rules), [JAK-03](jakub.md#jak-03-cleartext-and-rdp-rules-the-rule-set-is-complete) | code, tested |
| [AMO-02](#amo-02-pci-dss-v401-rows-checked-in-the-official-document) | W3 | PCI DSS v4.0.1 rows, checked in the official document | [AMO-01](#amo-01-nist-sp-800-53-mapping-file-and-the-mapping-checks) | process |
| [AMO-03](#amo-03-report-export-json-csv-and-html) | W4 | Report export: JSON, CSV, and HTML | [JAI-05](jaiden.md#jai-05-the-pipeline-one-function-from-input-to-report) | code, tested |
| [AMO-04](#amo-04-cisa-cpg-20-and-cjis-v61-rows) | W5 | CISA CPG 2.0 and CJIS v6.1 rows | [AMO-02](#amo-02-pci-dss-v401-rows-checked-in-the-official-document) | process |
| [AMO-05](#amo-05-chain-of-custody-log) | S4 | Chain-of-custody log | [JAI-08](jaiden.md#jai-08-ed25519-signing-library) | code, tested |

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
git config --global user.name "Amory B."
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
git checkout -b amory/week0-team-row
```

2. **Make the change.** Run `code .`, open `docs/TEAM.md`, and add this line at
   the end (keep the `|` characters):

```markdown
| Amory B. | Compliance Mapping Analyst | gettalife | Mapping and reports |
```

3. **Commit** (the message says *what changed*, starting with a type such as
   `docs:`, `feat:`, `fix:` or `test:`; see `docs/CONTRIBUTING.md`):

```bash
git add docs/TEAM.md
git commit -m "docs: add Amory to TEAM.md"
```

4. **Push** your branch to GitHub:

```bash
git push -u origin amory/week0-team-row
```

Expected (from the planning simulation; the first lines differ on GitHub):

```text
 * [new branch]      amory/week0-team-row -> amory/week0-team-row
branch 'amory/week0-team-row' set up to track 'origin/amory/week0-team-row'.
```

5. **Open the pull request** and ask for a review:

```bash
gh pr create --base main --title "docs: add Amory to TEAM.md" --body "Week 0 onboarding." --reviewer ahmadalkhoudeir
```

`gh` prints the pull request's web address. (You can also click the link Git
printed after the push and press **Create pull request**.)

6. **After approval**, click **Squash and merge** on GitHub, then update your laptop:

```bash
git checkout main && git pull
git branch -d amory/week0-team-row
```

**If GitHub says "This branch has conflicts":** eight people are adding a line
to the same file this week, so this is expected. Bring `main` into your branch
and keep both lines:

```bash
git checkout main && git pull
git checkout amory/week0-team-row
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
   `AMO-01: pytest cannot import maxguard`). In the body, paste the
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

### AMO-01: NIST SP 800-53 mapping file and the mapping checks

**Due:** Week 1 (due Fri Oct 16) · **Milestone:** `W1 Building blocks` · **Needs first:** [JAI-02](jaiden.md#jai-02-merge-the-three-contracts-in-their-v20-form), [FIO-02](fiona.md#fio-02-tls-and-certificate-rules), [JAK-03](jakub.md#jak-03-cleartext-and-rdp-rules-the-rule-set-is-complete) · **Kind:** code, tested

**Issue labels:** `type:task` `phase:alpha` `owner:amory` `area:mapping` `critical-path`

#### Goal

Add the compliance mapping files (Contract 2): NIST SP 800-53 Rev. 5 (Release 5.2.0) with a verified row for every rule, the field guide `mappings/schema.md`, the PCI DSS, CISA CPG and CJIS files with their headers but no rows yet, and the tests that enforce CLAUDE.md rule 8 on every file.

#### Prerequisites

JAI-02 (the loader) is merged, and FIO-02 and JAK-03 (all 13 rule IDs exist).

#### Steps

**Step 1.** Update `main` and create your branch for this task (one branch per task):

```bash
cd ~/projects/maxguard
source .venv/bin/activate
git checkout main && git pull
git checkout -b amory/nist-mapping
```

If `source .venv/bin/activate` fails, you have not made the virtual environment yet: do Week 0 section 0.11 first.

**Step 2.** Create the field guide `mappings/schema.md` and read it first:

````markdown
# Mapping files: what every field means

MaxGuard finds problems on a network (for example "someone used Telnet").
A **mapping file** says which rules of a compliance framework each problem
breaks (for example "NIST SP 800-53 control SC-8"). MaxGuard copies these rows
into every report, so an auditor can see *which rule* a finding touches and
*why*.

There is one file per framework in this folder:

| File | Framework | Version (exact text) |
|---|---|---|
| `pci_dss_4_0_1.yaml` | PCI DSS | `4.0.1` |
| `nist_800_53_r5.yaml` | NIST SP 800-53 | `Rev. 5 (Release 5.2.0)` |
| `cisa_cpg_2_0.yaml` | CISA CPG | `2.0` |
| `cjis_6_1.yaml` | CJIS | `6.1` |
| `attack.yaml` (Fiona) | MITRE ATT&CK | `v19.x` point release |

The versions are locked in `docs/PROJECT_DECISIONS.md` section 8. Do not
change a version unless that table changes first.

## The file, line by line

```yaml
framework: NIST SP 800-53            # the framework's short name
version: "Rev. 5 (Release 5.2.0)"    # exact version text, ALWAYS in quotes
source: https://csrc.nist.gov/...    # where anyone can read the framework

mappings:                            # one entry per MaxGuard rule
  cleartext.telnet:                  # the rule's ID (see "Rule IDs" below)
    - control_id: SC-8               # the framework's own number for the rule
      title: Transmission Confidentiality and Integrity
      rationale: Telnet sends every keystroke in readable form, so ...
      verified: "OSCAL catalog 5.2.0, id sc-8 (title and statement)"
```

### Top of the file (once per file)

| Field | Required | What to write |
|---|---|---|
| `framework` | yes | The framework's short name, spelled exactly as in the table above. Reports group findings by this name. |
| `version` | yes | The exact version text from the table above. **Put it in quotes.** Without quotes, a version like `2.0` is read as the number 2 and the test fails. |
| `source` | yes | A link to the publisher's own page for this version (not a blog or a vendor summary). |
| `mappings` | yes | The list of rules, described below. If you have no checked rows yet, write `mappings: {}` (an empty list), never leave it blank. |

### One row (one framework control for one MaxGuard rule)

| Field | Required | What to write |
|---|---|---|
| `control_id` | yes | The control or requirement number exactly as the framework prints it, for example `SC-8(1)` or `4.2.1`. |
| `title` | yes | The control's title, copied word for word. For a NIST control enhancement write `<base title> \| <enhancement title>`, the way SP 800-53 prints it, for example `Transmission Confidentiality and Integrity \| Cryptographic Protection`. |
| `rationale` | yes | One plain sentence: why this finding breaks this control. Write it for a manager, not an engineer. |
| `verified` | yes for these four files | Where you checked the ID and title, precise enough that someone else can find it again in a minute: document + page or section, for example `PCI DSS v4.0.1 PDF, p. 112`. |
| `tactic` | ATT&CK only | The ATT&CK tactic, for example `credential-access`. Only `attack.yaml` uses it. |

The loader reads `control_id`, `title` and `rationale`; `verified` is for
people (reviewers and auditors) and is checked by the tests.

## Rule IDs

The keys under `mappings:` must be MaxGuard rule IDs that already exist, for
example `cleartext.telnet`, `cleartext.ftp`, `tls.weak_version`,
`cert.expired`. The full list is the rule ID table in
`docs/ARCHITECTURE.md` section 5; in code it is `maxguard.rules.base.RULES`. A rule may
be left out of a framework when no control in that framework fits it.
New rule IDs need Security Lead approval before they get mapping rows.

## The one rule that matters most: never guess

CLAUDE.md rule 8: every row must cite an exact control ID **you read in the
publisher's document** for the locked version. If you cannot check a row,
do not add it. A wrong control ID in a compliance report is worse than a
missing one, because people trust it.

That is why three files are shipped with `mappings: {}`: during planning the
PCI, CISA and FBI websites could not be opened, so Amory fills them in during
tasks AMO-02 (PCI DSS) and AMO-04 (CISA CPG and CJIS).

## How to check your work

From the repository root:

```
pytest tests/unit/test_mappings.py -q
```

The test fails if a file does not load, a required field is missing or
empty, a rule ID does not exist, a version is not the locked one, or a row
has no `verified` note.
````

**Step 3.** Create `mappings/nist_800_53_r5.yaml`:

```yaml
# NIST SP 800-53 mappings for MaxGuard rules (Contract 2; every field is
# explained in mappings/schema.md).
#
# How the rows were checked (CLAUDE.md rule 8):
#   Every control_id and title below was read on 2026-10-06 from NIST's own
#   machine-readable copy of the catalog (OSCAL JSON, metadata.version "5.2.0"):
#   https://raw.githubusercontent.com/usnistgov/oscal-content/main/nist.gov/SP800-53/rev5/json/NIST_SP-800-53_rev5_catalog.json
#   The "verified" field names the OSCAL control id that was read, e.g. "sc-8.1".
#   Enhancement titles are written the way SP 800-53 prints them:
#   "<base control title> | <enhancement title>".
#
# Before every release, re-check the version against the publisher (source).

framework: NIST SP 800-53
version: "Rev. 5 (Release 5.2.0)"
source: https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final

mappings:
  cleartext.ftp:
    - control_id: SC-8
      title: Transmission Confidentiality and Integrity
      rationale: FTP sends commands, files and the login without encryption, so the data it carries is not protected.
      verified: "OSCAL catalog 5.2.0, id sc-8 (title and statement)"
    - control_id: SC-8(1)
      title: Transmission Confidentiality and Integrity | Cryptographic Protection
      rationale: No encryption protects the FTP session, so anyone on the network path can read or change it.
      verified: "OSCAL catalog 5.2.0, id sc-8.1 (title and statement)"
    - control_id: IA-5(1)
      title: Authenticator Management | Password-based Authentication
      rationale: The FTP login sent a password without encryption, but part (c) allows passwords only over cryptographically protected channels.
      verified: "OSCAL catalog 5.2.0, id ia-5.1, statement item (c)"

  cleartext.telnet:
    - control_id: SC-8
      title: Transmission Confidentiality and Integrity
      rationale: Telnet sends every keystroke and every screen of output in readable form, so the data it carries is not protected.
      verified: "OSCAL catalog 5.2.0, id sc-8 (title and statement)"
    - control_id: SC-8(1)
      title: Transmission Confidentiality and Integrity | Cryptographic Protection
      rationale: Telnet has no encryption, so nothing stops someone on the network path from reading or changing the session.
      verified: "OSCAL catalog 5.2.0, id sc-8.1 (title and statement)"
    - control_id: AC-17(2)
      title: Remote Access | Protection of Confidentiality and Integrity Using Encryption
      rationale: Telnet is a remote login session, and this control requires remote access sessions to be protected with encryption.
      verified: "OSCAL catalog 5.2.0, id ac-17.2 (title and statement)"
    - control_id: IA-5(1)
      title: Authenticator Management | Password-based Authentication
      rationale: A Telnet login sends the password without encryption, but part (c) allows passwords only over cryptographically protected channels.
      verified: "OSCAL catalog 5.2.0, id ia-5.1, statement item (c)"

  cleartext.http:
    - control_id: SC-8
      title: Transmission Confidentiality and Integrity
      rationale: Plain HTTP sends pages, form data and cookies in readable form, so the data it carries is not protected.
      verified: "OSCAL catalog 5.2.0, id sc-8 (title and statement)"
    - control_id: SC-8(1)
      title: Transmission Confidentiality and Integrity | Cryptographic Protection
      rationale: No TLS protects this HTTP traffic, so anyone on the network path can read or change it.
      verified: "OSCAL catalog 5.2.0, id sc-8.1 (title and statement)"

  cleartext.http_alt:
    - control_id: SC-8
      title: Transmission Confidentiality and Integrity
      rationale: Plain HTTP on port 8080 sends pages, form data and cookies in readable form, so the data it carries is not protected.
      verified: "OSCAL catalog 5.2.0, id sc-8 (title and statement)"
    - control_id: SC-8(1)
      title: Transmission Confidentiality and Integrity | Cryptographic Protection
      rationale: No TLS protects this HTTP traffic on port 8080, so anyone on the network path can read or change it.
      verified: "OSCAL catalog 5.2.0, id sc-8.1 (title and statement)"

  cleartext.pop3:
    - control_id: SC-8
      title: Transmission Confidentiality and Integrity
      rationale: POP3 without TLS sends email in readable form, so the data it carries is not protected.
      verified: "OSCAL catalog 5.2.0, id sc-8 (title and statement)"
    - control_id: SC-8(1)
      title: Transmission Confidentiality and Integrity | Cryptographic Protection
      rationale: No TLS protects the POP3 session, so anyone on the network path can read or change it.
      verified: "OSCAL catalog 5.2.0, id sc-8.1 (title and statement)"
    - control_id: IA-5(1)
      title: Authenticator Management | Password-based Authentication
      rationale: A POP3 login without TLS normally sends the mailbox password unencrypted, but part (c) allows passwords only over cryptographically protected channels.
      verified: "OSCAL catalog 5.2.0, id ia-5.1, statement item (c)"

  cleartext.imap:
    - control_id: SC-8
      title: Transmission Confidentiality and Integrity
      rationale: IMAP without TLS sends email in readable form, so the data it carries is not protected.
      verified: "OSCAL catalog 5.2.0, id sc-8 (title and statement)"
    - control_id: SC-8(1)
      title: Transmission Confidentiality and Integrity | Cryptographic Protection
      rationale: No TLS protects the IMAP session, so anyone on the network path can read or change it.
      verified: "OSCAL catalog 5.2.0, id sc-8.1 (title and statement)"
    - control_id: IA-5(1)
      title: Authenticator Management | Password-based Authentication
      rationale: An IMAP login without TLS normally sends the mailbox password unencrypted, but part (c) allows passwords only over cryptographically protected channels.
      verified: "OSCAL catalog 5.2.0, id ia-5.1, statement item (c)"

  rdp.standard_security:
    - control_id: AC-17(2)
      title: Remote Access | Protection of Confidentiality and Integrity Using Encryption
      rationale: The remote desktop session used legacy Standard RDP Security instead of TLS, so it lacks the encryption protection this control expects for remote access.
      verified: "OSCAL catalog 5.2.0, id ac-17.2 (title and statement)"
    - control_id: SC-23
      title: Session Authenticity
      rationale: Without TLS the client cannot check the server's identity, so the session is open to a man-in-the-middle.
      verified: "OSCAL catalog 5.2.0, id sc-23 (title and statement)"

  tls.weak_version:
    - control_id: SC-8(1)
      title: Transmission Confidentiality and Integrity | Cryptographic Protection
      rationale: The connection used an outdated SSL or TLS version, so its protection in transit is weaker than it should be.
      verified: "OSCAL catalog 5.2.0, id sc-8.1 (title and statement)"
    - control_id: SC-13
      title: Cryptographic Protection
      rationale: An outdated SSL or TLS version is not the kind of cryptography an organization should require for data in transit.
      verified: "OSCAL catalog 5.2.0, id sc-13 (title and statement)"

  tls.weak_cipher:
    - control_id: SC-8(1)
      title: Transmission Confidentiality and Integrity | Cryptographic Protection
      rationale: The connection used a weak or NULL cipher, so data in transit was weakly encrypted or not encrypted at all.
      verified: "OSCAL catalog 5.2.0, id sc-8.1 (title and statement)"
    - control_id: SC-13
      title: Cryptographic Protection
      rationale: A weak or NULL cipher is not the kind of cryptography an organization should require for data in transit.
      verified: "OSCAL catalog 5.2.0, id sc-13 (title and statement)"

  cert.expired:
    - control_id: IA-5
      title: Authenticator Management
      rationale: A server certificate is the server's authenticator, and part (f) requires refreshing authenticators, but this one was used after it expired.
      verified: "OSCAL catalog 5.2.0, id ia-5, statement item (f)"

  cert.self_signed:
    - control_id: SC-17
      title: Public Key Infrastructure Certificates
      rationale: A self-signed certificate was not issued under a certificate policy or by an approved provider, and it acts as its own trust anchor.
      verified: "OSCAL catalog 5.2.0, id sc-17, statement items (a) and (b)"

  cert.weak_key:
    - control_id: SC-12
      title: Cryptographic Key Establishment and Management
      rationale: The certificate's RSA key is shorter than 2048 bits, too weak for the key management requirements this control asks the organization to set.
      verified: "OSCAL catalog 5.2.0, id sc-12 (title and statement)"
    - control_id: SC-13
      title: Cryptographic Protection
      rationale: A short RSA key is weaker cryptography than an organization should require for protecting connections.
      verified: "OSCAL catalog 5.2.0, id sc-13 (title and statement)"

  cert.sha1_signature:
    - control_id: SC-13
      title: Cryptographic Protection
      rationale: The certificate is signed with SHA-1, an outdated hash algorithm, so the cryptography in use is weaker than an organization should require.
      verified: "OSCAL catalog 5.2.0, id sc-13 (title and statement)"
```

Every `control_id` and `title` was read from NIST's machine-readable copy of the catalog (OSCAL, version 5.2.0); `verified` says which entry. Open two rows yourself in that file (the link is in the header) and confirm them before you commit.

**Step 4.** Create the three framework files whose rows you will fill later (AMO-02 and AMO-04). `mappings/pci_dss_4_0_1.yaml`:

```yaml
# PCI DSS mappings for MaxGuard rules (Contract 2; every field is explained in
# mappings/schema.md).
#
# EMPTY ON PURPOSE - this is not a mistake.
# CLAUDE.md rule 8 says every row must cite a requirement number that someone
# checked in the official PCI DSS v4.0.1 document. During planning the PCI SSC
# document library could not be opened (network blocked), so no row could be
# verified, and guessing requirement numbers is not allowed.
#
# Amory fills this file in task AMO-02 (docs/roadmap/amory.md):
#   1. Download "PCI DSS v4.0.1" from the document library (source below).
#   2. Start with cleartext.telnet (the demo finding), then the other rules.
#   3. Copy each requirement number and title exactly from the PDF and put the
#      page number in "verified", e.g. "PCI DSS v4.0.1 PDF, p. 112".
#   4. Run: pytest tests/unit/test_mappings.py

framework: PCI DSS
version: "4.0.1"
source: https://www.pcisecuritystandards.org/document_library/

mappings: {}
```

`mappings/cisa_cpg_2_0.yaml`:

```yaml
# CISA Cross-Sector Cybersecurity Performance Goals (CPG) mappings for MaxGuard
# rules (Contract 2; every field is explained in mappings/schema.md).
#
# EMPTY ON PURPOSE - this is not a mistake.
# CLAUDE.md rule 8 says every row must cite a goal ID that someone checked in
# the official CPG 2.0 document. During planning cisa.gov could not be opened
# (network blocked), so no row could be verified, and guessing goal IDs is not
# allowed. CPG 2.0 regrouped the goals, so never copy a goal ID from an older
# CPG version without finding it in the 2.0 document.
#
# Amory fills this file in task AMO-04 (docs/roadmap/amory.md):
#   1. Open the CPG 2.0 Report (December 2025) from the source page below
#      (direct PDF: https://www.cisa.gov/sites/default/files/2025-12/CPG_Report_2.0_508c.pdf).
#   2. Copy each goal ID and title exactly and put the page number in "verified".
#   3. Run: pytest tests/unit/test_mappings.py

framework: CISA CPG
version: "2.0"
source: https://www.cisa.gov/cybersecurity-performance-goals-2-0-cpg-2-0

mappings: {}
```

`mappings/cjis_6_1.yaml`:

```yaml
# CJIS Security Policy mappings for MaxGuard rules (Contract 2; every field is
# explained in mappings/schema.md).
#
# EMPTY ON PURPOSE - this is not a mistake.
# CLAUDE.md rule 8 says every row must cite a control ID that someone checked
# in the official CJIS Security Policy v6.1 document. During planning
# le.fbi.gov could not be opened (network blocked), so no row could be
# verified, and guessing control IDs is not allowed.
#
# Amory fills this file in task AMO-04 (docs/roadmap/amory.md):
#   1. Download CJIS Security Policy v6.1 (June 25, 2026) from the resource
#      center below.
#   2. Copy each control ID and title exactly as v6.1 prints them and put the
#      section and page number in "verified".
#   3. Run: pytest tests/unit/test_mappings.py

framework: CJIS
version: "6.1"
source: https://le.fbi.gov/cjis-division/cjis-security-policy-resource-center

mappings: {}
```

**Step 5.** Create the tests `tests/unit/test_mappings.py`:

```python
"""Checks for mappings/*.yaml (Contract 2 and CLAUDE.md rule 8).

These tests guard the compliance rows that end up in every report: each file
must load, use the locked framework version, name only real rule IDs, and
say where every row was verified.
"""

import re
from pathlib import Path

import pytest
import yaml

import maxguard.rules  # noqa: F401  (importing registers every rule)
from maxguard.mapping.loader import ATTACK, REQUIRED_TOP, validate
from maxguard.rules.base import RULES

MAPPINGS_DIR = Path(__file__).resolve().parents[2] / "mappings"
MAPPING_FILES = sorted(MAPPINGS_DIR.glob("*.yaml"))

# docs/PROJECT_DECISIONS.md section 8. Change this table only when that one changes.
LOCKED_VERSIONS = {
    "PCI DSS": "4.0.1",
    "NIST SP 800-53": "Rev. 5 (Release 5.2.0)",
    "CISA CPG": "2.0",
    "CJIS": "6.1",
}
# ATT&CK is locked to major version 19; the file records the exact point release.
ATTACK_VERSION = re.compile(r"^v19\.\d+$")

COMPLIANCE_FILES = {
    "pci_dss_4_0_1.yaml": "PCI DSS",
    "nist_800_53_r5.yaml": "NIST SP 800-53",
    "cisa_cpg_2_0.yaml": "CISA CPG",
    "cjis_6_1.yaml": "CJIS",
}


def load(path: Path) -> dict:
    return yaml.safe_load(path.read_text())


def rows_of(fw: dict):
    """Yield (rule_id, row) for every row in one mapping file."""
    for rule_id, rows in fw["mappings"].items():
        for row in rows:
            yield rule_id, row


def by_name(paths):
    return [pytest.param(p, id=p.name) for p in paths]


def test_every_compliance_framework_has_its_file():
    for file_name, framework in COMPLIANCE_FILES.items():
        path = MAPPINGS_DIR / file_name
        assert path.exists(), f"missing {file_name}"
        assert load(path)["framework"] == framework


@pytest.mark.parametrize("path", by_name(MAPPING_FILES))
def test_file_loads_with_required_keys(path):
    fw = load(path)
    assert isinstance(fw, dict)
    for key in REQUIRED_TOP:
        assert key in fw, f"{path.name}: missing {key!r}"
    # "mappings:" left blank loads as None and would crash the loader.
    assert isinstance(fw["mappings"], dict), "write 'mappings: {}' when there are no rows"


@pytest.mark.parametrize("path", by_name(MAPPING_FILES))
def test_version_is_the_locked_one(path):
    fw = load(path)
    # Unquoted 2.0 or 6.1 would load as a number, so check the type first.
    assert isinstance(fw["version"], str), "put the version in quotes"
    if fw["framework"] == ATTACK:
        assert ATTACK_VERSION.match(fw["version"])
    else:
        assert fw["version"] == LOCKED_VERSIONS[fw["framework"]]


@pytest.mark.parametrize("path", by_name(MAPPING_FILES))
def test_source_is_a_web_link(path):
    assert load(path)["source"].startswith("https://")


@pytest.mark.parametrize("path", by_name(MAPPING_FILES))
def test_every_rule_id_is_registered(path):
    unknown = set(load(path)["mappings"]) - set(RULES)
    assert not unknown, f"not in the rule registry: {sorted(unknown)}"


@pytest.mark.parametrize("path", by_name(MAPPING_FILES))
def test_loader_finds_no_problems(path):
    assert validate(load(path), set(RULES)) == []


@pytest.mark.parametrize("path", by_name(MAPPING_FILES))
def test_every_compliance_row_says_where_it_was_verified(path):
    fw = load(path)
    if fw["framework"] == ATTACK:
        pytest.skip("this check is for the four compliance files, not ATT&CK")
    for rule_id, row in rows_of(fw):
        assert str(row.get("verified", "")).strip(), f"{rule_id} {row['control_id']}: no 'verified'"


@pytest.mark.parametrize("path", by_name(MAPPING_FILES))
def test_no_control_listed_twice_for_one_rule(path):
    for rule_id, rows in load(path)["mappings"].items():
        ids = [row["control_id"] for row in rows]
        assert len(ids) == len(set(ids)), f"{rule_id}: repeated control_id"


def test_demo_finding_is_mapped_in_nist():
    # cleartext.telnet is the demo finding; it must show controls in reports.
    nist = load(MAPPINGS_DIR / "nist_800_53_r5.yaml")
    assert "SC-8" in [row["control_id"] for row in nist["mappings"]["cleartext.telnet"]]
```

**Step 6.** Run them:

```bash
pytest tests/unit/test_mappings.py -q
```

Expected output:

```text
..............................                                                               [100%]
30 passed in 0.18s
```

**Step 7.** Count the NIST rows per rule:

```bash
python -c "import yaml; f = yaml.safe_load(open('mappings/nist_800_53_r5.yaml')); print(f['version']); [print(rule, [r['control_id'] for r in rows]) for rule, rows in sorted(f['mappings'].items())]"
```

Expected output:

```text
Rev. 5 (Release 5.2.0)
cert.expired ['IA-5']
cert.self_signed ['SC-17']
cert.sha1_signature ['SC-13']
cert.weak_key ['SC-12', 'SC-13']
cleartext.ftp ['SC-8', 'SC-8(1)', 'IA-5(1)']
cleartext.http ['SC-8', 'SC-8(1)']
cleartext.http_alt ['SC-8', 'SC-8(1)']
cleartext.imap ['SC-8', 'SC-8(1)', 'IA-5(1)']
cleartext.pop3 ['SC-8', 'SC-8(1)', 'IA-5(1)']
cleartext.telnet ['SC-8', 'SC-8(1)', 'AC-17(2)', 'IA-5(1)']
rdp.standard_security ['AC-17(2)', 'SC-23']
tls.weak_cipher ['SC-8(1)', 'SC-13']
tls.weak_version ['SC-8(1)', 'SC-13']
```

**Step 8.** Commit, push, and open the pull request:

```bash
git add -A
git status          # only this task's files: nothing from .venv/, data/ or lab/captures/
git commit -m "feat: NIST SP 800-53 mapping file and mapping checks (AMO-01)"
git push -u origin HEAD
```

`HEAD` means "the branch I am on", so you do not have to retype its name. Open the repository on github.com: a yellow bar shows your branch with a **Compare & pull request** button. Click it, keep the title `feat: NIST SP 800-53 mapping file and mapping checks (AMO-01)`, fill in the template (paste the real output of the commands above under **How I tested it**), write `Closes #<issue number>` (this task's issue), and pick **@ahmadalkhoudeir** under **Reviewers**. Click **Create pull request**, then fix anything CI or the reviewer finds with new commits on the same branch.

#### How to test

`pytest` passes, and every one of the 13 rules has at least one NIST control.

#### What you just did and why

A compliance report is only useful if an auditor can look up every control it names. That is why each row records where it was checked, why the version string must match `docs/PROJECT_DECISIONS.md` exactly, and why three files ship empty instead of with guessed IDs: a wrong control ID is worse than a missing one, because people trust it. The tests make those rules impossible to forget.

#### Pull request checklist

- [ ] `ruff check .` prints `All checks passed!`
- [ ] `pytest -m "not integration" -q` passes on your laptop
- [ ] The pull request title has the form `type: summary (TASK-ID)` and the body says `Closes #<issue number>`
- [ ] No secrets, passwords, email addresses, personal data, or captures from a real network (CLAUDE.md rule 6)
- [ ] Any new dependency has a row in `docs/DEPENDENCIES.md` with its license
- [ ] CI is green and your reviewer approved
- [ ] You opened at least two NIST rows in the OSCAL catalog yourself
- [ ] Ahmad reviewed the rows (compliance accuracy)

### AMO-02: PCI DSS v4.0.1 rows, checked in the official document

**Due:** Week 3 (due Fri Oct 30) · **Milestone:** `W3 API and alert queue` · **Needs first:** [AMO-01](#amo-01-nist-sp-800-53-mapping-file-and-the-mapping-checks) · **Kind:** process

**Issue labels:** `type:task` `phase:alpha` `owner:amory` `area:mapping`

#### Goal

Fill `mappings/pci_dss_4_0_1.yaml` with requirement numbers you read in the official PCI DSS v4.0.1 document, starting with `cleartext.telnet` (the demo finding), so the Week 4 report shows PCI DSS controls.

#### Prerequisites

AMO-01 is merged.

#### Steps

**Step 1.** Update `main` and create your branch for this task (one branch per task):

```bash
cd ~/projects/maxguard
source .venv/bin/activate
git checkout main && git pull
git checkout -b amory/pci-rows
```

If `source .venv/bin/activate` fails, you have not made the virtual environment yet: do Week 0 section 0.11 first.

**Step 2.** Download **PCI DSS v4.0.1** from the PCI Security Standards Council document library (the `source` link in the file; you accept their license agreement to download it). Do not commit the PDF: its license does not allow redistribution.

**Step 3.** For each rule, find the requirements it shows a failure of. Start with Requirement 4 (protect cardholder data with strong cryptography during transmission over open, public networks) and Requirement 2 and 8 for insecure services and passwords, but only write a row when the requirement's own text fits the finding.

**Step 4.** Write each row in the Contract 2 format (`mappings/schema.md`): the exact requirement number and title as the PDF prints them, a one-sentence rationale in plain words, and `verified: "PCI DSS v4.0.1 PDF, p. <page>"`.

**Step 5.** Run `pytest tests/unit/test_mappings.py -q`, then `maxguard analyze tests/fixtures/zeek/telnet --no-ai --frameworks "PCI DSS"` and check the Telnet finding lists your rows.

**Step 6.** Commit, push, and open the pull request:

```bash
git add -A
git status          # only this task's files: nothing from .venv/, data/ or lab/captures/
git commit -m "feat: PCI DSS v4.0.1 mapping rows (AMO-02)"
git push -u origin HEAD
```

`HEAD` means "the branch I am on", so you do not have to retype its name. Open the repository on github.com: a yellow bar shows your branch with a **Compare & pull request** button. Click it, keep the title `feat: PCI DSS v4.0.1 mapping rows (AMO-02)`, fill in the template (paste the real output of the commands above under **How I tested it**), write `Closes #<issue number>` (this task's issue), and pick **@ahmadalkhoudeir** under **Reviewers**. Click **Create pull request**, then fix anything CI or the reviewer finds with new commits on the same branch.

#### How to test

The mapping tests pass, and Ahmad can open the PDF at every page you cite and find the requirement.

#### What you just did and why

PCI DSS is the framework the original MaxGuard was built for, and small retailers are a target audience. The requirement numbers changed between versions, so only the v4.0.1 document itself is a valid source (CLAUDE.md rule 8).

#### Pull request checklist

- [ ] `ruff check .` prints `All checks passed!`
- [ ] `pytest -m "not integration" -q` passes on your laptop
- [ ] The pull request title has the form `type: summary (TASK-ID)` and the body says `Closes #<issue number>`
- [ ] No secrets, passwords, email addresses, personal data, or captures from a real network (CLAUDE.md rule 6)
- [ ] Any new dependency has a row in `docs/DEPENDENCIES.md` with its license
- [ ] CI is green and your reviewer approved
- [ ] Every row has a page number in `verified`
- [ ] The PDF itself is not committed
- [ ] Ahmad checked the rows against the PDF

### AMO-03: Report export: JSON, CSV, and HTML

**Due:** Week 4 (due Fri Nov 6) · **Milestone:** `W4 Full offline report` · **Needs first:** [JAI-05](jaiden.md#jai-05-the-pipeline-one-function-from-input-to-report) · **Kind:** code, tested

**Issue labels:** `type:task` `phase:alpha` `owner:amory` `area:mapping` `critical-path`

#### Goal

Write `maxguard/report.py`, which turns the report into three formats: JSON (all of it), CSV (one row per finding and control, for spreadsheets and auditors), and one self-contained HTML page that opens offline. All three escape text that came from network traffic.

#### Prerequisites

JAI-05 (the pipeline) is merged.

#### Steps

**Step 1.** Update `main` and create your branch for this task (one branch per task):

```bash
cd ~/projects/maxguard
source .venv/bin/activate
git checkout main && git pull
git checkout -b amory/report-export
```

If `source .venv/bin/activate` fails, you have not made the virtual environment yet: do Week 0 section 0.11 first.

**Step 2.** Create `maxguard/report.py`:

```python
"""Report export (Amory): turn a report dict into JSON, CSV or HTML text.

The input is the dict that maxguard.pipeline.analyze() returns (schema
"maxguard.report/2"). Each function returns a string; the caller decides
where to save it. Nothing here reads the clock, so the same report always
gives exactly the same file (CLAUDE.md rule 2). Standard library only, so
exports work on an offline machine.
"""

from __future__ import annotations

import csv
import html
import io
import json
from datetime import UTC, datetime

from maxguard.models import SEVERITIES

TOP_FINDINGS = 10  # how many findings the HTML page lists in its table

# ---------------------------------------------------------------- JSON


def to_json(report: dict) -> str:
    """The whole report as JSON. Sorted keys make two exports easy to diff."""
    return json.dumps(report, sort_keys=True, indent=2) + "\n"


# ---------------------------------------------------------------- CSV

CSV_COLUMNS = [
    "finding_id", "rule_id", "severity", "title",
    "src_ip", "dst_ip", "dst_port", "protocol",
    "count", "first_seen", "last_seen",
    "framework", "version", "control_id", "control_title", "rationale",
    "evidence_record_ids",
]

# A spreadsheet app runs a cell that starts with one of these as a formula.
# Titles and hosts can come from network traffic, so an attacker could plant
# "=HYPERLINK(...)". OWASP's advice: put a single quote in front of such cells.
# https://owasp.org/www-community/attacks/CSV_Injection
FORMULA_STARTS = ("=", "+", "-", "@", "\t", "\r", "\n")


def to_csv(report: dict) -> str:
    """One row per finding per control, for spreadsheets and auditors.

    A finding with no controls still gets one row (with empty control
    columns), so no finding ever disappears from the export.
    """
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=CSV_COLUMNS)
    writer.writeheader()
    for finding in report.get("findings", []):
        for row in csv_rows(finding):
            writer.writerow({column: safe_cell(row[column]) for column in CSV_COLUMNS})
    return out.getvalue()


def csv_rows(finding: dict) -> list[dict]:
    """The CSV rows for one finding: one per control, or one with no control."""
    base = {
        "finding_id": finding["finding_id"],
        "rule_id": finding["rule_id"],
        "severity": finding["severity"],
        "title": finding["title"],
        "src_ip": finding["src_ip"],
        "dst_ip": finding["dst_ip"],
        "dst_port": finding["dst_port"],
        "protocol": finding["protocol"],
        "count": finding["count"],
        "first_seen": iso_utc(finding["first_seen"]),
        "last_seen": iso_utc(finding["last_seen"]),
        "evidence_record_ids": " ".join(evidence_ids(finding)),
    }
    controls = finding.get("controls") or [None]  # [None] -> one row, empty columns
    return [{**base, **control_columns(control)} for control in controls]


def control_columns(control: dict | None) -> dict:
    """The five control columns of a CSV row ("" when there is no control)."""
    if control is None:
        return {"framework": "", "version": "", "control_id": "",
                "control_title": "", "rationale": ""}
    return {
        "framework": control["framework"],
        "version": control["version"],
        "control_id": control["control_id"],
        "control_title": control["title"],
        "rationale": control["rationale"],
    }


def safe_cell(value: object) -> str:
    """Text for one CSV cell, made safe to open in a spreadsheet app."""
    text = "" if value is None else str(value)
    if text.startswith(FORMULA_STARTS):
        return "'" + text
    return text


# ---------------------------------------------------------------- helpers


def iso_utc(ts: float) -> str:
    """Epoch seconds -> '2026-10-06T01:02:03Z'. Converts a stored time; never reads the clock."""
    return datetime.fromtimestamp(float(ts), tz=UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def evidence_ids(finding: dict) -> list[str]:
    """The record IDs of a finding's evidence, in order."""
    return [ev["record_id"] for ev in finding.get("evidence", []) if ev.get("record_id")]


def by_severity(findings: list[dict]) -> list[dict]:
    """Most severe first. The sort is stable, so ties keep the report's order."""
    return sorted(findings, key=lambda f: SEVERITIES.index(f["severity"]))


def esc(value: object) -> str:
    """HTML-escape any value. Every piece of report data goes through this,
    because titles, hosts and AI sentences can contain text from the network."""
    return html.escape("" if value is None else str(value), quote=True)


# ---------------------------------------------------------------- HTML

# The page loads nothing from outside: no fonts, no scripts, no images.
# The CSP line below makes the browser enforce that, even if a later edit
# adds a link by mistake. Only the inline <style> block is allowed.
CSP = "default-src 'none'; style-src 'unsafe-inline'"

STYLE = """
body { font-family: system-ui, sans-serif; margin: 0; color: #1a1a1a; background: #fff; }
main { max-width: 960px; margin: 0 auto; padding: 16px; }
table { border-collapse: collapse; width: 100%; margin: 8px 0 16px; }
th, td { border: 1px solid #ccc; padding: 4px 8px; text-align: left; vertical-align: top; }
th { background: #f2f2f2; }
code { font-size: 0.9em; overflow-wrap: anywhere; }
.sev { font-weight: bold; text-transform: uppercase; }
.sev-critical { color: #8b0000; } .sev-high { color: #b22222; }
.sev-medium { color: #a0522d; } .sev-low { color: #2f4f4f; } .sev-info { color: #555; }
.note { color: #555; }
"""


def to_html(report: dict) -> str:
    """A standalone HTML page: totals, top findings, frameworks, AI sentences."""
    findings = by_severity(report.get("findings", []))
    sections = [
        html_head(report),
        html_summary(report, findings),
        html_severity_totals(findings),
        html_top_findings(findings),
        html_frameworks(findings),
        html_ai(report, findings),
        "</main>\n</body>\n</html>\n",
    ]
    return "\n".join(sections)


def html_head(report: dict) -> str:
    name = report.get("input", {}).get("name", "")
    return (
        "<!doctype html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        f"<meta http-equiv=\"Content-Security-Policy\" content=\"{CSP}\">\n"
        f"<title>MaxGuard report: {esc(name)}</title>\n"
        f"<style>{STYLE}</style>\n</head>\n<body>\n<main>\n"
        "<h1>MaxGuard report</h1>"
    )


def html_summary(report: dict, findings: list[dict]) -> str:
    source = report.get("input", {})
    tools = report.get("tools", {})
    rows = [
        ("Input", source.get("name", "")),
        ("SHA-256", source.get("sha256") or "(folder of logs, not hashed)"),
        ("Input type", source.get("adapter", "")),
        ("Zeek ran in this analysis", "yes" if tools.get("zeek") else "no"),
        ("Suricata output used", "yes" if tools.get("suricata") else "no"),
        ("Findings", len(findings)),
    ]
    cells = "\n".join(f"<tr><th>{esc(label)}</th><td>{esc(value)}</td></tr>"
                      for label, value in rows)
    return f"<h2>Summary</h2>\n<table>\n{cells}\n</table>"


def html_severity_totals(findings: list[dict]) -> str:
    """Number of findings per severity, every severity listed even when 0."""
    rows = []
    for severity in SEVERITIES:
        total = sum(1 for f in findings if f["severity"] == severity)
        rows.append(f"<tr><td class=\"sev sev-{esc(severity)}\">{esc(severity)}</td>"
                    f"<td>{total}</td></tr>")
    rows.append(f"<tr><th>Total</th><th>{len(findings)}</th></tr>")
    body = "\n".join(rows)
    return ("<h2>Findings by severity</h2>\n<table>\n"
            f"<tr><th>Severity</th><th>Findings</th></tr>\n{body}\n</table>")


def html_top_findings(findings: list[dict]) -> str:
    title = f"<h2>Top findings (most severe first, up to {TOP_FINDINGS})</h2>"
    if not findings:
        return f"{title}\n<p>No findings.</p>"
    header = ("<tr><th>#</th><th>Severity</th><th>Finding</th><th>Source</th>"
              "<th>Destination</th><th>Port</th><th>Count</th><th>Controls</th></tr>")
    rows = [html_finding_row(i, f) for i, f in enumerate(findings[:TOP_FINDINGS], start=1)]
    body = "\n".join(rows)
    return f"{title}\n<table>\n{header}\n{body}\n</table>"


def html_finding_row(number: int, f: dict) -> str:
    controls = "<br>".join(esc(line) for line in controls_by_framework(f)) or "none mapped"
    return (
        f"<tr><td>{number}</td>"
        f"<td class=\"sev sev-{esc(f['severity'])}\">{esc(f['severity'])}</td>"
        f"<td>{esc(f['title'])}<br><code>{esc(f['rule_id'])} {esc(f['finding_id'])}</code></td>"
        f"<td><code>{esc(f['src_ip'])}</code></td><td><code>{esc(f['dst_ip'])}</code></td>"
        f"<td>{esc(f['dst_port'])}/{esc(f['protocol'])}</td><td>{esc(f['count'])}</td>"
        f"<td>{controls}</td></tr>"
    )


def controls_by_framework(finding: dict) -> list[str]:
    """['NIST SP 800-53: SC-8, SC-8(1)', ...], frameworks in the order they appear."""
    ids: dict[str, list[str]] = {}
    for control in finding.get("controls", []):
        ids.setdefault(control["framework"], []).append(control["control_id"])
    return [f"{framework}: {', '.join(control_ids)}" for framework, control_ids in ids.items()]


def frameworks_affected(findings: list[dict]) -> dict[tuple[str, str], dict]:
    """(framework, version) -> {"controls": [...], "findings": n} for frameworks with hits."""
    affected: dict[tuple[str, str], dict] = {}
    for f in findings:
        hit_here: set[tuple[str, str]] = set()
        for control in f.get("controls", []):
            key = (control["framework"], control["version"])
            entry = affected.setdefault(key, {"controls": [], "findings": 0})
            if control["control_id"] not in entry["controls"]:
                entry["controls"].append(control["control_id"])
            hit_here.add(key)
        for key in hit_here:  # count each finding once per framework
            affected[key]["findings"] += 1
    return affected


def html_frameworks(findings: list[dict]) -> str:
    title = "<h2>Frameworks affected</h2>"
    # A framework with no rows here is NOT a pass: its mapping file may simply
    # have no checked rows yet. Say so, so nobody reads silence as compliance.
    note = ("<p class=\"note\">A framework that is not listed has no mapped controls for "
            "these findings. That does not mean the network meets that framework.</p>")
    affected = frameworks_affected(findings)
    if not affected:
        return f"{title}\n<p>No mapped controls.</p>\n{note}"
    rows = [
        f"<tr><td>{esc(framework)}</td><td>{esc(version)}</td><td>{entry['findings']}</td>"
        f"<td>{esc(', '.join(entry['controls']))}</td></tr>"
        for (framework, version), entry in affected.items()
    ]
    header = "<tr><th>Framework</th><th>Version</th><th>Findings</th><th>Controls</th></tr>"
    body = "\n".join(rows)
    return f"{title}\n<table>\n{header}\n{body}\n</table>\n{note}"


AI_STATUS_TEXT = {
    "ok": "Sentences from the local AI, each with the evidence records it cites. "
          "Sentences without valid citations were removed before this report was made.",
    "unavailable": "The local AI could not be reached, so there are no AI explanations.",
    "disabled": "AI explanations were turned off for this analysis.",
}


def html_ai(report: dict, findings: list[dict]) -> str:
    ai = report.get("ai", {})
    status = ai.get("status", "disabled")
    stats = (f"Model: <code>{esc(ai.get('model') or 'none')}</code>. "
             f"Findings explained: {esc(ai.get('explained', 0))}. "
             f"Sentences removed for bad citations: {esc(ai.get('dropped_sentences', 0))}.")
    lines = [
        "<h2>AI explanations</h2>",
        f"<p class=\"note\">{esc(AI_STATUS_TEXT.get(status, status))}</p>",
        f"<p class=\"note\">{stats}</p>",
    ]
    for f in findings:
        if f.get("explanation_sentences"):
            lines.append(html_ai_finding(f))
    return "\n".join(lines)


def html_ai_finding(f: dict) -> str:
    """One finding's AI sentences, each followed by the record IDs it cites."""
    items = []
    for sentence in f["explanation_sentences"]:
        cited = ", ".join(sentence.get("evidence_ids", []))
        items.append(f"<li>{esc(sentence['text'])} "
                     f"<span class=\"note\">[evidence: <code>{esc(cited)}</code>]</span></li>")
    body = "\n".join(items)
    return (f"<h3>{esc(f['title'])} <code>{esc(f['finding_id'])}</code></h3>\n"
            f"<ul>\n{body}\n</ul>")
```

Two security details: `safe_cell()` puts a `'` in front of any CSV cell that a spreadsheet would run as a formula (an attacker can put `=HYPERLINK(...)` into a host name), and every HTML value goes through `esc()`.

**Step 3.** Create the tests `tests/unit/test_report.py`:

```python
"""Tests for maxguard.report: JSON, CSV and HTML exports of a report dict."""

import csv
import io
import json
from pathlib import Path

from maxguard.models import Control, Evidence, Finding, Sentence
from maxguard.pipeline import analyze
from maxguard.report import CSV_COLUMNS, to_csv, to_html, to_json

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "zeek"

NIST_SC8 = Control("NIST SP 800-53", "Rev. 5 (Release 5.2.0)", "SC-8",
                   "Transmission Confidentiality and Integrity", "Sent in readable form.")
TEST_ROW = Control("PCI DSS", "4.0.1", "TEST-1", "Made-up row for tests", "Not a real control.")


def finding(title="Telnet session in cleartext", severity="high", dst_port=23,
            controls=(), sentences=()) -> Finding:
    """A small Finding built through Contract 1, so the tests follow the real shape."""
    return Finding(
        rule_id="cleartext.telnet", title=title, severity=severity,
        src_ip="10.0.0.5", dst_ip="10.0.0.9", dst_port=dst_port, protocol="telnet",
        first_seen=1791250285.789302, last_seen=1791250285.789302,
        evidence=[Evidence("maxguard_cleartext.log", "C1", 1791250285.789302,
                           "aab5e36795eaa77e")],
        controls=list(controls), explanation_sentences=list(sentences),
    )


def make_report(*findings: Finding, ai_status: str = "disabled") -> dict:
    """A report dict with the maxguard.report/2 keys the exporters read."""
    return {
        "schema": "maxguard.report/2",
        "input": {"name": "telnet.pcap", "sha256": "ab" * 32, "adapter": "pcap"},
        "tools": {"zeek": True, "suricata": False},
        "frameworks": [],
        "findings": [f.to_dict() for f in findings],
        "assets": [],
        "events": [],
        "ai": {"status": ai_status, "model": None, "explained": 0, "dropped_sentences": 0},
    }


def csv_data_rows(text: str) -> list[dict]:
    return list(csv.DictReader(io.StringIO(text)))


# ---------------------------------------------------------------- JSON

def test_json_round_trips():
    report = make_report(finding(controls=[NIST_SC8]))
    assert json.loads(to_json(report)) == report


def test_json_text_does_not_depend_on_key_order():
    # Same content, keys inserted in a different order -> the same text.
    report = make_report(finding())
    reordered = dict(reversed(list(report.items())))
    assert to_json(reordered) == to_json(report)


# ---------------------------------------------------------------- CSV

def test_csv_header_is_the_column_list():
    header = to_csv(make_report()).splitlines()[0]
    assert header.split(",") == CSV_COLUMNS


def test_csv_has_one_row_per_control():
    rows = csv_data_rows(to_csv(make_report(finding(controls=[NIST_SC8, TEST_ROW]))))
    assert [r["control_id"] for r in rows] == ["SC-8", "TEST-1"]
    assert rows[0]["framework"] == "NIST SP 800-53"
    assert rows[0]["control_title"] == "Transmission Confidentiality and Integrity"


def test_csv_keeps_a_finding_without_controls():
    rows = csv_data_rows(to_csv(make_report(finding())))
    assert len(rows) == 1
    assert rows[0]["rule_id"] == "cleartext.telnet"
    assert rows[0]["framework"] == rows[0]["control_id"] == ""


def test_csv_times_are_utc_and_evidence_ids_are_listed():
    row = csv_data_rows(to_csv(make_report(finding())))[0]
    assert row["first_seen"] == "2026-10-06T01:31:25Z"
    assert row["evidence_record_ids"] == "aab5e36795eaa77e"


def test_csv_stops_spreadsheet_formulas():
    row = csv_data_rows(to_csv(make_report(finding(title="=HYPERLINK(\"x\")"))))[0]
    assert row["title"] == "'=HYPERLINK(\"x\")"


# ---------------------------------------------------------------- HTML

def test_html_escapes_every_value():
    evil = finding(
        title="<script>alert(1)</script>",
        controls=[Control("NIST SP 800-53", "v", "<b>X</b>", "<i>t</i>", "r")],
        sentences=[Sentence("<img src=x onerror=alert(1)>", ["aab5e36795eaa77e"])],
    )
    page = to_html(make_report(evil, ai_status="ok"))
    assert "<script" not in page
    assert "<img" not in page
    assert "<b>X</b>" not in page
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in page


def test_html_loads_nothing_from_outside():
    page = to_html(make_report(finding(controls=[NIST_SC8])))
    for forbidden in ("<script", "<link", "<img", "<iframe", "src=", "@import", "url("):
        assert forbidden not in page
    assert "Content-Security-Policy" in page


def test_html_totals_by_severity():
    page = to_html(make_report(finding(), finding(severity="medium", dst_port=24),
                               finding(severity="medium", dst_port=25)))
    assert '<td class="sev sev-high">high</td><td>1</td>' in page
    assert '<td class="sev sev-medium">medium</td><td>2</td>' in page
    assert '<td class="sev sev-critical">critical</td><td>0</td>' in page
    assert "<tr><th>Total</th><th>3</th></tr>" in page


def test_html_lists_ten_findings_most_severe_first():
    findings = [finding(title=f"Low {i:02d}", severity="low", dst_port=i) for i in range(11)]
    findings.append(finding(title="The high one", severity="high", dst_port=99))
    page = to_html(make_report(*findings))
    assert page.index("The high one") < page.index("Low 00")
    assert "Low 08" in page
    assert "Low 09" not in page  # 1 high + Low 00..08 = the top 10


def test_html_names_affected_frameworks_only():
    page = to_html(make_report(finding(controls=[NIST_SC8])))
    assert "<td>NIST SP 800-53</td><td>Rev. 5 (Release 5.2.0)</td><td>1</td><td>SC-8</td>" in page
    assert "PCI DSS" not in page


def test_html_shows_ai_sentences_with_their_record_ids():
    cited = finding(sentences=[Sentence("Telnet sent the login in cleartext.",
                                        ["aab5e36795eaa77e"])])
    page = to_html(make_report(cited, ai_status="ok"))
    assert "Telnet sent the login in cleartext." in page
    assert "[evidence: <code>aab5e36795eaa77e</code>]" in page


def test_html_explains_when_ai_was_off():
    page = to_html(make_report(finding(), ai_status="unavailable"))
    assert "could not be reached" in page


def test_html_is_the_same_every_time():
    report = make_report(finding(controls=[NIST_SC8]))
    assert to_html(report) == to_html(json.loads(to_json(report)))


# ---------------------------------------------------------------- real pipeline output

def test_exports_for_the_telnet_fixture(tmp_path):
    report = analyze(FIXTURES / "telnet", tmp_path, explain=False)
    rows = csv_data_rows(to_csv(report))
    assert {r["rule_id"] for r in rows} == {"cleartext.telnet"}
    assert "SC-8" in {r["control_id"] for r in rows}
    page = to_html(report)
    assert "Telnet session in cleartext" in page
    assert json.loads(to_json(report))["schema"] == "maxguard.report/2"
```

**Step 4.** Run them:

```bash
pytest tests/unit/test_report.py -q
```

Expected output:

```text
................                                                                             [100%]
16 passed in 0.11s
```

**Step 5.** Make the three files for the Telnet fixture and look at the CSV:

```bash
python -c "import tempfile; from maxguard.pipeline import analyze; from maxguard import report; r = analyze('tests/fixtures/zeek/telnet', tempfile.mkdtemp(), explain=False); open('telnet.csv', 'w').write(report.to_csv(r)); open('telnet.html', 'w').write(report.to_html(r))" && head -n 3 telnet.csv | cut -c1-120 && grep -c '<tr>' telnet.html
```

Expected output:

```text
finding_id,rule_id,severity,title,src_ip,dst_ip,dst_port,protocol,count,first_seen,last_seen,framework,version,control_i
c6823b232c932762,cleartext.telnet,high,Telnet session in cleartext,172.18.0.3,172.18.0.2,23,telnet,1,2026-10-06T01:31:25
c6823b232c932762,cleartext.telnet,high,Telnet session in cleartext,172.18.0.3,172.18.0.2,23,telnet,1,2026-10-06T01:31:25
17
```

**Step 6.** Commit, push, and open the pull request:

```bash
git add -A
git status          # only this task's files: nothing from .venv/, data/ or lab/captures/
git commit -m "feat: JSON, CSV and HTML report export (AMO-03)"
git push -u origin HEAD
```

`HEAD` means "the branch I am on", so you do not have to retype its name. Open the repository on github.com: a yellow bar shows your branch with a **Compare & pull request** button. Click it, keep the title `feat: JSON, CSV and HTML report export (AMO-03)`, fill in the template (paste the real output of the commands above under **How I tested it**), write `Closes #<issue number>` (this task's issue), and pick **@ahmadalkhoudeir** under **Reviewers**. Click **Create pull request**, then fix anything CI or the reviewer finds with new commits on the same branch.

#### How to test

`pytest` passes; open `telnet.html` in a browser with Wi-Fi off and check that it looks complete (no missing styles or images).

#### What you just did and why

Different people need different formats: an analyst wants JSON, an auditor a spreadsheet, a small-business owner a page they can read and email. The HTML page has no external files, scripts, or fonts, so it works offline and is safe to open, and every export is deterministic, so two exports of the same report can be compared.

#### Pull request checklist

- [ ] `ruff check .` prints `All checks passed!`
- [ ] `pytest -m "not integration" -q` passes on your laptop
- [ ] The pull request title has the form `type: summary (TASK-ID)` and the body says `Closes #<issue number>`
- [ ] No secrets, passwords, email addresses, personal data, or captures from a real network (CLAUDE.md rule 6)
- [ ] Any new dependency has a row in `docs/DEPENDENCIES.md` with its license
- [ ] CI is green and your reviewer approved
- [ ] You opened the HTML file with the network off

### AMO-04: CISA CPG 2.0 and CJIS v6.1 rows

**Due:** Week 5 (due Fri Nov 13) · **Milestone:** `W5 Alpha feature freeze` · **Needs first:** [AMO-02](#amo-02-pci-dss-v401-rows-checked-in-the-official-document) · **Kind:** process

**Issue labels:** `type:task` `phase:alpha` `owner:amory` `area:mapping`

#### Goal

Fill `mappings/cisa_cpg_2_0.yaml` and `mappings/cjis_6_1.yaml` with goal and control IDs read in the official documents, so all four frameworks appear in the alpha's reports (the Week 5 milestone).

#### Prerequisites

AMO-02 is merged (same method, so its review comments help here).

#### Steps

**Step 1.** Update `main` and create your branch for this task (one branch per task):

```bash
cd ~/projects/maxguard
source .venv/bin/activate
git checkout main && git pull
git checkout -b amory/cpg-cjis-rows
```

If `source .venv/bin/activate` fails, you have not made the virtual environment yet: do Week 0 section 0.11 first.

**Step 2.** CPG 2.0: open the CPG 2.0 report from the `source` page (the direct PDF link is in the file's header). CPG 2.0 regrouped the goals, so never copy an ID from an older CPG version. Write rows with `verified: "CPG 2.0 report, p. <page>"`.

**Step 3.** CJIS: download CJIS Security Policy v6.1 from the FBI's resource center (the `source` link). Copy control IDs and titles exactly as v6.1 prints them, with `verified: "CJIS SP v6.1, section <x>, p. <page>"`.

**Step 4.** Run `pytest tests/unit/test_mappings.py -q` and check the Telnet finding in `maxguard analyze tests/fixtures/zeek/telnet --no-ai` lists controls from all four frameworks.

**Step 5.** Commit, push, and open the pull request:

```bash
git add -A
git status          # only this task's files: nothing from .venv/, data/ or lab/captures/
git commit -m "feat: CISA CPG 2.0 and CJIS v6.1 mapping rows (AMO-04)"
git push -u origin HEAD
```

`HEAD` means "the branch I am on", so you do not have to retype its name. Open the repository on github.com: a yellow bar shows your branch with a **Compare & pull request** button. Click it, keep the title `feat: CISA CPG 2.0 and CJIS v6.1 mapping rows (AMO-04)`, fill in the template (paste the real output of the commands above under **How I tested it**), write `Closes #<issue number>` (this task's issue), and pick **@ahmadalkhoudeir** under **Reviewers**. Click **Create pull request**, then fix anything CI or the reviewer finds with new commits on the same branch.

#### How to test

The mapping tests pass and the Telnet finding has controls in all four frameworks.

#### What you just did and why

CPG gives small organizations a short, practical list, and CJIS matters to anyone who touches criminal-justice data (local police and the companies that serve them). Both are locked to exact versions in `docs/PROJECT_DECISIONS.md`, and before each release someone must check they are still the current versions (CLAUDE.md rule 8).

#### Pull request checklist

- [ ] `ruff check .` prints `All checks passed!`
- [ ] `pytest -m "not integration" -q` passes on your laptop
- [ ] The pull request title has the form `type: summary (TASK-ID)` and the body says `Closes #<issue number>`
- [ ] No secrets, passwords, email addresses, personal data, or captures from a real network (CLAUDE.md rule 6)
- [ ] Any new dependency has a row in `docs/DEPENDENCIES.md` with its license
- [ ] CI is green and your reviewer approved
- [ ] Every row has a page or section in `verified`
- [ ] Ahmad checked the rows

## Spring 2027: v2.0

### AMO-05: Chain-of-custody log

**Due:** Spring S1-S4 (due Fri Feb 12, 2027) · **Milestone:** `S1-S4 Live sensor` · **Needs first:** [JAI-08](jaiden.md#jai-08-ed25519-signing-library) · **Kind:** code, tested

**Issue labels:** `type:task` `phase:spring` `owner:amory` `area:mapping` `area:release`

#### Goal

Write `maxguard/custody/log.py`: an append-only, tamper-evident log of what happened to evidence (capture received, report generated, report exported). Each entry holds the previous entry's hash and an Ed25519 signature, so editing, deleting, or reordering any line is detected.

#### Prerequisites

JAI-08 (signing) is merged.

#### Steps

**Step 1.** Update `main` and create your branch for this task (one branch per task):

```bash
cd ~/projects/maxguard
source .venv/bin/activate
git checkout main && git pull
git checkout -b amory/custody-log
```

If `source .venv/bin/activate` fails, you have not made the virtual environment yet: do Week 0 section 0.11 first.

**Step 2.** Create `maxguard/custody/log.py`:

```python
"""Chain-of-custody log (Amory, AMO-05).

An append-only JSON Lines file that records what happened to evidence, for
example "capture_received", "report_generated" or "report_exported". Each line
is one entry:

    seq         1, 2, 3, ... in the order the entries were written
    at          when it happened, in Unix seconds (passed in: never read from the clock)
    action      what happened
    artifact    the file's name (not its path, which differs between machines)
    sha256      the file's SHA-256 at that moment
    size        the file's size in bytes
    actor       who did it
    prev_hash   the entry_hash of the entry before (64 zeros for the first entry)
    entry_hash  SHA-256 of this entry as canonical JSON, without entry_hash and signature
    signature   Ed25519 signature of entry_hash (base64), made with the custody key

Why both a hash chain and a signature:
- The chain shows that no entry was edited, removed or moved: each entry pins
  the hash of the one before it.
- The signature shows that this MaxGuard installation wrote the entries. Without
  it, someone who changed a line could simply recompute every hash after it.

What the chain cannot show: that entries were cut off at the END. A shorter log
is still a valid chain. So `verify` prints the last entry's hash ("head"): write
it into the report or the case notes, and compare it later.

Verify a log from the command line:
    python -m maxguard.custody.log verify custody.jsonl custody_ed25519_public.pem
"""

from __future__ import annotations

import argparse
import base64
import binascii
import hashlib
import json
import os
import sys
import threading
from pathlib import Path

from maxguard.custody.signing import sign
from maxguard.custody.signing import verify as signature_ok
from maxguard.ids import canonical_json

GENESIS_HASH = "0" * 64  # the "entry before" the first entry
HASHED_FIELDS = ("seq", "at", "action", "artifact", "sha256", "size", "actor", "prev_hash")
ALL_FIELDS = (*HASHED_FIELDS, "entry_hash", "signature")

# Two threads appending at once could both take the same seq. The API runs
# analyses in worker threads, so appends inside one process take turns.
# Only one program (the console) should write to a log.
_append_lock = threading.Lock()


def append(log_path: Path, *, action: str, artifact_path: Path, actor: str, at: float,
           private_key_path: Path) -> dict:
    """Add one signed entry for artifact_path to the log and return it."""
    log_path = Path(log_path)
    with _append_lock:
        last = last_entry(log_path)
        entry = {
            "seq": last["seq"] + 1 if last else 1,
            "at": at,
            "action": action,
            "artifact": Path(artifact_path).name,
            "sha256": file_sha256(artifact_path),
            "size": Path(artifact_path).stat().st_size,
            "actor": actor,
            "prev_hash": last["entry_hash"] if last else GENESIS_HASH,
        }
        entry["entry_hash"] = entry_hash(entry)
        signature = sign(entry["entry_hash"].encode("ascii"), private_key_path)
        entry["signature"] = base64.b64encode(signature).decode("ascii")
        write_line(log_path, entry)
    return entry


def entry_hash(entry: dict) -> str:
    """SHA-256 of the hashed fields in one fixed text form (sorted keys, no spaces)."""
    hashed = {field: entry[field] for field in HASHED_FIELDS}
    return hashlib.sha256(canonical_json(hashed).encode("utf-8")).hexdigest()


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def last_entry(log_path: Path) -> dict | None:
    if not log_path.exists():
        return None
    lines = log_path.read_text(encoding="utf-8").splitlines()
    return json.loads(lines[-1]) if lines else None


def write_line(log_path: Path, entry: dict) -> None:
    """Append one line and make sure it is on the disk before returning."""
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, sort_keys=True) + "\n")
        f.flush()
        os.fsync(f.fileno())  # a power cut right after append() must not lose the entry


def verify(log_path: Path, public_key_path: Path) -> tuple[bool, int | None, str]:
    """Check every entry in order.

    Returns (True, None, "ok"), or (False, first_bad_seq, reason) where
    first_bad_seq is the position (1, 2, 3, ...) of the first entry that fails."""
    previous = GENESIS_HASH
    lines = Path(log_path).read_text(encoding="utf-8").splitlines()
    for position, line in enumerate(lines, start=1):
        problem = check_entry(line, position, previous, public_key_path)
        if problem:
            return False, position, problem
        previous = json.loads(line)["entry_hash"]
    return True, None, "ok"


def check_entry(line: str, position: int, previous: str, public_key_path: Path) -> str | None:
    """Why this line is not a good entry, or None if it is."""
    try:
        entry = json.loads(line)
    except json.JSONDecodeError:
        return "not valid JSON"
    if not isinstance(entry, dict) or set(entry) != set(ALL_FIELDS):
        return "missing or unexpected fields"
    if entry["seq"] != position:
        return f"seq is {entry['seq']!r}, expected {position}: an entry was removed or moved"
    if entry["prev_hash"] != previous:
        return "prev_hash does not match the entry before: an entry was removed, moved or changed"
    if entry_hash(entry) != entry["entry_hash"]:
        return "entry_hash does not match the entry: the entry was changed after it was written"
    try:
        signature = base64.b64decode(entry["signature"], validate=True)
    except (binascii.Error, TypeError):
        return "signature is not valid base64"
    if not signature_ok(entry["entry_hash"].encode("ascii"), signature, public_key_path):
        return "bad signature: the entry was forged, or this is the wrong public key"
    return None


def head(log_path: Path) -> tuple[int, str]:
    """(seq, entry_hash) of the last entry: record it elsewhere to detect a cut-off log."""
    last = last_entry(Path(log_path))
    return (last["seq"], last["entry_hash"]) if last else (0, GENESIS_HASH)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m maxguard.custody.log",
                                     description="Check a MaxGuard chain-of-custody log.")
    commands = parser.add_subparsers(dest="command", required=True)
    check = commands.add_parser("verify", help="check every entry's hash chain and signature")
    check.add_argument("log", type=Path, help="the custody log (JSON Lines)")
    check.add_argument("public_key", type=Path, help="the custody public key (PEM)")
    args = parser.parse_args(argv)

    ok, bad_seq, reason = verify(args.log, args.public_key)
    if not ok:
        print(f"FAILED at seq {bad_seq}: {reason}")
        return 1
    seq, last_hash = head(args.log)
    noun = "entry" if seq == 1 else "entries"
    print(f"ok: {seq} {noun}, head {last_hash}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

Three details: `at` comes from the caller, never from the clock (the same rule as the stores), so the same inputs give a byte-identical log, because Ed25519 signatures are deterministic; `os.fsync` puts each entry on the disk before `append()` returns; and a hash chain cannot show that entries were cut off at the end, so `verify` prints the last entry's hash (the head) for you to record somewhere else, such as the case notes or the exported report.

**Step 3.** Create the tests `tests/unit/test_custody.py`:

```python
"""Tests for the chain-of-custody log (Amory, AMO-05)."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from maxguard.custody import log as custody
from maxguard.custody.signing import generate_keypair

AT = 1791250000.0  # a fixed time: the log never reads the clock


@pytest.fixture
def keys(tmp_path) -> tuple[Path, Path]:
    return generate_keypair(tmp_path / "keys")


@pytest.fixture
def artifacts(tmp_path) -> list[Path]:
    """Three small evidence files (stand-ins for a capture and two reports)."""
    files = []
    for name, data in (("telnet.pcap", b"capture bytes"), ("report.json", b"{}"),
                       ("report.html", b"<html></html>")):
        path = tmp_path / "evidence" / name
        path.parent.mkdir(exist_ok=True)
        path.write_bytes(data)
        files.append(path)
    return files


def write_log(log_path: Path, artifacts: list[Path], private_key: Path) -> list[dict]:
    actions = ("capture_received", "report_generated", "report_exported")
    return [custody.append(log_path, action=action, artifact_path=artifact, actor="amory",
                           at=AT + i, private_key_path=private_key)
            for i, (action, artifact) in enumerate(zip(actions, artifacts, strict=True))]


@pytest.fixture
def log_path(tmp_path, artifacts, keys) -> Path:
    path = tmp_path / "custody.jsonl"
    write_log(path, artifacts, keys[0])
    return path


def read_lines(path: Path) -> list[str]:
    return path.read_text().splitlines()


def write_lines(path: Path, lines: list[str]) -> None:
    path.write_text("\n".join(lines) + "\n")


def change_entry(path: Path, position: int, field: str, value) -> None:
    lines = read_lines(path)
    entry = json.loads(lines[position - 1])
    entry[field] = value
    lines[position - 1] = json.dumps(entry, sort_keys=True)
    write_lines(path, lines)


# ---------- a good log ----------

def test_a_good_chain_verifies(log_path, keys):
    assert custody.verify(log_path, keys[1]) == (True, None, "ok")


def test_entries_link_to_each_other(log_path, artifacts):
    entries = [json.loads(line) for line in read_lines(log_path)]
    assert [e["seq"] for e in entries] == [1, 2, 3]
    assert entries[0]["prev_hash"] == "0" * 64
    assert entries[1]["prev_hash"] == entries[0]["entry_hash"]
    assert entries[2]["prev_hash"] == entries[1]["entry_hash"]

    first = entries[0]
    assert set(first) == set(custody.ALL_FIELDS)
    assert first["artifact"] == "telnet.pcap"  # the name, never the path
    assert first["sha256"] == hashlib.sha256(b"capture bytes").hexdigest()
    assert first["size"] == len(b"capture bytes")
    assert first["at"] == AT
    assert first["action"] == "capture_received"


def test_append_never_reads_the_clock(tmp_path, artifacts, keys, monkeypatch):
    def no_clock():
        raise AssertionError("the custody log must not read the clock")

    monkeypatch.setattr("time.time", no_clock)
    entry = custody.append(tmp_path / "c.jsonl", action="capture_received",
                           artifact_path=artifacts[0], actor="amory", at=AT,
                           private_key_path=keys[0])
    assert entry["at"] == AT


def test_same_inputs_give_the_same_log(tmp_path, artifacts, keys):
    # Ed25519 signatures are deterministic, so the whole file is.
    write_log(tmp_path / "a.jsonl", artifacts, keys[0])
    write_log(tmp_path / "b.jsonl", artifacts, keys[0])
    assert (tmp_path / "a.jsonl").read_bytes() == (tmp_path / "b.jsonl").read_bytes()


# ---------- tampering ----------

@pytest.mark.parametrize("field, value", [
    ("seq", 7),
    ("at", AT + 3600),
    ("action", "report_deleted"),
    ("artifact", "other.pcap"),
    ("sha256", "0" * 64),
    ("size", 1),
    ("actor", "mallory"),
    ("prev_hash", "f" * 64),
    ("entry_hash", "e" * 64),
    ("signature", "AAAA"),
])
def test_changing_any_field_fails_at_that_entry(log_path, keys, field, value):
    change_entry(log_path, 2, field, value)
    ok, bad_seq, reason = custody.verify(log_path, keys[1])
    assert (ok, bad_seq) == (False, 2)
    assert reason


def test_a_rewritten_entry_with_a_fresh_hash_fails_on_the_signature(log_path, keys):
    entry = json.loads(read_lines(log_path)[1])
    entry["actor"] = "mallory"
    change_entry(log_path, 2, "actor", "mallory")
    change_entry(log_path, 2, "entry_hash", custody.entry_hash(entry))
    ok, bad_seq, reason = custody.verify(log_path, keys[1])
    assert (ok, bad_seq) == (False, 2)
    assert "signature" in reason


def test_deleting_a_line_fails(log_path, keys):
    lines = read_lines(log_path)
    write_lines(log_path, [lines[0], lines[2]])
    ok, bad_seq, reason = custody.verify(log_path, keys[1])
    assert (ok, bad_seq) == (False, 2)
    assert "removed or moved" in reason


def test_swapping_two_lines_fails(log_path, keys):
    lines = read_lines(log_path)
    write_lines(log_path, [lines[0], lines[2], lines[1]])
    assert custody.verify(log_path, keys[1])[:2] == (False, 2)


def test_a_line_that_is_not_json_fails(log_path, keys):
    lines = read_lines(log_path)
    write_lines(log_path, [lines[0], "not json", *lines[1:]])
    assert custody.verify(log_path, keys[1]) == (False, 2, "not valid JSON")


def test_the_wrong_public_key_fails_at_the_first_entry(log_path, tmp_path):
    _, other_public = generate_keypair(tmp_path / "other-keys")
    ok, bad_seq, reason = custody.verify(log_path, other_public)
    assert (ok, bad_seq) == (False, 1)
    assert "wrong public key" in reason


def test_cutting_off_the_end_needs_the_recorded_head(log_path, keys):
    # A shorter log is still a valid chain: this is why the head is recorded elsewhere.
    recorded = custody.head(log_path)
    write_lines(log_path, read_lines(log_path)[:2])
    assert custody.verify(log_path, keys[1]) == (True, None, "ok")
    assert custody.head(log_path) != recorded
    assert recorded[0] == 3


# ---------- command line ----------

def test_command_line_verify(log_path, keys, capsys):
    assert custody.main(["verify", str(log_path), str(keys[1])]) == 0
    seq, last_hash = custody.head(log_path)
    assert capsys.readouterr().out == f"ok: 3 entries, head {last_hash}\n"

    change_entry(log_path, 3, "actor", "mallory")
    assert custody.main(["verify", str(log_path), str(keys[1])]) == 1
    assert capsys.readouterr().out.startswith("FAILED at seq 3: entry_hash does not match")
```

**Step 4.** Run them:

```bash
pytest tests/unit/test_custody.py -q
```

Expected output:

```text
.....................                                                                        [100%]
21 passed in 0.18s
```

**Step 5.** Try the command line: make a key pair, log one capture, verify the log, change one word in it, and verify again:

```bash
python -c "from pathlib import Path; from maxguard.custody.signing import generate_keypair; from maxguard.custody.log import append; private, public = generate_keypair(Path('data/keys')); append(Path('data/custody.jsonl'), action='capture_received', artifact_path=Path('tests/pcaps/telnet.pcap'), actor='amory', at=1791250000.0, private_key_path=private)"
python -m maxguard.custody.log verify data/custody.jsonl data/keys/custody_ed25519_public.pem
sed -i.bak 's/"actor": "amory"/"actor": "mallory"/' data/custody.jsonl
python -m maxguard.custody.log verify data/custody.jsonl data/keys/custody_ed25519_public.pem
```

Expected output:

```text
ok: 1 entry, head ef422ca1d6ea20c4beb60151895e2830b0bc0913272bc0aee61a94c270c43ec0
FAILED at seq 1: entry_hash does not match the entry: the entry was changed after it was written
```

*Your head hash is the same as this one: it covers the entry (file hash, time, actor), not the signature, and the inputs here are fixed. The last command exits with 1.*

**Step 6.** Commit, push, and open the pull request:

```bash
git add -A
git status          # only this task's files: nothing from .venv/, data/ or lab/captures/
git commit -m "feat: tamper-evident chain-of-custody log (AMO-05)"
git push -u origin HEAD
```

`HEAD` means "the branch I am on", so you do not have to retype its name. Open the repository on github.com: a yellow bar shows your branch with a **Compare & pull request** button. Click it, keep the title `feat: tamper-evident chain-of-custody log (AMO-05)`, fill in the template (paste the real output of the commands above under **How I tested it**), write `Closes #<issue number>` (this task's issue), and pick **@ahmadalkhoudeir** under **Reviewers**. Click **Create pull request**, then fix anything CI or the reviewer finds with new commits on the same branch.

#### How to test

All tamper cases fail verification at the right line, and a clean log verifies.

#### What you just did and why

If MaxGuard's findings are ever used in an incident report, someone will ask how you know the capture and report were not changed afterwards. A hash chain shows that no line was edited or removed, and the signature shows that the log was written by this MaxGuard installation and not rebuilt by someone else.

#### Pull request checklist

- [ ] `ruff check .` prints `All checks passed!`
- [ ] `pytest -m "not integration" -q` passes on your laptop
- [ ] The pull request title has the form `type: summary (TASK-ID)` and the body says `Closes #<issue number>`
- [ ] No secrets, passwords, email addresses, personal data, or captures from a real network (CLAUDE.md rule 6)
- [ ] Any new dependency has a row in `docs/DEPENDENCIES.md` with its license
- [ ] CI is green and your reviewer approved
- [ ] No key file is committed
