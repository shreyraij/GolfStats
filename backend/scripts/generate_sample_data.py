"""Regenerates backend/app/data/sample_data.json — the fixture served when
DATAGOLF_API_KEY isn't set (see app/data/source.py).

Everything here is FICTIONAL: player names, courses, events and stats are
made up so the dashboard can run end to end without a paid DataGolf key.
Seeded, so re-running produces the same file.

    cd backend && python scripts/generate_sample_data.py
"""

from __future__ import annotations

import json
import random
import re
from datetime import date, timedelta
from pathlib import Path

SEED = 20261122
OUT_PATH = Path(__file__).resolve().parent.parent / "app" / "data" / "sample_data.json"

# Deliberately invented names; not modelled on any real player.
PLAYERS = [
    ("Corwin Ashgrove", "USA"), ("Matthias Vellbrook", "GER"), ("Desmond Quayle", "ENG"),
    ("Teodor Halvik", "NOR"), ("Rafferty Lusk", "IRL"), ("Kenji Amarozawa", "JPN"),
    ("Ellison Prewitt", "USA"), ("Bastien Oriel", "FRA"), ("Lachlan Fenwarra", "AUS"),
    ("Ignacio Valdemora", "ESP"), ("Wyatt Brannock", "USA"), ("Soren Kettleby", "DEN"),
    ("Hugo Marchetti-Lowe", "ITA"), ("Dariusz Wolanek", "POL"), ("Thabo Kesselring", "RSA"),
    ("Callum Strathorne", "SCO"), ("Joon-ho Baekwon", "KOR"), ("Alder Pennick", "CAN"),
    ("Silas Marrowfield", "USA"), ("Emeric Dufrenne", "BEL"), ("Rohan Tiwarekar", "IND"),
    ("Augustin Pellerey", "FRA"), ("Nils Grabowe", "SWE"), ("Fergus Ottaway", "NZL"),
    ("Quentin Harbridge", "USA"), ("Mateo Escarlata", "ARG"), ("Linus Ebberhart", "AUT"),
    ("Tomasz Wierzbica", "POL"), ("Barnaby Coldwater", "ENG"), ("Jasper Vintrell", "USA"),
]

# Fictional events at fictional courses. base_wind is the course's typical
# daytime wind in mph; rain_chance is per-round.
EVENTS = [
    ("Saltmarsh Invitational", "Saltmarsh Links", 18, 0.25),
    ("Cedar Hollow Classic", "Cedar Hollow Country Club", 8, 0.20),
    ("Ironwood Open", "Ironwood National", 11, 0.15),
    ("Bramblecrest Championship", "Bramblecrest Golf Club", 9, 0.30),
    ("Gullhaven Links Trophy", "Gullhaven Links", 20, 0.35),
    ("Desert Mesa Shootout", "Desert Mesa Resort", 7, 0.05),
    ("Thornbury Masters", "Thornbury Park", 10, 0.25),
    ("Kestrel Point Open", "Kestrel Point", 16, 0.20),
    ("Willowmere Classic", "Willowmere Golf & CC", 6, 0.30),
    ("Harrowgate Heritage", "Harrowgate Downs", 13, 0.40),
    ("Copperfield Championship", "Copperfield Ridge", 9, 0.10),
    ("Northgale Open", "Northgale Links", 19, 0.30),
    ("Pinecrest Pro-Am", "Pinecrest Valley", 8, 0.20),
    ("Ravensclaw Invitational", "Ravensclaw Golf Club", 12, 0.15),
    ("Seabright Classic", "Seabright Dunes", 17, 0.25),
    ("Granite Falls Championship", "Granite Falls GC", 10, 0.20),
]

PAR = 72


def build_tournaments(rng: random.Random) -> list[dict]:
    tournaments = []
    start = date(2026, 1, 15)
    for i, (name, course, base_wind, rain_chance) in enumerate(EVENTS):
        first_day = start + timedelta(weeks=2 * i)
        rounds = []
        for r in range(1, 5):
            wind = max(2.0, rng.gauss(base_wind, 4.5))
            rounds.append(
                {
                    "round_number": r,
                    "round_date": (first_day + timedelta(days=r - 1)).isoformat(),
                    "wind_speed_mph": round(wind, 1),
                    "precipitation": rng.random() < rain_chance,
                    "temperature_f": round(rng.gauss(72, 9), 1),
                }
            )
        tournaments.append(
            {
                "tournament_id": f"sample-evt-{i + 1:02d}",
                "name": name,
                "course_id": f"sample-course-{i + 1:02d}",
                "course_name": course,
                "par": PAR,
                "rounds": rounds,
            }
        )
    return tournaments


def player_traits(rng: random.Random, rank: int) -> dict:
    skill = 0.6 - rank * 0.025  # better-ranked players lean a bit stronger
    return {
        # Per-hole probabilities in neutral conditions.
        "birdie_p": min(0.30, max(0.14, rng.gauss(0.20 + skill * 0.06, 0.025))),
        "bogey_p": min(0.22, max(0.08, rng.gauss(0.13 - skill * 0.04, 0.025))),
        # Extra bogey probability per mph of wind over 10, and in rain.
        "wind_sensitivity": max(0.0, rng.gauss(0.006, 0.004)),
        "rain_sensitivity": max(0.0, rng.gauss(0.03, 0.025)),
        "events_played": rng.randint(9, 14),
    }


def simulate_round(rng: random.Random, traits: dict, conditions: dict) -> dict:
    wind_over = max(0.0, conditions["wind_speed_mph"] - 10)
    bogey_p = traits["bogey_p"] + wind_over * traits["wind_sensitivity"]
    birdie_p = traits["birdie_p"] - wind_over * traits["wind_sensitivity"] * 0.5
    if conditions["precipitation"]:
        bogey_p += traits["rain_sensitivity"]
        birdie_p -= traits["rain_sensitivity"] * 0.5
    birdie_p = max(0.03, birdie_p)
    bogey_p = min(0.5, bogey_p)

    birdies = pars = bogeys = 0
    score = 0
    for _ in range(18):
        roll = rng.random()
        if roll < birdie_p:
            birdies += 1
            score -= 2 if rng.random() < 0.04 else 1  # occasional eagle
        elif roll < birdie_p + bogey_p:
            bogeys += 1
            score += 2 if rng.random() < 0.12 else 1  # occasional double
        else:
            pars += 1
    return {"birdies_or_better": birdies, "pars": pars, "bogeys_or_worse": bogeys, "score_to_par": score}


def main() -> None:
    rng = random.Random(SEED)
    tournaments = build_tournaments(rng)

    players = []
    for rank, (name, country) in enumerate(PLAYERS, start=1):
        traits = player_traits(rng, rank)
        # A couple of players get a thin schedule so the UI's "not enough
        # data yet" states are visible in sample mode too.
        if rank in (12, 27):
            traits["events_played"] = 1
        events = sorted(rng.sample(tournaments, traits["events_played"]), key=lambda t: t["tournament_id"])

        rounds = []
        for event in events:
            two_round_total = 0
            for cond in event["rounds"]:
                if cond["round_number"] == 3 and two_round_total > 2:
                    break  # missed the cut
                result = simulate_round(rng, traits, cond)
                if cond["round_number"] <= 2:
                    two_round_total += result["score_to_par"]
                rounds.append({"tournament_id": event["tournament_id"], "round_number": cond["round_number"], **result})

        players.append(
            {
                "player_id": f"sample-{rank:03d}",
                "player_name": name,
                "country": country,
                "owgr_rank": rank,
                "rounds": rounds,
            }
        )

    fixture = {
        "_notice": (
            "SAMPLE DATA. All players, events, courses and stats in this file are fictional, "
            "generated by backend/scripts/generate_sample_data.py. Served only when "
            "DATAGOLF_API_KEY is not set."
        ),
        "tournaments": tournaments,
        "players": players,
    }
    # One round per line keeps the file small but still diffable.
    text = json.dumps(fixture, indent=1)
    text = re.sub(r"\{\n\s+(\"(?:round_number|tournament_id)\"[^{}\[\]]*?)\n\s+\}",
                  lambda m: "{" + re.sub(r"\n\s+", " ", m.group(1)) + "}", text)
    OUT_PATH.write_text(text + "\n")
    total_rounds = sum(len(p["rounds"]) for p in players)
    print(f"Wrote {OUT_PATH} ({len(players)} players, {len(tournaments)} events, {total_rounds} rounds)")


if __name__ == "__main__":
    main()
