# Acceptance criteria — FitFindr

Five criteria that say what "working" means for this agent, written in unit 3
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"The agent handles errors"* is an opinion.
*"When search returns nothing, the agent stops before calling the second tool,
in 5 of 5 tries"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter one. A reason that says something about your tools, your loop, or the
data earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

**Two are written for you. You write three.**

---

## 1. A matching query completes all three tools (MET)

Given a query that matches at least one listing, the agent completes all three
tool calls and returns a fit card — in at least 4 of 5 tries.

**Why this target:**
The search is based on plain keyboard and this means the matching sets are are imperfect so some valid phrases will miss. A strict 5/5 target would be harder to guarantee

---

## 2. An impossible query stops before the second tool (MET)

Given a query that matches no listings, the agent stops before calling
`suggest_outfit` and returns a message naming what to change — in 5 of 5 tries.

**Why this target:**
the criteria is direct and has a yes or no system. If the query stops before the second tool, it works but if it does not, it isn't working hence the 5/5 target 

---

## 3. The selected item must survive the whole loop (MISSED)

After `search_listings` returns a result and the loop stores it in `session["selected_item"]`, that same item's `id` and price appear in the session and in the output of both `suggest_outfit` and `create_fit_card` — in 5 of 5 tries.

**Why this target:**
The loop can call all three tools and still be wrong if it switches items between steps. Either the item IDs match or they don't so 5 of 5 is the right target. If state is broken, no other criterion can pass

**Why it missed**
It missed in a tool, specifically the prompts that suggest_outfit and create_fit_card build. The criterion missed all five tries and every try failed the same way. All tries held the item throughout the loop but not the ID or the price. Those two got missed within the loop. 

---

## 4. Fit-card fallback and content requirement are both enforced (MET)

`create_fit_card` returns a 2-4 sentence caption that mentions the price of the item and platform - 4 out of 5 tries 



**Why this target:**

wording varies between runs and the acceptance criteria is whether the output is caption-shaped and includes the required details not whether it is word for word identical 
---

## 5. Search enforces the Price Cap (MET)

Given a search with a price ceiling like "under $30", every listing returned by `search_listings` has a price at or below the requested maximum in 5 of 5 tries.

**Why this target:**
Either the prices are below the cap or they aren't. If the search ignores the budget, the result is broken, not close. So 5 of 5 is the right setting



---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 4 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 4. Something about the fit card

         The fit card is different every time.

         **Why this target:** ...

         > **Revised in unit 4:** For 5 different items, the 5 fit cards share
         > no opening sentence.
         >
         > **Why revised:** "different" wasn't checkable — two cards that
         > differed by one word still counted. The new version is something I
         > can actually score.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said the empty search stops it 5 of 5 times, but I got 3 of 5,
            so 3 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->

---

# Capstone criteria: the embedding-search fallback

Five criteria for the capstone. C1–C4 are about the new capability: embedding
search as a fallback when keyword search returns nothing. C5 checks that the
original five criteria still meet their targets with the extension in place.
Numbered C1–C5 so they can't be confused with criteria 1–5 above.

Labelled queries live in `retrieval_queries.py`: 5 plurals, 5 synonyms and
5 exact-wording queries, each with the listing ids that count as a hit. The
labels were written before embedding search had been run on any of them.

---

## C1. Embedding hit@3 is at least 12 of 15, beats keyword on plurals and synonyms, and ties or beats it on exact wording (MET)
On the 15 labelled queries, `semantic_search_listings` puts at least one
labelled listing id in its top 3 results on **at least 12 of 15** queries.
On the 10 plural and synonym queries, its hit count is **higher than keyword
search's**. On the 5 exact-wording queries, its hit count is **equal to or
higher than keyword search's**.

**How it's scored:** `python eval_retrieval.py` prints a HIT or miss for each
query and strategy, and a count per group. It runs with no size or price
filter, so the query parser isn't involved.

**Why this target:**
The 12/15 target was set in the README's Capstone section before the eval
ran.

- **Why not stricter (15/15):** three synonym labels depend on knowledge
  that isn't in any listing's text. "Headwear" has to mean a bucket hat,
  "trainers" a sneaker, and "purse" a shoulder bag. `gemini-embedding-001` is
  a general-purpose model that I don't control, so a miss there is a gap in
  its vocabulary, not a bug in my code. With only 15 queries, a 15/15 target
  would let one debatable label decide the whole verdict.
- **Why not looser (10/15):** keyword search already gets the 5 exact-wording
  queries. An embedding score of 10 could mean those same 5 plus only half of
  the 10 queries the fallback exists for. Below 12 means at least 4 misses
  among those 10. In the agent, each miss costs 2 model calls spent styling
  the wrong listing.
- **Why "ties or beats" on exact wording, not "beats":** keyword search
  already scores 5/5 there, so beating it isn't possible. The agent never
  shows embedding results for those queries, because keyword search isn't
  empty. The tie still matters: if embeddings lose queries where the right
  answer contains the query's own words, their ranking on plurals and
  synonyms can't be trusted either.

**Result (3 runs, 18 Nov 2026):** 15/15, 15/15, 15/15 (keyword search 5/15 each run). Plurals and synonyms: embedding 10/10 vs keyword 0/10. Exact wording: 5/5 vs 5/5. Held in all 3 runs, so **MET**.

---

## C2. On 10 of 10 queries, the strategy recorded matches whether keyword search was empty (MET)
For 10 queries sent through `run_agent`, 5 where keyword search returns
results and 5 where it returns `[]`:

- when keyword search returned results: `session["search_strategy"]` is
  `"keyword"`, and the trace has **no** `semantic_search_listings` step
- when keyword search returned `[]`: `session["search_strategy"]` is
  `"embedding"`, and the trace **has** a `semantic_search_listings` step

Target: **10 of 10**.

**How it's scored:** for each run, read the `search_listings` step's `out:`
line in the trace, then check the strategy field and whether the
`semantic_search_listings` step is there.

**Why this target:**
- **Why not looser (9/10):** the branch is one `if not search_results` on
  keyword search's output, and keyword search returns the same list for the
  same input every time. Nothing random sits between the two, so a single
  wrong run is a bug, not variation.

  Being wrong costs something real in both directions. If the fallback fires
  when keyword search found results, it replaces those results, so C5's
  comparison with unit 4 breaks and an embedding request is wasted. If it
  fails to fire when keyword search is empty, a query like "tees" gets "no
  items found", which is the exact failure the capstone was built to fix.
- **Why not stricter (more than 10 queries):** 10 of 10 is already every run.
  The 5 + 5 split runs each side of the branch five times. More queries would
  cost 2 model calls each and exercise the same `if` again, not a new
  path.

**Result (3 runs, 18 Nov 2026):** 10/10, 10/10, 10/10. Held in all 3 runs, so **MET**.

---

## C3. All 5 unseen off-topic queries return 0 listings and make 0 model calls (MISSED → MET after the keyword-search fix)
For these 5 off-topic queries, none of which were used to choose the 0.60
similarity floor in `config.EMBEDDING_MIN_SIMILARITY`:

- `airline ticket refund`
- `how to change a car tire`
- `python list comprehension`
- `pizza delivery near me`
- `mortgage interest rates`

two things hold on **5 of 5**:

1. `semantic_search_listings(query)` returns `[]` (0 listings).
2. Sent through the agent, the run ends with `selected_item` set to `None`,
   `fit_card` set to `None`, and `model_calls` equal to 0 in its log record.

**How it's scored:** call the search function directly and count the
results, then read `status`, `output.selected_item` and `model_calls` from
each run's record in `logs/runs.jsonl`.

**Why this target:**
The floor was calibrated on different off-topic queries ("spaceship engine
parts", "tax return form"), which topped out at 0.575 similarity. Scoring it
on those same queries would only confirm the calibration, so these five are
new.

- **Why not looser (4/5):** this runs on a public site where every search
  spends the same API key. Each off-topic query that gets through costs 2
  generation requests (about 1,000 tokens, and 2 of the 15 allowed per
  minute) and shows the visitor a styled listing unrelated to what they
  typed. 4/5 would accept that happening on 1 in 5 off-topic searches.
- **Why not stricter:** 5/5 is already all of them. What makes this hard to
  pass is the floor's thin margin: 0.60 is only 0.025 above the highest
  off-topic score seen during calibration. Five unseen queries are enough to
  show whether new off-topic text lands above that line.
- **A second way to fail:** the agent half depends on keyword search
  returning `[]` first. Its matching counts a query word found anywhere
  inside a description, so a short word like "a" or "to" can match almost
  any listing. If that happens, the fallback never runs and the floor is
  never consulted. That would be a C3 miss caused by keyword search, not by
  the floor.

**Result (3 runs, 18 Nov 2026):** 3/5, 3/5, 3/5. The target is 5 of 5, so **MISSED** in every run.

**Why it missed:**
**Stage: keyword search, `tools.py::search_listings`. The fallback and the
floor never got to run.** The same two queries failed in all three runs:
`how to change a car tire` and `pizza delivery near me`. When
`semantic_search_listings` was called directly, it returned 0 listings for all
5 queries in all 3 runs, so the 0.60 floor works.

The mechanism is the description check: `elif keyword in desc_text` is a
substring test against the whole description string, while the title check
splits the title into words first. So a query word counts as matching if it
appears *inside* any word of a description:

- "me" matches 17 listings, through words like "medium" and "some", even
  though no description contains "me" as a word.
- "car" matches inside "cardigan", which is why a knit cardigan came first.
- "a" matches all 40 listings.

Keyword search returns 10 results, so the agent's empty-result branch is never
taken, and it spends 2 model calls styling an unrelated listing.

My criterion assumed that an off-topic query reaches the fallback, meaning
keyword search returns `[]` for words that aren't in the catalogue. That's
false for any query containing a short or common word.

Whole-word matching alone would fix `pizza delivery near me`: none of its four
words appears as a whole word in any listing. It would not fix the car-tire
query, because "a" is a real word in 18 descriptions and "to" in 5. That one
also needs filler words like "a" and "to" ignored.

**After the improvement (3 runs, 18 Nov 2026, 02:54–03:08):** 5/5, 5/5, 5/5,
so **MET**. One change, in `tools.py::search_listings`: matching is whole-word,
and filler words are dropped from the query. Both failing queries now get
`[]` from keyword search, reach the fallback, and stop with 0 model calls in
every run. Raw output: `results/capstone_runs_after_fix/`.

---

## C4. At least 8 of 10 plural or synonym queries typed into the agent select a labelled listing (MET)
For the 10 plural and synonym queries in `retrieval_queries.py`, each typed
as-is into the agent, the `selected_item` id in the run's log record is one
of that query's labelled ids on **at least 8 of 10**.

**How it's scored:** compare `output.selected_item.id` in each log record
with the `relevant` list for that query in `retrieval_queries.py`.

**Why this target:**
C1 scores the search function with clean input. C4 scores what a user gets,
which goes through the regex query parser first.

- **Why not stricter (10/10):** with clean input, all 10 of these queries
  already put a labelled listing first (C1's eval output), so the parser is
  the only thing between this criterion and 10 of 10. The parser is a known,
  documented bug (`purse` is searched as size S; see README → Failure
  Modes), and fixing it is outside the capstone's scope. At 10/10, C4 would
  be a test of the parser, not of the extension.
- **Why not looser (6/10):** these 10 queries are exactly the ones the
  extension was built for. Below 8 means a user typing a plural or a synonym
  gets the wrong listing more than 1 time in 5. Each wrong run still costs 2
  model calls and produces a confident fit card for the wrong item, with
  nothing on screen to show it's wrong. 8 allows the parser to garble 2
  queries and no more.

**Result (3 runs, 18 Nov 2026):** 9/10, 9/10, 9/10. The target is at least 8 of 10, so **MET**. (Before the parser fix it was 4/10. The one remaining miss, `denim pants`, is the "keyword search is wrong but not empty" case left out of scope: five listings tie at the top of keyword search's ranking with one title-word match each, and corduroy pants, `lst_005`, wins the tie only because it comes first in the catalogue. The actual jeans rank lower, because "denim" is only in their style tags.)

---

## C5. All 5 original criteria are MET, and the same 2 listings are selected in 5 of 5 tries (MISSED)
With the extension in place, `python run_eval.py` (cache off, 5 tries per
scenario) gives:

- a **MET** verdict on all 5 of criteria 1–5 above, scored against their
  original targets
- `selected_item` id `lst_021` for the criterion 1 scenario and `lst_004` for
  the empty-wardrobe scenario, in **5 of 5** tries each. These are the
  listings selected in the unit 4 "after" run.

**How it's scored:** fill in the run log table the same way as in unit 4,
and read the selected ids from the trace's `suggest_outfit` lines.

**Why this target:**
- **Why not looser (MET verdicts only):** criterion 1 only asks that all
  three tools run, so it passes whichever listing is selected. If the
  fallback fired on the criterion 1 query, all five verdicts could stay MET
  while a different item is styled. The listing ids are what would catch
  that.
- **Why not stricter (identical outputs):** `suggest_outfit` and
  `create_fit_card` run at temperature 0.9, so their text differs every try
  by design and can't be compared. The selected listing comes from parsing
  and keyword search, which have no randomness, so the id is the part that
  should never change.
- **Why 5 of 5 for the ids, not 4 of 5:** for the same deterministic reason,
  one different id in five tries means the code path changed, not that the
  model varied.

**Result (3 runs, 18 Nov 2026):** all 5 original criteria MET in every run (5/5, 5/5, 5/5). Listing ids: 0/10, 0/10, 0/10. The target needs both, so **MISSED** in every run.

**Why it missed:**
**Stage: the query parser, `agent.py::parse_query`. The fallback isn't
involved.** In every try of both scenarios, the trace shows
`search_listings` returning results ("branch: results, continuing") and no
`semantic_search_listings` step. The listing that changed was chosen by
keyword search, with no fallback step in between.

The mechanism: the parser fix changed what keyword search is given.

- **Criterion 1 query** (`vintage graphic tee under $30`): the old parser
  also read the price as size "30". The size filter's substring test let only
  "W30" listings through, and with the $30 cap that left exactly one result,
  `lst_021`, the olive trousers. The new parser sends size `None`, so search
  returns 10 listings and the first is `lst_006`, a graphic tee.
- **Empty-wardrobe query** (`denim jacket under $50`): the old parser turned
  this into "deni jacket" with size M, which ranked the track jacket
  (`lst_004`) first. The new parser sends "denim jacket" with no size, and the
  first result is `lst_007`, the denim jacket.

The id check was written to catch the fallback firing when it shouldn't. It
assumed the only thing that could change the selected listing was the
fallback. But `lst_021` and `lst_004` were themselves products of the parser
bug, so fixing the parser changed them. The target stays as written, and this
counts as a miss.
