import logging
from pathlib import Path

LOG_FILE = Path.home() / ".nice" / "nice.log"
_configured = False


def setup_logging(level: str = "warning") -> None:
    global _configured
    if _configured:
        return

    numeric = getattr(logging, level.upper(), logging.WARNING)

    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)-8s] %(name)s — %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    ))

    logger = logging.getLogger("nice")
    logger.setLevel(numeric)
    logger.addHandler(file_handler)
    logger.propagate = False

    _configured = True


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(f"nice.{name}")
