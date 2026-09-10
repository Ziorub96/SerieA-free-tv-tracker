"""
Session HTTP condivisa con retry automatici e backoff.
Tutti gli scraper la usano invece di chiamare requests.get() direttamente,
così i tentativi falliti (timeout, 429, 5xx, 403) vengono ritentati in modo
uniforme senza duplicare la logica in ogni file.
"""

import logging
import time

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

import config

logger = logging.getLogger("seriea_tracker")


def build_session() -> requests.Session:
    session = requests.Session()
    session.headers.update(config.DEFAULT_HEADERS)

    # Retry anche sui 403 (ESPN a volte blocca i runner di GitHub Actions)
    retry = Retry(
        total=config.REQUEST_RETRIES,
        backoff_factor=config.REQUEST_BACKOFF_SECONDS,
        status_forcelist=(403, 429, 500, 502, 503, 504),
        allowed_methods=("GET", "HEAD"),
        raise_on_status=False,
        respect_retry_after_header=True,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


SESSION = build_session()


def fetch_pages(urls, timeout: int = None) -> list[str]:
    """
    Scarica una lista di URL e restituisce il testo delle risposte con status 200.
    Gli errori (timeout, DNS, 4xx/5xx residui dopo i retry) vengono loggati come
    warning e non interrompono lo scraping degli altri URL/broadcaster.
    """
    timeout = timeout or config.REQUEST_TIMEOUT
    pages = []
    for url in urls:
        try:
            resp = SESSION.get(url, timeout=timeout)
            if resp.status_code == 200:
                pages.append(resp.text)
            else:
                logger.warning("GET %s -> HTTP %s", url, resp.status_code)
        except requests.RequestException as exc:
            logger.warning("GET %s fallita: %s", url, exc)
    return pages


def safe_scrape(name: str, func):
    """
    Esegue una funzione di scraping catturando qualunque eccezione, così un
    broadcaster che va in errore non blocca l'esecuzione degli altri.
    Restituisce sempre una lista (eventualmente vuota).
    """
    start = time.monotonic()
    try:
        pages = func() or []
        logger.info(
            "%s: %d pagine recuperate in %.1fs", name, len(pages), time.monotonic() - start
        )
        return pages
    except Exception as exc:  # scraper di terze parti: meglio essere permissivi qui
        logger.error("%s: errore durante lo scraping - %s", name, exc, exc_info=True)
        return []