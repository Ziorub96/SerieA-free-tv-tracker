"""
Recupera il calendario completo della Serie A dall'API pubblica di ESPN.

BUG CORRETTO rispetto alla versione originale: l'endpoint scoreboard di ESPN,
se chiamato senza parametro "dates", restituisce solo le partite della
giornata/settimana corrente — non l'intero campionato. Per ottenere tutta la
stagione occorre paginare per finestre di date (qui: blocchi di
config.ESPN_WINDOW_DAYS giorni) e unire i risultati deduplicando per event id.
"""

import logging
from datetime import datetime, timedelta

from scrapers.base import SESSION
import config

logger = logging.getLogger("seriea_tracker")


def _date_windows(start: str, end: str, window_days: int):
    start_dt = datetime.strptime(start, "%Y-%m-%d")
    end_dt = datetime.strptime(end, "%Y-%m-%d")
    cur = start_dt
    while cur <= end_dt:
        win_end = min(cur + timedelta(days=window_days - 1), end_dt)
        yield cur.strftime("%Y%m%d"), win_end.strftime("%Y%m%d")
        cur = win_end + timedelta(days=1)


def get_matches() -> list[dict]:
    """
    Restituisce una lista di dict: home, away, date (YYYY-MM-DD), time (HH:MM),
    datetime_iso, event_id. Deduplicata per event_id.
    """
    matches_by_id = {}

    for date_from, date_to in _date_windows(
        config.SEASON_START, config.SEASON_END, config.ESPN_WINDOW_DAYS
    ):
        params = {"dates": f"{date_from}-{date_to}"}
        try:
            resp = SESSION.get(
                config.ESPN_SCOREBOARD_URL, params=params, timeout=config.REQUEST_TIMEOUT
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception as exc:
            logger.warning("Finestra %s-%s fallita: %s", date_from, date_to, exc)
            continue

        for event in data.get("events", []):
            try:
                event_id = event["id"]
                comp = event["competitions"][0]
                home = away = None
                for team in comp["competitors"]:
                    if team["homeAway"] == "home":
                        home = team["team"]["displayName"]
                    elif team["homeAway"] == "away":
                        away = team["team"]["displayName"]

                if not home or not away:
                    continue

                date_str = event["date"]
                dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))

                matches_by_id[event_id] = {
                    "event_id": event_id,
                    "home": home,
                    "away": away,
                    "date": dt.strftime("%Y-%m-%d"),
                    "time": dt.strftime("%H:%M"),
                    "datetime_iso": date_str,
                }
            except (KeyError, IndexError, ValueError) as exc:
                logger.debug("Evento scartato (formato inatteso): %s", exc)
                continue

    matches = sorted(matches_by_id.values(), key=lambda m: m["datetime_iso"])
    logger.info("Calendario Serie A: %d partite recuperate.", len(matches))
    return matches
