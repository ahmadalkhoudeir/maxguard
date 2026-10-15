"""Smoke test: proves pytest collects and runs tests from tests/unit/.

Replace or extend this once real unit tests land (JAI-02 onward).
"""

import sys


def test_python_version_is_supported():
    # MaxGuard v2.0 targets Python 3.11 or newer (see CLAUDE.md).
    assert sys.version_info >= (3, 11)
