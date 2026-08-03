# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project status

This repository is currently empty — no code has been written yet. This file documents the intended
product, architecture, and decisions made so far so that implementation can start from a shared plan
rather than from scratch. Update this file as real structure, commands, and conventions come into
existence; move anything that becomes "obvious from reading the code" out of here.

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
1. Research and evaluate data sources against the specific stats in "Core metrics" — not just
   "does an API exist" but "does it have the granularity this specific metric needs." Confirm
   coverage for all top-200 players.
2. Decide on and set up the data source(s)/pipeline, including how source-specific data gets
   normalized into a common internal schema (see "Architecture guidance").
3. Build the backend metrics computations against real (or realistically shaped) data.
4. Only then build the frontend against a working backend/API.

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

## Data source (open question — resolve before building the data layer)

Not yet decided where rankings, hole-by-hole scoring, weather/conditions per round, and course
attributes (fairway width, bunker counts, etc.) will come from. Options discussed:

- **DataGolf API** (paid) — most likely to have strokes-gained data and the granularity these
  metrics need.
- **PGA Tour / ESPN public stats + scraping** — free but fragile, and shot-level/weather detail
  is limited or absent.
- A source not yet identified.

Do not assume a specific provider's schema when writing the data layer — isolate all
source-specific parsing behind an adapter (e.g. `backend/app/data/`) so the source can be swapped
or combined with others without touching the metrics code. The metrics logic should operate on a
normalized internal schema (player → rounds → holes, with conditions and course attributes
attached to each round), not on a specific API's response shape.

## Core metrics (the actual point of the project)

These are the stats that don't exist on mainstream golf sites today. Each should be computed from
normalized hole-by-hole/round-by-round data, not pulled pre-computed from a source, since no
source publishes them.

1. **Course/conditions fit** — does a player's game suit specific course setups? E.g.
   performance correlation with tight/narrow fairways, heavy bunkering, small greens, etc.
   This needs course attribute data (fairway width, bunker count, green size) joined against a
   player's historical results on that course type. Most data-hungry metric — needs a large
   sample of rounds across many courses before it's meaningful.
2. **Weather performance** — scoring average in wind vs. calm, and rain vs. dry. Needs per-round
   (ideally per-hole) weather/conditions data, which most public sources don't carry.
3. **Clutch factor** — how well a player protects a lead over the closing stretch (back nine,
   or final round). Compare a player's scoring on those holes when leading vs. their own
   baseline. Note: a first pass that ignores the strength of the chasing field is a
   simplification, not the final definition — revisit once there's real data to test against.
4. **Consistency / volatility** — players who make a lot of birdies but also a lot of bogeys,
   so their finish position doesn't reflect how aggressive/exciting their game is. Computable
   directly from hole-by-hole score-to-par once that data exists (birdie rate vs.
   bogey-or-worse rate per round).

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

## Commands

Not yet applicable — no build tooling exists yet. Once scaffolded, this section should list
exact install/dev/build/lint/test commands for both `frontend/` and `backend/`, including how to
run a single test in each.
