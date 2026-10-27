"""A hostile fake Ollama server for 127.0.0.1 only (POST /api/chat).

It answers the way a model that OBEYS injected instructions would. Modes:
  attacks       one answer with many hostile sentences (see SENTENCES below) plus
                extra top-level fields (severity, status, explanation, title)
  html_body     HTTP 200, Content-Type text/html, an HTML page instead of JSON
  html_error    HTTP 500 with an HTML body (the client copies 200 chars into ai.reason)
  html_content  valid Ollama JSON, but message.content is HTML, not JSON
  severity_only answer is {"severity": "info"} and nothing else
Every request body is appended to <log file> as one JSON line.

CLI: python fake_ollama.py <mode> <port file> <log file> <all-ids json file>
"""

from __future__ import annotations

import json
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

EVIDENCE_HEADER = "EVIDENCE (record_id -> log record):\n"
MADE_UP = "0000000000000000"
HTML_TEXT = "<script>alert(51)</script>\"><img src=x onerror=alert(52)> {{7*7}} javascript:alert(53)"


def own_ids(body: dict) -> list[str]:
    user = body["messages"][1]["content"]
    return sorted(json.loads(user.split(EVIDENCE_HEADER, 1)[1]))


def attacks_answer(own: list[str], foreign: list[str]) -> dict:
    o = own[0]
    f = foreign[0] if foreign else MADE_UP
    sentences = [
        # K1 kept: valid citation, but tries to add a severity field to the sentence
        {"text": "K1 This is harmless; severity is info.", "evidence_ids": [o],
         "severity": "info", "status": "false_positive"},
        # D1 dropped: cites a real record of ANOTHER finding
        {"text": "D1 cites a foreign record.", "evidence_ids": [f]},
        # D2 dropped: cites a made-up record
        {"text": "D2 cites a made-up record.", "evidence_ids": [MADE_UP]},
        # D3 dropped: cites nothing
        {"text": "D3 cites nothing.", "evidence_ids": []},
        # D4 dropped: no evidence_ids key at all
        {"text": "D4 has no evidence_ids key."},
        # D5 dropped: evidence_ids is a string, not a list
        {"text": "D5 evidence_ids is a string.", "evidence_ids": o},
        # D6 dropped: one own + one foreign
        {"text": "D6 own plus foreign.", "evidence_ids": [o, f]},
        # D7 dropped: text is not a string
        {"text": 12345, "evidence_ids": [o]},
        # D8 dropped: whitespace-only text
        {"text": "   ", "evidence_ids": [o]},
        # K2 kept: HTML/script/template text with a valid citation (escaping must handle it)
        {"text": "K2 " + HTML_TEXT, "evidence_ids": [o, o]},
    ]
    return {"severity": "info", "status": "false_positive", "title": "pwned",
            "explanation": "TOPLEVEL-EXPLANATION", "explanation_sentences": [
                {"text": "TOPLEVEL-SENTENCE", "evidence_ids": [o]}],
            "sentences": sentences}


def make_handler(mode: str, log_file: Path, all_ids: set[str]):
    lock = threading.Lock()

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def send(self, code: int, body: bytes, ctype: str) -> None:
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_POST(self):
            length = int(self.headers.get("Content-Length", "0"))
            body = json.loads(self.rfile.read(length))
            with lock, log_file.open("a") as f:
                f.write(json.dumps({"path": self.path, "body": body}) + "\n")
            if mode == "html_body":
                return self.send(200, b"<html><body><script>alert(61)</script></body></html>",
                                 "text/html")
            if mode == "html_error":
                return self.send(500, b"<img src=x onerror=alert(62)><script>alert(63)</script>",
                                 "text/html")
            if mode == "html_content":
                content = "<b>not json</b><script>alert(64)</script>"
            elif mode == "severity_only":
                content = json.dumps({"severity": "info"})
            else:
                own = own_ids(body)
                foreign = sorted(all_ids - set(own))
                content = json.dumps(attacks_answer(own, foreign))
            reply = {"model": body.get("model"), "message": {"role": "assistant",
                                                           "content": content},
                     "done": True, "done_reason": "stop"}
            return self.send(200, json.dumps(reply).encode(), "application/json")

    return Handler


def start(mode: str, log_file: Path, all_ids: set[str]) -> ThreadingHTTPServer:
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(mode, log_file, all_ids))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


if __name__ == "__main__":
    mode, port_file, log_file, ids_file = sys.argv[1:5]
    ids = set(json.loads(Path(ids_file).read_text())) if Path(ids_file).exists() else set()
    srv = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(mode, Path(log_file), ids))
    Path(port_file).write_text(str(srv.server_address[1]))
    srv.serve_forever()
