import asyncio
import time
from dataclasses import dataclass

from groq import APIStatusError, AsyncGroq
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.core.config import get_settings


@dataclass
class LLMResponse:
    text: str
    model_used: str
    prompt_tokens: int
    completion_tokens: int
    latency_ms: int


class GroqUnavailable(Exception):
    pass


class GroqClient:
    def __init__(self) -> None:
        settings = get_settings()
        self._client = AsyncGroq(api_key=settings.groq_api_key or "unset")
        self._primary = settings.groq_model_primary
        self._fallback = settings.groq_model_fallback
        self._semaphore = asyncio.Semaphore(settings.groq_max_concurrency)

    @retry(
        retry=retry_if_exception_type(APIStatusError),
        wait=wait_exponential(multiplier=1, min=1, max=20),
        stop=stop_after_attempt(4),
        reraise=True,
    )
    async def _call_model(self, model: str, messages: list[dict], **kwargs) -> LLMResponse:
        async with self._semaphore:
            start = time.monotonic()
            resp = await self._client.chat.completions.create(model=model, messages=messages, **kwargs)
            elapsed_ms = int((time.monotonic() - start) * 1000)

        choice = resp.choices[0].message.content or ""
        usage = resp.usage
        return LLMResponse(
            text=choice,
            model_used=model,
            prompt_tokens=usage.prompt_tokens if usage else 0,
            completion_tokens=usage.completion_tokens if usage else 0,
            latency_ms=elapsed_ms,
        )

    async def chat(self, messages: list[dict], *, temperature: float = 0.1, max_tokens: int = 1024) -> LLMResponse:
        try:
            return await self._call_model(self._primary, messages, temperature=temperature, max_tokens=max_tokens)
        except APIStatusError:
            try:
                return await self._call_model(self._fallback, messages, temperature=temperature, max_tokens=max_tokens)
            except APIStatusError as e2:
                raise GroqUnavailable(f"both models failed: {e2}") from e2


_client: GroqClient | None = None


def get_groq_client() -> GroqClient:
    global _client
    if _client is None:
        _client = GroqClient()
    return _client