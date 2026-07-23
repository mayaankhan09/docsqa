"""FastAPI service exposing the DocsQA retrieval and generation pipeline."""
from __future__ import annotations

import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.embeddings import get_model
from app.generation import answer_question
from app.llm import LLMError
from app.models import (
    AskRequest, AskResponse, HealthResponse, SearchResult, SourceOut,
)
from app.retrieval import get_reranker, retrieve
from app.vectorstore import load_index

_state: dict = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Warm the models and index once, at startup."""
    print("loading embedding model...")
    get_model()
    print("loading reranker...")
    get_reranker()
    try:
        index, meta = load_index()
        _state["chunks"] = index.ntotal
        print(f"index ready: {index.ntotal} chunks")
    except FileNotFoundError:
        _state["chunks"] = 0
        print("WARNING: no index found — run scripts/build_index.py")
    yield
    _state.clear()


app = FastAPI(
    title="DocsQA",
    description="Retrieval-augmented QA over health insurance policy documents, "
                "with clause-level citations.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


def _require_index() -> None:
    if not _state.get("chunks"):
        raise HTTPException(
            status_code=503,
            detail="Index not available. Run scripts/build_index.py and restart.",
        )


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(
        status="ok" if _state.get("chunks") else "degraded",
        chunks_indexed=_state.get("chunks", 0),
        embedding_model=settings.embedding_model,
        reranker_model=settings.reranker_model,
        provider_chain=settings.provider_chain,
    )


@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest) -> AskResponse:
    _require_index()
    started = time.perf_counter()

    try:
        result = answer_question(
            req.query,
            min_score=req.min_score if req.min_score is not None else 1.0,
        )
    except LLMError as exc:
        raise HTTPException(status_code=502, detail=f"All LLM providers failed: {exc}")

    sources = [
        SourceOut(
            index=i,
            citation=s.citation(),
            insurer=s.insurer,
            page=s.page,
            source=s.source,
            text=s.text,
            rerank_score=round(s.rerank_score, 3),
            vector_rank=s.vector_rank,
            cited=i in result.cited_indices,
        )
        for i, s in enumerate(result.sources, 1)
    ]

    return AskResponse(
        query=req.query,
        answer=result.text,
        found=result.found,
        sources=sources,
        provider=result.provider,
        invalid_citations=result.invalid_citations,
        elapsed_ms=int((time.perf_counter() - started) * 1000),
    )


@app.get("/search", response_model=list[SearchResult])
def search(q: str, k: int = 5, rerank: bool = True) -> list[SearchResult]:
    """Retrieval only — no LLM call. Useful for debugging and evaluation."""
    _require_index()
    if len(q) < 3:
        raise HTTPException(status_code=422, detail="Query too short.")

    results = retrieve(q, top_n=min(k, 10), rerank=rerank)
    return [
        SearchResult(
            citation=r.citation(), insurer=r.insurer, page=r.page, text=r.text,
            vector_score=round(r.vector_score, 3),
            rerank_score=round(r.rerank_score, 3),
            vector_rank=r.vector_rank,
        )
        for r in results
    ]