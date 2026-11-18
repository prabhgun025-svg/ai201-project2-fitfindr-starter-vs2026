"""
Structured run log: one JSON record per agent run, failures included.

Every entry point (the CLI, the web server, measure_cost.py) runs the agent
through `logged_run()` instead of calling `run_agent()` directly, so every run
leaves exactly one record, whether it finished, stopped early, or crashed.
Requests the server turns away before the agent runs (no query, too many
requests) are logged with `log_rejected()`.

Records go to logs/runs.jsonl, one JSON object per line. With echo=True (the
web server) each record is also printed to stdout, because a host like Render
wipes its disk on restart but keeps stdout in its log viewer.

Fields in every record:
    timestamp         UTC, ISO 8601
    run_id            8 hex chars, to find one run again
    source            "cli", "http", or "measure"
    status            "ok"          finished with a fit card
                      "no_results"  both searches empty, stopped before suggest_outfit
                      "model_error" found an item, but the model couldn't be reached
                      "error"       run_agent raised (a crash); see `exception`
                      "rejected"    the server refused the request; see `reason`
    input             {"query", "wardrobe_items"}
    parsed            what the query parser pulled out (description, size, max_price)
    search_strategy   "keyword", or "embedding" if the fallback ran
    results_count     how many listings the search that was used returned
    output            {"selected_item", "fit_card", "outfit_chars", "error"}
    duration_s        wall-clock seconds for the whole run
    rate_limit_wait_s seconds of that spent waiting on the request limiter
    model_calls       generation requests actually sent (cache hits excluded)
    cache_hits        generation calls answered from the local cache (cost 0)
    prompt_tokens     input tokens the service reported for those calls
    output_tokens     output tokens the service reported
    embedding_requests  query embeddings sent (1 when the fallback ran). These
                      happen inside the MCP server process, so their tokens
                      aren't in prompt_tokens; a query embedding is a few tokens.
    mcp_calls         MCP tool calls (1, or 2 with the fallback)
    model             generation model name
    exception         "Type: message" when status is "error", else null
"""

import datetime as dt
import hashlib
import json
import time
import uuid

import config
import generate

LOG_PATH = config.ROOT / "logs" / "runs.jsonl"


def _now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def _write(record: dict, echo: bool) -> None:
    line = json.dumps(record, ensure_ascii=False)
    try:
        LOG_PATH.parent.mkdir(exist_ok=True)
        with LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
    except OSError as exc:  # a full or read-only disk must not break a run
        print(f"[runlog] couldn't write {LOG_PATH}: {exc}", flush=True)
        echo = True
    if echo:
        print(f"[runlog] {line}", flush=True)


def client_tag(raw: str | None) -> str | None:
    """A short hash of the client address, so rejections can be grouped without storing IPs."""
    if not raw:
        return None
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:8]


def _status(session: dict | None, failure: str | None) -> str:
    if failure:
        return "error"
    if session.get("error"):
        return "model_error" if session.get("selected_item") else "no_results"
    return "ok"


def logged_run(query: str, wardrobe: dict, source: str, echo: bool = False):
    """
    Run the agent once and log it. Returns (session, record).

    If run_agent raises, the record is written with status "error" first and
    the exception is re-raised, so callers handle it exactly as before.
    """
    from agent import run_agent

    calls0 = generate.call_count()
    hits0 = generate.cache_hits()
    tokens0 = generate.token_counts()
    wait0 = generate.wait_seconds()
    timestamp = _now()
    start = time.perf_counter()

    session, failure, raised = None, None, None
    try:
        session = run_agent(query, wardrobe)
    except Exception as exc:  # noqa: BLE001 — logged, then re-raised
        failure = f"{type(exc).__name__}: {exc}"
        raised = exc

    duration = time.perf_counter() - start
    tokens1 = generate.token_counts()
    s = session or {}
    item = s.get("selected_item") or None
    strategy = s.get("search_strategy")

    record = {
        "timestamp": timestamp,
        "run_id": uuid.uuid4().hex[:8],
        "source": source,
        "status": _status(session, failure),
        "input": {"query": query, "wardrobe_items": len((wardrobe or {}).get("items", []))},
        "parsed": s.get("parsed") or None,
        "search_strategy": strategy,
        "results_count": len(s.get("search_results") or []),
        "output": {
            "selected_item": (
                {k: item.get(k) for k in ("id", "title", "price", "platform")} if item else None
            ),
            "fit_card": s.get("fit_card"),
            "outfit_chars": len(s.get("outfit_suggestion") or ""),
            "error": s.get("error"),
        },
        "duration_s": round(duration, 2),
        "rate_limit_wait_s": round(generate.wait_seconds() - wait0, 2),
        "model_calls": generate.call_count() - calls0,
        "cache_hits": generate.cache_hits() - hits0,
        "prompt_tokens": tokens1["prompt"] - tokens0["prompt"],
        "output_tokens": tokens1["output"] - tokens0["output"],
        "embedding_requests": 1 if strategy == "embedding" else 0,
        "mcp_calls": 0 if session is None else (2 if strategy == "embedding" else 1),
        "model": config.MODEL,
        "exception": failure,
    }
    _write(record, echo)

    if raised is not None:
        raise raised
    return session, record


def log_rejected(query, reason: str, source: str, client: str | None = None, echo: bool = False) -> dict:
    """Log a request that was refused before the agent ran."""
    record = {
        "timestamp": _now(),
        "run_id": uuid.uuid4().hex[:8],
        "source": source,
        "status": "rejected",
        "reason": reason,
        "input": {"query": query},
        "client": client,
        "duration_s": 0.0,
        "model_calls": 0,
        "exception": None,
    }
    _write(record, echo)
    return record
