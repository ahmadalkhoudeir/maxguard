# MaxGuard v2.0: Dependencies and Licenses

> **Status:** checked on **October 6, 2026**. In the "Pin" column, Python versions
> are what `pip` resolved on that date for Python 3.11 on Linux x86-64, which are
> also the versions MaxGuard v2.0 was tested with during planning;
> `pyproject.toml` (task JAI-01) records them as minimum versions. Image versions
> are the tags MaxGuard pins (`docs/ARCHITECTURE.md` section 17). Until JAI-01 is
> merged, the repository's `requirements.txt` is still the v0.8.0 list
> (section 8).

## Why this file exists

`CLAUDE.md` rule 7 says: *record the license of every new dependency in
`docs/DEPENDENCIES.md`.* MaxGuard's own code is licensed under **Apache-2.0**
(the `LICENSE` file at the repository root). Everything else we run or ship
belongs to someone else, and its license tells us three things:

1. whether we may use it together with our Apache-2.0 code,
2. whether we may copy it into the **offline bundle** (the USB/air-gapped
   install), and
3. which notices or source code we must ship with it.

**Before you add a dependency:** open a pull request that adds a row to the right
table below. Fill in every column, then wait for review (see `CLAUDE.md`, "How to
work in this repo").

### How to read the tables

| Column | Meaning |
|---|---|
| **License (SPDX)** | The standard short license name from the [SPDX list](https://spdx.org/licenses/). `A OR B` means we may pick either one. `A AND B` means both apply. |
| **Used in** | **Runtime**: shipped inside MaxGuard. **Dev**: developer laptops only. **CI**: GitHub Actions only. **Lab**: the reference lab only, never shipped. |
| **Bundle?** | May we put a copy in the offline bundle? |
| **Notice** | What we must ship next to the copy. "License file" means the license file(s) found in the package itself. |
| **Confidence** | **Verified**: the license text was read from the project itself (the license file inside the package, the project's own repository, or PyPI's JSON metadata). **Likely**: confirmed only through search results because the primary site was blocked from the research environment (section 10). **Unverified**: not checked. |

## Summary (read this first)

1. **Python runtime:** all 26 packages that `pip` installs are permissive (MIT,
   MIT-0, BSD-2/3-Clause, Apache-2.0, PSF-2.0), except **certifi (MPL-2.0)**,
   which is weak copyleft and fine to use unmodified. All 26 may go in the
   offline bundle if we include their license files (section 7 has a tested
   script that collects them).
2. **Suricata is GPL-2.0-only.** The FSF does not consider Apache-2.0 compatible
   with GPL version 2, so Suricata and MaxGuard must stay **separate programs**:
   MaxGuard starts Suricata, Suricata writes `eve.json`, and MaxGuard reads the
   file. Never import, link, or copy Suricata code, and that includes its JA4
   code (section 6).
3. **Container images contain GPL and LGPL operating-system packages** (Debian,
   Ubuntu, AlmaLinux). If the offline bundle includes image tarballs, we are
   distributing GPL binaries, so we must also ship the source code or a written
   offer (GPL-2.0 section 3). **Decision needed.**
4. **The `ollama/ollama` image also contains NVIDIA CUDA libraries** (`cublas`,
   `cublasLt`, `cudart`), which are covered by NVIDIA's EULA, not an open-source
   license. **Decision needed.**
5. **Models:** Qwen3 and Granite (Apache-2.0) and Phi-4-mini (MIT) are the
   simplest to ship. Llama 3.1/3.2 and Gemma 3 allow redistribution, but they
   add notice, branding and use-policy duties.
6. **Offline-rule findings from the same check** (section 8): DuckDB will try
   to download extensions unless we turn that off. FastAPI now pulls in
   `opentelemetry-api` (API only, cannot send data). Starlette's test client
   now wants `httpx2`.

---

## 1. Python runtime packages (shipped)

These are the packages installed by
`pip install pyyaml requests fastapi uvicorn jinja2 python-multipart duckdb cryptography`
(Python 3.11, October 6, 2026): 8 direct dependencies and 18 transitive ones.
Every row is **Verified** against both the PyPI JSON API
(`https://pypi.org/pypi/<name>/json`) and the license file inside the installed
wheel. All of them may be bundled. The notice for each is the license file from
the wheel.

| Package | Pin | License (SPDX) | Why we need it | Notes | Source |
|---|---|---|---|---|---|
| fastapi | 0.142.2 | MIT | API backend and dashboard (direct) | Now requires `opentelemetry-api` and `annotated-doc` | [PyPI](https://pypi.org/pypi/fastapi/json) |
| starlette | 1.7.0 | BSD-3-Clause | Web framework under FastAPI; server-sent events | | [PyPI](https://pypi.org/pypi/starlette/json) |
| pydantic | 2.13.5 | MIT | Request/response validation (FastAPI) | | [PyPI](https://pypi.org/pypi/pydantic/json) |
| pydantic-core | 2.46.5 | MIT | Compiled core of pydantic | pydantic 2.13.5 requires exactly `==2.46.5`. PyPI's newest (2.49.0) does not fit. | [PyPI](https://pypi.org/pypi/pydantic-core/json) |
| uvicorn | 0.54.0 | BSD-3-Clause | Web server that runs FastAPI (direct) | | [PyPI](https://pypi.org/pypi/uvicorn/json) |
| h11 | 0.16.0 | MIT | HTTP/1.1 parser for uvicorn | | [PyPI](https://pypi.org/pypi/h11/json) |
| click | 8.5.0 | BSD-3-Clause | uvicorn's command line | | [PyPI](https://pypi.org/pypi/click/json) |
| anyio | 4.15.1 | MIT | Async support for Starlette | | [PyPI](https://pypi.org/pypi/anyio/json) |
| jinja2 | 3.1.6 | BSD-3-Clause | Server-rendered HTML templates (direct) | PyPI shows only the generic "BSD License" classifier. The wheel's `LICENSE.txt` has the three BSD clauses, so it is BSD-3-Clause. | [PyPI](https://pypi.org/pypi/jinja2/json), [LICENSE](https://github.com/pallets/jinja/blob/main/LICENSE.txt) |
| markupsafe | 3.0.4 | BSD-3-Clause | HTML escaping for Jinja2 | | [PyPI](https://pypi.org/pypi/markupsafe/json) |
| python-multipart | 0.0.32 | Apache-2.0 | Pcap upload forms (direct) | | [PyPI](https://pypi.org/pypi/python-multipart/json) |
| pyyaml | 6.0.3 | MIT | Reads the mapping YAML files (direct) | | [PyPI](https://pypi.org/pypi/pyyaml/json) |
| requests | 2.34.2 | Apache-2.0 | HTTP client for the local Ollama API (direct) | Ships a `NOTICE` file ("Requests Copyright 2019 Kenneth Reitz"). Keep it next to the license. Apache-2.0 section 4(d) requires a readable copy of the NOTICE in anything derived from the package, and keeping it on unmodified copies is standard practice. | [PyPI](https://pypi.org/pypi/requests/json) |
| urllib3 | 2.8.0 | MIT | Used by requests | | [PyPI](https://pypi.org/pypi/urllib3/json) |
| idna | 3.20 | BSD-3-Clause | Used by requests and anyio | | [PyPI](https://pypi.org/pypi/idna/json) |
| charset-normalizer | 3.5.2 | MIT | Used by requests | | [PyPI](https://pypi.org/pypi/charset-normalizer/json) |
| certifi | 2026.7.22 | **MPL-2.0** | CA certificate bundle used by requests | Weak copyleft (section 6). Do not edit `cacert.pem`. If we ever need our own CA, put it in a separate file. | [PyPI](https://pypi.org/pypi/certifi/json) |
| duckdb | 1.5.6 | MIT | Queries the hourly Parquet event files (direct) | PyPI has only the "MIT License" classifier. The wheel's `LICENSE` is MIT ("Copyright 2018-2026 Stichting DuckDB Foundation"). Parquet, JSON and ICU support are built in. **Read section 8 (extension auto-install).** | [PyPI](https://pypi.org/pypi/duckdb/json), [LICENSE](https://github.com/duckdb/duckdb-python/blob/main/LICENSE) |
| cryptography | 50.0.2 | Apache-2.0 OR BSD-3-Clause | Signs and verifies intel bundles and the custody log (direct) | The wheel contains its own copy of **OpenSSL 4.0.3** (reported by `backend.openssl_version_text()`; there is no separate `libssl` file). OpenSSL is Apache-2.0, so add its license to the bundle notices. | [PyPI](https://pypi.org/pypi/cryptography/json), [OpenSSL LICENSE](https://github.com/openssl/openssl/blob/openssl-4.0/LICENSE.txt) |
| cffi | 2.1.1 | MIT-0 | Used by cryptography | MIT No Attribution: no notice required | [PyPI](https://pypi.org/pypi/cffi/json) |
| pycparser | 3.0 | BSD-3-Clause | Used by cffi | | [PyPI](https://pypi.org/pypi/pycparser/json) |
| typing-extensions | 4.16.0 | PSF-2.0 | Used by pydantic and FastAPI | | [PyPI](https://pypi.org/pypi/typing-extensions/json) |
| typing-inspection | 0.4.4 | MIT | Used by pydantic and FastAPI | | [PyPI](https://pypi.org/pypi/typing-inspection/json) |
| annotated-types | 0.8.0 | MIT | Used by pydantic | | [PyPI](https://pypi.org/pypi/annotated-types/json) |
| annotated-doc | 0.0.5 | MIT | Used by FastAPI | | [PyPI](https://pypi.org/pypi/annotated-doc/json) |
| opentelemetry-api | 1.45.0 | Apache-2.0 | Used by FastAPI | API only, no SDK or exporter, so nothing can be sent (section 8) | [PyPI](https://pypi.org/pypi/opentelemetry-api/json) |

**Listed in the original task but not installed by the runtime set:**

| Package | License (SPDX) | Why it is not here | Source |
|---|---|---|---|
| sniffio 1.3.1 | MIT OR Apache-2.0 | anyio 4.15.1 no longer depends on it | [PyPI](https://pypi.org/pypi/sniffio/json) |
| httpx / httpcore | BSD-3-Clause | Only needed by the test client (section 2) | [PyPI](https://pypi.org/pypi/httpx/json) |

## 2. Python packages for development, CI, and the lab (not shipped)

None of these go into the offline bundle, so there is nothing to bundle and no notice
to ship. All are **Verified** (PyPI JSON plus the license file inside the wheel).

| Package | Pin | License (SPDX) | Used in | Notes | Source |
|---|---|---|---|---|---|
| pytest | 9.1.1 | MIT | Dev, CI | | [PyPI](https://pypi.org/pypi/pytest/json) |
| iniconfig | 2.3.0 | MIT | Dev, CI | pytest dependency | [PyPI](https://pypi.org/pypi/iniconfig/json) |
| packaging | 26.3 | Apache-2.0 OR BSD-2-Clause | Dev, CI | pytest dependency (also present inside `python:3.11-slim`) | [PyPI](https://pypi.org/pypi/packaging/json) |
| pluggy | 1.6.0 | MIT | Dev, CI | pytest dependency | [PyPI](https://pypi.org/pypi/pluggy/json) |
| pygments | 2.21.0 | BSD-2-Clause | Dev, CI | pytest dependency | [PyPI](https://pypi.org/pypi/pygments/json) |
| ruff | 0.16.10 | MIT | Dev, CI | Its `LICENSE` also carries the notices of tools it reimplements (Flake8, pycodestyle, pyupgrade and others) | [PyPI](https://pypi.org/pypi/ruff/json) |
| httpx2 | 2.13.1 | BSD-3-Clause | Dev, CI | FastAPI `TestClient` (the `dev` extra in `pyproject.toml`). With plain `httpx`, Starlette 1.7.0 prints "Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead" (seen in planning). | [PyPI](https://pypi.org/pypi/httpx2/json) |
| httpcore2 | 2.13.1 | BSD-3-Clause | Dev, CI | httpx2 dependency | [PyPI](https://pypi.org/pypi/httpcore2/json) |
| truststore | 0.10.4 | MIT | Dev, CI | httpx2 dependency | [PyPI](https://pypi.org/pypi/truststore/json) |
| httpx / httpcore | 0.28.1 / 1.0.9 | BSD-3-Clause | (avoid) | Still works with Starlette 1.7.0 but prints a deprecation warning. Use httpx2. | [PyPI](https://pypi.org/pypi/httpx/json) |
| pyftpdlib | 2.2.0 | MIT | Lab only | PyPI has no license fields. The wheel's `LICENSE` and the GitHub `LICENSE` are MIT ("Copyright (c) 2007 Giampaolo Rodola'"). | [LICENSE](https://github.com/giampaolo/pyftpdlib/blob/master/LICENSE) |
| playwright | 1.63.0 | Apache-2.0 | Dev only, if browser tests are added | `playwright install` downloads browser builds separately. Their licenses were **not checked**, and they must never be bundled. | [PyPI](https://pypi.org/pypi/playwright/json) |
| pyee | 13.0.1 | MIT | Dev only | playwright dependency | [PyPI](https://pypi.org/pypi/pyee/json) |
| greenlet | 3.5.6 | MIT AND PSF-2.0 | Dev only | playwright dependency | [PyPI](https://pypi.org/pypi/greenlet/json) |

## 3. Programs and container images

Image digests are the multi-architecture digests from Docker Hub on October 6,
2026. Pin by digest (`image@sha256:...`) so a re-pushed tag cannot change what
we ship.

| Component | Pin | License | Used in | Bundle? | Notice | Source | Confidence |
|---|---|---|---|---|---|---|---|
| **Zeek** | 9.0.0 | BSD-3-Clause | Runtime: sensor, pcap parsing | Yes | Zeek `COPYING`. It is **not** inside the image (the only `COPYING` in the image is CMake's), so add it ourselves. | [COPYING](https://github.com/zeek/zeek/blob/master/COPYING) | Verified |
| `zeek/zeek` image | `9.0.0@sha256:70733f4e540ba1608e37e00c6a93d009f79734262c9ec2ba09d90aa9abc16de5` | Zeek BSD-3-Clause + Debian packages | Runtime | Yes, with the OS-package duties in 3.1 | as above + 3.1 | [docker/README.md](https://github.com/zeek/zeek/blob/master/docker/README.md), [Dockerfile](https://github.com/zeek/zeek/blob/master/docker/Dockerfile) | Verified (amd64 image pulled; arm64 not run, verify on hardware) |
| **Suricata** | 8.0.7 (live sensor); 7.0.10 (engine image, from Debian 13) | **GPL-2.0-only** | Runtime: capture analysis in the engine image, the live sensor, JA4 source | Yes, **as a separate program only** | GPL-2.0 text plus the complete source code or a written offer (GPL-2.0 section 3) | [LICENSE](https://github.com/OISF/suricata/blob/main/LICENSE), [src/suricata.c header](https://github.com/OISF/suricata/blob/main/src/suricata.c) ("version 2", no "or later") | Verified |
| `jasonish/suricata` image | `8.0.7@sha256:7ca2546f7f2735f621b981b6a5ec84fb962984636f7629a1a2fa6a324d4b6840` | Dockerfiles and scripts: MIT ("Copyright (c) 2021 Open Information Security Foundation"). Contents: Suricata GPL-2.0-only + AlmaLinux 9.8 (191 RPMs: GPL, LGPL, MIT, BSD) + Hyperscan (BSD) | Runtime | Yes, with the duties in 3.1 | The image's `/usr/share/doc/suricata/` has **no** GPL text, so add it ourselves | [README "License"](https://github.com/jasonish/docker-suricata#license), [LICENSE.txt](https://github.com/jasonish/docker-suricata/blob/main/LICENSE.txt), [Docker Hub](https://hub.docker.com/r/jasonish/suricata) | Verified. Published under the personal Docker Hub namespace `jasonish`. Whether OISF calls it its official image is **unverified**. |
| Debian package `suricata` | Debian 13 "trixie": probably `1:7.0.10` (stable updates) and `1:8.0.6` (trixie-backports) | GPL-2.0-only (upstream) + Debian packaging | Runtime: installed by `docker/Dockerfile` into the engine image (the stable `1:7.0.10`) | Same as Suricata | `/usr/share/doc/suricata/copyright` | [Debian tracker news](https://tracker.debian.org/news/1701457/accepted-suricata-17010-1deb13u2-source-into-proposed-updates/), [backports list](https://lists.debian.org/debian-backports-changes/2026/07/msg00036.html) | Versions **Likely** (search only). Copyright file **Unverified** (Debian sites blocked). Check on hardware (section 9). |
| **Ollama** | 0.35.1 (0.40.0 is release-candidate only) | MIT ("Copyright (c) Ollama") | Runtime: console machine only, not the Pi | Yes, for Ollama's own code | `LICENSE` + `/usr/lib/ollama/GO_LICENSE` (Go dependency licenses, placed in the image by the Dockerfile) | [LICENSE](https://github.com/ollama/ollama/blob/main/LICENSE) | Verified |
| `ollama/ollama` image | `0.35.1@sha256:292ee7945dfc3d5840a181f3ab86fedb1e66703e02c8af98b50f4da56b7e278c` | Mixed: Ollama MIT + Ubuntu 24.04 packages + **NVIDIA CUDA runtime (`cublas`, `cublasLt`, `cudart`) under NVIDIA's CUDA EULA** + Vulkan and MLX libraries (amd64) + NVIDIA JetPack libraries (arm64) | Runtime | **Decision needed** (section 6 and open questions) | All of the above + the NVIDIA EULA | [Dockerfile](https://github.com/ollama/ollama/blob/main/Dockerfile), [llama/server/CMakeLists.txt](https://github.com/ollama/ollama/blob/main/llama/server/CMakeLists.txt) ("Bundle GPU runtime libraries (cublas, cudart, rocblas, etc.)") | Verified from the build files. Image not pulled (several GB). |
| **htmx** | 2.0.11 | 0BSD | Runtime: vendored JavaScript for the dashboard | Yes | None required (0BSD). Keep the file header anyway. | [LICENSE at tag v2.0.11](https://github.com/bigskysoftware/htmx/blob/v2.0.11/LICENSE), [npm](https://registry.npmjs.org/htmx.org/2.0.11) (`"license": "0BSD"`, integrity `sha512-Thx/WtpeOQqSrqBCw/A1cwGJGg4UrVa3+sW0GmrM3p4gJgO89ecH4qtbnyzDDWFvBTqjnIMCgELTNt636dtamA==`) | Verified |
| **goflow2** | v2.2.7, `netsampler/goflow2:v2.2.7@sha256:b8fdc8f3666b05b0022ada3a3c8c50dcde97f7d19e3f42d050695fa0571fb952` | BSD-3-Clause ("Copyright (c) 2021, NetSampler") | Planned: NetFlow/IPFIX input (JAK-10, spring) | Yes | `LICENSE`. The image is built on `alpine:latest`. Its Alpine packages were **not inspected**. | [LICENSE](https://github.com/netsampler/goflow2/blob/main/LICENSE) | Verified (license). Image contents unverified. |
| `nicolaka/netshoot` image | `v0.15` (the lab's sniffer; `v0.16` is the newest) | Repository: Apache-2.0. The image (Alpine) also contains **nmap (Nmap Public Source License 0.95)**, tshark/termshark, tcpdump, scapy (GPL-2.0-only) and more. | Lab only | **No. Never ship it.** Students pull it themselves. | n/a | [LICENSE](https://github.com/nicolaka/netshoot/blob/master/LICENSE), [Dockerfile](https://github.com/nicolaka/netshoot/blob/master/Dockerfile), [nmap LICENSE](https://github.com/nmap/nmap/blob/master/LICENSE) | Verified (repository license and the `v0.16` contents; `v0.15` was used, not inspected) |
| `python:3.11-slim-bookworm` image | `3.11-slim-bookworm` | CPython: PSF-2.0. Dockerfiles: MIT ("Copyright (c) 2014 Docker, Inc."). Debian packages, many under GPL (for example bash, coreutils). | Lab only (the traffic lab's server and client). **Not** the base of the MaxGuard image, which is `zeek/zeek` | No | n/a | [CPython 3.11 LICENSE](https://github.com/python/cpython/blob/3.11/LICENSE), [docker-library/python LICENSE](https://github.com/docker-library/python/blob/master/LICENSE), [Docker license note](https://github.com/docker-library/docs/blob/master/.template-helpers/license-common.md) | Verified (license files; the `3.11-slim` trixie variant was inspected in planning) |

### 3.1 What "operating-system packages inside an image" means for the bundle

Docker's own note for official images says they "likely also contain other
software which may be under other licenses (such as Bash, etc from the base
distribution...)" and that "it is the image user's responsibility to ensure that
any use of this image complies with any relevant licenses for all software
contained within"
([source](https://github.com/docker-library/docs/blob/master/.template-helpers/license-common.md)).

If we put `docker save` tarballs on the USB, we distribute GPL programs (bash,
coreutils, Suricata and others) in binary form. GPL-2.0 section 3 then requires
**one** of these
([GPL-2.0 text, from Suricata's LICENSE](https://github.com/OISF/suricata/blob/main/LICENSE)):

- **(a)** ship "the complete corresponding machine-readable source code" with it, or
- **(b)** ship "a written offer, valid for at least three years" to provide the source, or
- **(c)** pass on the offer we received. This is allowed "only for noncommercial
  distribution" and only if we received such an offer. Docker images do not come
  with one, so (c) does not apply.

**Recommendation (decision for Jaiden and the Security Lead):** use **(a)**. Put
the Suricata 8.0.7 source tarball and the source packages for each image's GPL
components on the bundle, or on a second "sources" USB. A student team cannot
promise to answer a written offer for three years. GPL-3.0 (which bash and
coreutils use) has the same choice in its section 6, "Conveying Non-Source
Forms", including a "written offer, valid for at least three years" (verified
from `/usr/share/common-licenses/GPL-3`).

---

## 4. Data, specifications, and fingerprint methods

| Item | Version | License | Used in | Bundle? | Notice | Source | Confidence |
|---|---|---|---|---|---|---|---|
| **MITRE ATT&CK** Enterprise STIX data | v19.x (record the exact point release, per `PROJECT_DECISIONS.md` section 8) | MITRE ATT&CK Terms of Use, a custom permissive license with no SPDX id. "A non-exclusive, royalty-free license to use ATT&CK® for research, development, and commercial purposes." | Runtime: ATT&CK mapping | Yes | "Any copy you make ... is authorized provided that you reproduce MITRE's copyright designation and this license." Copy the `LICENSE.txt` from the release we ship. Today's text is: "© 2026 The MITRE Corporation. This work is reproduced and distributed with the permission of The MITRE Corporation." | [attack-stix-data LICENSE.txt](https://github.com/mitre-attack/attack-stix-data/blob/master/LICENSE.txt), [Terms of Use](https://attack.mitre.org/resources/legal-and-branding/terms-of-use/) | Verified (license text). Trademark rules **Likely**: write "MITRE ATT&CK®" on first reference and do not imply that MITRE endorses MaxGuard ([Legal & Branding](https://attack.mitre.org/resources/legal-and-branding/), search only). |
| **Community ID** spec | v1 | BSD-3-Clause ("Copyright (c) 2017-2018 by Corelight, Inc") | Runtime, through Zeek and Suricata output | n/a | None, unless we copy code from the spec repository (then keep its `COPYING`) | [COPYING](https://github.com/corelight/community-id-spec/blob/master/COPYING) | Verified |
| pycommunityid (only if we compute Community ID in Python) | not chosen | BSD-3-Clause (Corelight, 2017-2023) | Not used yet | Yes | `LICENSE` | [LICENSE](https://github.com/corelight/pycommunityid/blob/master/LICENSE) | Verified (header only) |
| **JA4** (TLS client fingerprint) | n/a | BSD-3-Clause (`LICENSE-JA4`, FoxIO). The README says FoxIO "does not have patent claims" on JA4. | Runtime, through Suricata's built-in JA4 | n/a: we only store and display the fingerprint string | Keep FoxIO's copyright if we ever copy JA4 code (we should not) | [LICENSE-JA4](https://github.com/FoxIO-LLC/ja4/blob/main/LICENSE-JA4), [README "Licensing"](https://github.com/FoxIO-LLC/ja4#licensing) | Verified |
| Suricata's JA4 implementation | in Suricata 8.0.7 | GPL-2.0-only ("Copyright (C) 2023-2024 Open Information Security Foundation") | Runtime, inside the Suricata process | as Suricata | as Suricata | [rust/src/ja4.rs](https://github.com/OISF/suricata/blob/main/rust/src/ja4.rs) | Verified. `jasonish/suricata:8.0.7` reports `JA4 support: yes` (amd64; arm64 not run). Enable it with `ja4-fingerprints` under the TLS app-layer settings in `suricata.yaml`. |
| **JA4+** (JA4S, JA4H, JA4L, JA4LS, JA4X, JA4T, JA4TS, JA4TScan, JA4D, JA4D6, JA4SScan, JA4E, JA4SSH) | n/a | FoxIO License 1.1, **non-commercial only** | **Excluded** (`CLAUDE.md` rule 7) | No | n/a | [LICENSE](https://github.com/FoxIO-LLC/ja4/blob/main/LICENSE) | Verified |

## 5. Local AI models (Ollama)

`PROJECT_DECISIONS.md` section 6: "Only models whose license allows
redistribution in the offline bundle are eligible." All five families below
allow redistribution, but two of them come with extra duties. Ali's evaluation
picks the model. Where quality is close, prefer Apache-2.0 or MIT.

| Model family | License | Bundle? | What we must ship or show | Source | Confidence |
|---|---|---|---|---|---|
| **Qwen3** | Apache-2.0 | Yes | Apache-2.0 text + any NOTICE in that model's repository | [Qwen3 README](https://github.com/QwenLM/Qwen3#license-agreement): "All our open-weight models are licensed under Apache 2.0." | Verified (README). The per-model LICENSE on Hugging Face was not opened (blocked). |
| **Granite** 3.3 / 4.0 language models | Apache-2.0 | Yes | Apache-2.0 text | [granite-3.3 LICENSE](https://github.com/ibm-granite/granite-3.3-language-models/blob/main/LICENSE), [granite-4.0 LICENSE](https://github.com/ibm-granite/granite-4.0-language-models/blob/main/LICENSE) | Verified |
| **Phi-4-mini** | MIT | Yes | MIT text | [Hugging Face model card](https://huggingface.co/microsoft/Phi-4-mini-instruct) | **Likely** (search only; Hugging Face blocked) |
| **Llama 3.2** (1B/3B text) | Llama 3.2 Community License (not an open-source license) | Yes, with conditions | (A) "provide a copy of this Agreement"; (B) "prominently display 'Built with Llama'" in the UI, about page or docs; a `Notice` text file containing "Llama 3.2 is licensed under the Llama 3.2 Community License, Copyright © Meta Platforms, Inc. All Rights Reserved."; follow the Acceptable Use Policy. The EU restriction in the policy applies only to **multimodal** Llama 3.2 models. | [LICENSE](https://github.com/meta-llama/llama-models/blob/main/models/llama3_2/LICENSE), [USE_POLICY.md](https://github.com/meta-llama/llama-models/blob/main/models/llama3_2/USE_POLICY.md) | Verified |
| **Llama 3.1** (8B) | Llama 3.1 Community License | Yes, with conditions | Same as 3.2, with the notice "Llama 3.1 is licensed under the Llama 3.1 Community License, Copyright © Meta Platforms, Inc. All Rights Reserved." | [LICENSE](https://github.com/meta-llama/llama-models/blob/main/models/llama3_1/LICENSE) | Verified |
| **Gemma 3** | Gemma Terms of Use (not an open-source license) | Yes, with conditions | Section 3.1: our own terms must include Google's use restrictions (section 3.2) "as an enforceable provision"; give every recipient a copy of the terms; mark modified files; ship a `Notice` file containing "Gemma is provided under and subject to the Gemma Terms of Use found at ai.google.dev/gemma/terms". | [Gemma Terms of Use](https://ai.google.dev/gemma/terms) | **Likely** (search only; ai.google.dev blocked) |

To print the license that comes with a pulled model:
`ollama show <model> --license` (**not run**: no Ollama here. Check the flag
with `ollama show --help` first.)

---

## 6. Compatibility with our Apache-2.0 code

The Apache Software Foundation's [third-party license policy](https://www.apache.org/legal/resolved.html)
is a good, conservative yardstick. It is written for ASF projects, which are
stricter than we need to be.

| License family | Where it appears | OK with Apache-2.0? | What we must do | Source |
|---|---|---|---|---|
| MIT, MIT-0, BSD-2-Clause, BSD-3-Clause, ISC, 0BSD, PSF-2.0, Apache-2.0 | Almost every Python package, Zeek, Ollama, htmx, goflow2, JA4 | **Yes.** All are in ASF "Category A", which the ASF considers "similar in terms to the Apache License 2.0". | Keep their copyright and license files. Keep the NOTICE file for Apache-2.0 packages (requests). | [ASF Category A](https://www.apache.org/legal/resolved.html#category-a) |
| MPL-2.0 | certifi | **Yes, when unmodified.** ASF "Category B" ("weak copyleft"). MPL applies file by file. | Keep the license block in `cacert.pem` and do not edit the file. MPL section 3.2: when shipping "Executable Form", the source must be available. A wheel is already plain Python and PEM text, so shipping the wheel unmodified covers this (our reading, not legal advice). | [ASF Category B](https://www.apache.org/legal/resolved.html#category-b), [MPL-2.0](https://www.mozilla.org/en-US/MPL/2.0/) section 3.2(a): "must also be made available in Source Code Form ... and You must inform recipients of the Executable Form how they can obtain a copy" (Verified from the MPL-2.0 text that Debian ships in `/usr/share/common-licenses/MPL-2.0`, package `base-files`) |
| **GPL-2.0-only** | Suricata; scapy (v0.8 only); GPL packages inside images | **Not compatible for combining into one program.** ASF: "the FSF has never considered the Apache License to be compatible with GPL version 2". **Fine as separate programs** on the same medium. | Run Suricata as its own process. Talk to it only through files (`eve.json`), the command line, and sockets. Never `import`, link, or copy GPL code into MaxGuard. Ship Suricata's source (section 3.1). | [ASF GPL compatibility](https://www.apache.org/licenses/GPL-compatibility.html), GPL-2.0 section 2: "mere aggregation of another work not based on the Program with the Program ... on a volume of a storage or distribution medium does not bring the other work under the scope of this License" ([text](https://github.com/OISF/suricata/blob/main/LICENSE)) |
| GPL (FSF's view of "separate programs") | as above | as above | The FSF FAQ says an "aggregate" of separate programs on one medium is allowed. "Pipes, sockets and command-line arguments are communication mechanisms normally used between two separate programs", but "if the semantics of the communication are intimate enough, exchanging complex internal data structures", the two parts may count as one program. Reading JSON log lines is ordinary program-to-program communication. | [GPL FAQ: MereAggregation](https://www.gnu.org/licenses/gpl-faq.html#MereAggregation) (**Likely**: gnu.org blocked, wording confirmed through search) |
| FoxIO License 1.1 | JA4+ (except JA4) | **No** (non-commercial only) | Excluded | [LICENSE](https://github.com/FoxIO-LLC/ja4/blob/main/LICENSE) |
| Nmap Public Source License 0.95 | nmap inside netshoot | Not standard, with extra conditions | Lab only, never bundled | [nmap LICENSE](https://github.com/nmap/nmap/blob/master/LICENSE) |
| NVIDIA CUDA EULA | CUDA libraries inside `ollama/ollama` | Proprietary. Only listed "redistributable" files may be shipped, under conditions (for example: "Your application must have material additional functionality, beyond the included portions of the SDK"). | **Decision needed.** Options: (1) ship the image as-is with the NVIDIA EULA in the notices; (2) have users pull the image themselves; (3) find a CPU-only Ollama build (not researched). | [CUDA EULA](https://docs.nvidia.com/cuda/eula/index.html) (**Likely**: docs.nvidia.com blocked) |
| Llama Community License, Gemma Terms of Use | model files | They do not change MaxGuard's own license. They add duties to the bundle (section 5). | Ship the notices. Show "Built with Llama" if a Llama model ships. | section 5 |

## 7. Offline-bundle notice checklist

Make a `third_party_licenses/` folder in the bundle and fill it like this.

**Step 1: Python packages (tested October 6, 2026, Python 3.11, Linux x86-64).**
Run this inside the virtual environment that will be bundled. It copies every
license, notice, and authors file that each installed wheel ships.

```bash
python - <<'EOF'
import importlib.metadata as m, pathlib, shutil
out = pathlib.Path("third_party_licenses/python")
for d in m.distributions():
    name, ver = d.metadata["Name"], d.version
    if name.lower() in {"pip", "setuptools"}:
        continue  # venv tooling, not shipped by MaxGuard
    dest = out / f"{name}-{ver}"
    for f in d.files or []:
        p = str(f)
        if ".dist-info/" in p and any(k in p.rsplit("/", 1)[-1].upper() for k in ("LICEN", "COPYING", "NOTICE", "AUTHORS")):
            dest.mkdir(parents=True, exist_ok=True)
            shutil.copy(d.locate_file(f), dest / pathlib.Path(p).name)
    if not dest.exists():
        print("NO LICENSE FILE FOUND:", name, ver)
print(len(list(out.iterdir())), "packages collected")
EOF
```

Expected output for the runtime set in section 1: `26 packages collected`, and
no `NO LICENSE FILE FOUND` lines. Why it matters: MIT, BSD and Apache-2.0 all
require that the license text travels with every copy. If a line says
`NO LICENSE FILE FOUND`, stop and find that package's license by hand.

**Step 2: add these by hand** (they are not inside the wheels or images):

- [ ] OpenSSL `LICENSE.txt` (Apache-2.0), for the OpenSSL 4.0.3 inside `cryptography`
- [ ] Zeek `COPYING`
- [ ] Suricata `COPYING` (GPL-2.0) **and** the source of every Suricata build you ship: Debian's `suricata` source package for the 7.0.10 inside the engine image, and the Suricata 8.0.7 source tarball if the sensor image ships
- [ ] Ollama `LICENSE` and `GO_LICENSE`. To copy the second one out of the image:
      `docker run --rm --entrypoint cat ollama/ollama:0.35.1 /usr/lib/ollama/GO_LICENSE > third_party_licenses/ollama-GO_LICENSE`
      (**not run**: image not pulled here)
- [ ] htmx `LICENSE` (0BSD; optional, but harmless)
- [ ] goflow2 `LICENSE` (only if goflow2 ships)
- [ ] MITRE ATT&CK `LICENSE.txt` from the bundled release
- [ ] Model notices from section 5 (and the NVIDIA EULA if the Ollama image ships)
- [ ] Source code or a written offer for the GPL packages in each image (section 3.1)

**Step 3:** put the ATT&CK attribution (and "Built with Llama", if a Llama
model ships) on the dashboard's About page.

## 8. Things found during this check (not license issues, but they affect rules 1 and 6)

1. **DuckDB can download extensions by itself.** In duckdb 1.5.6,
   `autoinstall_known_extensions` and `autoload_known_extensions` are both
   `true` by default (confirmed in planning). Parquet, JSON and ICU are built
   in, but a query that needs another extension (for example `httpfs` for a URL)
   would try to download it. That breaks `CLAUDE.md` rule 1, so
   `maxguard/storage/events.py` (JAI-06) opens every connection with both
   switched off, and a unit test checks it. Any new DuckDB code must do the same
   (tested):

   ```python
   import duckdb
   con = duckdb.connect(config={"autoinstall_known_extensions": False,
                                "autoload_known_extensions": False})
   ```

   Expected: `select current_setting('autoinstall_known_extensions')` returns
   `False`. A query on an `https://` path then fails with
   `requires the extension httpfs to be loaded` instead of downloading anything.
2. **FastAPI 0.142.2 depends on `opentelemetry-api`.** Only the API is installed:
   the tracer provider is `ProxyTracerProvider`, and `opentelemetry.sdk` and
   `opentelemetry.exporter` are absent (tested), so nothing can be sent. Never
   add `opentelemetry-sdk` or an exporter package.
3. **Tests use `httpx2`, not `httpx`.** With plain `httpx`, Starlette 1.7.0's
   `TestClient` warns that it is deprecated; `pyproject.toml` lists `httpx2` in
   the `dev` extra.
4. **scapy is GPL-2.0-only** ([PyPI](https://pypi.org/pypi/scapy/json)), and the
   v0.8.0 code imports it. v2.0 code under Apache-2.0 must **not** `import scapy`.
   For synthetic test captures, run capture tools as separate programs, or keep
   any scapy script outside the Apache-2.0 tree under its own GPL-2.0 license
   (decision needed).
5. **Legacy v0.8.0 `requirements.txt`** (retired in v2.0): scapy 2.8.0
   GPL-2.0-only, openai Apache-2.0, streamlit Apache-2.0, pandas BSD-3-Clause,
   plotly MIT, python-dotenv BSD-3-Clause (all from PyPI JSON).

## 9. How to re-check (run before every release)

**Licenses of everything pip installs** (tested October 6, 2026):

```bash
python3.11 -m venv .venv-licenses
. .venv-licenses/bin/activate
python -m pip install --quiet pyyaml requests fastapi uvicorn jinja2 python-multipart duckdb cryptography
python - <<'EOF'
import importlib.metadata as m
for d in sorted(m.distributions(), key=lambda d: d.metadata["Name"].lower()):
    md = d.metadata
    lic = md.get("License-Expression") or md.get("License") or "; ".join(
        c.split(" :: ")[-1] for c in (md.get_all("Classifier") or []) if c.startswith("License"))
    print(f'{md["Name"]:<20} {d.version:<12} {lic}')
EOF
deactivate
```

Expected output (first lines; versions change over time):

```
annotated-doc        0.0.5        MIT
annotated-types      0.8.0        MIT
anyio                4.15.1       MIT
certifi              2026.7.22    MPL-2.0
cffi                 2.1.1        MIT-0
```

How to read it:
- A **blank** license (setuptools shows one) means "open the LICENSE file".
- **"MIT License"** or **"BSD License"** comes from a classifier, which is not
  exact. Read the LICENSE file to find the SPDX id. That is how Jinja2
  (BSD-3-Clause) and DuckDB (MIT) were confirmed.
- Any **GPL, LGPL, AGPL, SSPL, or "non-commercial"** license on a runtime
  package: stop and ask the Security Lead before merging.

**One package, straight from PyPI:**

```bash
curl -sS https://pypi.org/pypi/certifi/json | python3 -c "import json,sys; i=json.load(sys.stdin)['info']; print(i['name'], i['version'], i.get('license_expression') or i.get('license'))"
```

Expected: `certifi 2026.7.22 MPL-2.0` (the version changes over time).

**JA4 is compiled into the Suricata image** (tested on amd64):

```bash
docker run --rm --network none --entrypoint suricata jasonish/suricata:8.0.7 --build-info | grep "JA4 support"
```

Expected: `  JA4 support:                             yes`. On the Pi (arm64):
**not run, verify on hardware.**

**Debian/Raspberry Pi OS `suricata` package** (**not run, verify on hardware**):

```bash
apt-cache policy suricata                      # which version apt would install
less /usr/share/doc/suricata/copyright         # after installing: the license list
suricata --build-info | grep "JA4 support"     # after installing: must say yes
```

## 10. What could not be verified from a primary source

The research environment's network policy blocked these sites, so nothing was
fetched from them (no mirrors or caches were used either): `www.gnu.org`,
`attack.mitre.org`, `www.mozilla.org`, `docs.nvidia.com`, `ai.google.dev`,
`www.llama.com`, `huggingface.co`, `ollama.com`, `registry.ollama.ai`,
`spdx.org`, `packages.debian.org`, `sources.debian.org`, `salsa.debian.org`,
`tracker.debian.org`. A team member should open these in a browser and change
the matching rows from **Likely** to **Verified**:

- [ ] FSF GPL FAQ "MereAggregation" wording
- [ ] MITRE ATT&CK Terms of Use page and Brand Guide (trademark rules)
- [ ] NVIDIA CUDA EULA: redistributable files list (Attachment A) and distribution requirements
- [ ] Gemma Terms of Use section 3.1
- [ ] Phi-4-mini license on its Hugging Face model card
- [ ] Qwen3 per-model `LICENSE` on Hugging Face
- [ ] Debian `suricata` versions and `debian/copyright`

Also not checked: notices for third-party code compiled into the DuckDB and
pydantic-core binaries; the Playwright browser licenses; the Alpine packages in
the goflow2 image; the real contents of the `ollama/ollama` image (only its build
files were read); and every arm64 image.

## Sources

- PyPI JSON API, one URL per package: `https://pypi.org/pypi/<name>/json` (links in sections 1 and 2)
- Zeek: <https://github.com/zeek/zeek/blob/master/COPYING>, <https://github.com/zeek/zeek/blob/master/docker/Dockerfile>
- Suricata: <https://github.com/OISF/suricata/blob/main/LICENSE>, <https://github.com/OISF/suricata/blob/main/src/suricata.c>, <https://github.com/OISF/suricata/blob/main/rust/src/ja4.rs>, <https://github.com/OISF/suricata/blob/main/suricata.yaml.in>
- docker-suricata: <https://github.com/jasonish/docker-suricata/blob/main/LICENSE.txt>, <https://github.com/jasonish/docker-suricata/blob/main/README.md>
- Ollama: <https://github.com/ollama/ollama/blob/main/LICENSE>, <https://github.com/ollama/ollama/blob/main/Dockerfile>, <https://github.com/ollama/ollama/blob/main/llama/server/CMakeLists.txt>
- htmx: <https://github.com/bigskysoftware/htmx/blob/v2.0.11/LICENSE>, <https://registry.npmjs.org/htmx.org/2.0.11>
- goflow2: <https://github.com/netsampler/goflow2/blob/main/LICENSE>
- netshoot: <https://github.com/nicolaka/netshoot/blob/master/LICENSE>, <https://github.com/nicolaka/netshoot/blob/master/Dockerfile>; nmap: <https://github.com/nmap/nmap/blob/master/LICENSE>
- Python image: <https://github.com/docker-library/python/blob/master/LICENSE>, <https://github.com/docker-library/docs/blob/master/.template-helpers/license-common.md>, <https://github.com/python/cpython/blob/3.11/LICENSE>
- Docker Hub tags and digests: `https://hub.docker.com/v2/repositories/<namespace>/<name>/tags/<tag>`
- OpenSSL: <https://github.com/openssl/openssl/blob/openssl-4.0/LICENSE.txt>
- MITRE ATT&CK: <https://github.com/mitre-attack/attack-stix-data/blob/master/LICENSE.txt>, <https://attack.mitre.org/resources/legal-and-branding/terms-of-use/>
- Community ID: <https://github.com/corelight/community-id-spec/blob/master/COPYING>, <https://github.com/corelight/pycommunityid/blob/master/LICENSE>
- JA4: <https://github.com/FoxIO-LLC/ja4/blob/main/LICENSE-JA4>, <https://github.com/FoxIO-LLC/ja4/blob/main/LICENSE>, <https://github.com/FoxIO-LLC/ja4/blob/main/README.md>
- Models: <https://github.com/QwenLM/Qwen3/blob/main/README.md>, <https://github.com/meta-llama/llama-models/tree/main/models/llama3_2>, <https://github.com/meta-llama/llama-models/tree/main/models/llama3_1>, <https://github.com/ibm-granite/granite-3.3-language-models>, <https://github.com/ibm-granite/granite-4.0-language-models>, <https://huggingface.co/microsoft/Phi-4-mini-instruct>, <https://ai.google.dev/gemma/terms>
- Compatibility: <https://www.apache.org/legal/resolved.html>, <https://www.apache.org/licenses/GPL-compatibility.html>, <https://www.gnu.org/licenses/gpl-faq.html#MereAggregation>
- NVIDIA: <https://docs.nvidia.com/cuda/eula/index.html>
