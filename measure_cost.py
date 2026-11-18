#!/usr/bin/env python3
"""
Measure what one FitFindr run costs.

    python measure_cost.py                 10 runs of the criterion-1 query
    python measure_cost.py --runs 10 --query 'denim jacket under $50'

Runs the agent N times through runlog.logged_run() with the response cache
OFF, so every run sends real requests, then averages the fields the log
already records: wall-clock seconds, seconds of that spent waiting on the rate
limiter, generation requests, and the prompt/output tokens the service
reported. Writes the raw log lines and the averages to results/.

The default query is the criterion-1 query, which runs the whole loop
(search → suggest_outfit → create_fit_card), so the number is the cost of a
complete run, not of one that stopped early.
"""

import argparse
import datetime as dt
import json
import statistics

import config

config.CACHE_ENABLED = False  # before anything calls generate(): every run must be real

from runlog import logged_run  # noqa: E402
from utils.data_loader import get_example_wardrobe  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=10)
    parser.add_argument("--query", default="vintage graphic tee under $30")
    args = parser.parse_args()

    records = []
    for i in range(1, args.runs + 1):
        try:
            _, record = logged_run(args.query, get_example_wardrobe(), source="measure")
        except Exception as exc:  # noqa: BLE001 — already logged with status "error"
            print(f"run {i}: crashed ({type(exc).__name__}: {exc})")
            continue
        records.append(record)
        print(f"run {i}: {record['status']}, {record['duration_s']}s, "
              f"{record['model_calls']} calls, {record['prompt_tokens']}+{record['output_tokens']} tokens")

    def avg(key):
        return statistics.mean(r[key] for r in records)

    def sd(key):
        return statistics.stdev(r[key] for r in records) if len(records) > 1 else 0.0

    active = [r["duration_s"] - r["rate_limit_wait_s"] for r in records]
    summary = {
        "runs": len(records),
        "statuses": {s: sum(r["status"] == s for r in records) for s in {r["status"] for r in records}},
        "avg_duration_s": round(avg("duration_s"), 2),
        "sd_duration_s": round(sd("duration_s"), 2),
        "avg_rate_limit_wait_s": round(avg("rate_limit_wait_s"), 2),
        "avg_active_s": round(statistics.mean(active), 2),
        "avg_model_calls": round(avg("model_calls"), 2),
        "avg_prompt_tokens": round(avg("prompt_tokens"), 1),
        "avg_output_tokens": round(avg("output_tokens"), 1),
        "avg_total_tokens": round(avg("prompt_tokens") + avg("output_tokens"), 1),
        "sd_output_tokens": round(sd("output_tokens"), 1),
        "avg_embedding_requests": round(avg("embedding_requests"), 2),
    }

    lines = [
        "# Cost of one run",
        "",
        f"- When: {dt.datetime.now():%Y-%m-%d %H:%M}",
        f"- Query: `{args.query}` (example wardrobe), {args.runs} runs, cache off",
        f"- Model: `{config.MODEL}`, temperature {config.TEMPERATURE}",
        "- Produced by: `measure_cost.py`, averaging the records `runlog.logged_run()` wrote",
        "",
        "## Averages",
        "",
        "```json",
        json.dumps(summary, indent=2),
        "```",
        "",
        "## Raw log records",
        "",
        "```",
        *[json.dumps(r, ensure_ascii=False) for r in records],
        "```",
    ]
    text = "\n".join(lines) + "\n"
    config.RESULTS_DIR.mkdir(exist_ok=True)
    out = config.RESULTS_DIR / f"cost_{dt.datetime.now():%Y-%m-%d_%H%M}.md"
    out.write_text(text, encoding="utf-8")
    print(json.dumps(summary, indent=2))
    print(f"Wrote {out.relative_to(config.ROOT)}")


if __name__ == "__main__":
    main()
