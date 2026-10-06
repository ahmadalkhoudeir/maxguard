"""Local AI layer and Home mode text.

- ollama_client.py: evidence-citing explanations from a local Ollama model.
- citations.py: drops any AI sentence that does not cite this finding's records.
- home_text.yaml: plain-language headline and action per rule_id for Home mode.
  People write it, not the AI, so it is the same on every machine.
"""

from __future__ import annotations

from pathlib import Path

import yaml

HOME_TEXT_PATH = Path(__file__).with_name("home_text.yaml")


def load_home_text() -> dict[str, dict[str, str]]:
    """{rule_id: {"headline": ..., "action": ...}} from home_text.yaml."""
    return yaml.safe_load(HOME_TEXT_PATH.read_text(encoding="utf-8"))
