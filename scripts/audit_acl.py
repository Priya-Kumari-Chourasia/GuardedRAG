from collections import defaultdict

from qdrant_client import QdrantClient

from app.core.config import get_settings


def audit_acl() -> None:
    settings = get_settings()
    client = QdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key)

    by_department: dict[str, list[dict]] = defaultdict(list)
    offset = None
    while True:
        points, offset = client.scroll(
            settings.qdrant_collection, limit=256, offset=offset, with_payload=True
        )
        for p in points:
            by_department[p.payload["department"]].append(p.payload)
        if offset is None:
            break

    total = 0
    for department in sorted(by_department):
        chunks = by_department[department]
        total += len(chunks)
        print(f"\n=== {department} ({len(chunks)} chunks) ===")
        for c in sorted(chunks, key=lambda x: (x["doc_id"], x["chunk_index"])):
            roles = ",".join(sorted(c["allowed_roles"]))
            print(f"  {c['chunk_id']:45s} class={c['doc_class']:22s} sens={c['sensitivity']:12s} roles=[{roles}]")

    print(f"\nTOTAL: {total} chunks across {len(by_department)} departments")


if __name__ == "__main__":
    audit_acl()
