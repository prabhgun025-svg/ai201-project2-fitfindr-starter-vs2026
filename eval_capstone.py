#!/usr/bin/env python3
"""
Score capstone criteria C2, C3 and C4 (see criteria.md).

    python eval_capstone.py

Every agent run goes through runlog.logged_run (source "eval") with the
response cache off, so each one leaves a record in logs/runs.jsonl. MCP calls
are recorded on the way through, so the script can see what keyword search
returned before the fallback overwrote session["search_results"].

C2  10 queries: the first 5 from CANDIDATES whose keyword search (as the agent
    parses them) returns results, and the first 5 that return []. That split
    is decided by a dry pass that stops each run right after keyword search,
    with no model calls. Pass: strategy and trace match the branch.
C3  5 unseen off-topic queries. Pass: semantic_search_listings returns [] AND
    the agent run has no selected item, no fit card and 0 model calls.
C4  the 10 plural/synonym queries from retrieval_queries.py. Pass: the
    selected listing id is one of that query's labelled ids.

Results go to results/capstone_criteria_<timestamp>.md.
"""

import datetime as dt
import json

import config

config.CACHE_ENABLED = False  # every run must send real requests

import agent  # noqa: E402
import trace as trace_module  # noqa: E402
from retrieval_queries import QUERIES  # noqa: E402
from runlog import logged_run  # noqa: E402
from tools import semantic_search_listings  # noqa: E402
from utils.data_loader import get_example_wardrobe  # noqa: E402

CANDIDATES = [
    "chelsea boots", "denim jacket under $50", "cargo pants", "graphic tee",
    "leather belt", "slip dress", "tees", "hoodies", "dresses", "blazers",
    "belts", "purse", "trainers", "headwear", "sweater", "jorts",
    "windbreakers", "flannels",
]
OFF_TOPIC = [
    "airline ticket refund",
    "how to change a car tire",
    "python list comprehension",
    "pizza delivery near me",
    "mortgage interest rates",
]

_real_call_tool = agent.call_tool
_calls: list[tuple[str, dict, object]] = []


class _StopAfterKeyword(Exception):
    pass


def _recording_call_tool(name, arguments):
    result = _real_call_tool(name, arguments)
    _calls.append((name, arguments, result))
    return result


def _keyword_only(name, arguments):
    result = _real_call_tool(name, arguments)
    _calls.append((name, arguments, result))
    raise _StopAfterKeyword


def dry_keyword(query: str) -> list:
    """What the agent's keyword search returns for this query. No model calls."""
    _calls.clear()
    agent.call_tool = _keyword_only
    try:
        agent.run_agent(query, get_example_wardrobe())
    except _StopAfterKeyword:
        pass
    finally:
        agent.call_tool = _real_call_tool
    return _calls[0][2] or []


def real_run(query: str) -> dict:
    """One logged agent run, with MCP calls and the trace captured."""
    _calls.clear()
    trace_module.start_trace()
    agent.call_tool = _recording_call_tool
    try:
        session, record = logged_run(query, get_example_wardrobe(), source="eval")
    finally:
        agent.call_tool = _real_call_tool
    keyword = next((r for n, _, r in _calls if n == "search_listings"), None)
    return {
        "query": query,
        "session": session,
        "record": record,
        "trace": trace_module.get_trace(),
        "keyword_results": keyword or [],
        "semantic_called": any(n == "semantic_search_listings" for n, _, _ in _calls),
        "parsed": session.get("parsed"),
    }


def ids(listings, n=3):
    return ", ".join(l["id"] for l in (listings or [])[:n]) or "(empty)"


def main() -> None:
    out = [f"# Capstone criteria C2–C4 — run {dt.datetime.now():%Y-%m-%d %H:%M}", "",
           f"Cache off. Model `{config.MODEL}`, embedding `{config.EMBEDDING_MODEL}`, "
           f"floor {config.EMBEDDING_MIN_SIMILARITY}. Produced by `eval_capstone.py`; every run "
           f"below also has a record in `logs/runs.jsonl` (source \"eval\").", ""]

    # ── C2 ────────────────────────────────────────────────────────────────────
    print("C2: sorting candidates by keyword result (no model calls)…", flush=True)
    with_results, empty = [], []
    for q in CANDIDATES:
        (with_results if dry_keyword(q) else empty).append(q)
    chosen = with_results[:5] + empty[:5]
    c2 = []
    for q in chosen:
        r = real_run(q)
        kw_empty = not r["keyword_results"]
        strategy = r["session"].get("search_strategy")
        has_step = "semantic_search_listings" in r["trace"]
        expected = "embedding" if kw_empty else "keyword"
        ok = strategy == expected and has_step == kw_empty and r["semantic_called"] == kw_empty
        c2.append((r, kw_empty, strategy, has_step, ok))
        print(f"  C2 {q!r}: keyword {'empty' if kw_empty else 'results'} → {strategy} "
              f"{'PASS' if ok else 'FAIL'}", flush=True)
    c2_pass = sum(x[4] for x in c2)
    out += ["## C2. Strategy matches whether keyword search was empty — target 10/10", "",
            f"Candidates with keyword results: {len(with_results)}; with keyword `[]`: {len(empty)}. "
            f"First 5 of each used.", "",
            "| Query | Parsed | Keyword top 3 | Keyword empty? | Strategy | semantic step in trace? | Result |",
            "|---|---|---|---|---|---|---|"]
    for r, kw_empty, strategy, has_step, ok in c2:
        out.append(f"| {r['query']} | `{json.dumps(r['parsed'])}` | {ids(r['keyword_results'])} | "
                   f"{'yes' if kw_empty else 'no'} | {strategy} | {'yes' if has_step else 'no'} | "
                   f"{'PASS' if ok else 'FAIL'} |")
    out += ["", f"**{c2_pass}/10 — {'MET' if c2_pass == 10 else 'MISSED'}**", ""]

    # ── C3 ────────────────────────────────────────────────────────────────────
    c3 = []
    for q in OFF_TOPIC:
        direct = semantic_search_listings(q)
        r = real_run(q)
        rec = r["record"]
        agent_ok = (rec["output"]["selected_item"] is None and rec["output"]["fit_card"] is None
                    and rec["model_calls"] == 0)
        ok = not direct and agent_ok
        c3.append((r, direct, agent_ok, ok))
        print(f"  C3 {q!r}: direct {len(direct)} listings, agent "
              f"{rec['status']} with {rec['model_calls']} calls → {'PASS' if ok else 'FAIL'}", flush=True)
    c3_pass = sum(x[3] for x in c3)
    out += ["## C3. Unseen off-topic queries: 0 listings and 0 model calls — target 5/5", "",
            "| Query | `semantic_search_listings` direct | Agent: parsed | Agent: keyword top 3 | "
            "Strategy | Selected | Model calls | Result |",
            "|---|---|---|---|---|---|---|---|"]
    for r, direct, agent_ok, ok in c3:
        rec = r["record"]
        sel = rec["output"]["selected_item"]
        out.append(f"| {r['query']} | {len(direct)} listings | `{json.dumps(r['parsed'])}` | "
                   f"{ids(r['keyword_results'])} | {rec['search_strategy']} | "
                   f"{sel['id'] + ' ' + sel['title'] if sel else '—'} | {rec['model_calls']} | "
                   f"{'PASS' if ok else 'FAIL'} |")
    out += ["", f"**{c3_pass}/5 — {'MET' if c3_pass == 5 else 'MISSED'}**", ""]

    # ── C4 ────────────────────────────────────────────────────────────────────
    c4 = []
    for q in [q for q in QUERIES if q["group"] in ("plural", "synonym")]:
        r = real_run(q["query"])
        sel = r["record"]["output"]["selected_item"]
        ok = bool(sel) and sel["id"] in q["relevant"]
        c4.append((q, r, sel, ok))
        print(f"  C4 {q['query']!r}: selected {sel['id'] if sel else None} "
              f"→ {'PASS' if ok else 'FAIL'}", flush=True)
    c4_pass = sum(x[3] for x in c4)
    out += ["## C4. Plural/synonym queries typed into the agent select a labelled listing — target ≥ 8/10", "",
            "| Group | Query | Labelled ids | Parsed | Strategy | Selected | Result |",
            "|---|---|---|---|---|---|---|"]
    for q, r, sel, ok in c4:
        out.append(f"| {q['group']} | {q['query']} | {', '.join(q['relevant'])} | "
                   f"`{json.dumps(r['parsed'])}` | {r['record']['search_strategy']} | "
                   f"{sel['id'] + ' ' + sel['title'] if sel else '— (' + str(r['record']['status']) + ')'} | "
                   f"{'PASS' if ok else 'FAIL'} |")
    out += ["", f"**{c4_pass}/10 — {'MET' if c4_pass >= 8 else 'MISSED'}**", ""]

    text = "\n".join(out) + "\n"
    config.RESULTS_DIR.mkdir(exist_ok=True)
    path = config.RESULTS_DIR / f"capstone_criteria_{dt.datetime.now():%Y-%m-%d_%H%M}.md"
    path.write_text(text, encoding="utf-8")
    print(f"\nC2 {c2_pass}/10   C3 {c3_pass}/5   C4 {c4_pass}/10")
    print(f"Wrote {path.relative_to(config.ROOT)}")


if __name__ == "__main__":
    main()
