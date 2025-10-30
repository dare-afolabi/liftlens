
import sys
from pathlib import Path

from loguru import logger

from ..config.settings import settings


def setup_logging(level: str | None = None) -> None:
    """
    Configure structured JSON logging with rotation.
    """
    logger.remove()  # Remove default handler

    level = level or settings.log_level

    # Console (human-readable)
    logger.add(
        sys.stderr,
        level=level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        colorize=True
    )

    # JSON file (structured)
    log_path = Path("logs") / "liftlens_{time:YYYY-MM-DD}.json"
    logger.add(
        log_path,
        rotation="10 MB",
        retention="7 days",
        compression="zip",
        serialize=True,
        level="DEBUG"
    )

    logger.info(f"Logging initialized: level={level}, JSON logs → {log_path.parent}")


