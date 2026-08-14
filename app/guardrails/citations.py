from __future__ import annotations

from app.rag.generate import CITATION_RE


def has_citations(answer: str) -> bool:
    """G7: does this answer carry at least one resolvable citation marker?

    Just the detection half of G7 -- SPEC §4.4's action ("regenerate once,
    then suppress") is a retry policy that needs to call generate_answer
    again, which belongs in pipeline.py alongside the other stage
    orchestration, not in this small, easily-unit-tested checker.
    """
    return bool(CITATION_RE.search(answer))
