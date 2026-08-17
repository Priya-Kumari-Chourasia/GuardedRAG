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


# GROQ_MODEL_FALLBACK's context window is much smaller than the model this judge
# used to run on (empirically found 2026-08-17: allam-2-7b accepts ~3000 prompt
# tokens, fails above ~4000 -- see app/core/config.py's groq_model_fallback comment
# for why that model was chosen anyway). retrieve()'s top_k=8 chunks at
# ingest.py's CHUNK_TARGET_TOKENS=512 can alone reach ~4096 tokens, before the
# prompt template or answer are even added -- comfortably over the limit for
# retrieval-heavy questions. Truncating here (word-based, matching ingest.py's
# own TOKENS_PER_WORD approximation convention) trades a small loss of judge
# visibility into the tail of the context for never hard-failing G6 on a
# legitimately-answerable question purely because of judge-model context size.
_MAX_CONTEXT_WORDS = 2000


def _truncate_context(context: str) -> str:
    words = context.split()
    if len(words) <= _MAX_CONTEXT_WORDS:
        return context
    return " ".join(words[:_MAX_CONTEXT_WORDS])


async def check_groundedness(answer: str, context: str) -> GroundednessResult:
    """G6, feature-flagged via ENABLE_GROUNDEDNESS_CHECK -- see pipeline.py for
    where that flag is read and the latency delta this stage adds. Reuses
    GROQ_MODEL_FALLBACK as the judge model rather than adding a dedicated
    "judge model" setting SPEC never defines; Phase 5's Ragas harness judge
    is a separate, larger concern and can introduce its own setting if it
    turns out to need a different model.
    """
    settings = get_settings()
    prompt = _JUDGE_PROMPT.format(context=_truncate_context(context), answer=answer)
    resp = await get_groq_client().classify(settings.groq_model_fallback, [{"role": "user", "content": prompt}])
    score = float(resp.text.strip())
    score = max(0.0, min(1.0, score))
    return GroundednessResult(score=score, grounded=score >= settings.faithfulness_threshold)
