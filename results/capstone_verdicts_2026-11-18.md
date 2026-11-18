# Capstone criteria: verdicts, 2026-11-18

Scored against the targets in `criteria.md` → Capstone criteria. All runs had
the cache off.

| # | Criterion | Target | Result | Verdict |
|---|---|---|---|---|
| C1 | Embedding hit@3 vs keyword on 15 labelled queries | ≥ 12/15; beats keyword on plurals and synonyms; ties or beats on exact | 15/15 (keyword 5/15). Plurals and synonyms 10/10 vs 0/10; exact 5/5 vs 5/5 | **MET** |
| C2 | Recorded strategy matches whether keyword search was empty | 10/10 | 10/10 | **MET** |
| C3 | Unseen off-topic queries: 0 listings and 0 model calls | 5/5 | 2/5. The floor alone returned 0 listings on 5/5, but the agent styled an item on 3 | **MISSED (2/5)** |
| C4 | Plural/synonym queries typed into the agent select a labelled listing | ≥ 8/10 | 4/10 | **MISSED (4/10)** |
| C5 | Original criteria 1–5 all MET; same ids as unit 4 in 5/5 tries | All MET; `lst_021` and `lst_004` 5/5 | All 5 MET; ids matched 10/10 | **MET** |

Raw output:

- C1: `results/retrieval_*.md` (latest run)
- C2–C4: `results/capstone_criteria_2026-11-18_0148.md`
- C5: `results/run_2026-11-18_0150_capstone_c5.md`

## C5: the original criteria, scored

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. A matching query completes all three tools | 4/5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. An impossible query stops before the second tool | 5/5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. The selected item's id and price survive the whole loop | 5/5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. The fit card is 2–4 sentences and names the price and platform | 4/5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 5. Search enforces the price cap | 5/5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

How each was scored:

1. All 5 tries completed with a fit card.
2. All 5 impossible-query tries stopped with the "No items found … Try
   different keywords, a higher price, or removing size filters" message. 0
   of 5 reached `suggest_outfit`.
3. `[lst_021 · $29.0]` (criterion 1 scenario) and `[lst_004 · $45.0]`
   (empty-wardrobe scenario) appear at the start of every `suggest_outfit`
   and `create_fit_card` output: 20 of 20. The selected listing was the same
   as in unit 4 in 10 of 10 tries.
4. Read by hand: every fit card is 2–4 sentences (hashtag lines not counted)
   and names both the price and Poshmark.
5. Every listing that search returned for the criterion 1 query is at or under
   the $30 cap: 1 result, `lst_021` at $29.

## Diagnosis: C3 and C4

**Both misses happen at the same place: the query parser in
`agent.py::run_agent`, before either search runs.** The embedding search
itself passed every time it got clean input. It returned 0 listings for all 5
off-topic queries (C3), and with clean input it put a labelled listing first
for all 10 C4 queries (C1).

The parser's size regex has no word boundaries, and it removes every match
from the description, not just the first one. So any S, M, L or X inside a
word is treated as a size and deleted:

| Typed | Parsed description | Parsed size |
|---|---|---|
| `dresses` | `dree` | `SS` |
| `belts` | `bet` | `L` |
| `blazers` | `bazer` | `L` |
| `purse` | `pure` | `S` |
| `python list comprehension` | `python it coprehenion` | `L` |
| `pizza delivery near me` | `pizza deivery near e` | `L` |

**C4 (4/10):** the 6 misses all trace back to the parser. A garbled
description gets a poor embedding match (`belts` searched as "bet" found a
tie-dye top). The invented size also filters out the right listing: the only
hoodie is size L, so `hoodies` searched with size S can never find it. For
`denim pants`, the garbled "deni pant" still matched something by keyword
search, so the fallback never ran, which is the "wrong but not empty" case
the capstone left out of scope.

**C3 (2/5):** the 3 misses come from keyword search, not the floor. Keyword
search counts a query word found anywhere inside a description as a match.
`how to change a car tire` matched through "a" and "to", and the parser's
leftovers ("it", "e") matched in the other two. Keyword search wasn't empty,
so the fallback and its floor never ran, and the agent spent 2 model calls
styling an unrelated listing.

**What it points to:** fix the parser (word-boundary size matching, and only
remove the matched size), and require keyword search to match whole words.
Both are outside the capstone's stated scope, which promised not to touch
anything but retrieval. The keyword fix also changes keyword search's
results, so criteria 1–5 and C1 would need re-running afterwards.

---

# After the parser fix

**One change:** query parsing moved into `agent.py::parse_query`. Price and
size patterns now match whole words only, and only the matched span is
removed. Nothing else changed: same search, same fallback, same floor, same
prompts. All runs had the cache off.

Raw output:

- C2–C4: `results/capstone_criteria_2026-11-18_0212.md`
- C5: `results/run_2026-11-18_0214_parser_fix.md`

| # | Target | Before fix | After fix | Verdict |
|---|---|---|---|---|
| C1 | ≥ 12/15 | 15/15 | not re-run (no parser in this eval) | **MET** |
| C2 | 10/10 | 10/10 | 10/10 | **MET** |
| C3 | 5/5 | 2/5 | 3/5 | **MISSED (3/5)** |
| C4 | ≥ 8/10 | 4/10 | 9/10 | **MET (9/10)** |
| C5 | all 5 original MET + `lst_021` / `lst_004` in 5/5 | met | all 5 MET; selected `lst_006` / `lst_007` | **MISSED** |

## C5 scored

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. A matching query completes all three tools | 4/5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. An impossible query stops before the second tool | 5/5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. The selected item's id and price survive the whole loop | 5/5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. The fit card is 2–4 sentences and names the price and platform | 4/5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 5. Search enforces the price cap | 5/5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

- **Criterion 3:** `[lst_006 · $24.0]` and `[lst_007 · $42.0]` appear on every
  `suggest_outfit` and `create_fit_card` output, 20 of 20.
- **Criterion 4:** all 10 fit cards are 3–4 sentences and name the price and
  Depop or Poshmark.
- **Criterion 5:** the criterion 1 query now returns 10 listings, all at or
  under $30 (the highest is $30.00).
- **Criterion 2:** the impossible query is now parsed as "designer ballgown",
  size XXS, $5, and it stops before `suggest_outfit` in 5 of 5 tries.

## Diagnoses

**C5 (MISSED on the listing ids):** the selected listings changed from
`lst_021` (olive trousers) to `lst_006` (graphic tee) for the criterion 1
query, and from `lst_004` (track jacket) to `lst_007` (denim jacket) for
the empty-wardrobe query. **The cause is the parser fix, not the fallback.**
Both runs show `search_listings` returning results with the note "branch:
results, continuing", and no `semantic_search_listings` step, so the fallback
never fired. Before the fix, "under $30" also set size 30, which filtered the
search down to a single pair of W30 trousers. "denim jacket" was parsed as
"deni jacket" with size M, which found a track jacket. The listings now
selected are the items the queries actually ask for.

The id clause was written to catch the fallback firing when it shouldn't.
It assumed nothing else would change the selected listing, and the parser
fix broke that assumption. The miss stays recorded as a miss.

**C3 (3/5):** the parser fix rescued `python list comprehension`, which used
to be garbled into fragments that keyword search matched. The 2 remaining
misses are `how to change a car tire` and `pizza delivery near me`. Both are
parsed correctly now, but keyword search still returns results for them,
because it counts a query word found anywhere inside a description as a
match: "a", "to" and "me" occur inside almost every description. The fallback
never runs, so the 0.60 floor is never consulted. Called directly,
`semantic_search_listings` returned 0 listings for all 5. **Remaining cause:
substring matching in `tools.py::search_listings`.**

**C4 (9/10):** the one miss is `denim pants`. Keyword search matches "denim"
in many listings' tags and descriptions and returns the corduroys
(`lst_005`) first, so the fallback never runs. That's the "wrong but not
empty" case the capstone left out of scope. Embedding search alone ranks a
pair of jeans first for this query (C1).
