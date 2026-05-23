import logging
import os

LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG").upper()


def _configure_logger():
    logger = logging.getLogger("nvidianemotron")
    if not logger.handlers:
        handler = logging.StreamHandler()
        fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        handler.setFormatter(logging.Formatter(fmt))
        logger.addHandler(handler)
    try:
        logger.setLevel(getattr(logging, LOG_LEVEL))
    except Exception:
        logger.setLevel(logging.INFO)
    return logger


_LOGGER = _configure_logger()


def get_logger(name: str = None):
    """Return a namespaced logger for the project.

    Usage:
        from logger_config import get_logger
        logger = get_logger(__name__)
    """
    if name:
        return _LOGGER.getChild(name)
    return _LOGGER
