from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.booking import Booking, BookingState
from app.models.trip import TripStatus
from app.schemas.booking_schema import BookingCreate, WebhookPayload
from app.daos import trip_dao, booking_dao


def create_booking(db: Session, trip_id: str, data: BookingCreate) -> Booking:
    trip = trip_dao.get_trip(db, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    if trip.status != TripStatus.PUBLISHED:
        raise HTTPException(status_code=400, detail="Trip is not available for booking")
    if trip.available_seats < data.num_seats:
        raise HTTPException(status_code=409, detail="Not enough seats available")

    trip_dao.decrement_seats(db, trip_id, data.num_seats)

    booking = Booking(
        trip_id=trip_id,
        user_id=data.user_id,
        num_seats=data.num_seats,
        state=BookingState.PENDING_PAYMENT,
        price_at_booking=float(trip.price) * data.num_seats,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=15),
    )
    return booking_dao.create_booking(db, booking)


def handle_webhook(db: Session, payload: WebhookPayload) -> dict:
    if payload.idempotency_key:
        existing = booking_dao.get_booking_by_idempotency_key(db, payload.idempotency_key)
        if existing:
            return {"status": "already_processed"}

    booking = booking_dao.get_booking(db, payload.booking_id)
    if not booking:
        return {"status": "booking_not_found"}

    if booking.state != BookingState.PENDING_PAYMENT:
        return {"status": "ignored", "reason": "booking not in pending state"}

    if payload.status == "success":
        booking.state = BookingState.CONFIRMED
    else:
        booking.state = BookingState.EXPIRED
        trip_dao.increment_seats(db, booking.trip_id, booking.num_seats)

    booking.idempotency_key = payload.idempotency_key
    booking_dao.update_booking(db, booking)
    return {"status": "processed"}


def cancel_booking(db: Session, booking_id: str) -> Booking:
    booking = booking_dao.get_booking(db, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.state in (BookingState.CANCELLED, BookingState.EXPIRED):
        raise HTTPException(status_code=409, detail=f"Cannot cancel a {booking.state.value} booking")
    if booking.state == BookingState.PENDING_PAYMENT:
        raise HTTPException(status_code=409, detail="Cannot cancel a booking that has not been confirmed")

    trip = trip_dao.get_trip(db, booking.trip_id)
    days_to_trip = (trip.start_date - datetime.now(timezone.utc)).days

    if days_to_trip > trip.refundable_until_days_before:
        refund = float(booking.price_at_booking) * (1 - trip.cancellation_fee_percent / 100)
        trip_dao.increment_seats(db, booking.trip_id, booking.num_seats)
    else:
        refund = 0.0

    booking.state = BookingState.CANCELLED
    booking.cancelled_at = datetime.now(timezone.utc)
    booking.refund_amount = refund
    return booking_dao.update_booking(db, booking)
