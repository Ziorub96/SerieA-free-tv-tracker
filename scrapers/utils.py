from rapidfuzz import fuzz
from playwright.sync_api import sync_playwright

TEAM_TRANSLATIONS = {
    "es": {
        "Milan": "Milan", "Inter": "Inter de Milán", "Juventus": "Juventus",
        "Napoli": "Nápoles", "Roma": "Roma", "Lazio": "Lazio",
        "Fiorentina": "Fiorentina", "Atalanta": "Atalanta", "Bologna": "Bolonia",
        "Torino": "Turín", "Udinese": "Udinese", "Genoa": "Génova",
        "Cagliari": "Cagliari", "Lecce": "Lecce", "Verona": "Verona",
        "Parma": "Parma", "Como": "Como", "Monza": "Monza",
        "Venezia": "Venecia", "Frosinone": "Frosinone", "Sassuolo": "Sassuolo",
    },
    "fr": {
        "Milan": "Milan", "Inter": "Inter Milan", "Juventus": "Juventus",
        "Napoli": "Naples", "Roma": "Rome", "Lazio": "Lazio",
        "Fiorentina": "Fiorentina", "Atalanta": "Atalanta", "Bologna": "Bologne",
        "Torino": "Turin", "Udinese": "Udinese", "Genoa": "Gênes",
        "Cagliari": "Cagliari", "Lecce": "Lecce", "Verona": "Vérone",
        "Parma": "Parme", "Como": "Côme", "Monza": "Monza",
        "Venezia": "Venise", "Frosinone": "Frosinone", "Sassuolo": "Sassuolo",
    },
    "ru": {
        "Milan": "Милан", "Inter": "Интер", "Juventus": "Ювентус",
        "Napoli": "Наполи", "Roma": "Рома", "Lazio": "Лацио",
        "Fiorentina": "Фиорентина", "Atalanta": "Аталанта", "Bologna": "Болонья",
        "Torino": "Торино", "Udinese": "Удинезе", "Genoa": "Дженоа",
        "Cagliari": "Кальяри", "Lecce": "Лечче", "Verona": "Верона",
        "Parma": "Парма", "Como": "Комо", "Monza": "Монца",
        "Venezia": "Венеция", "Frosinone": "Фрозиноне", "Sassuolo": "Сассуоло",
    }
}


def translate_team(team_name, lang="it"):
    if lang == "it":
        return team_name
    return TEAM_TRANSLATIONS.get(lang, {}).get(team_name, team_name)


def match_game(text, home, away, lang="it", threshold=78):
    """Fuzzy matching con supporto multi-lingua."""
    if not text or len(text) < 50:
        return False

    text_lower = text.lower()
    home_t = translate_team(home, lang).lower()
    away_t = translate_team(away, lang).lower()

    # Controllo diretto
    if home_t in text_lower and away_t in text_lower:
        return True

    # Fuzzy matching
    home_score = fuzz.partial_ratio(home_t, text_lower)
    away_score = fuzz.partial_ratio(away_t, text_lower)

    return home_score >= threshold and away_score >= threshold


def fetch_dynamic_html(urls, wait_ms=3000):
    """
    Scarica HTML da siti SPA usando Playwright.
    Restituisce una lista di HTML renderizzati.
    """
    pages = []

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = context.new_page()

            for url in urls:
                try:
                    page.goto(url, timeout=30000, wait_until="domcontentloaded")
                    page.wait_for_timeout(wait_ms)
                    html = page.content()
                    if html and len(html) > 1000:
                        pages.append(html)
                except Exception as e:
                    print(f"  [Playwright] {url}: {e}")

            browser.close()
    except Exception as e:
        print(f"  [Playwright] errore generale: {e}")

    return pages