"""A tiny fake Ollama for the dash-manual review: POST /api/chat only, on 127.0.0.1.

It reads the record IDs MaxGuard put in the prompt (the EVIDENCE keys) and answers
in Ollama's /api/chat (stream: false) reply shape. The reply depends on the word in
the mode file: good | bad | hostile. Every request body is appended to the log file.

usage: python3 fake_ollama.py <port> <mode file> <request log file>
"""

import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORT, MODE_FILE, LOG_FILE = int(sys.argv[1]), sys.argv[2], sys.argv[3]
MARK = "EVIDENCE (record_id -> log record):\n"
FOREIGN = "aa1f0f2c2964073b"   # the conn.log record of the same upload: real, but not this finding's
MADE_UP = "ffffffffffffffff"


def sentences(mode: str, ids: list[str]) -> list[dict]:
    first = ids[0]
    if mode == "good":
        return [
            {"text": "A device at 172.18.0.3 opened a Telnet session to 172.18.0.2 on port 23.",
             "evidence_ids": [first]},
            {"text": "Telnet sends the login and everything typed without encryption.",
             "evidence_ids": ids},
            {"text": "Turn off Telnet on 172.18.0.2 and use SSH instead.", "evidence_ids": [first]},
        ]
    if mode == "bad":
        return [
            {"text": "KEPT: A device at 172.18.0.3 opened a Telnet session to 172.18.0.2.",
             "evidence_ids": [first]},
            {"text": "DROP-FOREIGN: cites a real record of this upload that is not this finding's.",
             "evidence_ids": [FOREIGN]},
            {"text": "DROP-MADEUP: cites a record ID that exists nowhere.", "evidence_ids": [MADE_UP]},
            {"text": "DROP-MIXED: cites this finding's record and a foreign one.",
             "evidence_ids": [first, FOREIGN]},
            {"text": "DROP-NONE: cites nothing.", "evidence_ids": []},
        ]
    if mode == "hostile":
        return [
            {"text": "<script>window.__pwned=1;alert('ai')</script><b>bold?</b> <img src=x onerror=alert(2)>",
             "evidence_ids": [first]},
        ]
    raise ValueError(mode)


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):  # noqa: N802 (http.server naming)
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        with open(LOG_FILE, "a", encoding="utf-8") as log:
            log.write(json.dumps({"path": self.path, "host": self.headers.get("Host"),
                                  "body": body}) + "\n")
        if self.path != "/api/chat":
            self.send_error(404)
            return
        prompt = body["messages"][-1]["content"]
        shown = json.loads(prompt.split(MARK, 1)[1])
        mode = open(MODE_FILE, encoding="utf-8").read().strip()
        if mode == "notfound":  # Ollama runs, but the model was never pulled
            self.send_json(404, {"error": f"model '{body['model']}' not found"})
            return
        if mode == "garbage":   # a reply whose content is not the JSON we asked for
            content = "Sure! Here is my explanation: Telnet is bad."
        else:
            content = json.dumps({"sentences": sentences(mode, sorted(shown))})
        reply = {"model": body["model"], "created_at": "2026-10-27T00:00:00Z",
                 "message": {"role": "assistant", "content": content},
                 "done": True, "done_reason": "stop", "total_duration": 1, "load_duration": 1,
                 "prompt_eval_count": 1, "prompt_eval_duration": 1, "eval_count": 1,
                 "eval_duration": 1}
        self.send_json(200, reply)

    def send_json(self, code, obj):
        data = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
