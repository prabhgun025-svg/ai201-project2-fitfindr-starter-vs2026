"""
The FitFindr planning loop.

This is the file that makes FitFindr an agent rather than a script. It decides
which tool to run next based on what the last one returned.

If your loop calls all three tools no matter what comes back, you have a list
of function calls. A loop looks at the last result before it picks the next
step. **That branch is the graded part of this unit.**

Build and test your three tools in `tools.py` first. Then come here.

    python agent.py          runs both example paths below
"""

import config
import trace
from tools import suggest_outfit, create_fit_card
from mcp_client import call_tool, MCPError
from generate import ModelUnavailable


# ── session state ─────────────────────────────────────────────────────────────

def new_session(query: str, wardrobe: dict) -> dict:
    """
    A fresh session for one user interaction.

    The session is the single source of truth for a run. Every tool result goes
    in here, and the next tool reads it back out.

    You could pass values straight from one call to the next. It would work,
    and you would not be able to test it — you can't print a variable you have
    already overwritten. Going through the session is what makes the state
    visible, and unit 4 has you write a criterion about exactly that.

    Add fields if you need them.
    """
    return {
        "query": query,              # what the user typed
        "parsed": {},                # description / size / max_price you pulled out of it
        "search_results": [],        # everything search_listings returned
        "search_strategy": None,     # "keyword", or "embedding" if the fallback ran
        "selected_item": None,       # the one you chose — goes into suggest_outfit
        "wardrobe": wardrobe,        # the user's wardrobe
        "outfit_suggestion": None,   # what suggest_outfit returned
        "fit_card": None,            # what create_fit_card returned
        "error": None,               # set when the run ended early
    }


# ── planning loop ─────────────────────────────────────────────────────────────

def run_agent(query: str, wardrobe: dict) -> dict:
    """
    Run the loop once and return the finished session.

    Args:
        query:    what the user asked for, in plain language
                  (e.g. "vintage graphic tee under $30, size M").
        wardrobe: a wardrobe dict — get_example_wardrobe() or
                  get_empty_wardrobe() from utils/data_loader.py.

    Returns:
        The session dict. **Check session["error"] first** — if it isn't None,
        the run ended early and the later fields will still be None.

    ─────────────────────────────────────────────────────────────────────────
    TODO — build this, following the branch rule you wrote in Milestone 2.

      1. Start a session with new_session().

      2. Count the times round the loop, and call trace.check_iterations(count)
         on each one before you go again. It raises when the count passes
         MAX_ITERATIONS in config.py — see trace.py.

      3. Parse the query into a description, a size, and a max_price. Regex,
         string splitting, or asking the model are all fine — say which you
         chose in your README. Put the result in session["parsed"].

      4. Call search_listings() with what you parsed.
         Put the results in session["search_results"].

         ⚠️ THIS IS THE BRANCH. If nothing came back:
              - put a message in session["error"] saying what the user could
                change — "No results" is not that message
              - return the session
              - do NOT call suggest_outfit with nothing

      5. Choose an item — the first result is fine. Put it in
         session["selected_item"].

      6. Call suggest_outfit() with the selected item and the wardrobe.
         Put the result in session["outfit_suggestion"].

      7. Call create_fit_card() with the outfit and the item.
         Put the result in session["fit_card"].

      8. Return the session.

    ─────────────────────────────────────────────────────────────────────────
    IN UNIT 4 you come back and add two things:

      • Trace calls. One per step. `trace.step("search_listings", inputs=...,
        returned=...)` — see trace.py. Your README needs the output.

      • A handler for ModelUnavailable, so a bad key produces a message rather
        than a stack trace. The import is already at the top of this file.
    """
    session = new_session(query, wardrobe)
    
    # Parse the query using regex to extract price and size
    import re
    
    description = query
    max_price = None
    size = None
    
    # Extract price: look for "under $X" or "$X" or "under X"
    price_match = re.search(r'(?:under\s+)?(?:\$)?(\d+(?:\.\d+)?)', query, re.IGNORECASE)
    if price_match:
        max_price = float(price_match.group(1))
        description = re.sub(r'(?:under\s+)?(?:\$)?\d+(?:\.\d+)?', '', description, flags=re.IGNORECASE)
    
    # Extract size: look for "size X" or common size abbreviations
    size_match = re.search(r'(?:size\s+)?([XS]+|M|L|XL|XXL|\d+)', query, re.IGNORECASE)
    if size_match:
        size = size_match.group(1).upper()
        description = re.sub(r'(?:size\s+)?([XS]+|M|L|XL|XXL|\d+)', '', description, flags=re.IGNORECASE)
    
    # Clean up description
    description = description.replace(',', ' ').strip()
    
    session["parsed"] = {
        "description": description,
        "size": size,
        "max_price": max_price,
    }
    trace.step("parse_query", inputs=query, returned=str(session["parsed"]))
    
    # Call search_listings over MCP
    search_results = call_tool("search_listings", {
        "description": description,
        "size": size,
        "max_price": max_price,
    })
    session["search_results"] = search_results
    session["search_strategy"] = "keyword"
    fallback_note = None

    # CAPSTONE BRANCH: keyword search found nothing, so try embedding search
    # with the same filters before giving up. Keyword stays the default; this
    # only runs on an empty result.
    if not search_results:
        trace.step("search_listings (via MCP)", inputs=str(session["parsed"]),
                   returned=search_results, note="branch: empty, trying embedding search")
        try:
            search_results = call_tool("semantic_search_listings", {
                "description": description,
                "size": size,
                "max_price": max_price,
            }) or []
        except MCPError as exc:
            # Embedding model unreachable: treat as no results rather than crash.
            search_results = []
            fallback_note = f"embedding search failed ({str(exc).splitlines()[0]})"
        session["search_results"] = search_results
        session["search_strategy"] = "embedding"
        if search_results:
            trace.step("semantic_search_listings (via MCP)", inputs=str(session["parsed"]),
                       returned=search_results, note="branch: results, continuing")
        else:
            trace.step("semantic_search_listings (via MCP)", inputs=str(session["parsed"]),
                       returned=fallback_note or search_results, note="branch: empty, stopping")

    # BRANCH: If both searches return an empty list, stop
    if not search_results:
        why = (f"Keyword search found nothing and the meaning-based search couldn't run: {fallback_note}."
               if fallback_note else "Neither keyword nor meaning-based search found a match.")
        session["error"] = f"No items found matching '{description}'" + (f" under ${max_price}" if max_price else "") + (f" in size {size}" if size else "") + f". {why} Try different keywords, a higher price, or removing size filters."
        return session
    if session["search_strategy"] == "keyword":
        trace.step("search_listings (via MCP)", inputs=str(session["parsed"]),
                   returned=search_results, note="branch: results, continuing")
    
    # Choose the first result and store in session
    selected_item = search_results[0]
    session["selected_item"] = selected_item
    trace.step("select_item", inputs=f"{len(search_results)} results",
               returned=selected_item, note="first result")
    
    try:
        # Call suggest_outfit with the selected item from session
        item_from_session = session["selected_item"]
        outfit_suggestion = suggest_outfit(item_from_session, wardrobe)
        session["outfit_suggestion"] = outfit_suggestion
        trace.step("suggest_outfit",
                   inputs=f"new_item={item_from_session.get('id')} {item_from_session.get('title')!r} "
                          f"(${item_from_session.get('price')}), "
                          f"wardrobe={len(wardrobe.get('items', []))} items",
                   returned=outfit_suggestion)
        
        # Call create_fit_card, reading outfit from session
        outfit_from_session = session["outfit_suggestion"]
        item_for_card = session["selected_item"]
        fit_card = create_fit_card(outfit_from_session, item_for_card)
        session["fit_card"] = fit_card
        trace.step("create_fit_card",
                   inputs=f"new_item={item_for_card.get('id')} {item_for_card.get('title')!r} "
                          f"(${item_for_card.get('price')}), outfit=<suggest_outfit text>",
                   returned=fit_card)
    except ModelUnavailable as exc:
        # Keep the search result in the session; only the model steps failed.
        session["error"] = (
            f"Found {selected_item.get('title')} (${selected_item.get('price')} on "
            f"{selected_item.get('platform')}), but couldn't reach the model to style it: {exc} "
            f"Fix that and ask again."
        )
        trace.step("model call failed", returned=str(exc), note="ModelUnavailable, stopping")
        return session
    
    return session


# ── running it directly ───────────────────────────────────────────────────────

def _show(session: dict) -> None:
    if session["error"]:
        print(f"  stopped: {session['error']}")
        print(f"  fit_card is {session['fit_card']!r} — it should still be None here")
        return

    item = session["selected_item"] or {}
    print(f"  found:    {item.get('title')} — ${item.get('price')} on {item.get('platform')}")
    print(f"  outfit:   {session['outfit_suggestion']}")
    print(f"  fit card: {session['fit_card']}")


if __name__ == "__main__":
    from utils.data_loader import get_example_wardrobe

    print("=== A query the data can match ===")
    _show(run_agent(
        query="looking for a vintage graphic tee under $30",
        wardrobe=get_example_wardrobe(),
    ))

    print("\n=== A query it can't ===")
    _show(run_agent(
        query="designer ballgown size XXS under $5",
        wardrobe=get_example_wardrobe(),
    ))

    print(
        "\nThe second one should stop before the fit card. If both paths look "
        "the same,\nthe branch isn't doing anything yet."
    )
