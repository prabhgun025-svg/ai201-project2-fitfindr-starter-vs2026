# Running FitFindr

Everything about how the starter works and how to use it.

---

## Deployment

FitFindr runs on **Render** (free web service): a web page at `/`, and the
JSON API behind it at `/ask`.

| | |
|---|---|
| **Live URL** | `https://<your-service>.onrender.com` ← *fill in after the first deploy* |
| **Platform** | Render, free plan (512 MB RAM, sleeps after ~15 min idle) |
| **Config** | [`render.yaml`](render.yaml) in the repo root |
| **Build command** | `pip install -r requirements.txt` |
| **Start command** | `gunicorn serve:app --timeout 120` |
| **Health check** | `GET /health` → `{"status":"ok"}` |

### Try it

Open the URL in a browser: type what you're looking for, or click one of the
example queries. The page shows the listing found, the fit card, the outfit
suggestions, and what the agent understood from the query.

The first request after the service has been idle takes about a minute while
Render wakes it up. After that, a request takes a few seconds. Each visitor
gets 5 searches a minute (`FITFINDR_VISITOR_LIMIT`); more get HTTP 429 with a
"try again in N seconds" message, because every search spends the same API key.

The same thing from a terminal:

```bash
curl https://<your-service>.onrender.com/health

curl -X POST https://<your-service>.onrender.com/ask \
  -H 'Content-Type: application/json' \
  -d '{"query": "vintage graphic tee under $30"}'
```

`/ask` returns the agent's session as JSON. Check `error` first: if it isn't
`null`, the run stopped early and says why. Otherwise read `selected_item`,
`outfit_suggestion` and `fit_card`. `search_strategy` is `"keyword"`, or
`"embedding"` when keyword search came back empty and the embedding fallback
ran. Sending no `query` returns HTTP 400 with an example of the right body.

### How it got there

1. Pushed this repo to GitHub.
2. In the Render dashboard: **New → Blueprint**, then connected the repo. Render
   reads `render.yaml` and creates one web service named `fitfindr`.
3. When prompted, pasted the Gemini key as the value of `GEMINI_API_KEY`. It
   is stored as a Render secret and is never committed.
4. Render runs the build command, then the start command, and waits for
   `/health` to answer before sending traffic.
5. Every later push to the default branch redeploys automatically.

Why the start command is exactly `gunicorn serve:app --timeout 120`:

- **Sync worker (gunicorn's default).** Not `-k gevent`, `-k eventlet` or
  uvicorn. `mcp_client.call_tool` uses `asyncio.run()`, which can't start
  inside a running event loop, so an async worker breaks every MCP call.
- **`--timeout 120`.** gunicorn kills a worker after 30 s by default. A request
  that hits the model's rate limiter (15 requests a minute on the free tier)
  can wait up to 60 s, so the default would kill it partway through.
- **No `--bind`.** gunicorn listens on `0.0.0.0:$PORT` when the host sets
  `PORT`, and Render does.

### What the environment needs

| Need | Value |
|---|---|
| Python | **3.13.0** (tested). 3.11 or 3.12 also work. **Not 3.14**: several pinned packages don't support it. Render's version is pinned with `PYTHON_VERSION` in `render.yaml` |
| Dependencies | [`requirements.txt`](requirements.txt), pinned with lower and upper bounds. Versions resolved and tested: `Flask 3.1.3`, `google-genai 1.75.0`, `gunicorn 23.0.0`, `mcp 1.30.0`, `python-dotenv 1.1.1`. About 74 MB installed |
| Secrets | `GEMINI_API_KEY`: a Google AI Studio key. Locally it goes in `.env`; on Render it's a dashboard secret |
| Model files | **None.** Generation (`gemini-3.5-flash-lite`) and embeddings (`gemini-embedding-001`) both run on Google's API. Nothing is downloaded |
| Disk | The embedding index for the 40 listings is built on first use and cached in `.cache/` (1.6 MB, gitignored). Render's disk is wiped on every deploy and restart, so the first embedding search after a restart rebuilds it. That costs one extra API request, not a failure |
| Memory | Fits in 512 MB because `serve.py` handles one request at a time. Each MCP call starts a second Python process, and two at once wouldn't fit |

Optional settings: `AI201_CACHE=0` turns off response caching;
`AI201_MODEL` and `AI201_EMBEDDING_MODEL` change the models;
`FITFINDR_VISITOR_LIMIT` changes the per-visitor searches per minute (default 5).

### Logs

Every run writes one JSON record, including runs that stop early and runs
that crash. Requests the server refuses (no query, a query over 300
characters, over the visitor limit) are logged too, with status `rejected`.

- **Where:** `logs/runs.jsonl`, one record per line (gitignored). The server
  also prints each record to stdout prefixed `[runlog]`, which is where to read
  them on Render (**Logs** tab), since Render's disk is wiped on restart.
- **Fields:** listed at the top of [`runlog.py`](runlog.py). They include
  timestamp, input, status, output, duration, rate-limit wait, model calls,
  tokens, search strategy and exception.
- **Cost:** `python measure_cost.py` runs the agent 10 times with the cache
  off and writes the averages and raw records to `results/cost_*.md`.

### Running the same thing locally

From a clean checkout:

```bash
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env              # paste your key into .env
python test.py                    # should end "10 passed, 0 failed"
gunicorn serve:app --timeout 120  # the host's exact command; listens on :8000
# or: python serve.py             # Flask's dev server, listens on :5000
```

These steps were tested in a fresh copy of the repo (only the files git tracks,
no `.venv`, no `.cache`) with a new virtual environment. All 10 checks in
`test.py` passed, and the embedding index was built from scratch on the first
query. `gunicorn serve:app --timeout 120` was also run locally and checked:

- `/health` answered.
- `/ask` with `"purse"` went through the embedding fallback and returned a
  fit card.
- `/ask` with an impossible query stopped with an error message.
- `/ask` with an empty body returned HTTP 400.

### Known limitation you'll see on the live URL

The regex query parser in `agent.py::run_agent` treats any S, M, L or XL letter
in the query, and any number, as a size. "purse" is searched as size S, and
"graphic tee under $30" as size 30. Many queries therefore search with the
wrong size and a garbled description. The README's **Failure Modes** and
**What's Still Broken** sections cover this. It's a parsing bug, not a
deployment problem: the same query gives the same result locally.

---

## Before your first class

Setup happens **before class**. The [environment setup page](../pages/ide_setup)
has the per-operating-system commands and the exact versions.

**Same API key you set up in unit 1.** Nothing new to sign up for. There is one
new package — the MCP SDK, for unit 4 — and it installs with everything else.

From inside this repo after you've forked and cloned it:

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # then paste your key into .env
python test.py
```

**Windows (PowerShell)**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env         # then paste your key into .env
python test.py
```

**You're ready when `python test.py` passes.**

If it doesn't and you've made one honest attempt at the error, post the
**whole** output in the help channel.

> Activate the virtual environment every time you open a new terminal. You
> should see `(.venv)` at the start of your prompt.

---

## Your first five minutes

Start with the data. Your tools will only be as good as your understanding of
what they're reading, and ten minutes here saves an hour of confused debugging.

```bash
python app.py fields                    # what a listing and a wardrobe item hold
python app.py listings --full -n 6      # read six listings all the way through
python app.py examples                  # queries worth trying
python app.py ask 'vintage graphic tee under $30'
```

> **Quote your queries with single quotes**, on every operating system. In
> PowerShell, `"vintage graphic tee under $30"` in double quotes silently
> becomes `vintage graphic tee under ` — PowerShell reads `$30` as a variable
> and substitutes nothing. You get results with no price ceiling and no error
> saying so. Single quotes are literal in PowerShell, bash and zsh alike.

That last one runs the loop. All three tools are stubs, so it will tell you the
loop isn't built yet. **That's the correct starting position** — it runs, and it
does nothing.

---

## Every command

| Command | What it does |
|---|---|
| `python test.py` | Checks your environment. Run it whenever something feels off |
| `python app.py fields` | The fields a listing and a wardrobe item have — **Milestone 1** |
| `python app.py listings` | Browse the data. `--full` for whole records, `-n` for how many |
| `python app.py examples` | Queries worth trying, including one that matches nothing |
| `python app.py ask '...'` | Run the agent on one query — **single quotes** |
| `python app.py ask` | Keep asking until you press Enter on an empty line |
| `python agent.py` | Runs both example paths — one that matches, one that can't |
| `python mcp_server.py` | Starts your MCP server — **unit 4** |
| `python mcp_client.py` | Asks the server what it offers — **unit 4** |
| `python run_eval.py --label before` | Runs every scenario five times and writes the run log — **unit 4** |
| `python serve.py` | Serves the agent over HTTP instead of exiting — **unit 9** |
| `gunicorn serve:app --timeout 120` | The deployed start command. See **Deployment** at the top |
| `python eval_retrieval.py` | Capstone: hit@3 for keyword vs embedding search on 15 labelled queries |
| `python measure_cost.py` | 10 cache-off runs; averages seconds, requests and tokens per run into `results/` |

Useful flags on `ask`:

| Flag | What it does |
|---|---|
| `--trace` | Print the loop step by step, once you've added the trace calls |
| `--empty-wardrobe` | Run as a user with nothing saved — one of unit 4's failure modes |

---

## Which command goes with which milestone

### Unit 3 — the build

| Milestone | What you're doing | Where |
|---|---|---|
| 1 | Read the data, run the starter | `app.py fields`, `app.py listings --full`, `app.py ask` |
| 2 | Spec your three tools | README, **Tool Inventory** |
| 3 | Write your acceptance criteria | `criteria.md` |
| 4 | Build the three tools | `tools.py`, tested one at a time from a terminal |
| 5 | Wire the loop and the state | `agent.py::run_agent` |
| 6 | Write it up | README |

### Unit 4 — the test

| Milestone | What you're doing | Where |
|---|---|---|
| 1 | Move one tool onto MCP | `mcp_server.py`, then `mcp_client.call_tool` in `run_agent` |
| 2 | Break it on purpose, then trace it | `trace.py`, `app.py ask --trace` |
| 3 | Run your test | `scenarios.py`, then `run_eval.py --label before` |
| 4 | Call each criterion, diagnose the misses | README |
| 5 | Fix one thing and re-run | `run_eval.py --label after` |
| 6 | Say what's still broken | README |

---

## Running it somewhere else — **unit 9**

Everything above exits when the command finishes. A host has nothing to keep
running, so before you can deploy this you need something that stays up.
`serve.py` is that: the same `run_agent()`, behind two HTTP routes.

On your machine:

```bash
python serve.py
curl -X POST http://localhost:5000/ask \
  -H 'Content-Type: application/json' \
  -d '{"query": "vintage graphic tee under $30"}'
```

On a host, the start command is (see **Deployment** at the top for why
`--timeout 120`):

```bash
gunicorn serve:app --timeout 120
```

| Thing | What it means |
|---|---|
| `PORT` | The host tells your app which port to listen on by setting this. Both `serve.py` and `gunicorn` read it, and `serve.py` falls back to `5000` on your machine. Don't hard-code a port |
| `POST /ask` | `{"query": "...", "wardrobe": {...}}` — wardrobe optional. Returns the session dict, `error` and all |
| `GET /health` | Says `ok` if the app is awake |
| It answers one request at a time | On purpose. A second request waits for the first to finish, and prints `[serve] another request is still running` while it waits. An MCP tool call starts a whole second Python process, and the free tier's 512 MB has no room for two of those at once — and `generate.py`'s rate-limit counting assumes one caller. The reasoning is written out in `serve.py` |
| `gunicorn serve:app --timeout 120`, exactly | Not `-k gevent`, not `-k eventlet`, not wrapped for uvicorn. `mcp_client.call_tool` uses `asyncio.run()`, which won't start inside a running event loop, so an async worker breaks **every** MCP call — and only once you've deployed it |
| The first request is slow | The free tier puts your app to sleep after about fifteen minutes of nothing. The next request wakes it up and waits for it — around a minute. Not a bug, and worth knowing before you demo it |

`serve.py` ships with **no logging and no timing in it**, on purpose. You add
that yourself in the follow-along, before you deploy — instrumenting first is
the point of the session.

---

## Where everything lives

| File | What it does |
|---|---|
| `config.py` | Every setting worth changing — **TEMPERATURE and the cache are at the top** |
| `tools.py` | Your three tools. **Stubs — you build these** |
| `agent.py` | The planning loop and the session. **Stub — you build this** |
| `generate.py` | The only thing that calls out to a service. Handles pacing and quota |
| `trace.py` | The trace helper, and the loop's stop condition |
| `app.py` | The command line |
| `serve.py` | The same agent over HTTP, for deploying — **unit 9** |
| `mcp_server.py` | Your MCP server — **unit 4, you register the tool** |
| `mcp_client.py` | Calling an MCP tool from your agent. Given to you |
| `scenarios.py` | What your test runs. **You fill this in** |
| `run_eval.py` | Runs the scenarios repeatedly and writes the run log |
| `criteria.md` | Your five acceptance criteria. **You fill this in** |
| `retrieval_queries.py` | Capstone: 15 labelled queries for the retrieval eval |
| `eval_retrieval.py` | Capstone: hit@3 for keyword vs embedding search, written to `results/` |
| `render.yaml` | Render deploy config: build and start commands, Python version, the secret it needs |
| `static/index.html` | The web page served at `/` |
| `runlog.py` | One JSON record per run, written to `logs/runs.jsonl` |
| `measure_cost.py` | Measures the average cost of one run |
| `data/` | 40 listings and the wardrobe schema |
| `utils/data_loader.py` | Loading the data. Use this rather than reading the files yourself |
| `results/` | Run logs. **Commit these** — they're your evidence |

---

## The two settings people go looking for

Both are at the top of `config.py`, and the brief points at them by name.

If your fit cards come out **word-for-word identical** every time, it is one of:

- **`CACHE_ENABLED`** — while you build, identical prompts reuse the answer
  already received. That's deliberate; it makes debugging free. `run_eval.py`
  turns it off automatically.
- **`TEMPERATURE`** — at `0.0` the model gives you the same words every time.
  It ships at `0.9`.

---

## About rate limits

**This is the heaviest pair in the course for call volume.** Two of your three
tools call the model, so one agent run is several requests, and a few runs back
to back while debugging can cross the per-minute limit.

`generate.py` handles it:

- **It paces itself** and says when it's waiting. **A pause is the starter
  doing its job, not a bug.**
- **It reuses answers** to prompts already sent, while you build.
- **It stops** if a session makes an unreasonable number of calls, rather than
  draining your day's allowance. For an agent, that usually means a loop isn't
  ending — look for that before raising the number.
- **It counts your calls** and prints the total when you exit.

`config.MAX_ITERATIONS` is the loop's own stop condition. Your loop this unit
is short enough that you may never hit it. Keep it — a missing stop condition
is the most common architectural failure in production agents.

---

## When something goes wrong

| What you see | What it means |
|---|---|
| `The planning loop isn't built yet` | Correct, at the start. That's the TODO in `agent.py` |
| `No GEMINI_API_KEY found` | No `.env`, or the key wasn't pasted in. On Windows check it didn't save as `.env.txt` |
| A message saying the model couldn't be reached | Usually a bad key. This is also **exactly what unit 4 Milestone 2 asks you to trigger on purpose** |
| `[rate limit] ... Waiting 34s` | Working as intended. Leave it |
| `[serve] another request is still running` | Also working as intended. `serve.py` answers one request at a time; yours is queued behind one that's mid-run |
| `QuotaGuard: This session has made 300 requests` | A loop isn't ending. Find it before raising the budget |
| `The loop ran 11 times, past MAX_ITERATIONS` | Same thing, caught earlier |
| `The server doesn't offer a tool called '...'` | Nothing registered in `mcp_server.py` yet, or the name doesn't match |
| MCP returns a string where you expected a list | You're not going through `mcp_client.call_tool`, which unwraps it |
| Fit cards identical every run | `CACHE_ENABLED` or `TEMPERATURE`. See above |
| `--trace` prints nothing | You haven't added `trace.step()` calls yet — unit 4, Milestone 2 |
| `IncompleteFieldDefinitionWarning: Field 'lifespan'` | Harmless noise from the MCP library's dependencies. Not your code, not an error. Ignore it |
| A price ceiling you typed is being ignored | You used double quotes in PowerShell. `$30` vanished. Use single quotes |
| `UnicodeEncodeError: 'charmap' codec can't encode` | Shouldn't happen — `config.py` sets the console to UTF-8. If you see it, you're running a file that doesn't import `config` |

Still stuck after one honest attempt? Post in the help channel with the full
error, what you ran, and what you expected.

---

## A note on committing

At least four new commits in unit 3, at least four more in unit 4. Your commit
history is what shows your criteria existed before your results did.

**Do not delete and recreate this repository.** You submit the same URL both
units.

`results/` is deliberately **not** in `.gitignore`.
