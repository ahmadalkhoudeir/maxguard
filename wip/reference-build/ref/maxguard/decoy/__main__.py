"""Run the decoys: python -m maxguard.decoy (Fiona, FIO-06).

Settings come from environment variables, so docker/decoy-compose.yaml can set them:
  MAXGUARD_DECOY_PORTS    services and ports, default "telnet=23,ftp=21,http=80"
  MAXGUARD_DECOY_LOG      where decoy.log goes, default "decoy.log"
  MAXGUARD_DECOY_HOST     address to listen on, default "0.0.0.0" (all of the container's)
  MAXGUARD_DECOY_TIMEOUT  seconds to wait for a client, default 5
"""

from __future__ import annotations

import asyncio
import os
from pathlib import Path

from maxguard.decoy.service import DEFAULT_TIMEOUT, parse_ports, serve_forever


def main() -> None:
    ports = parse_ports(os.environ.get("MAXGUARD_DECOY_PORTS", "telnet=23,ftp=21,http=80"))
    log_path = Path(os.environ.get("MAXGUARD_DECOY_LOG", "decoy.log"))
    host = os.environ.get("MAXGUARD_DECOY_HOST", "0.0.0.0")
    timeout = float(os.environ.get("MAXGUARD_DECOY_TIMEOUT", DEFAULT_TIMEOUT))
    log_path.parent.mkdir(parents=True, exist_ok=True)
    asyncio.run(serve_forever(ports, log_path, host=host, timeout=timeout))


if __name__ == "__main__":
    main()
