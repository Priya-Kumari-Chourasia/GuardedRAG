from __future__ import annotations

import hashlib
import json
import re
import uuid
from pathlib import Path

import numpy as np
import yaml
from fastembed import TextEmbedding
from qdrant_client import QdrantClient, models

from app.core.config import get_settings
from app.rbac.acl import acl_for, most_restrictive

RAW_ROOT = Path("data/raw")
CENTROID_PATH = Path("data/corpus_centroid.json")

CHUNK_TARGET_TOKENS = 512
CHUNK_OVERLAP_TOKENS = 64
CHUNK_MIN_TOKENS = 100

# Our docs are short markdown, not something we run through a real tokenizer at
# chunk-build time -- this word->token ratio is a rough approximation, good enough
# for deciding chunk boundaries. It is NOT used for the actual embedding step,
# which uses FastEmbed's real tokenizer internally.
TOKENS_PER_WORD = 1.3


def _words_for_tokens(n_tokens: int) -> int:
    return int(n_tokens / TOKENS_PER_WORD)


def parse_doc(path: Path) -> tuple[dict, str]:
    raw = path.read_text(encoding="utf-8")
    _, frontmatter, body = raw.split("---", 2)
    meta = yaml.safe_load(frontmatter)
    return meta, body.strip()


def split_sections(body: str) -> list[tuple[str, str]]:
    """Split a markdown body on '## ' headers into (section_title, section_text) pairs.
    Any text before the first '## ' (e.g. an opening summary) becomes a section with
    an empty title."""
    parts = re.split(r"(?m)^## ", body)
    sections: list[tuple[str, str]] = []

    preamble = parts[0].strip()
    if preamble:
        sections.append(("", preamble))

    for part in parts[1:]:
        title, _, rest = part.partition("\n")
        sections.append((title.strip(), rest.strip()))

    return sections


def chunk_text(text: str) -> list[str]:
    """Word-based sliding window: ~512-token target chunks, 64-token overlap."""
    words = text.split()
    if not words:
        return []

    target = _words_for_tokens(CHUNK_TARGET_TOKENS)
    overlap = _words_for_tokens(CHUNK_OVERLAP_TOKENS)

    chunks = []
    start = 0
    while start < len(words):
        end = min(start + target, len(words))
        chunks.append(" ".join(words[start:end]))
        if end == len(words):
            break
        start = end - overlap
    return chunks


def build_chunks(doc_title: str, body: str) -> list[dict]:
    """Chunk a document's body, then merge any under-sized chunk into the previous
    one. Merging can cause a chunk to span two sections -- that's expected, and is
    exactly why acl.py's most_restrictive() exists: the merged chunk must inherit
    the strictest sensitivity of any section it now touches. In our corpus every
    section of a document shares one doc_class, so in practice this is a no-op --
    but the pipeline still routes through it because SPEC treats it as a required
    invariant, not an optimization to skip when it looks unnecessary today."""
    min_words = _words_for_tokens(CHUNK_MIN_TOKENS)

    raw: list[dict] = []
    for section_title, section_text in split_sections(body):
        for piece in chunk_text(section_text):
            raw.append({"section_titles": [section_title] if section_title else [], "text": piece})

    merged: list[dict] = []
    for item in raw:
        if merged and len(item["text"].split()) < min_words:
            merged[-1]["text"] += " " + item["text"]
            for t in item["section_titles"]:
                if t not in merged[-1]["section_titles"]:
                    merged[-1]["section_titles"].append(t)
        else:
            merged.append(item)

    result = []
    for m in merged:
        prefix = f"# {doc_title}"
        if m["section_titles"]:
            prefix += " > ## " + " & ".join(m["section_titles"])
        result.append({"section_titles": m["section_titles"], "text": f"{prefix}\n\n{m['text']}"})
    return result


def process_document(path: Path, department: str) -> list[dict]:
    meta, body = parse_doc(path)
    doc_id = meta["doc_id"]
    doc_class = meta["doc_class"]
    title = meta["title"]
    contains_pii = bool(meta.get("contains_pii", False))

    allowed_roles, sensitivity = acl_for(doc_class)
    chunks = build_chunks(title, body)

    # Every chunk in this document maps to the same doc_class today, so this list
    # is uniform -- most_restrictive() still runs per SPEC 5.3's chunk-spanning rule.
    doc_sensitivity = most_restrictive([sensitivity] * max(len(chunks), 1))

    records = []
    for i, chunk in enumerate(chunks):
        chunk_id = f"{doc_id}::c{i:02d}"
        records.append(
            {
                "chunk_id": chunk_id,
                "doc_id": doc_id,
                "doc_title": title,
                "department": department,
                "doc_class": doc_class,
                "sensitivity": doc_sensitivity,
                "allowed_roles": allowed_roles,
                "chunk_index": i,
                "chunk_text": chunk["text"],
                "page": None,
                "source_uri": str(path).replace("\\", "/"),
                "effective_date": None,
                "contains_pii": contains_pii,
                "content_hash": "sha256:" + hashlib.sha256(chunk["text"].encode("utf-8")).hexdigest(),
            }
        )
    return records


def embed_and_upsert(chunks: list[dict], *, update_centroid: bool = True) -> None:
    settings = get_settings()
    client = QdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key)
    embedder = TextEmbedding(model_name=settings.embed_model)

    texts = [c["chunk_text"] for c in chunks]
    # parallel=None (NOT 0 -- FastEmbed treats parallel=0 as "use os.cpu_count()
    # worker subprocesses", each loading its own copy of the ONNX model, which is
    # worse) forces single-process sequential embedding. Small batch_size keeps
    # peak memory per ONNX forward pass low -- default batch_size=256 exhausted
    # this machine's page file.
    vectors = list(embedder.embed(texts, batch_size=8, parallel=None))

    # G3 (out-of-scope guardrail) needs a fixed point to measure "how close is
    # this query to what PKC's corpus is actually about". Computing that mean
    # here -- once, at ingest -- instead of at query time means G3 never pays
    # for a full-collection scan; it just loads this small cached vector.
    # Normalized so a later cosine-similarity dot product is a plain dot
    # product, not a full cosine formula, at query time.
    #
    # update_centroid=False for a partial/fixture ingest (evals/CI): this file
    # is shared, unconditional-write, full-corpus state, not per-collection --
    # a 25-doc fixture ingest overwriting it with a 25-doc centroid would
    # quietly degrade the real app's G3 detection. Learned this the hard way:
    # a baseline-run fixture ingest into a scratch Qdrant collection clobbered
    # this file even though it never touched the real collection.
    if update_centroid:
        centroid = np.mean(np.array(vectors), axis=0)
        centroid = centroid / np.linalg.norm(centroid)
        CENTROID_PATH.parent.mkdir(parents=True, exist_ok=True)
        CENTROID_PATH.write_text(json.dumps(centroid.tolist()))

    points = [
        models.PointStruct(
            # Deterministic ID (derived from chunk_id, not random) makes re-running
            # ingest idempotent: same chunk_id -> same point ID -> upsert overwrites
            # instead of creating a duplicate.
            id=str(uuid.uuid5(uuid.NAMESPACE_URL, chunk["chunk_id"])),
            vector=vector.tolist(),
            payload=chunk,
        )
        for chunk, vector in zip(chunks, vectors)
    ]

    batch_size = 64
    for i in range(0, len(points), batch_size):
        client.upsert(collection_name=settings.qdrant_collection, points=points[i : i + batch_size])


def ingest_all(doc_ids: set[str] | None = None) -> None:
    """doc_ids=None ingests the full 100-doc corpus (normal/local use). Passing
    a set restricts ingestion to those doc_ids -- used for the CI fixture corpus
    (PLAN.md task 5.5/5.6, SPEC_1.md Sec 7.4: ~5 min PR-gate budget, not the
    full 100 docs). Filtered by filename stem, not by opening+parsing every
    file's frontmatter, since every raw doc is named exactly f"{doc_id}.md"
    (scripts/corpus_manifest.py's convention)."""
    all_chunks: list[dict] = []
    n_docs = 0
    for dept_dir in sorted(p for p in RAW_ROOT.iterdir() if p.is_dir()):
        for doc_path in sorted(dept_dir.glob("*.md")):
            if doc_ids is not None and doc_path.stem not in doc_ids:
                continue
            all_chunks.extend(process_document(doc_path, dept_dir.name))
            n_docs += 1

    if doc_ids is not None and n_docs != len(doc_ids):
        missing = doc_ids - {c["doc_id"] for c in all_chunks}
        raise ValueError(f"fixture doc_ids not found under {RAW_ROOT}: {sorted(missing)}")

    print(f"Parsed {len(all_chunks)} chunks from {n_docs} documents.")
    embed_and_upsert(all_chunks, update_centroid=doc_ids is None)
    print(f"Upserted {len(all_chunks)} chunks into '{get_settings().qdrant_collection}'.")


if __name__ == "__main__":
    ingest_all()
