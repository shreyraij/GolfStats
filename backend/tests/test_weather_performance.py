from app.metrics.weather_performance import compute_weather_performance
from app.models.schemas import CourseInfo, PlayerProfile, RoundConditions, RoundResult

COURSE = CourseInfo(course_id="c1", course_name="Test Course")


def make_round(score_to_par, wind_speed_mph=None, precipitation=None):
    return RoundResult(
        tournament_id="t1",
        round_number=1,
        round_date="2025-01-01",
        course=COURSE,
        round_score_to_par=score_to_par,
        conditions=RoundConditions(wind_speed_mph=wind_speed_mph, precipitation=precipitation),
    )


def test_no_conditions_data_returns_none():
    profile = PlayerProfile(player_id="p1", name="Test Player", world_rank=1, rounds=[])
    result = compute_weather_performance(profile)
    assert result["avg_score_to_par_windy"] is None
    assert result["avg_score_to_par_calm"] is None


def test_splits_windy_vs_calm_correctly():
    rounds = [
        make_round(score_to_par=2, wind_speed_mph=20),
        make_round(score_to_par=4, wind_speed_mph=25),
        make_round(score_to_par=-1, wind_speed_mph=5),
        make_round(score_to_par=-2, wind_speed_mph=8),
    ]
    profile = PlayerProfile(player_id="p1", name="Test Player", world_rank=1, rounds=rounds)
    result = compute_weather_performance(profile)

    assert result["avg_score_to_par_windy"] == 3.0
    assert result["avg_score_to_par_calm"] == -1.5
    assert result["wind_rounds_sample_size"] == 2


def test_splits_rain_vs_dry_correctly():
    rounds = [
        make_round(score_to_par=3, precipitation=True),
        make_round(score_to_par=1, precipitation=True),
        make_round(score_to_par=-2, precipitation=False),
    ]
    profile = PlayerProfile(player_id="p1", name="Test Player", world_rank=1, rounds=rounds)
    result = compute_weather_performance(profile)

    assert result["avg_score_to_par_rain"] == 2.0
    assert result["avg_score_to_par_dry"] == -2.0
