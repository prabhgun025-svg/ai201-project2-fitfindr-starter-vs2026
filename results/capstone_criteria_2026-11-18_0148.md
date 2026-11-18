# Capstone criteria C2–C4 — run 2026-11-18 01:45

Cache off. Model `gemini-3.5-flash-lite`, embedding `gemini-embedding-001`, floor 0.6. Produced by `eval_capstone.py`; every run below also has a record in `logs/runs.jsonl` (source "eval").

## C2. Strategy matches whether keyword search was empty — target 10/10

Candidates with keyword results: 6; with keyword `[]`: 12. First 5 of each used.

| Query | Parsed | Keyword top 3 | Keyword empty? | Strategy | semantic step in trace? | Result |
|---|---|---|---|---|---|---|
| chelsea boots | `{"description": "cheea boot", "size": "L", "max_price": null}` | lst_006 | no | keyword | no | PASS |
| denim jacket under $50 | `{"description": "deni jacket", "size": "M", "max_price": 50.0}` | lst_004, lst_032, lst_038 | no | keyword | no | PASS |
| graphic tee | `{"description": "graphic tee", "size": null, "max_price": null}` | lst_006, lst_002, lst_033 | no | keyword | no | PASS |
| leather belt | `{"description": "eather bet", "size": "L", "max_price": null}` | lst_014 | no | keyword | no | PASS |
| slip dress | `{"description": "ip dre", "size": "S", "max_price": null}` | lst_014, lst_008 | no | keyword | no | PASS |
| cargo pants | `{"description": "cargo pant", "size": "S", "max_price": null}` | (empty) | yes | embedding | yes | PASS |
| hoodies | `{"description": "hoodie", "size": "S", "max_price": null}` | (empty) | yes | embedding | yes | PASS |
| dresses | `{"description": "dree", "size": "SS", "max_price": null}` | (empty) | yes | embedding | yes | PASS |
| blazers | `{"description": "bazer", "size": "L", "max_price": null}` | (empty) | yes | embedding | yes | PASS |
| belts | `{"description": "bet", "size": "L", "max_price": null}` | (empty) | yes | embedding | yes | PASS |

**10/10 — MET**

## C3. Unseen off-topic queries: 0 listings and 0 model calls — target 5/5

| Query | `semantic_search_listings` direct | Agent: parsed | Agent: keyword top 3 | Strategy | Selected | Model calls | Result |
|---|---|---|---|---|---|---|---|
| airline ticket refund | 0 listings | `{"description": "airine ticket refund", "size": "L", "max_price": null}` | (empty) | embedding | — | 0 | PASS |
| how to change a car tire | 0 listings | `{"description": "how to change a car tire", "size": null, "max_price": null}` | lst_008, lst_001, lst_006 | keyword | lst_008 Knit Cardigan — Chunky Brown | 2 | FAIL |
| python list comprehension | 0 listings | `{"description": "python it coprehenion", "size": "L", "max_price": null}` | lst_006, lst_010, lst_015 | keyword | lst_006 Graphic Tee — 2003 Tour Bootleg Style | 2 | FAIL |
| pizza delivery near me | 0 listings | `{"description": "pizza deivery near e", "size": "L", "max_price": null}` | lst_001, lst_003, lst_006 | keyword | lst_001 Vintage Levi's 501 Jeans — Medium Wash | 2 | FAIL |
| mortgage interest rates | 0 listings | `{"description": "ortgage interet rate", "size": "M", "max_price": null}` | (empty) | embedding | — | 0 | PASS |

**2/5 — MISSED**

## C4. Plural/synonym queries typed into the agent select a labelled listing — target ≥ 8/10

| Group | Query | Labelled ids | Parsed | Strategy | Selected | Result |
|---|---|---|---|---|---|---|
| plural | tees | lst_006, lst_002, lst_033 | `{"description": "tee", "size": "S", "max_price": null}` | keyword | lst_002 Y2K Baby Tee — Butterfly Print | PASS |
| plural | hoodies | lst_015 | `{"description": "hoodie", "size": "S", "max_price": null}` | embedding | lst_012 Oversized Crewneck Sweatshirt — Vintage Navy | FAIL |
| plural | dresses | lst_013 | `{"description": "dree", "size": "SS", "max_price": null}` | embedding | — (no_results) | FAIL |
| plural | blazers | lst_018, lst_036 | `{"description": "bazer", "size": "L", "max_price": null}` | embedding | lst_032 Shacket — Olive Canvas | FAIL |
| plural | belts | lst_014 | `{"description": "bet", "size": "L", "max_price": null}` | embedding | lst_040 Tie-Dye Long Sleeve — Pastel | FAIL |
| synonym | denim pants | lst_001, lst_031, lst_037 | `{"description": "deni pant", "size": "M", "max_price": null}` | keyword | lst_038 Denim Vest — Medium Wash, Studded | FAIL |
| synonym | sweater | lst_008, lst_030, lst_012, lst_027 | `{"description": "weater", "size": "S", "max_price": null}` | embedding | lst_008 Knit Cardigan — Chunky Brown | PASS |
| synonym | purse | lst_039 | `{"description": "pure", "size": "S", "max_price": null}` | embedding | lst_035 Low-Top Canvas Sneakers — Off-White | FAIL |
| synonym | trainers | lst_019, lst_035 | `{"description": "trainer", "size": "S", "max_price": null}` | embedding | lst_019 Platform Sneakers — White Chunky Sole | PASS |
| synonym | headwear | lst_034 | `{"description": "headwear", "size": null, "max_price": null}` | embedding | lst_034 Bucket Hat — Reversible, Brown Plaid | PASS |

**4/10 — MISSED**

