"""Scoring performance in wind vs. calm conditions, and rain vs. dry."""

from __future__ import annotations

from statistics import mean

from app.models.schemas import PlayerProfile

WIND_THRESHOLD_MPH = 15.0
MIN_ROUNDS_FOR_RELIABLE_RESULT = 5


def compute_weather_performance(profile: PlayerProfile) -> dict:
    windy_scores = []
    calm_scores = []
    rain_scores = []
    dry_scores = []

    for round_result in profile.rounds:
        conditions = round_result.conditions
        if conditions is None:
            continue

        if conditions.wind_speed_mph is not None:
            bucket = windy_scores if conditions.wind_speed_mph >= WIND_THRESHOLD_MPH else calm_scores
            bucket.append(round_result.round_score_to_par)

        if conditions.precipitation is not None:
            bucket = rain_scores if conditions.precipitation else dry_scores
            bucket.append(round_result.round_score_to_par)

    return {
        "player_id": profile.player_id,
        "avg_score_to_par_windy": round(mean(windy_scores), 2) if windy_scores else None,
        "avg_score_to_par_calm": round(mean(calm_scores), 2) if calm_scores else None,
        "wind_rounds_sample_size": len(windy_scores),
        "wind_result_reliable": len(windy_scores) >= MIN_ROUNDS_FOR_RELIABLE_RESULT,
        "avg_score_to_par_rain": round(mean(rain_scores), 2) if rain_scores else None,
        "avg_score_to_par_dry": round(mean(dry_scores), 2) if dry_scores else None,
        "rain_rounds_sample_size": len(rain_scores),
        "rain_result_reliable": len(rain_scores) >= MIN_ROUNDS_FOR_RELIABLE_RESULT,
    }
