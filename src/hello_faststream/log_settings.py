import logging
import os
import sys

import structlog
from msgspec.json import encode as msgspec_encode


def configure_logging() -> None:
    """
    Configure structured JSON logging to stdout.

    Sets up the pipeline:
        structlog → stdlib → StreamHandler(stdout)
    """
    level_name = os.environ.get("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    # structlog — formats records as JSON before they hit stdlib
    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.ExceptionRenderer(),
            # msgspec is faster than stdlib json; decode bytes→str for stdlib logging compatibility
            structlog.processors.JSONRenderer(
                serializer=lambda obj, **_: msgspec_encode(obj).decode()
            ),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
    )

    root = logging.getLogger()
    root.setLevel(level)
    root.addHandler(logging.StreamHandler(sys.stdout))

    # Suppress noisy third-party loggers
    logging.getLogger("nats").setLevel(logging.WARNING)


def shutdown_logging() -> None:
    """No-op placeholder — retained for when OTLP export is re-added."""
    pass


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    return structlog.get_logger(name)
