from decimal import Decimal

from faststream import Logger

from hello_faststream.app_factory import create_app
from hello_faststream.schema import ProcessedSensorData, RawSensorData

# gets a reference to the app and broker
app, broker = create_app("consumer_worker")


@broker.subscriber("sensors.raw")
@broker.publisher("sensors.processed")
async def handle_telemetry(data: RawSensorData, logger: Logger) -> ProcessedSensorData:
    """Handles incoming raw readings and publishes the processed results."""

    # logs the raw sensor reading at debug level
    logger.debug(f"Consumed: {data.sensor_read}")

    # calculate a 2x adjustment using Decimal for mathematical accuracy
    val = (data.sensor_read * Decimal("2.0")).quantize(Decimal("0.01"))

    # publishes processed data back to NATS, with schema validation via msgspec for low-latency serialization
    return ProcessedSensorData(
        occurred_at=data.occurred_at,
        processed_value=val,
        status="VALIDATED",
    )
