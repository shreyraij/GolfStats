# GolfStats

A golf dashboard covering every player in the top 200 of the Official World Golf Ranking (OWGR).
Rankings and bios are table stakes — the goal is a second layer of stats that mainstream golf
sites (PGA Tour, ESPN, OWGR) don't publish.

## Status

Early planning stage. No code yet — see [CLAUDE.md](./CLAUDE.md) for the full architecture plan
and build order. Data sources for the metrics below have not been chosen yet; that's the first
thing to nail down before any implementation starts.

## What makes this different

Most golf sites stop at scoring average, driving distance, and strokes gained. This project adds
metrics built from hole-by-hole, condition-by-condition data:

- **Course/conditions fit** — does a player's game suit specific course setups, e.g. tight/narrow
  fairways, heavy bunkering, small greens?
- **Weather performance** — scoring average in wind vs. calm, and rain vs. dry.
- **Clutch factor** — how well a player protects a lead over the closing holes (back nine or
  final round), compared to their own baseline.
- **Consistency / volatility** — players who make a lot of birdies but also a lot of bogeys, so
  their finish position doesn't reflect how aggressive their game actually is.

These definitions are a starting point and will keep evolving as the underlying data is scoped
out.

## Planned stack

- **Frontend**: React + Vite + TypeScript
- **Backend**: Python, a separate service exposing an API, doing the numerical/statistical work
  the metrics above need
- **Data source**: not yet decided — see CLAUDE.md

## Build order

1. Find and validate data sources against the specific metrics above (not just "does an API
   exist," but "does it have the granularity this needs").
2. Set up the data pipeline and a normalized internal schema.
3. Build the backend metric computations.
4. Build the frontend.

## Contributing / working in this repo

See [CLAUDE.md](./CLAUDE.md) for architecture guidance and working conventions if you're using
Claude Code in this repository.
