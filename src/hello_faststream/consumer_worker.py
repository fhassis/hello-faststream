# src/hello_faststream/consumer.py
import logging
import os
from decimal import Decimal

from fast_depends.msgspec import MsgSpecSerializer
from faststream import FastStream, Logger
from faststream.nats import NatsBroker

from hello_faststream.schema import ProcessedSensorData, RawSensorData

logger = logging.getLogger(__name__)

# configures app and broker
broker = NatsBroker(os.environ["NATS_URL"], serializer=MsgSpecSerializer())
app = FastStream(broker)


@app.on_startup
async def on_start():
    """Worker initialization logic, executed when the process starts."""
    logger.info("Consumer worker started.")


@app.on_shutdown
async def on_stop():
    """Worker cleanup logic, executed when the process shuts down."""
    logger.info("Consumer worker stopped.")


@broker.subscriber("sensors.raw")
@broker.publisher("sensors.processed")
async def handle_telemetry(data: RawSensorData, logger: Logger) -> ProcessedSensorData:
    """
    Handles incoming raw readings and publish the processed results.
    """
    logger.debug(f"Consumer reading: {data.sensor_read}")

    # Calculate a doubled adjustment using Decimal for mathematical accuracy
    val = (data.sensor_read * Decimal("2.0")).quantize(Decimal("0.01"))

    # publishes processed data back to NATS, with schema validation via msgspec for low-latency serialization
    return ProcessedSensorData(
        occurred_at=data.occurred_at,
        processed_value=val,
        status="VALIDATED",
    )
