import requests

def get_schedule():
    """
    XSports: canale TV free-to-air brasiliano.
    Non ha una pagina programmazione web stabile.
    Prova a recuperare la homepage.
    """
    pages = []
    urls = [
        "https://www.xsports.com.br",
    ]
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    for url in urls:
        try:
            r = requests.get(url, timeout=20, headers=headers)
            if r.status_code == 200 and len(r.text) > 1000:
                pages.append(r.text)
        except Exception as e:
            print(f"  [XSports] {url}: {e}")
    return pages