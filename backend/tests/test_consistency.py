from app.metrics.consistency import compute_consistency
from app.models.schemas import CourseInfo, HoleOutcomeCounts, PlayerProfile, RoundResult

COURSE = CourseInfo(course_id="c1", course_name="Test Course")


def make_round(birdies, pars, bogeys):
    return RoundResult(
        tournament_id="t1",
        round_number=1,
        round_date="2025-01-01",
        course=COURSE,
        round_score_to_par=birdies * -1 + bogeys,
        hole_outcomes=HoleOutcomeCounts(birdies_or_better=birdies, pars=pars, bogeys_or_worse=bogeys),
    )


def test_no_rounds_returns_unreliable_none():
    profile = PlayerProfile(player_id="p1", name="Test Player", world_rank=1, rounds=[])
    result = compute_consistency(profile)
    assert result["total_holes"] == 0
    assert result["birdie_rate"] is None
    assert result["reliable"] is False


def test_high_birdie_high_bogey_gives_high_volatility():
    rounds = [make_round(birdies=6, pars=6, bogeys=6) for _ in range(3)]
    profile = PlayerProfile(player_id="p1", name="Test Player", world_rank=1, rounds=rounds)
    result = compute_consistency(profile)

    assert result["total_holes"] == 54
    assert result["birdie_rate"] == round(18 / 54, 4)
    assert result["bogey_or_worse_rate"] == round(18 / 54, 4)
    assert result["volatility_score"] == round(18 / 54 + 18 / 54, 4)


def test_reliability_floor():
    rounds = [make_round(birdies=1, pars=16, bogeys=1) for _ in range(3)]
    profile = PlayerProfile(player_id="p1", name="Test Player", world_rank=1, rounds=rounds)
    result = compute_consistency(profile)
    assert result["rounds_counted"] == 3
    assert result["reliable"] is False

    rounds_enough = rounds * 4  # 12 rounds
    profile_enough = PlayerProfile(player_id="p1", name="Test Player", world_rank=1, rounds=rounds_enough)
    result_enough = compute_consistency(profile_enough)
    assert result_enough["reliable"] is True
