"""Logging configuration for AuroraAgent."""

import logging
import sys


def setup_logging(level: str = "INFO", format_string: str = None):
    """Configure logging for Aurora.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_string: Custom format string
    """
    fmt = format_string or "%(asctime)s [%(levelname)s] %(name)s: %(message)s"

    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format=fmt,
        stream=sys.stderr,
        force=True,
    )

    # Quiet noisy third-party loggers
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
