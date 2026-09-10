"""
Configurazione centralizzata del progetto.
Tutti i parametri "da aggiornare ogni stagione" (canali YouTube, date campionato,
squadre promosse/retrocesse) stanno qui, così non serve toccare il codice degli
scraper per un aggiornamento stagionale.
"""

import os

# ---------------------------------------------------------------------------
# Calendario / API partite
# ---------------------------------------------------------------------------

ESPN_LEAGUE_SLUG = "ita.1"  # Serie A su ESPN
ESPN_SCOREBOARD_URL = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{ESPN_LEAGUE_SLUG}/scoreboard"

# La Serie A 2026/27 si gioca indicativamente da fine agosto 2026 a fine maggio 2027.
# Aggiorna queste due date a inizio stagione se cambia il calendario ufficiale.
SEASON_START = "2026-08-22"
SEASON_END = "2027-05-31"

# Numero di giorni per ogni "finestra" richiesta all'API ESPN (l'endpoint scoreboard
# non restituisce un intero campionato con una singola chiamata: va paginato per date).
ESPN_WINDOW_DAYS = 15

# Considera solo le partite da oggi in poi nel report finale (le passate non servono
# a chi vuole sapere "dove la vedo").
ONLY_UPCOMING_MATCHES = True

# ---------------------------------------------------------------------------
# HTTP
# ---------------------------------------------------------------------------

REQUEST_TIMEOUT = 20  # secondi
REQUEST_RETRIES = 3
REQUEST_BACKOFF_SECONDS = 1.5

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)

DEFAULT_HEADERS = {
    "User-Agent": DEFAULT_USER_AGENT,
    "Accept-Language": "it-IT,it;q=0.9,en;q=0.8",
}

# ---------------------------------------------------------------------------
# Canali YouTube (broadcaster gratuiti via YouTube)
# ---------------------------------------------------------------------------
# Per ciascun canale puoi specificare l'handle (es. "@CazeTV") e/o l'ID canonico
# (UC...). Se l'ID non è noto/verificato lascialo a None: lo scraper lo risolverà
# automaticamente dall'handle alla prima esecuzione (più lento ma sempre corretto).

YOUTUBE_CHANNELS = {
    "CazéTV": {
        "handle": "@CazeTV",
        # Verificato via Wikidata (settembre 2026): non hardcodare mai un ID
        # senza controllo, YouTube lo cambia raramente ma non è garantito.
        "channel_id": "UCZiYbVptd3PVPf4f6eR6UaQ",
        "lang": "pt",
        "affidabile": True,
    },
    "SportyNet": {
        "handle": "@SportyNetBrasil",
        # ID NON verificato nella versione precedente del progetto: lo lasciamo
        # vuoto così viene risolto automaticamente dall'handle invece di usare
        # un ID potenzialmente sbagliato.
        "channel_id": None,
        "lang": "pt",
        "affidabile": True,
    },
}

# ---------------------------------------------------------------------------
# Altri broadcaster gratuiti (siti web / palinsesti)
# ---------------------------------------------------------------------------
# "affidabile": False significa "includi nel report ma marca come da verificare
# manualmente" — usato per broadcaster con geoblocking severo o modello
# freemium poco chiaro.

WEB_BROADCASTERS = {
    "XSports": {
        "urls": [
            "https://www.xsports.com.br",
            "https://www.xsports.com.br/programacao",
        ],
        "lang": "pt",
        "affidabile": False,  # geoblocking Brasile, palinsesto non sempre pubblicato online
    },
    "SportyTV": {
        "urls": [
            "https://sporty.com/tv",
        ],
        "lang": "en",
        "affidabile": False,  # nessun palinsesto pubblico strutturato confermato
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
        "affidabile": False,  # gratuito solo via antenna OTA, palinsesto poco affidabile online
    },
    "ANTV": {
        "urls": [
            "https://www.antvklik.com",
        ],
        "lang": "id",
        "affidabile": False,  # palinsesto indonesiano non sempre indicizzabile
    },
    "Match TV": {
        "urls": [
            "https://matchtv.ru/football",
        ],
        "lang": "ru",
        "affidabile": False,  # geoblocking Russia + solo alcune partite top
    },
    "New World TV": {
        "urls": [
            "https://www.newworldtv.com/sports",
        ],
        "lang": "fr",
        "affidabile": False,  # prevalentemente pay, quota gratuita non documentata
    },
    "ELTA": {
        "urls": [
            "https://eltaott.tv/sports",
        ],
        "lang": "zh",
        "affidabile": False,  # servizio OTT freemium, quota gratuita non documentata
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
