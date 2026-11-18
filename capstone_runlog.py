#!/usr/bin/env python3
"""
Run every capstone criterion (C1–C5) three separate times, save the real
output, and score each run against the targets in criteria.md.

    python capstone_runlog.py              3 runs (default)
    python capstone_runlog.py --runs 1

Each run calls the same three scripts a person would, as separate processes:

    eval_retrieval.py                C1  (embedding calls only)
    eval_capstone.py                 C2, C3, C4
    run_eval.py --label capstone_runN    C5  (5 tries per scenario, cache off)

Everything they print and write is saved under results/capstone_runs/runN/.
The scoring at the end reads only those saved files, plus one deterministic
re-check for original criterion 5: each matching-query try's parsed query is
re-run through tools.search_listings to read the prices of every listing it
returned, because run_eval.py saves the count of results but not their prices.

Writes results/capstone_runs/RUN_LOG.md with the table: one row per criterion,
one column per run, and a verdict that is MET only if every run met the target.
"""

import argparse
import datetime as dt
import json
import re
import shutil
import subprocess
import sys

import config

OUT = config.RESULTS_DIR / "capstone_runs"
PY = sys.executable


def run(cmd: list[str], log_path) -> str:
    """Run one script, save everything it printed, return it."""
    proc = subprocess.run(cmd, cwd=config.ROOT, capture_output=True, text=True)
    text = proc.stdout + ("\n[stderr]\n" + proc.stderr if proc.stderr.strip() else "")
    text += f"\n[exit code {proc.returncode}]\n"
    log_path.write_text(text, encoding="utf-8")
    return text


def move_written(text: str, dest_dir) -> list[str]:
    """Move files a script reported with 'Wrote results/…' into this run's folder."""
    moved = []
    for rel in re.findall(r"Wrote (results/\S+\.md)", text):
        src = config.ROOT / rel
        if src.exists():
            shutil.move(str(src), dest_dir / src.name)
            moved.append(src.name)
    return moved


# ── scoring ──────────────────────────────────────────────────────────────────

def score_c1(text: str) -> tuple[str, bool]:
    rows = {}
    for group, kw, em in re.findall(r"^\| \**(plural|synonym|exact|all)\** \| \**(\d+)/\d+\** \| \**(\d+)/\d+\**",
                                    text, re.M):
        rows[group] = (int(kw), int(em))
    if set(rows) != {"plural", "synonym", "exact", "all"}:
        return "no result", False
    kw_new = rows["plural"][0] + rows["synonym"][0]
    em_new = rows["plural"][1] + rows["synonym"][1]
    ok = rows["all"][1] >= 12 and em_new > kw_new and rows["exact"][1] >= rows["exact"][0]
    return f"{rows['all'][1]}/15 (keyword {rows['all'][0]}/15)", ok


def score_c234(text: str):
    m = re.search(r"C2 (\d+)/10\s+C3 (\d+)/5\s+C4 (\d+)/10", text)
    if not m:
        return [("no result", False)] * 3
    c2, c3, c4 = map(int, m.groups())
    return [(f"{c2}/10", c2 == 10), (f"{c3}/5", c3 == 5), (f"{c4}/10", c4 >= 8)]


_SCEN = ["matching query completes", "impossible query stops early", "empty wardrobe"]


def _sections(text: str, prefix: str = "") -> dict[str, str]:
    """Split run_eval output into its three scenarios. The .md file names them in
    its summary table first, so there the headings ("### name") are the anchors."""
    out = {}
    for i, name in enumerate(_SCEN):
        start = text.find(prefix + name)
        end = text.find(prefix + _SCEN[i + 1], start) if i + 1 < len(_SCEN) else len(text)
        out[name] = text[start:end] if start >= 0 else ""
    return out


def _tries(section: str) -> list[tuple[str, str]]:
    """(trace for this try, the 'try N:' result line) pairs, in order."""
    parts = re.split(r"^(  try \d+: .*)$", section, flags=re.M)
    return [(parts[i], parts[i + 1]) for i in range(0, len(parts) - 1, 2)]


def _sentences(card: str) -> int:
    body = re.sub(r"^\s*\[lst_\d+ · \$[\d.]+\]\s*", "", card.strip())
    body = "\n".join(l for l in body.splitlines() if not l.strip().startswith("#"))
    # A fragment with no letters (e.g. trailing "🌿✨") isn't a sentence.
    return len([s for s in re.split(r"(?<=[.!?])[\"”']?\s+", body.strip()) if re.search(r"[A-Za-z]", s)])


def score_c5(stdout: str, md: str) -> tuple[str, bool, dict]:
    from tools import search_listings

    out_secs, md_secs = _sections(stdout), _sections(md, "### ")
    match_tries = _tries(out_secs[_SCEN[0]])
    imp_tries = _tries(out_secs[_SCEN[1]])
    sel = {k: re.findall(r"- selected_item: (lst_\d+|\(none\))", md_secs[k]) for k in _SCEN}
    cards = re.findall(r"Fit card:\s*\n```\s*\n(.*?)\n```", md_secs[_SCEN[0]], re.S)

    c = {}
    # 1. matching query completes all three tools (target 4/5)
    c[1] = sum("completed" in line for _, line in match_tries)
    # 2. impossible query stops before suggest_outfit (target 5/5)
    c[2] = sum("stopped early" in line and "suggest_outfit" not in trace for trace, line in imp_tries)
    # 3. selected id and price stamped on both model outputs (target 5/5)
    n3 = 0
    for trace, _ in match_tries:
        sel_m = re.search(r"\[\d+\] select_item.*?\n\s+out: .*?\(\$([\d.]+)", trace, re.S)
        stamps = re.findall(r"\] (?:suggest_outfit|create_fit_card)\n(?:.*\n)*?\s+out: \[(lst_\d+) · \$([\d.]+)\]", trace)
        n3 += bool(sel_m) and len(stamps) == 2 and len({s for s in stamps}) == 1 and stamps[0][1] == sel_m.group(1)
    c[3] = n3
    # 4. fit card 2–4 sentences, names price and platform (target 4/5)
    c[4] = sum(2 <= _sentences(card) <= 4 and bool(re.search(r"\$\d", card))
               and bool(re.search(r"poshmark|depop|thredup", card, re.I)) for card in cards)
    # 5. every listing search returned is at or under the price cap (target 5/5)
    n5 = 0
    for trace, _ in match_tries:
        p = re.search(r"\[\d+\] parse_query\n.*\n\s+out: (\{.*\})", trace)
        if not p:
            continue
        parsed = json.loads(p.group(1).replace("'", '"').replace("None", "null"))
        cap = parsed["max_price"]
        results = search_listings(parsed["description"], parsed["size"], cap)
        n5 += bool(results) and cap is not None and all(l["price"] <= cap for l in results)
    c[5] = n5

    targets = {1: 4, 2: 5, 3: 5, 4: 4, 5: 5}
    all_met = all(c[k] >= targets[k] for k in targets) and len(match_tries) == 5
    ids_ok = sum(i == "lst_021" for i in sel[_SCEN[0]]) + sum(i == "lst_004" for i in sel[_SCEN[2]])
    met_count = sum(c[k] >= targets[k] for k in targets)
    cell = f"{met_count}/5 MET; ids {ids_ok}/10"
    detail = {"criteria": c, "selected": sel, "ids_matching_unit4": ids_ok}
    return cell, all_met and ids_ok == 10, detail


# ── main ─────────────────────────────────────────────────────────────────────

ROWS = [
    ("C1. Embedding hit@3 ≥ 12/15, beats keyword on plurals/synonyms, ties on exact", "≥ 12 of 15"),
    ("C2. Recorded strategy matches whether keyword search was empty", "10 of 10"),
    ("C3. Unseen off-topic queries: 0 listings and 0 model calls", "5 of 5"),
    ("C4. Plural/synonym queries typed into the agent select a labelled listing", "≥ 8 of 10"),
    ("C5. Original criteria 1–5 all MET, and `lst_021`/`lst_004` selected 10/10", "5/5 MET; ids 10/10"),
]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=int, default=3)
    ap.add_argument("--out", default="capstone_runs",
                    help="folder under results/ for this set of runs")
    ap.add_argument("--label", default="",
                    help="what changed before this set of runs, for the RUN_LOG heading")
    args = ap.parse_args()
    global OUT
    OUT = config.RESULTS_DIR / args.out
    OUT.mkdir(parents=True, exist_ok=True)

    cells: list[list[tuple[str, bool]]] = [[] for _ in ROWS]
    details = {}
    for k in range(1, args.runs + 1):
        d = OUT / f"run{k}"
        d.mkdir(exist_ok=True)
        started = dt.datetime.now()
        print(f"run {k}: C1…", flush=True)
        t1 = run([PY, "eval_retrieval.py"], d / "c1_stdout.txt")
        move_written(t1, d)
        print(f"run {k}: C2–C4…", flush=True)
        t234 = run([PY, "eval_capstone.py"], d / "c2_c3_c4_stdout.txt")
        move_written(t234, d)
        print(f"run {k}: C5…", flush=True)
        t5 = run([PY, "run_eval.py", "--label", f"{args.out}_run{k}"], d / "c5_stdout.txt")
        md5 = move_written(t5, d)
        md_text = (d / md5[0]).read_text(encoding="utf-8") if md5 else ""

        c1 = score_c1(t1)
        c2, c3, c4 = score_c234(t234)
        c5_cell, c5_ok, c5_detail = score_c5(t5, md_text)
        for i, cell in enumerate([c1, c2, c3, c4, (c5_cell, c5_ok)]):
            cells[i].append(cell)
        details[f"run{k}"] = {"started": started.isoformat(timespec="seconds"),
                              "finished": dt.datetime.now().isoformat(timespec="seconds"),
                              "c5": c5_detail}
        print(f"run {k}: {[c[0] for c in (c1, c2, c3, c4)]} C5 {c5_cell}", flush=True)

    header = "| Criterion | Target | " + " | ".join(f"Run {k}" for k in range(1, args.runs + 1)) + " | Verdict |"
    sep = "|---|---|" + "---|" * args.runs + "---|"
    lines = [header, sep]
    for (name, target), row in zip(ROWS, cells):
        met_runs = sum(ok for _, ok in row)
        verdict = "MET" if met_runs == len(row) else "MISSED"
        lines.append(f"| {name} | {target} | " + " | ".join(c for c, _ in row) +
                     f" | {verdict} ({met_runs} of {len(row)} runs) |")

    doc = [
        f"# Capstone run log — {dt.datetime.now():%Y-%m-%d %H:%M}",
        "",
        *([f"After: {args.label}", ""] if args.label else []),
        f"{args.runs} separate runs of every capstone criterion, cache off. Produced by "
        "`capstone_runlog.py`. A criterion is MET only if every run met its target.",
        "",
        *lines,
        "",
        "C5 cell: how many of the 5 original criteria met their targets, and how many of "
        "the 10 tries selected the unit 4 listing (`lst_021` for the criterion 1 query, "
        "`lst_004` for the empty-wardrobe query).",
        "",
        "Raw output for each run is in `runN/`: each script's full stdout, plus the result "
        "files it wrote.",
        "",
        "## C5 detail",
        "",
        "```json",
        json.dumps(details, indent=2),
        "```",
    ]
    (OUT / "RUN_LOG.md").write_text("\n".join(doc) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print(f"Wrote {(OUT / 'RUN_LOG.md').relative_to(config.ROOT)}")


if __name__ == "__main__":
    main()
