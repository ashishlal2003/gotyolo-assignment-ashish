from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.trip import Trip, TripStatus
from app.schemas.trip_schema import TripCreate
from app.daos import trip_dao


def create_trip(db: Session, data: TripCreate) -> Trip:
    trip = Trip(
        title=data.title,
        destination=data.destination,
        start_date=data.start_date,
        end_date=data.end_date,
        price=data.price,
        max_capacity=data.max_capacity,
        available_seats=data.max_capacity,
        status=TripStatus.DRAFT,
        refundable_until_days_before=data.refundable_until_days_before,
        cancellation_fee_percent=data.cancellation_fee_percent,
    )
    return trip_dao.create_trip(db, trip)


def get_trip(db: Session, trip_id: str) -> Trip:
    trip = trip_dao.get_trip(db, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip


def list_trips(db: Session, destination: str = None) -> list[Trip]:
    return trip_dao.get_all_published_trips(db, destination)
