"""
Scraper per i broadcaster gratuiti "web" (non YouTube).
Sostituisce gli 8 file quasi identici della versione originale
(xsports.py, sportytv.py, golazo.py, telemundo.py, antv.py, matchtv.py,
newworld.py, elta.py): la logica era duplicata otto volte con la sola
differenza degli URL, quindi ora è un'unica funzione pilotata da
config.WEB_BROADCASTERS.

ATTENZIONE (onestà sui limiti): molti di questi siti generano il palinsesto
via JavaScript lato client. Uno scraping con semplice requests.get() vede solo
l'HTML iniziale e potrebbe non trovare gli orari delle partite. Per questi
broadcaster il matching si basa sul testo effettivamente presente nell'HTML
statico: se un broadcaster risulta sempre "nessuna conferma" nel report,
probabilmente ha questo problema e andrebbe migrato a uno scraping con
browser headless (Playwright) — vedi README, sezione "Limiti noti".
"""

from scrapers.base import fetch_pages
import config


def get_all_web_sources() -> dict:
    """
    Restituisce {nome_broadcaster: {"pages": [...], "lang": ..., "affidabile": ...}}
    per tutti i broadcaster web configurati.
    """
    sources = {}
    for name, broadcaster_config in config.WEB_BROADCASTERS.items():
        sources[name] = {
            "pages": fetch_pages(broadcaster_config["urls"]),
            "lang": broadcaster_config["lang"],
            "affidabile": broadcaster_config["affidabile"],
        }
    return sources
