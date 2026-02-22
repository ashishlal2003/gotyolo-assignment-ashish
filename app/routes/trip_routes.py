from fastapi import APIRouter, Depends, Query
from typing import Optional
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.trip_schema import TripCreate, TripResponse
from app.services import trip_service

router = APIRouter(prefix="/trips", tags=["trips"])


@router.get("", response_model=list[TripResponse])
def list_trips(destination: Optional[str] = Query(None), db: Session = Depends(get_db)):
    return trip_service.list_trips(db, destination)


@router.get("/{trip_id}", response_model=TripResponse)
def get_trip(trip_id: str, db: Session = Depends(get_db)):
    return trip_service.get_trip(db, trip_id)


@router.post("", response_model=TripResponse, status_code=201)
def create_trip(data: TripCreate, db: Session = Depends(get_db)):
    return trip_service.create_trip(db, data)
