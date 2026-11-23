"""DataGolf adapter. Requires a Scratch Plus API key in the DATAGOLF_API_KEY
env var (get one at https://datagolf.com/api-access after subscribing).

Covers two things:
  - Top-200 OWGR rankings, via get-dg-rankings (this also replaces a
    separate OWGR scraper — see CLAUDE.md "Data sources" for why).
  - Round-level scoring / strokes-gained / hole-level birdie-bogey counts,
    via the historical raw data feed.

This module only translates DataGolf's response shape into our normalized
schema (app.models.schemas); nothing outside this file should know what
DataGolf's JSON looks like.
"""

from __future__ import annotations

import os

import httpx

from app.models.schemas import CourseInfo, HoleOutcomeCounts, RankingEntry, RoundResult

BASE_URL = "https://feeds.datagolf.com"
DEFAULT_TIMEOUT = 30.0


class DataGolfConfigError(RuntimeError):
    pass


def _get_api_key() -> str:
    api_key = os.environ.get("DATAGOLF_API_KEY")
    if not api_key:
        raise DataGolfConfigError(
            "DATAGOLF_API_KEY is not set. Subscribe at https://datagolf.com/subscribe, "
            "grab a key from https://datagolf.com/api-access, and set it in the environment."
        )
    return api_key


def get_top_owgr_rankings(limit: int = 200) -> list[RankingEntry]:
    """Top-N players by OWGR rank, sourced from DataGolf's DG rankings feed
    (which carries each player's OWGR rank as a field alongside DG's own).
    """
    api_key = _get_api_key()

    response = httpx.get(
        f"{BASE_URL}/preds/get-dg-rankings",
        params={"file_format": "json", "key": api_key},
        timeout=DEFAULT_TIMEOUT,
    )
    response.raise_for_status()
    payload = response.json()

    rankings = payload["rankings"] if isinstance(payload, dict) and "rankings" in payload else payload

    entries = [
        RankingEntry(
            owgr_rank=row["owgr_rank"],
            player_id=str(row["dg_id"]),
            player_name=row["player_name"],
        )
        for row in rankings
        if row.get("owgr_rank") is not None
    ]
    entries.sort(key=lambda e: e.owgr_rank)
    return entries[:limit]


def get_historical_rounds(tour: str, event_id: str, year: int) -> list[RoundResult]:
    """Round-level scoring + hole-outcome counts for one event.

    NOTE: DataGolf's docs describe hole-level birdie/par/bogey counts being
    present in this feed but don't publish exact field names in the prose
    documentation. The field names below (`birdies`, `pars`, `bogeys`) are
    a best guess based on DataGolf's snake_case convention elsewhere in the
    raw data feed — verify against a live response once DATAGOLF_API_KEY is
    set, and fix the mapping below if the actual keys differ.
    """
    api_key = _get_api_key()

    response = httpx.get(
        f"{BASE_URL}/historical-raw-data/rounds",
        params={"tour": tour, "event_id": event_id, "year": year, "file_format": "json", "key": api_key},
        timeout=DEFAULT_TIMEOUT,
    )
    response.raise_for_status()
    payload = response.json()
    rows = payload["scores"] if isinstance(payload, dict) and "scores" in payload else payload

    results = []
    for row in rows:
        hole_outcomes = None
        if all(k in row for k in ("birdies", "pars", "bogeys")):
            hole_outcomes = HoleOutcomeCounts(
                birdies_or_better=row["birdies"],
                pars=row["pars"],
                bogeys_or_worse=row["bogeys"],
            )

        results.append(
            RoundResult(
                tournament_id=str(event_id),
                round_number=row["round"],
                round_date=str(row.get("teetime", "")),
                course=CourseInfo(
                    course_id=str(row.get("course_num", row.get("course_name", "unknown"))),
                    course_name=row.get("course_name", "unknown"),
                ),
                round_score_to_par=row["round_score"] - row["course_par"],
                hole_outcomes=hole_outcomes,
            )
        )
    return results
