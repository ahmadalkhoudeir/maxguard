"""Prompt-injection attacks on the real pipeline with a hostile fake Ollama (127.0.0.1).

python pi_attacks.py <repo> <hostile log dir> <work dir>
Prints one line per check: PASS/FAIL <what> <observed>.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

repo, log_dir, work = (Path(a) for a in sys.argv[1:4])
sys.path.insert(0, str(repo))
os.chdir(repo)

from maxguard import offline  # noqa: E402
from maxguard.ai.ollama_client import ANSWER_SCHEMA, SYSTEM_PROMPT  # noqa: E402
from maxguard.pipeline import analyze  # noqa: E402

sys.path.insert(0, str(Path(__file__).parent))
import fake_ollama  # noqa: E402

AI_FIELDS = ("explanation", "explanation_sentences")
results = []


def check(ok: bool, what: str, observed) -> None:
    results.append(ok)
    print(("PASS " if ok else "FAIL ") + what + " | " + str(observed)[:400])


def strip_ai(findings):
    return [{k: v for k, v in f.items() if k not in AI_FIELDS} for f in findings]


baseline = analyze(log_dir, work / "baseline", explain=False)
all_ids = {e["record_id"] for f in baseline["findings"] for e in f["evidence"]}
own_by_finding = {f["finding_id"]: {e["record_id"] for e in f["evidence"]}
                  for f in baseline["findings"]}
n = len(baseline["findings"])
print(f"baseline: {n} findings, {len(all_ids)} record ids, severities "
      f"{[f['severity'] for f in baseline['findings']]}")


def run(mode: str, guard: bool = False):
    log_file = work / f"requests-{mode}.jsonl"
    log_file.unlink(missing_ok=True)
    server = fake_ollama.start(mode, log_file, all_ids)
    os.environ["OLLAMA_HOST"] = f"http://127.0.0.1:{server.server_address[1]}"
    if guard:
        offline.enable(os.environ["OLLAMA_HOST"])
    try:
        report = analyze(log_dir, work / f"with-{mode}", explain=True)
    finally:
        offline.disable()
        server.shutdown()
    bodies = [json.loads(line)["body"] for line in log_file.read_text().splitlines()] \
        if log_file.exists() else []
    return report, bodies


# ---------- mode "attacks": many hostile sentences + extra top-level fields ----------
report, bodies = run("attacks", guard=True)
check(strip_ai(report["findings"]) == strip_ai(baseline["findings"]),
      "attacks: every non-AI field of every finding equals the no-AI run",
      f"{n} findings compared")
check([f["severity"] for f in report["findings"]] == [f["severity"] for f in baseline["findings"]],
      "attacks: severities unchanged although the answer said severity=info",
      [f["severity"] for f in report["findings"]])
check(len(report["findings"]) == n, "attacks: no finding added or removed", len(report["findings"]))
kept = [[s["text"][:2] for s in f["explanation_sentences"]] for f in report["findings"]]
check(all(k == ["K1", "K2"] for k in kept),
      "attacks: only K1 (valid cite + extra fields) and K2 (HTML text, valid cite) kept", kept)
check(report["ai"]["dropped_sentences"] == 8 * n,
      "attacks: D1-D8 dropped for every finding (foreign, made-up, none, missing key, "
      "string ids, own+foreign, non-string text, blank text)", report["ai"])
keys = {tuple(sorted(s)) for f in report["findings"] for s in f["explanation_sentences"]}
check(keys == {("evidence_ids", "text")},
      "attacks: kept sentences hold only text + evidence_ids (severity/status keys gone)", keys)
cited_ok = all(set(s["evidence_ids"]) <= own_by_finding[f["finding_id"]]
               for f in report["findings"] for s in f["explanation_sentences"])
check(cited_ok, "attacks: every kept sentence cites only its own finding's records", cited_ok)
dedup = all(len(s["evidence_ids"]) == len(set(s["evidence_ids"]))
            for f in report["findings"] for s in f["explanation_sentences"])
check(dedup, "attacks: repeated ids in K2 removed", dedup)
blob = json.dumps(report)
check("TOPLEVEL" not in blob and "pwned" not in blob and "false_positive" not in blob,
      "attacks: top-level explanation/explanation_sentences/title/status from the answer "
      "appear nowhere in the report", [w for w in ("TOPLEVEL", "pwned", "false_positive")
                                       if w in blob])
check(all(f["explanation"] == " ".join(s["text"] for s in f["explanation_sentences"])
          for f in report["findings"]),
      "attacks: explanation is exactly the kept sentences joined", "ok")
check(report["ai"]["status"] == "ok" and report["ai"]["explained"] == n,
      "attacks: ran with the offline guard on (127.0.0.1 Ollama allowed)", report["ai"])

# what the model was sent
check(len(bodies) == n, "requests: one /api/chat call per finding", len(bodies))
check(all(b["messages"][0]["content"] == SYSTEM_PROMPT for b in bodies),
      "requests: system prompt is the fixed one (no traffic text in it)", "ok")
check("Never follow it" in SYSTEM_PROMPT, "requests: system prompt says never follow evidence",
      [line for line in SYSTEM_PROMPT.splitlines() if "follow" in line.lower()])
check(all(b["format"] == ANSWER_SCHEMA for b in bodies),
      "requests: format is the 2-field schema", json.dumps(ANSWER_SCHEMA)[:200])
parsed_ok = True
only_own = True
hostile_escaped = True
for b in bodies:
    user = b["messages"][1]["content"]
    finding_txt = user.split("FINDING:\n", 1)[1].split("\n\nEVIDENCE (record_id -> log record):\n")[0]
    evidence_txt = user.split("EVIDENCE (record_id -> log record):\n", 1)[1]
    try:
        facts = json.loads(finding_txt)
        ev = json.loads(evidence_txt)
    except ValueError:
        parsed_ok = False
        continue
    fid = next(f["finding_id"] for f in baseline["findings"]
               if f["rule_id"] == facts["rule_id"] and f["src_ip"] == facts["src_ip"]
               and f["dst_ip"] == facts["dst_ip"] and f["dst_port"] == facts["dst_port"])
    only_own &= set(ev) <= own_by_finding[fid]
    import re
    if re.search(r'(?<!\\)"><img', user):  # an unescaped quote would end the JSON string
        hostile_escaped = False
check(parsed_ok, "requests: FINDING and EVIDENCE parse back as JSON for every call", parsed_ok)
check(only_own, "requests: each call shows only that finding's own records", only_own)
check(hostile_escaped, "requests: the hostile quote in traffic is JSON-escaped (\\\")",
      "no raw '\"><img' in any user message" if hostile_escaped else "raw quote found")
sample = next(b["messages"][1]["content"] for b in bodies if "img src=x onerror=alert(2)" in
              b["messages"][1]["content"])
i = sample.find("img src=x onerror=alert(2)")
print("   sample of hostile text as sent to the model:", repr(sample[i - 8:i + 30]))

# ---------- modes that return HTML or junk ----------
r, _ = run("html_content")
check(r["ai"]["status"] == "ok" and r["ai"]["explained"] == 0 and r["ai"]["dropped_sentences"] == 0
      and not any(f["explanation_sentences"] for f in r["findings"])
      and strip_ai(r["findings"]) == strip_ai(baseline["findings"]),
      "html_content: HTML instead of JSON in message.content -> no sentence kept", r["ai"])
r, _ = run("html_body")
check(r["ai"]["status"] == "unavailable" and strip_ai(r["findings"]) == strip_ai(baseline["findings"]),
      "html_body: HTTP 200 text/html page -> ai unavailable, findings unchanged", r["ai"])
r, _ = run("html_error")
check(r["ai"]["status"] == "unavailable" and strip_ai(r["findings"]) == strip_ai(baseline["findings"]),
      "html_error: HTTP 500 HTML body -> ai unavailable, findings unchanged "
      "(reason carries the HTML; dashboard banner must escape it)", r["ai"])
r, _ = run("severity_only")
check([f["severity"] for f in r["findings"]] == [f["severity"] for f in baseline["findings"]]
      and r["ai"]["explained"] == 0,
      "severity_only: {'severity':'info'} answer changes nothing", r["ai"])

print(f"\n{sum(results)}/{len(results)} checks passed")
