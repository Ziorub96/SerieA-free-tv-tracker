from scrapers.utils import fetch_dynamic_html

def get_schedule():
    """
    New World TV: pay TV con match sub-licenziati free.
    Il sito blocca requests (403); usa Playwright.
    """
    urls = [
        "https://www.newworldtv.com",
        "https://www.newworldtv.com/programmes",
    ]
    return fetch_dynamic_html(urls)