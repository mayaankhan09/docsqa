"""Request and response schemas."""
from __future__ import annotations

from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=500)
    top_n: int | None = Field(None, ge=1, le=10)
    min_score: float | None = Field(None, ge=-15.0, le=15.0)


class SourceOut(BaseModel):
    index: int
    citation: str
    insurer: str
    page: int
    source: str
    text: str
    rerank_score: float
    vector_rank: int
    cited: bool


class AskResponse(BaseModel):
    query: str
    answer: str
    found: bool
    sources: list[SourceOut]
    provider: str
    invalid_citations: list[int]
    elapsed_ms: int


class SearchResult(BaseModel):
    citation: str
    insurer: str
    page: int
    text: str
    vector_score: float
    rerank_score: float
    vector_rank: int


class HealthResponse(BaseModel):
    status: str
    chunks_indexed: int
    embedding_model: str
    reranker_model: str
    provider_chain: str