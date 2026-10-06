"""Tests for maxguard.ai.ollama_client against a fake Ollama on 127.0.0.1.

The fake speaks real HTTP, so these tests also check the exact JSON body we
send. Its error replies are copied from the real server (ollama/ollama:0.12.6
and 0.35.1, model not pulled). No model ran here, so the success reply follows
the documented /api/chat shape: {"message": {"content": "<JSON text>"}, ...}.
"""

import json
import socket
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

import maxguard.rules  # noqa: F401  (importing registers every rule)
from maxguard.adapters.base import read_log
from maxguard.ai import ollama_client
from maxguard.ai.ollama_client import AIUnavailable, explain, explain_all
from maxguard.ids import record_id
from maxguard.models import Evidence, Finding
from maxguard.rules.base import RULES

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "zeek"

# Recorded from the real server: POST /api/chat with a model that is not pulled.
MODEL_NOT_FOUND = (404, {"error": "model 'qwen3:4b' not found"})


class FakeOllamaHandler(BaseHTTPRequestHandler):
    """Answers each POST with the next reply in server.replies."""

    def do_POST(self):
        length = int(self.headers["Content-Length"])
        self.server.received.append(json.loads(self.rfile.read(length)))
        status, reply = self.server.replies.pop(0)
        data = json.dumps(reply).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *args):  # keep test output quiet
        pass


@pytest.fixture
def ollama(monkeypatch):
    server = ThreadingHTTPServer(("127.0.0.1", 0), FakeOllamaHandler)
    server.replies, server.received = [], []
    # A short poll interval makes shutdown() quick at the end of each test.
    threading.Thread(target=server.serve_forever, args=(0.01,), daemon=True).start()
    monkeypatch.setenv("OLLAMA_HOST", f"http://127.0.0.1:{server.server_port}")
    monkeypatch.setenv("MAXGUARD_MODEL", "qwen3:4b")
    yield server
    server.shutdown()
    server.server_close()


def chat_reply(answer) -> tuple[int, dict]:
    """A successful /api/chat reply whose content is the model's JSON answer."""
    content = answer if isinstance(answer, str) else json.dumps(answer)
    return 200, {"model": "qwen3:4b", "done": True, "done_reason": "stop",
                 "message": {"role": "assistant", "content": content}}


def make_finding(dst_ip: str, rid: str, severity: str = "high") -> Finding:
    return Finding(rule_id="cleartext.telnet", title="Telnet session in cleartext",
                   severity=severity, src_ip="10.0.0.1", dst_ip=dst_ip, dst_port=23,
                   protocol="telnet", first_seen=1.0, last_seen=1.0,
                   evidence=[Evidence("maxguard_cleartext.log", "C1", 1.0, rid)])


def telnet_from_fixture() -> tuple[dict, dict[str, dict]]:
    """The real telnet finding and its record, from the Zeek fixture logs."""
    log_dir = FIXTURES / "telnet"
    finding = RULES["cleartext.telnet"](log_dir)[0]
    rec = next(read_log(log_dir, "maxguard_cleartext.log"))
    rid = record_id("maxguard_cleartext.log", rec)
    return finding.to_dict(), {rid: {**rec, "_log": "maxguard_cleartext.log"}}


# ---- settings ------------------------------------------------------------

def test_ollama_url_default_and_host_without_scheme(monkeypatch):
    monkeypatch.delenv("OLLAMA_HOST", raising=False)
    assert ollama_client.ollama_url() == "http://127.0.0.1:11434"
    monkeypatch.setenv("OLLAMA_HOST", "ollama:11434")  # Ollama's own short form
    assert ollama_client.ollama_url() == "http://ollama:11434"


def test_model_name_default_is_the_temporary_placeholder(monkeypatch):
    monkeypatch.delenv("MAXGUARD_MODEL", raising=False)
    assert ollama_client.model_name() == ollama_client.TEMPORARY_DEFAULT_MODEL


# ---- explain(): one finding ---------------------------------------------

def test_request_body_matches_the_spec(ollama):
    finding, records = telnet_from_fixture()
    ollama.replies.append(chat_reply({"sentences": []}))
    explain(finding, records)

    body = ollama.received[0]
    assert body["model"] == "qwen3:4b"
    assert body["stream"] is False
    assert body["think"] is False
    assert body["options"] == {"temperature": 0, "seed": 42}
    assert body["format"] == ollama_client.ANSWER_SCHEMA
    assert [m["role"] for m in body["messages"]] == ["system", "user"]
    rid = finding["evidence"][0]["record_id"]
    assert f'"{rid}"' in body["messages"][1]["content"]  # evidence is keyed by record_id


def test_keeps_cited_sentences_and_counts_dropped_ones(ollama):
    finding, records = telnet_from_fixture()
    rid = finding["evidence"][0]["record_id"]
    ollama.replies.append(chat_reply({"sentences": [
        {"text": "A Telnet session to 172.18.0.2 port 23 was seen.", "evidence_ids": [rid]},
        {"text": "The password was admin.", "evidence_ids": []},
        {"text": "It came from a botnet.", "evidence_ids": ["0000000000000000"]},
    ]}))
    kept, dropped = explain(finding, records)
    assert [s.text for s in kept] == ["A Telnet session to 172.18.0.2 port 23 was seen."]
    assert kept[0].evidence_ids == [rid]
    assert dropped == 2


def test_prompt_shows_only_this_findings_records(ollama):
    finding, records = telnet_from_fixture()
    records["ffffffffffffffff"] = {"_log": "conn.log", "note": "belongs to another finding"}
    ollama.replies.append(chat_reply({"sentences": []}))
    explain(finding, records)
    assert "ffffffffffffffff" not in ollama.received[0]["messages"][1]["content"]


def test_no_evidence_records_means_no_model_call(ollama):
    finding, _ = telnet_from_fixture()
    assert explain(finding, {}) == ([], 0)
    assert ollama.received == []


def test_answer_that_is_not_json_gives_no_sentences(ollama):
    finding, records = telnet_from_fixture()
    ollama.replies.append(chat_reply('{"sentences": [{"text": "cut off'))
    assert explain(finding, records) == ([], 0)


def test_model_not_pulled_raises_ai_unavailable(ollama):
    finding, records = telnet_from_fixture()
    ollama.replies.append(MODEL_NOT_FOUND)
    with pytest.raises(AIUnavailable, match="HTTP 404: model 'qwen3:4b' not found"):
        explain(finding, records)


def test_server_not_running_raises_ai_unavailable(monkeypatch):
    with socket.socket() as s:  # find a free port, then close it so nothing listens
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
    monkeypatch.setenv("OLLAMA_HOST", f"http://127.0.0.1:{port}")
    finding, records = telnet_from_fixture()
    with pytest.raises(AIUnavailable, match="not reachable"):
        explain(finding, records)


def test_proxy_settings_are_ignored(ollama, monkeypatch):
    # 192.0.2.1 is a documentation address (RFC 5737): nothing ever answers there.
    for name in ("HTTP_PROXY", "http_proxy", "ALL_PROXY", "all_proxy"):
        monkeypatch.setenv(name, "http://192.0.2.1:9")
    for name in ("NO_PROXY", "no_proxy"):
        monkeypatch.delenv(name, raising=False)
    finding, records = telnet_from_fixture()
    ollama.replies.append(chat_reply({"sentences": []}))
    explain(finding, records)
    assert len(ollama.received) == 1  # the request reached Ollama directly


# ---- explain_all(): many findings ---------------------------------------

@pytest.fixture
def fake_records(monkeypatch):
    """Stand-in for maxguard.events.lookup.records_for."""
    def records(log_dir, record_ids):
        return {rid: {"_log": "maxguard_cleartext.log", "ts": 1.0} for rid in record_ids}
    monkeypatch.setattr(ollama_client, "evidence_records", records)


def test_each_finding_gets_its_own_model_call(ollama, fake_records):
    # Fall 2026 bug: one answer per rule_id was reused for every finding.
    first = make_finding("10.0.0.2", "aaaa000000000001")
    second = make_finding("10.0.0.3", "bbbb000000000002")  # same rule_id
    ollama.replies.append(chat_reply({"sentences": [
        {"text": "Telnet to 10.0.0.2.", "evidence_ids": ["aaaa000000000001"]}]}))
    # If the model repeats the first answer, its citation is not this finding's.
    ollama.replies.append(chat_reply({"sentences": [
        {"text": "Telnet to 10.0.0.2.", "evidence_ids": ["aaaa000000000001"]}]}))

    status = explain_all([first, second], Path("unused"))

    assert len(ollama.received) == 2
    assert first.explanation == "Telnet to 10.0.0.2."
    assert second.explanation is None
    assert status == {"status": "ok", "model": "qwen3:4b",
                      "explained": 1, "dropped_sentences": 1, "reason": None}


def test_most_severe_first_up_to_the_limit(ollama, fake_records):
    medium = make_finding("10.0.0.2", "aaaa000000000001", severity="medium")
    high = make_finding("10.0.0.3", "bbbb000000000002", severity="high")
    ollama.replies.append(chat_reply({"sentences": [
        {"text": "High one.", "evidence_ids": ["bbbb000000000002"]}]}))

    status = explain_all([medium, high], Path("unused"), limit=1)

    assert len(ollama.received) == 1
    assert high.explanation == "High one."
    assert medium.explanation is None
    assert status["explained"] == 1


def test_explain_all_sends_the_real_evidence_records(ollama):
    # No fakes except the model: real rules, real fixture logs, real lookup.
    pytest.importorskip("maxguard.events.lookup")
    log_dir = FIXTURES / "cert_expired"
    finding = RULES["cert.expired"](log_dir)[0]
    ssl_id, x509_id = [e.record_id for e in finding.evidence]
    ollama.replies.append(chat_reply({"sentences": [
        {"text": "The server certificate had expired.", "evidence_ids": [x509_id, ssl_id]}]}))

    status = explain_all([finding], log_dir)

    prompt = ollama.received[0]["messages"][1]["content"]
    assert '"_log": "ssl.log"' in prompt and '"_log": "x509.log"' in prompt
    assert finding.explanation_sentences[0].evidence_ids == [x509_id, ssl_id]
    assert status["explained"] == 1


def test_unavailable_ai_still_returns_a_status(ollama, fake_records):
    finding = make_finding("10.0.0.2", "aaaa000000000001")
    ollama.replies.append(MODEL_NOT_FOUND)

    status = explain_all([finding], Path("unused"))

    assert status["status"] == "unavailable"
    assert status["model"] == "qwen3:4b"
    assert (status["explained"], status["dropped_sentences"]) == (0, 0)
    # The reason tells the dashboard what to show, e.g. "run: ollama pull qwen3:4b".
    assert "not found" in status["reason"]
    assert finding.explanation is None
    assert finding.explanation_sentences == []
