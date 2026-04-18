import logging
import os

from fast_depends.msgspec import MsgSpecSerializer
from faststream import FastStream
from faststream.nats import NatsBroker

from hello_faststream.log_settings import configure_logging


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
