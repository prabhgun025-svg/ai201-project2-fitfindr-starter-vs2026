"""
Labelled queries for the capstone retrieval comparison.

Each query lists the listing ids that count as a correct answer. A strategy
"hits" a query when at least one of those ids is in its top 3 (hit@3).

These labels were written by reading data/listings.json, BEFORE embedding
search was run on any of them, so the embedding results couldn't shape them.

Three groups of five:
  plural   — the singular form exists in the data, the plural doesn't
  synonym  — the item exists under a different word
  exact    — wording that already appears in the data; keyword search
             should get these, and embeddings must not do worse
"""

QUERIES = [
    # ── plurals ──────────────────────────────────────────────────────────────
    {"group": "plural", "query": "tees",      "relevant": ["lst_006", "lst_002", "lst_033"]},
    {"group": "plural", "query": "hoodies",   "relevant": ["lst_015"]},
    {"group": "plural", "query": "dresses",   "relevant": ["lst_013"]},
    {"group": "plural", "query": "blazers",   "relevant": ["lst_018", "lst_036"]},
    {"group": "plural", "query": "belts",     "relevant": ["lst_014"]},

    # ── synonyms ─────────────────────────────────────────────────────────────
    {"group": "synonym", "query": "denim pants", "relevant": ["lst_001", "lst_031", "lst_037"]},
    {"group": "synonym", "query": "sweater",     "relevant": ["lst_008", "lst_030", "lst_012", "lst_027"]},
    {"group": "synonym", "query": "purse",       "relevant": ["lst_039"]},
    {"group": "synonym", "query": "trainers",    "relevant": ["lst_019", "lst_035"]},
    {"group": "synonym", "query": "headwear",    "relevant": ["lst_034"]},

    # ── exact wording keyword search already handles ─────────────────────────
    {"group": "exact", "query": "graphic tee",   "relevant": ["lst_006", "lst_002", "lst_033"]},
    {"group": "exact", "query": "denim jacket",  "relevant": ["lst_007"]},
    {"group": "exact", "query": "chelsea boots", "relevant": ["lst_028"]},
    {"group": "exact", "query": "slip dress",    "relevant": ["lst_013"]},
    {"group": "exact", "query": "cargo pants",   "relevant": ["lst_011"]},
]
