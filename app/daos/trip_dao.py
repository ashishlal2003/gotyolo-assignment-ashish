from sqlalchemy.orm import Session
from typing import Optional
from app.models import Trip, TripStatus


def get_trip(db: Session, trip_id: str) -> Optional[Trip]:
    return db.query(Trip).filter(Trip.id == trip_id).first()


def get_all_published_trips(db: Session, destination: Optional[str] = None) -> list[Trip]:
    query = db.query(Trip).filter(Trip.status == TripStatus.PUBLISHED)
    if destination:
        query = query.filter(Trip.destination.ilike(f"%{destination}%"))
    return query.all()


def create_trip(db: Session, trip: Trip) -> Trip:
    db.add(trip)
    db.commit()
    db.refresh(trip)
    return trip


def decrement_seats(db: Session, trip_id: str, n: int):
    db.query(Trip).filter(Trip.id == trip_id).update(
        {"available_seats": Trip.available_seats - n}
    )


def increment_seats(db: Session, trip_id: str, n: int):
    db.query(Trip).filter(Trip.id == trip_id).update(
        {"available_seats": Trip.available_seats + n}
    )


def get_all_trips(db: Session) -> list[Trip]:
    return db.query(Trip).all()
