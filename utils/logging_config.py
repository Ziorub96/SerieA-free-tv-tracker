"""Configurazione logging condivisa: un logger nominato, output su console."""

import logging


def setup_logging(level=logging.INFO) -> logging.Logger:
    logger = logging.getLogger("seriea_tracker")
    if logger.handlers:  # evita handler duplicati se chiamata più volte
        return logger

    logger.setLevel(level)
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", "%H:%M:%S")
    )
    logger.addHandler(handler)
    return logger
