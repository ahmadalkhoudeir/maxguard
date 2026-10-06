"""Contract 3: the input adapter interface.

Unchanged from the Fall 2026 roadmap. v2.0 note: the directory returned by
to_zeek_logs() may also contain Suricata's eve.json (one JSON object per line),
which rules read with the same read_log() helper: read_log(log_dir, "eve.json").
"""

from collections.abc import Iterator
from pathlib import Path
from typing import Protocol


class InputAdapter(Protocol):
    name: str

    def accepts(self, path: Path) -> bool: ...

    def to_zeek_logs(self, path: Path, workdir: Path) -> Path:
        """Return a directory of Zeek JSON logs (one object per line)."""


def read_log(log_dir: Path, log_name: str) -> Iterator[dict]:
    """Yield records from e.g. conn.log; yield nothing if the file is absent."""
    import json

    p = log_dir / log_name
    if not p.exists():
        return
    with p.open() as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                yield json.loads(line)
