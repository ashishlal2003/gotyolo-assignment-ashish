from app.database import SessionLocal
from app.daos import booking_dao, trip_dao


def expire_pending_bookings():
    db = SessionLocal()
    try:
        expired = booking_dao.get_expired_pending_bookings(db)
        for booking in expired:
            trip_dao.increment_seats(db, booking.trip_id, booking.num_seats)
            booking.state = "EXPIRED"
        if expired:
            db.commit()
            print(f"[expiry_job] Expired {len(expired)} booking(s)")
    except Exception as e:
        db.rollback()
        print(f"[expiry_job] Error: {e}")
    finally:
        db.close()
