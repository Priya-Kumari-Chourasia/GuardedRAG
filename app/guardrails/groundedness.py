from __future__ import annotations

from dataclasses import dataclass

from app.core.config import get_settings
from app.core.groq_client import get_groq_client

_JUDGE_PROMPT = """You are a strict faithfulness judge. Given CONTEXT passages and an \
ANSWER, score from 0.0 to 1.0 how well the answer is supported ONLY by the context \
(no outside knowledge, no unsupported claims). Respond with ONLY the numeric score, \
nothing else -- no words, no explanation.

CONTEXT:
{context}

ANSWER:
{answer}

SCORE:"""


@dataclass
class GroundednessResult:
    score: float
    grounded: bool


async def check_groundedness(answer: str, context: str) -> GroundednessResult:
    """G6, feature-flagged via ENABLE_GROUNDEDNESS_CHECK -- see pipeline.py for
    where that flag is read and the latency delta this stage adds. Reuses
    GROQ_MODEL_FALLBACK as the judge model rather than adding a dedicated
    "judge model" setting SPEC never defines; Phase 5's Ragas harness judge
    is a separate, larger concern and can introduce its own setting if it
    turns out to need a different model.
    """
    settings = get_settings()
    prompt = _JUDGE_PROMPT.format(context=context, answer=answer)
    resp = await get_groq_client().classify(settings.groq_model_fallback, [{"role": "user", "content": prompt}])
    score = float(resp.text.strip())
    score = max(0.0, min(1.0, score))
    return GroundednessResult(score=score, grounded=score >= settings.faithfulness_threshold)
