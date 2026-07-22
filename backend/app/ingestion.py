"""Load policy PDFs, clean the text, and split into retrievable chunks."""
from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, asdict
from pathlib import Path

import pypdf
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import settings

BACKEND_DIR = Path(__file__).resolve().parents[1]

INSURERS = {
    "sbi_superhealth": "SBI General — SuperHealth",
    "hdfcergo_optima_restore": "HDFC ERGO — Optima Restore",
    "futuregenerali_health_suraksha": "Future Generali — Health Suraksha",
    "futuregenerali_group_health": "Future Generali — Group Health",
    "unitedindia_group_health": "United India — Group Health",
    "bajaj_health_total": "Bajaj Allianz — Health Total",
    "carehealth_group": "Care Health — Group Health",
    "adityabirla_group_activ": "Aditya Birla — Group Activ Health",
    "kotak_health_care": "Kotak General — Health Care",
}


@dataclass
class Chunk:
    chunk_id: str
    text: str
    source: str
    insurer: str
    page: int

    def to_dict(self) -> dict:
        return asdict(self)


def extract_pages(pdf_path: Path) -> list[str]:
    """Return one string per page, in order."""
    reader = pypdf.PdfReader(str(pdf_path))
    return [(page.extract_text() or "") for page in reader.pages]


def find_boilerplate(pages: list[str], threshold: float = 0.6) -> set[str]:
    """Identify short lines repeated across most pages (headers and footers)."""
    counts: Counter[str] = Counter()
    for page in pages:
        for line in {ln.strip() for ln in page.splitlines() if ln.strip()}:
            if len(line) < 100:
                counts[line] += 1
    cutoff = max(2, int(len(pages) * threshold))
    return {line for line, n in counts.items() if n >= cutoff}


def clean_page(text: str, boilerplate: set[str]) -> str:
    kept = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped in boilerplate:
            continue
        if re.fullmatch(r"(page\s*)?[|\-\s]*\d+[|\-\s]*", stripped, re.I):
            continue
        kept.append(stripped)
    joined = " ".join(kept)
    return re.sub(r"\s+", " ", joined).strip()


def build_splitter() -> RecursiveCharacterTextSplitter:
    return RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        separators=["\n\n", "\n", ". ", "; ", ", ", " ", ""],
        length_function=len,
    )


def ingest_pdf(pdf_path: Path, splitter: RecursiveCharacterTextSplitter) -> list[Chunk]:
    stem = pdf_path.stem
    insurer = INSURERS.get(stem, stem.replace("_", " ").title())

    raw_pages = extract_pages(pdf_path)
    boilerplate = find_boilerplate(raw_pages)

    chunks: list[Chunk] = []
    for page_no, raw in enumerate(raw_pages, start=1):
        cleaned = clean_page(raw, boilerplate)
        if len(cleaned) < 120:
            continue
        for i, piece in enumerate(splitter.split_text(cleaned)):
            piece = re.sub(r"^[\s.,;:)\]]+", "", piece).strip()
            if len(piece) < 50:
                continue
            chunks.append(
                Chunk(
                    chunk_id=f"{stem}:p{page_no}:c{i}",
                    text=piece,
                    source=pdf_path.name,
                    insurer=insurer,
                    page=page_no,
                )
            )
    return chunks


def ingest_all(raw_dir: Path | None = None) -> list[Chunk]:
    raw_dir = raw_dir or (BACKEND_DIR / settings.raw_dir)
    splitter = build_splitter()

    all_chunks: list[Chunk] = []
    for pdf_path in sorted(raw_dir.glob("*.pdf")):
        chunks = ingest_pdf(pdf_path, splitter)
        print(f"{pdf_path.name:<40} {len(chunks):>5} chunks")
        all_chunks.extend(chunks)
    return all_chunks


if __name__ == "__main__":
    chunks = ingest_all()
    print(f"\ntotal: {len(chunks)} chunks")
    if chunks:
        sizes = sorted(len(c.text) for c in chunks)
        print(f"median chunk: {sizes[len(sizes) // 2]} chars")
        print(f"\nsample — {chunks[len(chunks) // 2].chunk_id}")
        print(chunks[len(chunks) // 2].text[:400])