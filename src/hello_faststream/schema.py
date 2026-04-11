from msgspec import Struct
from decimal import Decimal

class Trade(Struct):
    symbol: str
    price: Decimal
    amount: Decimal
    exchange: str
