"""serve.py, but with Referrer-Policy: no-referrer (to test the guide's claim) and AI sentences on.
Usage: python serve_variant.py <repo> <data_dir> <port> <referrer-policy>"""
import copy, sys, tempfile
from pathlib import Path
repo, data_dir, port, policy = Path(sys.argv[1]), Path(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
sys.path.insert(0, str(repo))
import uvicorn
from maxguard.api.app import create_app
from maxguard.pipeline import analyze
from maxguard.web import routes
routes.SECURITY_HEADERS["Referrer-Policy"] = policy
app = create_app(data_dir, explain=False)
report = analyze(repo / "tests/fixtures/zeek/telnet", tempfile.mkdtemp(), explain=False)
for f in report["findings"]:
    f["explanation_sentences"] = [{"text": "A device logged in with Telnet.", "evidence_ids": [e["record_id"] for e in f["evidence"]]}]
report["ai"] = {"status": "ok", "model": "test", "explained": 1, "dropped_sentences": 0, "reason": None}
app.state.state_store.save_analysis(report, received_at=1791300000.0)
uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning")
