# Capstone criteria C2–C4 — run 2026-11-18 03:00

Cache off. Model `gemini-3.5-flash-lite`, embedding `gemini-embedding-001`, floor 0.6. Produced by `eval_capstone.py`; every run below also has a record in `logs/runs.jsonl` (source "eval").

## C2. Strategy matches whether keyword search was empty — target 10/10

Candidates with keyword results: 6; with keyword `[]`: 12. First 5 of each used.

| Query | Parsed | Keyword top 3 | Keyword empty? | Strategy | semantic step in trace? | Result |
|---|---|---|---|---|---|---|
| chelsea boots | `{"description": "chelsea boots", "size": null, "max_price": null}` | lst_028 | no | keyword | no | PASS |
| denim jacket under $50 | `{"description": "denim jacket", "size": null, "max_price": 50.0}` | lst_007, lst_004, lst_016 | no | keyword | no | PASS |
| cargo pants | `{"description": "cargo pants", "size": null, "max_price": null}` | lst_011, lst_005 | no | keyword | no | PASS |
| graphic tee | `{"description": "graphic tee", "size": null, "max_price": null}` | lst_006, lst_002, lst_033 | no | keyword | no | PASS |
| leather belt | `{"description": "leather belt", "size": null, "max_price": null}` | lst_014, lst_022, lst_039 | no | keyword | no | PASS |
| tees | `{"description": "tees", "size": null, "max_price": null}` | (empty) | yes | embedding | yes | PASS |
| hoodies | `{"description": "hoodies", "size": null, "max_price": null}` | (empty) | yes | embedding | yes | PASS |
| dresses | `{"description": "dresses", "size": null, "max_price": null}` | (empty) | yes | embedding | yes | PASS |
| blazers | `{"description": "blazers", "size": null, "max_price": null}` | (empty) | yes | embedding | yes | PASS |
| belts | `{"description": "belts", "size": null, "max_price": null}` | (empty) | yes | embedding | yes | PASS |

**10/10 — MET**

## C3. Unseen off-topic queries: 0 listings and 0 model calls — target 5/5

| Query | `semantic_search_listings` direct | Agent: parsed | Agent: keyword top 3 | Strategy | Selected | Model calls | Result |
|---|---|---|---|---|---|---|---|
| airline ticket refund | 0 listings | `{"description": "airline ticket refund", "size": null, "max_price": null}` | (empty) | embedding | — | 0 | PASS |
| how to change a car tire | 0 listings | `{"description": "how to change a car tire", "size": null, "max_price": null}` | (empty) | embedding | — | 0 | PASS |
| python list comprehension | 0 listings | `{"description": "python list comprehension", "size": null, "max_price": null}` | (empty) | embedding | — | 0 | PASS |
| pizza delivery near me | 0 listings | `{"description": "pizza delivery near me", "size": null, "max_price": null}` | (empty) | embedding | — | 0 | PASS |
| mortgage interest rates | 0 listings | `{"description": "mortgage interest rates", "size": null, "max_price": null}` | (empty) | embedding | — | 0 | PASS |

**5/5 — MET**

## C4. Plural/synonym queries typed into the agent select a labelled listing — target ≥ 8/10

| Group | Query | Labelled ids | Parsed | Strategy | Selected | Result |
|---|---|---|---|---|---|---|
| plural | tees | lst_006, lst_002, lst_033 | `{"description": "tees", "size": null, "max_price": null}` | embedding | lst_033 Vintage Band Tee — Faded Grey | PASS |
| plural | hoodies | lst_015 | `{"description": "hoodies", "size": null, "max_price": null}` | embedding | lst_015 Vintage Graphic Hoodie — Faded Black | PASS |
| plural | dresses | lst_013 | `{"description": "dresses", "size": null, "max_price": null}` | embedding | lst_013 90s Silk Slip Dress — Floral, Midi Length | PASS |
| plural | blazers | lst_018, lst_036 | `{"description": "blazers", "size": null, "max_price": null}` | embedding | lst_018 Vintage Linen Blazer — Cream | PASS |
| plural | belts | lst_014 | `{"description": "belts", "size": null, "max_price": null}` | embedding | lst_014 Leather Belt — Brown, Braided | PASS |
| synonym | denim pants | lst_001, lst_031, lst_037 | `{"description": "denim pants", "size": null, "max_price": null}` | keyword | lst_005 Corduroy Wide-Leg Pants — Rust | FAIL |
| synonym | sweater | lst_008, lst_030, lst_012, lst_027 | `{"description": "sweater", "size": null, "max_price": null}` | embedding | lst_008 Knit Cardigan — Chunky Brown | PASS |
| synonym | purse | lst_039 | `{"description": "purse", "size": null, "max_price": null}` | embedding | lst_039 Mini Shoulder Bag — Tan Leather | PASS |
| synonym | trainers | lst_019, lst_035 | `{"description": "trainers", "size": null, "max_price": null}` | embedding | lst_019 Platform Sneakers — White Chunky Sole | PASS |
| synonym | headwear | lst_034 | `{"description": "headwear", "size": null, "max_price": null}` | embedding | lst_034 Bucket Hat — Reversible, Brown Plaid | PASS |

**9/10 — MET**

