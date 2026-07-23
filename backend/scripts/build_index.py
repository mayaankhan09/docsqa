"""Ingest PDFs and build the FAISS index in one step."""
from app.ingestion import ingest_all
from app.vectorstore import build_index

if __name__ == "__main__":
    chunks = ingest_all()
    print(f"\n{len(chunks)} chunks ingested\n")
    build_index(chunks)