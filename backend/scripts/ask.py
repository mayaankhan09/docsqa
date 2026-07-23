"""Ask a question against the indexed policy documents."""
import sys

from app.generation import answer_question

DEFAULTS = [
    "What is the waiting period for pre-existing diseases?",
    "How do I use the cashless hospitalisation facility?",
    "Is there a limit on room rent?",
    "What is the capital of France?",
]


def ask(query: str) -> None:
    print(f"\n{'=' * 90}\nQ: {query}\n{'-' * 90}")
    a = answer_question(query)
    print(a.text)

    if a.sources:
        print(f"\nRetrieved {len(a.sources)} sources, cited {len(a.cited_indices)}:")
        for i, s in enumerate(a.sources, 1):
            mark = "*" if i in a.cited_indices else " "
            print(f" {mark}[{i}] {s.citation():<45} rerank {s.rerank_score:+.2f}")

    if a.invalid_citations:
        print(f"\n!! FABRICATED CITATIONS: {a.invalid_citations}")
    if a.provider:
        print(f"\nprovider: {a.provider}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        ask(" ".join(sys.argv[1:]))
    else:
        for q in DEFAULTS:
            ask(q)