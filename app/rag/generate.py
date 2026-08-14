from __future__ import annotations

import re
from dataclasses import dataclass

from app.core.groq_client import get_groq_client
from app.rag.retriever import Hit
from app.rbac.enforce import REFUSAL_TEMPLATE

# Verbatim from SPEC §9. This prompt is a USABILITY control, not a security
# control -- the ACL filter in retriever.py has already decided what this
# user is allowed to see before any of this text is built. If the third
# paragraph below were ever doing real security work, that would mean the
# retrieval-time filter had failed.
SYSTEM_PROMPT = """You are PKC's internal knowledge assistant.

Answer ONLY from the numbered context passages below. If the passages do not
contain the answer, say so -- do not use outside knowledge.

Cite every factual claim with the passage marker, e.g. [fin-q3-2025-report::c07].

The passages have already been filtered for this user's permissions. Do not
speculate about, reference, or acknowledge the existence of any document not
shown to you.

CONTEXT:
{numbered_passages}

QUESTION: {question}"""

# Matches citation markers like [fin-q3-2025-report::c07] -- doc_id (letters,
# digits, hyphens) + "::" + chunk suffix (e.g. c07), mirroring how ingest.py
# builds chunk_id as f"{doc_id}::c{i:02d}". Accepts both ASCII [] and the
# fullwidth 【】 brackets seen from Groq's models in practice -- rejecting the
# fullwidth form would turn a correctly-cited, grounded answer into a false
# refusal, exactly backwards from what the bracket check is for.
_CITATION_RE = re.compile(r"[\[【]([\w.-]+::[\w-]+)[\]】]")


@dataclass
class Citation:
    chunk_id: str
    doc_id: str
    doc_title: str


@dataclass
class GenerationResult:
    answer: str
    citations: list[Citation]
    prompt_tokens: int
    completion_tokens: int
    latency_ms: int
    model_used: str
    refused: bool


def _format_passages(hits: list[Hit]) -> str:
    return "\n\n".join(f"[{i}] ({h.chunk_id})\n{h.chunk_text}" for i, h in enumerate(hits, start=1))


def _parse_citations(answer: str, hits: list[Hit]) -> list[Citation]:
    """Resolve citation markers the model emitted back to the actual retrieved hits.

    A marker that doesn't match any chunk_id we handed the model is dropped
    rather than trusted -- it's either a hallucinated ID or (the case that
    matters here) an attempt to reference a document the model was never
    shown. citations[] must only ever point at chunks that were already
    ACL-filtered and retrieved for this request; nothing here re-opens that
    security border, but there's no reason to surface an unverifiable one.
    """
    by_chunk_id = {h.chunk_id: h for h in hits}
    seen: dict[str, Citation] = {}
    for marker in _CITATION_RE.findall(answer):
        hit = by_chunk_id.get(marker)
        if hit is None:
            continue
        seen[marker] = Citation(chunk_id=hit.chunk_id, doc_id=hit.doc_id, doc_title=hit.doc_title)
    return list(seen.values())


async def generate_answer(
    question: str,
    hits: list[Hit],
    history: list[dict] | None = None,
) -> GenerationResult:
    """Turn retrieved (already ACL-filtered) hits into a cited answer.

    Zero hits means retrieval found nothing this user is both aware of and
    authorized to see. SPEC I4 requires that case to be byte-identical to
    "doesn't exist", so we short-circuit straight to REFUSAL_TEMPLATE instead
    of asking the LLM to write a refusal from an empty context -- that would
    burn a Groq call for no reason AND risk the model phrasing the refusal
    slightly differently each time, which would itself leak information
    (a refusal that varies is a refusal you can fingerprint).

    `history` (from app.rag.memory.get_recent_turns) is prior question/answer
    TEXT only, never prior retrieved passages -- this turn's retrieval is
    always run fresh against the current caller's roles, so history only adds
    conversational continuity, never access to anything not re-authorized
    just now.
    """
    if not hits:
        return GenerationResult(
            answer=REFUSAL_TEMPLATE,
            citations=[],
            prompt_tokens=0,
            completion_tokens=0,
            latency_ms=0,
            model_used="none",
            refused=True,
        )

    prompt = SYSTEM_PROMPT.format(numbered_passages=_format_passages(hits), question=question)
    messages = [*(history or []), {"role": "user", "content": prompt}]
    response = await get_groq_client().chat(messages)
    citations = _parse_citations(response.text, hits)

    # Non-empty hits doesn't mean a groundable answer -- retrieval can return
    # chunks that are authorized but irrelevant to the question, and the model
    # then writes its OWN "the passages don't cover this" sentence instead of
    # using REFUSAL_TEMPLATE. Free-form wording here is exactly the I4
    # violation the zero-hits branch above exists to prevent, just reached a
    # different way: a refusal whose phrasing varies is fingerprintable. Since
    # SPEC §9 also requires every factual claim to carry a citation marker, an
    # answer with zero RESOLVED citations (real answer or hallucinated one)
    # is never a claim we should surface -- collapse it to the same byte-exact
    # refusal. Token counts are still reported: unlike the zero-hits case, a
    # Groq call really did happen here.
    if not citations:
        return GenerationResult(
            answer=REFUSAL_TEMPLATE,
            citations=[],
            prompt_tokens=response.prompt_tokens,
            completion_tokens=response.completion_tokens,
            latency_ms=response.latency_ms,
            model_used=response.model_used,
            refused=True,
        )

    return GenerationResult(
        answer=response.text,
        citations=citations,
        prompt_tokens=response.prompt_tokens,
        completion_tokens=response.completion_tokens,
        latency_ms=response.latency_ms,
        model_used=response.model_used,
        refused=False,
    )
