"""Birdie/bogey volatility: players who make a lot of birdies but also a lot
of bogeys, so their scoring average or finish position doesn't reflect how
many birdies they actually made.
"""

from __future__ import annotations

from app.models.schemas import PlayerProfile

MIN_ROUNDS_FOR_RELIABLE_RESULT = 10


def compute_consistency(profile: PlayerProfile) -> dict:
    rounds_with_data = [r for r in profile.rounds if r.hole_outcomes is not None]

    birdies = sum(r.hole_outcomes.birdies_or_better for r in rounds_with_data)
    pars = sum(r.hole_outcomes.pars for r in rounds_with_data)
    bogeys_or_worse = sum(r.hole_outcomes.bogeys_or_worse for r in rounds_with_data)
    total_holes = birdies + pars + bogeys_or_worse

    if total_holes == 0:
        return {
            "player_id": profile.player_id,
            "rounds_counted": 0,
            "total_holes": 0,
            "birdie_rate": None,
            "bogey_or_worse_rate": None,
            "volatility_score": None,
            "reliable": False,
        }

    birdie_rate = birdies / total_holes
    bogey_rate = bogeys_or_worse / total_holes

    # High birdie_rate AND high bogey_rate together is the "fireworks but no
    # consistency" profile this dashboard wants to surface.
    volatility_score = birdie_rate + bogey_rate

    return {
        "player_id": profile.player_id,
        "rounds_counted": len(rounds_with_data),
        "total_holes": total_holes,
        "birdie_rate": round(birdie_rate, 4),
        "bogey_or_worse_rate": round(bogey_rate, 4),
        "volatility_score": round(volatility_score, 4),
        "reliable": len(rounds_with_data) >= MIN_ROUNDS_FOR_RELIABLE_RESULT,
    }
