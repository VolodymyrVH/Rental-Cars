from datetime import datetime
from enum import Enum
from pydantic import BaseModel
from decimal import Decimal


class RentalStatus(str, Enum):
    NOT_STARTED: str = "NOT_STARTED"
    ACTIVE: str = "ACTIVE"
    FINISHED: str = "FINISHED"


class PaymentStatus(str, Enum):
    PAID: str = "PAID"
    NOT_PAID: str = "NOT_PAID"


class RentalCreateSchema(BaseModel):
    car_id: int
    user_id: int
    start_date: datetime
    end_date: datetime


class RentalResponseSchema(BaseModel):
    id: int
    car_id: int
    user_id: int
    start_date: datetime
    end_date: datetime
    price_sum: Decimal
    created_at: datetime
    status: RentalStatus

    model_config = {"from_attributes": True}


class PaymentCreateSchema(BaseModel):
    rental_id: int
    amount: Decimal
    payment_method: str


class PaymentResponseSchema(BaseModel):
    id: int
    rental_id: int
    amount: Decimal
    payment_method: str
    status: PaymentStatus
    paid_at: datetime | None

    model_config = {"from_attributes": True}