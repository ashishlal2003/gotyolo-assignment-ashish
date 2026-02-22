from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models import BookingState

class BookingCreate(BaseModel):
    user_id: str
    num_seats: int

class BookingResponse(BaseModel):
    id: str
    trip_id: str
    user_id: str
    num_seats: int
    state: BookingState
    price_at_booking: float
    payment_reference: Optional[str]
    expires_at: datetime
    cancelled_at: Optional[datetime]
    refund_amount: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True

class WebhookPayload(BaseModel):
    booking_id: str
    status: str
    idempotency_key: Optional[str]

class CancelResponse(BaseModel):
    booking_id: str
    state: BookingState
    refund_amount: float
