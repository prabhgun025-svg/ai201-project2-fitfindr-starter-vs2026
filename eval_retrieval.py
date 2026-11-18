#!/usr/bin/env python3
"""
Capstone measurement: hit@3 for keyword search vs embedding search.

    python eval_retrieval.py

Runs every labelled query in retrieval_queries.py through both strategies, plus
the agent's actual policy (keyword first, embedding only when keyword is empty),
and writes a markdown table into results/.

The search functions are called directly, with the query text exactly as
labelled and no size or price filter. That keeps the agent's regex query parser
out of the measurement, so a difference in the numbers is a difference in
retrieval and nothing else.

hit@3: a query counts as a hit when at least one of its labelled ids appears in
the strategy's top 3 results. An empty result is a miss.

Cost: one embedding request for the whole catalogue (then cached in .cache/),
plus one per query, so about 16 requests on a cold run. No generation calls.
"""

import datetime as dt

import config
from retrieval_queries import QUERIES
from tools import search_listings, semantic_search_scored

K = 3


def _hit(ids: list[str], relevant: list[str]) -> bool:
    return any(i in relevant for i in ids[:K])


def main() -> None:
    rows = []
    for q in QUERIES:
        kw_ids = [l["id"] for l in search_listings(q["query"])]
        scored = semantic_search_scored(q["query"])
        em_ids = [l["id"] for _, l in scored]
        policy_ids = kw_ids if kw_ids else em_ids
        rows.append({
            **q,
            "kw_ids": kw_ids, "em_ids": em_ids, "em_scores": [s for s, _ in scored],
            "kw": _hit(kw_ids, q["relevant"]),
            "em": _hit(em_ids, q["relevant"]),
            "policy": _hit(policy_ids, q["relevant"]),
            "fallback": not kw_ids,
        })

    def tally(group: str | None, key: str) -> str:
        sel = [r for r in rows if group is None or r["group"] == group]
        return f"{sum(r[key] for r in sel)}/{len(sel)}"

    mark = lambda b: "HIT" if b else "miss"
    fmt = lambda ids: ", ".join(ids[:K]) or "(empty)"

    lines = [
        f"# Retrieval eval — hit@{K}",
        "",
        f"Run {dt.datetime.now():%Y-%m-%d %H:%M}. Embedding model `{config.EMBEDDING_MODEL}`, "
        f"min similarity {config.EMBEDDING_MIN_SIMILARITY}. No size or price filter.",
        "",
        "## Summary",
        "",
        "| Group | Keyword | Embedding | Agent policy (keyword → embedding if empty) |",
        "|---|---|---|---|",
    ]
    for g in ["plural", "synonym", "exact"]:
        lines.append(f"| {g} | {tally(g, 'kw')} | {tally(g, 'em')} | {tally(g, 'policy')} |")
    lines.append(f"| **all** | **{tally(None, 'kw')}** | **{tally(None, 'em')}** | **{tally(None, 'policy')}** |")
    lines += [
        "",
        "## Per query",
        "",
        "| Group | Query | Relevant | Keyword top 3 | KW | Embedding top 3 (score) | EM | Fallback ran? | Policy |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        em = ", ".join(f"{i} ({s:.2f})" for i, s in zip(r["em_ids"][:K], r["em_scores"])) or "(empty)"
        lines.append(
            f"| {r['group']} | {r['query']} | {', '.join(r['relevant'])} | {fmt(r['kw_ids'])} | "
            f"{mark(r['kw'])} | {em} | {mark(r['em'])} | {'yes' if r['fallback'] else 'no'} | {mark(r['policy'])} |"
        )

    text = "\n".join(lines) + "\n"
    print(text)
    config.RESULTS_DIR.mkdir(exist_ok=True)
    out = config.RESULTS_DIR / f"retrieval_{dt.datetime.now():%Y-%m-%d_%H%M}.md"
    out.write_text(text, encoding="utf-8")
    print(f"Wrote {out.relative_to(config.ROOT)}")


if __name__ == "__main__":
    main()
