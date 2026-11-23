"""Sample-data mode: what the app serves when DATAGOLF_API_KEY isn't set."""

import pytest
from fastapi.testclient import TestClient

from app.data.source import DataGolfSource, SampleDataSource, get_data_source
from app.main import app

client = TestClient(app)


@pytest.fixture
def sample_mode(monkeypatch):
    monkeypatch.delenv("DATAGOLF_API_KEY", raising=False)


def test_switch_picks_sample_without_key(sample_mode):
    assert isinstance(get_data_source(), SampleDataSource)


def test_switch_picks_datagolf_with_key(monkeypatch):
    monkeypatch.setenv("DATAGOLF_API_KEY", "test-key")
    assert isinstance(get_data_source(), DataGolfSource)


def test_sample_rankings(sample_mode):
    body = client.get("/rankings").json()
    assert body["data_source"] == "sample"

    rankings = body["rankings"]
    assert len(rankings) >= 20
    assert [r["owgr_rank"] for r in rankings] == sorted(r["owgr_rank"] for r in rankings)
    # Sample IDs are namespaced so they can't be mistaken for real DataGolf IDs.
    assert all(r["player_id"].startswith("sample-") for r in rankings)
    assert all(r["player_name"] for r in rankings)

    limited = client.get("/rankings?limit=5").json()["rankings"]
    assert len(limited) == 5


def test_both_metrics_compute_on_sample_data(sample_mode):
    rankings = client.get("/rankings").json()["rankings"]
    top_player = rankings[0]["player_id"]

    consistency = client.get(f"/players/{top_player}/metrics/consistency").json()
    assert consistency["data_source"] == "sample"
    assert consistency["reliable"] is True
    assert consistency["rounds_counted"] >= 10
    assert 0 < consistency["birdie_rate"] < 1
    assert 0 < consistency["bogey_or_worse_rate"] < 1
    assert consistency["total_holes"] == consistency["rounds_counted"] * 18

    weather = client.get(f"/players/{top_player}/metrics/weather-performance").json()
    assert weather["data_source"] == "sample"
    assert weather["wind_result_reliable"] is True
    assert weather["avg_score_to_par_windy"] is not None
    assert weather["avg_score_to_par_calm"] is not None
    assert weather["rain_rounds_sample_size"] > 0
    assert weather["avg_score_to_par_dry"] is not None


def test_every_sample_player_has_computable_metrics(sample_mode):
    source = SampleDataSource()
    for entry in source.get_rankings():
        profile = source.get_player_profile(entry.player_id)
        assert profile.name == entry.player_name
        assert profile.rounds, f"{entry.player_id} has no rounds"
        for r in profile.rounds:
            assert r.hole_outcomes.total_holes == 18
            assert r.conditions is not None


def test_sample_includes_thin_sample_player(sample_mode):
    """At least one player should fall below the reliability floor, so the
    UI's small-sample state is exercised in sample mode too."""
    rankings = client.get("/rankings").json()["rankings"]
    reliabilities = [
        client.get(f"/players/{r['player_id']}/metrics/consistency").json()["reliable"] for r in rankings
    ]
    assert not all(reliabilities)
