from pydantic import BaseModel
from datetime import datetime
from app.models.trip import TripStatus


class TripCreate(BaseModel):
    title: str
    destination: str
    start_date: datetime
    end_date: datetime
    price: float
    max_capacity: int
    refundable_until_days_before: int = 7
    cancellation_fee_percent: int = 10


class TripResponse(BaseModel):
    id: str
    title: str
    destination: str
    start_date: datetime
    end_date: datetime
    price: float
    max_capacity: int
    available_seats: int
    status: TripStatus
    refundable_until_days_before: int
    cancellation_fee_percent: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
