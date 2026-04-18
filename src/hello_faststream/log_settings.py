import logging
import os
import sys
from typing import Any

import structlog
from msgspec.json import encode as msgspec_encode
from opentelemetry import trace


def _add_otel_context(
    logger: Any, method: str, event_dict: dict[str, Any]
) -> dict[str, Any]:
    """Inject OTel trace_id and span_id into each log record.

    No-op when there is no active span so it is safe to call unconditionally.
    The IDs use the standard 32-hex / 16-hex format that Grafana expects for
    log-to-trace correlation in Loki → Tempo.
    """
    span = trace.get_current_span()
    ctx = span.get_span_context()
    if ctx.is_valid:
        event_dict["trace_id"] = format(ctx.trace_id, "032x")
        event_dict["span_id"] = format(ctx.span_id, "016x")
    return event_dict


def configure_logging() -> None:
    """
    Configure structured JSON logging to stdout.

    Sets up the pipeline:
        structlog → stdlib → StreamHandler(stdout)

    Each log record emitted inside an active OTel span will carry
    ``trace_id`` and ``span_id`` fields, enabling log-to-trace correlation
    in Grafana (Loki → Tempo).  A log collector (Alloy / Promtail) is
    expected to scrape stdout and forward records to Loki.
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
            _add_otel_context,
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


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    return structlog.get_logger(name)
