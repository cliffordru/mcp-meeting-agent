"""
Configures structured logging for the application using structlog.
"""
import logging
import logging.config
import sys
import os
import structlog
from structlog.types import Processor

from .config import settings

SILENT_LOGGERS = ["pytest", "test"]

def setup_logging():
    """
    Configures structlog for structured logging.
    Logs will be written to console and optionally to a local file.
    """
    # Configure structlog
    timestamper = structlog.processors.TimeStamper(fmt="iso")

    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        timestamper,
        structlog.processors.StackInfoRenderer(),
    ]

    structlog.configure(
        processors=shared_processors + [
            structlog.processors.dict_tracebacks,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Handlers for both console and file output
    handlers = {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "console",
        },
    }
    active_handlers = ["console"]

    # Conditional File Handler - only if not running under pytest
    if "pytest" not in sys.modules:
        # Ensure the logs directory exists
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        log_file_path = os.path.join(log_dir, "meeting_agent.log")
        print(f"File logging is enabled. Logs will be written to {log_file_path}")

        handlers["file"] = {
            "class": "logging.handlers.WatchedFileHandler",
            "filename": log_file_path,
            "formatter": "json",
        }
        active_handlers.append("file")

    logging.config.dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": "structlog.stdlib.ProcessorFormatter",
                "processor": structlog.processors.JSONRenderer(),
                "foreign_pre_chain": shared_processors,
            },
            "console": {
                "()": "structlog.stdlib.ProcessorFormatter",
                "processor": structlog.dev.ConsoleRenderer(),
                "foreign_pre_chain": shared_processors,
            },
        },
        "handlers": handlers,
        "loggers": {
            "": {
                "handlers": active_handlers,
                "level": settings.LOG_LEVEL,
                "propagate": True,
            },
            **{name: {"handlers": [], "level": "WARNING"} for name in SILENT_LOGGERS}
        }
    })

def get_logger(name: str):
    """
    Returns a structlog logger instance for the given name.
    """
    return structlog.get_logger(name)
