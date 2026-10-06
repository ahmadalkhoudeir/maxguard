"""OPNsense enforcer: put an approved address in a firewall alias (Ahmad, AHM-08).

Optional. Without it, MaxGuard shows the commands and a person applies them by
hand. With it, MaxGuard asks the user's own OPNsense firewall, through its API,
to add the address to an alias that the user's block rules already use.

The endpoints, read from the OPNsense source (opnsense/core, commit
1177021c22d6dedb63ff9bffd6300e789a8822e2, 2026-10-06):
- POST /api/firewall/alias_util/add/<alias>     body {"address": "<ip>"} -> {"status": "done"}
- POST /api/firewall/alias_util/delete/<alias>  body {"address": "<ip>"} -> {"status": "done"}
  src/opnsense/mvc/app/controllers/OPNsense/Firewall/Api/AliasUtilController.php
  (addAction, deleteAction). Both update the alias in the configuration AND the
  live pf table at once ("pfctl -t <alias> -T add <ip>",
  src/opnsense/service/conf/actions.d/actions_filter.conf, [add.table]).
- POST /api/firewall/alias/reconfigure                                 -> {"status": "ok"}
  src/opnsense/mvc/app/controllers/OPNsense/Firewall/Api/AliasController.php
  (reconfigureAction): the "Apply" button for aliases.
- A JSON body is read like a form (ApiControllerBase.php, parseJsonBodyData).
- API key: a file with the lines "key=..." and "secret=...", sent with HTTP basic
  auth (opnsense/docs repository, source/development/how-tos/api.rst).
- Least privilege for the API user (src/opnsense/mvc/app/models/OPNsense/Core/ACL/ACL.xml):
  "Diagnostics: PF Table IP addresses" (api/firewall/alias_util/*) and
  "Firewall: Alias: Edit" (api/firewall/alias/*).

Safety:
- https only, TLS verification always on. A firewall with its own certificate
  authority: give its CA file (MAXGUARD_OPNSENSE_CA).
- The API key lives in the data folder (data/opnsense/apikey.txt), never in the
  repository. Proxy settings from the environment are ignored: the request goes
  straight to the firewall on the user's own network.
- With the offline guard on (MAXGUARD_OFFLINE=1), add the firewall's host name or
  IP to MAXGUARD_OFFLINE_ALLOW, or every request fails with OfflineViolation.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from urllib.parse import urlparse

import requests

from maxguard.offline import OfflineViolation
from maxguard.response.enforcers.base import EnforcerError
from maxguard.response.generate import parse_ip

TIMEOUT = (5.0, 20.0)  # seconds to connect, seconds to wait for an answer
ALIAS_NAME = re.compile(r"[A-Za-z0-9_]{1,32}")  # OPNsense alias names: letters, digits, _
KEY_FILE = Path("opnsense") / "apikey.txt"      # inside the data folder


class OPNsenseEnforcer:
    """Adds and removes addresses in one OPNsense alias."""

    def __init__(self, base_url: str, key: str, secret: str, *, alias: str,
                 ca_file: str | None = None):
        if urlparse(base_url).scheme != "https":
            raise ValueError("the OPNsense URL must start with https://")
        if not ALIAS_NAME.fullmatch(alias):
            raise ValueError(f"not an OPNsense alias name: {alias!r}")
        self.base_url = base_url.rstrip("/")
        self.alias = alias
        self.session = requests.Session()
        self.session.auth = (key, secret)
        self.session.verify = ca_file or True   # never False
        self.session.trust_env = False          # no proxy, no ~/.netrc: straight to the firewall

    def add(self, ip: str) -> None:
        address = str(parse_ip(ip))  # checked again here: only a clean address is sent
        self.post(f"/api/firewall/alias_util/add/{self.alias}", {"address": address}, "done")

    def remove(self, ip: str) -> None:
        address = str(parse_ip(ip))
        self.post(f"/api/firewall/alias_util/delete/{self.alias}", {"address": address},
                  "done")

    def apply(self) -> None:
        self.post("/api/firewall/alias/reconfigure", {}, "ok")

    def post(self, path: str, body: dict, expected: str) -> None:
        """POST JSON and check OPNsense's {"status": ...} answer."""
        try:
            response = self.session.post(self.base_url + path, json=body, timeout=TIMEOUT,
                                         allow_redirects=False)
        except OfflineViolation as err:
            raise EnforcerError(f"{err} (add the firewall to MAXGUARD_OFFLINE_ALLOW)") from err
        except requests.RequestException as err:
            raise EnforcerError(f"OPNsense not reachable: {err}") from err
        if response.status_code != 200:
            raise EnforcerError(f"OPNsense answered HTTP {response.status_code} for {path}")
        try:
            status = response.json().get("status")
        except (ValueError, AttributeError):
            raise EnforcerError(f"OPNsense sent an answer that is not JSON for {path}") from None
        if status != expected:
            raise EnforcerError(f"OPNsense said {status!r} for {path} (expected {expected!r})")


def read_api_key(path: Path) -> tuple[str, str]:
    """Read the key file OPNsense lets you download once: lines key=... and secret=..."""
    values = {}
    for line in Path(path).read_text().splitlines():
        name, sep, value = line.strip().partition("=")  # the secret itself may end in "="
        if sep:
            values[name] = value
    if not values.get("key") or not values.get("secret"):
        raise EnforcerError(f"{path} needs a key=... line and a secret=... line")
    return values["key"], values["secret"]


def from_env(data_dir: Path, alias: str) -> OPNsenseEnforcer | None:
    """The enforcer the user configured, or None when MAXGUARD_OPNSENSE_URL is not set."""
    url = os.environ.get("MAXGUARD_OPNSENSE_URL")
    if not url:
        return None
    key_file = Path(data_dir) / KEY_FILE
    if not key_file.is_file():
        raise EnforcerError(f"MAXGUARD_OPNSENSE_URL is set but {key_file} does not exist")
    key, secret = read_api_key(key_file)
    return OPNsenseEnforcer(url, key, secret, alias=alias,
                            ca_file=os.environ.get("MAXGUARD_OPNSENSE_CA") or None)
