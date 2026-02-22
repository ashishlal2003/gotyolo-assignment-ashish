from fastapi import FastAPI
from app.database import Base, engine
from app.models import Trip, Booking 

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def health():
    return {"message": "GotYolo API"}
