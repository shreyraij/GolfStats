from fastapi import APIRouter

from app.data.source import get_data_source
from app.metrics.consistency import compute_consistency
from app.metrics.weather_performance import compute_weather_performance

router = APIRouter(prefix="/players/{player_id}")


@router.get("/metrics/consistency")
def player_consistency(player_id: str):
    source = get_data_source()
    profile = source.get_player_profile(player_id)
    return {**compute_consistency(profile), "data_source": source.name}


@router.get("/metrics/weather-performance")
def player_weather_performance(player_id: str):
    source = get_data_source()
    profile = source.get_player_profile(player_id)
    return {**compute_weather_performance(profile), "data_source": source.name}
