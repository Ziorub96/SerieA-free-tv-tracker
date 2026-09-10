"""
Configurazione centralizzata del progetto.
Tutti i parametri "da aggiornare ogni stagione" (canali YouTube, date campionato,
squadre promosse/retrocesse) stanno qui, così non serve toccare il codice degli
scraper per un aggiornamento stagionale.
"""

import os

# ---------------------------------------------------------------------------
# Calendario / API partite  (NUOVA FONTE: football-data.org)
# ---------------------------------------------------------------------------

FOOTBALL_DATA_BASE = "https://api.football-data.org/v4"
FOOTBALL_DATA_COMPETITION = "SA"  # Serie A
FOOTBALL_DATA_TOKEN = os.getenv("FOOTBALL_DATA_TOKEN", "")  # letto dal secret di GitHub Actions

# La Serie A 2026/27 si gioca indicativamente da fine agosto 2026 a fine maggio 2027.
SEASON_START = "2026-08-22"
SEASON_END = "2027-05-31"

# Considera solo le partite da oggi in poi nel report finale
ONLY_UPCOMING_MATCHES = True

# ---------------------------------------------------------------------------
# HTTP
# ---------------------------------------------------------------------------

REQUEST_TIMEOUT = 25
REQUEST_RETRIES = 4
REQUEST_BACKOFF_SECONDS = 2.0

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/128.0.0.0 Safari/537.36"
)

DEFAULT_HEADERS = {
    "User-Agent": DEFAULT_USER_AGENT,
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9,it;q=0.8",
}

# ---------------------------------------------------------------------------
# Canali YouTube
# ---------------------------------------------------------------------------

YOUTUBE_CHANNELS = {
    "CazéTV": {
        "handle": "@CazeTV",
        "channel_id": "UCZiYbVptd3PVPf4f6eR6UaQ",
        "lang": "pt",
        "affidabile": True,
    },
    "SportyNet": {
        "handle": "@SportyNetBrasil",
        "channel_id": None,
        "lang": "pt",
        "affidabile": True,
    },
}

# ---------------------------------------------------------------------------
# Altri broadcaster gratuiti
# ---------------------------------------------------------------------------

WEB_BROADCASTERS = {
    "XSports": {
        "urls": [
            "https://www.xsports.com.br",
            "https://www.xsports.com.br/programacao",
        ],
        "lang": "pt",
        "affidabile": False,
    },
    "SportyTV": {
        "urls": [
            "https://sporty.com/tv",
        ],
        "lang": "en",
        "affidabile": False,
    },
    "CBS Sports Golazo": {
        "urls": [
            "https://www.cbssports.com/soccer/schedule/",
        ],
        "lang": "en",
        "affidabile": True,
    },
    "Telemundo": {
        "urls": [
            "https://www.telemundo.com/deportes/futbol",
        ],
        "lang": "es",
        "affidabile": False,
    },
    "ANTV": {
        "urls": [
            "https://www.antvklik.com",
        ],
        "lang": "id",
        "affidabile": False,
    },
    "Match TV": {
        "urls": [
            "https://matchtv.ru/football",
        ],
        "lang": "ru",
        "affidabile": False,
    },
    "New World TV": {
        "urls": [
            "https://www.newworldtv.com/sports",
        ],
        "lang": "fr",
        "affidabile": False,
    },
    "ELTA": {
        "urls": [
            "https://eltaott.tv/sports",
        ],
        "lang": "zh",
        "affidabile": False,
    },
}

# ---------------------------------------------------------------------------
# Matching
# ---------------------------------------------------------------------------

FUZZY_MATCH_THRESHOLD = 80

# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
REPORT_JSON_PATH = os.path.join(DATA_DIR, "report.json")
REPORT_MD_PATH = os.path.join(OUTPUT_DIR, "report.md")