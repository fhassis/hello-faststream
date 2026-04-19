import logging
import os

from fast_depends.msgspec import MsgSpecSerializer
from faststream import FastStream
from faststream.nats import JStream, NatsBroker
from nats.js.api import RetentionPolicy, StorageType

from hello_faststream.log_settings import configure_logging

# shared JetStream definition — both workers declare it (idempotent) so the
# stream exists whichever worker starts first. Covers both raw + processed
# subjects so replay/resume works across the full pipeline.
SENSORS_STREAM = JStream(
    name="SENSORS",
    subjects=["sensors.>"],
    # INTEREST: message is deleted once every bound consumer has acked it.
    # Supports fan-out (e.g. consumer + notifier) without keeping data forever.
    retention=RetentionPolicy.INTEREST,
    storage=StorageType.FILE,
    # Safety net: evict messages older than 60 days even if unacked (poison messages
    # that exhaust max_deliver stay in the stream otherwise).
    max_age=60 * 24 * 60 * 60,
)


def create_app(title: str) -> tuple[FastStream, NatsBroker]:
    """
    Create and configure a FastStream app and NatsBroker for a named worker.

    Initialises structured logging and wires a stdlib logger into both the
    broker and the app so FastStream's internal messages flow through the same
    pipeline.
    """

    # initializes application logginging
    configure_logging()

    # creates the application logger
    logger = logging.getLogger(title)

    # creates the message broker
    broker = NatsBroker(
        os.environ["NATS_URL"],
        serializer=MsgSpecSerializer(),
        logger=logger,
    )

    # creates the FastStream app
    app = FastStream(broker, logger=logger)

    @app.on_startup
    async def _on_startup() -> None:
        """Startup loggic for the worker."""
        logger.info("%s worker started.", title)

    @app.on_shutdown
    async def _on_shutdown() -> None:
        """Shutdown logic for the worker."""
        logger.info("%s worker stopped.", title)

    return app, broker
