# GoTyolo API

A travel booking management API built with FastAPI that handles trip management, bookings, payment processing, and administrative analytics.

## Features

### Trip Management
- Create and manage trips with details (destination, dates, price, capacity)
- List published trips with optional destination filtering
- Get detailed trip information
- Trip statuses: DRAFT (not bookable) and PUBLISHED (available for booking)
- Dynamic seat availability tracking

### Booking Management
- Create bookings for trips with specified number of seats
- Booking state workflow: PENDING_PAYMENT → CONFIRMED/EXPIRED or CANCELLED
- Automatic expiry of pending bookings after 15 minutes if payment not confirmed
- Payment webhook integration for external payment systems
- Booking cancellation with configurable refund policies
- Refund calculation based on cancellation timing and fees

### Background Processing
- Automated expiry job that runs every 60 seconds to expire pending bookings past their expiration time
- Built with APScheduler for reliable background task execution

### Admin Features
- At-risk trips analysis: Identify published trips starting within 7 days with less than 50% occupancy
- Comprehensive trip metrics including occupancy, seat distribution, booking states, and financial data (gross revenue, refunds, net revenue)

## Technology Stack

- **FastAPI 0.129.2** - Modern async web framework
- **Uvicorn** - ASGI server
- **SQLAlchemy** - ORM for database operations
- **SQLite** - Default database
- **APScheduler 3.11.2** - Background job scheduling
- **Python 3.11**
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration

## Project Structure

```
gotyolo-assignment-ashish/
├── app/
│   ├── main.py                  # Application entry point
│   ├── config.py                # Configuration settings
│   ├── database.py              # Database connection management
│   ├── models/
│   │   ├── trip.py             # Trip ORM model
│   │   └── booking.py          # Booking ORM model
│   ├── routes/
│   │   ├── trip_routes.py      # Trip endpoints
│   │   ├── booking_routes.py   # Booking endpoints
│   │   └── admin_route.py      # Admin endpoints
│   ├── services/
│   │   ├── trip_service.py     # Trip business logic
│   │   ├── booking_service.py  # Booking business logic
│   │   └── admin_service.py    # Analytics logic
│   ├── daos/
│   │   ├── trip_dao.py         # Trip data access
│   │   └── booking_dao.py      # Booking data access
│   ├── schemas/
│   │   ├── trip_schema.py      # Trip Pydantic models
│   │   └── booking_schema.py   # Booking Pydantic models
│   └── jobs/
│       └── expiry_job.py       # Background expiry job
├── seed/
│   └── seed.py                  # Sample data initialization
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── gotyolo.db                   # SQLite database file
```

## Installation

### Using Docker (Recommended)

1. Clone the repository
```bash
git clone <repository-url>
cd gotyolo-assignment-ashish
```

2. Run with Docker Compose
```bash
docker-compose up
```

The API will be available at `http://localhost:8000`

### Local Setup

1. Install Python 3.11 or higher

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. (Optional) Seed sample data
```bash
python seed/seed.py
```

4. Run the application
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Configuration

Create a `.env` file in the root directory to override default settings:

```env
DATABASE_URL=sqlite:///./gotyolo.db
```

The database is automatically initialized on application startup.

## API Endpoints

### Trip Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/trips` | List all published trips (optional: `?destination=<city>`) |
| GET | `/trips/{trip_id}` | Get trip details |
| POST | `/trips` | Create new trip (status: DRAFT) |

### Booking Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/trips/{trip_id}/book` | Create booking (auto-assigned PENDING_PAYMENT, 15min expiry) |
| GET | `/bookings/{booking_id}` | Get booking details |
| POST | `/bookings/{booking_id}/cancel` | Cancel booking with refund logic |
| POST | `/payments/webhook` | Payment status webhook (CONFIRMED/EXPIRED handling) |

### Admin Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/admin/trips/at-risk` | Get trips at risk (imminent + low occupancy) |
| GET | `/admin/trips/{trip_id}/metrics` | Get detailed trip metrics and financials |

## Database Models

### Trip Table

- `id` (UUID): Primary key
- `title`: Trip title
- `destination`: Trip destination
- `start_date`: Trip start date
- `end_date`: Trip end date
- `price`: Price per seat
- `max_capacity`: Maximum number of seats
- `available_seats`: Currently available seats
- `status`: DRAFT or PUBLISHED
- `refundable_until_days_before`: Days before trip for full refund eligibility
- `cancellation_fee_percent`: Percentage fee if cancelled outside refund window
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

### Booking Table

- `id` (UUID): Primary key
- `trip_id` (FK): Reference to trip
- `user_id`: User identifier
- `num_seats`: Number of seats booked
- `state`: PENDING_PAYMENT, CONFIRMED, CANCELLED, or EXPIRED
- `price_at_booking`: Total price at booking time
- `payment_reference`: Payment system reference
- `idempotency_key`: Unique key for idempotent webhook processing
- `expires_at`: Expiration timestamp for pending bookings
- `cancelled_at`: Cancellation timestamp
- `refund_amount`: Refund issued (if cancelled)


### Key Features

- Dependency injection via `Depends(get_db)` for database sessions
- Separation of concerns with clear layer boundaries
- Background scheduling via APScheduler with lifespan context manager
- Pydantic schemas for request/response validation
- HTTP error handling with appropriate status codes

### Booking Workflow

1. User creates booking → PENDING_PAYMENT (15min timeout)
2. Payment webhook arrives → CONFIRMED (if success) or EXPIRED
3. Auto-expiry job → EXPIRED (if 15min passed without payment)
4. User can cancel → CANCELLED (with refund calculation)

## Booking Refund Policy

Refunds are calculated based on two trip-level configurations:

- `refundable_until_days_before`: Number of days before trip start when full refund is available
- `cancellation_fee_percent`: Percentage fee applied to refunds

**Refund Logic:**
- If cancelled before the refund window: Full refund minus cancellation fee
- If cancelled within the refund window: No refund

## Development Notes

- **Idempotency**: Webhook handler checks `idempotency_key` to prevent duplicate processing
- **Seat Management**: Available seats are decremented on booking creation and incremented on expiry/cancellation
- **Timezone Handling**: All timestamps use UTC timezone
- **Status Workflow**: Strict state machine for booking states ensures data integrity

## API Documentation

Once the application is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
