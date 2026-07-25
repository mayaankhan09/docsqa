# Evidex

**Ask health-insurance policies in plain language. Every answer cites the exact clause it came from.**

Evidex is a retrieval-augmented question-answering system over health-insurance policy documents. Ask *"what is the waiting period for pre-existing diseases?"* and it returns a direct answer grounded in the specific clause, insurer, and page it came from — across nine insurers' policy wordings. If no relevant clause exists, it refuses rather than inventing an answer.

The design premise: **an answer is only as trustworthy as the source behind it.** Every claim is traceable, and hallucination is controlled at three layers, not just the prompt.

<p align="center">
  <img src="D:\Users\STORAGE\Documents\docsqa\Screenshot 2026-07-25 114955.png" width="49%" alt="Evidex light mode" />
  <img src="D:\Users\STORAGE\Documents\docsqa\Screenshot 2026-07-25 115307.png" width="49%" alt="Evidex dark mode" />
</p>

---

## Why this is not a tutorial RAG project

Most RAG demos stop at "it returns an answer." Evidex is measured, and the two things that most distinguish it — **cross-encoder reranking** and **evaluation** — are the two things tutorial projects skip.

### Measured results

Evaluated on 15 hand-labelled questions plus 2 out-of-scope refusals ([`backend/evals/`](backend/evals/)):

| Metric | Result |
|---|---|
| Retrieval hit-rate @5 | **73%** |
| Retrieval hit-rate @10 | **93%** |
| Answer faithfulness | **87%** |
| Refusal accuracy (out-of-scope) | **2 / 2** |

The 20-point gap between hit-rate @5 and @10 is the most useful finding: correct clauses are being *retrieved* into the candidate pool but occasionally *ranked* outside the top 5. That localises the bottleneck to reranking rather than retrieval — a diagnosis only possible because retrieval and generation are measured separately.

The two faithfulness "misses" were correct answers with numeric phrasing variance (spelled-out vs. numeral), which is a limitation of substring-based faithfulness scoring rather than a model error — noted honestly because knowing the difference matters.

---

## How it works

```
PDF policies → chunk → embed → FAISS index
                                     │
query ──► embed ──► retrieve top-20 ─┤
                                     ▼
                          cross-encoder rerank
                                     │
                            top-5 ───┤
                                     ▼
                       confidence gate (drop weak)
                                     │
                                     ▼
                    LLM: answer using ONLY these,
                         cite every claim
                                     ▼
                    validate citations, return
```

**Two-stage retrieval.** A bi-encoder (`all-MiniLM-L6-v2`) casts a wide, cheap net over all ~1,800 clauses and returns 20 candidates. A cross-encoder (`ms-marco-MiniLM-L-6-v2`) then re-scores just those 20 by reading the query and each clause *together*, and keeps the best 5. This recovers clauses the bi-encoder buries — in testing, a correct room-rent clause ranked 13th by vector search was promoted to 1st by reranking.

**Three-layer hallucination control.**
1. **Confidence gate** — clauses scoring below a cross-encoder threshold are dropped before the LLM sees them. If nothing clears the bar, the system refuses without an LLM call.
2. **Grounded prompt** — the model is instructed to answer *only* from the numbered sources, cite every claim, and reply `NOT_FOUND` if the answer isn't present.
3. **Citation validation** — citation markers in the answer are parsed and checked against the sources actually provided; fabricated citations are flagged.

**Provider-agnostic generation.** The LLM sits behind a provider interface with an automatic fallback chain (`groq,gemini`). When one provider hits a rate limit, the chain falls through to the next with no downtime — a failure mode encountered and absorbed during development.

---

## Stack

| Layer | Choice | Rationale |
|---|---|---|
| Ingestion | pypdf + langchain-text-splitters | Page-level chunking preserves exact citations |
| Embeddings | `all-MiniLM-L6-v2` (local) | Zero API cost, offline, no rate limits during tuning |
| Vector store | FAISS (`IndexFlatIP`) | Exact search; approximation unwarranted at this scale |
| Reranking | `ms-marco-MiniLM-L-6-v2` cross-encoder | Precision over raw recall |
| Generation | Groq / Gemini (fallback chain) | Free tiers; provider-agnostic by design |
| API | FastAPI | Typed schemas, async, auto-generated docs |
| Frontend | React + Vite | Light/dark, citation-to-source tracing |
| Packaging | Docker + docker-compose | Reproducible deployment |

---

## Corpus

Nine health-insurance policy wordings from nine Indian insurers (SBI General, HDFC ERGO, Future Generali ×2, United India, Bajaj Allianz, Care Health, Aditya Birla, Kotak General), sourced from [IRDAI's public repository](https://irdai.gov.in/health-insurance-products) of filed product documents.

The insurers overlap deliberately — all cover waiting periods, exclusions, sub-limits, and cashless claims, but with different terms and figures. That overlap means naive keyword matching retrieves the wrong insurer's clause, so the corpus genuinely exercises retrieval quality.

---

## Run it locally

**Backend**

```bash
cd backend
python -m venv venv
venv\Scripts\activate           # Windows  (source venv/bin/activate on macOS/Linux)
pip install -r requirements.txt

cp .env.example .env            # add a GROQ_API_KEY (free at console.groq.com)
python scripts/download_corpus.py
python -m scripts.build_index   # ingest + embed + build FAISS index

uvicorn app.main:app --reload --port 8000
```

API docs at `http://127.0.0.1:8000/docs`.

**Frontend**

```bash
cd frontend
npm install
npm run dev                     # http://localhost:5173
```

**With Docker**

```bash
docker compose up --build
```

---

## Project structure

```
evidex/
├── backend/
│   ├── app/
│   │   ├── ingestion.py      PDF → cleaned, page-tagged chunks
│   │   ├── embeddings.py     local sentence-transformer encoder
│   │   ├── vectorstore.py    FAISS index + metadata sidecar
│   │   ├── retrieval.py      two-stage retrieve + rerank
│   │   ├── generation.py     grounded prompt, citation validation
│   │   ├── llm.py            provider chain with fallback
│   │   └── main.py           FastAPI service
│   ├── evals/                gold set + evaluation harness
│   └── Dockerfile
├── frontend/                 React + Vite UI
└── docker-compose.yml
```

---

## Known limitations

- **Table extraction.** Benefit grids and plan-comparison tables flatten into low-quality text during linear PDF extraction. Table-aware parsing is out of scope; noted where it affects retrieval.
- **Faithfulness metric.** Scored by substring match — cheap and lexical. An LLM-as-judge approach would catch semantic drift a substring check misses.
- **Adjacent-chunk duplication.** Neighbouring chunks from the same page occasionally both surface, spending two of five source slots on near-identical text. A page-level dedup step is the planned fix.

---

## What I'd build next

Retrieval hit-rate @5 is the clearest target: the @10 result shows the right clauses are already being found, so the win is in reranking. Candidate improvements — query expansion for short jargon queries, a stronger cross-encoder, and adjacent-chunk deduplication — would be validated against the existing eval harness rather than by eye.