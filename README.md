# GolfStats

A golf dashboard covering every player in the top 200 of the Official World Golf Ranking (OWGR).
Rankings and bios are table stakes — the goal is a second layer of stats that mainstream golf
sites (PGA Tour, ESPN, OWGR) don't publish.

## Status

Phase 1 works end-to-end: rankings list, player profile page, and the Consistency / Weather
Performance tabs, backed by a real API. Phase 2 metrics (clutch factor, course fit) are
intentionally deferred and show as "coming soon" tabs.

**It runs on sample data by default.** With no `DATAGOLF_API_KEY` set, the backend serves a
fixture of **fictional** players, events and stats (`backend/app/data/sample_data.json`) so the
whole dashboard works without a paid key. Every API response carries a `data_source` field
(`"sample"` or `"datagolf"`), and the frontend shows a **Sample data** badge whenever it isn't
live. None of the sample players are real — don't read anything into their numbers.

## What makes this different

Most golf sites stop at scoring average, driving distance, and strokes gained. This project adds
metrics built from hole-by-hole, condition-by-condition data:

**Building now:**
- **Consistency / volatility** — players who make a lot of birdies but also a lot of bogeys, so
  their finish position doesn't reflect how aggressive their game actually is.
- **Weather performance** — scoring average in wind vs. calm, and rain vs. dry.

**Deferred to phase 2** (blocked on data sources that are either expensive or need manual work):
- **Clutch factor** — how well a player protects a lead over the closing holes (back nine or
  final round), compared to their own baseline.
- **Course/conditions fit** — does a player's game suit specific course setups, e.g. tight/narrow
  fairways, heavy bunkering, small greens?

These definitions are a starting point and will keep evolving.

## Stack

- **Frontend**: React + Vite + TypeScript (`frontend/`)
- **Backend**: Python + FastAPI (`backend/`), doing the numerical/statistical work the metrics
  above need
- **Data sources**: [DataGolf](https://datagolf.com/api-access) for rankings, scoring,
  strokes-gained, and hole-level stats; [Open-Meteo](https://open-meteo.com/en/docs/historical-weather-api)
  for historical weather — see CLAUDE.md for why, and for what's deferred.

## Build order

1. ~~Find and validate data sources~~ — done, see CLAUDE.md.
2. ~~Set up the data pipeline and a normalized internal schema~~ — done.
3. ~~Build the backend metric computations (phase 1 metrics first)~~ — done, tested.
4. ~~Build the frontend~~ — done, verified in-browser against the local backend.
5. ~~Sample-data mode so the app runs without a key~~ — done.
6. Set a real `DATAGOLF_API_KEY` and verify the adapter's field mappings against live data (some
   field names were best guesses from docs prose — see CLAUDE.md).

## Running it

Prerequisites: Python 3.11+ and Node 20.19+ (required by Vite 8).

**Backend** (FastAPI, port 8000):

```sh
cd backend
python3 -m venv .venv          # first time only
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Frontend** (Vite, port 5173 — expects the backend on :8000; override with `VITE_API_BASE_URL`):

```sh
cd frontend
npm install
npm run dev                    # http://localhost:5173
npm run build                  # typecheck + production build
```

**Tests** (backend):

```sh
cd backend
source .venv/bin/activate
pytest
```

### Live data (optional)

Live rankings and round data come from the [DataGolf API](https://datagolf.com/api-access), which
requires a **paid DataGolf "Scratch Plus" membership**. Pick the plan carefully:

- **Monthly ($30/mo)** includes API access, but **not** the historical/archive endpoints.
- **Annual ($270/yr)** is required for the historical/archive endpoints. The round-level data
  this app uses comes from DataGolf's historical raw data feed, so you will likely need the
  annual plan.

(Prices and plan contents as of this writing; check DataGolf's site before subscribing.) Once
subscribed, copy your key from <https://datagolf.com/api-access> and set it before starting the
backend:

```sh
export DATAGOLF_API_KEY=your-key-here
uvicorn app.main:app --reload --port 8000
```

The backend checks for the key on each request: set means live DataGolf data
(`"data_source": "datagolf"`), unset means sample data. The switch lives in one place,
`backend/app/data/source.py`. Note that live per-player profile assembly is still a stub (see
`backend/app/data/player_repository.py`), so with a key set the metric tabs will show "not enough
data" until that's built.

To change the sample data, edit and re-run `backend/scripts/generate_sample_data.py` (seeded, so
output is reproducible) rather than hand-editing the JSON.

## Contributing / working in this repo

See [CLAUDE.md](./CLAUDE.md) for architecture guidance and working conventions if you're using
Claude Code in this repository.
