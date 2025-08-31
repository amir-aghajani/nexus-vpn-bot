from enum import Enum

from pydantic import BaseModel


class PaymentMethodType(str, Enum):
    card_transfer = 'cardTransfer'
    zarinpal = 'zarinpal'
    cryptocurrency = 'cryptocurrency'


class PaymentMethodBase(BaseModel):
    name: str
    api_key: str | None = None
    type: PaymentMethodType
