from decimal import Decimal

from faststream import Logger

from hello_faststream.app_factory import create_app
from hello_faststream.log_settings import get_logger
from hello_faststream.schema import ProcessedSensorData, RawSensorData

# configures app and broker via the factory, which also sets up structured logging
app, broker = create_app("consumer")

# Logger injection via FastStream's DI only works in subscriber handlers, not lifecycle hooks
logger = get_logger(__name__)


@app.on_startup
async def on_start() -> None:
    """Worker initialization logic, executed when the process starts."""
    logger.info("Consumer worker started.")


@app.on_shutdown
async def on_stop() -> None:
    """Worker cleanup logic, executed when the process shuts down."""
    logger.info("Consumer worker stopped.")


@broker.subscriber("sensors.raw")
@broker.publisher("sensors.processed")
async def handle_telemetry(data: RawSensorData, logger: Logger) -> ProcessedSensorData:
    """Handles incoming raw readings and publishes the processed results."""
    logger.debug(f"Consumed: {data.sensor_read}")

    # calculate a 2x adjustment using Decimal for mathematical accuracy
    val = (data.sensor_read * Decimal("2.0")).quantize(Decimal("0.01"))

    # publishes processed data back to NATS, with schema validation via msgspec for low-latency serialization
    return ProcessedSensorData(
        occurred_at=data.occurred_at,
        processed_value=val,
        status="VALIDATED",
    )
