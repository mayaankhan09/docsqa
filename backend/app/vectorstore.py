"""Build, persist, and search a FAISS index over chunk embeddings."""
from __future__ import annotations

import json
from pathlib import Path

import faiss
import numpy as np

from app.config import settings
from app.embeddings import embed_texts
from app.ingestion import Chunk

BACKEND_DIR = Path(__file__).resolve().parents[1]
INDEX_DIR = BACKEND_DIR / settings.index_dir
INDEX_PATH = INDEX_DIR / "chunks.faiss"
META_PATH = INDEX_DIR / "chunks.jsonl"


def build_index(chunks: list[Chunk]) -> None:
    """Embed all chunks, write the FAISS index and its metadata sidecar."""
    INDEX_DIR.mkdir(parents=True, exist_ok=True)

    print(f"embedding {len(chunks)} chunks...")
    vectors = embed_texts([c.text for c in chunks], show_progress=True)

    index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(vectors)
    faiss.write_index(index, str(INDEX_PATH))

    with META_PATH.open("w", encoding="utf-8") as f:
        for chunk in chunks:
            f.write(json.dumps(chunk.to_dict(), ensure_ascii=False) + "\n")

    print(f"index:    {index.ntotal} vectors, dim {vectors.shape[1]}")
    print(f"written:  {INDEX_PATH.name}, {META_PATH.name}")


def load_index() -> tuple[faiss.Index, list[dict]]:
    """Load the persisted index and its aligned metadata."""
    if not INDEX_PATH.exists():
        raise FileNotFoundError(
            f"No index at {INDEX_PATH}. Run: python -m scripts.build_index"
        )

    index = faiss.read_index(str(INDEX_PATH))
    with META_PATH.open(encoding="utf-8") as f:
        meta = [json.loads(line) for line in f]

    if index.ntotal != len(meta):
        raise ValueError(
            f"Index/metadata mismatch: {index.ntotal} vectors, {len(meta)} records. "
            "Rebuild the index."
        )
    return index, meta


def search(query_vector: np.ndarray, k: int) -> list[dict]:
    """Return the k nearest chunks, each with a similarity score."""
    index, meta = load_index()
    scores, ids = index.search(query_vector, k)

    results = []
    for score, idx in zip(scores[0], ids[0]):
        if idx == -1:
            continue
        record = dict(meta[idx])
        record["score"] = float(score)
        results.append(record)
    return results