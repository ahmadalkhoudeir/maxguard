"""Shared test helpers: where the fixture logs and test captures live.

pytest loads this file automatically before any test. Tests get the helpers as
fixtures (arguments), for example:

    def test_telnet(fixture_dir):
        log_dir = fixture_dir("telnet")   # tests/fixtures/zeek/telnet

Code that runs while pytest collects tests (for example a
@pytest.mark.parametrize list) cannot use fixtures; it can use the constants:

    from conftest import CAPTURE_NAMES
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
TESTS_DIR = REPO_ROOT / "tests"
FIXTURES = TESTS_DIR / "fixtures" / "zeek"  # Zeek JSON logs + eve.json per capture
PCAPS = TESTS_DIR / "pcaps"  # the synthetic lab captures

# One folder per lab capture. Folders starting with "_" hold hand-made extras.
# Empty until Karthik's captures and fixtures are merged (KAR-02).
CAPTURE_NAMES = sorted(
    p.name for p in FIXTURES.iterdir() if p.is_dir() and not p.name.startswith("_")
) if FIXTURES.is_dir() else []


def find_fixture_dir(name: str) -> Path:
    """tests/fixtures/zeek/<name>, e.g. "telnet" or "_handmade/dns_dhcp"."""
    path = FIXTURES / name
    if not path.is_dir():
        raise FileNotFoundError(f"no fixture folder {path}")
    return path


def find_pcap(name: str) -> Path:
    """tests/pcaps/<name>.pcap, e.g. find_pcap("telnet")."""
    path = PCAPS / f"{name}.pcap"
    if not path.is_file():
        raise FileNotFoundError(f"no test capture {path}")
    return path


@pytest.fixture
def fixture_dir() -> Callable[[str], Path]:
    """Returns a function: fixture_dir("telnet") -> Path to that fixture folder."""
    return find_fixture_dir


@pytest.fixture
def pcap_file() -> Callable[[str], Path]:
    """Returns a function: pcap_file("telnet") -> Path to tests/pcaps/telnet.pcap."""
    return find_pcap


@pytest.fixture(autouse=True)
def allow_test_client_host(monkeypatch):
    """The API answers only host names in MAXGUARD_ALLOWED_HOSTS (JAI-07), and FastAPI's
    TestClient calls the app "testserver". autouse: every test gets it without asking."""
    monkeypatch.setenv("MAXGUARD_ALLOWED_HOSTS", "testserver,localhost,127.0.0.1,[::1]")
