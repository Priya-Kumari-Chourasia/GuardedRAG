"""G6 (groundedness) -- PLAN.md Phase 4 task 4.4, feature-flagged via
ENABLE_GROUNDEDNESS_CHECK (not exercised here -- that flag gates the
pipeline's use of this stage, not the stage itself). Live LLM-as-judge call
against Groq."""

import asyncio

from app.guardrails.groundedness import check_groundedness

_CONTEXT = (
    "[1] (co-holiday-calendar-2026::c00)\n"
    "PKC Technologies observes the following holidays in 2026: Republic Day "
    "(Jan 26), Holi (Mar 4), Independence Day (Aug 15), Diwali (Nov 8), and "
    "Christmas (Dec 25). The office is closed on all five dates."
)


def test_answer_supported_by_context_is_grounded():
    answer = "PKC's 2026 holidays include Republic Day (Jan 26) and Diwali (Nov 8) [co-holiday-calendar-2026::c00]."
    result = asyncio.run(check_groundedness(answer, _CONTEXT))
    assert result.grounded is True
    assert result.score >= 0.7


def test_answer_contradicting_context_is_not_grounded():
    answer = "PKC's offices remain open on all public holidays, including Diwali and Christmas."
    result = asyncio.run(check_groundedness(answer, _CONTEXT))
    assert result.grounded is False
    assert result.score < 0.7
