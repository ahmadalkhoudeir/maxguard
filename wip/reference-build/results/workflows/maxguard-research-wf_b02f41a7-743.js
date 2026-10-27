export const meta = {
  name: 'maxguard-research',
  description: 'Research and verify facts for HARDWARE.md, DEPENDENCIES.md and the spring calendar',
  phases: [
    { title: 'Research', detail: 'parallel fact-finding with primary sources' },
    { title: 'Verify', detail: 'independent skeptics check each draft' },
  ],
}
const OUT = args.out
const FACTS = {
  type: 'object',
  properties: {
    topic: { type: 'string' },
    facts: { type: 'array', items: { type: 'object', properties: {
      claim: { type: 'string' }, source_url: { type: 'string' }, source_title: { type: 'string' },
      confidence: { type: 'string', enum: ['verified', 'likely', 'unverified'] }, notes: { type: 'string' } },
      required: ['claim', 'source_url', 'confidence'] } },
    draft_markdown: { type: 'string' },
    open_questions: { type: 'array', items: { type: 'string' } },
  },
  required: ['topic', 'facts', 'draft_markdown', 'open_questions'],
}
const RULES = `Rules: use web search (and web fetch when a site is reachable) to verify EVERY claim from a primary
source (manufacturer manual/datasheet/FAQ, official project docs, license file). Record the URL for each fact.
Mark anything you could not verify as unverified — never invent menu names, default IPs, prices, or flags.
Write for a junior CCSU student: exact clicks/commands, expected result, why it matters.
This is for a PUBLIC repository: no personal data, no real home-network details (use RFC 1918 example addresses
like 192.168.50.x and say they are examples). You may run harmless local commands to check syntax (bash -n, docker
compose config, docker run of public images) but there is no Raspberry Pi or switch here: anything hardware-specific
must be labeled "not run — verify on hardware".`

const TOPICS = [
  { key: 'switch-mirror', prompt: `TP-Link TL-SG105E (5-port Gigabit Easy Smart switch): hardware versions (V3/V4/V5/V6...) and
how each is managed (web UI vs Easy Smart Configuration Utility), default management IP and login, how to change the
password and management IP, exact steps for Port Mirroring (menu path, mirroring port vs mirrored port, ingress/egress),
limits (one mirroring port? can the mirroring port still pass normal traffic?), firmware update location, and the
"mirror the router uplink port 1 (ingress+egress) to port 5" setup from our topology. Also: does mirroring work at full
gigabit, what happens when combined traffic > 1 Gbps. Also confirm whether the Dualcomm ETAP-2003 aggregates both
directions onto one monitor port (datasheet) and its price range.` },
  { key: 'router-mesh', prompt: `(1) TP-Link Archer AX4400 router: how to turn its Wi-Fi off, confirm DHCP server settings, see the
DHCP client list, set a DHCP reservation, and whether it offers any local firewall/blocking API or only web UI features
(Access Control / Parental Controls / IP-MAC binding). (2) Consumer mesh Wi-Fi in bridge / access point mode: generic
steps plus verified exact steps for three common brands (TP-Link Deco "Access Point mode", eero "Bridge mode", Google Nest
Wifi/Google Wifi "bridge mode") — cite each vendor's help page; explain why bridge mode matters (double NAT would hide
devices behind the mesh's NAT). (3) Why Wi-Fi-to-Wi-Fi traffic on the same mesh is invisible to the mirror port.` },
  { key: 'pi-os-docker', prompt: `Raspberry Pi 5 sensor setup: (1) Raspberry Pi OS 64-bit current release as of Oct 2026 (Bookworm or Trixie?
cite raspberrypi.com), flashing with Raspberry Pi Imager incl. OS customisation (hostname, user, SSH key, no Wi-Fi),
first boot, apt full-upgrade. (2) Networking with NetworkManager (default on Pi OS Bookworm+): give the USB RTL8153
adapter a static management IP or DHCP reservation, and configure the onboard eth0 as the capture interface with NO IP
address (ipv4.method disabled, ipv6.method disabled/ignore), up in promiscuous mode, and disable offloads (ethtool -K
gro off lro off) — verify the exact nmcli commands and the ethtool package; explain why offloads matter for Zeek/Suricata.
(3) Install Docker Engine on Raspberry Pi OS 64-bit (Debian-based arm64): official docs method (apt repository for
Debian), docker group, verify with docker run hello-world. (4) USB 3 SSD for /data: mount by UUID in /etc/fstab with
nofail, why (SD wear). (5) Raspberry Pi 5 power: 27W USB-C PSU needed for USB peripherals (cite). (6) Pi 5 cooling:
Active Cooler. (7) Check Docker Hub that zeek/zeek:9.0.0, jasonish/suricata:7.0.10 and nicolaka/netshoot have arm64
images (use https://hub.docker.com/v2/repositories/<repo>/tags/<tag> JSON) and try to run the arm64 zeek image under
emulation here: docker run --privileged --rm tonistiigi/binfmt --install arm64, then docker run --rm --platform linux/arm64
zeek/zeek:9.0.0 zeek --version — record exact output or the failure.` },
  { key: 'mirror-test', prompt: `Design a test that PROVES the mirror port works, for docs/HARDWARE.md, runnable by a student:
(1) On the Pi: sudo tcpdump -i eth0 -nn -c 50 (and -e to show MACs) while a phone on the mesh Wi-Fi loads a website: expect
packets with the phone's internal IP in BOTH directions; show how to check both directions (count packets src vs dst);
(2) a DNS check: dig/nslookup from a laptop and see the query and response on the Pi; (3) a DHCP check: reconnect a device
and see DHCP DISCOVER/REQUEST; (4) a throughput/loss check: iperf3 between two wired devices across the mirrored link and
compare with Zeek's capture_loss.log and Suricata's stats (capture.kernel_drops) — explain what each means; (5) a negative
test: unplug the mirror config and show the Pi sees only broadcast. Verify every command/flag (tcpdump man page, iperf3
docs, Zeek capture_loss.log fields, Suricata stats field names) and cite. Run the tcpdump/iperf3 parts in Docker here
where possible (e.g., two containers on a docker network with a third sharing netns running tcpdump) to show realistic
expected output, and say which outputs are from the simulation.` },
  { key: 'licenses', prompt: `For docs/DEPENDENCIES.md, verify the license of each dependency from its primary source
(PyPI JSON https://pypi.org/pypi/<name>/json -> info.license / license_expression / classifiers, and the project's LICENSE
file on GitHub when PyPI is ambiguous). Python: pyyaml, requests, fastapi, starlette, pydantic, pydantic-core, uvicorn,
jinja2, markupsafe, python-multipart, duckdb, cryptography, cffi, httpx, httpcore, anyio, idna, certifi (MPL-2.0!),
charset-normalizer, urllib3, h11, sniffio, typing-extensions, annotated-types, click, pytest, ruff, pyftpdlib (lab only),
playwright (dev only, if used). Also get transitive runtime deps of the runtime set: run in a temp venv
"pip install pyyaml requests fastapi uvicorn jinja2 python-multipart duckdb cryptography" then "pip list" and
"pip show" each to list everything that actually gets installed, with versions and licenses. Non-Python: Zeek (BSD-3-Clause,
COPYING), Suricata (GPL-2.0-only; we run it as a separate program, not linked), Ollama (MIT), htmx 2.0.11 (0BSD),
goflow2 (BSD-3?), nicolaka/netshoot (Apache-2.0?), Docker images zeek/zeek, jasonish/suricata (who maintains it; license of
the Dockerfiles), ollama/ollama, python:3.11-slim (PSF + Debian packages), MITRE ATT&CK data (Terms of Use: what attribution
is required), Community ID spec (BSD-3, Corelight), JA4 (BSD-3-Clause, FoxIO), Debian suricata package. Models (only if
quickly verifiable): Qwen3 (Apache-2.0), Llama 3.2/3.1 (Llama Community License), Phi-4-mini (MIT), Gemma 3 (Gemma Terms
of Use), Granite (Apache-2.0). For each: name, version we pin, license (SPDX), where it is used (runtime/dev/lab/CI), can
it be redistributed in our offline bundle and what notice is required, source URL. Check compatibility with Apache-2.0
for our own code (GPL-2.0 Suricata is fine as a separate program — cite FSF's "aggregate" FAQ). draft_markdown should be
the full DEPENDENCIES.md table.` },
  { key: 'calendar', prompt: `Find Central Connecticut State University (CCSU) academic calendar dates for Fall 2026 and Spring 2027:
Thanksgiving recess, last day of classes and final exams Fall 2026, winter break, Spring 2027 first day of classes,
spring break week, last day of classes, finals. Cite ccsu.edu calendar pages. If Spring 2027 is not published, say so and
give the Spring 2026 pattern as an estimate clearly labeled. Then list all Fridays from Oct 9, 2026 to May 14, 2027 with
any that fall in a break.` },
  { key: 'gh-cli', prompt: `For scripts/create_issues.sh (GitHub CLI): verify current gh syntax (cite cli.github.com manual) for:
gh label create (--color, --description, --force), creating milestones (gh has no milestone command: use gh api
repos/{owner}/{repo}/milestones -f title= -f due_on= ; check idempotency approach: list existing first), gh issue create
(--title --body-file --label --milestone --assignee), gh project create/list/item-add (Projects v2: gh project create
--owner --title; gh project item-add <number> --owner --url; the token needs the "project" scope: gh auth refresh -s project),
GitHub Discussions enabling (repo settings; gh api graphql?), and rate-limit-friendly behavior. Also: GitHub issue forms
(.github/ISSUE_TEMPLATE/*.yml) schema: name, description, title, labels, assignees, body with type markdown/input/textarea/
dropdown/checkboxes, validations.required; config.yml with blank_issues_enabled and contact_links (point questions to
Discussions). And .github/pull_request_template.md conventions. Check whether gh is installed here (gh --version) and write
a fake "gh" shim approach for testing a script without touching GitHub. draft_markdown: notes + the exact syntax table.` },
]

phase('Research')
const results = await pipeline(TOPICS,
  t => agent(`${RULES}\n\nTOPIC: ${t.key}\n${t.prompt}\n\nAlso write your draft into ${OUT}/${t.key}.md (create the folder if needed).`,
             { label: `research:${t.key}`, phase: 'Research', schema: FACTS }),
  (r, t) => r ? agent(`You are a skeptical fact-checker. Here is a research result on "${t.key}" for a public student
project's documentation. Independently re-check the 8 most important or most surprising claims (menu paths, default IPs,
commands/flags, licenses, dates) using web search / primary sources. Default to "refuted" if a claim cannot be confirmed.
Return the same schema: keep confirmed facts as verified, downgrade or correct the rest, and put corrections in notes.
Also fix the draft_markdown accordingly and overwrite ${OUT}/${t.key}.md with the corrected draft.
RESULT TO CHECK:\n${JSON.stringify(r).slice(0, 60000)}`, { label: `verify:${t.key}`, phase: 'Verify', schema: FACTS }) : null)
return results.filter(Boolean).map(r => ({ topic: r.topic, open_questions: r.open_questions,
  facts: r.facts.length, unverified: r.facts.filter(f => f.confidence !== 'verified').map(f => f.claim) }))
