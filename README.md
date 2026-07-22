# DocsQA — RAG assistant for insurance policy documents

DocsQA answers natural-language questions over insurance policy wordings with clause-level citations. Given a user query, it retrieves the most relevant passages from a corpus of IRDAI-filed policy documents using semantic search (FAISS + sentence-transformers), reranks them with a cross-encoder, and synthesises a grounded answer via Gemini or Groq — citing the exact clause and document it drew each fact from.

## Stack

- **Backend:** FastAPI, sentence-transformers (embeddings), FAISS (vector index), cross-encoder reranking, Gemini / Groq (generation), PyPDF, LangChain text splitters
- **Frontend:** React (Vite)
- **Infra:** Docker

## Corpus

The document corpus consists of publicly available health insurance policy wordings filed with the Insurance Regulatory and Development Authority of India (IRDAI) by 9 Indian insurers: SBI Health, HDFC Ergo, Future Generali, United India, Bajaj Allianz, Care Health, and Aditya Birla Health.

## Setup

```bash
# 1. Create and activate a virtual environment
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

# 2. Install dependencies
pip install -r backend/requirements.txt

# 3. Configure environment
cp backend/.env.example backend/.env
# Edit backend/.env and add your GEMINI_API_KEY (and optionally GROQ_API_KEY)

# 4. Download the policy corpus
python backend/scripts/download_corpus.py
```

## Architecture

TODO

## Evaluation

TODO
