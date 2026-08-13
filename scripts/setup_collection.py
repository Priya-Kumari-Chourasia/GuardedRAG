from qdrant_client import QdrantClient, models
from app.core.config import get_settings

VECTOR_SIZE = 384  # must match the embedding model we'll use in the next phase


def setup_collection():
    settings = get_settings()
    client = QdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key)
    collection_name = settings.qdrant_collection

    existing = [c.name for c in client.get_collections().collections]
    if collection_name in existing:
        print(f"Collection '{collection_name}' already exists - skipping creation.")
    else:
        client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(size=VECTOR_SIZE, distance=models.Distance.COSINE),
        )
        print(f"Created collection '{collection_name}' ({VECTOR_SIZE}-dim, cosine distance).")

    client.create_payload_index(
        collection_name=collection_name,
        field_name="allowed_roles",
        field_schema=models.PayloadSchemaType.KEYWORD,
    )
    print("Created (or confirmed) KEYWORD index on 'allowed_roles'.")


if __name__ == "__main__":
    setup_collection()