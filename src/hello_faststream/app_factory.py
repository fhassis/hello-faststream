import logging
import os

from fast_depends.msgspec import MsgSpecSerializer
from faststream import FastStream
from faststream.nats import NatsBroker

from hello_faststream.log_settings import configure_logging, shutdown_logging


def create_app(title: str) -> tuple[FastStream, NatsBroker]:
    """
    Create and configure a FastStream app and NatsBroker for a named worker.

    Initialises structured logging, wires a stdlib logger into both the broker
    and the app so FastStream's internal messages flow through the same pipeline,
    and registers a shutdown hook to flush the log queue on exit.
    """
    configure_logging(title)

    logger = logging.getLogger(f"hello_faststream.{title}")
    broker = NatsBroker(os.environ["NATS_URL"], serializer=MsgSpecSerializer(), logger=logger)
    app = FastStream(broker, logger=logger)

    @app.on_shutdown
    async def _stop_logging() -> None:
        shutdown_logging()

    return app, broker
