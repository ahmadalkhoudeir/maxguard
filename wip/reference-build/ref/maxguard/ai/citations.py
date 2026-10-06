"""Citation check for AI sentences (CLAUDE.md rule 3).

The model is asked to cite evidence, but a prompt is only a request. This
module is the part that enforces it: a sentence survives only if it cites at
least one record ID and every ID it cites belongs to the finding being
explained. Anything else is dropped and counted.
"""

from __future__ import annotations

from maxguard.models import Sentence


def validate(raw: dict, allowed_ids: set[str]) -> tuple[list[Sentence], int]:
    """Keep only well-cited sentences from the model's answer.

    raw looks like {"sentences": [{"text": "...", "evidence_ids": ["..."]}]}.
    Returns (kept_sentences, number_of_dropped_sentences).
    """
    items = raw.get("sentences") if isinstance(raw, dict) else None
    if not isinstance(items, list):
        return [], 0  # no sentences at all: nothing to keep, nothing to drop

    kept: list[Sentence] = []
    dropped = 0
    for item in items:
        sentence = check_sentence(item, allowed_ids)
        if sentence is None:
            dropped += 1
        else:
            kept.append(sentence)
    return kept, dropped


def check_sentence(item: object, allowed_ids: set[str]) -> Sentence | None:
    """Return a Sentence if this one item passes every check, else None."""
    if not isinstance(item, dict):
        return None
    text = item.get("text")
    ids = item.get("evidence_ids")
    if not isinstance(text, str) or not text.strip():
        return None
    if not isinstance(ids, list) or not ids:
        return None  # rule 3: no evidence, no sentence
    if not all(isinstance(i, str) and i in allowed_ids for i in ids):
        return None  # one made-up or foreign ID is enough to reject the sentence
    unique_ids = list(dict.fromkeys(ids))  # drop repeats, keep the model's order
    return Sentence(text=text.strip(), evidence_ids=unique_ids)
