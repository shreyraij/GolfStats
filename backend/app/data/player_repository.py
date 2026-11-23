"""Assembles a full PlayerProfile from DataGolf event data.

NOT YET IMPLEMENTED: DataGolf's historical-raw-data/rounds endpoint is
scoped per tournament (tour + event_id + year), not per player, so building
one player's full history means iterating their event schedule and
filtering rows by player_id. That iteration/caching strategy hasn't been
designed yet, and can't really be tested without a live DATAGOLF_API_KEY to
check the real response shapes against.

Returns an empty profile for now so the API and metrics stay callable
end-to-end — the metrics already handle empty data correctly (they report
`reliable: false` rather than erroring), so this stub doesn't need special
handling upstream once the real implementation lands.
"""

from __future__ import annotations

from app.models.schemas import PlayerProfile


def get_player_profile(player_id: str, player_name: str = "", world_rank: int = 0) -> PlayerProfile:
    return PlayerProfile(player_id=player_id, name=player_name, world_rank=world_rank, rounds=[])
