from __future__ import annotations

from dataclasses import dataclass

from app.core.config import get_settings
from app.core.groq_client import get_groq_client


@dataclass
class InjectionResult:
    score: float
    blocked: bool


async def check_injection(text: str) -> InjectionResult:
    """G1: score prompt-injection likelihood via Groq's dedicated classifier.

    llama-prompt-guard-2-86m is not a chat model -- confirmed against the live
    API that for this model Groq's chat/completions response content IS the
    malicious-probability score itself (e.g. "0.9995..."), not a natural-
    language reply. We parse that string as a float and compare it to
    INJECTION_THRESHOLD.

    Deliberately does NOT catch exceptions here (a failed API call, an
    unparseable response): app.guardrails.pipeline is the single place that
    turns "this stage raised" into "fail closed, block the request" [I5], so
    every guardrail module gets to just do its real work.
    """
    settings = get_settings()
    resp = await get_groq_client().classify(settings.groq_guard_model, [{"role": "user", "content": text}])
    score = float(resp.text.strip())
    return InjectionResult(score=score, blocked=score > settings.injection_threshold)
