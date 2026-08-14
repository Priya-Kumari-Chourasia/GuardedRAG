import time
import uuid

from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel
from qdrant_client import QdrantClient

from app.api.auth import CurrentUser, get_current_user, router as auth_router
from app.core.config import get_settings
from app.rag import memory
from app.rag.generate import Citation, generate_answer
from app.rag.retriever import retrieve

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
    # cached in the conversation. retrieve() raises ACLViolation (-> 500) via
    # assert_acl if a filtered hit is ever somehow unauthorized -- that must
    # never happen in a correct system, so it is deliberately NOT caught here.
    hits = await retrieve(body.question, user.roles, request_id, user.email)
    result = await generate_answer(body.question, hits, history=history)

    memory.append_message(conversation_id, "user", body.question)
    memory.append_message(conversation_id, "assistant", result.answer)

    latency_ms = int((time.monotonic() - start) * 1000)

    return ChatResponse(
        answer=result.answer,
        citations=result.citations,
        # No guardrail pipeline exists yet (Phase 4) -- "allowed" here means
        # "not blocked by a guardrail", which is trivially true when there are
        # none. It is NOT the same thing as an ACL refusal: a REFUSAL_TEMPLATE
        # answer from an empty retrieval still reports "allowed", because the
        # security border that fired is retrieval-time authorization, not a
        # guardrail verdict. Phase 4 will make this field mean something.
        guardrail_verdict="allowed",
        request_id=request_id,
        conversation_id=conversation_id,
        tokens=TokenUsage(prompt=result.prompt_tokens, completion=result.completion_tokens),
        latency_ms=latency_ms,
        # Groundedness checking (G6) is a Phase 4 guardrail, feature-flagged
        # off by default at the pipeline level -- None here just means
        # "not measured yet", not "ungrounded".
        faithfulness_score=None,
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
