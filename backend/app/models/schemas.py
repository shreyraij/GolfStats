"""Normalized internal schema. Every data source adapter (DataGolf,
Open-Meteo) maps its own response shape into these models; metrics code
only ever reads these, never a source's raw response.
"""

from __future__ import annotations

from pydantic import BaseModel


class RankingEntry(BaseModel):
    owgr_rank: int
    player_id: str
    player_name: str
    # DataGolf's rankings endpoint doesn't document a country field; leave
    # unset until a supplementary source is picked, rather than fake it.
    country: str | None = None


class Player(BaseModel):
    player_id: str
    name: str
    country: str | None = None
    world_rank: int


class HoleOutcomeCounts(BaseModel):
    """Aggregate hole outcomes for one round. This is what DataGolf's
    hole-level feed actually provides (counts, not a per-hole sequence) for
    PGA/European/Korn Ferry/LIV tours — sufficient for the consistency
    metric without needing hole-by-hole granularity.
    """

    birdies_or_better: int
    pars: int
    bogeys_or_worse: int

    @property
    def total_holes(self) -> int:
        return self.birdies_or_better + self.pars + self.bogeys_or_worse


class CourseInfo(BaseModel):
    course_id: str
    course_name: str
    latitude: float | None = None
    longitude: float | None = None


class RoundConditions(BaseModel):
    wind_speed_mph: float | None = None
    precipitation: bool | None = None
    temperature_f: float | None = None


class RoundResult(BaseModel):
    tournament_id: str
    round_number: int
    round_date: str
    course: CourseInfo
    round_score_to_par: int
    hole_outcomes: HoleOutcomeCounts | None = None
    conditions: RoundConditions | None = None


class PlayerProfile(Player):
    rounds: list[RoundResult] = []
