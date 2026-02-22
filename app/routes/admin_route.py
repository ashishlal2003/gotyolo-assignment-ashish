from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services import admin_service

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/trips/at-risk")
def at_risk_trips(db: Session = Depends(get_db)):
    return admin_service.get_at_risk_trips(db)


@router.get("/trips/{trip_id}/metrics")
def trip_metrics(trip_id: str, db: Session = Depends(get_db)):
    return admin_service.get_trip_metrics(db, trip_id)
