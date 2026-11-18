# Capstone run log — 2026-11-18 03:08

After: keyword search matches whole words and ignores filler words (tools.py::search_listings)

3 separate runs of every capstone criterion, cache off. Produced by `capstone_runlog.py`. A criterion is MET only if every run met its target.

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| C1. Embedding hit@3 ≥ 12/15, beats keyword on plurals/synonyms, ties on exact | ≥ 12 of 15 | 15/15 (keyword 5/15) | 15/15 (keyword 5/15) | 15/15 (keyword 5/15) | MET (3 of 3 runs) |
| C2. Recorded strategy matches whether keyword search was empty | 10 of 10 | 10/10 | 10/10 | 10/10 | MET (3 of 3 runs) |
| C3. Unseen off-topic queries: 0 listings and 0 model calls | 5 of 5 | 5/5 | 5/5 | 5/5 | MET (3 of 3 runs) |
| C4. Plural/synonym queries typed into the agent select a labelled listing | ≥ 8 of 10 | 9/10 | 9/10 | 9/10 | MET (3 of 3 runs) |
| C5. Original criteria 1–5 all MET, and `lst_021`/`lst_004` selected 10/10 | 5/5 MET; ids 10/10 | 5/5 MET; ids 0/10 | 5/5 MET; ids 0/10 | 5/5 MET; ids 0/10 | MISSED (0 of 3 runs) |

C5 cell: how many of the 5 original criteria met their targets, and how many of the 10 tries selected the unit 4 listing (`lst_021` for the criterion 1 query, `lst_004` for the empty-wardrobe query).

Raw output for each run is in `runN/`: each script's full stdout, plus the result files it wrote.

## C5 detail

```json
{
  "run1": {
    "started": "2026-11-18T02:54:53",
    "finished": "2026-11-18T03:00:01",
    "c5": {
      "criteria": {
        "1": 5,
        "2": 5,
        "3": 5,
        "4": 5,
        "5": 5
      },
      "selected": {
        "matching query completes": [
          "lst_006",
          "lst_006",
          "lst_006",
          "lst_006",
          "lst_006"
        ],
        "impossible query stops early": [
          "(none)",
          "(none)",
          "(none)",
          "(none)",
          "(none)"
        ],
        "empty wardrobe": [
          "lst_007",
          "lst_007",
          "lst_007",
          "lst_007",
          "lst_007"
        ]
      },
      "ids_matching_unit4": 0
    }
  },
  "run2": {
    "started": "2026-11-18T03:00:01",
    "finished": "2026-11-18T03:04:23",
    "c5": {
      "criteria": {
        "1": 5,
        "2": 5,
        "3": 5,
        "4": 5,
        "5": 5
      },
      "selected": {
        "matching query completes": [
          "lst_006",
          "lst_006",
          "lst_006",
          "lst_006",
          "lst_006"
        ],
        "impossible query stops early": [
          "(none)",
          "(none)",
          "(none)",
          "(none)",
          "(none)"
        ],
        "empty wardrobe": [
          "lst_007",
          "lst_007",
          "lst_007",
          "lst_007",
          "lst_007"
        ]
      },
      "ids_matching_unit4": 0
    }
  },
  "run3": {
    "started": "2026-11-18T03:04:23",
    "finished": "2026-11-18T03:08:53",
    "c5": {
      "criteria": {
        "1": 5,
        "2": 5,
        "3": 5,
        "4": 5,
        "5": 5
      },
      "selected": {
        "matching query completes": [
          "lst_006",
          "lst_006",
          "lst_006",
          "lst_006",
          "lst_006"
        ],
        "impossible query stops early": [
          "(none)",
          "(none)",
          "(none)",
          "(none)",
          "(none)"
        ],
        "empty wardrobe": [
          "lst_007",
          "lst_007",
          "lst_007",
          "lst_007",
          "lst_007"
        ]
      },
      "ids_matching_unit4": 0
    }
  }
}
```
