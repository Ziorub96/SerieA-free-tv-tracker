from scrapers.utils import fetch_dynamic_html

def get_schedule():
    """
    ELTA: OTT freemium taiwanese.
    Il palinsesto è caricato via JavaScript.
    """
    urls = [
        "https://eltaott.tv/sports_program_detail",
        "https://eltaott.tv/sports",
    ]
    return fetch_dynamic_html(urls)