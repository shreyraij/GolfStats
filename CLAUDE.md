# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project status

Phase 1 scaffold is built and working end-to-end (backend API + frontend, verified in-browser):
rankings list → player profile page with Consistency and Weather Performance tabs (real, backed by
adapters) plus Clutch Factor and Course Fit tabs (placeholder, phase 2). The one missing piece to
get real data flowing is a `DATAGOLF_API_KEY` — see "Commands" below. Player-profile data assembly
(`backend/app/data/player_repository.py`) is still a stub returning empty profiles; see that file's
docstring for why and what's needed to finish it.

## What this project is

A golf dashboard covering every player in the top 200 of the Official World Golf Ranking. Each player
has a profile page. Rankings and basic bios are table-stakes; the point of the project is the
**second layer of stats that mainstream golf sites (PGA Tour, ESPN, OWGR) don't surface** — see
"Core metrics" below.

## Build order (important — do not skip ahead)

**Data sources first, frontend last.** The whole point of this project is metrics that mainstream
golf sites don't publish (course fit, weather performance, clutch factor, consistency/volatility —
see "Core metrics" below). None of that is buildable without first confirming where the underlying
data actually comes from at the granularity needed (hole-by-hole scores, per-round weather/wind,
course attributes like fairway width and bunker counts, situational data like who was leading
entering the back nine). Do not scaffold or build the frontend before this is settled.

Order of work:
1. ~~Research and evaluate data sources against the specific stats in "Core metrics".~~ Done —
   see "Data sources" below. Phase 1 metrics (consistency, weather performance) have sources
   lined up; phase 2 metrics (clutch factor, course fit) are deferred pending more data work.
2. ~~Set up the data source(s)/pipeline for phase 1~~ Done — `backend/app/data/{datagolf,open_meteo}.py`
   plus the normalized schema in `backend/app/models/schemas.py`.
3. ~~Build the backend metrics computations for phase 1~~ Done — `backend/app/metrics/{consistency,weather_performance}.py`,
   both tested (`backend/tests/`). Not yet tested against *real* DataGolf data (no key set yet) —
   only against hand-built fixtures, so field-mapping bugs in `datagolf.py` are still possible.
4. ~~Build the frontend~~ Done — rankings list + player profile page with one tab per metric,
   verified working end-to-end in a browser against the local backend.
5. Remaining: get a live `DATAGOLF_API_KEY` set and re-verify `datagolf.py`'s field mappings
   against real responses (see "Commands" and the note in that file — some field names, like the
   hole-outcome-count keys, were a best guess from docs prose, not a confirmed live response).
   Then build out `player_repository.py`'s real profile-assembly logic (see its docstring).

## Working conventions

**Ask before assuming.** If a requirement, data source, metric definition, or design choice is
unclear or ambiguous, ask the user rather than guessing and proceeding. This project has a lot of
still-evolving ideas (see "Core metrics"); confirm intent before committing to an interpretation,
especially for anything that would be expensive to redo (choice of data provider, schema design,
a metric's precise definition).

## Tech stack (decided)

- **Frontend**: React + Vite + TypeScript. Talks to the backend over HTTP.
- **Backend**: Python, separate service exposing a REST (or GraphQL) API. Python was chosen
  specifically because the metrics below need real numerical/statistical computation
  (pandas/numpy-style work) over raw round- and hole-level data, not just CRUD.
- These are two separate deployable apps (e.g. `frontend/` and `backend/`), not a monorepo
  framework like Next.js — keep the data-computation layer decoupled from the UI layer.

## Data sources (decided, phase 1)

Researched against the specific metrics (not just "does an API exist") — no single source covers
everything, so this is a composite:

- **Rankings (top 200 OWGR)**: **not** scraped from owgr.com — that site is a client-rendered
  Next.js app with no discoverable public JSON API (checked: not in the SSR payload, not in the
  Next.js data route, not found by grepping the JS bundles for an API host). A real scraper would
  need a headless browser (Playwright), which was more than this needed. Instead, use DataGolf's
  `get-dg-rankings` endpoint (`backend/app/data/datagolf.py::get_top_owgr_rankings`), which
  returns each player's OWGR rank directly, via the same subscription/auth as everything else
  below. One gap: that endpoint's documented fields don't include player country — `Player.country`
  and `RankingEntry.country` are `str | None` in the schema for this reason; backfill from a
  supplementary source later if a country column is wanted.
- **Round scoring, strokes gained, hole-level birdie/par/bogey counts**: [DataGolf API](https://datagolf.com/api-access),
  "Scratch Plus" membership. **Plan matters**: the monthly plan ($30/mo) includes API access but
  not the historical/archive endpoints; the annual plan ($270/yr) is required for those, and the
  round data this app uses (`historical-raw-data/rounds`) likely needs it. Approved as the
  primary paid source. Covers round-level scoring/strokes-gained/driving stats across 22 tours,
  and hole-level birdie/bogey
  counts specifically for PGA/European/Korn Ferry/LIV tours — this is what feeds the
  consistency/volatility metric. **Caveat**: the exact JSON field names for hole-outcome counts
  aren't published in DataGolf's docs prose — `datagolf.py::get_historical_rounds` guesses
  `birdies`/`pars`/`bogeys` based on their snake_case convention elsewhere. Verify against a live
  response once `DATAGOLF_API_KEY` is set and fix the mapping if wrong.
- **Weather (wind/rain)**: no golf-specific source publishes this. Pull tournament dates + course
  coordinates from DataGolf's schedule data, then cross-reference against
  [Open-Meteo's historical weather API](https://open-meteo.com/en/docs/historical-weather-api)
  (free, keyless, hourly wind/precipitation back to 1940) for the relevant location/date/hour.

**Explicitly deferred — do not build against these yet:**

- **Clutch factor** (who was leading entering the back nine/final round) needs true hole-by-hole
  scores for the whole field to reconstruct leaderboard state at any point. DataGolf's hole-level
  data is aggregate counts, not a per-hole sequence with field positions — the real source for
  this would be Sportradar's Golf API, which is enterprise-priced (custom quotes, no public
  pricing, likely $1,000s/month). Decision: defer this metric until the rest of the dashboard
  proves out; do not build a data pipeline for it yet.
- **Course/conditions fit** (fairway width, bunker count, green size) has no ready API — GIS
  providers (iGolf, Golf Intelligence, GolfAPI.io) sell course polygon data for GPS rangefinder
  apps, not ready numeric fields, and licensing terms/cost aren't public. Manual curation for the
  ~50-60 unique PGA Tour courses per season is more practical than licensing a mismatched GIS
  feed, but hasn't started. Decision: defer this metric too.

Do not assume a specific provider's schema when writing the data layer — isolate all
source-specific parsing behind an adapter (e.g. `backend/app/data/`) so a source can be swapped or
added later without touching metrics code. The metrics logic should operate on a normalized
internal schema (player → rounds → holes, with conditions attached to each round), not on a
specific API's response shape — this matters especially because clutch factor and course fit will
need new fields (field-wide hole sequences, course attributes) bolted on later without a rewrite.

## Core metrics (the actual point of the project)

These are the stats that don't exist on mainstream golf sites today. Each should be computed from
normalized hole-by-hole/round-by-round data, not pulled pre-computed from a source, since no
source publishes them.

**Phase 1 (buildable now with decided data sources):**

1. **Consistency / volatility** — players who make a lot of birdies but also a lot of bogeys,
   so their finish position doesn't reflect how aggressive/exciting their game is. Computable
   directly from DataGolf's hole-level birdie/par/bogey counts.
2. **Weather performance** — scoring average in wind vs. calm, and rain vs. dry. Computable by
   joining DataGolf round data with Open-Meteo historical weather for the course
   location/tournament dates.

**Phase 2 (deferred — data sources not yet in place, see "Data sources"):**

3. **Clutch factor** — how well a player protects a lead over the closing stretch (back nine,
   or final round). Compare a player's scoring on those holes when leading vs. their own
   baseline. Blocked on field-wide hole-by-hole data (Sportradar or equivalent) needed to
   reconstruct leaderboard position at a given hole. Note: even once data exists, a first pass
   that ignores the strength of the chasing field is a simplification, not the final definition.
4. **Course/conditions fit** — does a player's game suit specific course setups? E.g.
   performance correlation with tight/narrow fairways, heavy bunkering, small greens, etc.
   Blocked on course attribute data (fairway width, bunker count, green size), which needs
   manual curation — no ready API exists for it.

These metric definitions are a starting point, not final — the user has more ideas in progress.
Expect them to be refined and expect new ones to be added; keep each metric's computation
isolated (one module per metric) so definitions can change independently.

## Architecture guidance for implementation

- Keep source-specific data fetching/parsing, the normalized data model, and metric computation
  in separate layers. The normalized model is the contract between them — metrics code should
  never know which API a stat originally came from.
- Every metric needs a documented sample-size floor before it's shown for a player (e.g. clutch
  factor is meaningless from 2 rounds). Surface sample size alongside the metric value rather
  than hiding small-sample noise.
- Player profile pages are the primary UI surface — rankings list → player profile → the
  advanced metrics for that player. Design the API around fetching one player's full profile
  efficiently, not just listing rankings.
- **One metric, one backend module, one frontend tab.** Each metric in "Core metrics" gets its
  own file under `backend/app/metrics/` (e.g. `consistency.py`, `weather_performance.py`,
  `clutch.py`, `course_fit.py`) and its own dedicated tab/section on the player profile page in
  the frontend, with its own API endpoint. Don't merge metrics into a shared "stats" blob on
  either side — this is what lets metric definitions change independently (per "Core metrics"
  above) and lets phase 2 metrics (clutch, course fit) slot in later as their own tab without
  touching phase 1 code. A phase 2 metric's tab can exist as a "coming soon" placeholder before
  its data source is wired up.

## Commands

**Backend** (from `backend/`):
```
source .venv/bin/activate       # venv already created; recreate with: python3 -m venv .venv
pip install -r requirements.txt
export DATAGOLF_API_KEY=...     # optional: unset = fictional sample data (app/data/source.py);
                                 # set = live DataGolf. Get one at
                                 # https://datagolf.com/subscribe -> https://datagolf.com/api-access
uvicorn app.main:app --reload --port 8000
pytest                          # full suite
pytest tests/test_consistency.py -k test_reliability_floor   # single test
```

**Frontend** (from `frontend/`):
```
npm install
npm run dev        # http://localhost:5173, expects the backend on :8000 (see VITE_API_BASE_URL)
npm run build       # tsc -b && vite build
npx tsc -b          # typecheck only
```

The backend's CORS config (`backend/app/main.py`) only allows `http://localhost:5173` — update it
if the frontend dev port changes.
