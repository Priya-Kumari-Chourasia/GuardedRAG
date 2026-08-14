"""G7 (citation presence) -- PLAN.md Phase 4 task 4.6.

Pure regex check, no network calls -- see app/guardrails/pipeline.py for the
"regenerate once, then suppress" retry policy this feeds into, which is
exercised as part of the pipeline integration tests instead (it needs a live
generate_answer() retry, which this module deliberately doesn't own)."""

from app.guardrails.citations import has_citations


def test_detects_ascii_citation_marker():
    assert has_citations("Revenue was strong [fin-q3-2025-report::c07].")


def test_detects_fullwidth_citation_marker():
    # Groq's models sometimes emit fullwidth brackets -- generate.py's
    # CITATION_RE already tolerates both forms; this proves G7 inherits that
    # tolerance rather than re-narrowing it with a second regex.
    assert has_citations("Revenue was strong 【fin-q3-2025-report::c07】.")


def test_no_citation_marker_present():
    assert not has_citations("I'm not sure the passages cover that.")


def test_bracketed_text_without_chunk_id_shape_is_not_a_citation():
    # A bracket that isn't shaped like "doc_id::cNN" must not count -- e.g. a
    # markdown link or a stray footnote marker in the model's prose.
    assert not has_citations("See the FAQ [here] for more details.")
