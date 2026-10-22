"""Structured logging configuration."""

import logging
import sys

from app.config.settings import settings

try:
    from pythonjsonlogger import jsonlogger
    _HAS_JSON_LOGGER = True
except ImportError:  # pragma: no cover
    _HAS_JSON_LOGGER = False


class CustomJsonFormatter(jsonlogger.JsonFormatter if _HAS_JSON_LOGGER else object):
    """JSON formatter that adds standard fields."""

    def add_fields(self, log_record, record, message_dict):
        if _HAS_JSON_LOGGER:
            super().add_fields(log_record, record, message_dict)
        log_record["level"] = record.levelname
        log_record["logger"] = record.name
        log_record["environment"] = settings.ENVIRONMENT
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)


def setup_logging() -> None:
    """Configure root logger with console handler."""
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)

    # Remove existing handlers to avoid duplicates on reload
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    console_handler = logging.StreamHandler(sys.stdout)

    if settings.is_production and _HAS_JSON_LOGGER:
        formatter = CustomJsonFormatter("%(asctime)s %(level)s %(name)s %(message)s")
    else:
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Reduce noise from third-party libraries
    noisy_loggers = [
        "httpx",
        "httpcore",
        "urllib3",
        "asyncio",
        "playwright",
        "chromadb",
        "google.generativeai",
        "sqlalchemy.engine",
    ]
    for noisy in noisy_loggers:
        logging.getLogger(noisy).setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Return a logger instance for the given name."""
    return logging.getLogger(name)