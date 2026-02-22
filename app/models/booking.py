import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Numeric, DateTime, Enum as SAEnum, ForeignKey
from app.database import Base
import enum


class BookingState(str, enum.Enum):
    PENDING_PAYMENT = "PENDING_PAYMENT"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    trip_id = Column(String, ForeignKey("trips.id"), nullable=False)
    user_id = Column(String, nullable=False)
    num_seats = Column(Integer, nullable=False)
    state = Column(SAEnum(BookingState), nullable=False, default=BookingState.PENDING_PAYMENT)
    price_at_booking = Column(Numeric(10, 2), nullable=False)
    payment_reference = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    cancelled_at = Column(DateTime, nullable=True)
    refund_amount = Column(Numeric(10, 2), nullable=True)
    idempotency_key = Column(String, unique=True, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
