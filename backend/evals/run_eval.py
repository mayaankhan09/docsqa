"""Evaluate retrieval and generation against the gold set."""
from __future__ import annotations

import json
from pathlib import Path

from app.generation import answer_question
from app.retrieval import retrieve

GOLD = Path(__file__).parent / "gold.jsonl"


def load_gold() -> list[dict]:
    with GOLD.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def retrieval_hit(item: dict, results, k: int) -> bool:
    """Hit if a top-k result matches an expected insurer (and page, if specified)."""
    top = results[:k]
    want_pages = set(item.get("expected_pages", []))
    want_insurers = set(item.get("expected_insurers", []))

    for r in top:
        insurer_ok = (not want_insurers) or any(ins in r.insurer for ins in want_insurers)
        page_ok = (not want_pages) or (r.page in want_pages)
        if insurer_ok and page_ok:
            return True
    return False


def faithful(item: dict, answer_text: str) -> bool:
    """Cheap proxy: does the answer contain every required substring?"""
    needles = item.get("answer_contains", [])
    if not needles:
        return True
    low = answer_text.lower()
    return all(n.lower() in low for n in needles)


def main() -> None:
    gold = load_gold()

    # Separate answerable questions from refusal cases
    answerable = [g for g in gold if not g.get("expect_not_found")]
    refusals = [g for g in gold if g.get("expect_not_found")]
    n = len(answerable)

    hits_at_5 = hits_at_10 = faithful_count = 0
    rows = []

    for item in answerable:
        q = item["query"]
        raw = retrieve(q, top_n=10, rerank=True)
        h5 = retrieval_hit(item, raw, 5)
        h10 = retrieval_hit(item, raw, 10)
        hits_at_5 += h5
        hits_at_10 += h10

        ans = answer_question(q)
        f = faithful(item, ans.text)
        faithful_count += f
        rows.append((q[:50], h5, f, ans.found))

    # Refusal cases: correct behaviour is found == False
    refused_ok = 0
    for item in refusals:
        ans = answer_question(item["query"])
        ok = not ans.found
        refused_ok += ok
        rows.append((item["query"][:50], "-", "-", ans.found))

    print(f"\n{'query':<52} {'R@5':<5} {'faith':<6} found")
    print("-" * 74)
    for q, h5, f, found in rows:
        h5s = h5 if isinstance(h5, str) else ("Y" if h5 else ".")
        fs = f if isinstance(f, str) else ("Y" if f else ".")
        print(f"{q:<52} {h5s:<5} {fs:<6} {found}")

    print("-" * 74)
    print(f"Retrieval hit-rate @5:   {hits_at_5}/{n} = {100*hits_at_5/n:.0f}%")
    print(f"Retrieval hit-rate @10:  {hits_at_10}/{n} = {100*hits_at_10/n:.0f}%")
    print(f"Answer faithfulness:     {faithful_count}/{n} = {100*faithful_count/n:.0f}%")
    if refusals:
        print(f"Refusal accuracy:        {refused_ok}/{len(refusals)} correctly declined")


if __name__ == "__main__":
    main()