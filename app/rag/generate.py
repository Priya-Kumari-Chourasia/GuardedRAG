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
# fullwidth 【】 brackets seen from Groq's models in practice, AND both ASCII
# hyphen (U+002D) and the Unicode look-alikes Groq's models have been
# observed substituting inside doc_ids -- confirmed live: "diwali holiday"
# question came back as 【co‑holiday‑calendar‑2026::c02】 using U+2011
# NON-BREAKING HYPHEN throughout, which the ASCII-only class silently failed
# to match, treating a correctly-cited, grounded answer as uncited. Same
# failure shape as the fullwidth-bracket case: rejecting a look-alike
# character turns a good answer into a false refusal, exactly backwards from
# what this check exists for.
#
# Public (not _-prefixed): app.guardrails.citations (G7) reuses this exact
# pattern rather than maintaining a second regex that could drift out of
# sync with what this module actually parses.
_HYPHENS = r"\-‐‑‒–"
CITATION_RE = re.compile(rf"[\[【]([\w.{_HYPHENS}]+::[\w{_HYPHENS}]+)[\]】]")


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
    for marker in CITATION_RE.findall(answer):
        # Normalize Unicode hyphen look-alikes back to ASCII before lookup --
        # real chunk_ids (built in ingest.py) only ever use ASCII '-'.
        # Without this, a marker the regex above correctly recognized as
        # citation-shaped would still fail to resolve to any hit.
        normalized = re.sub(f"[{_HYPHENS}]", "-", marker)
        hit = by_chunk_id.get(normalized)
        if hit is None:
            continue
        seen[normalized] = Citation(chunk_id=hit.chunk_id, doc_id=hit.doc_id, doc_title=hit.doc_title)
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

    # Non-empty hits doesn't guarantee a groundable answer -- retrieval can
    # return chunks that are authorized but irrelevant, and the model then
    # writes its OWN "the passages don't cover this" sentence with zero
    # resolvable citation markers. That case is NOT collapsed here: it is
    # exactly what G7 (app.guardrails.citations / pipeline.py) exists to
    # catch, per SPEC §4.4's "zero found -> regenerate once, then suppress".
    # Collapsing it here too would make G7's regenerate-once step
    # unreachable, since by the time the pipeline saw the result it would
    # already be an unconditional refusal.
    return GenerationResult(
        answer=response.text,
        citations=citations,
        prompt_tokens=response.prompt_tokens,
        completion_tokens=response.completion_tokens,
        latency_ms=response.latency_ms,
        model_used=response.model_used,
        refused=False,
    )
