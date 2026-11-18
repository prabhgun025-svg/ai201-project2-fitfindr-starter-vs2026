# FitFindr

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every
> command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> python app.py listings --full -n 6      # read the data (Milestone 1)
> python app.py fields                    # what you can filter on
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> All three tools are stubs, so that last command will do nothing useful yet.
> That's the starting position.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

> ### ⚠️ Note on this repository
>
> On **18 November 2026** I deleted my original repository by accident:
> `github.com/prabhgun025-svg/ai201-project2-fitfindr-starter-v2026`, a fork of
> the course starter. GitHub doesn't let me restore it from the trash, because
> it was a fork.
>
> **The project itself is unchanged.** It's the same FitFindr project, with the
> same code, criteria, results and README, and it's what I'm continuing to
> work on. I'm re-uploading it to a new repository from my local copy.
>
> **What's different:**
> - The repository URL is now `<new repository URL>`.
> - The new repository is not linked to the course starter as a fork.
> - Anything that pointed to the old URL, such as an earlier submission link,
>   no longer works.
>
> The run logs in `results/` are timestamped records from the actual runs, so
> the dates of the testing are still on record.

---
## Capstone is at the bottom

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     This is your submission. Fill each section in as you finish the milestone
     it belongs to — don't leave it all to the end.

     Unit 3 asks for the first five sections. Unit 4 adds the five below them.
     Leave the unit 4 sections alone until then; they're here so you know
     what's coming.

     Everything is pasted as TEXT. No screenshots, no images, no video links.
     A typed block of output gets full credit; a picture of the same output
     gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 3 — THE BUILD ═══════════════════════ -->

## Stretch Features I am adding to the project 
1. a Fourth Tool which is price comparison 
2. Style Memory in which the agent remembers a wardrobe between runs 


## What This Does

This is a fitfindr application in which the user asks questions such as pricing, or fit models or reccomendations, etc. and the AI will output the answers. It would search the projects listing to match to match the text query and optional fiters for candidates, suggets outfits for the candidates 
---

## Tool Inventory

<!-- Four lines per tool. This is worth 2 points and it's the single most
     common place students lose them.

     "Returns a list" earns NOTHING. The description has to say what is IN
     the list.

     The empty case isn't optional either — it's the thing your loop branches
     on, and if you don't decide it here you'll discover it as a crash in
     Milestone 5. -->

### `search_listings`

- What it does: Searches the project's listings data for items whose title, description, or style tags match the keywords. It can also filter by size and a price ceiling. Results are ranked by keyword overlap, and title matches count most.
- Inputs: `description` (str, required), `size` (str, optional, matched case-insensitively), `max_price` (float, optional, US dollars, inclusive)
- Returns: Up to 10 listing dicts, best match first. Each has keys: `id` (str), `title` (str), `description` (str), `category` (str), `style_tags` (list of str), `size` (str), `condition` (str), `price` (float), `colors` (list of str), `brand` (str or null), and `platform` (str).
- When it has nothing: Returns an empty list (`[]`).

### `suggest_outfit`

- What it does: Generates outfit suggestions by combining one or more listings into cohesive looks based on style rules and optional user/context inputs.
- Inputs: `listings` (list of listing dicts), `weather` (str, optional), `occasion` (str, optional), `user_profile` (dict, optional)
- Returns: A list of outfit dicts, each with `items` (list of listing `id` strings), `description` (str), `style_tags` (list of str), and `confidence` (float 0.0-1.0).
- When it has nothing: Returns an empty list (`[]`).

### `create_fit_card`

- What it does: Renders a single, shareable fit card summarizing an outfit or listing, suitable for display or sending to a UI or API consumer.
- Inputs: `outfit` (dict describing the outfit; required), `image_url` (str, optional), `brand_info` (dict, optional)
- Returns: A dict with `title` (str), `bullet_points` (list of str), `price` (float), `image` (str URL or null), `call_to_action` (str), and `metadata` (dict with source ids and timestamps).
- When it has nothing: Returns `None` when it cannot produce a valid card (e.g., missing required `outfit` information).

### `price_comparison`

- What it does: Compares a target listing's price against similar listings to show how it sits in the market.
- Inputs: `target` (listing dict with `id` and `price`), `candidates` (list of listing dicts, optional)
- Returns: A dict with `target_id` (str), `target_price` (float), `median_price` (float), `min_price` (float), `max_price` (float), `num_competitors` (int), and `competitors` (list of dicts with `id`, `price`, `platform`, `url`, `similarity`).
- When it has nothing: Returns `None` when no comparable listings can be found.

---

## Planning Loop

<!-- Your branch rule, stated as a rule — the condition AND both paths — plus
     the file and function that holds it.

     Like this:
       "If search_listings returns an empty list, put a message in the session
        and stop. Otherwise take the first result and go to suggest_outfit."
        — agent.py::run_agent

     The grader checks your code against what you claim here, so the file and
     function have to be real. -->

**Branch rule:** "If `search_listings` returns an empty list, put a message in the session and stop. Otherwise, take the first result and go to `suggest_outfit`. If `suggest_outfit` returns an empty string or the wardrobe is empty, put a message in the session and stop; otherwise continue to `create_fit_card`." — `agent.py::run_agent`

**Where it lives:** `agent.py::run_agent`

**How the query is parsed:** Regex, in `agent.py::parse_query`. The price is a number after `$` or after "under", "below", "less than", "max" or "up to". The size is `size X`, a waist (`W30`), a shoe size (`US 8.5`), or a standalone size label (`XS`, `XL`, or a capital `S`, `M`, `L`). Every pattern matches whole words only, and only the matched span is removed; the remaining text becomes the description.

> *Changed in the capstone.* The original regex was `(?:under\s+)?(?:\$)?(\d+(?:\.\d+)?)` for price and `(?:size\s+)?([XS]+|M|L|XL|XXL|\d+)` for size. It had no word boundaries and removed every match anywhere in the query, so "dresses" was searched as size SS with the description "dree", and "under $30" also became size 30. That bug caused both capstone misses (C3 and C4).

**What moves through the session:** `query` (input) → `parsed` (description, size, max_price extracted) → `search_results` (list of listings) → `selected_item` (first listing, or None if empty search) → `outfit_suggestion` (model text) → `fit_card` (model caption, or None if stopped early) → `error` (message if branch stops).

---

## Sample Run

<!-- Two things go here.

     1. One FULL query and its output, pasted as text.
     2. Your three per-tool terminal tests — the command and what it printed. -->

**One full query**

```
$ python3 app.py ask 'silk slip dress in midi length under $40'

```

  Found:    Leather Belt — Brown, Braided — $12.0 on thredUp

  Outfit:   Here are two distinct outfit suggestions that incorporate your new brown braided leather belt with your current wardrobe, leaning into its vintage, western, and earth-tone qualities:

### Outfit 1: The Laid-Back Earth-Tone Neutral
*This look plays on relaxed proportions and mixes shades of brown, khaki, and white for an effortless, vintage-casual everyday vibe.*

*   **Bottoms:** Wide-leg khaki trousers
*   **Tops:** White ribbed tank top
*   **Outerwear:** Oversized grey crewneck sweatshirt (worn over the shoulders or layered on top)
*   **Shoes:** Chunky white sneakers
*   **Accessories:** Brown leather belt + Black crossbody bag

**Why it works:** Threading the brown braided belt through the wide-leg khakis anchors the high-waisted fit and breaks up the light earth tones. Pairing it with the crisp white ribbed tank keeps the top half light and summery, while the chunky white sneakers tie the whole casual silhouette together. 

---

### Outfit 2: Western-Edge Denim on Denim
*This look utilizes the belt as a bridge between classic western styling and your darker streetwear pieces.*

*   **Bottoms:** Baggy straight-leg jeans (dark wash)
*   **Tops:** Black cropped zip hoodie
*   **Outerwear:** Vintage black denim jacket
*   **Shoes:** Black combat boots
*   **Accessories:** Brown leather belt

**Why it works:** The dark wash straight-leg jeans provide a great canvas for the rich texture of the brown braided belt, leaning heavily into a rugged, vintage aesthetic. Layering the black cropped zip hoodie under the vintage black denim jacket creates a sleek, monochromatic dark base that lets the brown leather belt stand out as a stylish, contrasting focal point. Finished with the black combat boots, the look gets a tough, grounded edge.

  Fit card: Scored this gorgeous vintage brown braided leather belt on thredUp for just $12 in literal mint condition! Obsessed with how the rich texture adds the *best* earthy, western touch to both lazy-day denim looks and tailored trousers. Can't wait to wear this piece on repeat. 🤎✨

2 model calls this session, 642 prompt + 450 output tokens

**The three tools, tested one at a time**

```
$ python3 -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"

```
[{'id': 'lst_006', 'title': 'Graphic Tee — 2003 Tour Bootleg Style', 'description': 'Vintage-style bootleg tee with faded graphic. Slightly boxy fit. 100% cotton, soft and worn-in.', 'category': 'tops', 'style_tags': ['graphic tee', 'vintage', 'grunge', 'streetwear', 'band tee'], 'size': 'L', 'condition': 'good', 'price': 24.0, 'colors': ['black'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_002', 'title': 'Y2K Baby Tee — Butterfly Print', 'description': 'Super cute early 2000s baby tee with butterfly graphic. Fitted crop length. Tag says medium but fits like a small.', 'category': 'tops', 'style_tags': ['y2k', 'vintage', 'graphic tee', 'cottagecore'], 'size': 'S/M', 'condition': 'excellent', 'price': 18.0, 'colors': ['white', 'pink', 'purple'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_033', 'title': 'Vintage Band Tee — Faded Grey', 'description': 'Faded grey band-style tee with distressed graphic. Crew neck. Fits boxy. Well-loved but no holes or major damage.', 'category': 'tops', 'style_tags': ['vintage', 'grunge', 'band tee', 'graphic tee', 'streetwear'], 'size': 'L', 'condition': 'fair', 'price': 19.0, 'colors': ['grey', 'charcoal'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_015', 'title': 'Vintage Graphic Hoodie — Faded Black', 'description': 'Faded black pullover hoodie with barely-visible vintage graphic on the chest. Cozy interior. Some pilling but adds to the worn-in look.', 'category': 'tops', 'style_tags': ['vintage', 'grunge', 'graphic', 'streetwear'], 'size': 'L', 'condition': 'fair', 'price': 26.0, 'colors': ['black', 'charcoal'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_017', 'title': 'Mesh Long-Sleeve Top — Black', 'description': 'Sheer black mesh long-sleeve. Great for layering under a graphic tee or over a bralette. Stretchy material, fits true to size.', 'category': 'tops', 'style_tags': ['y2k', 'grunge', 'goth', 'layering'], 'size': 'S/M', 'condition': 'excellent', 'price': 15.0, 'colors': ['black'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_011', 'title': 'Low-Rise Cargo Pants — Khaki', 'description': 'Y2K era low-rise cargo pants. Lots of pockets. Khaki color, slightly distressed at the hems. Great for layering with a long tee.', 'category': 'bottoms', 'style_tags': ['y2k', 'cargo', '2000s', 'streetwear'], 'size': 'W29', 'condition': 'fair', 'price': 27.0, 'colors': ['khaki', 'tan'], 'brand': None, 'platform': 'poshmark'}, {'id': 'lst_012', 'title': 'Oversized Crewneck Sweatshirt — Vintage Navy', 'description': 'Perfectly faded navy crewneck. Genuinely vintage — not manufactured distressed. Ribbed cuffs and hem. No graphics, clean.', 'category': 'tops', 'style_tags': ['vintage', 'basics', 'oversized', 'classic'], 'size': 'XL (fits oversized)', 'condition': 'good', 'price': 20.0, 'colors': ['navy'], 'brand': None, '
```
$ python3 -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"

```
Here are two specific outfit suggestions that integrate the medium-wash Levi's 501s with your current wardrobe, leaning into different vibes you can create:

### Outfit 1: Effortless Streetwear Casual
*This look plays with proportions by pairing the straight-leg 501s with an oversized top, grounded by chunky sneakers for an easy, everyday aesthetic.*

* **Bottoms:** Vintage Levi's 501 Jeans (Medium Wash)
* **Top:** Oversized grey crewneck sweatshirt
* **Shoes:** Chunky white sneakers
* **Accessories:** Black crossbody bag + Brown leather belt 

### Outfit 2: Edgy Contrast
*This look creates a cool-girl textural contrast by pairing the vintage medium-wash denim with darker, cropped layers and utilitarian footwear.*

* **Bottoms:** Vintage Levi's 501 Jeans (Medium Wash)
* **Top:** White ribbed tank top
* **Outerwear:** Black cropped zip hoodie (layered over the tank)
* **Shoes:** Black combat boots
* **Accessories:** Brown leather belt
```
$ python3 -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"

```
Nothing beats the broken-in feel of a true vintage pair of Levi's 501s, especially in this classic medium wash. Just dropped these beauties on my Depop for $38 and they are dying for a simple weekend uniform of crisp white sneakers and an oversized tee. Grab them before I change my mind and keep them for myself!
'''
python3 -c "from tools import price_comparison; from utils.data_loader import load_listings; print(price_comparison(load_listings()[0]))"

'''
{'target_id': 'lst_001', 'target_price': 38.0, 'median_price': 30.0, 'min_price': 14.0, 'max_price': 36.0, 'num_competitors': 9, 'competitors': [{'id': 'lst_021', 'price': 29.0, 'platform': 'poshmark', 'url': '', 'similarity': 0.75}, {'id': 'lst_016', 'price': 24.0, 'platform': 'poshmark', 'url': '', 'similarity': 0.65}, {'id': 'lst_037', 'price': 30.0, 'platform': 'thredUp', 'url': '', 'similarity': 0.65}, {'id': 'lst_031', 'price': 36.0, 'platform': 'depop', 'url': '', 'similarity': 0.6}, {'id': 'lst_005', 'price': 32.0, 'platform': 'depop', 'url': '', 'similarity': 0.55}, {'id': 'lst_011', 'price': 27.0, 'platform': 'poshmark', 'url': '', 'similarity': 0.55}, {'id': 'lst_013', 'price': 30.0, 'platform': 'depop', 'url': '', 'similarity': 0.55}, {'id': 'lst_026', 'price': 14.0, 'platform': 'depop', 'url': '', 'similarity': 0.55}, {'id': 'lst_025', 'price': 34.0, 'platform': 'poshmark', 'url': '', 'similarity': 0.5}]}
---

## How I Used AI

<!-- Two specific moments. What you asked, what came back, what you changed.

     "I used Claude to help me code" is not enough.

     "I gave Claude my search_listings spec. It returned None on no match
     instead of an empty list, so I changed it" is the level we want. -->

**Moment 1**

- I told the AI to check my criteria from 3-5 to see if they are good enough for in which I am able to answer and do with no context and give reccomendations for the the targets set 
- The criteria for 3 was not able to be followed with little context so it was unable to decipher and the targets were too lenient (3/5 + 4/5)
- I changed the criteria for number three to better reflect and tested it again until the criteria can be done with no context and I did not follow the AI reccomendation for the targets set so I made the targets 5/5 as I think that would better fit the criterion 


**Moment 2**

- I asked it to tell me what to try next after reading the empty result message and to tell me what would it do if the search returns nothing, knowing nothing about the app. 
- it said it would know to loosen the filters or rephrase, so it isn't a dead end. But It would be guessing which lever matters, and the description would make it suspect the problem was something It couldn't see.
- I made it more descriptive so the AI knows exactly where the search went wrong as well as give it tips on what to try in their next search 

<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

<!-- Five criteria, five tries each, in this exact format.

     Five, because your criteria are written out of five. Mark each try PASS
     or FAIL, count the passes, and read that count against your target — a
     row targeting 4 of 5 with three PASS cells is MISSED (3/5).

     `python run_eval.py --label before` runs everything and writes the table
     into results/. Paste it here and fill in the verdicts. -->



| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. A Matching Query completes all three tools  | 4/5 | PASS | PASS |PASS| PASS | PASS | MET (5/5)|
| 2. An Impossible Query stops before the second tool | 5/5 | PASS |PASS  | PASS | PASS | PASS | MET (5/5) |
| 3. The selected item must survive the whole loop | 5/5 | FAIL | FAIL | FAIL |FAIL| FAIL | MISSED 0/5 |
| 4. fit card fllback and content requirement are both enforced |  4/5| PASS | PASS |PASS  | PASS | PASS | MET (5/5) |
| 5. search enforces the Price Cap | 5/5 |  PASS| PASS | PASS | PASS | PASS | MET (5/5) |

**Real output from one try**, pasted as text, naming the file and function
that produced it:

```

matching query completes  (example wardrobe)
  query: vintage graphic tee under $30
[1] parse_query
      in:  vintage graphic tee under $30
      out: {'description': 'vintage graphic tee', 'size': '30', 'max_price': 30.0}
[2] search_listings (via MCP)
      in:  {'description': 'vintage graphic tee', 'size': '30', 'max_price': 30.0}
      out: 1 items: Straight Leg Khaki Trousers — Olive
      →    branch: results, continuing
[3] select_item
      in:  1 results
      out: Straight Leg Khaki Trousers — Olive ($29.0, poshmark)
      →    first result
[4] suggest_outfit
      in:  new_item='Straight Leg Khaki Trousers — Olive', wardrobe=10 items
      out: Here are two specific outfit suggestions that incorporate your new olive straight-leg trousers, blending that …
[5] create_fit_card
      in:  new_item='Straight Leg Khaki Trousers — Olive', outfit=<suggest_outfit text>
      out: Scored these gorgeous olive straight-leg trousers in pristine condition on Poshmark for just $29, and I am off…
  try 1: completed — fit card 366 chars
[1] parse_query
      in:  vintage graphic tee under $30
      out: {'description': 'vintage graphic tee', 'size': '30', 'max_price': 30.0}
[2] search_listings (via MCP)
      in:  {'description': 'vintage graphic tee', 'size': '30', 'max_price': 30.0}
      out: 1 items: Straight Leg Khaki Trousers — Olive
      →    branch: results, continuing
[3] select_item
      in:  1 results
      out: Straight Leg Khaki Trousers — Olive ($29.0, poshmark)
      →    first result
[4] suggest_outfit
      in:  new_item='Straight Leg Khaki Trousers — Olive', wardrobe=10 items
      out: Here are two specific outfit suggestions that incorporate your new olive straight-leg khaki trousers while pla…
[5] create_fit_card
      in:  new_item='Straight Leg Khaki Trousers — Olive', outfit=<suggest_outfit text>
      out: Found my new favorite pair of trousers on Poshmark for just $29 and the condition is honestly unreal! These ol…
  try 2: completed — fit card 322 chars
[1] parse_query
      in:  vintage graphic tee under $30
      out: {'description': 'vintage graphic tee', 'size': '30', 'max_price': 30.0}
[2] search_listings (via MCP)
      in:  {'description': 'vintage graphic tee', 'size': '30', 'max_price': 30.0}
      out: 1 items: Straight Leg Khaki Trousers — Olive
      →    branch: results, continuing
[3] select_item
      in:  1 results
      out: Straight Leg Khaki Trousers — Olive ($29.0, poshmark)
      →    first result
[4] suggest_outfit
      in:  new_item='Straight Leg Khaki Trousers — Olive', wardrobe=10 items
      out: Here are two specific outfit suggestions that blend your new olive straight-leg trousers with your current war…
[5] create_fit_card
      in:  new_item='Straight Leg Khaki Trousers — Olive', outfit=<suggest_outfit text>
      out: Scored these straight-leg olive trousers in excellent condition on Poshmark for just $29, and they are officia…
  try 3: completed — fit card 358 chars
[1] parse_query
      in:  vintage graphic tee under $30
      out: {'description': 'vintage graphic tee', 'size': '30', 'max_price': 30.0}
[2] search_listings (via MCP)
      in:  {'description': 'vintage graphic tee', 'size': '30', 'max_price': 30.0}
      out: 1 items: Straight Leg Khaki Trousers — Olive
      →    branch: results, continuing
[3] select_item
      in:  1 results
      out: Straight Leg Khaki Trousers — Olive ($29.0, poshmark)
      →    first result
[4] suggest_outfit
      in:  new_item='Straight Leg Khaki Trousers — Olive', wardrobe=10 items
      out: Here are 2 specific outfit suggestions that seamlessly integrate your new olive straight-leg trousers into you…
[5] create_fit_card
      in:  new_item='Straight Leg Khaki Trousers — Olive', outfit=<suggest_outfit text>
      out: Scored these olive straight-leg trousers in pristine condition for just $29 on Poshmark, and they are official…
  try 4: completed — fit card 371 chars
[1] parse_query
      in:  vintage graphic tee under $30
      out: {'description': 'vintage graphic tee', 'size': '30', 'max_price': 30.0}
[2] search_listings (via MCP)
      in:  {'description': 'vintage graphic tee', 'size': '30', 'max_price': 30.0}
      out: 1 items: Straight Leg Khaki Trousers — Olive
      →    branch: results, continuing
[3] select_item
      in:  1 results
      out: Straight Leg Khaki Trousers — Olive ($29.0, poshmark)
      →    first result
[4] suggest_outfit
      in:  new_item='Straight Leg Khaki Trousers — Olive', wardrobe=10 items
      out: Here are two specific outfit suggestions that incorporate your new olive straight-leg trousers with pieces fro…
[5] create_fit_card
      in:  new_item='Straight Leg Khaki Trousers — Olive', outfit=<suggest_outfit text>
      out: Scored these gorgeous olive straight-leg trousers in pristine condition for just $29 on Poshmark, and I am off…
  try 5: completed — fit card 336 chars

impossible query stops early  (example wardrobe)
  query: designer ballgown size XXS under $5
[1] parse_query
      in:  designer ballgown size XXS under $5
      out: {'description': 'deigner bagown', 'size': 'S', 'max_price': 5.0}
[2] search_listings (via MCP)
      in:  {'description': 'deigner bagown', 'size': 'S', 'max_price': 5.0}
      out: [] (empty)
      →    branch: empty, stopping
  try 1: stopped early — No items found matching 'deigner bagown' under $5.0 in size 
[1] parse_query
      in:  designer ballgown size XXS under $5
      out: {'description': 'deigner bagown', 'size': 'S', 'max_price': 5.0}
[2] search_listings (via MCP)
      in:  {'description': 'deigner bagown', 'size': 'S', 'max_price': 5.0}
      out: [] (empty)
      →    branch: empty, stopping
  try 2: stopped early — No items found matching 'deigner bagown' under $5.0 in size 
[1] parse_query
      in:  designer ballgown size XXS under $5
      out: {'description': 'deigner bagown', 'size': 'S', 'max_price': 5.0}
[2] search_listings (via MCP)
      in:  {'description': 'deigner bagown', 'size': 'S', 'max_price': 5.0}
      out: [] (empty)
      →    branch: empty, stopping
  try 3: stopped early — No items found matching 'deigner bagown' under $5.0 in size 
[1] parse_query
      in:  designer ballgown size XXS under $5
      out: {'description': 'deigner bagown', 'size': 'S', 'max_price': 5.0}
[2] search_listings (via MCP)
      in:  {'description': 'deigner bagown', 'size': 'S', 'max_price': 5.0}
      out: [] (empty)
      →    branch: empty, stopping
  try 4: stopped early — No items found matching 'deigner bagown' under $5.0 in size 
[1] parse_query
      in:  designer ballgown size XXS under $5
      out: {'description': 'deigner bagown', 'size': 'S', 'max_price': 5.0}
[2] search_listings (via MCP)
      in:  {'description': 'deigner bagown', 'size': 'S', 'max_price': 5.0}
      out: [] (empty)
      →    branch: empty, stopping
  try 5: stopped early — No items found matching 'deigner bagown' under $5.0 in size 

empty wardrobe  (empty wardrobe)
  query: denim jacket under $50
[1] parse_query
      in:  denim jacket under $50
      out: {'description': 'deni jacket', 'size': 'M', 'max_price': 50.0}
[2] search_listings (via MCP)
      in:  {'description': 'deni jacket', 'size': 'M', 'max_price': 50.0}
      out: 3 items: 90s Track Jacket — Navy/White Stripe, Shacket — Olive Canvas, Denim Vest — Medium Wash, Studded
      →    branch: results, continuing
[3] select_item
      in:  3 results
      out: 90s Track Jacket — Navy/White Stripe ($45.0, poshmark)
      →    first result
[4] suggest_outfit
      in:  new_item='90s Track Jacket — Navy/White Stripe', wardrobe=0 items
      out: That’s an incredible find. A 90s Champion track jacket in navy with white stripes is the ultimate heritage str…
[5] create_fit_card
      in:  new_item='90s Track Jacket — Navy/White Stripe', outfit=<suggest_outfit text>
      out: Scored this absolute vintage treasure on Poshmark for just $45! This 90s navy and white striped track jacket h…
  try 1: completed — fit card 291 chars
[1] parse_query
      in:  denim jacket under $50
      out: {'description': 'deni jacket', 'size': 'M', 'max_price': 50.0}
[2] search_listings (via MCP)
      in:  {'description': 'deni jacket', 'size': 'M', 'max_price': 50.0}
      out: 3 items: 90s Track Jacket — Navy/White Stripe, Shacket — Olive Canvas, Denim Vest — Medium Wash, Studded
      →    branch: results, continuing
[3] select_item
      in:  3 results
      out: 90s Track Jacket — Navy/White Stripe ($45.0, poshmark)
      →    first result
[4] suggest_outfit
      in:  new_item='90s Track Jacket — Navy/White Stripe', wardrobe=0 items
      out: That is an absolute classic find. A 90s Champion navy and white track jacket is the holy grail of vintage athl…
[5] create_fit_card
      in:  new_item='90s Track Jacket — Navy/White Stripe', outfit=<suggest_outfit text>
      out: Absolute holy grail find secured! ⚡️ Scoring this vintage 90s navy and white track jacket in pristine conditio…
  try 2: completed — fit card 385 chars
[1] parse_query
      in:  denim jacket under $50
      out: {'description': 'deni jacket', 'size': 'M', 'max_price': 50.0}
[2] search_listings (via MCP)
      in:  {'description': 'deni jacket', 'size': 'M', 'max_price': 50.0}
      out: 3 items: 90s Track Jacket — Navy/White Stripe, Shacket — Olive Canvas, Denim Vest — Medium Wash, Studded
      →    branch: results, continuing
[3] select_item
      in:  3 results
      out: 90s Track Jacket — Navy/White Stripe ($45.0, poshmark)
      →    first result
[4] suggest_outfit
      in:  new_item='90s Track Jacket — Navy/White Stripe', wardrobe=0 items
      out: That is an absolute classic find! A 90s Champion navy and white stripe track jacket is one of the most versati…
  [rate limit] 15 requests used this minute. Waiting 32s. This is normal.
[5] create_fit_card
      in:  new_item='90s Track Jacket — Navy/White Stripe', outfit=<suggest_outfit text>
      out: Scored the ultimate 90s vintage track jacket in pristine condition for just $45! ⚡️ Obsessed with the navy and…
  try 3: completed — fit card 361 chars
[1] parse_query
      in:  denim jacket under $50
      out: {'description': 'deni jacket', 'size': 'M', 'max_price': 50.0}
[2] search_listings (via MCP)
      in:  {'description': 'deni jacket', 'size': 'M', 'max_price': 50.0}
      out: 3 items: 90s Track Jacket — Navy/White Stripe, Shacket — Olive Canvas, Denim Vest — Medium Wash, Studded
      →    branch: results, continuing
[3] select_item
      in:  3 results
      out: 90s Track Jacket — Navy/White Stripe ($45.0, poshmark)
      →    first result
[4] suggest_outfit
      in:  new_item='90s Track Jacket — Navy/White Stripe', wardrobe=0 items
      out: That is a classic find! A 90s Champion track jacket is the ultimate versatile piece because it bridges the gap…
[5] create_fit_card
      in:  new_item='90s Track Jacket — Navy/White Stripe', outfit=<suggest_outfit text>
      out: Scored this vintage 90s navy and white track jacket in mint condition for just $45 on Poshmark! It’s the ultim…
  try 4: completed — fit card 281 chars
[1] parse_query
      in:  denim jacket under $50
      out: {'description': 'deni jacket', 'size': 'M', 'max_price': 50.0}
[2] search_listings (via MCP)
      in:  {'description': 'deni jacket', 'size': 'M', 'max_price': 50.0}
      out: 3 items: 90s Track Jacket — Navy/White Stripe, Shacket — Olive Canvas, Denim Vest — Medium Wash, Studded
      →    branch: results, continuing
[3] select_item
      in:  3 results
      out: 90s Track Jacket — Navy/White Stripe ($45.0, poshmark)
      →    first result
[4] suggest_outfit
      in:  new_item='90s Track Jacket — Navy/White Stripe', wardrobe=0 items
      out: That is a classic find! A 90s Champion track jacket in navy with white stripes is the ultimate heritage street…
[5] create_fit_card
      in:  new_item='90s Track Jacket — Navy/White Stripe', outfit=<suggest_outfit text>
      out: Scored this pristine 90s navy and white track jacket for just $45, and honestly, it’s the ultimate heritage st…
  try 5: completed — fit card 385 chars

Wrote results/run_2026-10-11_1347_before.md
```

---

## Verdicts and Diagnoses

<!-- MET or MISSED per criterion against LAST UNIT's target, plus a sentence on
     how you decided.

     Then, for every miss: which of the four places it happened — a tool, the
     loop's branch, the session, or the model's output — AND the mechanism.

     Not a diagnosis:  "The fit card was bad."
     A diagnosis:      "The fit card criterion missed on 2 of 5 items. Both had
                        an empty brand field. My prompt puts the brand in the
                        first sentence, so the card opened with a blank and read
                        like a fragment. The tool worked; the prompt assumed a
                        field that isn't always there."

     Look for a pattern. Three misses on the same tool is one problem, not
     three. -->

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1. A Matching Query completes all three tools  | 4/5 | 5/5 | In all five tries, the three tools worked as intended and each try ends with a fit card  |  
| 2. An Impossible Query stops before the second tool | 5/5 | 5/5 | All impossible queries in all 5 tries stopped early and the message said what to change in the search |  
| 3. The selected item must survive the whole loop | 5/5 | 0/5| While it survived the loop, no id appears in the log and that is what the criterion asks for, the id |
| 4. fit card fllback and content requirement are both enforced| 5/5 | 5/5 | every item has 3-4 sentences and mentions both price and platform|
| 5. search enforces the Price Cap| 5/5 | 5/5 | every try returned under the price capped at $30 so they all passed |  

**Diagnoses**



---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

**Happy path** (`python app.py ask 'vintage graphic tee under $30' --trace`)

```
[1] parse_query
      in:  vintage graphic tee under $30
      out: {'description': 'vintage graphic tee', 'size': '30', 'max_price': 30.0}
[2] search_listings (via MCP)
      in:  {'description': 'vintage graphic tee', 'size': '30', 'max_price': 30.0}
      out: 1 items: Straight Leg Khaki Trousers — Olive
      →    branch: results, continuing
[3] select_item
      in:  1 results
      out: Straight Leg Khaki Trousers — Olive ($29.0, poshmark)
      →    first result
[4] suggest_outfit
      in:  new_item='Straight Leg Khaki Trousers — Olive', wardrobe=10 items
      out: Here are two specific outfit suggestions that incorporate your new olive straight-leg khaki trousers while pla…
[5] create_fit_card
      in:  new_item='Straight Leg Khaki Trousers — Olive', outfit=<suggest_outfit text>
      out: Scored these olive straight-leg trousers in excellent condition on Poshmark for just $29, and I am officially …
```

The loop works, but step [1] shows the query parser reading the price "30" as `size='30'`, so the search's only match is a pair of W30 trousers, not a tee.

**Empty search** (`python app.py ask 'designer ballgown size XXS under $5' --trace`)

```
[1] parse_query
      in:  designer ballgown size XXS under $5
      out: {'description': 'deigner bagown', 'size': 'S', 'max_price': 5.0}
[2] search_listings (via MCP)
      in:  {'description': 'deigner bagown', 'size': 'S', 'max_price': 5.0}
      out: [] (empty)
      →    branch: empty, stopping
```

Two steps instead of five: the branch stops before `suggest_outfit`.

**On the MCP move:** <!-- what changed in your code, and whether anything
behaved differently afterwards. If the rewire didn't work, say exactly where it
broke — the error text and the last thing that worked. That earns the point in
full. -->



---

## Failure Modes

Each one triggered on its own, with `search_listings` running over MCP.

**1. Empty search.** `python app.py ask 'designer ballgown size XXS under $5'`

```
  No items found matching 'deigner bagown' under $5.0 in size S. Try different keywords, a higher price, or removing size filters.

0 model calls this session
```

Handled: the loop stopped before `suggest_outfit` and named three things to change. The message also exposes a parser bug in `agent.py::run_agent`: the size regex has no word boundaries, so it took the "s" in "designer" as size S (not XXS) and stripped letters out of the description.

**2. Empty wardrobe.** `python app.py ask 'denim jacket under $50' --empty-wardrobe`

```
(running with an empty wardrobe)

  Found:    90s Track Jacket — Navy/White Stripe — $45.0 on poshmark

  Outfit:   That is an absolute classic find. ... Since you are starting your
            wardrobe from scratch, this jacket is a fantastic anchor piece.
            Here are two distinct ways to style it ...
            [two looks built from essentials to buy, plus a starter checklist]

  Fit card: Scored the ultimate 90s heritage piece today ...

2 model calls this session, 786 prompt + 691 output tokens
```

Handled: `suggest_outfit` returned real advice, not a crash and not an empty string, and the fit card still rendered. Same parser bug: "denim" contains an "m", so it searched with size M and a mangled description, which is why it found a track jacket instead of a denim one.

**3. Model unavailable.** Changed the last character of `GEMINI_API_KEY`, then ran a query I hadn't asked before: `python app.py ask 'corduroy overshirt in olive under $35'`

```
ModelUnavailable: The model rejected your API key. Check GEMINI_API_KEY in your .env file, or create a fresh key at aistudio.google.com.

1 model calls this session
```

Not handled by the agent. That clean message came from the catch-all in `app.py::main`, not from my loop: `run_agent` raised, the session (and the listing it had already found) was lost, and the run exited with code 1. Calling `run_agent` directly would have shown a stack trace.

Fix: `agent.py::run_agent` now catches `ModelUnavailable` around `suggest_outfit` and `create_fit_card`, keeps the search result, and puts a message in `session["error"]`. Re-run with a broken key and a new query (`python app.py ask 'faded black denim jacket under $60' --trace`):

```
[3] select_item
      in:  6 results
      out: Vintage Graphic Hoodie — Faded Black ($26.0, depop)
      →    first result
[4] model call failed
      out: The model rejected your API key. Check GEMINI_API_KEY in your .env file, or create a fresh key at aistudio.goo…
      →    ModelUnavailable, stopping

  Found Vintage Graphic Hoodie — Faded Black ($26.0 on depop), but couldn't reach the model to style it: The model rejected your API key. Check GEMINI_API_KEY in your .env file, or create a fresh key at aistudio.google.com. Fix that and ask again.
```

Now it names what broke and what to do, exits 0, and doesn't hang (about 1 second). I put the key back afterwards.

---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:**
In tools.py, I added the ID and price to both tools output as well as added the price to the suggest_outfit prompt. in agent.py, the ID and price showed in the trace and in run_eval.py, the ID showed in the run log  
**Which failure it was meant to fix:**
it was meant to fix the fact that the runs in criterion 3, all while showing the item, did not show the id or price during the loop. 
### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. A Matching Query completes all three tools  | 4/5 | PASS | PASS |PASS| PASS | PASS | MET (5/5)|
| 2. An Impossible Query stops before the second tool | 5/5 | PASS |PASS  | PASS | PASS | PASS | MET (5/5) |
| 3. The selected item must survive the whole loop | 5/5 | PASS | PASS | PASS |PASS| PASS | MET 5/5 |
| 4. fit card fllback and content requirement are both enforced |  4/5| PASS | PASS |PASS  | PASS | PASS | MET (5/5) |
| 5. search enforces the Price Cap | 5/5 |  PASS| PASS | PASS | PASS | PASS | MET (5/5) |

**Did it help, and how do I know:**

It helped as now the ID and price is showing within each run and try for the third criterion. 


---

## What's Still Broken

While nothing is technically broken and technically every criterion is passing, the catch for criterion 1 is that sometimes it finds the wrong item or the match is incorrect. But since the criterions only ask if all three tools run, it is techncially passing. This is something I would have to fix and make sure that the criterion is tightened. 

## Capstone 

**What Shape did I choose**
I picked Shape C: add one real capability to a system that already works. My project already has a fourth tool (price comparison), so I'm adding a second retrieval strategy to search_listings.
Right now search uses keyword overlap, which only matches exact words. "tee" returns 5 listings but "tees" returns 0, and "denim pants" misses jeans whose titles don't contain "pants." This is the same weakness I described in What's Still Broken: criterion 1 passes even when search returns the wrong item.
The new strategy is embedding search: each listing's title, description, and style tags are turned into an embedding, and listings are ranked by cosine similarity to the query's embedding. Keyword search stays as the default. The agent falls back to embeddings when keyword search returns nothing, and the trace records that branch.
How I'll know it works: I'll label about 15 queries with the listing IDs that should come back. I'll include plurals, synonyms, and queries keyword search already handles. I'll report hit@3 (a correct item in the top 3) for both strategies side by side. 
My target, set before running: embeddings hit on at least 12/15, beat keyword on the plural and synonym queries, and do no worse on the queries keyword already gets right.

**What is out of scope** 

1. **I'm not replacing keyword search or blending the two.** Keyword search stays the default, and embeddings only run when it comes back empty. Merging both scores into one hybrid ranking would mean picking weights and tuning them. Then I couldn't report hit@3 for each strategy on its own, which is the whole measurement.
2. **I'm not adding a vector database or a reranker.** There are 40 listings. I'll embed them once and keep the vectors in memory. A database, or a second model pass to re-sort the top results, is more to build and debug, and the comparison doesn't need it.
3. **I'm not touching the other tools or the interface.** `suggest_outfit`, `create_fit_card`, `price_comparison`, style memory, `app.py` and the CLI output all stay as they are. If the numbers move, it's because of retrieval and not because I also changed a prompt.


---

## Capstone Run Log

Each of the five capstone criteria (C1–C5, in `criteria.md`) was run three
separate times, with the response cache off, on 18 November 2026 between
02:21 and 02:48. A criterion is MET only if every run met its target.

These runs include the query parser fix (`agent.py::parse_query`), which was
made after the first measurement. Before the fix, C4 scored 4/10 and C3 2/5.

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| C1. Embedding hit@3 ≥ 12/15, beats keyword on plurals/synonyms, ties on exact | ≥ 12 of 15 | 15/15 (keyword 5/15) | 15/15 (keyword 5/15) | 15/15 (keyword 5/15) | MET |
| C2. Recorded strategy matches whether keyword search was empty | 10 of 10 | 10/10 | 10/10 | 10/10 | MET |
| C3. Unseen off-topic queries return 0 listings and make 0 model calls | 5 of 5 | 3/5 | 3/5 | 3/5 | MISSED |
| C4. Plural/synonym queries typed into the agent select a labelled listing | ≥ 8 of 10 | 9/10 | 9/10 | 9/10 | MET |
| C5. Original criteria 1–5 all MET, and `lst_021`/`lst_004` selected in 10 of 10 tries | 5/5 MET; ids 10/10 | 5/5 MET; ids 0/10 | 5/5 MET; ids 0/10 | 5/5 MET; ids 0/10 | MISSED |

### Real output from run 1

All of this is copied from the files saved during run 1
(18 November 2026, 02:21–02:26), in `results/capstone_runs/run1/`. The text
is unchanged. The only edits: some blocks show selected lines (each one says
so), the fit card's code fence was removed, and the scored C5 entry's lists
are put on single lines.

In the agent traces, the numbered `[n] step / in / out / →` lines are written
by `trace.py::step`, called from `agent.py::run_agent`. The `(via MCP)` steps
are the searches running in `mcp_server.py`.

**C1:** `c1_stdout.txt`, printed by `eval_retrieval.py::main`, which calls
`tools.py::search_listings` and `tools.py::semantic_search_scored` directly.

```
| Group | Keyword | Embedding | Agent policy (keyword → embedding if empty) |
|---|---|---|---|
| plural | 0/5 | 5/5 | 5/5 |
| synonym | 0/5 | 5/5 | 4/5 |
| exact | 5/5 | 5/5 | 5/5 |
| **all** | **5/15** | **15/15** | **14/15** |

| Group | Query | Relevant | Keyword top 3 | KW | Embedding top 3 (score) | EM | Fallback ran? | Policy |
|---|---|---|---|---|---|---|---|---|
| plural | tees | lst_006, lst_002, lst_033 | (empty) | miss | lst_033 (0.67), lst_002 (0.67), lst_006 (0.66) | HIT | yes | HIT |
| synonym | denim pants | lst_001, lst_031, lst_037 | lst_005, lst_007, lst_011 | miss | lst_037 (0.69), lst_016 (0.67), lst_001 (0.67) | HIT | no | miss |
| synonym | purse | lst_039 | (empty) | miss | lst_039 (0.68), lst_034 (0.62), lst_040 (0.61) | HIT | yes | HIT |
| exact | chelsea boots | lst_028 | lst_028 | HIT | lst_028 (0.71), lst_009 (0.62), lst_019 (0.60) | HIT | no | HIT |
```

(4 of the 15 per-query rows shown; all 15 are in the file.)

**C2:** `c2_c3_c4_stdout.txt`. The trace is from `agent.py::run_agent`; the
`C2 …` lines and the final tally are printed by `eval_capstone.py::main`. Below
are one query where keyword search found results (no
`semantic_search_listings` step) and one where it returned `[]` (fallback
step present), then all ten result lines.

```
[1] parse_query
      in:  chelsea boots
      out: {'description': 'chelsea boots', 'size': None, 'max_price': None}
[2] search_listings (via MCP)
      in:  {'description': 'chelsea boots', 'size': None, 'max_price': None}
      out: 1 items: Suede Chelsea Boots — Tan
      →    branch: results, continuing
[3] select_item
      in:  1 results
      out: Suede Chelsea Boots — Tan ($44.0, poshmark)
      →    first result
[4] suggest_outfit
      in:  new_item=lst_028 'Suede Chelsea Boots — Tan' ($44.0), wardrobe=10 items
      out: [lst_028 · $44.0] At $44, tan suede Chelsea boots are a fantastic find—they add a softer, more vintage texture…
[5] create_fit_card
      in:  new_item=lst_028 'Suede Chelsea Boots — Tan' ($44.0), outfit=<suggest_outfit text>
      out: [lst_028 · $44.0] Scored these tan suede Chelsea boots in fair condition on Poshmark for just $44, and honestl…
  C2 'chelsea boots': keyword results → keyword PASS
```

```
[1] parse_query
      in:  tees
      out: {'description': 'tees', 'size': None, 'max_price': None}
[2] search_listings (via MCP)
      in:  {'description': 'tees', 'size': None, 'max_price': None}
      out: [] (empty)
      →    branch: empty, trying embedding search
[3] semantic_search_listings (via MCP)
      in:  {'description': 'tees', 'size': None, 'max_price': None}
      out: 10 items: Vintage Band Tee — Faded Grey, Y2K Baby Tee — Butterfly Print, Graphic Tee — 2003 Tour Bootleg Style … +7 more
      →    branch: results, continuing
[4] select_item
      in:  10 results
      out: Vintage Band Tee — Faded Grey ($19.0, depop)
      →    first result
[5] suggest_outfit
      in:  new_item=lst_033 'Vintage Band Tee — Faded Grey' ($19.0), wardrobe=10 items
      out: [lst_033 · $19.0] Here are two specific outfit suggestions that blend the grunge, vintage vibe of your new ban…
[6] create_fit_card
      in:  new_item=lst_033 'Vintage Band Tee — Faded Grey' ($19.0), outfit=<suggest_outfit text>
      out: [lst_033 · $19.0] Scored this perfectly faded vintage band tee for just $19 on Depop and I’m officially obsess…
  C2 'tees': keyword empty → embedding PASS
```

```
  C2 'chelsea boots': keyword results → keyword PASS
  C2 'denim jacket under $50': keyword results → keyword PASS
  C2 'cargo pants': keyword results → keyword PASS
  C2 'graphic tee': keyword results → keyword PASS
  C2 'leather belt': keyword results → keyword PASS
  C2 'tees': keyword empty → embedding PASS
  C2 'hoodies': keyword empty → embedding PASS
  C2 'dresses': keyword empty → embedding PASS
  C2 'blazers': keyword empty → embedding PASS
  C2 'belts': keyword empty → embedding PASS
```

**C3:** `c2_c3_c4_stdout.txt`, from the same two functions. The first
query passed: keyword search returned `[]`, the fallback returned `[]`, and
the run stopped with no model calls. The second failed: keyword search
returned 10 listings, so the fallback never ran and the agent styled a
cardigan with 2 model calls. Then all five result lines.

```
[1] parse_query
      in:  airline ticket refund
      out: {'description': 'airline ticket refund', 'size': None, 'max_price': None}
[2] search_listings (via MCP)
      in:  {'description': 'airline ticket refund', 'size': None, 'max_price': None}
      out: [] (empty)
      →    branch: empty, trying embedding search
[3] semantic_search_listings (via MCP)
      in:  {'description': 'airline ticket refund', 'size': None, 'max_price': None}
      out: [] (empty)
      →    branch: empty, stopping
  C3 'airline ticket refund': direct 0 listings, agent no_results with 0 calls → PASS
```

```
[1] parse_query
      in:  how to change a car tire
      out: {'description': 'how to change a car tire', 'size': None, 'max_price': None}
[2] search_listings (via MCP)
      in:  {'description': 'how to change a car tire', 'size': None, 'max_price': None}
      out: 10 items: Knit Cardigan — Chunky Brown, Vintage Levi's 501 Jeans — Medium Wash, Graphic Tee — 2003 Tour Bootleg Style … +7 more
      →    branch: results, continuing
[3] select_item
      in:  10 results
      out: Knit Cardigan — Chunky Brown ($35.0, depop)
      →    first result
[4] suggest_outfit
      in:  new_item=lst_008 'Knit Cardigan — Chunky Brown' ($35.0), wardrobe=10 items
      out: [lst_008 · $35.0] Here are two specific outfit suggestions that combine your new chunky brown cardigan with pi…
[5] create_fit_card
      in:  new_item=lst_008 'Knit Cardigan — Chunky Brown' ($35.0), outfit=<suggest_outfit text>
      out: [lst_008 · $35.0] scored this chunky brown knit cardigan in pristine condition on Depop for just $35 and I am …
  C3 'how to change a car tire': direct 0 listings, agent ok with 2 calls → FAIL
```

```
  C3 'airline ticket refund': direct 0 listings, agent no_results with 0 calls → PASS
  C3 'how to change a car tire': direct 0 listings, agent ok with 2 calls → FAIL
  C3 'python list comprehension': direct 0 listings, agent no_results with 0 calls → PASS
  C3 'pizza delivery near me': direct 0 listings, agent ok with 2 calls → FAIL
  C3 'mortgage interest rates': direct 0 listings, agent no_results with 0 calls → PASS
```

**C4:** `c2_c3_c4_stdout.txt`, from the same two functions. This is the one
failing query: keyword search found "denim" in 7 listings and put the
corduroys first, so the fallback never ran. Then all ten result lines and the
run's final tally.

```
[1] parse_query
      in:  denim pants
      out: {'description': 'denim pants', 'size': None, 'max_price': None}
[2] search_listings (via MCP)
      in:  {'description': 'denim pants', 'size': None, 'max_price': None}
      out: 7 items: Corduroy Wide-Leg Pants — Rust, Denim Jacket — Light Wash, Cropped, Low-Rise Cargo Pants — Khaki … +4 more
      →    branch: results, continuing
[3] select_item
      in:  7 results
      out: Corduroy Wide-Leg Pants — Rust ($32.0, depop)
      →    first result
[4] suggest_outfit
      in:  new_item=lst_005 'Corduroy Wide-Leg Pants — Rust' ($32.0), wardrobe=10 items
      out: [lst_005 · $32.0] Here are two outfit suggestions that incorporate your new rust corduroy pants into your curr…
[5] create_fit_card
      in:  new_item=lst_005 'Corduroy Wide-Leg Pants — Rust' ($32.0), outfit=<suggest_outfit text>
      out: [lst_005 · $32.0] scored these vintage-washed rust corduroy wide-legs on Depop for just $32 and I am never tak…
  C4 'denim pants': selected lst_005 → FAIL
```

```
  C4 'tees': selected lst_033 → PASS
  C4 'hoodies': selected lst_015 → PASS
  C4 'dresses': selected lst_013 → PASS
  C4 'blazers': selected lst_018 → PASS
  C4 'belts': selected lst_014 → PASS
  C4 'denim pants': selected lst_005 → FAIL
  C4 'sweater': selected lst_008 → PASS
  C4 'purse': selected lst_039 → PASS
  C4 'trainers': selected lst_019 → PASS
  C4 'headwear': selected lst_034 → PASS
C2 10/10   C3 3/5   C4 9/10
```

**C5:** `c5_stdout.txt`. The trace is from `agent.py::run_agent`; the
`try N:` lines are printed by `run_eval.py::main`. Below are try 1 of each
scenario, the full fit card that `run_eval.py::write_report` saved to
`run_2026-11-18_0226_capstone_run1.md`, and run 1's scored entry, which
`capstone_runlog.py::main` wrote to `results/capstone_runs/RUN_LOG.md`.

Matching query, try 1. All three tools ran, the selected listing is `lst_006`
(not unit 4's `lst_021`), and its id and price are stamped on both model
outputs:

```
matching query completes  (example wardrobe)
  query: vintage graphic tee under $30
[1] parse_query
      in:  vintage graphic tee under $30
      out: {'description': 'vintage graphic tee', 'size': None, 'max_price': 30.0}
[2] search_listings (via MCP)
      in:  {'description': 'vintage graphic tee', 'size': None, 'max_price': 30.0}
      out: 10 items: Graphic Tee — 2003 Tour Bootleg Style, Vintage Band Tee — Faded Grey, Y2K Baby Tee — Butterfly Print … +7 more
      →    branch: results, continuing
[3] select_item
      in:  10 results
      out: Graphic Tee — 2003 Tour Bootleg Style ($24.0, depop)
      →    first result
[4] suggest_outfit
      in:  new_item=lst_006 'Graphic Tee — 2003 Tour Bootleg Style' ($24.0), wardrobe=10 items
      out: [lst_006 · $24.0] Here are two ways to style your new 2003 tour bootleg tee using items already in your wardro…
[5] create_fit_card
      in:  new_item=lst_006 'Graphic Tee — 2003 Tour Bootleg Style' ($24.0), outfit=<suggest_outfit text>
      out: [lst_006 · $24.0] Scored this absolute gem of a 2003 tour bootleg tee on Depop for just $24, and the vintage f…
  try 1: completed — fit card 290 chars
```

```
Fit card:

[lst_006 · $24.0]
Scored this absolute gem of a 2003 tour bootleg tee on Depop for just $24, and the vintage fade on it is unreal. It’s got that heavy-duty grunge energy that makes any basic outfit look instantly cool. Grab it over on my shop before I change my mind and keep it for myself!
```

Impossible query, try 1. It stopped before `suggest_outfit`:

```
impossible query stops early  (example wardrobe)
  query: designer ballgown size XXS under $5
[1] parse_query
      in:  designer ballgown size XXS under $5
      out: {'description': 'designer ballgown', 'size': 'XXS', 'max_price': 5.0}
[2] search_listings (via MCP)
      in:  {'description': 'designer ballgown', 'size': 'XXS', 'max_price': 5.0}
      out: [] (empty)
      →    branch: empty, trying embedding search
[3] semantic_search_listings (via MCP)
      in:  {'description': 'designer ballgown', 'size': 'XXS', 'max_price': 5.0}
      out: [] (empty)
      →    branch: empty, stopping
  try 1: stopped early — No items found matching 'designer ballgown' under $5.0 in si
```

Empty wardrobe, try 1. The selected listing is `lst_007` (not unit 4's
`lst_004`), and there's no `semantic_search_listings` step, so the fallback
didn't cause the change:

```
empty wardrobe  (empty wardrobe)
  query: denim jacket under $50
[1] parse_query
      in:  denim jacket under $50
      out: {'description': 'denim jacket', 'size': None, 'max_price': 50.0}
[2] search_listings (via MCP)
      in:  {'description': 'denim jacket', 'size': None, 'max_price': 50.0}
      out: 7 items: Denim Jacket — Light Wash, Cropped, 90s Track Jacket — Navy/White Stripe, High-Waisted Denim Shorts — Cutoff … +4 more
      →    branch: results, continuing
[3] select_item
      in:  7 results
      out: Denim Jacket — Light Wash, Cropped ($42.0, poshmark)
      →    first result
[4] suggest_outfit
      in:  new_item=lst_007 'Denim Jacket — Light Wash, Cropped' ($42.0), wardrobe=0 items
      out: [lst_007 · $42.0] That is a classic find! A vintage Wrangler light wash cropped denim jacket is one of the mos…
[5] create_fit_card
      in:  new_item=lst_007 'Denim Jacket — Light Wash, Cropped' ($42.0), outfit=<suggest_outfit text>
      out: [lst_007 · $42.0] Scored this vintage Wrangler light wash cropped denim jacket in excellent condition on Poshm…
  try 1: completed — fit card 343 chars
```

Run 1's scored C5 entry. `criteria` is the number of tries (out of 5) that
met each original criterion 1–5, and `ids_matching_unit4` is the number of
tries (out of 10) that selected `lst_021`/`lst_004`:

```json
"run1": {
  "started": "2026-11-18T02:21:20",
  "finished": "2026-11-18T02:26:14",
  "c5": {
    "criteria": {"1": 5, "2": 5, "3": 5, "4": 5, "5": 5},
    "selected": {
      "matching query completes": ["lst_006", "lst_006", "lst_006", "lst_006", "lst_006"],
      "impossible query stops early": ["(none)", "(none)", "(none)", "(none)", "(none)"],
      "empty wardrobe": ["lst_007", "lst_007", "lst_007", "lst_007", "lst_007"]
    },
    "ids_matching_unit4": 0
  }
}
```

**How it was run:** `python capstone_runlog.py` runs `eval_retrieval.py`
(C1), `eval_capstone.py` (C2–C4) and `run_eval.py` (C5, 5 tries per scenario)
once per run, saves everything they print, and scores each cell from the
saved files. Before using it, I checked its C5 scoring against two earlier
runs I had scored by hand, and it matched both. The raw output for each run
is in `results/capstone_runs/run1`–`run3`, and the scored table is in
`results/capstone_runs/RUN_LOG.md`.

A first attempt was killed partway through run 1, when my Claude Code session
ended. Its partial output is kept in `results/capstone_runs_incomplete/` and
is not used here.

**The runs were identical.** All three gave the same numbers, and the same
queries failed every time. Both searches are deterministic, so only the
model's writing varied between runs. That varies the fit card text, not which
listing is chosen or which branch runs.

### Verdicts

Each verdict is scored against the target set in `criteria.md`. A target
counts as met only if it held in all three runs.

- **C1: MET.** 15/15 in all 3 runs (target ≥ 12 of 15). It beat keyword
  search on plurals and synonyms (10/10 vs 0/10) and tied it on exact wording
  (5/5 vs 5/5).
- **C2: MET.** 10/10 in all 3 runs (target 10 of 10).
- **C3: MISSED.** 3/5 in all 3 runs (target 5 of 5).
- **C4: MET.** 9/10 in all 3 runs (target ≥ 8 of 10).
- **C5: MISSED.** All 5 original criteria were met in every run, but the
  listing ids matched 0/10 in every run (target 10/10).

### Diagnoses

**C3 (MISSED).** The same 2 of 5 off-topic queries failed in all three runs:
`how to change a car tire` and `pizza delivery near me`. **The stage is
keyword search, `tools.py::search_listings`. The fallback and its floor never
ran.** Called directly, `semantic_search_listings` returned 0 listings for all
5 queries in all 3 runs.

The mechanism is the description check, `elif keyword in desc_text`. It's a
substring test against the whole description string, while the title check
splits the title into words first. A query word therefore matches if it
appears *inside* any word of a description:

- "me" matches 17 listings, through "medium", "some" and similar words,
  though no description contains "me" as a word.
- "car" matches inside "cardigan", which is why the car-tire query styled a
  knit cardigan.
- "a" matches all 40 listings.

Keyword search returns 10 results, so the agent never takes its empty-result
branch, and it spends 2 model calls styling an unrelated listing.

My criterion assumed an off-topic query would reach the fallback, meaning
keyword search returns `[]` for words that aren't in the catalogue. That
assumption is false for any query that contains a short or common word.

Whole-word matching would fix the pizza query: none of its four words appears
as a whole word in any listing. It wouldn't fix the car-tire query on its own,
because "a" is a real word in 18 descriptions and "to" in 5. That query also
needs filler words like "a" and "to" ignored.

**C5 (MISSED).** All five original criteria were met in all three runs, but
the selected listings differed from unit 4's in all 10 tries of every run.
The criterion 1 query selected `lst_006`, a graphic tee, instead of `lst_021`,
the olive trousers. The empty-wardrobe query selected `lst_007`, a denim
jacket, instead of `lst_004`, a track jacket. **The stage is the query parser,
`agent.py::parse_query`. The fallback isn't involved.** Every trace shows
`search_listings` returning results ("branch: results, continuing") and no
`semantic_search_listings` step, so keyword search picked the new listings.

The mechanism is that the parser fix changed keyword search's input:

- The old parser also read "under $30" as size "30". The size filter is a
  substring test, so only "W30" listings got through, and with the $30 cap
  that left exactly one result: `lst_021`.
- The old parser turned "denim jacket" into "deni jacket" with size M, which
  ranked the track jacket (`lst_004`) first.

With clean input, keyword search now returns the items the queries actually
ask for. The id check was written to catch the fallback firing when it
shouldn't. It assumed the fallback was the only thing that could change the
selected listing. But the two unit 4 listings were themselves products of the
parser bug, so fixing the parser changed them. The target stays as written,
and this counts as a miss.

**C4 (MET, but not 10/10).** The one miss in every run is `denim pants`.
Keyword search returns 7 listings. Five of them tie at the top with a score
of 2, each matching one title word: corduroy pants, cargo pants, a denim
jacket, denim shorts and a denim vest. Corduroy pants (`lst_005`) wins the
tie only because it comes first in the catalogue. The two actual pairs of
jeans score 1.5, because "denim" is only in their style tags and neither
title contains "pants". The result isn't empty, so the fallback never runs. That's the "keyword search is
wrong but not empty" case the capstone left out of scope. Embedding search
alone ranks a pair of jeans first for this query (C1).


---

## The Capstone Improvement

### The pattern

Two of the remaining failures come from the same stage. C3's two misses
(`how to change a car tire`, `pizza delivery near me`) and the one query C4
still gets wrong (`denim pants`) all happen in **keyword search,
`tools.py::search_listings`**. In each case keyword search returns a result
that isn't empty but is built from incidental matches, and the fallback only
runs on an empty result. That's one problem with several symptoms: keyword
search's idea of a match is too loose to serve as the fallback's trigger.

C5's miss has a different cause. It comes from the earlier parser fix, which
changed the listings selected for unit 4's two scenarios, and that change was
intended. No change to search can make C5's id check pass without bringing
the parser bug back. So C5 stays MISSED, and this improvement doesn't target
it.

### What I changed

One change, in `tools.py::search_listings`:

1. **Whole-word matching.** The description check was `keyword in
   desc_text`, a substring test against the whole description string. It now
   compares against the description's words, the same way the title check
   already worked. "me" no longer matches "medium", and "car" no longer
   matches "cardigan".
2. **Filler words are ignored.** Words like "a", "to", "the", "me" and "how"
   are dropped from the query before matching (`_STOPWORDS`). The diagnosis
   showed whole-word matching alone wasn't enough: "a" is a real word in 18
   descriptions and "to" in 5, so the car-tire query would still have matched.

Nothing else changed: same parser, same fallback, same 0.60 floor, same
prompts.

**Which failure it was meant to fix:** C3. The diagnosis named keyword
search as the stage and substring matching as the mechanism, and this
removes that mechanism.

**Checked before spending any model calls:** I ran old and new keyword search
on all 27 queries the evals use. 4 changed:

- C3's two failing queries now return `[]`.
- `graphic tee` and `slip dress` lost a few incidental matches at the bottom
  of their lists. One was a belt that matched "dress" inside "dressed up".
  Their top results didn't change.

Every other query, including all three `run_eval.py` scenarios, returned
exactly the same listings.

### Run log after the improvement

Three separate runs, cache off, 18 November 2026, 02:54–03:08. Produced by
`capstone_runlog.py --out capstone_runs_after_fix`. Raw output for each run is
in `results/capstone_runs_after_fix/run1`–`run3`, and the scored table is in
`results/capstone_runs_after_fix/RUN_LOG.md`.

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| C1. Embedding hit@3 ≥ 12/15, beats keyword on plurals/synonyms, ties on exact | ≥ 12 of 15 | 15/15 (keyword 5/15) | 15/15 (keyword 5/15) | 15/15 (keyword 5/15) | MET |
| C2. Recorded strategy matches whether keyword search was empty | 10 of 10 | 10/10 | 10/10 | 10/10 | MET |
| C3. Unseen off-topic queries return 0 listings and make 0 model calls | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |
| C4. Plural/synonym queries typed into the agent select a labelled listing | ≥ 8 of 10 | 9/10 | 9/10 | 9/10 | MET |
| C5. Original criteria 1–5 all MET, and `lst_021`/`lst_004` selected in 10 of 10 tries | 5/5 MET; ids 10/10 | 5/5 MET; ids 0/10 | 5/5 MET; ids 0/10 | 5/5 MET; ids 0/10 | MISSED |

**Real output from run 1:** `results/capstone_runs_after_fix/run1/c2_c3_c4_stdout.txt`.
The trace is from `agent.py::run_agent` (via `trace.py::step`); the `C3 …` and
`C2 …` lines are printed by `eval_capstone.py::main`. Here is the car-tire
query that failed in every earlier run. Keyword search now returns `[]`, the
fallback runs, the floor turns the query away, and the run stops before
`suggest_outfit`:

```
[1] parse_query
      in:  how to change a car tire
      out: {'description': 'how to change a car tire', 'size': None, 'max_price': None}
[2] search_listings (via MCP)
      in:  {'description': 'how to change a car tire', 'size': None, 'max_price': None}
      out: [] (empty)
      →    branch: empty, trying embedding search
[3] semantic_search_listings (via MCP)
      in:  {'description': 'how to change a car tire', 'size': None, 'max_price': None}
      out: [] (empty)
      →    branch: empty, stopping
  C3 'how to change a car tire': direct 0 listings, agent no_results with 0 calls → PASS
```

```
  C3 'airline ticket refund': direct 0 listings, agent no_results with 0 calls → PASS
  C3 'how to change a car tire': direct 0 listings, agent no_results with 0 calls → PASS
  C3 'python list comprehension': direct 0 listings, agent no_results with 0 calls → PASS
  C3 'pizza delivery near me': direct 0 listings, agent no_results with 0 calls → PASS
  C3 'mortgage interest rates': direct 0 listings, agent no_results with 0 calls → PASS
C2 10/10   C3 5/5   C4 9/10
```

Before this change, the same query returned 10 listings at step [2] and the
agent styled a knit cardigan with 2 model calls (see the C3 trace under
**Real output from run 1** above).

### Did it help, and how do I know

**Yes, for the failure it was aimed at.** C3 went from 3/5 in every run to
5/5 in every run, which moves it from MISSED to MET. The two queries that
failed before now stop at the fallback with 0 model calls in all three runs.
Each of them used to cost 2 model calls and showed an unrelated listing.

**Nothing else moved.** C1, C2 and C4 scored exactly what they scored before,
and C5 still met all five original criteria in every try. That matches the
offline check: the change only affected incidental matches, and no query's
top result changed.

**What it didn't fix:**

- **C4's `denim pants` still misses in every run.** Both of its words
  genuinely appear in listings, so whole-word matching changes nothing for
  it. Five listings tie at the top with one title-word match each, and
  corduroy pants wins the tie by catalogue order. Fixing that means changing
  how keyword search ranks, or letting the fallback run when keyword results
  are weak rather than empty. That's the "wrong but not empty" case the
  capstone left out of scope.
- **C5 stays MISSED** for the reason given above. It meets every original
  target, but its id check is tied to listings the parser bug produced.

That leaves 4 of 5 capstone criteria MET. C4 is the loosest of them: it met
its target of 8 of 10 with a 9/10 that never moved across six runs. If I
tightened one, it would be C4, to 10 of 10. That would turn the `denim pants`
miss from accepted into required, and it can't pass until keyword search's
ranking changes.


---

## What's Still Broken — Capstone

**C5 is the one criterion still missed.** In every run it meets all five
original criteria. It misses on its listing-id check, which expects unit 4's
`lst_021` and `lst_004`; the agent now selects `lst_006` and `lst_007`.

- **What I'd do:** revise the criterion. Following the course's rule, I'd add
  the revision underneath and leave the original line as it is. The revised
  check would be what the id test was meant to catch: in both scenarios the
  trace has no `semantic_search_listings` step, and the selected listing is
  keyword search's first result.
- **Why I stopped:** this miss isn't a defect I can fix in the code. The only
  change that would bring back `lst_021` and `lst_004` is putting the parser
  bug back. I left the revision undone because the course treats a revision
  as earning credit only when a criterion is broken, meaning it can't be
  measured. This one can be measured; it just measures something that stopped
  being meaningful once the parser was fixed. That call belongs to the grader,
  not to me lowering my own target, so the miss stays recorded.

**C4 is met, but `denim pants` fails in every run (9/10 against a target of
8).**

- **What I'd do:** let the fallback run when keyword results are weak, not
  only when they're empty. For example, run it when the top keyword score
  matches only one query word. For this query, five listings tie on a single
  title word and corduroy pants wins by catalogue order, while embedding
  search alone ranks a pair of jeans first (C1).
- **Why I stopped:** it's the case I ruled out of scope before building: "I'm
  not replacing keyword search or blending the two." Changing when the
  fallback fires would change C2's branch rule and every keyword-search result
  the original criteria depend on. It needs its own criteria and its own
  before-and-after run, not a fix squeezed in at the end.

**The target I'd tighten:** C4, from 8 of 10 to **10 of 10**. It scored 9/10
in all six runs, so the current target never tests the one miss it contains.
At 10 of 10, `denim pants` stops being an accepted miss and becomes a
requirement.

**What I'd do next:** if this were real and I had another unit, I'd first make
the fallback trigger on weak keyword results instead of only empty ones,
because `denim pants` is the one failure left where a user gets a confident
fit card for the wrong item with nothing on screen to show it's wrong. Every
other failure the criteria found now either stops with a message or picks the
right listing, so that silent wrong answer is the most expensive thing still
in the system.

---

## Instrumentation

**What gets logged.** Every agent run writes one JSON record through
`runlog.py::logged_run`, which the CLI (`app.py`), the web server (`serve.py`)
and `measure_cost.py` all call instead of calling `run_agent` directly. If
`run_agent` raises, the record is written with `status: "error"` and the
exception text before the exception is re-raised, so a crash still leaves a
record. Requests the server refuses before the agent runs (no query, a query
over 300 characters, over the 5-per-minute visitor limit) are logged by
`runlog.py::log_rejected` with `status: "rejected"` and a `reason`.

Records go to `logs/runs.jsonl`, one per line. The server also prints each one
to stdout, because Render wipes its disk on restart but keeps stdout in its
Logs tab.

| Field | What it is |
|---|---|
| `timestamp`, `run_id` | UTC time the run started; 8-character id to find it again |
| `source` | `cli`, `http` (the site/API) or `measure` |
| `status` | `ok`, `no_results` (both searches empty, stopped before `suggest_outfit`), `model_error` (item found, model unreachable), `error` (crash), `rejected` |
| `input` | the query and how many wardrobe items came with it |
| `parsed` | what the query parser pulled out. This is how the parser bug shows up in the log (`"size": "30"` from a price) |
| `search_strategy`, `results_count` | `keyword`, or `embedding` when the capstone fallback ran, and how many listings came back |
| `output` | selected item (id, title, price, platform), fit card, outfit length, error message |
| `duration_s`, `rate_limit_wait_s` | wall-clock seconds, and how much of that was spent waiting on the request limiter |
| `model_calls`, `cache_hits`, `prompt_tokens`, `output_tokens` | generation requests actually sent, answers served from cache, tokens the service reported |
| `embedding_requests`, `mcp_calls` | query embeddings sent (1 when the fallback ran) and MCP tool calls (1 or 2) |
| `exception` | `Type: message` when `status` is `error` |

**Ten runs.** These are the 10 cost-measurement runs (`python measure_cost.py`,
cache off), followed by three runs through the web server's API: two finished
searches, one of which used the embedding fallback (`tees`), and one
impossible query that stopped early.

```
{"timestamp": "2026-11-18T05:15:27+00:00", "run_id": "4f690276", "source": "measure", "status": "ok", "input": {"query": "vintage graphic tee under $30", "wardrobe_items": 10}, "parsed": {"description": "vintage graphic tee", "size": "30", "max_price": 30.0}, "search_strategy": "keyword", "results_count": 1, "output": {"selected_item": {"id": "lst_021", "title": "Straight Leg Khaki Trousers — Olive", "price": 29.0, "platform": "poshmark"}, "fit_card": "[lst_021 · $29.0]\nObsessed with these straight-leg olive trousers I just scored on Poshmark for only $29 in mint condition! The color is the ultimate neutral, and they give off the best vintage workwear vibes. Can't wait to style them with a cropped hoodie and combat boots or keep it casual with an oversized crewneck.", "outfit_chars": 1683, "error": null}, "duration_s": 3.71, "rate_limit_wait_s": 0.0, "model_calls": 2, "cache_hits": 0, "prompt_tokens": 640, "output_tokens": 426, "embedding_requests": 0, "mcp_calls": 1, "model": "gemini-3.5-flash-lite", "exception": null}
{"timestamp": "2026-11-18T05:15:31+00:00", "run_id": "cc58aa34", "source": "measure", "status": "ok", "input": {"query": "vintage graphic tee under $30", "wardrobe_items": 10}, "parsed": {"description": "vintage graphic tee", "size": "30", "max_price": 30.0}, "search_strategy": "keyword", "results_count": 1, "output": {"selected_item": {"id": "lst_021", "title": "Straight Leg Khaki Trousers — Olive", "price": 29.0, "platform": "poshmark"}, "fit_card": "[lst_021 · $29.0]\nScored these olive straight-leg trousers in pristine condition on Poshmark for just $29, and I’m already obsessed with the earthy, vintage fit. Thinking I’ll keep it casual with a ribbed tank and chunky sneakers today, but they're going to look so good styled with a distressed black denim jacket and combat boots, too. Nothing beats finding a staple piece that feels this effortless! 🫒✨", "outfit_chars": 1129, "error": null}, "duration_s": 2.51, "rate_limit_wait_s": 0.0, "model_calls": 2, "cache_hits": 0, "prompt_tokens": 534, "output_tokens": 342, "embedding_requests": 0, "mcp_calls": 1, "model": "gemini-3.5-flash-lite", "exception": null}
{"timestamp": "2026-11-18T05:15:33+00:00", "run_id": "1e6a2e9c", "source": "measure", "status": "ok", "input": {"query": "vintage graphic tee under $30", "wardrobe_items": 10}, "parsed": {"description": "vintage graphic tee", "size": "30", "max_price": 30.0}, "search_strategy": "keyword", "results_count": 1, "output": {"selected_item": {"id": "lst_021", "title": "Straight Leg Khaki Trousers — Olive", "price": 29.0, "platform": "poshmark"}, "fit_card": "[lst_021 · $29.0]\nScored these straight-leg olive trousers in amazing condition for just $29 on Poshmark, and I’m already obsessed with the color. They have the absolute best vintage utility vibe and fit like a dream. Can’t wait to style them with a white tank and a black denim jacket, or just keep it cozy with an oversized grey crewneck and combat boots!", "outfit_chars": 1590, "error": null}, "duration_s": 3.63, "rate_limit_wait_s": 0.0, "model_calls": 2, "cache_hits": 0, "prompt_tokens": 608, "output_tokens": 404, "embedding_requests": 0, "mcp_calls": 1, "model": "gemini-3.5-flash-lite", "exception": null}
{"timestamp": "2026-11-18T05:15:37+00:00", "run_id": "27bd6b77", "source": "measure", "status": "ok", "input": {"query": "vintage graphic tee under $30", "wardrobe_items": 10}, "parsed": {"description": "vintage graphic tee", "size": "30", "max_price": 30.0}, "search_strategy": "keyword", "results_count": 1, "output": {"selected_item": {"id": "lst_021", "title": "Straight Leg Khaki Trousers — Olive", "price": 29.0, "platform": "poshmark"}, "fit_card": "[lst_021 · $29.0]\nObsessed with these straight-leg olive trousers I just scored on Poshmark for only $29! The color is the ultimate earthy neutral, and the condition is literally spotless. I’m already planning to style them two ways: either dressed down with a ribbed white tank and a vintage black denim jacket for 90s minimalism, or thrown on with an oversized grey crewneck and combat boots for that effortless utility vibe. ✨", "outfit_chars": 1722, "error": null}, "duration_s": 2.87, "rate_limit_wait_s": 0.0, "model_calls": 2, "cache_hits": 0, "prompt_tokens": 652, "output_tokens": 459, "embedding_requests": 0, "mcp_calls": 1, "model": "gemini-3.5-flash-lite", "exception": null}
{"timestamp": "2026-11-18T05:15:40+00:00", "run_id": "75bd3c40", "source": "measure", "status": "ok", "input": {"query": "vintage graphic tee under $30", "wardrobe_items": 10}, "parsed": {"description": "vintage graphic tee", "size": "30", "max_price": 30.0}, "search_strategy": "keyword", "results_count": 1, "output": {"selected_item": {"id": "lst_021", "title": "Straight Leg Khaki Trousers — Olive", "price": 29.0, "platform": "poshmark"}, "fit_card": "[lst_021 · $29.0]\nScored these olive straight-leg trousers in pristine condition on Poshmark for just $29, and I’m already obsessed with the vintage earth-tone vibe. I’m thinking they’ll look so good with an oversized crewneck and combat boots, or dressed down with a simple white tank and chunky sneakers. Such a good minimalist staple for autumn! 🫒✨", "outfit_chars": 1140, "error": null}, "duration_s": 2.07, "rate_limit_wait_s": 0.0, "model_calls": 2, "cache_hits": 0, "prompt_tokens": 540, "output_tokens": 339, "embedding_requests": 0, "mcp_calls": 1, "model": "gemini-3.5-flash-lite", "exception": null}
{"timestamp": "2026-11-18T05:15:42+00:00", "run_id": "8fd42522", "source": "measure", "status": "ok", "input": {"query": "vintage graphic tee under $30", "wardrobe_items": 10}, "parsed": {"description": "vintage graphic tee", "size": "30", "max_price": 30.0}, "search_strategy": "keyword", "results_count": 1, "output": {"selected_item": {"id": "lst_021", "title": "Straight Leg Khaki Trousers — Olive", "price": 29.0, "platform": "poshmark"}, "fit_card": "[lst_021 · $29.0]\nScored these gorgeous olive straight-leg trousers in pristine condition on Poshmark for just $29, and I’m already obsessed with the color. They have the coolest vintage utility vibe and fit like a dream. Can’t wait to style them with everything from chunky white sneakers to my favorite combat boots! 🫒✨", "outfit_chars": 1076, "error": null}, "duration_s": 2.46, "rate_limit_wait_s": 0.0, "model_calls": 2, "cache_hits": 0, "prompt_tokens": 518, "output_tokens": 307, "embedding_requests": 0, "mcp_calls": 1, "model": "gemini-3.5-flash-lite", "exception": null}
{"timestamp": "2026-11-18T05:15:44+00:00", "run_id": "5fd1913a", "source": "measure", "status": "ok", "input": {"query": "vintage graphic tee under $30", "wardrobe_items": 10}, "parsed": {"description": "vintage graphic tee", "size": "30", "max_price": 30.0}, "search_strategy": "keyword", "results_count": 1, "output": {"selected_item": {"id": "lst_021", "title": "Straight Leg Khaki Trousers — Olive", "price": 29.0, "platform": "poshmark"}, "fit_card": "[lst_021 · $29.0]\nScored these straight-leg olive trousers in pristine condition for just $29 on Poshmark, and they are officially my new daily uniform. Obsessed with the structured fit and that perfect, earthy 90s wash. Thinking of styling them with a crisp white tank and vintage denim, or leaning into the cozy slouch with an oversized grey crewneck and combat boots!", "outfit_chars": 1800, "error": null}, "duration_s": 2.63, "rate_limit_wait_s": 0.0, "model_calls": 2, "cache_hits": 0, "prompt_tokens": 680, "output_tokens": 475, "embedding_requests": 0, "mcp_calls": 1, "model": "gemini-3.5-flash-lite", "exception": null}
{"timestamp": "2026-11-18T05:15:47+00:00", "run_id": "e5cfc545", "source": "measure", "status": "ok", "input": {"query": "vintage graphic tee under $30", "wardrobe_items": 10}, "parsed": {"description": "vintage graphic tee", "size": "30", "max_price": 30.0}, "search_strategy": "keyword", "results_count": 1, "output": {"selected_item": {"id": "lst_021", "title": "Straight Leg Khaki Trousers — Olive", "price": 29.0, "platform": "poshmark"}, "fit_card": "[lst_021 · $29.0]\nScored these pristine olive straight-leg trousers on Poshmark for just $29 and I’m officially obsessed with the color. They have that perfect 90s slouch and look insanely good paired with a white ribbed tank and a vintage black denim jacket. Can't wait to style these on heavy rotation! 🫒✨", "outfit_chars": 1413, "error": null}, "duration_s": 42.49, "rate_limit_wait_s": 39.24, "model_calls": 2, "cache_hits": 0, "prompt_tokens": 599, "output_tokens": 389, "embedding_requests": 0, "mcp_calls": 1, "model": "gemini-3.5-flash-lite", "exception": null}
{"timestamp": "2026-11-18T05:16:29+00:00", "run_id": "e4510ad3", "source": "measure", "status": "ok", "input": {"query": "vintage graphic tee under $30", "wardrobe_items": 10}, "parsed": {"description": "vintage graphic tee", "size": "30", "max_price": 30.0}, "search_strategy": "keyword", "results_count": 1, "output": {"selected_item": {"id": "lst_021", "title": "Straight Leg Khaki Trousers — Olive", "price": 29.0, "platform": "poshmark"}, "fit_card": "[lst_021 · $29.0]\nScored these straight-leg olive trousers in mint condition for just $29 on Poshmark, and they are officially my new favorite earth-toned staple. I'm already planning to style them with a white tank and chunky sneakers for casual off-duty days, or lean into a grunge vibe with an oversized grey crewneck and combat boots. Such a versatile vintage find! 🫒✨", "outfit_chars": 1653, "error": null}, "duration_s": 3.44, "rate_limit_wait_s": 0.0, "model_calls": 2, "cache_hits": 0, "prompt_tokens": 640, "output_tokens": 442, "embedding_requests": 0, "mcp_calls": 1, "model": "gemini-3.5-flash-lite", "exception": null}
{"timestamp": "2026-11-18T05:16:33+00:00", "run_id": "e5d2f32f", "source": "measure", "status": "ok", "input": {"query": "vintage graphic tee under $30", "wardrobe_items": 10}, "parsed": {"description": "vintage graphic tee", "size": "30", "max_price": 30.0}, "search_strategy": "keyword", "results_count": 1, "output": {"selected_item": {"id": "lst_021", "title": "Straight Leg Khaki Trousers — Olive", "price": 29.0, "platform": "poshmark"}, "fit_card": "[lst_021 · $29.0]\nScored these olive straight-leg trousers in pristine condition on Poshmark for just $29, and I’m already obsessed with the rich earth tone. They have that perfect vintage minimalist fit that looks just as good with a simple white tank and sneakers as they do dressed down with an oversized crewneck. Sustainable style really does hit different! 🌱✨", "outfit_chars": 1655, "error": null}, "duration_s": 3.22, "rate_limit_wait_s": 0.0, "model_calls": 2, "cache_hits": 0, "prompt_tokens": 636, "output_tokens": 427, "embedding_requests": 0, "mcp_calls": 1, "model": "gemini-3.5-flash-lite", "exception": null}
{"timestamp": "2026-11-18T05:16:56+00:00", "run_id": "dd8ee1fe", "source": "http", "status": "ok", "input": {"query": "chelsea boots", "wardrobe_items": 10}, "parsed": {"description": "cheea boot", "size": "L", "max_price": null}, "search_strategy": "keyword", "results_count": 1, "output": {"selected_item": {"id": "lst_006", "title": "Graphic Tee — 2003 Tour Bootleg Style", "price": 24.0, "platform": "depop"}, "fit_card": "[lst_006 · $24.0]\nScored the ultimate 2003 tour bootleg tee for just $24 on Depop and I’m honestly obsessed with the vintage grunge fade on this graphic. Tossed it on with baggy dark denim and a black jacket for the easiest off-duty streetwear fit, but it looks just as good tucked into wide-leg trousers with combat boots. Tap the link in bio to shop the look before I change my mind and keep it for myself! 🖤✨", "outfit_chars": 1085, "error": null}, "duration_s": 5.47, "rate_limit_wait_s": 0.0, "model_calls": 2, "cache_hits": 0, "prompt_tokens": 545, "output_tokens": 352, "embedding_requests": 0, "mcp_calls": 1, "model": "gemini-3.5-flash-lite", "exception": null}
{"timestamp": "2026-11-18T05:17:02+00:00", "run_id": "f9a7ca12", "source": "http", "status": "ok", "input": {"query": "tees", "wardrobe_items": 0}, "parsed": {"description": "tee", "size": "S", "max_price": null}, "search_strategy": "keyword", "results_count": 2, "output": {"selected_item": {"id": "lst_002", "title": "Y2K Baby Tee — Butterfly Print", "price": 18.0, "platform": "depop"}, "fit_card": "[lst_002 · $18.0]\nScored this absolute dream of a Y2K butterfly baby tee in mint condition and I'm obsessed! 🦋 It’s the ultimate versatile anchor piece for anyone building their wardrobe from scratch—you can style it super nostalgic with cargos or lean into a soft indie-streetwear vibe. Snagging this gem for just $18 over on my Depop before I keep it for myself! ✨🛒", "outfit_chars": 2089, "error": null}, "duration_s": 5.25, "rate_limit_wait_s": 0.0, "model_calls": 2, "cache_hits": 0, "prompt_tokens": 702, "output_tokens": 594, "embedding_requests": 0, "mcp_calls": 1, "model": "gemini-3.5-flash-lite", "exception": null}
{"timestamp": "2026-11-18T05:17:07+00:00", "run_id": "f8ccb033", "source": "http", "status": "no_results", "input": {"query": "designer ballgown size XXS under $5", "wardrobe_items": 10}, "parsed": {"description": "deigner bagown", "size": "S", "max_price": 5.0}, "search_strategy": "embedding", "results_count": 0, "output": {"selected_item": null, "fit_card": null, "outfit_chars": 0, "error": "No items found matching 'deigner bagown' under $5.0 in size S. Neither keyword nor meaning-based search found a match. Try different keywords, a higher price, or removing size filters."}, "duration_s": 0.94, "rate_limit_wait_s": 0.0, "model_calls": 0, "cache_hits": 0, "prompt_tokens": 0, "output_tokens": 0, "embedding_requests": 1, "mcp_calls": 2, "model": "gemini-3.5-flash-lite", "exception": null}
```

**Failed runs.** All three are from the same server session:

1. **Rejected input:** a request with no `query`, which got HTTP 400.
2. **Rejected input:** a sixth search inside a minute from one visitor, which
   got HTTP 429. The five before it are in the full log.
3. **Model error:** a search with the server started on an invalid
   `GEMINI_API_KEY`. Search still worked, because the MCP server process read
   the real key from `.env`. The run found an item, then the model call
   failed, and the agent stopped with a message instead of crashing.

```
{"timestamp": "2026-11-18T05:17:07+00:00", "run_id": "d97807d4", "source": "http", "status": "rejected", "reason": "no query in request body", "input": {"query": null}, "client": "14915055", "duration_s": 0.0, "model_calls": 0, "exception": null}
{"timestamp": "2026-11-18T05:17:12+00:00", "run_id": "76a6372e", "source": "http", "status": "rejected", "reason": "visitor limit: 5 searches per 60s", "input": {"query": "designer ballgown size XXS under $5"}, "client": "fec52565", "duration_s": 0.0, "model_calls": 0, "exception": null}
{"timestamp": "2026-11-18T05:17:14+00:00", "run_id": "c4452261", "source": "http", "status": "model_error", "input": {"query": "cargo pants under $40", "wardrobe_items": 10}, "parsed": {"description": "cargo pant", "size": "S", "max_price": 40.0}, "search_strategy": "embedding", "results_count": 2, "output": {"selected_item": {"id": "lst_008", "title": "Knit Cardigan — Chunky Brown", "price": 35.0, "platform": "depop"}, "fit_card": null, "outfit_chars": 0, "error": "Found Knit Cardigan — Chunky Brown ($35.0 on depop), but couldn't reach the model to style it: The model rejected your API key. Check GEMINI_API_KEY in your .env file, or create a fresh key at aistudio.google.com. Fix that and ask again."}, "duration_s": 1.32, "rate_limit_wait_s": 0.0, "model_calls": 1, "cache_hits": 0, "prompt_tokens": 0, "output_tokens": 0, "embedding_requests": 1, "mcp_calls": 2, "model": "gemini-3.5-flash-lite", "exception": null}
```

The full session, all 20 records unedited, is committed in
`results/runlog_2026-11-18_session.md`.

---

## What It Costs

**The real cost is quota and seconds, not dollars.** FitFindr runs on Gemini's
free tier, so the actual API spend is $0. What runs out is requests: the free
tier allows 15 generation requests a minute for `gemini-3.5-flash-lite`, and
that is the limit that makes runs wait.

**One complete run costs, on average:**

| | Per run (mean of 10) |
|---|---|
| Generation requests | **2** (`suggest_outfit` + `create_fit_card`), every run |
| Tokens | **1,006** (605 prompt + 401 output; output varied ±56 between runs) |
| Seconds of active work | **3.0 s** |
| Wall-clock seconds | **6.9 s**, including 3.9 s average rate-limit wait |
| Embedding requests | **0** on this query; **+1** when keyword search is empty and the fallback runs |

So one key supports at most **7 complete runs a minute** (15 ÷ 2), and the
eighth waits. That happened in this measurement: run 8 waited 39 s, which is
why the wall-clock mean (6.9 s, standard deviation 12.5 s) is much higher than
the active time (3.0 s). Runs that stop early cost much less. The five
impossible queries in the server log made 0 generation requests and took
about 0.9 s each.

**How I measured it.** `python measure_cost.py` ran the criterion 1 query
(`vintage graphic tee under $30`, example wardrobe) 10 times in a row, with
the response cache off so every run sent real requests. Each run went through
`runlog.logged_run`, which takes the request and token counters from
`generate.py` before and after the run and records the difference. Token
counts are the ones the Gemini API reports in `usage_metadata`; seconds are
`time.perf_counter()` around `run_agent`; the wait time is what `generate.py`'s
rate limiter actually slept. The script averages those fields over the 10
records. Averages and raw records: `results/cost_2026-11-18_0016.md`.

**What the numbers leave out:**

- **Embedding tokens.** A query embedding is sent from inside the MCP server
  process, so its tokens aren't in `prompt_tokens`. A query is a few words, so
  it's negligible next to about 1,000 generation tokens.
- **The embedding index build.** It happens once per server start (one
  request covering all 40 listings) and is then cached, so it's not a per-run
  cost.
- **Render's free tier.** It's $0 too. Its cost is the roughly one-minute
  wake-up after 15 idle minutes, which isn't part of any single run.
- **Thinking tokens.** Google bills a model's thinking tokens as output. My
  output count is `candidates_token_count`, which leaves out any thinking
  tokens, so if the model used any, the real output cost is higher than shown.
- **The capstone fixes.** I measured this on 18 November, before the parser
  and keyword-search fixes. A complete run still makes exactly 2 generation
  calls, but the selected item is now different, so the token counts per run
  may shift slightly.

**For a hundred people a day:** if 100 people each run one complete search a
day, FitFindr would cost about **$0.12 a day (about $3.55 a month)** at
Gemini's paid standard rate, and it would fit within the free tier's 15
requests a minute as long as no more than 7 searches arrive in the same
minute.

The arithmetic. Rates are from Google's Gemini API pricing page, checked 18
November 2026: `gemini-3.5-flash-lite` costs $0.30 per 1M input tokens and
$2.50 per 1M output tokens.

```
one run, input:   604.7 tokens × $0.30 / 1,000,000  = $0.0001814
one run, output:  401.0 tokens × $2.50 / 1,000,000  = $0.0010025
one run, total:                                       $0.0011839

100 runs a day:   100 × $0.0011839                  = $0.1184 a day
30 days:          30  × $0.1184                     = $3.55 a month
365 days:         365 × $0.1184                     = $43.21 a year

requests:         100 runs × 2 generation calls     = 200 a day
tokens:           100 × (604.7 + 401.0)             = 100,570 a day
active compute:   100 × 3.0 s                       = 300 s, about 5 minutes a day
```

Output is 85% of the cost ($0.0010025 of $0.0011839 per run), even though it's
fewer tokens than the input, because output tokens cost about 8 times as much.
The outfit suggestion is the longest output, so its length is what to cut if
cost ever mattered. The assumption that matters most is "one search each": at
three searches per person, every figure above triples, to $0.36 a day.

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**

