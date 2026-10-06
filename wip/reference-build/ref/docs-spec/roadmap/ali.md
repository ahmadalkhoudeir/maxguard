# Ali: AI Model Evaluation Engineer

**Ali Al-Kheder** (@al-kheder) · Module: AI evaluation · Reviewer for your pull requests: @MeliorExi (Jonattan) · Ask first when stuck: Jonattan

This is your part of the MaxGuard v2.0 roadmap. Read [the roadmap overview](README.md) once, then work top to bottom: Week 0 first, then your tasks in order. Each task's ID is also the start of its GitHub issue's title.

## Your tasks

| Task | Due | Title | Needs first | Kind |
|---|---|---|---|---|
| [ALI-00](#week-0--onboarding-due-friday-october-9-2026) | W0 | Week 0 onboarding (Ali) | — | process |
| [ALI-01](#ali-01-model-shortlist-and-license-check) | W1 | Model shortlist and license check | — | process |
| [ALI-02](#ali-02-evaluation-set-the-same-13-questions-for-every-model) | W2 | Evaluation set: the same 13 questions for every model | [FIO-02](fiona.md#fio-02-tls-and-certificate-rules), [JAK-03](jakub.md#jak-03-cleartext-and-rdp-rules-the-rule-set-is-complete), [AMO-01](amory.md#amo-01-nist-sp-800-53-mapping-file-and-the-mapping-checks), [JAI-03](jaiden.md#jai-03-common-event-schema-the-normalizer-and-record-lookup) | code, tested |
| [ALI-03](#ali-03-benchmark-script-speed-citations-and-unsupported-details) | W3 | Benchmark script: speed, citations, and unsupported details | [ALI-02](#ali-02-evaluation-set-the-same-13-questions-for-every-model), [JON-02](jonattan.md#jon-02-ollama-client-one-evidence-citing-explanation-per-finding) | code, tested |
| [ALI-04](#ali-04-run-the-benchmark-on-both-tiers-and-propose-the-default-models) | W4 | Run the benchmark on both tiers and propose the default models | [ALI-01](#ali-01-model-shortlist-and-license-check), [ALI-03](#ali-03-benchmark-script-speed-citations-and-unsupported-details) | process |
| [ALI-05](#ali-05-re-evaluate-the-models-against-prompt-injection-and-the-spring-rules) | S8 | Re-evaluate the models against prompt injection and the spring rules | [ALI-04](#ali-04-run-the-benchmark-on-both-tiers-and-propose-the-default-models), [JON-06](jonattan.md#jon-06-prompt-injection-tests-for-the-ai-layer) | process |

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
git config --global user.name "Ali Al-Kheder"
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
git checkout -b ali/week0-team-row
```

2. **Make the change.** Run `code .`, open `docs/TEAM.md`, and add this line at
   the end (keep the `|` characters):

```markdown
| Ali Al-Kheder | AI Model Evaluation Engineer | al-kheder | AI evaluation |
```

3. **Commit** (the message says *what changed*, starting with a type such as
   `docs:`, `feat:`, `fix:` or `test:`; see `docs/CONTRIBUTING.md`):

```bash
git add docs/TEAM.md
git commit -m "docs: add Ali to TEAM.md"
```

4. **Push** your branch to GitHub:

```bash
git push -u origin ali/week0-team-row
```

Expected (from the planning simulation; the first lines differ on GitHub):

```text
 * [new branch]      ali/week0-team-row -> ali/week0-team-row
branch 'ali/week0-team-row' set up to track 'origin/ali/week0-team-row'.
```

5. **Open the pull request** and ask for a review:

```bash
gh pr create --base main --title "docs: add Ali to TEAM.md" --body "Week 0 onboarding." --reviewer MeliorExi
```

`gh` prints the pull request's web address. (You can also click the link Git
printed after the push and press **Create pull request**.)

6. **After approval**, click **Squash and merge** on GitHub, then update your laptop:

```bash
git checkout main && git pull
git branch -d ali/week0-team-row
```

**If GitHub says "This branch has conflicts":** eight people are adding a line
to the same file this week, so this is expected. Bring `main` into your branch
and keep both lines:

```bash
git checkout main && git pull
git checkout ali/week0-team-row
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
   `ALI-01: pytest cannot import maxguard`). In the body, paste the
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

### ALI-01: Model shortlist and license check

**Due:** Week 1 (due Fri Oct 16) · **Milestone:** `W1 Building blocks` · **Needs first:** none · **Kind:** process

**Issue labels:** `type:task` `phase:alpha` `owner:ali` `area:ai`

#### Goal

Start `docs/model-eval/README.md`: the two hardware tiers, the shortlist of models for each, and for every model its license, whether MaxGuard may ship it in the offline bundle, and exactly what notice or attribution that requires. License is a hard gate: a model we may not redistribute cannot be the default.

#### Prerequisites

None. You can start in Week 1.

#### Steps

**Step 1.** Update `main` and create your branch for this task (one branch per task):

```bash
cd ~/projects/maxguard
source .venv/bin/activate
git checkout main && git pull
git checkout -b ali/model-shortlist
```

If `source .venv/bin/activate` fails, you have not made the virtual environment yet: do Week 0 section 0.11 first.

**Step 2.** Create `docs/model-eval/README.md` with this starting text. It was drafted in planning from search results, because the model sites (Hugging Face, ollama.com, Google, Meta) were blocked there:

````markdown
# Choosing the local AI model (evaluation template)

> **Status: template.** No model could be downloaded in the planning environment where this was
> written, so no real model was benchmarked there. Every cell that says
> **not run - verify on hardware** must be filled in from a real run on the
> matching hardware. Licenses were checked on 2026-10-06 (sources in section 9).

## 1. What we are choosing

MaxGuard asks a local model (through Ollama) to explain each finding in 2 to 4
plain sentences. The model never decides what is an alert: the rules do that.
Every sentence must cite evidence `record_id`s, and `maxguard/ai/citations.py`
drops any sentence that does not.

We pick **one default model per hardware tier**:

| Tier | Hardware class | Model size limit |
|---|---|---|
| `pi` | Raspberry Pi class sensor/appliance | up to 4B parameters |
| `laptop` | ordinary laptop or small PC | up to 8B parameters |

The winner replaces `TEMPORARY_DEFAULT_MODEL = "qwen3:4b"` in
`maxguard/ai/ollama_client.py` and goes into the offline bundle.

## 2. Shortlist and licenses

"Bundle" means our offline installer, which copies the model files to the
user's machine. That is a redistribution, so the license conditions below
apply to us. Apache-2.0 and MIT are the simplest; the Llama and Gemma licenses
are custom licenses with extra duties.

| Tier | Ollama tag | Model | License | Allowed in our bundle? | What we must ship or show |
|---|---|---|---|---|---|
| pi | `qwen3:4b` | Qwen3 4B (Alibaba Qwen) | Apache-2.0 | Yes | A copy of the Apache-2.0 license; keep existing notices; include the model's NOTICE file if it has one (none in the GitHub repo; the Hugging Face repo could not be checked here) |
| pi | `llama3.2:3b` | Llama 3.2 3B Instruct (Meta), text only | Llama 3.2 Community License | Yes, with conditions | (1) a copy of the license; (2) show "Built with Llama" prominently on a related website, user interface, blog post, about page or product documentation; (3) a "Notice" text file with exactly: `Llama 3.2 is licensed under the Llama 3.2 Community License, Copyright © Meta Platforms, Inc. All Rights Reserved.`; (4) use must follow Meta's Acceptable Use Policy, which is part of the license |
| pi | `phi4-mini` | Phi-4-mini-instruct 3.8B (Microsoft) | MIT | Yes | The MIT license text with Microsoft's copyright line. **Read the license file before shipping**: the primary file (Hugging Face) was blocked here; MIT is confirmed only by search results quoting the model card |
| pi | `gemma3:4b` | Gemma 3 4B (Google) | Gemma Terms of Use (custom) | Yes, with conditions | (1) put the use restrictions of section 3.2 (Gemma Prohibited Use Policy) into our own terms as an enforceable part and tell users Gemma is subject to them; (2) give every recipient a copy of the Gemma Terms of Use; (3) mark any file we modify; (4) a "Notice" text file with exactly: `Gemma is provided under and subject to the Gemma Terms of Use found at ai.google.dev/gemma/terms`. Quoted from search results (ai.google.dev was blocked here): **read the full terms before shipping** |
| laptop | `qwen3:8b` | Qwen3 8B | Apache-2.0 | Yes | Same as `qwen3:4b` |
| laptop | `llama3.1:8b` | Llama 3.1 8B Instruct (Meta) | Llama 3.1 Community License | Yes, with conditions | Same four duties as Llama 3.2, with the notice `Llama 3.1 is licensed under the Llama 3.1 Community License, Copyright © Meta Platforms, Inc. All Rights Reserved.` |
| laptop | `granite4.2:8b` | Granite 4.2 8B (IBM) | Apache-2.0 | Yes | A copy of the Apache-2.0 license (no NOTICE file in the GitHub repo) |

Notes:

- **Granite:** the plan named `granite3.3:8b`. Granite 4.2 (3B, 8B, 30B, Apache-2.0)
  is the newest Granite generation, so the laptop shortlist uses `granite4.2:8b`.
  Search results show Ollama tags such as `granite4.2:8b-q4_0` and
  `granite4.2:8b-q8_0`; confirm the plain `granite4.2:8b` tag with `ollama pull`.
  Granite 3.3 8B (`granite3.3:8b`) is also Apache-2.0 if you want it as a comparison.
  Granite 4.2 has a thinking mode; MaxGuard sends `"think": false`.
- **Llama 3.2 EU clause:** Meta's Acceptable Use Policy withholds the license
  from people and companies in the EU only for the *multimodal* Llama 3.2
  models. The 3B model is text only, so this clause does not apply to it.
- **Apache-2.0 duties** (section 4 of the license): give recipients a copy of
  the license, mark files you changed, keep copyright and attribution notices,
  and pass on the NOTICE file if the work has one.
- **Ollama can store a license text with a model.** On the test machine,
  `ollama show --license <tag>` prints the one Ollama ships with that model.
  Compare it with this table before shipping a model.
- **Tags move.** A tag such as `qwen3:4b` can point to a newer build later
  (Qwen's own README warns that Ollama's names can differ from Qwen's). The
  benchmark records the model digest, so we know exactly which build was tested.

## 3. The evaluation set

`tests/fixtures/ai_eval/eval_set.json` holds 13 questions, one per Fall 2026
rule. `scripts/make_eval_set.py` builds it from the fixture logs in
`tests/fixtures/zeek/` exactly the way the pipeline does: run the rules, apply
the mapping files in `mappings/`, then find each cited evidence record by
re-hashing every log record with `maxguard.ids.record_id`. `clean_tls13` is
skipped (nothing to explain), and the hand-made `_handmade/rdp` fixture is added
so `rdp.standard_security` is covered too.

```bash
python -m scripts.make_eval_set
```

Expected output:

```
wrote 13 items (13 rules) to <repo>/tests/fixtures/ai_eval/eval_set.json
```

The file is the same byte for byte on every run (checked on Python 3.11 and
3.13). Rebuild and commit it whenever a rule, a mapping file or a fixture
changes; `tests/unit/test_benchmark.py` fails until you do.

## 4. What the benchmark measures

`scripts/benchmark_models.py` calls MaxGuard's own `explain()` (same prompt,
same JSON schema, `temperature 0`, `seed 42`, `think: false`, same citation
check), so we measure what users will get. For each model and each run it:

1. unloads and reloads the model (the load time is printed, not scored),
2. asks all 13 questions and times each answer.

Why reload? Ollama keeps recent prompts in a cache. In the planning environment (Ollama
0.35.1, tiny test model), asking the same question a second time reused 2498 of
its 2499 prompt tokens from the cache instead of processing them again (prompt
processing 32 ms the first time, 1 to 15 ms after). After an unload and reload,
0 tokens came from the cache. Without the reload, run 2 would skip work that
real use never skips, and look faster than it is.

### 4.1 Columns of `docs/model-eval/raw_results.csv`

| Column | Meaning |
|---|---|
| `tier`, `model` | from the command line |
| `model_digest`, `quantization` | which build was tested (from Ollama's `/api/tags`) |
| `ollama_version`, `eval_set` | Ollama version, and a fingerprint of the eval set file |
| `run`, `item_id`, `rule_id` | which pass and which question |
| `seconds` | time for one `explain()` call (what the user waits per finding) |
| `sentences_kept`, `sentences_dropped` | after the citation check |
| `unsupported_count`, `unsupported_details` | see 4.2 |
| `answer_hash`, `same_as_run_1` | see 4.3 |
| `error` | e.g. a timeout; the run goes on |
| `text` | the kept sentences, for the human review |

The summary printed at the end has, per model: `calls`, `errors`, `median_s`,
`explained` (run-1 answers with at least one kept sentence), `drop_rate`
(dropped / all sentences), `unsupported(run 1)` and `identical`.
`explained` matters: an answer whose JSON was cut off keeps 0 and drops 0
sentences, so its drop rate looks perfect while it explains nothing.

### 4.2 Unsupported details

Only kept sentences reach the user, so only they are checked. Every IP
address, port, host name, TLS version and cipher name in them must appear in
the finding or in its evidence records. The script finds them with these
patterns:

| Kind | How it is found | Found | Not found |
|---|---|---|---|
| IP | IPv4 regex `\b(?:\d{1,3}\.){3}\d{1,3}\b`; IPv6 candidates `\b[0-9a-f]{1,4}(?::[0-9a-f]{0,4}){2,7}`; Python's `ipaddress` keeps only real addresses | `172.18.0.2`, `fe80::1` | `999.1.2.3`, a MAC address, `10:30:00` |
| Port | `port 23` / `ports 80`, `172.18.0.2:4432`, `23/tcp` | those three forms | a bare number (`23 packets`), `port4431.lab.invalid` |
| Host | labels joined by dots, last label 2+ letters | `port4431.lab.invalid`, `ssl.log` | `TLSv1.2`, `4.0.1`, `e.g.` |
| TLS version | `TLSv10`, `TLS 1.0`, `TLSv1.0`, `SSLv3`, all written as `TLS 1.0` | those forms | `DTLS 1.2` |
| Cipher | IANA style `TLS_..._...` and OpenSSL style ending in `-SHA…`, `-MD5` or `-POLY1305` | `TLS_RSA_WITH_NULL_SHA256`, `NULL-SHA256` | `SHA-1` |

In the records, ports are also read from the port fields (`id.orig_p`,
`id.resp_p`, `src_port`, `dest_port`). A host name counts as supported when a
longer known name ends with it (`lab.invalid` is fine if
`port4431.lab.invalid` is in the records).

Known limits: `ports 80 and 443` checks only 80; `TLS 1.0/1.1` reads only
1.0; IPv6 addresses that start with `::` are not found; cipher names are
compared literally (`NULL-SHA256` is flagged even though it is the OpenSSL
name of `TLS_RSA_WITH_NULL_SHA256`).

**A flag is not always a mistake.** Real results of the check:

| Sentence (made up for this example) | Flagged | Verdict |
|---|---|---|
| Telnet finding: "... Use SSH on port 22 instead." | `port:22` | advice, fine |
| Weak TLS version: "... allow only TLS 1.2 or newer." | `tls:TLS 1.2` | advice, fine |
| Weak cipher: "... The client was 10.0.0.5." | `ip:10.0.0.5` | **made-up fact** |

So the raw count is only a pointer; section 6 asks a person to sort the flags.

### 4.3 Same answer twice (determinism)

With `temperature 0` and `seed 42` the answer should repeat. Ollama's
documentation says of `seed`: "Setting this to a specific number will make the
model generate the same text for the same prompt." The benchmark runs every
question twice by default (`--runs 2`), each run on a freshly loaded model,
and stores a short hash of each answer. `same_as_run_1` says `yes` or `no` for
run 2, and the summary prints `identical` as e.g. `13/13`. Any `no` goes into
the results notes. Compare `answer_hash` between the Pi and the laptop for the
same model too; write down whether they match (different hardware may round
differently, so a mismatch there is information, not a failure).

## 5. Running it

### 5.1 Start an Ollama for the evaluation

The production `docker/compose.yaml` keeps Ollama on an internal network with
no internet, so it can neither download models nor be reached from the host.
For the evaluation, start a separate Ollama with the same pinned version:

```bash
docker run -d --name ollama-eval -p 127.0.0.1:11434:11434 \
  -v ollama-eval:/root/.ollama ollama/ollama:0.35.1
docker exec ollama-eval ollama pull qwen3:4b          # needs internet
docker exec ollama-eval ollama show qwen3:4b          # check capabilities and quantization
docker exec ollama-eval ollama show --license qwen3:4b
```

Pull every model of the tier first. The script talks to
`http://127.0.0.1:11434` unless `OLLAMA_HOST` says otherwise.

### 5.2 Pi tier and laptop tier

From the repository root, on the matching machine:

```bash
python -m scripts.benchmark_models --tier pi qwen3:4b llama3.2:3b phi4-mini gemma3:4b
python -m scripts.benchmark_models --tier laptop qwen3:8b llama3.1:8b granite4.2:8b
```

Both commands append to `docs/model-eval/raw_results.csv`, so one file ends up
with both tiers. Delete the file to start a fresh evaluation. `--tier` only
labels the rows.

### 5.3 What the output looks like

Real output from the planning environment (Ollama 0.35.1 on port 21434, results written to
a scratch file). The model `maxguard-tiny:test` is **not a language model**: it
is a 27K-parameter file built only to test the script, and its answers are
always empty sentences that the citation check drops. The numbers mean
nothing; the shape is what you will see.

```
13 eval items (eval set 48db324924ec), Ollama 0.35.1 at http://127.0.0.1:21434, tier laptop
maxguard-tiny:test run 1: loaded in 0.3 s (not scored)
maxguard-tiny:test run 1 item 1/13 cert_expired/63ed8c36136c2c5a: 0.1 s, kept 0, dropped 1, unsupported 0
...
maxguard-tiny:test run 2: loaded in 0.3 s (not scored)
...
qwen3:4b: cannot load it (HTTP 404: model 'qwen3:4b' not found), skipping its remaining runs

model               tier     calls errors  median_s explained  drop_rate  unsupported(run 1)  identical
maxguard-tiny:test  laptop      26      0       0.0      0/13     100.0%                   0      13/13

raw results appended to ../ali-run/raw_results.csv
```

If Ollama is not running:

```
no Ollama answering at http://127.0.0.1:1: start it first
```

If none of the models is pulled (exit code 1, no CSV written):

```
qwen3:4b: cannot load it (HTTP 404: model 'qwen3:4b' not found), skipping its remaining runs
llama3.2:3b: cannot load it (HTTP 404: model 'llama3.2:3b' not found), skipping its remaining runs
no model could be loaded, so nothing was written
```

## 6. Results (fill in)

Hardware: **not run - verify on hardware** (write the exact board or laptop
model, RAM, storage, operating system). Ollama: 0.35.1. Eval set: `48db324924ec`
(change this if the eval set is rebuilt).

### Pi tier

| Model | Digest | Quant. | Median s | Explained | Drop rate | Flags (run 1) | Real made-up facts | Identical | Notes |
|---|---|---|---|---|---|---|---|---|---|
| `qwen3:4b` | not run - verify on hardware | | | | | | | | |
| `llama3.2:3b` | not run - verify on hardware | | | | | | | | |
| `phi4-mini` | not run - verify on hardware | | | | | | | | |
| `gemma3:4b` | not run - verify on hardware | | | | | | | | |

### Laptop tier

| Model | Digest | Quant. | Median s | Explained | Drop rate | Flags (run 1) | Real made-up facts | Identical | Notes |
|---|---|---|---|---|---|---|---|---|---|
| `qwen3:8b` | not run - verify on hardware | | | | | | | | |
| `llama3.1:8b` | not run - verify on hardware | | | | | | | | |
| `granite4.2:8b` | not run - verify on hardware | | | | | | | | |

### Human review

For every model, open `raw_results.csv` and, for each run-1 row with flags,
mark each flag as **advice** (fine) or **made-up fact** (bad). Put the number
of made-up facts in "Real made-up facts". Also read three full answers per
model (`text` column) and note whether they are plain, correct and useful for
a home or small-office user.

Things to check on hardware for the thinking models (`qwen3`, `granite4.2`):
with `think: false` the answers should arrive without long delays; if
`ollama show` lists `thinking` and the times are very long, note it.

## 7. Choosing the default (proposal for the team)

In this order:

1. The license allows our bundle and we can meet its duties (section 2).
2. Answers repeat (`identical` = 13/13). If not, write down why.
3. Fewest real made-up facts (after the human review).
4. Most questions explained (`explained`), then lowest drop rate.
5. Speed: `explain_all()` explains up to 20 findings one after another, so the
   longest wait for a full report is about 20 x median seconds. The team
   decides what is acceptable per tier.

If two models are close, prefer the Apache-2.0 or MIT one: fewer duties for the
offline bundle.

## 8. Newer models seen while checking licenses (not on the agreed shortlist)

Ask Ahmad (Security Lead) before adding any of these to the runs:

- **Gemma 4** (released 2026-04-02) is Apache-2.0, unlike Gemma 3. Its E2B
  size (2.3B effective parameters) fits the Pi tier. Ollama's README now uses
  `ollama run gemma4` as its example. The exact Ollama tags for each size were
  not checked.
- **Granite 4.2 3B** (Apache-2.0) would also fit the Pi tier.

## 9. Sources (checked 2026-10-06)

- Qwen3, Apache-2.0: Qwen3 README, "License Agreement" section,
  https://github.com/QwenLM/Qwen3/blob/main/README.md (also documents
  `ollama run qwen3:8b` and the warning about Ollama's naming)
- Llama 3.2 license and Acceptable Use Policy:
  https://github.com/meta-llama/llama-models/blob/main/models/llama3_2/LICENSE,
  https://github.com/meta-llama/llama-models/blob/main/models/llama3_2/USE_POLICY.md;
  text-only 3B: https://github.com/meta-llama/llama-models/blob/main/models/llama3_2/MODEL_CARD.md
- Llama 3.1 license: https://github.com/meta-llama/llama-models/blob/main/models/llama3_1/LICENSE
- Phi-4-mini, MIT: model card https://huggingface.co/microsoft/Phi-4-mini-instruct
  (blocked here; MIT confirmed by search results quoting it, e.g.
  https://build.nvidia.com/microsoft/phi-4-mini-instruct)
- Gemma Terms of Use (section 3.1 and the Notice text): https://ai.google.dev/gemma/terms
  (blocked here; quoted from search results, last modified 2025-03-24)
- Granite 4.2 and 3.3, Apache-2.0: https://github.com/ibm-granite/granite-4.2-language-models,
  https://github.com/ibm-granite/granite-3.3-language-models (README "License" and LICENSE);
  Ollama tags `granite4.2:8b-q4_0` / `-q8_0` seen at https://ollama.com/library/granite4.2 (search results)
- Gemma 4, Apache-2.0: Docker Hub model card https://hub.docker.com/r/ai/gemma4 (links
  https://ai.google.dev/gemma/docs/gemma_4_license) and news coverage of the 2026-04-02 release
- Ollama tags `gemma3`, `llama3.2`, `llama3.1`, `phi4-mini`, `granite3.3`: Ollama README model
  table, https://github.com/ollama/ollama/blob/v0.9.0/README.md
- Ollama 0.35.1 API (load, unload, `/api/tags`, `keep_alive` default 5m, `think`, `seed`):
  https://github.com/ollama/ollama/blob/v0.35.1/docs/api.md and
  https://github.com/ollama/ollama/blob/v0.35.1/docs/modelfile.mdx; `think: false` accepted for
  models without thinking: https://github.com/ollama/ollama/blob/v0.35.1/server/routes.go
  (ChatHandler), and observed with the test model
````

**Step 3.** **Check every row of section 2 against the primary source** and fix the file: open each model's own license (the Hugging Face model card's LICENSE file, Meta's Llama license page, Google's Gemma Terms of Use, IBM's Granite repository), and for Ollama also run `ollama show --license <tag>` after pulling. Watch for one trap: a GitHub repository's license can cover only the *code* in it, not the model weights (Google's `gemma` library is Apache-2.0, but the Gemma *models* are under the Gemma Terms of Use).

**Step 4.** Add a column **Checked on** with the date and the exact URL you read, and remove every "read the license file before shipping" warning you resolved.

**Step 5.** Post the shortlist in Discussions (category *Ideas*) and ask Jonattan and Ahmad whether any model should be added or removed before ALI-04 runs.

**Step 6.** Commit, push, and open the pull request:

```bash
git add -A
git status          # only this task's files: nothing from .venv/, data/ or lab/captures/
git commit -m "docs: model shortlist with verified licenses (ALI-01)"
git push -u origin HEAD
```

`HEAD` means "the branch I am on", so you do not have to retype its name. Open the repository on github.com: a yellow bar shows your branch with a **Compare & pull request** button. Click it, keep the title `docs: model shortlist with verified licenses (ALI-01)`, fill in the template (paste the real output of the commands above under **How I tested it**), write `Closes #<issue number>` (this task's issue), and pick **@MeliorExi** under **Reviewers**. Click **Create pull request**, then fix anything CI or the reviewer finds with new commits on the same branch.

#### How to test

Every row in section 2 names a license you read yourself, with a link and a date, and the redistribution duties match that license's text.

#### What you just did and why

The offline bundle copies the model onto the user's computer, which is redistribution, so the license applies to the team, not only to the user. Custom licenses (Llama, Gemma) add duties such as a notice file, an attribution line, or passing on a use policy; missing one is a license violation in a public project. Checking the primary source matters because search results and summaries mix up code licenses and model licenses.

#### Pull request checklist

- [ ] `ruff check .` prints `All checks passed!`
- [ ] `pytest -m "not integration" -q` passes on your laptop
- [ ] The pull request title has the form `type: summary (TASK-ID)` and the body says `Closes #<issue number>`
- [ ] No secrets, passwords, email addresses, personal data, or captures from a real network (CLAUDE.md rule 6)
- [ ] Any new dependency has a row in `docs/DEPENDENCIES.md` with its license
- [ ] CI is green and your reviewer approved
- [ ] Every license row has a primary-source link and a date

### ALI-02: Evaluation set: the same 13 questions for every model

**Due:** Week 2 (due Fri Oct 23) · **Milestone:** `W2 First end-to-end demo` · **Needs first:** [FIO-02](fiona.md#fio-02-tls-and-certificate-rules), [JAK-03](jakub.md#jak-03-cleartext-and-rdp-rules-the-rule-set-is-complete), [AMO-01](amory.md#amo-01-nist-sp-800-53-mapping-file-and-the-mapping-checks), [JAI-03](jaiden.md#jai-03-common-event-schema-the-normalizer-and-record-lookup) · **Kind:** code, tested

**Issue labels:** `type:task` `phase:alpha` `owner:ali` `area:ai`

#### Goal

Write `scripts/make_eval_set.py`, which turns the fixture logs into the evaluation set: one item per rule, holding the finding exactly as the pipeline gives it to the AI plus the raw log records it cites. Every model is then asked the same questions.

#### Prerequisites

FIO-02 and JAK-03 (rules), AMO-01 (mapping files) and JAI-03 (record lookup) are merged.

#### Steps

**Step 1.** Update `main` and create your branch for this task (one branch per task):

```bash
cd ~/projects/maxguard
source .venv/bin/activate
git checkout main && git pull
git checkout -b ali/eval-set
```

If `source .venv/bin/activate` fails, you have not made the virtual environment yet: do Week 0 section 0.11 first.

**Step 2.** Create `scripts/make_eval_set.py`:

```python
"""Build the AI evaluation set from the Zeek fixture logs (Ali).

One eval item = one finding, exactly as the pipeline hands it to the AI (rules
run, mapping files applied), plus the raw log records it cites, keyed by
record_id. scripts/benchmark_models.py asks every model about the same items,
so the models are compared on the same questions.

The output is deterministic: the same fixtures always give a byte-identical
eval_set.json. Run this again whenever a rule, a mapping file or a fixture
changes, and commit the new file (tests/unit/test_benchmark.py fails until you do).

Run from the repository root:
    python -m scripts.make_eval_set
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import maxguard.rules  # noqa: F401  (importing registers every rule)
from maxguard.events.lookup import records_for
from maxguard.mapping.loader import apply, load_all
from maxguard.models import Finding
from maxguard.rules.base import run_all

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURES_DIR = REPO_ROOT / "tests" / "fixtures" / "zeek"
MAPPINGS_DIR = REPO_ROOT / "mappings"
EVAL_SET_PATH = REPO_ROOT / "tests" / "fixtures" / "ai_eval" / "eval_set.json"
SCHEMA = "maxguard.eval_set/1"

# clean_tls13 is the "nothing wrong" capture: it has no finding to explain.
SKIPPED_FIXTURES = {"clean_tls13"}
# No lab capture contains RDP. This hand-made fixture is real Zeek 9.0.0 output
# (see its README), so adding it gives one item for every Fall 2026 rule.
EXTRA_FIXTURES = ["_handmade/rdp"]


def fixture_names(fixtures_dir: Path = FIXTURES_DIR) -> list[str]:
    """The lab capture folders (sorted, so the order never changes), then the extras.

    Folders starting with "_" hold hand-made extras; some are in Zeek's TSV
    format, which the rules cannot read directly, so only EXTRA_FIXTURES are used.
    """
    names = sorted(
        p.name
        for p in fixtures_dir.iterdir()
        if p.is_dir() and not p.name.startswith("_") and p.name not in SKIPPED_FIXTURES
    )
    return names + [name for name in EXTRA_FIXTURES if (fixtures_dir / name).is_dir()]


def findings_for(log_dir: Path, frameworks: list[dict]) -> list[Finding]:
    """Rules plus mappings, the same two steps maxguard.pipeline.analyze() does."""
    findings = run_all(log_dir)
    apply(findings, frameworks)
    return sorted(findings, key=lambda f: f.finding_id)  # a fixed order


def eval_item(fixture: str, finding: Finding, log_dir: Path) -> dict:
    """One finding plus its evidence records, in the shape explain() takes."""
    record_ids = {e.record_id for e in finding.evidence}
    # records_for() is what production uses: it re-hashes every record with
    # maxguard.ids.record_id and keeps the ones the finding cites.
    records = records_for(log_dir, record_ids)
    missing = record_ids - set(records)
    if missing:
        # The model would be asked about evidence it cannot see: stop loudly.
        raise ValueError(f"{fixture}: evidence records not found: {sorted(missing)}")
    return {
        "item_id": f"{fixture}/{finding.finding_id}",
        "fixture": fixture,
        "finding": finding.to_dict(),
        "records": records,
    }


def build_eval_set(fixtures_dir: Path = FIXTURES_DIR,
                   mappings_dir: Path = MAPPINGS_DIR) -> dict:
    """Every finding of every fixture, as eval items. Reads no clock: no "created at"."""
    frameworks = load_all(mappings_dir) if mappings_dir.is_dir() else []
    items = []
    for fixture in fixture_names(fixtures_dir):
        log_dir = fixtures_dir / fixture
        for finding in findings_for(log_dir, frameworks):
            items.append(eval_item(fixture, finding, log_dir))
    return {"schema": SCHEMA, "items": items}


def to_json(eval_set: dict) -> str:
    """Sorted keys and fixed indentation, so the file only changes when the data does."""
    return json.dumps(eval_set, indent=1, sort_keys=True) + "\n"


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Build the AI evaluation set.")
    parser.add_argument("--out", type=Path, default=EVAL_SET_PATH, help="where to write it")
    args = parser.parse_args(argv)

    eval_set = build_eval_set()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(to_json(eval_set))
    rule_ids = sorted({item["finding"]["rule_id"] for item in eval_set["items"]})
    print(f"wrote {len(eval_set['items'])} items ({len(rule_ids)} rules) to {args.out}")


if __name__ == "__main__":
    main()
```

**Step 3.** Build the set and commit the result `tests/fixtures/ai_eval/eval_set.json`:

```bash
python -m scripts.make_eval_set
```

Expected output:

```text
wrote 13 items (13 rules) to ~/projects/maxguard/tests/fixtures/ai_eval/eval_set.json
```

**Step 4.** Run it a second time and check that nothing changed (the file must be identical byte for byte):

```bash
cp tests/fixtures/ai_eval/eval_set.json /tmp/eval_set_1.json
python -m scripts.make_eval_set
cmp tests/fixtures/ai_eval/eval_set.json /tmp/eval_set_1.json && echo identical
```

Expected output:

```text
wrote 13 items (13 rules) to ~/projects/maxguard/tests/fixtures/ai_eval/eval_set.json
identical
```

**Step 5.** Commit, push, and open the pull request:

```bash
git add -A
git status          # only this task's files: nothing from .venv/, data/ or lab/captures/
git commit -m "feat: AI evaluation set built from the fixtures (ALI-02)"
git push -u origin HEAD
```

`HEAD` means "the branch I am on", so you do not have to retype its name. Open the repository on github.com: a yellow bar shows your branch with a **Compare & pull request** button. Click it, keep the title `feat: AI evaluation set built from the fixtures (ALI-02)`, fill in the template (paste the real output of the commands above under **How I tested it**), write `Closes #<issue number>` (this task's issue), and pick **@MeliorExi** under **Reviewers**. Click **Create pull request**, then fix anything CI or the reviewer finds with new commits on the same branch.

#### How to test

The script reports 13 items for 13 rules, and the second run prints `identical`.

#### What you just did and why

Comparing models only works if every model answers exactly the same questions with exactly the same evidence. Building the set from the same fixtures and the same code path as the real pipeline means the evaluation measures what users will see, and a deterministic file shows up in a pull request diff whenever a rule or mapping changes.

#### Pull request checklist

- [ ] `ruff check .` prints `All checks passed!`
- [ ] `pytest -m "not integration" -q` passes on your laptop
- [ ] The pull request title has the form `type: summary (TASK-ID)` and the body says `Closes #<issue number>`
- [ ] No secrets, passwords, email addresses, personal data, or captures from a real network (CLAUDE.md rule 6)
- [ ] Any new dependency has a row in `docs/DEPENDENCIES.md` with its license
- [ ] CI is green and your reviewer approved
- [ ] `tests/fixtures/ai_eval/eval_set.json` is committed

### ALI-03: Benchmark script: speed, citations, and unsupported details

**Due:** Week 3 (due Fri Oct 30) · **Milestone:** `W3 API and alert queue` · **Needs first:** [ALI-02](#ali-02-evaluation-set-the-same-13-questions-for-every-model), [JON-02](jonattan.md#jon-02-ollama-client-one-evidence-citing-explanation-per-finding) · **Kind:** code, tested

**Issue labels:** `type:task` `phase:alpha` `owner:ali` `area:ai`

#### Goal

Write `scripts/benchmark_models.py`: for each model, run the evaluation set through MaxGuard's own `explain()` twice and record per question the seconds taken, sentences kept and dropped by the citation check, "unsupported details" (an address, port, host name, TLS version or cipher that is not in the evidence), and whether run 2 gave the same answer as run 1.

#### Prerequisites

ALI-02 and JON-02 (the Ollama client) are merged.

#### Steps

**Step 1.** Update `main` and create your branch for this task (one branch per task):

```bash
cd ~/projects/maxguard
source .venv/bin/activate
git checkout main && git pull
git checkout -b ali/benchmark
```

If `source .venv/bin/activate` fails, you have not made the virtual environment yet: do Week 0 section 0.11 first.

**Step 2.** Create `scripts/benchmark_models.py`:

```python
"""Benchmark local Ollama models on the AI evaluation set (Ali).

For each model named on the command line, and for each run (--runs, default 2):
1. Reload the model. Ollama keeps recent prompts in a cache and answers a
   question it has seen before much faster, so without a fresh start the second
   run would look faster than real use. Loading time is printed, not scored.
2. Explain every eval item with MaxGuard's own explain() from
   maxguard.ai.ollama_client: same prompt, same JSON schema, temperature 0,
   seed 42, same citation check. We test what MaxGuard really runs.
Then the runs are compared: with temperature 0 and a fixed seed, run 2 should
give exactly the answers of run 1. Last, the model is unloaded so the next model
gets all the memory.

For every call it records the seconds taken, the sentences kept, the sentences
dropped by the citation check, and "unsupported details" (see find_details()).
Rows are appended to docs/model-eval/raw_results.csv and a summary per model is
printed. --tier only labels the rows ("pi" or "laptop"); it changes nothing else.

Run from the repository root, with Ollama running and the models pulled:
    python -m scripts.benchmark_models --tier pi qwen3:4b llama3.2:3b phi4-mini gemma3:4b
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import ipaddress
import json
import os
import re
import statistics
import time
from collections.abc import Callable, Iterator
from dataclasses import asdict
from pathlib import Path

import requests

from maxguard.ai.ollama_client import (
    CONNECT_TIMEOUT_SECONDS,
    READ_TIMEOUT_SECONDS,
    AIUnavailable,
    error_message,
    explain,
    ollama_url,
)
from maxguard.models import Sentence

REPO_ROOT = Path(__file__).resolve().parent.parent
EVAL_SET_PATH = REPO_ROOT / "tests" / "fixtures" / "ai_eval" / "eval_set.json"
RESULTS_PATH = REPO_ROOT / "docs" / "model-eval" / "raw_results.csv"
TIERS = ("pi", "laptop")

CSV_COLUMNS = [
    "tier", "model", "model_digest", "quantization", "ollama_version", "eval_set", "run",
    "item_id", "rule_id", "seconds", "sentences_kept", "sentences_dropped",
    "unsupported_count", "unsupported_details", "answer_hash", "same_as_run_1", "error", "text",
]

# The same signature as maxguard.ai.ollama_client.explain, so tests can pass a fake.
ExplainFn = Callable[[dict, dict], tuple[list[Sentence], int]]

# ---- unsupported details ----------------------------------------------------
# A detail is a fact the reader could act on: an address, a port, a host name,
# a TLS version or a cipher name. If the AI text mentions one that is not in the
# finding or its records, the model made it up (or brought it from its own
# memory). The regexes find candidates; a person reviews the flagged ones,
# because a regex cannot tell a wrong fact from harmless advice such as
# "use TLS 1.2 or newer".

# IPv4: four groups of 1-3 digits joined by dots, e.g. 172.18.0.2. \b (a word
# boundary) stops the match from starting or ending inside a longer number.
IPV4 = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")

# IPv6: groups of up to 4 hex digits joined by colons, e.g. fe80::1. "::"
# stands for any number of zero groups, so an exact regex would be huge.
# This one only finds candidates (a hex group, then 2 to 7 more ":group"
# parts); find_ips() lets Python's ipaddress module decide. Addresses that
# start with "::" (like ::1) are not found.
IPV6 = re.compile(r"\b[0-9a-f]{1,4}(?::[0-9a-f]{0,4}){2,7}", re.IGNORECASE)

# Ports only count when the text says they are ports: "port 23" / "ports 80",
# "172.18.0.2:4432" (address:port) and "23/tcp". A bare number could be a
# count or a byte size, so it is not checked.
PORT_PATTERNS = [
    re.compile(r"\bports?\s+(\d{1,5})\b", re.IGNORECASE),
    re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}:(\d{1,5})\b"),
    re.compile(r"\b(\d{1,5})/(?:tcp|udp)\b", re.IGNORECASE),
]

# Dot-separated labels ending in a label of 2+ letters: port4431.lab.invalid,
# example.com. A last label of digits (TLSv1.2, 4.0.1) or one letter (e.g.)
# does not match. Log file names like ssl.log match too; they are in every
# record's "_log" key, so they count as supported when the model cites them.
HOSTNAME = re.compile(r"\b(?:[a-z0-9-]+\.)+[a-z]{2,}\b", re.IGNORECASE)

# "TLSv10" (how Zeek writes it), "TLS 1.0", "TLSv1.0", "SSLv3". Groups: name,
# major digit, then the minor digit either after a dot or directly after major.
TLS_VERSION = re.compile(r"\b(SSL|TLS)\s?v?(\d)(?:\.(\d)|(\d))?\b", re.IGNORECASE)

# Cipher suite names are written in capitals, in two styles:
# - IANA/Zeek style, e.g. TLS_RSA_WITH_NULL_SHA256 or TLS_AES_128_GCM_SHA256
# - OpenSSL style, e.g. NULL-SHA256 or ECDHE-RSA-AES128-GCM-SHA256 (parts joined
#   by "-", ending in the MAC: SHA, SHA256, SHA384, MD5 or POLY1305).
# The check is literal: NULL-SHA256 is NOT matched to TLS_RSA_WITH_NULL_SHA256.
CIPHER_PATTERNS = [
    re.compile(r"\b(?:TLS|SSL)_[A-Z0-9_]+\b"),
    re.compile(r"\b[A-Z0-9]+(?:-[A-Z0-9]+)*-(?:SHA\d*|MD5|POLY1305)\b"),
]


def find_ips(text: str) -> set[str]:
    """IPv4 and IPv6 addresses in the text, in standard form (fe80:0::1 -> fe80::1)."""
    found = set()
    for candidate in IPV4.findall(text) + IPV6.findall(text):
        try:
            found.add(str(ipaddress.ip_address(candidate)))
        except ValueError:
            pass  # looks like an address but is not, e.g. 999.1.2.3, a MAC or a time
    return found


def tls_version_name(match: re.Match) -> str:
    """One spelling for every way of writing a version: TLSv10 -> "TLS 1.0"."""
    name, major, minor_after_dot, minor_no_dot = match.groups()
    minor = minor_after_dot or minor_no_dot or "0"  # "SSLv3" means SSL 3.0
    return f"{name.upper()} {major}.{minor}"


def find_details(text: str) -> dict[str, set[str]]:
    """Every checkable detail in a piece of text, grouped by kind."""
    ports = {str(int(m.group(1))) for p in PORT_PATTERNS for m in p.finditer(text)}
    return {
        "ip": find_ips(text),
        "port": ports,
        "host": {m.group(0).lower() for m in HOSTNAME.finditer(text)},
        "tls": {tls_version_name(m) for m in TLS_VERSION.finditer(text)},
        "cipher": {m.group(0) for p in CIPHER_PATTERNS for m in p.finditer(text)},
    }


def leaves(value: object, key: str = "") -> Iterator[tuple[str, object]]:
    """Yield (key, value) for every plain value inside nested dicts and lists."""
    if isinstance(value, dict):
        for k, v in value.items():
            yield from leaves(v, str(k))
    elif isinstance(value, list):
        for item in value:
            yield from leaves(item, key)
    else:
        yield key, value


def is_port_key(key: str) -> bool:
    # Zeek: id.orig_p, id.resp_p. Suricata: src_port, dest_port. Finding: dst_port.
    return key.endswith(("_p", "port"))


def known_details(finding: dict, records: dict[str, dict]) -> dict[str, set[str]]:
    """Every detail the model was shown: in the finding or in its records."""
    pairs = list(leaves(finding)) + list(leaves(records))
    known = find_details("\n".join(str(value) for _, value in pairs))
    # In the records a port is a number under a port key, not the words "port 23".
    known["port"] |= {str(value) for key, value in pairs
                      if is_port_key(key) and value is not None}
    return known


def is_supported(kind: str, value: str, known: dict[str, set[str]]) -> bool:
    if kind == "host":
        # "lab.invalid" is supported when "port4431.lab.invalid" is known.
        return any(name == value or name.endswith("." + value) for name in known["host"])
    return value in known[kind]


def unsupported_details(text: str, finding: dict, records: dict[str, dict]) -> list[str]:
    """Details in the text that the finding and its records do not contain,
    as sorted "kind:value" strings, e.g. ["ip:10.9.9.9", "port:443"]."""
    known = known_details(finding, records)
    found = find_details(text)
    return sorted(f"{kind}:{value}" for kind, values in found.items()
                  for value in values if not is_supported(kind, value, known))


# ---- talking to Ollama --------------------------------------------------------
# explain() does the real work; these small calls only describe and manage the
# models. Like explain(), they ignore proxy settings: Ollama is a local server.

def ollama_get(path: str) -> dict:
    """GET a small JSON document from Ollama, e.g. /api/version ({} if no answer)."""
    with requests.Session() as session:
        session.trust_env = False
        try:
            return session.get(f"{ollama_url()}{path}", timeout=CONNECT_TIMEOUT_SECONDS).json()
        except (requests.RequestException, ValueError):
            return {}


def ollama_version() -> str:
    """The Ollama version, e.g. "0.35.1"; "" if Ollama is not running."""
    return ollama_get("/api/version").get("version", "")


def installed_models() -> dict[str, dict]:
    """The pulled models (GET /api/tags), by name, e.g. {"qwen3:4b": {...}}."""
    return {m["name"]: m for m in ollama_get("/api/tags").get("models", [])}


def model_labels(model: str, installed: dict[str, dict]) -> dict[str, str]:
    """Digest and quantization of the pulled model. A tag such as qwen3:4b can
    point to a different build next month, so the digest says what was tested."""
    name = model if ":" in model else model + ":latest"  # Ollama's default tag
    info = installed.get(name, {})
    return {"model_digest": info.get("digest", "")[:12],
            "quantization": (info.get("details") or {}).get("quantization_level", "")}


def send_generate(body: dict) -> None:
    """POST /api/generate to Ollama. Raises AIUnavailable unless it answers 200."""
    with requests.Session() as session:
        session.trust_env = False
        try:
            response = session.post(f"{ollama_url()}/api/generate", json=body,
                                    timeout=(CONNECT_TIMEOUT_SECONDS, READ_TIMEOUT_SECONDS))
        except requests.RequestException as error:
            raise AIUnavailable(f"Ollama not reachable at {ollama_url()}: {error}") from error
    if response.status_code != 200:
        raise AIUnavailable(f"HTTP {response.status_code}: {error_message(response)}")


def load_model(model: str) -> None:
    """Load the model into memory: a generate request without a prompt.
    Raises AIUnavailable, e.g. "HTTP 404: model 'qwen3:4b' not found"."""
    send_generate({"model": model})


def unload_model(model: str) -> None:
    """Free the model's memory and empty its prompt cache (keep_alive 0)."""
    try:
        send_generate({"model": model, "keep_alive": 0})
    except AIUnavailable:
        pass  # e.g. never pulled: then it is not loaded either


# ---- running the models -------------------------------------------------------

def load_items(path: Path = EVAL_SET_PATH) -> list[dict]:
    return json.loads(path.read_text())["items"]


def eval_set_id(path: Path) -> str:
    """A short fingerprint of the eval set file. Results made with different
    versions of the questions must not be compared, and this column shows it."""
    return hashlib.sha256(path.read_bytes()).hexdigest()[:12]


def answer_hash(sentences: list[Sentence], dropped: int) -> str:
    """A short fingerprint of one answer, to compare runs (and machines)."""
    answer = {"sentences": [asdict(s) for s in sentences], "dropped": dropped}
    data = json.dumps(answer, sort_keys=True).encode("utf-8")
    return hashlib.sha256(data).hexdigest()[:12]


def explain_item(item: dict, explain_fn: ExplainFn, clock: Callable[[], float]) -> dict:
    """Ask about one eval item and measure the answer. Returns part of a CSV row."""
    row = {"item_id": item["item_id"], "rule_id": item["finding"]["rule_id"],
           "sentences_kept": 0, "sentences_dropped": 0, "unsupported_count": 0,
           "unsupported_details": "", "answer_hash": "", "error": "", "text": ""}
    start = clock()
    try:
        sentences, dropped = explain_fn(item["finding"], item["records"])
    except AIUnavailable as error:  # e.g. a read timeout: record it and go on
        row.update(seconds=round(clock() - start, 3), error=str(error))
        return row
    row["seconds"] = round(clock() - start, 3)

    # Only kept sentences reach the user, so only they are checked for made-up details.
    text = " ".join(s.text for s in sentences)
    unsupported = unsupported_details(text, item["finding"], item["records"])
    row.update(sentences_kept=len(sentences), sentences_dropped=dropped,
               unsupported_count=len(unsupported), unsupported_details="; ".join(unsupported),
               answer_hash=answer_hash(sentences, dropped), text=text)
    return row


def row_status(row: dict) -> str:
    """The progress line's end, e.g. "kept 2, dropped 1, unsupported 0"."""
    if row["error"]:
        return f"ERROR {row['error']}"
    return (f"kept {row['sentences_kept']}, dropped {row['sentences_dropped']}, "
            f"unsupported {row['unsupported_count']}")


def mark_repeats(rows: list[dict]) -> None:
    """Set same_as_run_1 to "yes"/"no" on runs 2+ ("" on run 1 and on errors)."""
    first = {r["item_id"]: r["answer_hash"] for r in rows if r["run"] == 1}
    for row in rows:
        earlier = first.get(row["item_id"], "")
        if row["run"] == 1 or not row["answer_hash"] or not earlier:
            row["same_as_run_1"] = ""
        else:
            row["same_as_run_1"] = "yes" if row["answer_hash"] == earlier else "no"


def benchmark_model(model: str, items: list[dict], *, tier: str, runs: int,
                    explain_fn: ExplainFn, labels: dict[str, str] | None = None,
                    clock: Callable[[], float] = time.perf_counter) -> list[dict]:
    """All runs of one model over all items. Returns [] if the model cannot be loaded."""
    # Production explain() reads the model name from this variable on every call.
    os.environ["MAXGUARD_MODEL"] = model
    rows = []
    for run in range(1, runs + 1):
        unload_model(model)  # empty the prompt cache, so every run starts the same way
        start = clock()
        try:
            load_model(model)
        except AIUnavailable as error:
            print(f"{model}: cannot load it ({error}), skipping its remaining runs", flush=True)
            break
        print(f"{model} run {run}: loaded in {clock() - start:.1f} s (not scored)", flush=True)

        for number, item in enumerate(items, start=1):
            row = explain_item(item, explain_fn, clock)
            row.update({"tier": tier, "model": model, "run": run, **(labels or {})})
            rows.append(row)
            print(f"{model} run {run} item {number}/{len(items)} {row['item_id']}: "
                  f"{row['seconds']:.1f} s, {row_status(row)}", flush=True)
    unload_model(model)  # give the next model all the memory
    mark_repeats(rows)
    return rows


# ---- results ------------------------------------------------------------------

def summarize(rows: list[dict]) -> dict:
    """One model's numbers. Seconds and drop rate use every run. "explained" and
    the unsupported count use run 1 only, so repeating a run does not double them."""
    answered = [r for r in rows if not r["error"]]
    run_1 = [r for r in rows if r["run"] == 1]
    seconds = [r["seconds"] for r in answered]
    kept = sum(r["sentences_kept"] for r in answered)
    dropped = sum(r["sentences_dropped"] for r in answered)
    repeats = [r for r in rows if r["same_as_run_1"]]
    identical = sum(r["same_as_run_1"] == "yes" for r in repeats)
    return {
        "model": rows[0]["model"],
        "tier": rows[0]["tier"],
        "calls": len(answered),
        "errors": len(rows) - len(answered),
        "median_seconds": statistics.median(seconds) if seconds else None,
        # An answer with no kept sentence explains nothing, even when nothing was
        # dropped (e.g. the JSON was cut off), so the drop rate alone can look too good.
        "explained": f"{sum(r['sentences_kept'] > 0 for r in run_1)}/{len(run_1)}",
        "drop_rate": dropped / (kept + dropped) if kept + dropped else 0.0,
        "unsupported_run_1": sum(r["unsupported_count"] for r in run_1),
        "identical": f"{identical}/{len(repeats)}" if repeats else "-",  # "-": --runs 1
    }


def print_summary(summaries: list[dict]) -> None:
    # The model column is as wide as the longest name (tags can be 30 characters long).
    width = max([len("model")] + [len(s["model"]) for s in summaries]) + 2
    print(f"\n{'model':<{width}}{'tier':<8}{'calls':>6}{'errors':>7}{'median_s':>10}"
          f"{'explained':>10}{'drop_rate':>11}{'unsupported(run 1)':>20}{'identical':>11}")
    for s in summaries:
        median = "-" if s["median_seconds"] is None else f"{s['median_seconds']:.1f}"
        print(f"{s['model']:<{width}}{s['tier']:<8}{s['calls']:>6}{s['errors']:>7}"
              f"{median:>10}{s['explained']:>10}{s['drop_rate']:>11.1%}"
              f"{s['unsupported_run_1']:>20}{s['identical']:>11}")


def append_csv(path: Path, rows: list[dict]) -> None:
    """Add rows to the CSV, so the Pi run and the laptop run end up in one file.
    Delete the file to start a fresh evaluation."""
    path.parent.mkdir(parents=True, exist_ok=True)
    is_new = not path.exists() or path.stat().st_size == 0
    if not is_new:
        with path.open(newline="") as f:
            header = next(csv.reader(f), [])
        if header != CSV_COLUMNS:
            # Mixing two column layouts would silently shift values into the wrong columns.
            raise SystemExit(f"{path} has other columns; move it away and run again")
    with path.open("a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        if is_new:
            writer.writeheader()
        writer.writerows(rows)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Benchmark Ollama models on the eval set.")
    parser.add_argument("models", nargs="+", help="Ollama model tags, e.g. qwen3:4b")
    parser.add_argument("--tier", required=True, choices=TIERS,
                        help="hardware class of this machine (only labels the results)")
    parser.add_argument("--runs", type=int, default=2,
                        help="passes over the eval set; 2+ checks that answers repeat")
    parser.add_argument("--eval-set", type=Path, default=EVAL_SET_PATH)
    parser.add_argument("--out", type=Path, default=RESULTS_PATH)
    args = parser.parse_args(argv)
    if args.runs < 1:
        parser.error("--runs must be at least 1")
    return args


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    items = load_items(args.eval_set)
    if not items:
        raise SystemExit(f"{args.eval_set} has no items; run: python -m scripts.make_eval_set")
    version = ollama_version()
    if not version:
        raise SystemExit(f"no Ollama answering at {ollama_url()}: start it first")
    labels = {"ollama_version": version, "eval_set": eval_set_id(args.eval_set)}
    installed = installed_models()
    print(f"{len(items)} eval items (eval set {labels['eval_set']}), Ollama {version} "
          f"at {ollama_url()}, tier {args.tier}", flush=True)

    summaries = []
    for model in args.models:
        rows = benchmark_model(model, items, tier=args.tier, runs=args.runs, explain_fn=explain,
                               labels={**labels, **model_labels(model, installed)})
        if rows:
            append_csv(args.out, rows)
            summaries.append(summarize(rows))
    if not summaries:
        raise SystemExit("no model could be loaded, so nothing was written")
    print_summary(summaries)
    print(f"\nraw results appended to {args.out}")


if __name__ == "__main__":
    main()
```

**Step 3.** Create the tests `tests/unit/test_benchmark.py`. They replace the model with a fake `explain()`, so no Ollama is needed:

```python
"""Tests for the model evaluation scripts (scripts/make_eval_set.py and
scripts/benchmark_models.py). No model and no network: a fake explain()
stands in for Ollama, and a fake clock makes the timings exact."""

import csv

import pytest

from maxguard.ai.ollama_client import AIUnavailable
from maxguard.models import Sentence
from scripts import benchmark_models as bench
from scripts import make_eval_set

FALL_2026_RULES = {
    "cleartext.ftp", "cleartext.telnet", "cleartext.http", "cleartext.http_alt",
    "cleartext.pop3", "cleartext.imap", "rdp.standard_security", "tls.weak_version",
    "tls.weak_cipher", "cert.expired", "cert.self_signed", "cert.weak_key",
    "cert.sha1_signature",
}


@pytest.fixture(autouse=True)
def ollama_calls(monkeypatch) -> list[tuple[str, str]]:
    """No test talks to Ollama: loading and unloading a model only record the call.
    benchmark_model() sets MAXGUARD_MODEL; monkeypatch puts the old value back."""
    calls = []
    monkeypatch.setattr(bench, "load_model", lambda model: calls.append(("load", model)))
    monkeypatch.setattr(bench, "unload_model", lambda model: calls.append(("unload", model)))
    monkeypatch.delenv("MAXGUARD_MODEL", raising=False)
    return calls


@pytest.fixture(scope="module")
def items() -> list[dict]:
    return bench.load_items()


def item_for(items: list[dict], rule_id: str) -> dict:
    return next(i for i in items if i["finding"]["rule_id"] == rule_id)


class FakeClock:
    """Each call returns 2 seconds more than the last one, so every timed call
    (one reading before, one after) takes exactly 2.0 seconds."""

    def __init__(self):
        self.now = 0.0

    def __call__(self) -> float:
        self.now += 2.0
        return self.now


def citing_explain(finding: dict, records: dict) -> tuple[list[Sentence], int]:
    """A well-behaved fake model: one sentence citing the first record, one dropped."""
    first_id = min(records)
    text = f"Traffic went to {finding['dst_ip']} port {finding['dst_port']}."
    return [Sentence(text, [first_id])], 1


# ---- the eval set -----------------------------------------------------------

def test_committed_eval_set_is_up_to_date():
    fresh = make_eval_set.to_json(make_eval_set.build_eval_set())
    assert fresh == make_eval_set.EVAL_SET_PATH.read_text(), (
        "a rule, mapping or fixture changed: run python -m scripts.make_eval_set and commit")


def test_eval_set_has_one_item_per_fall_rule(items):
    assert sorted(i["finding"]["rule_id"] for i in items) == sorted(FALL_2026_RULES)


def test_every_item_carries_the_records_it_cites(items):
    for item in items:
        cited = {e["record_id"] for e in item["finding"]["evidence"]}
        assert cited == set(item["records"]), item["item_id"]
        assert all("_log" in rec for rec in item["records"].values())


def test_clean_capture_is_not_in_the_eval_set():
    assert "clean_tls13" not in make_eval_set.fixture_names()


# ---- finding details in text ------------------------------------------------

@pytest.mark.parametrize("text, kind, expected", [
    ("from 172.18.0.3 to 172.18.0.2.", "ip", {"172.18.0.3", "172.18.0.2"}),
    ("fe80::1 and 2001:DB8:0:0::8a2e:370:7334", "ip", {"fe80::1", "2001:db8::8a2e:370:7334"}),
    ("MAC 02:00:00:aa:bb:cc at 10:30:00, 999.1.2.3", "ip", set()),  # not addresses
    ("Telnet on port 23 and ports 80", "port", {"23", "80"}),
    ("connect to 172.18.0.2:4432 or 23/tcp", "port", {"4432", "23"}),
    ("the host port4431.lab.invalid sent 23 packets", "port", set()),  # no "port N"
    ("Zeek says TLSv10, people say TLS 1.0", "tls", {"TLS 1.0"}),
    ("TLSv1.2 or tls1.3 or SSLv3", "tls", {"TLS 1.2", "TLS 1.3", "SSL 3.0"}),
    ("DTLS 1.2 is a different protocol", "tls", set()),
    ("TLS_RSA_WITH_NULL_SHA256 alias NULL-SHA256", "cipher",
     {"TLS_RSA_WITH_NULL_SHA256", "NULL-SHA256"}),
    ("signed with SHA-1", "cipher", set()),
    ("certificate for weak.lab.invalid", "host", {"weak.lab.invalid"}),
    ("e.g. TLSv1.2, OpenSSL 3.0.22 and PCI DSS 4.0.1", "host", set()),
])
def test_find_details(text, kind, expected):
    assert bench.find_details(text)[kind] == expected


def test_details_from_the_finding_and_records_are_supported(items):
    item = item_for(items, "tls.weak_version")
    text = ("The client 172.18.0.3 used TLS 1.0 (TLSv10) to reach "
            "port4431.lab.invalid on port 4431, a name under lab.invalid.")
    assert bench.unsupported_details(text, item["finding"], item["records"]) == []


def test_made_up_details_are_flagged(items):
    item = item_for(items, "tls.weak_version")
    text = ("Host 10.9.9.9 on port 443 used TLS 1.3 with TLS_AES_128_GCM_SHA256 "
            "at evil.example.com.")
    assert bench.unsupported_details(text, item["finding"], item["records"]) == [
        "cipher:TLS_AES_128_GCM_SHA256", "host:evil.example.com", "ip:10.9.9.9",
        "port:443", "tls:TLS 1.3",
    ]


def test_ports_from_record_fields_count_as_known(items):
    item = item_for(items, "cleartext.ftp")
    known = bench.known_details(item["finding"], item["records"])
    client_port = str(next(iter(item["records"].values()))["id.orig_p"])
    assert {"21", client_port} <= known["port"]


# ---- running models (fake explain) -------------------------------------------

def test_every_run_starts_with_a_freshly_loaded_model(items, ollama_calls):
    models_asked = []

    def fake_explain(finding, records):
        models_asked.append(bench.os.environ["MAXGUARD_MODEL"])
        return citing_explain(finding, records)

    rows = bench.benchmark_model("fake:1b", items, tier="pi", runs=2,
                                 explain_fn=fake_explain, clock=FakeClock())
    # Unloading empties Ollama's prompt cache, so run 2 is not faster than real use.
    assert ollama_calls == [("unload", "fake:1b"), ("load", "fake:1b")] * 2 + [
        ("unload", "fake:1b")]  # the last unload frees the memory for the next model
    assert set(models_asked) == {"fake:1b"}  # production explain() reads this variable
    assert len(models_asked) == len(rows) == 2 * len(items)
    first = rows[0]
    assert (first["tier"], first["model"], first["run"]) == ("pi", "fake:1b", 1)
    assert first["seconds"] == 2.0
    assert (first["sentences_kept"], first["sentences_dropped"]) == (1, 1)
    assert first["unsupported_count"] == 0
    assert [r["same_as_run_1"] for r in rows] == [""] * len(items) + ["yes"] * len(items)


def test_answers_that_change_between_runs_are_reported(items):
    counter = iter(range(1000))

    def changing_explain(finding, records):
        return [Sentence(f"Answer number {next(counter)}.", [min(records)])], 0

    rows = bench.benchmark_model("fake:1b", items[:2], tier="laptop", runs=2,
                                 explain_fn=changing_explain, clock=FakeClock())
    assert [r["same_as_run_1"] for r in rows] == ["", "", "no", "no"]


def test_model_that_cannot_load_is_skipped(items, monkeypatch):
    def not_pulled(model):
        raise AIUnavailable(f"HTTP 404: model '{model}' not found")

    monkeypatch.setattr(bench, "load_model", not_pulled)
    assert bench.benchmark_model("fake:1b", items, tier="pi", runs=2,
                                 explain_fn=citing_explain, clock=FakeClock()) == []


def test_one_failed_call_is_recorded_and_the_run_goes_on(items, capsys):
    answers = [citing_explain, None, citing_explain]

    def flaky_explain(finding, records):
        answer = answers.pop(0)
        if answer is None:
            raise AIUnavailable("read timed out")
        return answer(finding, records)

    rows = bench.benchmark_model("fake:1b", items[:3], tier="pi", runs=1,
                                 explain_fn=flaky_explain, clock=FakeClock())
    assert [r["error"] for r in rows] == ["", "read timed out", ""]
    assert rows[1]["answer_hash"] == ""
    printed = capsys.readouterr().out.splitlines()  # line 0 says the model was loaded
    assert printed[2].endswith("item 2/3 " + rows[1]["item_id"] + ": 2.0 s, ERROR read timed out")


# ---- summary and CSV ---------------------------------------------------------

def make_row(run, seconds, kept, dropped, unsupported, same="", error=""):
    return {"model": "m", "tier": "pi", "run": run, "seconds": seconds,
            "sentences_kept": kept, "sentences_dropped": dropped,
            "unsupported_count": unsupported, "same_as_run_1": same, "error": error}


def test_summary_numbers():
    rows = [
        make_row(1, 10.0, 3, 1, 2),
        make_row(1, 30.0, 0, 0, 0),  # valid but empty answer: explains nothing
        make_row(1, 99.0, 0, 0, 0, error="read timed out"),
        make_row(2, 20.0, 3, 1, 2, same="yes"),
    ]
    summary = bench.summarize(rows)
    assert summary["calls"] == 3 and summary["errors"] == 1
    assert summary["median_seconds"] == 20.0  # errors are not timed
    assert summary["explained"] == "1/3"  # of the run 1 items
    assert summary["drop_rate"] == pytest.approx(2 / 8)  # 2 dropped of 8 sentences
    assert summary["unsupported_run_1"] == 2  # run 2 repeats run 1, so it is not added
    assert summary["identical"] == "1/1"


def test_summary_table_fits_long_model_names(capsys):
    rows = [make_row(1, 12.0, 2, 0, 0)]
    rows[0]["model"] = "qwen3:4b-instruct-2507-q4_K_M"
    bench.print_summary([bench.summarize(rows)])
    assert "qwen3:4b-instruct-2507-q4_K_M  pi " in capsys.readouterr().out


def test_csv_header_is_written_once(tmp_path, items):
    rows = bench.benchmark_model("fake:1b", items[:1], tier="pi", runs=1,
                                 explain_fn=citing_explain, clock=FakeClock())
    out = tmp_path / "raw_results.csv"
    bench.append_csv(out, rows)
    bench.append_csv(out, rows)
    with out.open(newline="") as f:
        lines = list(csv.reader(f))
    assert lines[0] == bench.CSV_COLUMNS
    assert len(lines) == 3


def test_csv_with_other_columns_is_not_appended_to(tmp_path):
    out = tmp_path / "raw_results.csv"
    out.write_text("model,seconds\n")
    with pytest.raises(SystemExit, match="other columns"):
        bench.append_csv(out, [])


def test_tier_must_be_pi_or_laptop(capsys):
    with pytest.raises(SystemExit):
        bench.parse_args(["--tier", "server", "qwen3:4b"])
    assert "invalid choice" in capsys.readouterr().err


@pytest.fixture
def fake_ollama(monkeypatch):
    """main() with a fake Ollama 0.35.1 that has one model pulled."""
    monkeypatch.setattr(bench, "explain", citing_explain)
    monkeypatch.setattr(bench, "ollama_version", lambda: "0.35.1")
    monkeypatch.setattr(bench, "installed_models", lambda: {
        "fake:1b": {"digest": "0123456789abcdef", "details": {"quantization_level": "Q4_K_M"}}})


def test_main_writes_csv_and_summary(tmp_path, fake_ollama, capsys):
    out = tmp_path / "raw_results.csv"

    bench.main(["--tier", "laptop", "--out", str(out), "fake:1b"])

    with out.open(newline="") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 2 * len(FALL_2026_RULES)
    assert rows[0]["model_digest"] == "0123456789ab"
    assert rows[0]["quantization"] == "Q4_K_M"
    assert rows[0]["ollama_version"] == "0.35.1"
    assert rows[0]["eval_set"] == bench.eval_set_id(bench.EVAL_SET_PATH)
    printed = capsys.readouterr().out
    assert "fake:1b" in printed and "13/13" in printed


def test_main_stops_when_ollama_is_not_running(tmp_path, monkeypatch):
    monkeypatch.setattr(bench, "ollama_version", lambda: "")
    with pytest.raises(SystemExit, match="no Ollama answering"):
        bench.main(["--tier", "pi", "--out", str(tmp_path / "r.csv"), "fake:1b"])


def test_main_writes_nothing_when_no_model_loads(tmp_path, fake_ollama, monkeypatch):
    def not_pulled(model):
        raise AIUnavailable(f"HTTP 404: model '{model}' not found")

    monkeypatch.setattr(bench, "load_model", not_pulled)
    out = tmp_path / "raw_results.csv"
    with pytest.raises(SystemExit, match="nothing was written"):
        bench.main(["--tier", "pi", "--out", str(out), "missing:1b"])
    assert not out.exists()
```

**Step 4.** Run them:

```bash
pytest tests/unit/test_benchmark.py -q
```

Expected output:

```text
................................                                                             [100%]
32 passed in 0.25s
```

**Step 5.** Check the error path without Ollama running (the address points at a closed port):

```bash
OLLAMA_HOST=http://127.0.0.1:1 python -m scripts.benchmark_models --tier laptop qwen3:4b
```

Expected output:

```text
no Ollama answering at http://127.0.0.1:1: start it first
```

**Step 6.** Commit, push, and open the pull request:

```bash
git add -A
git status          # only this task's files: nothing from .venv/, data/ or lab/captures/
git commit -m "feat: model benchmark on the evaluation set (ALI-03)"
git push -u origin HEAD
```

`HEAD` means "the branch I am on", so you do not have to retype its name. Open the repository on github.com: a yellow bar shows your branch with a **Compare & pull request** button. Click it, keep the title `feat: model benchmark on the evaluation set (ALI-03)`, fill in the template (paste the real output of the commands above under **How I tested it**), write `Closes #<issue number>` (this task's issue), and pick **@MeliorExi** under **Reviewers**. Click **Create pull request**, then fix anything CI or the reviewer finds with new commits on the same branch.

#### How to test

`pytest` passes, and without Ollama the script stops with a clear message and exit code 1 instead of a traceback.

#### What you just did and why

Speed alone picks the wrong model: a fast model that invents details is worse than useless in a security tool. The citation check catches made-up record IDs, and the unsupported-detail check catches made-up facts *inside* a sentence that cites real records. Running twice checks that temperature 0 and a fixed seed really give repeatable answers on your hardware.

#### Pull request checklist

- [ ] `ruff check .` prints `All checks passed!`
- [ ] `pytest -m "not integration" -q` passes on your laptop
- [ ] The pull request title has the form `type: summary (TASK-ID)` and the body says `Closes #<issue number>`
- [ ] No secrets, passwords, email addresses, personal data, or captures from a real network (CLAUDE.md rule 6)
- [ ] Any new dependency has a row in `docs/DEPENDENCIES.md` with its license
- [ ] CI is green and your reviewer approved

### ALI-04: Run the benchmark on both tiers and propose the default models

**Due:** Week 4 (due Fri Nov 6) · **Milestone:** `W4 Full offline report` · **Needs first:** [ALI-01](#ali-01-model-shortlist-and-license-check), [ALI-03](#ali-03-benchmark-script-speed-citations-and-unsupported-details) · **Kind:** process

**Issue labels:** `type:task` `phase:alpha` `owner:ali` `area:ai` `critical-path` `needs-hardware`

> **Needs hardware.** Steps that use the Raspberry Pi, the switch or other devices were not run during planning; they are marked *not run — verify on hardware*.

#### Goal

Run the benchmark on a Pi-class machine (models of 4B parameters or fewer) and on a laptop (8B or fewer), review the answers by hand, and propose one default model per tier. The choice replaces `TEMPORARY_DEFAULT_MODEL` in `maxguard/ai/ollama_client.py` and goes into the offline bundle (JON-05).

#### Prerequisites

ALI-01 and ALI-03 are merged; Ollama 0.35.1 is installed on both machines.

#### Steps

**Step 1.** Update `main` and create your branch for this task (one branch per task):

```bash
cd ~/projects/maxguard
source .venv/bin/activate
git checkout main && git pull
git checkout -b ali/model-results
```

If `source .venv/bin/activate` fails, you have not made the virtual environment yet: do Week 0 section 0.11 first.

**Step 2.** Pull the shortlisted models on each machine (`ollama pull <tag>`), then follow sections 5.1 and 5.2 of `docs/model-eval/README.md` to run, for example:

```bash
python -m scripts.benchmark_models --tier pi qwen3:4b llama3.2:3b phi4-mini gemma3:4b
```

*Not run in planning (no model could be downloaded); verify on hardware.*

**Step 3.** Fill in section 6 (results per tier) from `docs/model-eval/raw_results.csv`, then the human review: read every kept sentence of the two best models and mark any that is wrong even though it cites real records.

**Step 4.** Write section 7: your proposal for each tier, with the reasons (grounding first, then license, then speed). Changing the default model updates `docs/PROJECT_DECISIONS.md`, so Ahmad (Security Lead) approves the pull request.

**Step 5.** In the same pull request, set `TEMPORARY_DEFAULT_MODEL` to the laptop-tier choice and rename it `DEFAULT_MODEL` (Jonattan reviews that change).

**Step 6.** Commit, push, and open the pull request:

```bash
git add -A
git status          # only this task's files: nothing from .venv/, data/ or lab/captures/
git commit -m "docs: model evaluation results and default models (ALI-04)"
git push -u origin HEAD
```

`HEAD` means "the branch I am on", so you do not have to retype its name. Open the repository on github.com: a yellow bar shows your branch with a **Compare & pull request** button. Click it, keep the title `docs: model evaluation results and default models (ALI-04)`, fill in the template (paste the real output of the commands above under **How I tested it**), write `Closes #<issue number>` (this task's issue), and pick **@MeliorExi** under **Reviewers**. Click **Create pull request**, then fix anything CI or the reviewer finds with new commits on the same branch.

#### How to test

Section 6 has real numbers for both tiers, every proposed model passed the license gate in section 2, and the unit tests still pass after the constant changes.

#### What you just did and why

The model is the one part of MaxGuard that can be confidently wrong. Measuring dropped sentences and unsupported details on the same questions, and then reading the answers yourself, is how the team picks a model it can defend in the final presentation.

#### Pull request checklist

- [ ] `ruff check .` prints `All checks passed!`
- [ ] `pytest -m "not integration" -q` passes on your laptop
- [ ] The pull request title has the form `type: summary (TASK-ID)` and the body says `Closes #<issue number>`
- [ ] No secrets, passwords, email addresses, personal data, or captures from a real network (CLAUDE.md rule 6)
- [ ] Any new dependency has a row in `docs/DEPENDENCIES.md` with its license
- [ ] CI is green and your reviewer approved
- [ ] Ahmad approved the choice
- [ ] `raw_results.csv` is committed

## Spring 2027: v2.0

### ALI-05: Re-evaluate the models against prompt injection and the spring rules

**Due:** Spring S5-S8 (due Fri Mar 12, 2027) · **Milestone:** `S5-S8 Respond` · **Needs first:** [ALI-04](#ali-04-run-the-benchmark-on-both-tiers-and-propose-the-default-models), [JON-06](jonattan.md#jon-06-prompt-injection-tests-for-the-ai-layer) · **Kind:** process

**Issue labels:** `type:task` `phase:spring` `owner:ali` `area:ai` `needs-hardware`

> **Needs hardware.** Steps that use the Raspberry Pi, the switch or other devices were not run during planning; they are marked *not run — verify on hardware*.

#### Goal

Run the evaluation again on both tiers with Jonattan's prompt-injection set and the spring rules (JA4 watchlist, decoys, baselines), and confirm or change the default models before the v2.0 feature freeze.

#### Prerequisites

ALI-04 and JON-06 are merged; the spring rules you evaluate are merged.

#### Steps

**Step 1.** Update `main` and create your branch for this task (one branch per task):

```bash
cd ~/projects/maxguard
source .venv/bin/activate
git checkout main && git pull
git checkout -b ali/eval-spring
```

If `source .venv/bin/activate` fails, you have not made the virtual environment yet: do Week 0 section 0.11 first.

**Step 2.** Regenerate the evaluation set once the spring rules and their fixtures are merged (`python -m scripts.make_eval_set`), so it has one item per rule, and commit it (`tests/unit/test_benchmark.py` checks it is up to date).

**Step 3.** On each tier, run the benchmark on both sets, then count how often each model obeyed the hostile text:

```bash
python -m scripts.benchmark_models --tier pi qwen3:4b llama3.2:3b
python -m scripts.benchmark_models --tier pi --eval-set tests/fixtures/ai_eval/injection/injection_set.json qwen3:4b llama3.2:3b
python -m scripts.injection_report docs/model-eval/raw_results.csv
```

"Obeyed" means the canary word reached a sentence MaxGuard kept. The citation check cannot catch those sentences when they cite the hostile record itself (JON-06 explains why), so this rate is a real difference between models. *Not run in planning (no model could be downloaded); verify on hardware.*

**Step 4.** Add a section 10 to `docs/model-eval/README.md`: the new results per tier, the injection rate per model, and whether the default models stay. A change of default model needs Ahmad's approval, as in ALI-04.

**Step 5.** Commit, push, and open the pull request:

```bash
git add -A
git status          # only this task's files: nothing from .venv/, data/ or lab/captures/
git commit -m "docs: spring model re-evaluation (ALI-05)"
git push -u origin HEAD
```

`HEAD` means "the branch I am on", so you do not have to retype its name. Open the repository on github.com: a yellow bar shows your branch with a **Compare & pull request** button. Click it, keep the title `docs: spring model re-evaluation (ALI-05)`, fill in the template (paste the real output of the commands above under **How I tested it**), write `Closes #<issue number>` (this task's issue), and pick **@MeliorExi** under **Reviewers**. Click **Create pull request**, then fix anything CI or the reviewer finds with new commits on the same branch.

#### How to test

The new results cover every spring rule and the injection set on both tiers.

#### What you just did and why

New rules mean new kinds of evidence (fingerprints, decoy contacts, baselines) that the model has never been tested on, and newer model versions appear every few months. A model that often obeys text from the network is a bad default even if its other numbers are good. A second evaluation before the feature freeze keeps the choice honest.

#### Pull request checklist

- [ ] `ruff check .` prints `All checks passed!`
- [ ] `pytest -m "not integration" -q` passes on your laptop
- [ ] The pull request title has the form `type: summary (TASK-ID)` and the body says `Closes #<issue number>`
- [ ] No secrets, passwords, email addresses, personal data, or captures from a real network (CLAUDE.md rule 6)
- [ ] Any new dependency has a row in `docs/DEPENDENCIES.md` with its license
- [ ] CI is green and your reviewer approved
- [ ] Ahmad approved any change of default model
