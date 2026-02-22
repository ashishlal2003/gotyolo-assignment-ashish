from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timezone
from app.models import Booking, BookingState

def get_booking(db: Session, booking_id: str) -> Optional[Booking]:
    return db.query(Booking).filter(Booking.id == booking_id).first()

def create_booking(db: Session, booking: Booking) -> Booking:
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking

def update_booking(db: Session, booking: Booking) -> Booking:
    db.commit()
    db.refresh(booking)
    return booking

def get_booking_by_idempotency_key(db: Session, key: str) -> Optional[Booking]:
    return db.query(Booking).filter(Booking.idempotency_key == key).first()

def get_expired_pending_bookings(db: Session) -> list[Booking]:
    return db.query(Booking).filter(Booking.state == BookingState.PENDING_PAYMENT, Booking.expires_at < datetime.now(timezone.utc)).all()

def get_bookings_for_trip(db: Session, trip_id: str) -> list[Booking]:
    return db.query(Booking).filter(Booking.trip_id == trip_id).all()
