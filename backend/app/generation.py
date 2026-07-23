"""Build grounded prompts, call the LLM, validate citations."""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from app.llm import generate as llm_generate
from app.retrieval import Result, retrieve

MIN_RERANK_SCORE = 1.0

SYSTEM_RULES = """You answer questions about health insurance policy documents.

Rules:
1. Use ONLY the numbered sources below. Do not use outside knowledge about insurance.
2. Cite every factual claim with its source number in square brackets, e.g. [2].
3. If the sources do not contain the answer, reply exactly: NOT_FOUND
4. If sources disagree, say so and cite each — different insurers have different terms.
5. Quote specific figures (durations, percentages, amounts) exactly as written.
6. Be concise. Two to four sentences unless the question needs more."""


@dataclass
class Answer:
    text: str
    sources: list[Result]
    cited_indices: list[int] = field(default_factory=list)
    invalid_citations: list[int] = field(default_factory=list)
    provider: str = ""
    found: bool = True

    def formatted_sources(self) -> list[str]:
        return [
            f"[{i}] {s.citation()}"
            for i, s in enumerate(self.sources, 1)
            if i in self.cited_indices
        ]


def build_prompt(query: str, results: list[Result]) -> str:
    blocks = [
        f"[{i}] ({r.insurer}, page {r.page})\n{r.text}"
        for i, r in enumerate(results, 1)
    ]
    return (
        f"{SYSTEM_RULES}\n\n"
        f"SOURCES\n{'-' * 60}\n" + "\n\n".join(blocks) + f"\n{'-' * 60}\n\n"
        f"QUESTION: {query}\n\nANSWER:"
    )


def parse_citations(text: str, n_sources: int) -> tuple[list[int], list[int]]:
    """Extract [n] and [n, m, ...] markers; split into valid and fabricated."""
    found: set[int] = set()
    for group in re.findall(r"\[([\d,\s]+)\]", text):
        for part in group.split(","):
            part = part.strip()
            if part.isdigit():
                found.add(int(part))
    valid = sorted(i for i in found if 1 <= i <= n_sources)
    invalid = sorted(i for i in found if i < 1 or i > n_sources)
    return valid, invalid


def answer_question(query: str, min_score: float = MIN_RERANK_SCORE) -> Answer:
    results = retrieve(query)
    relevant = [r for r in results if r.rerank_score >= min_score]

    if not relevant:
        return Answer(
            text="No sufficiently relevant clause was found in the indexed policy documents.",
            sources=[], found=False,
        )

    prompt = build_prompt(query, relevant)
    raw, provider = llm_generate(prompt)

    if raw.strip().upper().startswith("NOT_FOUND"):
        return Answer(
            text="The retrieved sources do not answer this question.",
            sources=relevant, provider=provider, found=False,
        )

    cited, invalid = parse_citations(raw, len(relevant))
    return Answer(
        text=raw, sources=relevant, cited_indices=cited,
        invalid_citations=invalid, provider=provider,
    )