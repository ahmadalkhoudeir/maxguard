"""Start the AHM-03 dashboard on 127.0.0.1:<port> with synthetic alerts already stored.

Usage: python serve.py <repo> <data_dir> <port> [seed]
seed: "basic" (telnet, ftp, plain_http, cert_expired fixtures) or "none".
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

repo, data_dir, port = Path(sys.argv[1]), Path(sys.argv[2]), int(sys.argv[3])
seed = sys.argv[4] if len(sys.argv) > 4 else "basic"
sys.path.insert(0, str(repo))

import uvicorn  # noqa: E402

from maxguard.api.app import create_app  # noqa: E402
from maxguard.pipeline import analyze  # noqa: E402

app = create_app(data_dir, explain=False)
if seed == "basic" and not app.state.state_store.list_alerts():
    for i, name in enumerate(["telnet", "ftp", "plain_http", "cert_expired"]):
        report = analyze(repo / "tests/fixtures/zeek" / name, tempfile.mkdtemp(), explain=False)
        app.state.state_store.save_analysis(report, received_at=1791300000.0 + i)
import os  # noqa: E402
uvicorn.run(app, host="127.0.0.1", port=port, log_level=os.environ.get("LOG_LEVEL", "warning"),
            timeout_graceful_shutdown=(float(os.environ["GRACE"]) if os.environ.get("GRACE") else None))
