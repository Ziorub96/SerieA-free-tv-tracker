from scrapers.utils import fetch_dynamic_html

def get_schedule():
    """
    Telemundo: free-to-air OTA negli USA (spagnolo).
    Il sito è una SPA.
    """
    urls = [
        "https://www.telemundo.com/deportes",
        "https://www.telemundo.com/deportes/futbol",
    ]
    return fetch_dynamic_html(urls)