# ALX Travel App
A Django-based platform that lets users browse listings, make bookings, and complete secure payments through the Chapa API.

## Features
### Core Functionality
- **Property Listings:** Hosts can create and manage property listings with detailed information.
- **Booking System:** Secure booking system with date availability checking.
- **User Reviews:** Rating and review system for completed bookings.

## Architecture
### Tech Stack
- **Backend:** Django 4.x, Django REST Framework  
- **Database:** PostgreSQL (recommended) / SQLite  
- **Authentication:** Django Authentication System  
- **API:** RESTful API with DRF ViewSets  

## Models Overview
- **User:** Extended Django User model with travel-specific features.  
- **Listing:** Property listings with amenities, pricing, and availability.  
- **Booking:** Reservation system with status tracking.  
- **Review:** Rating and review system.  
- **Payment:** Stores booking reference, transaction ID, and status for Chapa payments.

## Quick Start
### Prerequisites
- Python 3.8+
- Django 4.x
- Django REST Framework

### Installation
**Clone the repository**
```bash
git clone <repository-url>
cd alx_travel_app_0x02
```

**Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

**Install dependencies**
```bash
pip install -r requirements.txt
```

**Edit .env with your database and secret key**

Run migrations
```bash
python manage.py migrate
```
Create superuser
```bash
python manage.py createsuperuser
```
Run development server
```bash
python manage.py runserver
```

## API Documentation (**Key Endpoints**)

**Listings**
- GET /api/listings/ - Browse all listings
- POST /api/listings/ - Create new listing (hosts only)
- GET /api/listings/{id}/ - Get listing details
- PUT /api/listings/{id}/ - Update listing (host only)
- DELETE /api/listings/{id}/ - Delete listing (host only)
**Bookings**
- GET /api/bookings/ - User's bookings (as guest or host)
- POST /api/bookings/ - Create new booking
- GET /api/bookings/{id}/ - Booking details
- PUT /api/bookings/{id}/ - Update booking status
- DELETE /api/bookings/{id}/ - Cancel booking

**Payments (Chapa Integration)**
- POST /api/initiate-payment/ – Initialize a Chapa payment
- GET /api/verify-payment/<tx_ref>/ – Verify payment status

## Example API Usage
**Create a Listing**
{
  "name": "Seaside Villa",
  "description": "A cozy beach house with ocean view.",
  "price_per_night": 120.00,
  "location": "Lagos"
}

**Make a Booking**
{
  "user": 1,
  "listing": 2,
  "start_date": "2025-10-20",
  "end_date": "2025-10-22"
}

**Initiate Payment**
{
  "booking_reference": "1",
  "amount": "240.00"
}

