# ---- Base ----
FROM python:3.12-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/models

WORKDIR /app

# System deps some wheels need
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl \
    && rm -rf /var/lib/apt/lists/*

# ---- Python deps (cached layer) ----
# Copy only requirements first so deps re-install only when they change,
# not on every code edit.
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# ---- Pre-download models into the image ----
# Bakes the embedder + reranker into a layer so runtime never downloads them.
RUN python -c "from sentence_transformers import SentenceTransformer, CrossEncoder; \
    SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2'); \
    CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')"

# ---- App code ----
COPY app/ ./app/
COPY scripts/ ./scripts/

EXPOSE 8000

# Build the index at startup if missing, then serve.
CMD ["sh", "-c", "python -m scripts.build_index && uvicorn app.main:app --host 0.0.0.0 --port 8000"]