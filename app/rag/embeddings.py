from __future__ import annotations

from fastembed import TextEmbedding

from app.core.config import get_settings

# Shared between retriever.py (query-time embedding) and guardrails/scope.py
# (G3 out-of-scope check) so both embed with the exact same model instance/
# config instead of loading BAAI/bge-small-en-v1.5 twice.
_dense_model: TextEmbedding | None = None


def get_dense_model() -> TextEmbedding:
    global _dense_model
    if _dense_model is None:
        _dense_model = TextEmbedding(model_name=get_settings().embed_model)
    return _dense_model
