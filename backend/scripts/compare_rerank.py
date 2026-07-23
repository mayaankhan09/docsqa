"""Show what reranking changes, query by query."""
import sys

from app.retrieval import retrieve

QUERIES = [
    "waiting period for pre-existing diseases",
    "cashless hospitalisation process",
    "maternity coverage exclusions",
    "room rent sub-limit",
]


def show(query: str) -> None:
    print(f"\n{'=' * 100}")
    print(f"QUERY: {query}")
    print("=" * 100)

    baseline = retrieve(query, rerank=False)
    reranked = retrieve(query, rerank=True)

    print("\n-- vector only --")
    for r in baseline:
        print(f"  {r.final_rank}. [{r.vector_score:.3f}] {r.insurer[:24]:<26} p{r.page:<4} {r.text[:70]}")

    print("\n-- after reranking --")
    for r in reranked:
        moved = f"was #{r.vector_rank}"
        flag = "  <-- promoted" if r.vector_rank > settings_top_n() else ""
        print(f"  {r.final_rank}. [{r.rerank_score:+.2f}] ({moved:>7}) {r.insurer[:24]:<26} p{r.page:<4} {r.text[:70]}{flag}")


def settings_top_n() -> int:
    from app.config import settings
    return settings.top_n


if __name__ == "__main__":
    if len(sys.argv) > 1:
        show(" ".join(sys.argv[1:]))
    else:
        for q in QUERIES:
            show(q)
            