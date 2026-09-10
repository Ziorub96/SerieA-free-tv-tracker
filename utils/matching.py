"""
Fuzzy matching tra il testo di una pagina/palinsesto e una partita di Serie A.

Rispetto alla versione originale:
  - normalizzazione unicode (accenti, maiuscole) prima del confronto, così
    "Nápoles" e "napoles" matchano correttamente;
  - soglia di fuzzy matching centralizzata in config.py invece che hardcoded;
  - la tabella di traduzione squadre è dichiaratamente da aggiornare a ogni
    stagione (promozioni/retrocessioni cambiano le 20 squadre di Serie A).
"""

import unicodedata

from rapidfuzz import fuzz

import config

# Traduzioni per le lingue dei broadcaster che pubblicano il palinsesto in
# lingua locale (non in italiano/inglese). Aggiorna questa tabella a inizio
# stagione con le 20 squadre di Serie A effettivamente in campionato.
TEAM_TRANSLATIONS = {
    "es": {  # Telemundo
        "Milan": "Milan", "Inter Milan": "Inter de Milán", "Juventus": "Juventus",
        "Napoli": "Nápoles", "Roma": "Roma", "Lazio": "Lazio",
        "Fiorentina": "Fiorentina", "Atalanta": "Atalanta", "Bologna": "Bolonia",
        "Torino": "Turín", "Udinese": "Udinese", "Genoa": "Génova",
        "Cagliari": "Cagliari", "Lecce": "Lecce", "Hellas Verona": "Verona",
        "Parma": "Parma", "Como": "Como", "Monza": "Monza",
        "Venezia": "Venecia", "Sassuolo": "Sassuolo",
    },
    "fr": {  # New World TV
        "Milan": "Milan", "Inter Milan": "Inter Milan", "Juventus": "Juventus",
        "Napoli": "Naples", "Roma": "Rome", "Lazio": "Lazio",
        "Fiorentina": "Fiorentina", "Atalanta": "Atalanta", "Bologna": "Bologne",
        "Torino": "Turin", "Udinese": "Udinese", "Genoa": "Gênes",
        "Cagliari": "Cagliari", "Lecce": "Lecce", "Hellas Verona": "Vérone",
        "Parma": "Parme", "Como": "Côme", "Monza": "Monza",
        "Venezia": "Venise", "Sassuolo": "Sassuolo",
    },
    "ru": {  # Match TV
        "Milan": "Милан", "Inter Milan": "Интер", "Juventus": "Ювентус",
        "Napoli": "Наполи", "Roma": "Рома", "Lazio": "Лацио",
        "Fiorentina": "Фиорентина", "Atalanta": "Аталанта", "Bologna": "Болонья",
        "Torino": "Торино", "Udinese": "Удинезе", "Genoa": "Дженоа",
        "Cagliari": "Кальяри", "Lecce": "Лечче", "Hellas Verona": "Верона",
        "Parma": "Парма", "Como": "Комо", "Monza": "Монца",
        "Venezia": "Венеция", "Sassuolo": "Сассуоло",
    },
}


def _normalize(text: str) -> str:
    """Minuscolo + rimozione accenti, per confronti robusti tra lingue diverse."""
    text = text.lower().strip()
    text = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in text if not unicodedata.combining(ch))


def translate_team(team_name: str, lang: str) -> str:
    if lang in ("it", "en", "pt"):  # queste lingue usano di norma i nomi originali
        return team_name
    return TEAM_TRANSLATIONS.get(lang, {}).get(team_name, team_name)


def match_game(text: str, home: str, away: str, lang: str = "it", threshold: int = None) -> bool:
    """
    True se il testo (es. titolo di un video, HTML di un palinsesto) sembra
    riferirsi alla partita home-away, cercando entrambe le squadre.
    """
    if not text:
        return False

    threshold = threshold if threshold is not None else config.FUZZY_MATCH_THRESHOLD

    text_norm = _normalize(text)
    home_norm = _normalize(translate_team(home, lang))
    away_norm = _normalize(translate_team(away, lang))

    if home_norm in text_norm and away_norm in text_norm:
        return True

    home_score = fuzz.partial_ratio(home_norm, text_norm)
    away_score = fuzz.partial_ratio(away_norm, text_norm)
    return home_score >= threshold and away_score >= threshold
