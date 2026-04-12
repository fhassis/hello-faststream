from datetime import datetime
from decimal import Decimal

from msgspec import Struct


class RawSensorData(Struct):
    occurred_at: datetime
    sensor_read: Decimal


class ProcessedSensorData(Struct):
    occurred_at: datetime
    processed_value: Decimal
    status: str
