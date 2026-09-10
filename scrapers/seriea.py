import os
import requests
from datetime import datetime, timedelta

FOOTBALL_DATA_TOKEN = os.environ.get("FOOTBALL_DATA_TOKEN", "")

def get_matches(days_ahead=10):
    """
    Recupera il calendario della Serie A da football-data.org.
    Filtra solo le partite nei prossimi `days_ahead` giorni.
    """
    if not FOOTBALL_DATA_TOKEN:
        print("[WARNING] FOOTBALL_DATA_TOKEN non impostato. Uso ESPN come fallback.")
        return get_matches_espn(days_ahead)

    url = "https://api.football-data.org/v4/competitions/SA/matches"
    headers = {"X-Auth-Token": FOOTBALL_DATA_TOKEN}

    try:
        r = requests.get(url, headers=headers, timeout=30)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        print(f"[ERROR] football-data.org: {e}")
        return get_matches_espn(days_ahead)

    matches = []
    oggi = datetime.now()
    limite = oggi + timedelta(days=days_ahead)

    for m in data.get("matches", []):
        date_str = m["utcDate"]
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        dt_naive = dt.replace(tzinfo=None)

        if not (oggi <= dt_naive <= limite):
            continue

        matches.append({
            "home": m["homeTeam"]["name"],
            "away": m["awayTeam"]["name"],
            "date": dt.strftime("%Y-%m-%d"),
            "time": dt.strftime("%H:%M"),
            "datetime_iso": date_str
        })

    return matches


def get_matches_espn(days_ahead=10):
    """Fallback: API ESPN."""
    url = "https://site.api.espn.com/apis/site/v2/sports/soccer/ita.1/scoreboard"
    r = requests.get(url, timeout=20)
    data = r.json()

    matches = []
    oggi = datetime.now()
    limite = oggi + timedelta(days=days_ahead)

    for event in data.get("events", []):
        comp = event["competitions"][0]
        home = away = None
        for t in comp["competitors"]:
            if t["homeAway"] == "home":
                home = t["team"]["displayName"]
            elif t["homeAway"] == "away":
                away = t["team"]["displayName"]

        date_str = event["date"]
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        dt_naive = dt.replace(tzinfo=None)

        if not (oggi <= dt_naive <= limite):
            continue

        matches.append({
            "home": home,
            "away": away,
            "date": dt.strftime("%Y-%m-%d"),
            "time": dt.strftime("%H:%M"),
            "datetime_iso": date_str
        })

    return matches