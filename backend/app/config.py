"""
Application settings loaded from environment / .env file.

top_k  — number of FAISS candidate chunks retrieved before reranking.
top_n  — number of chunks that survive the cross-encoder reranking step.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    gemini_api_key: str
    groq_api_key: str = ""
    provider_chain: str = "gemini,groq"
    generation_model: str = "gemini-2.0-flash"
    groq_model: str = "llama-3.3-70b-versatile"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    chunk_size: int = 800
    chunk_overlap: int = 120
    top_k: int = 20
    top_n: int = 5
    index_dir: str = "data/index"
    raw_dir: str = "data/raw"


settings = Settings()
