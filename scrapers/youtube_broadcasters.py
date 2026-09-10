"""
Scraper per i broadcaster gratuiti che trasmettono su YouTube.
Sostituisce i vecchi file separati cazetv_youtube.py / sportynet_youtube.py:
la logica è identica per ogni canale, quindi viene fattorizzata qui e pilotata
da config.YOUTUBE_CHANNELS.
"""

from scrapers.youtube_utils import get_recent_videos
import config


def get_all_youtube_sources() -> dict:
    """
    Restituisce {nome_broadcaster: {"pages": [...], "lang": ..., "affidabile": ...}}
    per tutti i canali YouTube configurati.
    """
    sources = {}
    for name, channel_config in config.YOUTUBE_CHANNELS.items():
        sources[name] = {
            "pages": get_recent_videos(channel_config),
            "lang": channel_config["lang"],
            "affidabile": channel_config["affidabile"],
        }
    return sources
