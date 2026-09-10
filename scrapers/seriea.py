"""
Recupera il calendario completo della Serie A da football-data.org (API ufficiale e stabile).
"""

import logging
from datetime import datetime

from scrapers.base import SESSION
import config

logger = logging.getLogger("seriea_tracker")


def get_matches() -> list[dict]:
    """
    Restituisce una lista di dict: home, away, date, time, datetime_iso, event_id.
    """
    if not config.FOOTBALL_DATA_TOKEN:
        logger.error("FOOTBALL_DATA_TOKEN non impostato! Aggiungi il secret su GitHub Actions.")
        return []

    url = f"{config.FOOTBALL_DATA_BASE}/competitions/{config.FOOTBALL_DATA_COMPETITION}/matches"
    headers = {
        "X-Auth-Token": config.FOOTBALL_DATA_TOKEN,
        "User-Agent": config.DEFAULT_USER_AGENT,
    }

    params = {
        "status": "SCHEDULED,TIMED,IN_PLAY,PAUSED,FINISHED",  # prendiamo tutto e filtriamo dopo
        "dateFrom": config.SEASON_START,
        "dateTo": config.SEASON_END,
    }

    matches_by_id = {}

    try:
        resp = SESSION.get(url, headers=headers, params=params, timeout=config.REQUEST_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
    except Exception as exc:
        logger.error("Errore chiamata football-data.org: %s", exc)
        return []

    for match in data.get("matches", []):
        try:
            event_id = str(match["id"])
            home = match["homeTeam"]["name"]
            away = match["awayTeam"]["name"]
            date_str = match["utcDate"]  # es. "2026-09-11T18:45:00Z"

            dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))

            matches_by_id[event_id] = {
                "event_id": event_id,
                "home": home,
                "away": away,
                "date": dt.strftime("%Y-%m-%d"),
                "time": dt.strftime("%H:%M"),
                "datetime_iso": date_str,
            }
        except (KeyError, ValueError) as exc:
            logger.debug("Partita scartata: %s", exc)
            continue

    matches = sorted(matches_by_id.values(), key=lambda m: m["datetime_iso"])
    logger.info("Calendario Serie A (football-data.org): %d partite recuperate.", len(matches))
    return matches