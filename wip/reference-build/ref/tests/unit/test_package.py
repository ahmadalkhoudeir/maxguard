"""The first test in the repository: the package imports and has a version.

It exists so CI has something to run from day one (pytest fails when it finds
no tests at all).
"""

import maxguard


def test_package_imports_and_has_a_version():
    assert maxguard.__version__ == "2.0.0a0"
