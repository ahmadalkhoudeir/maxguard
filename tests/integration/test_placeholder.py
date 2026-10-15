"""Placeholder so the `integration` marker has something to filter.

KAR-03 replaces this with the real pipeline test on every capture.
"""

import pytest


@pytest.mark.integration
def test_engine_pipeline_placeholder():
    pytest.skip("Integration tests arrive with KAR-03 and run in the engine image")
