from scrapers.utils import fetch_dynamic_html

def get_schedule():
    """
    Match TV: canale federale russo free-to-air.
    Il sito richiede JavaScript.
    """
    urls = [
        "https://matchtv.ru/tvguide",
        "https://matchtv.ru/program",
    ]
    return fetch_dynamic_html(urls)