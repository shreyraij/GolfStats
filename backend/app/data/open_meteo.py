"""Open-Meteo historical weather adapter. Free, no API key.

Golf-specific weather (per-hole wind/rain) isn't published anywhere, so we
approximate: pull hourly wind/precipitation/temperature for the course's
coordinates on the round's date, and average over typical daytime play
hours (7am-7pm local) as a stand-in for "conditions during the round."
"""

from __future__ import annotations

import httpx

from app.models.schemas import RoundConditions

BASE_URL = "https://archive-api.open-meteo.com/v1/archive"
DEFAULT_TIMEOUT = 30.0

PLAY_HOURS_START = 7
PLAY_HOURS_END = 19


def get_round_conditions(latitude: float, longitude: float, date: str) -> RoundConditions:
    """`date` is an ISO date string (yyyy-mm-dd) in the course's local time."""

    response = httpx.get(
        BASE_URL,
        params={
            "latitude": latitude,
            "longitude": longitude,
            "start_date": date,
            "end_date": date,
            "hourly": "wind_speed_10m,precipitation,temperature_2m",
            "windspeed_unit": "mph",
            "temperature_unit": "fahrenheit",
            "timezone": "auto",
        },
        timeout=DEFAULT_TIMEOUT,
    )
    response.raise_for_status()
    payload = response.json()
    hourly = payload.get("hourly", {})

    times = hourly.get("time", [])
    wind_speeds = hourly.get("wind_speed_10m", [])
    precipitation = hourly.get("precipitation", [])
    temperatures = hourly.get("temperature_2m", [])

    daytime_indices = [
        i for i, t in enumerate(times) if PLAY_HOURS_START <= int(t[11:13]) < PLAY_HOURS_END
    ]

    if not daytime_indices:
        return RoundConditions()

    daytime_wind = [wind_speeds[i] for i in daytime_indices if i < len(wind_speeds)]
    daytime_precip = [precipitation[i] for i in daytime_indices if i < len(precipitation)]
    daytime_temp = [temperatures[i] for i in daytime_indices if i < len(temperatures)]

    return RoundConditions(
        wind_speed_mph=round(sum(daytime_wind) / len(daytime_wind), 1) if daytime_wind else None,
        precipitation=sum(daytime_precip) > 0 if daytime_precip else None,
        temperature_f=round(sum(daytime_temp) / len(daytime_temp), 1) if daytime_temp else None,
    )
