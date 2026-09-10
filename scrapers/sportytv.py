from scrapers.utils import fetch_dynamic_html

def get_schedule():
    """
    SportyTV: app gratuita per l'Africa subsahariana.
    Il sito è una SPA che richiede JavaScript.
    """
    urls = [
        "https://sporty.com/tv",
        "https://www.sportytv.com/schedule",
    ]
    return fetch_dynamic_html(urls)