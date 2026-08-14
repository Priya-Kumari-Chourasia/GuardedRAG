import time
import uuid

from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel
from qdrant_client import QdrantClient

from app.api.auth import CurrentUser, get_current_user, router as auth_router
from app.core.config import get_settings
from app.guardrails.pipeline import run_pipeline
from app.rag import memory
from app.rag.generate import Citation

app = FastAPI(title="PKC Secure Knowledge Assistant")
app.include_router(auth_router)


class ChatRequest(BaseModel):
    question: str
    conversation_id: str | None = None


class TokenUsage(BaseModel):
    prompt: int
    completion: int


class ChatResponse(BaseModel):
    answer: str
    citations: list[Citation]
    guardrail_verdict: str
    request_id: str
    conversation_id: str
    tokens: TokenUsage
    latency_ms: int
    faithfulness_score: float | None
    # Not in SPEC §4.5's literal field list -- extends the contract the same
    # way conversation_id already did in Phase 3. G2/G5 are non-blocking
    # (SPEC action: "redact ... warn inline"), so a redaction doesn't change
    # guardrail_verdict; the UI (Phase 6) needs *some* signal to show that
    # inline warning, and this is it.
    input_pii_redacted: bool
    output_pii_redacted: bool


class ConversationMessage(BaseModel):
    role: str
    content: str
    ts: str


@app.post("/api/chat", response_model=ChatResponse)
async def chat(body: ChatRequest, user: CurrentUser = Depends(get_current_user)) -> ChatResponse:
    request_id = str(uuid.uuid4())
    start = time.monotonic()

    # Ownership check up front: a conversation_id from another user's session
    # must fail exactly like a made-up one -- same 404, no distinguishing
    # detail -- for the same reason REFUSAL_TEMPLATE [I4] doesn't distinguish
    # "not found" from "not yours".
    if body.conversation_id is not None:
        owner = memory.conversation_owner(body.conversation_id)
        if owner is None or owner != user.email:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="conversation not found")
        conversation_id = body.conversation_id
    else:
        conversation_id = memory.start_conversation(user.email)

    # Prior turns are fetched BEFORE this turn is appended, and contain only
    # past question/answer TEXT -- never past retrieved passages. See
    # app/rag/memory.py::get_recent_turns for why that distinction matters.
    history = memory.get_recent_turns(conversation_id)

    # THE SECURITY BORDER, re-run on every single turn [I1]: user.roles comes
    # fresh from the just-validated JWT on THIS request, not from anything
    # cached in the conversation. run_pipeline() calls retrieve() internally,
    # which raises ACLViolation (-> 500) via assert_acl if a filtered hit is
    # ever somehow unauthorized -- that must never happen in a correct
    # system, so it is deliberately NOT caught here.
    #
    # tokens_used_today=0 is a known placeholder for G4 (budget): the
    # request_ledger table it would read from doesn't exist until Phase 6,
    # so G4 is wired into the pipeline's ordering now but never actually
    # blocks yet. See app/guardrails/budget.py.
    result = await run_pipeline(
        question=body.question,
        user_roles=user.roles,
        user_email=user.email,
        request_id=request_id,
        history=history,
        tokens_used_today=0,
    )

    # Store the (possibly PII-redacted) question that was actually used, not
    # necessarily the raw body.question -- conversation history must never
    # persist PII that G2 already decided shouldn't reach the LLM.
    memory.append_message(conversation_id, "user", result.question_used)
    memory.append_message(conversation_id, "assistant", result.answer)

    latency_ms = int((time.monotonic() - start) * 1000)

    return ChatResponse(
        answer=result.answer,
        citations=result.citations,
        guardrail_verdict=result.verdict.value,
        request_id=request_id,
        conversation_id=conversation_id,
        tokens=TokenUsage(prompt=result.prompt_tokens, completion=result.completion_tokens),
        latency_ms=latency_ms,
        faithfulness_score=result.faithfulness_score,
        input_pii_redacted=result.input_pii_redacted,
        output_pii_redacted=result.output_pii_redacted,
    )


@app.get("/api/conversations/{conversation_id}", response_model=list[ConversationMessage])
def get_conversation(conversation_id: str, user: CurrentUser = Depends(get_current_user)) -> list[ConversationMessage]:
    owner = memory.conversation_owner(conversation_id)
    if owner is None or owner != user.email:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="conversation not found")
    return [ConversationMessage(**m) for m in memory.get_conversation(conversation_id)]


@app.get("/health")
def health():
    settings = get_settings()

    try:
        client = QdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key)
        client.get_collections()
        qdrant_status = {"status": "ok"}
    except Exception as exc:
        qdrant_status = {"status": "error", "detail": str(exc)}

    # Deliberately no Groq API call here (SPEC §4.5) -- a health check that burns
    # free-tier LLM quota on every ping defeats the point of a health check.
    groq_status = {"status": "ok" if settings.groq_configured else "not_configured"}

    overall = "ok" if qdrant_status["status"] == "ok" and settings.groq_configured else "degraded"

    return {
        "status": overall,
        "qdrant": qdrant_status,
        "groq": groq_status,
        "version": "0.1.0",
    }
