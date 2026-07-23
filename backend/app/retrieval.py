"""Two-stage retrieval: FAISS recall, then cross-encoder precision."""
from __future__ import annotations

from dataclasses import dataclass

from sentence_transformers import CrossEncoder

from app.config import settings
from app.embeddings import embed_query
from app.vectorstore import search as vector_search

_reranker: CrossEncoder | None = None


def get_reranker() -> CrossEncoder:
    """Load the cross-encoder once and reuse it."""
    global _reranker
    if _reranker is None:
        _reranker = CrossEncoder(settings.reranker_model, max_length=512)
    return _reranker


@dataclass
class Result:
    chunk_id: str
    text: str
    insurer: str
    source: str
    page: int
    vector_score: float
    rerank_score: float
    vector_rank: int
    final_rank: int

    def citation(self) -> str:
        return f"{self.insurer}, p. {self.page}"


def retrieve(
    query: str,
    top_k: int | None = None,
    top_n: int | None = None,
    rerank: bool = True,
) -> list[Result]:
    """Retrieve top_k candidates by vector similarity, rerank, return top_n."""
    top_k = top_k or settings.top_k
    top_n = top_n or settings.top_n

    candidates = vector_search(embed_query(query), top_k)
    if not candidates:
        return []

    if not rerank:
        return [
            Result(
                chunk_id=c["chunk_id"], text=c["text"], insurer=c["insurer"],
                source=c["source"], page=c["page"],
                vector_score=c["score"], rerank_score=0.0,
                vector_rank=i + 1, final_rank=i + 1,
            )
            for i, c in enumerate(candidates[:top_n])
        ]

    model = get_reranker()
    scores = model.predict([(query, c["text"]) for c in candidates])

    ranked = sorted(
        zip(candidates, scores, range(1, len(candidates) + 1)),
        key=lambda t: t[1],
        reverse=True,
    )

    return [
        Result(
            chunk_id=c["chunk_id"], text=c["text"], insurer=c["insurer"],
            source=c["source"], page=c["page"],
            vector_score=c["score"], rerank_score=float(score),
            vector_rank=vrank, final_rank=i + 1,
        )
        for i, (c, score, vrank) in enumerate(ranked[:top_n])
    ]