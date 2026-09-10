"""
Utility per i broadcaster che trasmettono su YouTube (CazéTV, SportyNet, ...).

Non usa la YouTube Data API (richiederebbe una API key e ha quota limitata):
si appoggia invece al feed RSS pubblico di ogni canale, che espone gli ultimi
video (titolo + descrizione) senza autenticazione. È lo stesso approccio del
progetto originale, reso però più robusto:
  - se il channel_id in config.py manca o è sbagliato, viene risolto
    automaticamente a partire dall'handle (@nome) leggendo la pagina pubblica
    del canale;
  - eventuali errori di rete non bloccano lo scraper.
"""

import logging
import re

import feedparser

from scrapers.base import SESSION
import config

logger = logging.getLogger("seriea_tracker")

_CHANNEL_ID_RE = re.compile(r'"channelId":"(UC[0-9A-Za-z_-]{22})"')


def resolve_channel_id(handle: str) -> str | None:
    """
    Ricava l'ID canonico (UC...) di un canale a partire dal suo handle
    (es. "@CazeTV"), leggendo l'HTML pubblico della pagina del canale.
    """
    handle = handle.lstrip("@")
    url = f"https://www.youtube.com/@{handle}"
    try:
        resp = SESSION.get(url, timeout=config.REQUEST_TIMEOUT)
        if resp.status_code != 200:
            logger.warning("Impossibile aprire %s (HTTP %s)", url, resp.status_code)
            return None
        match = _CHANNEL_ID_RE.search(resp.text)
        if match:
            return match.group(1)
        logger.warning("channelId non trovato nella pagina di @%s", handle)
    except Exception as exc:
        logger.warning("Errore risolvendo l'handle @%s: %s", handle, exc)
    return None


def get_channel_id(channel_config: dict) -> str | None:
    """Restituisce il channel_id da config, risolvendolo dall'handle se assente."""
    channel_id = channel_config.get("channel_id")
    if channel_id:
        return channel_id
    handle = channel_config.get("handle")
    if not handle:
        return None
    resolved = resolve_channel_id(handle)
    if resolved:
        logger.info("Handle %s risolto in channel_id %s", handle, resolved)
    return resolved


def get_recent_videos(channel_config: dict) -> list[str]:
    """
    Restituisce titolo + descrizione degli ultimi video pubblicati dal canale,
    una stringa per video (usata poi per il fuzzy matching con le partite).
    """
    channel_id = get_channel_id(channel_config)
    if not channel_id:
        return []

    feed_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    try:
        feed = feedparser.parse(feed_url)
        if feed.bozo and not feed.entries:
            logger.warning("Feed RSS non valido per channel_id %s", channel_id)
            return []
        return [
            f"{entry.get('title', '')} {entry.get('summary', '')}"
            for entry in feed.entries
        ]
    except Exception as exc:
        logger.warning("Errore leggendo il feed RSS di %s: %s", channel_id, exc)
        return []
