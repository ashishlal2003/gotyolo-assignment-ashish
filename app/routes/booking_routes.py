from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.booking_schema import BookingCreate, BookingResponse, WebhookPayload, CancelResponse
from app.services import booking_service

router = APIRouter(tags=["bookings"])


@router.post("/trips/{trip_id}/book", response_model=BookingResponse, status_code=201)
def create_booking(trip_id: str, data: BookingCreate, db: Session = Depends(get_db)):
    return booking_service.create_booking(db, trip_id, data)


@router.get("/bookings/{booking_id}", response_model=BookingResponse)
def get_booking(booking_id: str, db: Session = Depends(get_db)):
    from app.daos import booking_dao
    from fastapi import HTTPException
    booking = booking_dao.get_booking(db, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking


@router.post("/bookings/{booking_id}/cancel", response_model=CancelResponse)
def cancel_booking(booking_id: str, db: Session = Depends(get_db)):
    booking = booking_service.cancel_booking(db, booking_id)
    return CancelResponse(
        booking_id=booking.id,
        state=booking.state,
        refund_amount=float(booking.refund_amount or 0),
    )


@router.post("/payments/webhook")
def payment_webhook(payload: WebhookPayload, db: Session = Depends(get_db)):
    result = booking_service.handle_webhook(db, payload)
    return result   # always 200
