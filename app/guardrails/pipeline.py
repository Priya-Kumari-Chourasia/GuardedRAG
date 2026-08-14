from __future__ import annotations

import time
from dataclasses import dataclass, field

from app.core.config import get_settings
from app.guardrails import citations as citations_guard
from app.guardrails import groundedness as groundedness_guard
from app.guardrails import injection as injection_guard
from app.guardrails import pii as pii_guard
from app.guardrails import scope as scope_guard
from app.guardrails.budget import check_budget
from app.guardrails.types import BUDGET_EXCEEDED_REFUSAL, OUT_OF_SCOPE_REFUSAL, Verdict
from app.rag.generate import Citation, generate_answer
from app.rag.retriever import Hit, retrieve
from app.rbac.enforce import REFUSAL_TEMPLATE, log_security_event


@dataclass
class PipelineResult:
    answer: str
    citations: list[Citation]
    verdict: Verdict
    question_used: str  # possibly PII-redacted -- what memory.py should store
    hits: list[Hit] = field(default_factory=list)
    prompt_tokens: int = 0
    completion_tokens: int = 0
    model_used: str = "none"
    faithfulness_score: float | None = None
    input_pii_redacted: bool = False
    output_pii_redacted: bool = False
    stage_latencies_ms: dict[str, int] = field(default_factory=dict)


def _refused(
    verdict: Verdict,
    answer: str,
    *,
    question_used: str,
    latencies: dict[str, int],
    input_pii_redacted: bool = False,
) -> PipelineResult:
    return PipelineResult(
        answer=answer,
        citations=[],
        verdict=verdict,
        question_used=question_used,
        stage_latencies_ms=latencies,
        input_pii_redacted=input_pii_redacted,
    )


async def run_pipeline(
    *,
    question: str,
    user_roles: list[str],
    user_email: str,
    request_id: str,
    history: list[dict] | None = None,
    tokens_used_today: int = 0,
) -> PipelineResult:
    """Ordered, short-circuiting, fail-closed [I5] guardrail pipeline (SPEC
    §4.4). Order is cheapest-and-most-decisive first: no point paying for an
    embedding + scope classification, let alone a Groq generation call, on a
    request that G1 is about to reject outright.

    Fail-closed is enforced in exactly ONE place: every stage call below is
    wrapped in `try/except Exception`, and ANY exception -- a Groq timeout, a
    Presidio crash, a bad float parse -- is treated as a block. Individual
    guardrail modules do NOT catch their own exceptions; they just do their
    real work and let failures propagate here.
    """
    settings = get_settings()
    latencies: dict[str, int] = {}

    def stage_done(name: str, start: float) -> None:
        latencies[name] = int((time.monotonic() - start) * 1000)

    # --- G1: injection -----------------------------------------------------
    t0 = time.monotonic()
    try:
        injection_result = await injection_guard.check_injection(question)
    except Exception as exc:
        log_security_event(
            severity="P1",
            event_type="guardrail_fail_closed",
            user_email=user_email,
            request_id=request_id,
            detail=f"stage=G1_injection error={exc!r}",
        )
        return _refused(Verdict.BLOCKED_INJECTION, REFUSAL_TEMPLATE, question_used=question, latencies=latencies)
    stage_done("G1_injection", t0)

    if injection_result.blocked:
        log_security_event(
            severity="P1",
            event_type="injection_attempt",
            user_email=user_email,
            request_id=request_id,
            detail=f"score={injection_result.score:.4f}",
        )
        return _refused(Verdict.BLOCKED_INJECTION, REFUSAL_TEMPLATE, question_used=question, latencies=latencies)

    # --- G2: input PII -------------------------------------------------------
    # Non-blocking by design (SPEC action: "redact ... warn inline") -- asking
    # about a colleague by name isn't an attack. But a FAILURE of this stage
    # still fails closed [I5]: if we can't be sure PII was scrubbed, the raw
    # text must never reach embedding or the LLM, so we block the request
    # rather than pass the un-redacted question through.
    t0 = time.monotonic()
    try:
        input_pii = pii_guard.scan_input(question)
    except Exception as exc:
        log_security_event(
            severity="P1",
            event_type="guardrail_fail_closed",
            user_email=user_email,
            request_id=request_id,
            detail=f"stage=G2_input_pii error={exc!r}",
        )
        return _refused(Verdict.BLOCKED_PII, REFUSAL_TEMPLATE, question_used=question, latencies=latencies)
    stage_done("G2_input_pii", t0)

    if input_pii.redacted:
        log_security_event(
            severity="P1",
            event_type="input_pii_redacted",
            user_email=user_email,
            request_id=request_id,
            detail=f"entities={input_pii.entity_types}",
        )
    # From here on, every downstream stage (scope check, retrieval, generation,
    # conversation memory) works on the redacted text -- the raw PII-bearing
    # question is never embedded, never sent to the LLM, and never persisted.
    question = input_pii.text

    # --- G3: out-of-scope ----------------------------------------------------
    t0 = time.monotonic()
    try:
        scope_result = await scope_guard.check_scope(question)
    except Exception as exc:
        log_security_event(
            severity="P1",
            event_type="guardrail_fail_closed",
            user_email=user_email,
            request_id=request_id,
            detail=f"stage=G3_scope error={exc!r}",
        )
        return _refused(
            Verdict.BLOCKED_OUT_OF_SCOPE,
            OUT_OF_SCOPE_REFUSAL,
            question_used=question,
            latencies=latencies,
            input_pii_redacted=input_pii.redacted,
        )
    stage_done("G3_scope", t0)

    if not scope_result.in_scope:
        return _refused(
            Verdict.BLOCKED_OUT_OF_SCOPE,
            OUT_OF_SCOPE_REFUSAL,
            question_used=question,
            latencies=latencies,
            input_pii_redacted=input_pii.redacted,
        )

    # --- G4: budget ------------------------------------------------------------
    # Pure check against a caller-supplied usage figure -- see budget.py for
    # why this doesn't query a ledger itself. Until Phase 6 wires a real
    # `tokens_used_today` lookup at the call site, the default of 0 means this
    # stage never actually blocks anything; it's here so the ordering, the
    # verdict, and the unit test all exist ahead of that wiring.
    t0 = time.monotonic()
    try:
        budget_result = check_budget(tokens_used_today, settings.daily_token_budget)
    except Exception as exc:
        log_security_event(
            severity="P2",
            event_type="guardrail_fail_closed",
            user_email=user_email,
            request_id=request_id,
            detail=f"stage=G4_budget error={exc!r}",
        )
        return _refused(
            Verdict.BLOCKED_BUDGET,
            BUDGET_EXCEEDED_REFUSAL,
            question_used=question,
            latencies=latencies,
            input_pii_redacted=input_pii.redacted,
        )
    stage_done("G4_budget", t0)

    if budget_result.blocked:
        log_security_event(
            severity="P2",
            event_type="budget_exceeded",
            user_email=user_email,
            request_id=request_id,
            detail=f"tokens_used_today={tokens_used_today} daily_budget={settings.daily_token_budget}",
        )
        return _refused(
            Verdict.BLOCKED_BUDGET,
            BUDGET_EXCEEDED_REFUSAL,
            question_used=question,
            latencies=latencies,
            input_pii_redacted=input_pii.redacted,
        )

    # --- retrieval + generation (not a guardrail stage; the security border
    # this depends on is I1/I3, enforced inside retrieve() itself) -----------
    hits = await retrieve(question, user_roles, request_id, user_email)
    gen_result = await generate_answer(question, hits, history=history)

    # A zero-HITS refusal is I4 (retrieval found nothing this user may see),
    # not a guardrail verdict -- there's no answer text to PII-scan, no
    # context to check groundedness against, and no citations to expect.
    # Passing it straight through as ALLOWED matches how main.py already
    # treats an ACL refusal: the border that fired was retrieval-time
    # authorization, not a guardrail.
    if gen_result.refused:
        return PipelineResult(
            answer=gen_result.answer,
            citations=[],
            verdict=Verdict.ALLOWED,
            question_used=question,
            hits=hits,
            prompt_tokens=gen_result.prompt_tokens,
            completion_tokens=gen_result.completion_tokens,
            model_used=gen_result.model_used,
            input_pii_redacted=input_pii.redacted,
            stage_latencies_ms=latencies,
        )

    return await _postprocess(
        question=question,
        hits=hits,
        gen_result=gen_result,
        history=history,
        input_pii_redacted=input_pii.redacted,
        user_email=user_email,
        request_id=request_id,
        latencies=latencies,
        allow_retry=True,
    )


async def _postprocess(
    *,
    question: str,
    hits: list[Hit],
    gen_result,
    history: list[dict] | None,
    input_pii_redacted: bool,
    user_email: str,
    request_id: str,
    latencies: dict[str, int],
    allow_retry: bool,
) -> PipelineResult:
    """G5 (output PII) -> G6 (groundedness) -> G7 (citations), in that order,
    applied to one generated answer. If G7 finds zero citations and a retry
    hasn't been used yet, this calls generate_answer ONCE more (SPEC: "zero
    found -> regenerate once, then suppress") and re-runs G5/G6/G7 against
    the fresh answer before finally suppressing.
    """
    settings = get_settings()

    # --- G5: output PII --------------------------------------------------
    t0 = time.monotonic()
    try:
        output_pii = pii_guard.scan_output(gen_result.answer)
    except Exception as exc:
        log_security_event(
            severity="P1",
            event_type="guardrail_fail_closed",
            user_email=user_email,
            request_id=request_id,
            detail=f"stage=G5_output_pii error={exc!r}",
        )
        return _refused(
            Verdict.BLOCKED_PII, REFUSAL_TEMPLATE, question_used=question, latencies=latencies,
            input_pii_redacted=input_pii_redacted,
        )
    stage_done_key = "G5_output_pii" if "G5_output_pii" not in latencies else "G5_output_pii_retry"
    latencies[stage_done_key] = int((time.monotonic() - t0) * 1000)

    if output_pii.redacted:
        log_security_event(
            severity="P1",
            event_type="output_pii_redacted",
            user_email=user_email,
            request_id=request_id,
            detail=f"entities={output_pii.entity_types}",
        )
    answer_text = output_pii.text

    # --- G6: groundedness (feature-flagged) -------------------------------
    faithfulness_score: float | None = None
    if settings.enable_groundedness_check:
        t0 = time.monotonic()
        try:
            context = "\n\n".join(h.chunk_text for h in hits)
            ground = await groundedness_guard.check_groundedness(answer_text, context)
        except Exception as exc:
            log_security_event(
                severity="P1",
                event_type="guardrail_fail_closed",
                user_email=user_email,
                request_id=request_id,
                detail=f"stage=G6_groundedness error={exc!r}",
            )
            return _refused(
                Verdict.BLOCKED_UNGROUNDED, REFUSAL_TEMPLATE, question_used=question, latencies=latencies,
                input_pii_redacted=input_pii_redacted,
            )
        key = "G6_groundedness" if "G6_groundedness" not in latencies else "G6_groundedness_retry"
        latencies[key] = int((time.monotonic() - t0) * 1000)
        faithfulness_score = ground.score

        if not ground.grounded:
            return _refused(
                Verdict.BLOCKED_UNGROUNDED, REFUSAL_TEMPLATE, question_used=question, latencies=latencies,
                input_pii_redacted=input_pii_redacted,
            )

    # --- G7: citation presence --------------------------------------------
    if not citations_guard.has_citations(gen_result.answer):
        if allow_retry:
            retry_result = await generate_answer(question, hits, history=history)
            return await _postprocess(
                question=question,
                hits=hits,
                gen_result=retry_result,
                history=history,
                input_pii_redacted=input_pii_redacted,
                user_email=user_email,
                request_id=request_id,
                latencies=latencies,
                allow_retry=False,
            )
        return _refused(
            Verdict.BLOCKED_UNGROUNDED, REFUSAL_TEMPLATE, question_used=question, latencies=latencies,
            input_pii_redacted=input_pii_redacted,
        )

    return PipelineResult(
        answer=answer_text,
        citations=gen_result.citations,
        verdict=Verdict.ALLOWED,
        question_used=question,
        hits=hits,
        prompt_tokens=gen_result.prompt_tokens,
        completion_tokens=gen_result.completion_tokens,
        model_used=gen_result.model_used,
        faithfulness_score=faithfulness_score,
        input_pii_redacted=input_pii_redacted,
        output_pii_redacted=output_pii.redacted,
        stage_latencies_ms=latencies,
    )
