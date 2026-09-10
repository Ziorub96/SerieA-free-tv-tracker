import requests
from bs4 import BeautifulSoup

def get_schedule():
    """
    LiveSoccerTV: aggregatore globale di palinsesti TV.
    Copre tutti i broadcaster (XSports, SportyTV, CBS Golazo,
    Telemundo, ANTV, Match TV, New World TV, ELTA, ecc.).
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
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, "lxml")

                # Estrai tutte le righe della tabella partite
                table = soup.find("table", class_="table")
                if table:
                    for row in table.find_all("tr"):
                        cells = row.find_all("td")
                        if len(cells) >= 3:
                            # Combina tutte le celle in un unico testo
                            text = " ".join(c.get_text(" ", strip=True) for c in cells)
                            if text and len(text) > 20:
                                pages.append(text)

                # Fallback: estrai tutto il testo rilevante
                if not pages:
                    for div in soup.find_all("div", class_="match"):
                        text = div.get_text(" ", strip=True)
                        if text and len(text) > 20:
                            pages.append(text)

        except Exception as e:
            print(f"  [LiveSoccerTV] {url}: {e}")

    return pages