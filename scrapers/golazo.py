from scrapers.utils import fetch_dynamic_html

def get_schedule():
    """
    CBS Sports Golazo Network: canale FAST gratuito.
    Il palinsesto è su una pagina SPA.
    """
    urls = [
        "https://www.cbssports.com/watch/golazo-network",
        "https://www.cbssports.com/soccer/schedule/",
    ]
    return fetch_dynamic_html(urls)