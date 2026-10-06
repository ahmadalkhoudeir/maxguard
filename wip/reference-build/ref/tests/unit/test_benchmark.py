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
