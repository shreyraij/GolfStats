"""The one place that decides where data comes from.

API routes call `get_data_source()` and use the returned object's
`get_rankings()` / `get_player_profile()`; they never import a provider
module directly. Both implementations return the normalized schema
(app.models.schemas), so metrics code can't tell them apart.

  - DATAGOLF_API_KEY set   -> DataGolfSource (live; app/data/datagolf.py,
                              unchanged, plus player_repository.py)
  - DATAGOLF_API_KEY unset -> SampleDataSource (fictional fixture in
                              app/data/sample_data.json)

The env var is read per request rather than at import time, so tests can
flip modes with monkeypatch and the server never caches a stale choice.
"""

from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Literal, Protocol

from app.data import datagolf, player_repository
from app.models.schemas import CourseInfo, HoleOutcomeCounts, PlayerProfile, RankingEntry, RoundConditions, RoundResult

DataSourceName = Literal["sample", "datagolf"]

SAMPLE_DATA_PATH = Path(__file__).with_name("sample_data.json")


class DataSource(Protocol):
    name: DataSourceName

    def get_rankings(self, limit: int = 200) -> list[RankingEntry]: ...

    def get_player_profile(self, player_id: str) -> PlayerProfile: ...


class DataGolfSource:
    name: DataSourceName = "datagolf"

    def get_rankings(self, limit: int = 200) -> list[RankingEntry]:
        return datagolf.get_top_owgr_rankings(limit=limit)

    def get_player_profile(self, player_id: str) -> PlayerProfile:
        return player_repository.get_player_profile(player_id)


class SampleDataSource:
    """Serves the fictional fixture. Unknown player IDs get an empty profile,
    matching the live path's behaviour (metrics then report `reliable: false`).
    """

    name: DataSourceName = "sample"

    def get_rankings(self, limit: int = 200) -> list[RankingEntry]:
        return _load_sample_data()[0][:limit]

    def get_player_profile(self, player_id: str) -> PlayerProfile:
        profiles = _load_sample_data()[1]
        if player_id in profiles:
            return profiles[player_id]
        return PlayerProfile(player_id=player_id, name="", world_rank=0, rounds=[])


@lru_cache(maxsize=1)
def _load_sample_data() -> tuple[list[RankingEntry], dict[str, PlayerProfile]]:
    raw = json.loads(SAMPLE_DATA_PATH.read_text())

    round_info: dict[tuple[str, int], tuple[dict, dict]] = {}
    for event in raw["tournaments"]:
        for rnd in event["rounds"]:
            round_info[(event["tournament_id"], rnd["round_number"])] = (event, rnd)

    rankings: list[RankingEntry] = []
    profiles: dict[str, PlayerProfile] = {}
    for player in raw["players"]:
        rankings.append(
            RankingEntry(
                owgr_rank=player["owgr_rank"],
                player_id=player["player_id"],
                player_name=player["player_name"],
                country=player.get("country"),
            )
        )

        rounds = []
        for r in player["rounds"]:
            event, rnd = round_info[(r["tournament_id"], r["round_number"])]
            rounds.append(
                RoundResult(
                    tournament_id=event["tournament_id"],
                    round_number=rnd["round_number"],
                    round_date=rnd["round_date"],
                    course=CourseInfo(course_id=event["course_id"], course_name=event["course_name"]),
                    round_score_to_par=r["score_to_par"],
                    hole_outcomes=HoleOutcomeCounts(
                        birdies_or_better=r["birdies_or_better"],
                        pars=r["pars"],
                        bogeys_or_worse=r["bogeys_or_worse"],
                    ),
                    conditions=RoundConditions(
                        wind_speed_mph=rnd["wind_speed_mph"],
                        precipitation=rnd["precipitation"],
                        temperature_f=rnd["temperature_f"],
                    ),
                )
            )

        profiles[player["player_id"]] = PlayerProfile(
            player_id=player["player_id"],
            name=player["player_name"],
            country=player.get("country"),
            world_rank=player["owgr_rank"],
            rounds=rounds,
        )

    rankings.sort(key=lambda e: e.owgr_rank)
    return rankings, profiles


def get_data_source() -> DataSource:
    if os.environ.get("DATAGOLF_API_KEY"):
        return DataGolfSource()
    return SampleDataSource()
