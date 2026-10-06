"""Run Suricata on one capture file and add eve.json to the log folder (v2.0).

Suricata is optional for reading captures: if the `suricata` program is not
installed (for example on a laptop running only the unit tests), the pipeline
continues with Zeek logs alone and the report says so.
"""

import shutil
import subprocess
from pathlib import Path

HERE = Path(__file__).parent
CONFIG = HERE / "maxguard-suricata.yaml"
RULES = HERE / "rules" / "maxguard.rules"


class SuricataError(RuntimeError):
    pass


def run_suricata(pcap: Path, log_dir: Path, timeout: int = 1800) -> Path:
    """Write log_dir/eve.json for one capture. Returns the eve.json path."""
    log_dir.mkdir(parents=True, exist_ok=True)
    cmd = ["suricata", "-c", str(CONFIG), "-r", str(pcap.resolve()),
           "-l", str(log_dir), "-k", "none", "--runmode", "single", "-S", str(RULES)]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, check=False)
    except subprocess.TimeoutExpired:
        raise SuricataError(f"Suricata took longer than {timeout} seconds") from None
    if res.returncode != 0:
        raise SuricataError(res.stderr.strip() or "suricata failed")
    for extra in ("fast.log", "stats.log", "suricata.log"):  # keep only eve.json
        (log_dir / extra).unlink(missing_ok=True)
    return log_dir / "eve.json"


def run_suricata_if_available(pcap: Path, log_dir: Path) -> Path | None:
    if shutil.which("suricata") is None:
        return None
    return run_suricata(pcap, log_dir)
