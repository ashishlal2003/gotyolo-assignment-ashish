import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Numeric, DateTime, Enum as SAEnum
from app.database import Base
import enum


class TripStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"

class Trip(Base):
    __tablename__ = "trips"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    price = Column(Numeric, nullable=False)
    max_capacity = Column(Integer, nullable=False)
    available_seats = Column(Integer, nullable=False, default=0)
    status = Column(SAEnum(TripStatus), nullable=False, default=TripStatus.DRAFT)
    refundable_until_days_before = Column(Integer, nullable=False, default=7)
    cancellation_fee_percent = Column(Integer, nullable=False, default=10)
    created_at = Column(DateTime, nullable=False, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=datetime.now(timezone.utc))
