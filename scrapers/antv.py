import requests

def get_schedule():
    """
    ANTV: free-to-air indonesiano.
    Il sito ha una pagina programmazione statica.
    """
    pages = []
    urls = [
        "https://www.antvklik.com",
        "https://www.antvklik.com/jadwal-acara",
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
            print(f"  [ANTV] {url}: {e}")
    return pages