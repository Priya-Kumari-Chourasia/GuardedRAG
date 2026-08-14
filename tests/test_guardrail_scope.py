"""G3 (out-of-scope) -- PLAN.md Phase 4 task 4.3.

Live calls: embedding is local (FastEmbed), the tiebreak call (only reached
when cosine similarity is already low) goes to Groq. Depends on
data/corpus_centroid.json, written by `python -m scripts.ingest`."""

import asyncio

from app.guardrails.scope import check_scope


def test_in_scope_question_passes_on_cosine_alone():
    result = asyncio.run(check_scope("What is the company holiday calendar for 2026?"))
    assert result.in_scope is True
    assert result.tiebreak_used is False


def test_off_topic_question_is_out_of_scope():
    # The exact PLAN.md demo case ("what's the weather in Pune?") -- low
    # cosine against the PKC corpus centroid, and the LLM tiebreak should
    # agree it isn't plausibly about PKC Technologies.
    result = asyncio.run(check_scope("What's the weather in Pune?"))
    assert result.in_scope is False
