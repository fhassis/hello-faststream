import asyncio
import logging
import os
import random
from datetime import datetime, timezone
from decimal import Decimal

from faststream import FastStream
from faststream.nats import NatsBroker
from fast_depends.msgspec import MsgSpecSerializer

from hello_faststream.schema import RawSensorData

logger = logging.getLogger(__name__)

# configures app and broker
broker = NatsBroker(os.environ["NATS_URL"], serializer=MsgSpecSerializer())
app = FastStream(broker)


@app.on_startup
async def on_start():
    """Worker initialization logic, executed when the process starts."""
    logger.info("Producer worker started.")


@app.on_shutdown
async def on_stop():
    """Worker cleanup logic, executed when the process shuts down."""
    logger.info("Producer worker stopped.")


@app.after_startup
async def publish_telemetry():
    """
    Generates and publishes fake telemetry data.
    """
    logger.debug("Producer loop started.")
    while True:
        try:
            # creates a fake sensor reading with a timestamp and a random value
            data = RawSensorData(
                occurred_at=datetime.now(timezone.utc),
                sensor_read=Decimal(random.uniform(20.0, 30.0)).quantize(
                    Decimal("0.01")
                ),
            )

            # FastStream handles serialization via msgspec for low-latency
            await broker.publish(data, subject="sensors.raw")

        except Exception as e:
            # Catch exceptions to prevent the loop from crashing the worker
            logger.error(f"Production error: {e}")

        # Throttling the production rate
        await asyncio.sleep(2)
