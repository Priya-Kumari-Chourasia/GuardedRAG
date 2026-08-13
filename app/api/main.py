from fastapi import FastAPI
from qdrant_client import QdrantClient

from app.api.auth import router as auth_router
from app.core.config import get_settings

app = FastAPI(title="PKC Secure Knowledge Assistant")
app.include_router(auth_router)


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
