from __future__ import annotations

from dataclasses import dataclass

from qdrant_client import QdrantClient

from app.core.config import get_settings
from app.rag.embeddings import get_dense_model
from app.rbac.acl import build_acl_filter
from app.rbac.enforce import assert_acl


@dataclass
class Hit:
    chunk_id: str
    doc_id: str
    doc_title: str
    chunk_text: str
    score: float
    payload: dict


async def retrieve(
    query: str,
    user_roles: list[str],
    request_id: str,
    user_email: str,
    top_k: int | None = None,
) -> list[Hit]:
    """Dense-only for now -- SPEC's hybrid dense+BM25 design was scoped out to
    avoid re-ingesting the corpus with sparse vectors; see DESIGN_DECISIONS.md.
    The security-critical part (ACL filter applied at the Qdrant query itself,
    not after) is unchanged by that choice."""
    settings = get_settings()
    top_k = top_k or settings.top_k

    # THE SECURITY BORDER [I1]: build_acl_filter raises on empty roles [I7] and
    # is passed straight into Qdrant's query_filter, so unauthorized chunks are
    # never returned by the database in the first place -- not filtered out of
    # a larger result set after the fact.
    acl_filter = build_acl_filter(user_roles)

    client = QdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key)
    query_vector = list(get_dense_model().embed([query]))[0]

    results = client.query_points(
        collection_name=settings.qdrant_collection,
        query=query_vector.tolist(),
        query_filter=acl_filter,
        limit=top_k,
        with_payload=True,
    ).points

    # Defense in depth [I3]: re-check every hit against user_roles even though
    # the query_filter above should make a violation impossible. Raises and logs
    # a P0 if it ever fires -- a tripwire on a path that should be unreachable.
    assert_acl(results, user_roles, request_id, user_email)

    return [
        Hit(
            chunk_id=r.payload["chunk_id"],
            doc_id=r.payload["doc_id"],
            doc_title=r.payload["doc_title"],
            chunk_text=r.payload["chunk_text"],
            score=r.score,
            payload=r.payload,
        )
        for r in results
    ]
