from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_rankings_serves_sample_data_without_api_key(monkeypatch):
    monkeypatch.delenv("DATAGOLF_API_KEY", raising=False)
    response = client.get("/rankings")
    assert response.status_code == 200
    body = response.json()
    assert body["data_source"] == "sample"
    assert len(body["rankings"]) > 0


def test_player_consistency_handles_empty_profile(monkeypatch):
    monkeypatch.delenv("DATAGOLF_API_KEY", raising=False)
    response = client.get("/players/abc123/metrics/consistency")
    assert response.status_code == 200
    body = response.json()
    assert body["player_id"] == "abc123"
    assert body["reliable"] is False


def test_player_weather_performance_handles_empty_profile(monkeypatch):
    monkeypatch.delenv("DATAGOLF_API_KEY", raising=False)
    response = client.get("/players/abc123/metrics/weather-performance")
    assert response.status_code == 200
    body = response.json()
    assert body["player_id"] == "abc123"
    assert body["avg_score_to_par_windy"] is None
