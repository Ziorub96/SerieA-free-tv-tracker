import requests
from bs4 import BeautifulSoup

def get_schedule():
    """
    LiveSoccerTV: aggregatore globale di palinsesti TV.
    Estrae ogni riga della tabella partite come testo separato.
    """
    pages = []
    urls = [
        "https://www.livesoccertv.com/competitions/italy/serie-a/",
    ]
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    for url in urls:
        try:
            r = requests.get(url, timeout=30, headers=headers)
            if r.status_code != 200:
                print(f"  [LiveSoccerTV] HTTP {r.status_code} su {url}")
                continue

            soup = BeautifulSoup(r.text, "lxml")

            # Strategia 1: righe della tabella partite
            # LiveSoccerTV usa table con classe "table" o righe con classe "matchrow"
            found = 0

            # Prova tutti i selettori noti
            selectors = [
                ("table", {"class_": "table"}),
                ("table", {"class_": "matches"}),
                ("tr", {"class_": "matchrow"}),
                ("tr", {"itemtype": "http://schema.org/SportsEvent"}),
            ]

            rows = []
            for tag, attrs in selectors:
                found_rows = soup.find_all(tag, **attrs)
                if found_rows:
                    rows.extend(found_rows)

            for row in rows:
                text = row.get_text(" ", strip=True)
                if text and len(text) > 20:
                    pages.append(text)
                    found += 1

            # Strategia 2: fallback su tutto il testo strutturato
            if found == 0:
                for div in soup.find_all(["div", "li"], class_=lambda c: c and ("match" in c.lower() or "event" in c.lower())):
                    text = div.get_text(" ", strip=True)
                    if text and len(text) > 20:
                        pages.append(text)
                        found += 1

            print(f"  [LiveSoccerTV] {found} righe estratte da {url}")

        except Exception as e:
            print(f"  [LiveSoccerTV] {url}: {e}")

    return pages