"""Encode text into dense vectors using a local sentence-transformers model."""
from __future__ import annotations

import numpy as np
from sentence_transformers import SentenceTransformer

from app.config import settings

_model: SentenceTransformer | None = None


def get_model() -> SentenceTransformer:
    """Load the encoder once and reuse it (loading costs ~2s)."""
    global _model
    if _model is None:
        _model = SentenceTransformer(settings.embedding_model)
    return _model


def embed_texts(texts: list[str], show_progress: bool = False) -> np.ndarray:
    """Encode documents. Returns L2-normalised float32 vectors, shape (n, dim)."""
    model = get_model()
    vectors = model.encode(
        texts,
        batch_size=64,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=show_progress,
    )
    return vectors.astype("float32")


def embed_query(text: str) -> np.ndarray:
    """Encode a single query. Returns shape (1, dim) for FAISS search."""
    return embed_texts([text])