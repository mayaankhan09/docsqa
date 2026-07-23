"""Quick manual check of retrieval quality."""
import sys

from app.embeddings import embed_query
from app.vectorstore import search

QUERIES = [
    "waiting period for pre-existing diseases",
    "cashless hospitalisation process",
    "maternity coverage exclusions",
    "room rent sub-limit",
]


def run(query: str, k: int = 5) -> None:
    print(f"\n=== {query}")
    for r in search(embed_query(query), k):
        print(f"{r['score']:.3f}  {r['insurer'][:26]:<28} p{r['page']:<4} {r['text'][:95]}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        run(" ".join(sys.argv[1:]))
    else:
        for q in QUERIES:
            run(q)