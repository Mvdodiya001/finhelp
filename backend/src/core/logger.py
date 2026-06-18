"""
Structured Logging — Replaces all print() statements with proper Python logging.

Provides a consistent log format across all modules:
  [2026-06-16 12:00:00] [ModuleName] [INFO] Message content here
"""
import logging
import sys


def setup_logging(level: int = logging.INFO) -> None:
    """
    Configure the root logger with a structured formatter.
    Call this once at application startup (in main.py).
    """
    formatter = logging.Formatter(
        fmt="[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Avoid duplicate handlers on reload
    if not root_logger.handlers:
        root_logger.addHandler(handler)

    # Suppress noisy third-party loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("yfinance").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Factory method to get a named logger for any module.

    Usage:
        from src.core.logger import get_logger
        logger = get_logger(__name__)
        logger.info("Fetching data for RELIANCE.NS")
    """
    return logging.getLogger(name)
