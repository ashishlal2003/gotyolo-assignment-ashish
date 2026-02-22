from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.models.booking import BookingState
from app.models.trip import TripStatus
from app.daos import trip_dao, booking_dao


def get_trip_metrics(db: Session, trip_id: str) -> dict:
    from app.daos.trip_dao import get_trip
    trip = get_trip(db, trip_id)
    if not trip:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Trip not found")

    bookings = booking_dao.get_bookings_for_trip(db, trip_id)

    confirmed = [b for b in bookings if b.state == BookingState.CONFIRMED]
    pending   = [b for b in bookings if b.state == BookingState.PENDING_PAYMENT]
    cancelled = [b for b in bookings if b.state == BookingState.CANCELLED]
    expired   = [b for b in bookings if b.state == BookingState.EXPIRED]

    booked_seats = sum(b.num_seats for b in confirmed + pending)
    gross = sum(float(b.price_at_booking) for b in confirmed + cancelled)
    refunds = sum(float(b.refund_amount or 0) for b in cancelled)

    return {
        "trip_id": trip.id,
        "title": trip.title,
        "occupancy_percent": round(booked_seats / trip.max_capacity * 100) if trip.max_capacity else 0,
        "total_seats": trip.max_capacity,
        "booked_seats": booked_seats,
        "available_seats": trip.available_seats,
        "booking_summary": {
            "confirmed": len(confirmed),
            "pending_payment": len(pending),
            "cancelled": len(cancelled),
            "expired": len(expired),
        },
        "financial": {
            "gross_revenue": round(gross, 2),
            "refunds_issued": round(refunds, 2),
            "net_revenue": round(gross - refunds, 2),
        }
    }


def get_at_risk_trips(db: Session) -> dict:
    all_trips = trip_dao.get_all_trips(db)
    now = datetime.now(timezone.utc)
    at_risk = []

    for trip in all_trips:
        if trip.status != TripStatus.PUBLISHED:
            continue
        start = trip.start_date
        if start.tzinfo is None:
            start = start.replace(tzinfo=timezone.utc)
        days_until = (start - now).days
        if days_until > 7:
            continue
        booked = trip.max_capacity - trip.available_seats
        occupancy = booked / trip.max_capacity * 100 if trip.max_capacity else 0
        if occupancy < 50:
            at_risk.append({
                "trip_id": trip.id,
                "title": trip.title,
                "departure_date": trip.start_date.date().isoformat(),
                "occupancy_percent": round(occupancy),
                "reason": "Low occupancy with imminent departure"
            })

    return {"at_risk_trips": at_risk}
