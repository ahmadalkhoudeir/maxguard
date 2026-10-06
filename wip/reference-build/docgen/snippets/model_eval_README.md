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
