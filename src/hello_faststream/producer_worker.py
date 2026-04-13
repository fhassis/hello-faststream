import asyncio
import random
from datetime import datetime, timezone
from decimal import Decimal

from msgspec.json import encode as msgspec_encode

from hello_faststream.app_factory import create_app
from hello_faststream.log_settings import get_logger
from hello_faststream.schema import RawSensorData

# configures app and broker via the factory, which also sets up structured logging
app, broker = create_app("producer")

# Logger injection via FastStream's DI only works in subscriber handlers, not lifecycle hooks
logger = get_logger(__name__)


@app.on_startup
async def on_start() -> None:
    """Worker initialization logic, executed when the process starts."""
    logger.info("Producer worker started.")


@app.on_shutdown
async def on_stop() -> None:
    """Worker cleanup logic, executed when the process shuts down."""
    logger.info("Producer worker stopped.")


@app.after_startup
async def start_produce_loop() -> None:
    """Starts the produce loop after the broker connection is established."""
    asyncio.create_task(_produce_loop())


async def _produce_loop() -> None:
    """Publishes a fake sensor reading every 2 seconds."""
    while True:
        # creates a fake sensor reading with a timestamp and a random value
        data = RawSensorData(
            occurred_at=datetime.now(timezone.utc),
            sensor_read=Decimal(random.uniform(20.0, 30.0)).quantize(Decimal("0.01")),
        )

        # encode to bytes via msgspec before publishing — FastStream's json.dumps doesn't handle msgspec.Struct
        await broker.publish(msgspec_encode(data), subject="sensors.raw")
        logger.debug(f"Produced: {data.sensor_read}")

        # throttle the production rate
        await asyncio.sleep(2)
