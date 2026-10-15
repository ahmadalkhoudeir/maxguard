"""Shared pytest setup for MaxGuard.

Registers the `integration` marker so `pytest -m "not integration"` works
without "unknown marker" warnings. When JAI-01 adds `pyproject.toml`, this
registration can move to `[tool.pytest.ini_options]`.
"""


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "integration: needs Zeek/Suricata (the engine image); skipped by "
        '`pytest -m "not integration"` and run by CI inside the engine image',
    )
