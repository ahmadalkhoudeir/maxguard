"""Tests for maxguard.ai.citations.validate (CLAUDE.md rule 3)."""

from maxguard.ai.citations import validate
from maxguard.models import Sentence

ALLOWED = {"aaaa000000000001", "aaaa000000000002"}


def answer(*sentences: dict) -> dict:
    return {"sentences": list(sentences)}


def test_keeps_sentence_whose_ids_are_all_allowed():
    raw = answer({"text": "Telnet was used.", "evidence_ids": ["aaaa000000000001"]})
    kept, dropped = validate(raw, ALLOWED)
    assert kept == [Sentence("Telnet was used.", ["aaaa000000000001"])]
    assert dropped == 0


def test_drops_sentence_without_evidence():
    raw = answer({"text": "Telnet is old.", "evidence_ids": []})
    assert validate(raw, ALLOWED) == ([], 1)


def test_drops_sentence_with_one_unknown_id():
    # One good ID does not rescue a sentence that also cites a made-up one.
    raw = answer({"text": "Mixed.", "evidence_ids": ["aaaa000000000001", "ffff000000000009"]})
    assert validate(raw, ALLOWED) == ([], 1)


def test_drops_empty_or_missing_text():
    raw = answer({"text": "   ", "evidence_ids": ["aaaa000000000001"]},
                 {"evidence_ids": ["aaaa000000000001"]})
    assert validate(raw, ALLOWED) == ([], 2)


def test_drops_items_with_wrong_types():
    raw = answer("not a dict",
                 {"text": "ids is a string", "evidence_ids": "aaaa000000000001"},
                 {"text": "id is a number", "evidence_ids": [12]})
    assert validate(raw, ALLOWED) == ([], 3)


def test_counts_kept_and_dropped_together():
    raw = answer({"text": "Good.", "evidence_ids": ["aaaa000000000002"]},
                 {"text": "Bad.", "evidence_ids": ["nope"]})
    kept, dropped = validate(raw, ALLOWED)
    assert [s.text for s in kept] == ["Good."]
    assert dropped == 1


def test_strips_text_and_removes_repeated_ids():
    raw = answer({"text": "  Seen twice.  ",
                  "evidence_ids": ["aaaa000000000002", "aaaa000000000001", "aaaa000000000002"]})
    kept, _ = validate(raw, ALLOWED)
    assert kept == [Sentence("Seen twice.", ["aaaa000000000002", "aaaa000000000001"])]


def test_answer_without_sentences_list_gives_nothing():
    assert validate({}, ALLOWED) == ([], 0)
    assert validate({"sentences": "oops"}, ALLOWED) == ([], 0)
    assert validate([], ALLOWED) == ([], 0)  # model answered a list, not an object
