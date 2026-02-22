from contextlib import asynccontextmanager
from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from app.database import Base, engine
from app.models import Trip, Booking
from app.routes import trip_routes, booking_routes, admin_route

Base.metadata.create_all(bind=engine)

scheduler = BackgroundScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.add_job(
        func="app.jobs.expiry_job:expire_pending_bookings",
        trigger="interval",
        seconds=60,
        id="expiry_job",
    )
    scheduler.start()
    print("[scheduler] Expiry job started — runs every 60s")
    yield
    scheduler.shutdown()
    print("[scheduler] Expiry job stopped")


app = FastAPI(title="GoTyolo API", lifespan=lifespan)

app.include_router(trip_routes.router)
app.include_router(booking_routes.router)
app.include_router(admin_route.router)


@app.get("/")
def health():
    return {"message": "GotYolo API"}
