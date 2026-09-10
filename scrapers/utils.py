from rapidfuzz import fuzz
from bs4 import BeautifulSoup
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


def extract_visible_text(html: str) -> str:
    """
    Estrae SOLO il testo visibile da un HTML, rimuovendo script/style/tag.
    Fondamentale: fare fuzzy matching sull'HTML grezzo produce falsi
    positivi quasi garantiti su pagine grandi.
    """
    if not html:
        return ""
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "noscript", "svg", "path"]):
        tag.decompose()
    return soup.get_text(" ", strip=True)


def match_game(text, home, away, lang="it", threshold=90, window=300):
    """
    True solo se home e away compaiono entrambi, vicini tra loro
    (entro `window` caratteri), nel testo VISIBILE della pagina.
    Soglia alzata a 90 perché ora operiamo su testo pulito, non su HTML:
    su testo pulito una soglia alta è finalmente significativa.
    """
    if not text or len(text) < 20:
        return False

    text_lower = text.lower()
    home_t = translate_team(home, lang).lower()
    away_t = translate_team(away, lang).lower()

    # Match diretto: entrambe le squadre nella stessa finestra di testo
    idx_home = text_lower.find(home_t)
    if idx_home == -1:
        # fallback fuzzy solo per trovare la posizione approssimativa
        home_score = fuzz.partial_ratio(home_t, text_lower)
        if home_score < threshold:
            return False
        idx_home = 0  # non sappiamo dove, controlliamo tutto il testo

    start = max(0, idx_home - window)
    end = idx_home + len(home_t) + window
    local_text = text_lower[start:end]

    if away_t in local_text:
        return True

    away_score = fuzz.partial_ratio(away_t, local_text)
    return away_score >= threshold


def fetch_dynamic_html(urls, wait_ms=3000):
    """
    Scarica pagine SPA con Playwright e restituisce TESTO VISIBILE
    (non HTML grezzo) di ognuna.
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
                    text = extract_visible_text(html)
                    # Una pagina di blocco/errore geografico è quasi sempre
                    # molto corta in testo visibile, anche se l'HTML "vuoto"
                    # pesa migliaia di caratteri di markup.
                    if len(text) > 200:
                        pages.append(text)
                    else:
                        print(f"  [Playwright] {url}: pagina troppo corta ({len(text)} caratteri) — probabile blocco/geoblocking")
                except Exception as e:
                    print(f"  [Playwright] {url}: {e}")

            browser.close()
    except Exception as e:
        print(f"  [Playwright] errore generale: {e}")

    return pages
