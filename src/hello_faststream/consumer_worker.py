from decimal import Decimal

from faststream import Logger
from faststream.nats import PullSub

from hello_faststream.app_factory import SENSORS_STREAM, create_app
from hello_faststream.schema import ProcessedSensorData, RawSensorData

# gets a reference to the app and broker
app, broker = create_app("consumer_worker")


# durable= makes JetStream remember the last-acked message for this consumer across restarts,
# so missed messages are replayed when the worker comes back up.
# PullSub is the recommended pattern for durable consumers — it also allows horizontal scaling
# (multiple instances with the same durable pull from the same cursor).
@broker.subscriber(
    "sensors.raw",
    stream=SENSORS_STREAM,
    durable="consumer_worker",
    pull_sub=PullSub(batch_size=1),
)
@broker.publisher("sensors.processed", stream=SENSORS_STREAM)
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
