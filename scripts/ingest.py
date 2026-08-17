import argparse
from pathlib import Path

from app.rag.ingest import ingest_all


def _load_fixture_docs(path: Path) -> set[str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    return {line.strip() for line in lines if line.strip() and not line.strip().startswith("#")}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest the corpus into Qdrant.")
    parser.add_argument(
        "--fixture",
        type=Path,
        default=None,
        help="Path to a doc_id list (one per line, '#' comments allowed) -- ingest only "
        "those docs instead of the full 100. Used by CI (data/golden/fixture_docs.txt).",
    )
    args = parser.parse_args()

    doc_ids = _load_fixture_docs(args.fixture) if args.fixture else None
    ingest_all(doc_ids)
