# DocsQA — RAG assistant for insurance policy documents

Answers natural-language questions about health insurance policy wordings and
grounds every answer in the exact clause it came from, with insurer and page
number. Built to make hallucination visible and verifiable: if the system
cannot cite a source, it should not answer.

Example: *"What is the waiting period for pre-existing diseases?"* returns the
relevant clause from each insurer alongside a citation such as
`SBI General — SuperHealth, p. 14`.

## Stack

| Layer | Choice | Why |
|---|---|---|
| Ingestion | pypdf + langchain-text-splitters | Fast, no external service |
| Embeddings | `all-MiniLM-L6-v2` (local) | Zero API cost, runs offline |
| Vector store | FAISS (local, persisted) | No hosted DB dependency |
| Reranking | `ms-marco-MiniLM-L-6-v2` cross-encoder | Retrieval precision over raw recall |
| Generation | Gemini, with Groq fallback | Provider-agnostic behind one interface |
| API | FastAPI | Async, typed request/response models |
| Frontend | React + Vite + Tailwind | *(planned)* |
| Packaging | Docker | *(planned)* |

Generation sits behind a provider interface, so the LLM vendor is a config
value rather than a dependency baked into the retrieval code.

## Corpus

Nine health insurance policy wordings from nine Indian insurers, drawn from
IRDAI's public repository of filed product documents
(<https://irdai.gov.in/health-insurance-products>). These are public regulatory
filings.

Nine insurers covering the same concepts — waiting periods, pre-existing
disease, sub-limits, exclusions, cashless claims — with different terms and
figures. That overlap is deliberate: naive keyword matching retrieves the wrong
insurer's clause, so the corpus actually exercises retrieval quality.

## Pipeline

1. **Extract** — per-page text via pypdf, preserving page numbers for citation
2. **Clean** — headers and footers removed by frequency analysis (lines appearing on ≥60% of pages), page-number artifacts stripped
3. **Chunk** — recursive character splitting, 800 chars with 120-char overlap
4. **Embed** — *(planned, Phase 2)*
5. **Retrieve and rerank** — *(planned, Phase 3)*
6. **Generate with citations** — *(planned, Phase 4)*

### Chunking rationale

800 characters is set by the embedding model, not by preference.
`all-MiniLM-L6-v2` truncates input at 256 tokens and discards the remainder
**silently** — no error is raised. At roughly 4 characters per token, 800 chars
lands near 200 tokens, leaving headroom for token-dense legal text. A larger
chunk size would drop more than half of each chunk before it was ever embedded.

Secondarily, policy clauses run 100–500 characters, so 800 fits a complete
clause plus its qualifying conditions. The 120-char overlap (~15%) keeps a
clause intact in at least one chunk when it straddles a boundary.

Chunking is done **per page rather than per document**. This keeps page numbers
exact, at the cost of splitting clauses that span a page break. Citation
precision was prioritised over clause continuity, since a user verifying an
answer needs to know which page to open.

Boilerplate is detected by frequency rather than a hardcoded blocklist — nine
insurers use nine different footer formats, so a static list would not
generalise.

**Current corpus stats:** 9 documents → ~1,800 chunks, median 686 characters.

## Known limitations

- **Extraction artifacts.** pypdf introduces intra-word spacing errors
  (`c alculating`, `forwar d`) in ~15% of chunks, affecting well under 1% of
  words. pdfplumber was evaluated as an alternative and rejected: 3–5× slower
  extraction for artifacts of a different kind rather than fewer. Revisit if
  Phase 8 retrieval evaluation shows measurable degradation.
- **Page-boundary splits.** A clause spanning two pages is split across two
  chunks. Accepted as a consequence of per-page chunking (see above).
- **Scanned documents unsupported.** No OCR stage; the corpus was verified to
  be digitally generated text.

## Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux
pip install -r requirements.txt

cp .env.example .env           # then add your API key
python scripts/download_corpus.py
python -m app.ingestion        # verify: ~1,800 chunks
```

Requires a Gemini API key (free tier, <https://aistudio.google.com>). A Groq
key is optional and used as a fallback provider.

All commands run from `backend/` with the virtualenv active.

## Status

- [x] **Phase 0** — Scaffold, config, corpus acquisition
- [x] **Phase 1** — Ingestion, cleaning, chunking
- [ ] **Phase 2** — Embeddings and FAISS index
- [ ] **Phase 3** — Retrieval with cross-encoder reranking
- [ ] **Phase 4** — Citation-grounded generation
- [ ] **Phase 5** — FastAPI service
- [ ] **Phase 6** — React frontend
- [ ] **Phase 7** — Containerisation
- [ ] **Phase 8** — Retrieval and faithfulness evaluation
- [ ] **Phase 9** — Deployment

## Architecture

*To be documented once the retrieval pipeline is complete (Phase 3).*

## Evaluation

*To be documented (Phase 8). Planned metrics: retrieval hit rate, answer
faithfulness, answer relevance.*