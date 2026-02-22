import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta, timezone
from app.database import SessionLocal, Base, engine
from app.models import Trip, Booking
from app.models.trip import TripStatus
from app.models.booking import BookingState

Base.metadata.create_all(bind=engine)

db = SessionLocal()

db.query(Booking).delete()
db.query(Trip).delete()
db.commit()

now = datetime.now(timezone.utc)

trips = [
    Trip(
        id="trip-001",
        title="Paris City Tour",
        destination="Paris",
        start_date=now + timedelta(days=30),
        end_date=now + timedelta(days=37),
        price=500.00,
        max_capacity=20,
        available_seats=5,
        status=TripStatus.PUBLISHED,
        refundable_until_days_before=7,
        cancellation_fee_percent=10,
    ),
    Trip(
        id="trip-002",
        title="Bali Beach Escape",
        destination="Bali",
        start_date=now + timedelta(days=5),
        end_date=now + timedelta(days=12),
        price=800.00,
        max_capacity=10,
        available_seats=7,
        status=TripStatus.PUBLISHED,
        refundable_until_days_before=7,
        cancellation_fee_percent=15,
    ),
    Trip(
        id="trip-003",
        title="Tokyo Food Trail",
        destination="Tokyo",
        start_date=now + timedelta(days=60),
        end_date=now + timedelta(days=67),
        price=1200.00,
        max_capacity=15,
        available_seats=15,
        status=TripStatus.PUBLISHED,
        refundable_until_days_before=14,
        cancellation_fee_percent=0,
    ),
    Trip(
        id="trip-004",
        title="Rome History Walk",
        destination="Rome",
        start_date=now + timedelta(days=90),
        end_date=now + timedelta(days=95),
        price=600.00,
        max_capacity=12,
        available_seats=12,
        status=TripStatus.DRAFT,
        refundable_until_days_before=7,
        cancellation_fee_percent=10,
    ),
]

db.add_all(trips)
db.commit()

bookings = [
    Booking(
        id="bk-001", trip_id="trip-001", user_id="user-A",
        num_seats=3, state=BookingState.CONFIRMED,
        price_at_booking=1500.00,
        expires_at=now + timedelta(minutes=15),
        idempotency_key="wh-001",
    ),
    Booking(
        id="bk-002", trip_id="trip-001", user_id="user-B",
        num_seats=4, state=BookingState.CONFIRMED,
        price_at_booking=2000.00,
        expires_at=now + timedelta(minutes=15),
        idempotency_key="wh-002",
    ),
    Booking(
        id="bk-003", trip_id="trip-001", user_id="user-C",
        num_seats=5, state=BookingState.CONFIRMED,
        price_at_booking=2500.00,
        expires_at=now + timedelta(minutes=15),
        idempotency_key="wh-003",
    ),
    Booking(
        id="bk-004", trip_id="trip-001", user_id="user-D",
        num_seats=2, state=BookingState.PENDING_PAYMENT,
        price_at_booking=1000.00,
        expires_at=now + timedelta(minutes=10),
    ),
    Booking(
        id="bk-005", trip_id="trip-001", user_id="user-E",
        num_seats=2, state=BookingState.CANCELLED,
        price_at_booking=1000.00,
        expires_at=now - timedelta(hours=2),
        cancelled_at=now - timedelta(hours=1),
        refund_amount=900.00,
        idempotency_key="wh-005",
    ),
    Booking(
        id="bk-006", trip_id="trip-001", user_id="user-F",
        num_seats=1, state=BookingState.EXPIRED,
        price_at_booking=500.00,
        expires_at=now - timedelta(hours=3),
    ),
    Booking(
        id="bk-007", trip_id="trip-002", user_id="user-A",
        num_seats=2, state=BookingState.CONFIRMED,
        price_at_booking=1600.00,
        expires_at=now + timedelta(minutes=15),
        idempotency_key="wh-007",
    ),
    Booking(
        id="bk-008", trip_id="trip-002", user_id="user-B",
        num_seats=1, state=BookingState.CONFIRMED,
        price_at_booking=800.00,
        expires_at=now + timedelta(minutes=15),
        idempotency_key="wh-008",
    ),
    Booking(
        id="bk-009", trip_id="trip-002", user_id="user-C",
        num_seats=1, state=BookingState.CANCELLED,
        price_at_booking=800.00,
        expires_at=now - timedelta(hours=1),
        cancelled_at=now - timedelta(hours=1),
        refund_amount=0.00,
        idempotency_key="wh-009",
    ),
    Booking(
        id="bk-010", trip_id="trip-003", user_id="user-G",
        num_seats=2, state=BookingState.PENDING_PAYMENT,
        price_at_booking=2400.00,
        expires_at=now - timedelta(minutes=5),
    ),
]

db.add_all(bookings)
db.commit()
db.close()

print("Seed complete:")
print("  4 trips (3 published, 1 draft)")
print("  10 bookings (3 confirmed Paris, 1 pending Paris, 1 cancelled+refund Paris,")
print("               1 expired Paris, 2 confirmed Bali, 1 cancelled-no-refund Bali,")
print("               1 expired-pending Tokyo)")
print("")
print("Interesting things to observe:")
print("  GET /admin/trips/at-risk         → Bali (5 days away, 30% occupancy)")
print("  GET /admin/trips/trip-001/metrics → Paris financials")
print("  bk-010 will be auto-expired by the expiry job within 60s of app start")
