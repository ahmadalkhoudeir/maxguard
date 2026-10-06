# Karthik: Test and CI Engineer

**Karthik Nair** (@Karthiknair91) · Module: Testing · Reviewer for your pull requests: @JWinborne1 (Jaiden) · Ask first when stuck: Jaiden

This is your part of the MaxGuard v2.0 roadmap. Read [the roadmap overview](README.md) once, then work top to bottom: Week 0 first, then your tasks in order. Each task's ID is also the start of its GitHub issue's title.

## Your tasks

| Task | Due | Title | Needs first | Kind |
|---|---|---|---|---|
| [KAR-00](#week-0--onboarding-due-friday-october-9-2026) | W0 | Week 0 onboarding (Karthik) | — | process |
| [KAR-01](#kar-01-traffic-lab-and-the-14-test-captures) | W0 | Traffic lab and the 14 test captures | — | code, tested |
| [KAR-02](#kar-02-test-fixtures-zeek-and-suricata-output-for-every-capture) | W1 | Test fixtures: Zeek and Suricata output for every capture | [KAR-01](#kar-01-traffic-lab-and-the-14-test-captures), [JAK-01](jakub.md#jak-01-maxguards-zeek-scripts-cleartext-sessions-and-asset-tracking), [JAK-02](jakub.md#jak-02-suricata-configuration-community-id-and-ja4), [JAI-01](jaiden.md#jai-01-restructure-the-repository-add-packaging-and-ci) | code, tested |
| [KAR-03](#kar-03-integration-tests-the-real-pipeline-on-every-capture) | W2 | Integration tests: the real pipeline on every capture | [JAI-05](jaiden.md#jai-05-the-pipeline-one-function-from-input-to-report), [JAI-04](jaiden.md#jai-04-the-engine-image-and-the-compose-files), [KAR-02](#kar-02-test-fixtures-zeek-and-suricata-output-for-every-capture) | code, tested |
| [KAR-04](#kar-04-ci-runs-the-integration-tests-plus-a-determinism-test) | W3 | CI runs the integration tests, plus a determinism test | [KAR-03](#kar-03-integration-tests-the-real-pipeline-on-every-capture) | code, written |
| [KAR-05](#kar-05-release-candidate-test-with-an-outside-tester) | W6 | Release-candidate test with an outside tester | [JAI-09](jaiden.md#jai-09-release-workflow-and-v20-alpha-rc1), [JON-05](jonattan.md#jon-05-offline-bundle-install-maxguard-on-a-machine-with-no-internet) | process |
| [KAR-06](#kar-06-end-to-end-test-of-the-live-sensor-on-the-lab) | S4 | End-to-end test of the live sensor on the lab | [JAK-07](jakub.md#jak-07-live-sensor-capture-rotation-and-shipping-to-the-console) | code, tested |

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
git config --global user.name "Karthik Nair"
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
git checkout -b karthik/week0-team-row
```

2. **Make the change.** Run `code .`, open `docs/TEAM.md`, and add this line at
   the end (keep the `|` characters):

```markdown
| Karthik Nair | Test and CI Engineer | Karthiknair91 | Testing |
```

3. **Commit** (the message says *what changed*, starting with a type such as
   `docs:`, `feat:`, `fix:` or `test:`; see `docs/CONTRIBUTING.md`):

```bash
git add docs/TEAM.md
git commit -m "docs: add Karthik to TEAM.md"
```

4. **Push** your branch to GitHub:

```bash
git push -u origin karthik/week0-team-row
```

Expected (from the planning simulation; the first lines differ on GitHub):

```text
 * [new branch]      karthik/week0-team-row -> karthik/week0-team-row
branch 'karthik/week0-team-row' set up to track 'origin/karthik/week0-team-row'.
```

5. **Open the pull request** and ask for a review:

```bash
gh pr create --base main --title "docs: add Karthik to TEAM.md" --body "Week 0 onboarding." --reviewer JWinborne1
```

`gh` prints the pull request's web address. (You can also click the link Git
printed after the push and press **Create pull request**.)

6. **After approval**, click **Squash and merge** on GitHub, then update your laptop:

```bash
git checkout main && git pull
git branch -d karthik/week0-team-row
```

**If GitHub says "This branch has conflicts":** eight people are adding a line
to the same file this week, so this is expected. Bring `main` into your branch
and keep both lines:

```bash
git checkout main && git pull
git checkout karthik/week0-team-row
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
   `KAR-01: pytest cannot import maxguard`). In the body, paste the
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

### KAR-01: Traffic lab and the 14 test captures

**Due:** Week 0 (due Fri Oct 9, 2026) · **Milestone:** `W0 Onboarding and contracts` · **Needs first:** none · **Kind:** code, tested

**Issue labels:** `type:task` `phase:alpha` `owner:karthik` `area:testing` `critical-path`

#### Goal

Build MaxGuard's traffic lab: insecure test services and a client on an isolated Docker network, recorded by tcpdump. Record one small capture per weakness (plus a clean TLS 1.3 session and a DNS lookup that must trigger nothing) into `tests/pcaps/`. Every rule's tests are built on these captures.

#### Prerequisites

Week 0 sections 0.1 to 0.8 are done (Docker works). This task does not need JAI-01.

#### Steps

**Step 1.** Update `main` and create your branch (this task needs no Python environment, so there is nothing to activate yet):

```bash
cd ~/projects/maxguard
git checkout main && git pull
git checkout -b karthik/traffic-lab
```

**Step 2.** Create the lab's Compose file `lab/compose.yaml`:

```yaml
# MaxGuard traffic lab: insecure test services on an isolated network.
# `internal: true` means nothing here can reach the internet or your LAN.
services:
  server:
    build: ./server
    networks: [lab]
  sniffer:
    image: nicolaka/netshoot:v0.15
    network_mode: "service:server"      # shares the server's network card
    volumes: ["./captures:/captures"]
    command: ["tcpdump", "-i", "eth0", "-s", "0", "-U", "-w", "/captures/${CAPTURE:-capture}.pcap"]
    depends_on: [server]
  client:
    build: ./client
    networks: [lab]
    depends_on: [server, sniffer]
    command: ["python", "/scenarios/${SCENARIO:-telnet}.py"]
networks:
  lab: { internal: true }
```

`internal: true` is the important line: nothing in the lab can reach the internet or your home network. The sniffer shares the server's network card, so it records exactly what the server sends and receives.

**Step 3.** Create the server: `lab/server/Dockerfile`

```dockerfile
FROM python:3.11-slim-bookworm
RUN pip install --no-cache-dir pyftpdlib==2.2.0 cryptography==50.0.2
COPY . /srv
WORKDIR /srv
RUN python make_certs.py
CMD ["python", "/srv/services.py"]
```

`lab/server/make_certs.py` (fake certificates; the SHA-1 one is made with the `openssl` command because the `cryptography` library refuses to sign with SHA-1):

```python
"""Create the lab's test certificates. All are fake and only valid in the lab.

A lab CA signs every certificate except "selfsigned", so each TLS scenario
triggers exactly one certificate rule. The SHA-1 certificate is made with the
openssl command because the cryptography library refuses to sign with SHA-1
(it is insecure, which is exactly why the lab needs one).
"""
import datetime as dt
import subprocess

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID


def name(cn):
    return x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, cn)])


def save(prefix, key, cert):
    with open(f"{prefix}.key", "wb") as f:
        f.write(key.private_bytes(serialization.Encoding.PEM,
                                  serialization.PrivateFormat.TraditionalOpenSSL,
                                  serialization.NoEncryption()))
    with open(f"{prefix}.crt", "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))


def build(subject, issuer, public_key, signing_key, start, end, ca=False):
    return (x509.CertificateBuilder().subject_name(subject).issuer_name(issuer)
            .public_key(public_key).serial_number(x509.random_serial_number())
            .not_valid_before(start).not_valid_after(end)
            .add_extension(x509.BasicConstraints(ca=ca, path_length=None), critical=True)
            .sign(signing_key, hashes.SHA256()))


VALID = (dt.datetime(2026, 1, 1), dt.datetime(2036, 1, 1))
EXPIRED = (dt.datetime(2020, 1, 1), dt.datetime(2020, 12, 31))

ca_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
ca_name = name("MaxGuard Lab CA")
save("ca", ca_key, build(ca_name, ca_name, ca_key.public_key(), ca_key, *VALID, ca=True))

for prefix, key_size, dates in (("good", 2048, VALID), ("expired", 2048, EXPIRED),
                                ("weak", 1024, VALID)):
    key = rsa.generate_private_key(public_exponent=65537, key_size=key_size)
    save(prefix, key, build(name(f"{prefix}.lab.invalid"), ca_name, key.public_key(),
                            ca_key, *dates))

key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
cn = name("selfsigned.lab.invalid")
save("selfsigned", key, build(cn, cn, key.public_key(), key, *VALID))

subprocess.run(["openssl", "req", "-new", "-newkey", "rsa:2048", "-nodes",
                "-keyout", "sha1.key", "-out", "sha1.csr", "-subj", "/CN=sha1.lab.invalid"],
               check=True, capture_output=True)
subprocess.run(["openssl", "x509", "-req", "-in", "sha1.csr", "-CA", "ca.crt",
                "-CAkey", "ca.key", "-CAcreateserial", "-sha1", "-days", "3650",
                "-out", "sha1.crt"], check=True, capture_output=True)
print("certificates written")
```

and `lab/server/services.py` (every service is insecure on purpose):

```python
"""All lab services in one process. Every protocol here is insecure on purpose."""
import socketserver
import ssl
import struct
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer


class Telnet(socketserver.StreamRequestHandler):
    def handle(self):
        self.wfile.write(b"lab login: ")
        for line in self.rfile:
            self.wfile.write(b"$ " + line)
            if line.strip() == b"exit":
                break

class POP3(socketserver.StreamRequestHandler):
    def handle(self):
        self.wfile.write(b"+OK POP3 ready\r\n")
        for line in self.rfile:
            self.wfile.write(b"+OK\r\n")
            if line.upper().startswith(b"QUIT"):
                break

class IMAP(socketserver.StreamRequestHandler):
    def handle(self):
        self.wfile.write(b"* OK IMAP4rev1 ready\r\n")
        for line in self.rfile:
            self.wfile.write(line.split(b" ", 1)[0] + b" OK done\r\n")
            if b"LOGOUT" in line.upper():
                break

LAB_ANSWER_IP = bytes([10, 99, 0, 7])  # made-up address, never a real host

def dns_reply(query):
    """Answer one DNS question: every A query gets LAB_ANSWER_IP, anything else "no records"."""
    txid = query[:2]
    end = query.index(b"\x00", 12) + 5  # the name ends with a zero byte, then type + class
    question = query[12:end]
    qtype = struct.unpack("!H", query[end - 4:end - 2])[0]
    # flags 0x8180 = response + recursion desired + recursion available, NOERROR
    if qtype != 1:
        return txid + struct.pack("!HHHHH", 0x8180, 1, 0, 0, 0) + question
    # 0xc00c points back to the name in the question (offset 12); TTL 300 s
    answer = struct.pack("!HHHIH", 0xC00C, 1, 1, 300, 4) + LAB_ANSWER_IP
    return txid + struct.pack("!HHHHH", 0x8180, 1, 1, 0, 0) + question + answer

class DNS(socketserver.BaseRequestHandler):
    def handle(self):
        query, sock = self.request  # UDP: one datagram per request
        sock.sendto(dns_reply(query), self.client_address)

class Hello(socketserver.StreamRequestHandler):
    def handle(self):
        self.rfile.readline()
        self.wfile.write(b"HTTP/1.0 200 OK\r\nContent-Length: 2\r\n\r\nok")

def serve(server):
    threading.Thread(target=server.serve_forever, daemon=True).start()

def tls_server(port, cert, minimum, maximum, ciphers):
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.minimum_version, ctx.maximum_version = minimum, maximum
    if ciphers:
        ctx.set_ciphers(ciphers)
    ctx.load_cert_chain(f"/srv/{cert}.crt", f"/srv/{cert}.key")
    srv = socketserver.ThreadingTCPServer(("0.0.0.0", port), Hello)
    srv.socket = ctx.wrap_socket(srv.socket, server_side=True)
    serve(srv)

socketserver.ThreadingTCPServer.allow_reuse_address = True
for port, handler in ((23, Telnet), (110, POP3), (143, IMAP)):
    serve(socketserver.ThreadingTCPServer(("0.0.0.0", port), handler))
for port in (80, 8080):
    handler = partial(SimpleHTTPRequestHandler, directory="/srv")
    serve(ThreadingHTTPServer(("0.0.0.0", port), handler))
serve(socketserver.ThreadingUDPServer(("0.0.0.0", 53), DNS))

V = ssl.TLSVersion
LEGACY = "ALL:@SECLEVEL=0"
tls_server(4431, "good", V.TLSv1, V.TLSv1, LEGACY)                    # TLS 1.0
tls_server(4432, "good", V.TLSv1_2, V.TLSv1_2, "NULL-SHA256:@SECLEVEL=0")  # no encryption
tls_server(4433, "expired", V.TLSv1_2, V.TLSv1_2, LEGACY)             # expired cert
tls_server(4434, "weak", V.TLSv1_2, V.TLSv1_2, LEGACY)                # 1024-bit key
tls_server(4435, "sha1", V.TLSv1_2, V.TLSv1_2, LEGACY)                # SHA-1 signature
tls_server(4436, "good", V.TLSv1_3, V.TLSv1_3, None)                  # clean TLS 1.3
tls_server(4437, "selfsigned", V.TLSv1_2, V.TLSv1_2, None)            # self-signed cert

auth = DummyAuthorizer()
auth.add_user("labuser", "labpass", "/srv", perm="elr")
FTPHandler.authorizer = auth
print("lab services running", flush=True)
FTPServer(("0.0.0.0", 21), FTPHandler).serve_forever()
```

**Step 4.** Create the client: `lab/client/Dockerfile`

```dockerfile
FROM python:3.11-slim-bookworm
COPY scenarios /scenarios
```

and the scenarios in `lab/client/scenarios/`, one file per capture. The shared helpers `_common.py`:

```python
"""Helpers shared by every scenario."""
import socket
import ssl
import time

SERVER = "server"

def wait_for_sniffer():
    time.sleep(3)  # give tcpdump time to start before we send anything

def finish():
    time.sleep(2)  # let the last packets reach tcpdump before the lab stops

def tls_get(port, minimum=ssl.TLSVersion.TLSv1, maximum=ssl.TLSVersion.TLSv1_3,
            ciphers="ALL:@SECLEVEL=0"):
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE  # lab certificates are fake on purpose
    ctx.minimum_version, ctx.maximum_version = minimum, maximum
    if ciphers:
        ctx.set_ciphers(ciphers)
    with socket.create_connection((SERVER, port), timeout=10) as raw:
        with ctx.wrap_socket(raw, server_hostname=f"port{port}.lab.invalid") as s:
            s.sendall(b"GET / HTTP/1.0\r\n\r\n")
            return s.recv(4096)
```

`telnet.py`:

```python
import socket
import time

from _common import SERVER, finish, wait_for_sniffer

wait_for_sniffer()
s = socket.create_connection((SERVER, 23), timeout=10)
s.recv(4096)
for cmd in (b"labuser\r\n", b"whoami\r\n", b"exit\r\n"):
    s.sendall(cmd)
    time.sleep(0.5)
    try:
        s.recv(4096)
    except TimeoutError:
        pass
s.close()
finish()
```

`ftp.py`:

```python
import ftplib

from _common import SERVER, finish, wait_for_sniffer

wait_for_sniffer()
ftp = ftplib.FTP(SERVER, timeout=10)
ftp.login("labuser", "labpass")
ftp.nlst()
ftp.quit()
finish()
```

`plain_http.py`:

```python
import urllib.request

from _common import SERVER, finish, wait_for_sniffer

wait_for_sniffer()
urllib.request.urlopen(f"http://{SERVER}:80/", timeout=10).read()
finish()
```

`plain_http_alt.py`:

```python
import urllib.request

from _common import SERVER, finish, wait_for_sniffer

wait_for_sniffer()
urllib.request.urlopen(f"http://{SERVER}:8080/", timeout=10).read()
finish()
```

`pop3.py`:

```python
import poplib

from _common import SERVER, finish, wait_for_sniffer

wait_for_sniffer()
p = poplib.POP3(SERVER, timeout=10)
p.user("labuser")
p.pass_("labpass")
p.quit()
finish()
```

`imap.py`:

```python
import socket
import time

from _common import SERVER, finish, wait_for_sniffer

wait_for_sniffer()
s = socket.create_connection((SERVER, 143), timeout=10)
s.recv(4096)
for cmd in (b"a1 LOGIN labuser labpass\r\n", b"a2 LOGOUT\r\n"):
    s.sendall(cmd)
    time.sleep(0.5)
    s.recv(4096)
s.close()
finish()
```

`tls_weak_version.py`:

```python
import ssl

from _common import finish, tls_get, wait_for_sniffer

wait_for_sniffer()
tls_get(4431, ssl.TLSVersion.TLSv1, ssl.TLSVersion.TLSv1)
finish()
```

`tls_weak_cipher.py`:

```python
import ssl

from _common import finish, tls_get, wait_for_sniffer

wait_for_sniffer()
tls_get(4432, ssl.TLSVersion.TLSv1_2, ssl.TLSVersion.TLSv1_2, "NULL-SHA256:@SECLEVEL=0")
finish()
```

`cert_expired.py`:

```python
import ssl

from _common import finish, tls_get, wait_for_sniffer

wait_for_sniffer()
tls_get(4433, ssl.TLSVersion.TLSv1_2, ssl.TLSVersion.TLSv1_2)
finish()
```

`cert_self_signed.py`:

```python
import ssl

from _common import finish, tls_get, wait_for_sniffer

wait_for_sniffer()
tls_get(4437, ssl.TLSVersion.TLSv1_2, ssl.TLSVersion.TLSv1_2, None)
finish()
```

`cert_weak_key.py`:

```python
import ssl

from _common import finish, tls_get, wait_for_sniffer

wait_for_sniffer()
tls_get(4434, ssl.TLSVersion.TLSv1_2, ssl.TLSVersion.TLSv1_2)
finish()
```

`cert_sha1.py`:

```python
import ssl

from _common import finish, tls_get, wait_for_sniffer

wait_for_sniffer()
tls_get(4435, ssl.TLSVersion.TLSv1_2, ssl.TLSVersion.TLSv1_2)
finish()
```

`clean_tls13.py`:

```python
import ssl

from _common import finish, tls_get, wait_for_sniffer

wait_for_sniffer()
tls_get(4436, ssl.TLSVersion.TLSv1_3, ssl.TLSVersion.TLSv1_3, None)
finish()
```

`dns_lookup.py`:

```python
"""Ask the lab DNS server (UDP port 53) for three made-up names."""
import socket
import struct

from _common import SERVER, finish, wait_for_sniffer

NAMES = ["printer.lab.invalid", "nas.lab.invalid", "camera.lab.invalid"]

def dns_query(txid, name):
    # flags 0x0100 = "recursion desired"; one question of type A (1), class IN (1)
    labels = b"".join(bytes([len(part)]) + part.encode() for part in name.split("."))
    return struct.pack("!HHHHHH", txid, 0x0100, 1, 0, 0, 0) + labels + b"\x00\x00\x01\x00\x01"

wait_for_sniffer()
server_ip = socket.gethostbyname(SERVER)  # Docker's built-in DNS: not on the captured link
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.settimeout(5)
    for txid, name in enumerate(NAMES, start=0x1001):
        s.sendto(dns_query(txid, name), (server_ip, 53))
        s.recv(512)  # wait for each answer so the capture has query + reply pairs
finish()
```

(The two HTTP scenarios are not called `http.py`: a file with that name would hide Python's own `http` package from the client.)

**Step 5.** Build the images once (this downloads Python packages, so it needs the internet):

```bash
cd lab && docker compose build && cd ..
```

*Run in planning with the same Dockerfiles; the build log is long and differs on every machine, so it is not shown. It ends without an error.*

**Step 6.** Record every capture. Each run starts the server and the sniffer, runs one scenario, and stops everything when the client finishes:

```bash
cd lab
for s in telnet ftp plain_http plain_http_alt pop3 imap tls_weak_version tls_weak_cipher cert_expired cert_self_signed cert_weak_key cert_sha1 clean_tls13 dns_lookup; do
  CAPTURE=$s SCENARIO=$s docker compose up --abort-on-container-exit --exit-code-from client
  docker compose down
done
ls -l captures
cd ..
```

Expected output (the end of the planning run for pop3):

```text
client-1 exited with code 0
 Compose Stopping Aborting on container exit...
sniffer-1  | 24 packets captured
sniffer-1  | 24 packets received by filter
sniffer-1  | 0 packets dropped by kernel
server-1 exited with code 137
```

*The server's exit code 137 is normal: Compose stops it once the client is done.*

**Step 7.** Copy the captures into the tests folder and add the source file `tests/pcaps/SOURCES.md` (update the SHA-256 column with `sha256sum tests/pcaps/*.pcap | cut -c1-16` if you re-recorded):

```bash
mkdir -p tests/pcaps
cp lab/captures/*.pcap tests/pcaps/
```

```markdown
# Where the test captures come from

Every capture in this folder is **synthetic**. It was recorded in MaxGuard's
own traffic lab (`lab/`): a client container talks to a server container on an
isolated Docker network (`internal: true`, no route to the internet or to any
LAN), and a third container records the server's network card with tcpdump.
No capture comes from a real network or from a third party (CLAUDE.md rule 6).

Recorded on October 6, 2026 with the lab as committed: server and client
`python:3.11-slim-bookworm` (pyftpdlib 2.2.0, cryptography 50.0.2, the image's
OpenSSL), sniffer `nicolaka/netshoot:v0.15`. Docker gave the lab network
172.18.0.0/16: server 172.18.0.2, client 172.18.0.3 (your own recordings may
get other addresses). All certificates are fake and made by
`lab/server/make_certs.py`; host names end in `.invalid`.

| Capture | Scenario (`lab/client/scenarios/`) | Shows | Rule it must trigger | SHA-256 (first 16) |
|---|---|---|---|---|
| `telnet.pcap` | `telnet.py` | Telnet login and commands | `cleartext.telnet` | `deb2874b1e5c2b87` |
| `ftp.pcap` | `ftp.py` | FTP login and a directory listing | `cleartext.ftp` | `01434b223a3cabc2` |
| `plain_http.pcap` | `plain_http.py` | HTTP on port 80 | `cleartext.http` | `b7d34b2ce10bbb9e` |
| `plain_http_alt.pcap` | `plain_http_alt.py` | HTTP on port 8080 | `cleartext.http_alt` | `4189f2906f14a26c` |
| `pop3.pcap` | `pop3.py` | POP3 without TLS | `cleartext.pop3` | `4edc60ce003e5b88` |
| `imap.pcap` | `imap.py` | IMAP without TLS | `cleartext.imap` | `d222b4fe1b780a7d` |
| `tls_weak_version.pcap` | `tls_weak_version.py` | TLS 1.0 | `tls.weak_version` | `782cb7525451bbbf` |
| `tls_weak_cipher.pcap` | `tls_weak_cipher.py` | TLS 1.2 with the NULL cipher (no encryption) | `tls.weak_cipher` | `b22a69477de2f5a0` |
| `cert_expired.pcap` | `cert_expired.py` | Certificate that expired in 2020 | `cert.expired` | `b513d0a4d34eb5f6` |
| `cert_self_signed.pcap` | `cert_self_signed.py` | Self-signed certificate | `cert.self_signed` | `47428ab30eea0c7a` |
| `cert_weak_key.pcap` | `cert_weak_key.py` | 1024-bit RSA key | `cert.weak_key` | `705b8183f48bc3b9` |
| `cert_sha1.pcap` | `cert_sha1.py` | Certificate signed with SHA-1 | `cert.sha1_signature` | `d04014c8ec011562` |
| `clean_tls13.pcap` | `clean_tls13.py` | Good TLS 1.3 session | none | `0319e88caf5ecb5c` |
| `dns_lookup.pcap` | `dns_lookup.py` | Three DNS questions and answers | none | `ae6da75fc2cc5f6f` |

The RDP rule (`rdp.standard_security`) and DHCP have no lab capture yet; their
tests use the hand-made fixtures in `tests/fixtures/zeek/_handmade/`.

**Adding a capture:** add a scenario to the lab, record it, add a row here,
regenerate the fixtures (`bash scripts/make_fixtures.sh`), and add its expected
result. No source line, no merge.
```

**Step 8.** Look inside one capture with tcpdump (the netshoot image has it):

```bash
docker run --rm -v "$PWD/tests/pcaps:/p:ro" --entrypoint tcpdump nicolaka/netshoot:v0.15 -nn -r /p/telnet.pcap 'tcp port 23' | head -n 4
```

Expected output:

```text
reading from file /p/telnet.pcap, link-type EN10MB (Ethernet), snapshot length 262144
01:31:24.287418 IP 172.18.0.3.55398 > 172.18.0.2.23: Flags [S], seq 2328852918, win 64240, options [mss 1460,sackOK,TS val 3374244774 ecr 0,nop,wscale 10], length 0
01:31:24.287571 IP 172.18.0.2.23 > 172.18.0.3.55398: Flags [S.], seq 3945191018, ack 2328852919, win 65160, options [mss 1460,sackOK,TS val 4015193217 ecr 3374244774,nop,wscale 10], length 0
01:31:24.287595 IP 172.18.0.3.55398 > 172.18.0.2.23: Flags [.], ack 1, win 63, options [nop,nop,TS val 3374244775 ecr 4015193217], length 0
01:31:24.288242 IP 172.18.0.2.23 > 172.18.0.3.55398: Flags [P.], seq 1:12, ack 1, win 64, options [nop,nop,TS val 4015193218 ecr 3374244775], length 11
```

**Step 9.** Commit, push, and open the pull request:

```bash
git add -A
git status          # only this task's files: nothing from .venv/, data/ or lab/captures/
git commit -m "test: traffic lab and the 14 synthetic test captures (KAR-01)"
git push -u origin HEAD
```

`HEAD` means "the branch I am on", so you do not have to retype its name. Open the repository on github.com: a yellow bar shows your branch with a **Compare & pull request** button. Click it, keep the title `test: traffic lab and the 14 synthetic test captures (KAR-01)`, fill in the template (paste the real output of the commands above under **How I tested it**), write `Closes #<issue number>` (this task's issue), and pick **@JWinborne1** under **Reviewers**. Click **Create pull request**, then fix anything CI or the reviewer finds with new commits on the same branch.

#### How to test

`ls -l lab/captures` lists 14 files of 1 to 4 KB. The tcpdump command shows the client (`172.18.0.3` in planning) opening a connection to port 23 on the server. Docker may give your lab network other addresses; that is fine. KAR-02 then turns the captures into fixtures, and FIO-02 and JAK-03 prove each one triggers exactly its rule.

#### What you just did and why

A detection rule is only as good as its test data, and this repository is public, so real captures from anyone's network are not allowed (CLAUDE.md rule 6). A lab of our own makes captures we can share, regenerate, and explain line by line. One weakness per capture keeps each test unambiguous; the two clean captures catch rules that fire on everything.

#### Pull request checklist

- [ ] `ruff check .` prints `All checks passed!`
- [ ] `pytest -m "not integration" -q` passes on your laptop
- [ ] The pull request title has the form `type: summary (TASK-ID)` and the body says `Closes #<issue number>`
- [ ] No secrets, passwords, email addresses, personal data, or captures from a real network (CLAUDE.md rule 6)
- [ ] Any new dependency has a row in `docs/DEPENDENCIES.md` with its license
- [ ] CI is green and your reviewer approved
- [ ] Every capture has a row in `tests/pcaps/SOURCES.md`
- [ ] Each capture is under 1 MB

### KAR-02: Test fixtures: Zeek and Suricata output for every capture

**Due:** Week 1 (due Fri Oct 16) · **Milestone:** `W1 Building blocks` · **Needs first:** [KAR-01](#kar-01-traffic-lab-and-the-14-test-captures), [JAK-01](jakub.md#jak-01-maxguards-zeek-scripts-cleartext-sessions-and-asset-tracking), [JAK-02](jakub.md#jak-02-suricata-configuration-community-id-and-ja4), [JAI-01](jaiden.md#jai-01-restructure-the-repository-add-packaging-and-ci) · **Kind:** code, tested

**Issue labels:** `type:task` `phase:alpha` `owner:karthik` `area:testing` `critical-path`

#### Goal

Write `scripts/make_fixtures.sh`, which runs Zeek 9.0.0 and Suricata 7.0.10 on every capture exactly the way MaxGuard does and saves the logs to `tests/fixtures/zeek/<capture>/`, and add the hand-made fixtures for traffic the lab does not make yet (DNS with DHCP, RDP, and tab-separated logs). Unit tests read these folders, so they run in seconds without Docker.

#### Prerequisites

KAR-01, JAK-01 (Zeek scripts) and JAK-02 (Suricata config) are merged.

#### Steps

**Step 1.** Update `main` and create your branch for this task (one branch per task):

```bash
cd ~/projects/maxguard
source .venv/bin/activate
git checkout main && git pull
git checkout -b karthik/fixtures
```

If `source .venv/bin/activate` fails, you have not made the virtual environment yet: do Week 0 section 0.11 first.

**Step 2.** Create `scripts/make_fixtures.sh`:

```bash
#!/usr/bin/env bash
# Rebuild the unit-test fixtures from the lab captures (Karthik, KAR-02).
#
# For every tests/pcaps/<name>.pcap this writes tests/fixtures/zeek/<name>/:
# the Zeek JSON logs and Suricata's eve.json, made exactly the way MaxGuard
# makes them (Zeek 9.0.0 with -D and Community ID, MaxGuard's Zeek scripts,
# Suricata 7.0.10 with MaxGuard's config). Unit tests read these folders, so
# they run in seconds without Docker.
#
# Usage (from the repository root):  bash scripts/make_fixtures.sh
# Optional: FIXTURES_DIR=/tmp/x bash scripts/make_fixtures.sh   (write elsewhere)
set -euo pipefail

ZEEK_IMAGE="zeek/zeek:9.0.0"
SURICATA_IMAGE="jasonish/suricata:7.0.10"   # same base version as Debian 13's package
FIXTURES_DIR="${FIXTURES_DIR:-tests/fixtures/zeek}"
USER_IDS="$(id -u):$(id -g)"   # files belong to you, not to root

cd "$(dirname "$0")/.."
mkdir -p "$FIXTURES_DIR"
FIXTURES_DIR="$(cd "$FIXTURES_DIR" && pwd)"

for pcap in tests/pcaps/*.pcap; do
  name="$(basename "$pcap" .pcap)"
  out="$FIXTURES_DIR/$name"
  rm -rf "$out"
  mkdir -p "$out"

  # Zeek: -D makes the output identical on every run; --network none proves it is offline.
  docker run --rm --network none --user "$USER_IDS" \
    -v "$PWD/tests/pcaps:/pcaps:ro" -v "$PWD/maxguard/zeek:/mgzeek:ro" \
    -v "$out:/logs" -w /logs "$ZEEK_IMAGE" \
    zeek -D -C -r "/pcaps/$name.pcap" /mgzeek/site.zeek LogAscii::use_json=T \
      policy/protocols/conn/community-id-logging /mgzeek/scripts/cleartext.zeek \
      /mgzeek/scripts/inventory.zeek
  # These logs describe the Zeek run itself, not the traffic, and change every run.
  rm -f "$out"/loaded_scripts.log "$out"/packet_filter.log "$out"/stats.log \
        "$out"/capture_loss.log "$out"/reporter.log

  # Suricata: writes eve.json (plus files we do not keep) into a scratch folder.
  scratch="$(mktemp -d)"
  docker run --rm --network none --user "$USER_IDS" --entrypoint suricata \
    -v "$PWD/tests/pcaps:/pcaps:ro" -v "$PWD/maxguard/suricata:/cfg:ro" -v "$scratch:/out" \
    "$SURICATA_IMAGE" -c /cfg/maxguard-suricata.yaml -r "/pcaps/$name.pcap" -l /out \
      -k none --runmode single -S /cfg/rules/maxguard.rules > /dev/null
  cp "$scratch/eve.json" "$out/eve.json"
  rm -rf "$scratch"

  echo "$name: $(cd "$out" && ls | tr '\n' ' ')"
done
```

**Step 3.** Run it:

```bash
bash scripts/make_fixtures.sh
```

It prints one line per capture with the files it wrote, for example `telnet: conn.log eve.json known_hosts.log maxguard_cleartext.log`.

**Step 4.** Add the hand-made fixtures for traffic the lab does not make yet. Create `tests/fixtures/zeek/_handmade/README.md`:

````markdown
# Hand-made fixtures

No lab capture has DHCP traffic or a Suricata alert (only `dns_lookup`, added
later, has DNS), and all their logs are JSON. These small fixtures fill those gaps. The folder name
starts with `_` so tests that loop over "one folder per lab capture" skip it.

All data is synthetic: addresses in 192.168.56.0/24, MAC 02:00:00:aa:bb:cc
(locally administered, made up), names under `.invalid`.

| Folder | What | Made with |
|---|---|---|
| `dns_dhcp/` | `dns_dhcp.pcap` (1 DHCP lease + 1 DNS lookup) and its `conn.log`, `dns.log`, `dhcp.log` (Zeek JSON) and `eve.json` (has `alert`, `dns`, `dhcp`, `flow`) | `make_dns_dhcp_pcap.py`, Zeek 9.0.0, Suricata 7.0.10 |
| `dns_dhcp_suricata8/` | `eve.json` of the same capture from Suricata 8.0.7 (eve DNS format version 3) | Suricata 8.0.7 |
| `tsv_plain_http/` | `conn.log`, `http.log` of `tests/pcaps/plain_http.pcap` in Zeek's default TSV format | Zeek 9.0.0 |
| `tsv_dns_dhcp/` | `conn.log`, `dns.log`, `dhcp.log` of `dns_dhcp.pcap` in TSV format | Zeek 9.0.0 |

`fixture-only.rules` holds one Suricata rule (sid 9000001) used only to get a
real `alert` record into `eve.json`. It is not part of MaxGuard's rules.

Field names come from the real tools, and match the Zeek 9.0.0 scripts
`base/protocols/dns/main.zeek` and `base/protocols/dhcp/main.zeek`
(https://github.com/zeek/zeek/tree/v9.0.0/scripts/base/protocols). Note that
`dhcp.log` has no `uid`/`id.*` fields: it has a `uids` set, and the ports are
not logged.

## Rebuild (from the repository root)

```bash
H=tests/fixtures/zeek/_handmade
python $H/make_dns_dhcp_pcap.py $H/dns_dhcp/dns_dhcp.pcap

# Zeek JSON logs (same options as maxguard/zeek/runner.py)
docker run --rm --network none -v "$PWD":/src -w /src/$H/dns_dhcp zeek/zeek:9.0.0 \
  zeek -D -C -r dns_dhcp.pcap /src/maxguard/zeek/site.zeek LogAscii::use_json=T \
  policy/protocols/conn/community-id-logging \
  /src/maxguard/zeek/scripts/cleartext.zeek /src/maxguard/zeek/scripts/inventory.zeek
# keep conn.log, dns.log, dhcp.log; delete the other *.log files

# Suricata eve.json (same options as maxguard/suricata/runner.py, plus the fixture rule)
docker run --rm --network none -v "$PWD":/src jasonish/suricata:7.0.10 \
  suricata -c /src/maxguard/suricata/maxguard-suricata.yaml \
  -r /src/$H/dns_dhcp/dns_dhcp.pcap -l /src/$H/dns_dhcp -k none --runmode single \
  -S /src/$H/fixture-only.rules
# delete fast.log, stats.log, suricata.log (only eve.json is kept)
```

For the TSV folders run the same Zeek command without `LogAscii::use_json=T`
(on `tests/pcaps/plain_http.pcap` for `tsv_plain_http/`).
````

the two capture generators (they write the same bytes on every run) `tests/fixtures/zeek/_handmade/make_dns_dhcp_pcap.py`:

```python
"""Build dns_dhcp.pcap: one DNS lookup and one DHCP lease, fully synthetic.

No lab capture contains DHCP (only dns_lookup has DNS), so this script writes the
packets byte by byte (standard library only). Zeek 9.0.0 and Suricata 7.0.10
then turn the capture into the dns.log, dhcp.log and eve.json fixtures next to
this file, so the field names are the real ones, not guesses.

Addresses: 192.168.56.0/24 (private lab range), MAC 02:00:00:aa:bb:cc (the 02
prefix marks a locally administered, made-up address), names under .invalid.

Run:  python make_dns_dhcp_pcap.py dns_dhcp.pcap
"""

from __future__ import annotations

import struct
import sys
from pathlib import Path

START_TS = 1791252600.0  # 2026-10-06 02:10:00 UTC (one hour after the lab captures)

CLIENT_MAC = bytes.fromhex("020000aabbcc")  # 02:00:00:aa:bb:cc
SERVER_MAC = bytes.fromhex("020000000001")
BROADCAST_MAC = b"\xff" * 6

CLIENT_IP = "192.168.56.50"
SERVER_IP = "192.168.56.1"
PRINTER_IP = "192.168.56.20"


def ip_bytes(ip: str) -> bytes:
    return bytes(int(part) for part in ip.split("."))


def checksum(data: bytes) -> int:
    """The 16-bit one's complement sum used by the IPv4 header."""
    if len(data) % 2:
        data += b"\x00"
    total = sum(struct.unpack(f"!{len(data) // 2}H", data))
    while total > 0xFFFF:
        total = (total & 0xFFFF) + (total >> 16)
    return ~total & 0xFFFF


def udp_packet(src_mac: bytes, dst_mac: bytes, src_ip: str, dst_ip: str,
               sport: int, dport: int, payload: bytes, ip_id: int) -> bytes:
    """Ethernet + IPv4 + UDP around a payload. UDP checksum 0 = "not used" (IPv4)."""
    udp = struct.pack("!HHHH", sport, dport, 8 + len(payload), 0) + payload
    header = struct.pack("!BBHHHBBH4s4s", 0x45, 0, 20 + len(udp), ip_id, 0, 64, 17, 0,
                         ip_bytes(src_ip), ip_bytes(dst_ip))
    header = header[:10] + struct.pack("!H", checksum(header)) + header[12:]
    return dst_mac + src_mac + b"\x08\x00" + header + udp


def dns_name(name: str) -> bytes:
    return b"".join(bytes([len(p)]) + p.encode() for p in name.split(".")) + b"\x00"


def dns_query(txid: int, name: str) -> bytes:
    # flags 0x0100 = "recursion desired"; one question, type A, class IN
    return struct.pack("!HHHHHH", txid, 0x0100, 1, 0, 0, 0) + dns_name(name) + b"\x00\x01\x00\x01"


def dns_answer(txid: int, name: str, answer_ip: str, ttl: int) -> bytes:
    # flags 0x8180 = response + recursion desired + recursion available, NOERROR
    question = dns_name(name) + b"\x00\x01\x00\x01"
    # 0xc00c is a pointer back to the name in the question (offset 12)
    answer = struct.pack("!HHHIH", 0xC00C, 1, 1, ttl, 4) + ip_bytes(answer_ip)
    return struct.pack("!HHHHHH", txid, 0x8180, 1, 1, 0, 0) + question + answer


def dhcp_message(op: int, xid: int, msg_type: int, yiaddr: str, options: bytes) -> bytes:
    """One BOOTP/DHCP message (RFC 2131) with the given options."""
    fixed = struct.pack("!BBBBIHH4s4s4s4s", op, 1, 6, 0, xid, 0, 0x8000,
                        ip_bytes("0.0.0.0"), ip_bytes(yiaddr),
                        ip_bytes("0.0.0.0"), ip_bytes("0.0.0.0"))
    chaddr = CLIENT_MAC + b"\x00" * 10
    sname_file = b"\x00" * (64 + 128)
    cookie = b"\x63\x82\x53\x63"
    return fixed + chaddr + sname_file + cookie + bytes([53, 1, msg_type]) + options + b"\xff"


def option(code: int, value: bytes) -> bytes:
    return bytes([code, len(value)]) + value


def build_packets() -> list[tuple[float, bytes]]:
    xid = 0x3903F326
    host = option(12, b"laptop-lab")
    server_opts = (option(54, ip_bytes(SERVER_IP)) + option(51, struct.pack("!I", 3600))
                   + option(1, ip_bytes("255.255.255.0")) + option(3, ip_bytes(SERVER_IP)))
    request_opts = host + option(50, ip_bytes(CLIENT_IP)) + option(54, ip_bytes(SERVER_IP))
    t = START_TS
    return [
        # DHCP: DISCOVER, OFFER, REQUEST, ACK (all broadcast, client has no IP yet)
        (t + 0.00, udp_packet(CLIENT_MAC, BROADCAST_MAC, "0.0.0.0", "255.255.255.255", 68, 67,
                              dhcp_message(1, xid, 1, "0.0.0.0", host), 1)),
        (t + 0.01, udp_packet(SERVER_MAC, BROADCAST_MAC, SERVER_IP, "255.255.255.255", 67, 68,
                              dhcp_message(2, xid, 2, CLIENT_IP, server_opts), 2)),
        (t + 0.02, udp_packet(CLIENT_MAC, BROADCAST_MAC, "0.0.0.0", "255.255.255.255", 68, 67,
                              dhcp_message(1, xid, 3, "0.0.0.0", request_opts), 3)),
        (t + 0.03, udp_packet(SERVER_MAC, BROADCAST_MAC, SERVER_IP, "255.255.255.255", 67, 68,
                              dhcp_message(2, xid, 5, CLIENT_IP, server_opts), 4)),
        # DNS: the new laptop looks up the printer
        (t + 1.00, udp_packet(CLIENT_MAC, SERVER_MAC, CLIENT_IP, SERVER_IP, 53001, 53,
                              dns_query(0x1A2B, "printer.lab.invalid"), 5)),
        (t + 1.01, udp_packet(SERVER_MAC, CLIENT_MAC, SERVER_IP, CLIENT_IP, 53, 53001,
                              dns_answer(0x1A2B, "printer.lab.invalid", PRINTER_IP, 300), 6)),
    ]


def write_pcap(path: Path, packets: list[tuple[float, bytes]]) -> None:
    # classic pcap: magic, version 2.4, timezone 0, sigfigs 0, snaplen, Ethernet
    out = [struct.pack("<IHHiIII", 0xA1B2C3D4, 2, 4, 0, 0, 65535, 1)]
    for ts, frame in packets:
        seconds = int(ts)
        micros = round((ts - seconds) * 1_000_000)
        out.append(struct.pack("<IIII", seconds, micros, len(frame), len(frame)) + frame)
    path.write_bytes(b"".join(out))


if __name__ == "__main__":
    write_pcap(Path(sys.argv[1]), build_packets())
```

and `tests/fixtures/zeek/_handmade/rdp/make_rdp_pcap.py` with its notes `tests/fixtures/zeek/_handmade/rdp/README.md`:

```python
"""Build rdp.pcap: two RDP connection starts, fully synthetic.

None of the lab captures contains RDP, so this script writes the packets byte
by byte (standard library only). Zeek 9.0.0 then turns the capture into the
rdp.log and conn.log next to this file, so the field names and values are the
real ones, not guesses.

Each connection is only the first RDP exchange (MS-RDPBCGR 2.2.1.1 and 2.2.1.2):
the client's X.224 Connection Request and the server's X.224 Connection Confirm,
whose RDP_NEG_RSP says which security protocol the server picked. That one
value is what Zeek logs as rdp.log `security_protocol`:
- old server 192.168.56.30 picks PROTOCOL_RDP (0) -> "RDP" (Standard RDP Security)
- new server 192.168.56.31 picks PROTOCOL_HYBRID (2) -> "HYBRID" (TLS + CredSSP)

Addresses: 192.168.56.0/24 (private lab range), MACs start with 02 (locally
administered, made up). The cookie user name "labuser" is made up too.

Run:  python make_rdp_pcap.py rdp.pcap
"""

from __future__ import annotations

import struct
import sys
from pathlib import Path

START_TS = 1791253200.0  # 2026-10-06 02:20:00 UTC (after the other hand-made fixtures)

CLIENT_MAC = bytes.fromhex("020000aabbcc")
SERVER_MAC = bytes.fromhex("020000000002")

CLIENT_IP = "192.168.56.50"
OLD_SERVER_IP = "192.168.56.30"  # answers with Standard RDP Security
NEW_SERVER_IP = "192.168.56.31"  # answers with HYBRID (Network Level Authentication)
RDP_PORT = 3389

# RDP_NEG_REQ / RDP_NEG_RSP protocol values (MS-RDPBCGR 2.2.1.1.1 and 2.2.1.2.1)
PROTOCOL_RDP = 0x00
PROTOCOL_SSL = 0x01
PROTOCOL_HYBRID = 0x02

# TCP flag bits
FIN, SYN, PSH, ACK = 0x01, 0x02, 0x08, 0x10


def ip_bytes(ip: str) -> bytes:
    return bytes(int(part) for part in ip.split("."))


def checksum(data: bytes) -> int:
    """The 16-bit one's complement sum used by IPv4 and TCP headers."""
    if len(data) % 2:
        data += b"\x00"
    total = sum(struct.unpack(f"!{len(data) // 2}H", data))
    while total > 0xFFFF:
        total = (total & 0xFFFF) + (total >> 16)
    return ~total & 0xFFFF


def tcp_packet(src_ip: str, dst_ip: str, sport: int, dport: int, seq: int, ack: int,
               flags: int, payload: bytes, ip_id: int) -> bytes:
    """Ethernet + IPv4 + TCP (20-byte header, no options) around a payload."""
    src_mac, dst_mac = (CLIENT_MAC, SERVER_MAC) if src_ip == CLIENT_IP else (SERVER_MAC, CLIENT_MAC)
    header = struct.pack("!HHIIBBHHH", sport, dport, seq, ack, 5 << 4, flags, 65535, 0, 0)
    # The TCP checksum covers a "pseudo header" with both IPs, then header + data.
    pseudo = ip_bytes(src_ip) + ip_bytes(dst_ip) + struct.pack("!BBH", 0, 6,
                                                                len(header) + len(payload))
    header = header[:16] + struct.pack("!H", checksum(pseudo + header + payload)) + header[18:]
    tcp = header + payload
    ip = struct.pack("!BBHHHBBH4s4s", 0x45, 0, 20 + len(tcp), ip_id, 0x4000, 64, 6, 0,
                     ip_bytes(src_ip), ip_bytes(dst_ip))
    ip = ip[:10] + struct.pack("!H", checksum(ip)) + ip[12:]
    return dst_mac + src_mac + b"\x08\x00" + ip + tcp


def tpkt(x224: bytes) -> bytes:
    """TPKT header (RFC 1006): version 3, reserved 0, total length, big-endian."""
    return struct.pack("!BBH", 3, 0, 4 + len(x224)) + x224


def connection_request(cookie: str, requested_protocols: int) -> bytes:
    """Client X.224 Connection Request PDU (MS-RDPBCGR 2.2.1.1)."""
    cookie_bytes = f"Cookie: mstshash={cookie}\r\n".encode("ascii")
    neg_req = struct.pack("<BBHI", 0x01, 0, 8, requested_protocols)  # RDP_NEG_REQ
    body = struct.pack("!BHHB", 0xE0, 0, 0, 0) + cookie_bytes + neg_req  # CR, refs, class 0
    return tpkt(bytes([len(body)]) + body)  # first byte = X.224 length indicator


def connection_confirm(selected_protocol: int) -> bytes:
    """Server X.224 Connection Confirm PDU (MS-RDPBCGR 2.2.1.2)."""
    neg_rsp = struct.pack("<BBHI", 0x02, 0, 8, selected_protocol)  # RDP_NEG_RSP
    body = struct.pack("!BHHB", 0xD0, 0, 0x1234, 0) + neg_rsp  # CC, refs, class 0
    return tpkt(bytes([len(body)]) + body)


def rdp_session(server_ip: str, client_port: int, request: bytes, confirm: bytes,
                start: float, first_ip_id: int) -> list[tuple[float, bytes]]:
    """Handshake, one request, one confirm, then a clean close (FIN both ways)."""
    c_seq, s_seq = 1000, 5000  # fixed initial sequence numbers: same bytes every run
    c_end = c_seq + 1 + len(request)  # client's next sequence number after its data
    s_end = s_seq + 1 + len(confirm)
    # (sent by client?, seq, ack, flags, data)
    steps = [
        (True, c_seq, 0, SYN, b""),
        (False, s_seq, c_seq + 1, SYN | ACK, b""),
        (True, c_seq + 1, s_seq + 1, ACK, b""),
        (True, c_seq + 1, s_seq + 1, PSH | ACK, request),
        (False, s_seq + 1, c_end, PSH | ACK, confirm),
        (True, c_end, s_end, FIN | ACK, b""),
        (False, s_end, c_end + 1, FIN | ACK, b""),
        (True, c_end + 1, s_end + 1, ACK, b""),
    ]
    packets = []
    for i, (from_client, seq, ack, flags, data) in enumerate(steps):
        if from_client:
            frame = tcp_packet(CLIENT_IP, server_ip, client_port, RDP_PORT,
                               seq, ack, flags, data, first_ip_id + i)
        else:
            frame = tcp_packet(server_ip, CLIENT_IP, RDP_PORT, client_port,
                               seq, ack, flags, data, first_ip_id + i)
        packets.append((start + i * 0.001, frame))
    return packets


def build_packets() -> list[tuple[float, bytes]]:
    # A legacy client that asks only for Standard RDP Security, and a server that agrees.
    old = rdp_session(OLD_SERVER_IP, 50001,
                      connection_request("labuser", PROTOCOL_RDP),
                      connection_confirm(PROTOCOL_RDP), START_TS, 1)
    # A modern client offering TLS or CredSSP; the server picks CredSSP (HYBRID).
    new = rdp_session(NEW_SERVER_IP, 50002,
                      connection_request("labuser", PROTOCOL_SSL | PROTOCOL_HYBRID),
                      connection_confirm(PROTOCOL_HYBRID), START_TS + 1.0, 101)
    return old + new


def write_pcap(path: Path, packets: list[tuple[float, bytes]]) -> None:
    # classic pcap: magic, version 2.4, timezone 0, sigfigs 0, snaplen, Ethernet
    out = [struct.pack("<IHHiIII", 0xA1B2C3D4, 2, 4, 0, 0, 65535, 1)]
    for ts, frame in packets:
        seconds = int(ts)
        micros = round((ts - seconds) * 1_000_000)
        out.append(struct.pack("<IIII", seconds, micros, len(frame), len(frame)) + frame)
    path.write_bytes(b"".join(out))


if __name__ == "__main__":
    write_pcap(Path(sys.argv[1]), build_packets())
```

````markdown
# RDP fixture (hand-made capture, real Zeek output)

No lab capture contains RDP, so `make_rdp_pcap.py` writes a tiny synthetic
capture byte by byte, and Zeek 9.0.0 turns it into the logs in this folder.
The logs are real Zeek output, not typed by hand, so their field names and
values are exactly what Zeek 9 writes.

| File | What |
|---|---|
| `make_rdp_pcap.py` | builds `rdp.pcap` (standard library only) |
| `rdp.pcap` | 2 TCP connections to port 3389, each: handshake, X.224 Connection Request, X.224 Connection Confirm, close |
| `rdp.log` | 2 records: `security_protocol` `"RDP"` (server 192.168.56.30) and `"HYBRID"` (server 192.168.56.31) |
| `conn.log` | the 2 connections (so the folder is also a valid Zeek log folder for `maxguard analyze`) |

`security_protocol` is the protocol the server picked in its RDP Negotiation
Response (`selectedProtocol`, MS-RDPBCGR 2.2.1.2.1:
https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-rdpbcgr/b2975bdc-6d56-49ee-9c57-f2ff3a0b6817).
Zeek 9.0.0 names the values in `base/protocols/rdp/consts.zeek`:
0 = `"RDP"` (Standard RDP Security), 1 = `"SSL"`, 2 = `"HYBRID"` (CredSSP),
8 = `"HYBRID_EX"`. The rdp.log fields are defined in
`base/protocols/rdp/main.zeek` (`RDP::Info`), read from the `zeek/zeek:9.0.0`
image and also at https://github.com/zeek/zeek/blob/v9.0.0/scripts/base/protocols/rdp/main.zeek.

Rule `rdp.standard_security` must fire for the `"RDP"` record only.

All data is synthetic: addresses in 192.168.56.0/24, MACs starting with 02
(locally administered), cookie user name `labuser`.

## Rebuild (from the repository root)

```bash
H=tests/fixtures/zeek/_handmade/rdp
python $H/make_rdp_pcap.py $H/rdp.pcap

# same options as maxguard/zeek/runner.py
docker run --rm --network none -v "$PWD":/src -w /src/$H zeek/zeek:9.0.0 \
  zeek -D -C -r rdp.pcap /src/maxguard/zeek/site.zeek LogAscii::use_json=T \
  policy/protocols/conn/community-id-logging \
  /src/maxguard/zeek/scripts/cleartext.zeek /src/maxguard/zeek/scripts/inventory.zeek
# keep conn.log and rdp.log; delete the other *.log files
```

Running the two steps twice gives byte-identical `rdp.pcap`, `rdp.log` and
`conn.log` (fixed sequence numbers and timestamps, and Zeek's `-D`).
````

and the one Suricata rule used only to get an `alert` event into a fixture, `tests/fixtures/zeek/_handmade/fixture-only.rules`:

```text
# Used ONLY to make the eve.json fixture in this folder (so it contains one real
# Suricata 7.0.10 "alert" record). Not part of MaxGuard's rule set.
alert dns any any -> any any (msg:"MaxGuard fixture: DNS lookup of a lab.invalid name"; dns.query; content:"lab.invalid"; nocase; sid:9000001; rev:1;)
```

Then run the commands in the README's **Rebuild** section (and the ones in the RDP notes). They were run when the fixtures were made in planning.

**Step 5.** Prove the fixtures are reproducible: make them again into a temporary folder and compare (Zeek's logs must be identical; Suricata's `eve.json` has a random `flow_id`, which MaxGuard ignores):

```bash
FIXTURES_DIR=/tmp/fixture-check bash scripts/make_fixtures.sh > /dev/null
for d in tests/fixtures/zeek/[a-z]*/; do n=$(basename "$d"); diff -rq --exclude=eve.json "$d" "/tmp/fixture-check/$n" > /dev/null && echo "$n: identical" || echo "$n: DIFFERENT"; done
```

Expected output:

```text
cert_expired: identical
cert_self_signed: identical
cert_sha1: identical
cert_weak_key: identical
clean_tls13: identical
dns_lookup: identical
ftp: identical
imap: identical
plain_http: identical
plain_http_alt: identical
pop3: identical
telnet: identical
tls_weak_cipher: identical
tls_weak_version: identical
```

**Step 6.** Run the unit tests (nothing should break):

```bash
pytest -m "not integration" -q
```

Expected output:

```text
..............                                                                               [100%]
14 passed in 0.11s
```

**Step 7.** Commit, push, and open the pull request:

```bash
git add -A
git status          # only this task's files: nothing from .venv/, data/ or lab/captures/
git commit -m "test: Zeek and Suricata fixtures for every capture (KAR-02)"
git push -u origin HEAD
```

`HEAD` means "the branch I am on", so you do not have to retype its name. Open the repository on github.com: a yellow bar shows your branch with a **Compare & pull request** button. Click it, keep the title `test: Zeek and Suricata fixtures for every capture (KAR-02)`, fill in the template (paste the real output of the commands above under **How I tested it**), write `Closes #<issue number>` (this task's issue), and pick **@JWinborne1** under **Reviewers**. Click **Create pull request**, then fix anything CI or the reviewer finds with new commits on the same branch.

#### How to test

Every capture prints `identical`, and the unit tests still pass.

#### What you just did and why

Unit tests that need Docker and a capture are slow, so nobody runs them often. Running Zeek and Suricata once, committing their output, and testing against it gives fast tests with real tool output. Zeek's `-D` option is what makes the output identical on every run; without it every fixture would change every time and the tests could never compare exact IDs. Re-run the script whenever a capture, a Zeek script, or the Suricata config changes, and commit the result.

#### Pull request checklist

- [ ] `ruff check .` prints `All checks passed!`
- [ ] `pytest -m "not integration" -q` passes on your laptop
- [ ] The pull request title has the form `type: summary (TASK-ID)` and the body says `Closes #<issue number>`
- [ ] No secrets, passwords, email addresses, personal data, or captures from a real network (CLAUDE.md rule 6)
- [ ] Any new dependency has a row in `docs/DEPENDENCIES.md` with its license
- [ ] CI is green and your reviewer approved
- [ ] All captures print `identical`

### KAR-03: Integration tests: the real pipeline on every capture

**Due:** Week 2 (due Fri Oct 23) · **Milestone:** `W2 First end-to-end demo` · **Needs first:** [JAI-05](jaiden.md#jai-05-the-pipeline-one-function-from-input-to-report), [JAI-04](jaiden.md#jai-04-the-engine-image-and-the-compose-files), [KAR-02](#kar-02-test-fixtures-zeek-and-suricata-output-for-every-capture) · **Kind:** code, tested

**Issue labels:** `type:task` `phase:alpha` `owner:karthik` `area:testing` `critical-path`

#### Goal

Write expected-result files and an integration test that runs the real pipeline on every capture inside the engine image and checks that each capture produces exactly the findings it should, and nothing it should not. Add fast unit checks of Suricata's saved output: a Community ID on every record and a JA4 on every TLS client hello.

#### Prerequisites

JAI-05 (pipeline) and JAI-04 (engine image) are merged.

#### Steps

**Step 1.** Update `main` and create your branch for this task (one branch per task):

```bash
cd ~/projects/maxguard
source .venv/bin/activate
git checkout main && git pull
git checkout -b karthik/integration-tests
```

If `source .venv/bin/activate` fails, you have not made the virtual environment yet: do Week 0 section 0.11 first.

**Step 2.** Write one expected-result file per capture in `tests/expected/`, in the Fall 2026 format. `expected` names the rule the capture was recorded to trigger, on its port. `must_not_contain` lists the other rules of the same family: they read the same logs, so they are the likely misfires, and a new rule never forces you to edit every file. The two clean captures say `expect_no_findings` instead.

`tests/expected/telnet.json`:

```json
{
  "capture": "telnet.pcap",
  "expected": [
    {"rule_id": "cleartext.telnet", "dst_port": 23, "min_count": 1}
  ],
  "must_not_contain": ["cleartext.ftp", "cleartext.http", "cleartext.http_alt", "cleartext.imap", "cleartext.pop3", "rdp.standard_security"]
}
```

`tests/expected/ftp.json`:

```json
{
  "capture": "ftp.pcap",
  "expected": [
    {"rule_id": "cleartext.ftp", "dst_port": 21, "min_count": 1}
  ],
  "must_not_contain": ["cleartext.http", "cleartext.http_alt", "cleartext.imap", "cleartext.pop3", "cleartext.telnet", "rdp.standard_security"]
}
```

`tests/expected/pop3.json`:

```json
{
  "capture": "pop3.pcap",
  "expected": [
    {"rule_id": "cleartext.pop3", "dst_port": 110, "min_count": 1}
  ],
  "must_not_contain": ["cleartext.ftp", "cleartext.http", "cleartext.http_alt", "cleartext.imap", "cleartext.telnet", "rdp.standard_security"]
}
```

`tests/expected/imap.json`:

```json
{
  "capture": "imap.pcap",
  "expected": [
    {"rule_id": "cleartext.imap", "dst_port": 143, "min_count": 1}
  ],
  "must_not_contain": ["cleartext.ftp", "cleartext.http", "cleartext.http_alt", "cleartext.pop3", "cleartext.telnet", "rdp.standard_security"]
}
```

`tests/expected/plain_http.json`:

```json
{
  "capture": "plain_http.pcap",
  "expected": [
    {"rule_id": "cleartext.http", "dst_port": 80, "min_count": 1}
  ],
  "must_not_contain": ["cleartext.ftp", "cleartext.http_alt", "cleartext.imap", "cleartext.pop3", "cleartext.telnet", "rdp.standard_security"]
}
```

`tests/expected/plain_http_alt.json`:

```json
{
  "capture": "plain_http_alt.pcap",
  "expected": [
    {"rule_id": "cleartext.http_alt", "dst_port": 8080, "min_count": 1}
  ],
  "must_not_contain": ["cleartext.ftp", "cleartext.http", "cleartext.imap", "cleartext.pop3", "cleartext.telnet", "rdp.standard_security"]
}
```

`tests/expected/tls_weak_version.json`:

```json
{
  "capture": "tls_weak_version.pcap",
  "expected": [
    {"rule_id": "tls.weak_version", "dst_port": 4431, "min_count": 1}
  ],
  "must_not_contain": ["cert.expired", "cert.self_signed", "cert.sha1_signature", "cert.weak_key", "tls.weak_cipher"]
}
```

`tests/expected/tls_weak_cipher.json`:

```json
{
  "capture": "tls_weak_cipher.pcap",
  "expected": [
    {"rule_id": "tls.weak_cipher", "dst_port": 4432, "min_count": 1}
  ],
  "must_not_contain": ["cert.expired", "cert.self_signed", "cert.sha1_signature", "cert.weak_key", "tls.weak_version"]
}
```

`tests/expected/cert_expired.json`:

```json
{
  "capture": "cert_expired.pcap",
  "expected": [
    {"rule_id": "cert.expired", "dst_port": 4433, "min_count": 1}
  ],
  "must_not_contain": ["cert.self_signed", "cert.sha1_signature", "cert.weak_key", "tls.weak_cipher", "tls.weak_version"]
}
```

`tests/expected/cert_self_signed.json`:

```json
{
  "capture": "cert_self_signed.pcap",
  "expected": [
    {"rule_id": "cert.self_signed", "dst_port": 4437, "min_count": 1}
  ],
  "must_not_contain": ["cert.expired", "cert.sha1_signature", "cert.weak_key", "tls.weak_cipher", "tls.weak_version"]
}
```

`tests/expected/cert_sha1.json`:

```json
{
  "capture": "cert_sha1.pcap",
  "expected": [
    {"rule_id": "cert.sha1_signature", "dst_port": 4435, "min_count": 1}
  ],
  "must_not_contain": ["cert.expired", "cert.self_signed", "cert.weak_key", "tls.weak_cipher", "tls.weak_version"]
}
```

`tests/expected/cert_weak_key.json`:

```json
{
  "capture": "cert_weak_key.pcap",
  "expected": [
    {"rule_id": "cert.weak_key", "dst_port": 4434, "min_count": 1}
  ],
  "must_not_contain": ["cert.expired", "cert.self_signed", "cert.sha1_signature", "tls.weak_cipher", "tls.weak_version"]
}
```

`tests/expected/clean_tls13.json`:

```json
{
  "capture": "clean_tls13.pcap",
  "expected": [],
  "expect_no_findings": true
}
```

`tests/expected/dns_lookup.json`:

```json
{
  "capture": "dns_lookup.pcap",
  "expected": [],
  "expect_no_findings": true
}
```

**Step 3.** Create `tests/integration/test_pcaps.py`. Besides one test per expected file, `test_every_capture_has_an_expected_file` fails when someone adds a capture without an answer key, so no capture goes untested:

```python
"""Integration tests (Karthik, KAR-03): the real pipeline on every lab capture.

Each tests/expected/<capture>.json says which findings its capture must give.
The test runs maxguard.pipeline.analyze() on the capture with the real tools and
compares. Unit tests use saved logs, so only these tests notice when the way
MaxGuard *runs* the tools breaks. (That Suricata runs too is checked by
tests/integration/test_suricata_pipeline.py, added with JAK-05.)

They need Zeek, so they run inside the engine test image:
    docker run --rm --network none maxguard:test pytest -m integration -q
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from maxguard.pipeline import analyze

TESTS = Path(__file__).resolve().parents[1]
PCAPS = TESTS / "pcaps"
EXPECTED_FILES = sorted((TESTS / "expected").glob("*.json"))


def load(expected_file: Path) -> dict:
    return json.loads(expected_file.read_text())


def count_by_rule_and_port(findings: list[dict]) -> dict[tuple[str, int], int]:
    """(rule_id, dst_port) -> total count. Adds up counts in case several findings
    (for example from different client addresses) share a rule and a port."""
    counts: dict[tuple[str, int], int] = {}
    for finding in findings:
        key = (finding["rule_id"], finding["dst_port"])
        counts[key] = counts.get(key, 0) + finding["count"]
    return counts


@pytest.mark.integration
def test_every_capture_has_an_expected_file():
    # A capture without an expected file would never be tested.
    captures = sorted(p.name for p in PCAPS.glob("*.pcap"))
    assert captures == sorted(load(f)["capture"] for f in EXPECTED_FILES)


@pytest.mark.integration
@pytest.mark.parametrize("expected_file", EXPECTED_FILES, ids=lambda p: p.stem)
def test_capture_gives_the_expected_findings(expected_file, tmp_path):
    spec = load(expected_file)
    report = analyze(PCAPS / spec["capture"], tmp_path, explain=False)

    assert report["tools"]["zeek"] is True  # a capture always goes through Zeek
    counts = count_by_rule_and_port(report["findings"])
    for want in spec["expected"]:
        got = counts.get((want["rule_id"], want["dst_port"]), 0)
        assert got >= want["min_count"], f"missing {want}; found {counts}"
    found_rules = {rule_id for rule_id, _port in counts}
    for rule_id in spec.get("must_not_contain", []):
        assert rule_id not in found_rules, f"{rule_id} fired on {spec['capture']}"
    if spec.get("expect_no_findings", False):
        assert report["findings"] == []
```

Whether Suricata ran is checked later, in JAK-05: the pipeline starts running it there.

**Step 4.** Create `tests/unit/test_suricata_eve.py`. It reads the saved `eve.json` fixtures, so it runs with the fast unit tests. A record with a server name (SNI) proves Suricata parsed the client hello, because the name is only sent there, and that is the message JA4 is computed from. Zeek's TLS sessions are a second witness, so the JA4 check cannot pass by checking nothing:

```python
"""Suricata eve.json checks (Karthik, KAR-03): Community ID and JA4 for every capture.

The eve.json in each tests/fixtures/zeek/<capture>/ folder was written by
Suricata 7.0.10 with MaxGuard's settings (scripts/make_fixtures.sh). For each one:
1. every record has a Community ID, the key that links it to Zeek's records;
2. Zeek's conn.log has the same Community IDs (both tools must use seed 0);
3. every TLS record whose client hello Suricata saw has a JA4;
4. maxguard.events.normalize copies that JA4 onto the normalized event.

These read saved files only, so they run with the unit tests. To check fresh
output the same way, write it to another folder and point FIXTURES_DIR there
(the same variable scripts/make_fixtures.sh uses):
    FIXTURES_DIR=/tmp/fresh bash scripts/make_fixtures.sh
    FIXTURES_DIR=/tmp/fresh pytest tests/unit/test_suricata_eve.py -q
"""

from __future__ import annotations

import os
import re
from pathlib import Path

import pytest

from maxguard.adapters.base import read_log
from maxguard.events.normalize import normalize
from maxguard.ids import record_id

DEFAULT_FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "zeek"
FIXTURES = Path(os.environ.get("FIXTURES_DIR", DEFAULT_FIXTURES))
# One folder per lab capture. _handmade/ has no eve.json directly inside, so it is left out.
EVE_FOLDERS = sorted(p.parent for p in FIXTURES.glob("*/eve.json"))

# Community ID version 1: "1:" and the base64 text of a 20-byte SHA-1 hash (28 characters).
COMMUNITY_ID = re.compile(r"^1:[A-Za-z0-9+/]{27}=$")
# JA4 as Suricata writes it: 10 characters (protocol, TLS version, domain or IP,
# number of ciphers, number of extensions, first ALPN), then two 12-character hashes.
JA4 = re.compile(r"^[a-zA-Z0-9]{10}_[0-9a-f]{12}_[0-9a-f]{12}$")


def eve_records(folder: Path) -> list[dict]:
    return list(read_log(folder, "eve.json"))


def client_hellos(folder: Path) -> list[dict]:
    """The eve "tls" records whose client hello Suricata parsed. The server name (SNI)
    is sent only in the client hello, so a record with an "sni" proves Suricata saw it."""
    return [rec for rec in eve_records(folder)
            if rec["event_type"] == "tls" and rec["tls"].get("sni")]


def test_there_are_eve_files_to_check():
    assert EVE_FOLDERS, f"no <capture>/eve.json under {FIXTURES}"


@pytest.mark.parametrize("folder", EVE_FOLDERS, ids=lambda p: p.name)
def test_every_record_has_a_community_id(folder):
    for rec in eve_records(folder):
        assert COMMUNITY_ID.match(rec.get("community_id", "")), rec["event_type"]


@pytest.mark.parametrize("folder", EVE_FOLDERS, ids=lambda p: p.name)
def test_zeek_logged_the_same_community_ids(folder):
    zeek_ids = {rec.get("community_id") for rec in read_log(folder, "conn.log")}
    for rec in eve_records(folder):
        assert rec["community_id"] in zeek_ids, rec["event_type"]


@pytest.mark.parametrize("folder", EVE_FOLDERS, ids=lambda p: p.name)
def test_every_client_hello_has_a_ja4(folder):
    hellos = client_hellos(folder)
    for rec in hellos:
        assert JA4.match(rec["tls"].get("ja4", "")), rec["tls"]
    # Zeek is a second witness, so this test cannot pass by checking nothing: every
    # TLS session in Zeek's ssl.log must be one of the client hellos above (every
    # lab client sends a server name). normalize() gives Zeek's TLS events the
    # Community ID of their connection.
    zeek_sessions = {e["community_id"] for e in normalize(folder, sensor_id="pcap")
                     if e["source"] == "zeek" and e["kind"] == "tls"}
    assert zeek_sessions == {rec["community_id"] for rec in hellos}


@pytest.mark.parametrize("folder", EVE_FOLDERS, ids=lambda p: p.name)
def test_normalize_puts_the_ja4_on_the_event(folder):
    events = {e["event_id"]: e for e in normalize(folder, sensor_id="pcap")}
    for rec in client_hellos(folder):
        event = events[record_id("eve.json", rec)]  # event_id is the record's ID
        assert event["kind"] == "tls"
        assert event["ja4"] == rec["tls"].get("ja4", "")  # a missing JA4 fails the test above
```

**Step 5.** Run it:

```bash
pytest tests/unit/test_suricata_eve.py -q
```

Expected output:

```text
.........................................................                                    [100%]
57 passed in 0.08s
```

**Step 6.** Build the test image and run the integration tests in it with networking off:

```bash
docker build -f docker/Dockerfile --target test -t maxguard:test .
docker run --rm --network none maxguard:test pytest -m integration -q
```

Expected output:

```text
...............                                                          [100%]
15 passed, 340 deselected in 8.57s
```

*Run in planning inside `zeek/zeek:9.0.0` with MaxGuard's Python packages added, because the engine image build needs Debian's package servers (JAI-04). Zeek ran for real on every capture.*

**Step 7.** Commit, push, and open the pull request:

```bash
git add -A
git status          # only this task's files: nothing from .venv/, data/ or lab/captures/
git commit -m "test: integration tests on every lab capture (KAR-03)"
git push -u origin HEAD
```

`HEAD` means "the branch I am on", so you do not have to retype its name. Open the repository on github.com: a yellow bar shows your branch with a **Compare & pull request** button. Click it, keep the title `test: integration tests on every lab capture (KAR-03)`, fill in the template (paste the real output of the commands above under **How I tested it**), write `Closes #<issue number>` (this task's issue), and pick **@JWinborne1** under **Reviewers**. Click **Create pull request**, then fix anything CI or the reviewer finds with new commits on the same branch.

#### How to test

`pytest -m integration -q` passes inside the test image (15 tests: one per capture, plus the one that checks every capture has an expected file), and the Suricata checks pass with the unit tests.

#### What you just did and why

Unit tests use saved fixtures, so they cannot notice when the way MaxGuard *runs* Zeek or Suricata breaks (a missing script, a wrong option, a new tool version). Integration tests run the real tools on the real captures, offline, the same way users will. In planning, leaving `cleartext.zeek` out of the Zeek command made exactly the Telnet, POP3 and IMAP tests fail, and nothing else. The `must_not_contain` lists catch a rule that starts firing where it should not.

#### Pull request checklist

- [ ] `ruff check .` prints `All checks passed!`
- [ ] `pytest -m "not integration" -q` passes on your laptop
- [ ] The pull request title has the form `type: summary (TASK-ID)` and the body says `Closes #<issue number>`
- [ ] No secrets, passwords, email addresses, personal data, or captures from a real network (CLAUDE.md rule 6)
- [ ] Any new dependency has a row in `docs/DEPENDENCIES.md` with its license
- [ ] CI is green and your reviewer approved
- [ ] One expected file per capture
- [ ] The integration tests pass in the test image

### KAR-04: CI runs the integration tests, plus a determinism test

**Due:** Week 3 (due Fri Oct 30) · **Milestone:** `W3 API and alert queue` · **Needs first:** [KAR-03](#kar-03-integration-tests-the-real-pipeline-on-every-capture) · **Kind:** code, written

**Issue labels:** `type:task` `phase:alpha` `owner:karthik` `area:testing` `area:release`

> **Written, not fully run.** The files in this task were written during planning, but part of them could not be run there (each such step says why). Your run is the first real one: if anything differs, fix this file in your pull request.

#### Goal

Add an `integration` job to CI that builds the engine image and runs the integration tests in it with networking off, and add a test that analyzes every capture twice and checks the two reports are identical.

#### Prerequisites

KAR-03 is merged.

#### Steps

**Step 1.** Update `main` and create your branch for this task (one branch per task):

```bash
cd ~/projects/maxguard
source .venv/bin/activate
git checkout main && git pull
git checkout -b karthik/ci-integration
```

If `source .venv/bin/activate` fails, you have not made the virtual environment yet: do Week 0 section 0.11 first.

**Step 2.** Replace `.github/workflows/ci.yml` with the version that has the second job:

```yaml
# Runs on every pull request and on every push to main.
# "test": lint + unit tests on Python 3.11 (fast, no Docker).
# "integration": builds the engine image and runs the integration tests inside
# it with networking switched off, the same way MaxGuard runs for real.
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

  integration:
    needs: test
    runs-on: ubuntu-latest
    timeout-minutes: 30
    steps:
      - uses: actions/checkout@v7

      - name: Build the engine image
        run: docker build -f docker/Dockerfile -t maxguard:ci .

      # Same Dockerfile, "test" stage: the engine plus pytest and the tests
      # folder. Reuses the cached engine layers from the step above.
      - name: Build the test image
        run: docker build -f docker/Dockerfile --target test -t maxguard:ci-test .

      - name: Check the engine image starts offline
        run: |
          docker run --rm --network none maxguard:ci zeek --version
          docker run --rm --network none maxguard:ci suricata -V
          # MaxGuard needs JA4 (docs/ARCHITECTURE.md section 16): fail if this build lacks it.
          docker run --rm --network none maxguard:ci sh -c 'suricata --build-info | grep -w HAVE_JA4'
          docker run --rm --network none maxguard:ci maxguard --help

      # pytest is already inside the image, so the tests run with no network at all.
      - name: Integration tests (no network)
        run: docker run --rm --network none maxguard:ci-test pytest -m integration -q
```

*Written in planning; its first real run is your pull request.* Check the action versions (`actions/checkout`, `actions/setup-python`) against their GitHub releases pages before merging. The `HAVE_JA4` line fails the job if the image's Suricata was built without JA4: Suricata 7.0.10 and 8.0.7 from `jasonish/suricata` list it, but Debian's package could not be checked in planning, so the first CI run answers that question.

**Step 3.** Create `tests/integration/test_determinism.py`. It analyzes every capture twice, into two *different* folders (so a folder path that leaks into the report fails too), and when the reports differ, `differences()` names the exact value, for example `report['events'][0]['uid']: 'CVMEph...' != 'CeUBb0...'`. The small test of that helper is not marked, so it also runs with the unit tests:

```python
"""Determinism test (Karthik, KAR-04): the same capture always gives the same report.

CLAUDE.md rule 2 with the real tools: analyze() runs twice on every capture, in
two different temporary folders, and the two report dicts must be equal. The
folders differ on purpose, so a folder path that leaks into the report fails too.
Zeek's -D option and record IDs that ignore Suricata's random flow_id are what
make this pass (docs/ARCHITECTURE.md section 7).

The determinism test needs Zeek, so it runs inside the engine test image
(pytest -m integration). The small test of the differences() helper needs
nothing, so it is not marked and also runs with the unit tests.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from maxguard.pipeline import analyze

PCAPS = sorted((Path(__file__).resolve().parents[1] / "pcaps").glob("*.pcap"))


def differences(first: object, second: object, where: str = "report") -> list[str]:
    """Every place where two reports differ, for example
    report['events'][3]['uid']: 'CAbc' != 'CXyz'. An empty list means identical."""
    if isinstance(first, dict) and isinstance(second, dict):
        found = []
        for key in sorted(set(first) | set(second)):
            found += differences(first.get(key), second.get(key), f"{where}[{key!r}]")
        return found
    if isinstance(first, list) and isinstance(second, list) and len(first) == len(second):
        found = []
        for index, (a, b) in enumerate(zip(first, second, strict=True)):
            found += differences(a, b, f"{where}[{index}]")
        return found
    return [] if first == second else [f"{where}: {first!r} != {second!r}"]


@pytest.mark.integration
@pytest.mark.parametrize("pcap", PCAPS, ids=lambda p: p.stem)
def test_two_runs_give_the_same_report(pcap, tmp_path):
    first = analyze(pcap, tmp_path / "first", explain=False)
    second = analyze(pcap, tmp_path / "second", explain=False)

    # Show at most 10 differences: the first one usually names the culprit.
    assert first == second, "\n".join(differences(first, second)[:10])


def test_differences_names_the_value_that_changed():
    # A plain unit test of the helper above, so its messages can be trusted.
    first = {"events": [{"uid": "CAbc", "ts": 1.0}], "tools": {"zeek": True}}
    second = {"events": [{"uid": "CXyz", "ts": 1.0}], "tools": {"zeek": True}}
    assert differences(first, first) == []
    assert differences(first, second) == ["report['events'][0]['uid']: 'CAbc' != 'CXyz'"]
    assert differences({"a": [1]}, {"a": [1, 2]}) == ["report['a']: [1] != [1, 2]"]
```

**Step 4.** Run the integration tests again:

```bash
docker build -f docker/Dockerfile --target test -t maxguard:test .
docker run --rm --network none maxguard:test pytest -m integration -q
```

Expected output:

```text
..............................                                           [100%]
30 passed, 443 deselected in 29.33s
```

*Run in planning inside `zeek/zeek:9.0.0` with MaxGuard's Python packages added (see KAR-03). Running Zeek without `-D` made the Telnet determinism test fail on the connection IDs, which is the mistake this test exists to catch.*

**Step 5.** Open the pull request and watch both jobs. In the `integration` job's log, check that the tests ran with `--network none`.

**Step 6.** Commit, push, and open the pull request:

```bash
git add -A
git status          # only this task's files: nothing from .venv/, data/ or lab/captures/
git commit -m "ci: integration job in the engine image, determinism test (KAR-04)"
git push -u origin HEAD
```

`HEAD` means "the branch I am on", so you do not have to retype its name. Open the repository on github.com: a yellow bar shows your branch with a **Compare & pull request** button. Click it, keep the title `ci: integration job in the engine image, determinism test (KAR-04)`, fill in the template (paste the real output of the commands above under **How I tested it**), write `Closes #<issue number>` (this task's issue), and pick **@JWinborne1** under **Reviewers**. Click **Create pull request**, then fix anything CI or the reviewer finds with new commits on the same branch.

#### How to test

Both CI jobs are green on your pull request. After merging, ask Jaiden to add `integration` to the required checks of the `main-protection` ruleset.

#### What you just did and why

Running the integration tests on every pull request means nobody can merge a change that breaks the real pipeline, even if all unit tests pass. Running them with the network off proves the engine works offline (CLAUDE.md rule 1), and the determinism test guards rule 2 with the real tools, not only with fixtures.

#### Pull request checklist

- [ ] `ruff check .` prints `All checks passed!`
- [ ] `pytest -m "not integration" -q` passes on your laptop
- [ ] The pull request title has the form `type: summary (TASK-ID)` and the body says `Closes #<issue number>`
- [ ] No secrets, passwords, email addresses, personal data, or captures from a real network (CLAUDE.md rule 6)
- [ ] Any new dependency has a row in `docs/DEPENDENCIES.md` with its license
- [ ] CI is green and your reviewer approved
- [ ] The `integration` job is green
- [ ] Jaiden added it to the required checks

### KAR-05: Release-candidate test with an outside tester

**Due:** Week 6 (due Fri Nov 20) · **Milestone:** `W6 Release candidate` · **Needs first:** [JAI-09](jaiden.md#jai-09-release-workflow-and-v20-alpha-rc1), [JON-05](jonattan.md#jon-05-offline-bundle-install-maxguard-on-a-machine-with-no-internet) · **Kind:** process

**Issue labels:** `type:task` `phase:alpha` `owner:karthik` `area:testing` `area:release` `critical-path`

#### Goal

Run the alpha acceptance test (`docs/roadmap/README.md`) on `v2.0-alpha-rc1` yourself, then with someone outside the team, on a computer that has never run MaxGuard, and turn every problem into an issue.

#### Prerequisites

JAI-09 (`v2.0-alpha-rc1` is tagged) and JON-05 (offline bundle) are merged.

#### Steps

**Step 1.** Write `docs/testing/rc-checklist.md`: the acceptance test steps as a checklist with a result column (pass, fail, notes), plus the exact versions under test.

**Step 2.** Run it yourself first, with the network unplugged at step 4.

**Step 3.** Run it with the outside tester (a classmate not on the team). Do not help unless they are stuck for more than 10 minutes; write down every place they hesitated.

**Step 4.** Open one issue per problem with the label `type:bug` and the milestone `W8 v2.0-alpha`. Commit the filled-in checklist.

**Step 5.** Commit, push, and open the pull request:

```bash
git add -A
git status          # only this task's files: nothing from .venv/, data/ or lab/captures/
git commit -m "docs: release-candidate test results (KAR-05)"
git push -u origin HEAD
```

`HEAD` means "the branch I am on", so you do not have to retype its name. Open the repository on github.com: a yellow bar shows your branch with a **Compare & pull request** button. Click it, keep the title `docs: release-candidate test results (KAR-05)`, fill in the template (paste the real output of the commands above under **How I tested it**), write `Closes #<issue number>` (this task's issue), and pick **@JWinborne1** under **Reviewers**. Click **Create pull request**, then fix anything CI or the reviewer finds with new commits on the same branch.

#### How to test

The checklist is filled in for both runs, and every failure has an issue.

#### What you just did and why

The team knows MaxGuard too well to notice what is confusing. An outside tester on a clean machine finds the missing step, the unclear error, and the assumption that only works on the developers' laptops, while there is still time to fix them.

#### Pull request checklist

- [ ] `ruff check .` prints `All checks passed!`
- [ ] `pytest -m "not integration" -q` passes on your laptop
- [ ] The pull request title has the form `type: summary (TASK-ID)` and the body says `Closes #<issue number>`
- [ ] No secrets, passwords, email addresses, personal data, or captures from a real network (CLAUDE.md rule 6)
- [ ] Any new dependency has a row in `docs/DEPENDENCIES.md` with its license
- [ ] CI is green and your reviewer approved
- [ ] Every failure has an issue

## Spring 2027: v2.0

### KAR-06: End-to-end test of the live sensor on the lab

**Due:** Spring S1-S4 (due Fri Feb 12, 2027) · **Milestone:** `S1-S4 Live sensor` · **Needs first:** [JAK-07](jakub.md#jak-07-live-sensor-capture-rotation-and-shipping-to-the-console) · **Kind:** code, tested

**Issue labels:** `type:task` `phase:spring` `owner:karthik` `area:testing` `area:sensor` `needs-hardware`

> **Needs hardware.** Steps that use the Raspberry Pi, the switch or other devices were not run during planning; they are marked *not run — verify on hardware*.

#### Goal

Prove the live path works end to end on the reference lab: generate known traffic, and check that the expected alerts appear on the console within the shipping interval, with the right devices attributed.

#### Prerequisites

JAK-07 (live sensor) is merged and running on the lab.

#### Steps

**Step 1.** Update `main` and create your branch for this task (one branch per task):

```bash
cd ~/projects/maxguard
source .venv/bin/activate
git checkout main && git pull
git checkout -b karthik/live-e2e
```

If `source .venv/bin/activate` fails, you have not made the virtual environment yet: do Week 0 section 0.11 first.

**Step 2.** Create `scripts/live_check.sh`:

```bash
#!/usr/bin/env bash
# Live-sensor end-to-end check (Karthik, KAR-06).
#
# Run it on the MaxGuard console: its API answers only on 127.0.0.1 (sensors reach
# a separate ingest-only port). It makes one plain-HTTP request (port 80) and one
# Telnet connection (port 23) to a test service on another lab machine, then
# asks the console for its alerts every minute, for up to 30 minutes,
# until a cleartext.http and a cleartext.telnet alert show traffic seen after the
# start. It prints how long each alert took.
#
# Usage:    bash scripts/live_check.sh <console URL> <lab service IPv4 address>
# Example:  bash scripts/live_check.sh http://127.0.0.1:8000 192.168.50.30
#
# The sensor sees only traffic that crosses the mirrored switch port (the cable to
# the router, docs/HARDWARE.md section 1). Plug the test service's machine into a
# LAN port of the router itself for this test, so the probes cross that cable.
#
# Settings (environment variables), mainly so a test can finish in seconds:
#   LIVE_CHECK_POLL_SECONDS     seconds between two looks at the console (default 60)
#   LIVE_CHECK_TIMEOUT_SECONDS  give up after this many seconds (default 1800 = 30 minutes)
#
# Exit codes: 0 both alerts appeared; 1 a probe or the console failed, or an
# alert did not appear in time; 2 wrong arguments or an address outside the lab.
#
# Needs: bash, python3, and curl with Telnet support ("curl --version" lists
# telnet under Protocols).
set -euo pipefail

POLL_SECONDS="${LIVE_CHECK_POLL_SECONDS:-60}"
TIMEOUT_SECONDS="${LIVE_CHECK_TIMEOUT_SECONDS:-1800}"

usage() {
  echo "usage: bash scripts/live_check.sh <console URL> <lab service IPv4 address>" >&2
  echo "example: bash scripts/live_check.sh http://127.0.0.1:8000 192.168.50.30" >&2
  exit 2
}

# Only lab machines may be probed (CLAUDE.md rule 4: never touch hosts you do not
# own). Allowed: the private ranges of RFC 1918, which home and office networks
# use (10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16), and the documentation ranges
# of RFC 5737 (192.0.2.0/24, 198.51.100.0/24, 203.0.113.0/24), which are never
# routed on the internet and are the example addresses in MaxGuard's docs. Any
# other address could be someone else's computer. Host names are refused because
# a name can point anywhere; leading zeros are refused because some programs
# read "010" as octal (8).
is_lab_address() {
  local octet='(0|[1-9][0-9]{0,2})'
  [[ "$1" =~ ^$octet\.$octet\.$octet\.$octet$ ]] || return 1
  local a="${BASH_REMATCH[1]}" b="${BASH_REMATCH[2]}" c="${BASH_REMATCH[3]}" d="${BASH_REMATCH[4]}"
  (( a <= 255 && b <= 255 && c <= 255 && d <= 255 )) || return 1
  (( a == 10 )) && return 0
  (( a == 172 && b >= 16 && b <= 31 )) && return 0
  (( a == 192 && b == 168 )) && return 0
  (( a == 192 && b == 0 && c == 2 )) && return 0
  (( a == 198 && b == 51 && c == 100 )) && return 0
  (( a == 203 && b == 0 && c == 113 )) && return 0
  return 1
}

# Every curl call uses --noproxy '*': with a web proxy set (http_proxy), curl
# would send the request to the proxy, so the sensor would see traffic to the
# proxy instead of the lab service, and the console might not be reachable.
fetch_alerts() {
  curl --silent --show-error --fail --max-time 30 --noproxy '*' "$1/api/alerts?limit=1000"
}

# Succeeds when the alert list (JSON on stdin) has an alert for rule $1 whose
# last_seen is at or after $2. Both are Unix seconds; last_seen is when the sensor
# saw the traffic, so the sensor's and this machine's clocks must agree (NTP).
alert_seen_since() {
  python3 -c '
import json, sys
rule, start = sys.argv[1], float(sys.argv[2])
alerts = json.load(sys.stdin)
sys.exit(0 if any(a["rule_id"] == rule and a["last_seen"] >= start for a in alerts) else 1)
' "$1" "$2"
}

check_console() {
  local alerts
  if ! alerts="$(fetch_alerts "$1")"; then
    echo "error: cannot read $1/api/alerts: is the console running?" >&2
    exit 1
  fi
  if ! python3 -c 'import json, sys; assert isinstance(json.load(sys.stdin), list)' \
      <<< "$alerts" 2> /dev/null; then
    echo "error: $1/api/alerts did not return a JSON list: is this a MaxGuard console?" >&2
    exit 1
  fi
}

probe_http() {
  # Any HTTP answer is fine (even 404): what matters is the unencrypted request.
  if ! curl --silent --show-error --max-time 10 --noproxy '*' --output /dev/null "http://$1/"; then
    echo "error: no HTTP answer from $1 port 80: is the test service running?" >&2
    exit 1
  fi
  echo "sent: plain HTTP request to $1 port 80"
}

probe_telnet() {
  # curl speaks Telnet too: type the lab user name, then "exit" so the service hangs up.
  local reply status=0
  reply="$(printf 'labuser\r\nexit\r\n' \
    | curl --silent --max-time 10 --noproxy '*' "telnet://$1:23")" || status=$?
  # A service that keeps asking for a password stops only at curl's time limit
  # (exit code 28); that is fine. What counts is that the service answered:
  # MaxGuard only reports a Telnet session in which the server sent something.
  if [[ -z "$reply" ]]; then
    echo "error: no Telnet answer from $1 port 23 (curl exit code $status):" \
      "is the test service running?" >&2
    exit 1
  fi
  echo "sent: Telnet session to $1 port 23"
}

minutes_and_seconds() {
  echo "$(( $1 / 60 )) min $(( $1 % 60 )) s"
}

main() {
  [[ $# -eq 2 ]] || usage
  local console="${1%/}" service="$2"
  [[ "$console" =~ ^https?:// ]] || usage
  if ! [[ "$POLL_SECONDS" =~ ^[1-9][0-9]*$ && "$TIMEOUT_SECONDS" =~ ^[1-9][0-9]*$ ]]; then
    echo "error: LIVE_CHECK_POLL_SECONDS and LIVE_CHECK_TIMEOUT_SECONDS must be" \
      "whole numbers above 0" >&2
    exit 2
  fi
  if ! is_lab_address "$service"; then
    echo "refused: $service is not a lab address (allowed: 10.0.0.0/8, 172.16.0.0/12," \
      "192.168.0.0/16 and the documentation ranges 192.0.2.0/24, 198.51.100.0/24," \
      "203.0.113.0/24; IPv4 numbers only)" >&2
    exit 2
  fi

  check_console "$console"  # fail now, not after 30 minutes of waiting
  local start
  start="$(date +%s)"
  probe_http "$service"
  probe_telnet "$service"
  echo "waiting for the alerts (checking every ${POLL_SECONDS} s, for up to" \
    "$(minutes_and_seconds "$TIMEOUT_SECONDS"))"

  local http_took="" telnet_took="" alerts now
  while true; do
    now="$(date +%s)"
    # A console that is busy or restarting is not a failure: try again next time.
    if alerts="$(fetch_alerts "$console")"; then
      if [[ -z "$http_took" ]] && alert_seen_since cleartext.http "$start" <<< "$alerts"; then
        http_took=$(( now - start ))
        echo "cleartext.http alert after $(minutes_and_seconds "$http_took")"
      fi
      if [[ -z "$telnet_took" ]] && alert_seen_since cleartext.telnet "$start" <<< "$alerts"; then
        telnet_took=$(( now - start ))
        echo "cleartext.telnet alert after $(minutes_and_seconds "$telnet_took")"
      fi
    else
      echo "warning: could not read the alerts this time; trying again" >&2
    fi
    if [[ -n "$http_took" && -n "$telnet_took" ]]; then
      echo "PASS: both alerts appeared"
      exit 0
    fi
    if (( now - start >= TIMEOUT_SECONDS )); then
      [[ -n "$http_took" ]] || echo "FAIL: no cleartext.http alert" >&2
      [[ -n "$telnet_took" ]] || echo "FAIL: no cleartext.telnet alert" >&2
      echo "after $(minutes_and_seconds "$TIMEOUT_SECONDS")" >&2
      exit 1
    fi
    sleep "$POLL_SECONDS"
  done
}

main "$@"
```

Three choices to notice. It refuses any address outside the lab ranges, because probing someone else's machine is never acceptable (CLAUDE.md rule 4). It uses `curl` for the Telnet probe too, so no Telnet client is needed. And it compares the alert's `last_seen` (the sensor's clock) with the console's clock, so both must keep the right time (NTP); a Raspberry Pi without a clock battery has the wrong time until it reaches a time server.

**Step 3.** Check the script with ShellCheck, and see it refuse an address outside the lab before it contacts anything:

```bash
docker run --rm -v "$PWD/scripts:/mnt:ro" koalaman/shellcheck:v0.11.0 /mnt/live_check.sh && echo "shellcheck: no findings"
bash scripts/live_check.sh http://127.0.0.1:8000 100.64.0.1
```

Expected output:

```text
shellcheck: no findings
refused: 100.64.0.1 is not a lab address (allowed: 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16 and the documentation ranges 192.0.2.0/24, 198.51.100.0/24, 203.0.113.0/24; IPv4 numbers only)
```

*The second command exits with 2: `100.64.0.1` is not a lab address.*

**Step 4.** On another lab machine, start a test service with Telnet and HTTP. The lab server from KAR-01 is one: `docker run -d --rm --name lab-service -p 23:23 -p 80:80 lab-server`. It is insecure on purpose: run it only on the lab network, and stop it (`docker stop lab-service`) after the test. Plug that machine into a LAN port of the **router** for the test, not into the switch or the mesh Wi-Fi: the sensor sees only traffic that crosses the cable on switch port 1 (`docs/HARDWARE.md` section 1), and traffic between two devices behind the switch never does.

**Step 5.** On the console machine (on the mesh Wi-Fi), run the check against the console and the lab service. The console's API answers only on `127.0.0.1`; sensors use the separate ingest port:

```bash
bash scripts/live_check.sh http://127.0.0.1:8000 192.168.50.30
```

Expected output (not run in planning):

```text
sent: plain HTTP request to 172.19.0.2 port 80
sent: Telnet session to 172.19.0.2 port 23
waiting for the alerts (checking every 1 s, for up to 0 min 20 s)
cleartext.telnet alert after 0 min 2 s
cleartext.http alert after 0 min 4 s
PASS: both alerts appeared
```

*Not run on the lab: verify on hardware. This output is from planning, where the test service was the lab server in a container (172.19.0.2), a fake console answered `/api/alerts`, and `LIVE_CHECK_POLL_SECONDS=1` and `LIVE_CHECK_TIMEOUT_SECONDS=20` shortened the waits. On the lab, expect up to one 15-minute interval plus the analysis time.*

**Step 6.** Run it three times on different days and record how long each alert took in `docs/testing/live-sensor.md`.

**Step 7.** Commit, push, and open the pull request:

```bash
git add -A
git status          # only this task's files: nothing from .venv/, data/ or lab/captures/
git commit -m "test: live-sensor end-to-end check on the lab (KAR-06)"
git push -u origin HEAD
```

`HEAD` means "the branch I am on", so you do not have to retype its name. Open the repository on github.com: a yellow bar shows your branch with a **Compare & pull request** button. Click it, keep the title `test: live-sensor end-to-end check on the lab (KAR-06)`, fill in the template (paste the real output of the commands above under **How I tested it**), write `Closes #<issue number>` (this task's issue), and pick **@JWinborne1** under **Reviewers**. Click **Create pull request**, then fix anything CI or the reviewer finds with new commits on the same branch.

#### How to test

All three runs show both alerts within one shipping interval plus the analysis time.

#### What you just did and why

Each piece of the live path is unit-tested, but the joints between them (rotation, shipping, ingest, analysis, dashboard) only break on real hardware. A repeatable end-to-end check catches those breaks before the v2.0 release.

#### Pull request checklist

- [ ] `ruff check .` prints `All checks passed!`
- [ ] `pytest -m "not integration" -q` passes on your laptop
- [ ] The pull request title has the form `type: summary (TASK-ID)` and the body says `Closes #<issue number>`
- [ ] No secrets, passwords, email addresses, personal data, or captures from a real network (CLAUDE.md rule 6)
- [ ] Any new dependency has a row in `docs/DEPENDENCIES.md` with its license
- [ ] CI is green and your reviewer approved
- [ ] Only lab machines were contacted
- [ ] The test service was stopped after the test
