from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from app.core.config import get_settings
from app.core.groq_client import get_groq_client
from app.rag.embeddings import get_dense_model
from app.rag.ingest import CENTROID_PATH

_TIEBREAK_PROMPT = (
    "You are a scope classifier for PKC Technologies' internal company knowledge "
    "assistant, which only answers questions about PKC's own business, finance, "
    "HR, engineering, sales, and operations. Could the following question "
    "plausibly be about PKC Technologies internal knowledge, as opposed to a "
    "general-knowledge or off-topic question? Answer with exactly one word: "
    "YES or NO.\n\nQuestion: {question}"
)

_centroid: np.ndarray | None = None


def _load_centroid() -> np.ndarray:
    global _centroid
    if _centroid is None:
        if not Path(CENTROID_PATH).exists():
            raise FileNotFoundError(
                f"{CENTROID_PATH} is missing -- run `python -m scripts.ingest` "
                "first so G3 has a corpus centroid to compare queries against."
            )
        _centroid = np.array(json.loads(Path(CENTROID_PATH).read_text()))
    return _centroid


@dataclass
class ScopeResult:
    cosine: float
    in_scope: bool
    tiebreak_used: bool


async def check_scope(query: str) -> ScopeResult:
    """G3, two-stage per SPEC §4.4.

    Stage 1: embed the query and take its cosine similarity against the
    corpus centroid (computed once at ingest, see ingest.py). A query about
    PKC's own business should land close to the mass of PKC's own documents.

    Stage 2 (only when stage 1 looks out-of-scope): a single low-cosine score
    is a noisy signal on its own -- a short or unusually-phrased in-scope
    question can still land below OUT_OF_SCOPE_THRESHOLD. Rather than refuse
    on embedding similarity alone, ask an LLM directly whether the question
    could plausibly be about PKC. This is a real Groq call, so it's the
    expensive path -- it only runs when stage 1 already flagged a problem.
    """
    settings = get_settings()
    centroid = _load_centroid()

    query_vector = np.array(list(get_dense_model().embed([query]))[0])
    query_vector = query_vector / np.linalg.norm(query_vector)
    cosine = float(np.dot(query_vector, centroid))

    if cosine >= settings.out_of_scope_threshold:
        return ScopeResult(cosine=cosine, in_scope=True, tiebreak_used=False)

    resp = await get_groq_client().classify(
        settings.groq_model_fallback,
        [{"role": "user", "content": _TIEBREAK_PROMPT.format(question=query)}],
    )
    in_scope = resp.text.strip().upper().startswith("Y")
    return ScopeResult(cosine=cosine, in_scope=in_scope, tiebreak_used=True)
