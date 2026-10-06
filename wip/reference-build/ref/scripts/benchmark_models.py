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
