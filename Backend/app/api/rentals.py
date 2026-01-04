from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.auth import get_current_user
from app.models.user import User
from app.core.database import get_db
from app.models.rental import Rental, Payment
from app.models.car import Car
from app.schemas.rental import RentalCreateSchema, RentalResponseSchema
from datetime import datetime, timezone
from decimal import Decimal
from math import ceil

router = APIRouter(prefix="/rentals", tags=["rentals"])

@router.post("/", response_model=RentalResponseSchema, status_code=201)
def create_rental(rental: RentalCreateSchema, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    rental_db = Rental(
        car_id=rental.car_id,
        user_id=current_user.id,
        start_date=rental.start_date,
        end_date=rental.end_date,
    )

    if rental_db.start_date >= rental_db.end_date:
        raise HTTPException(status_code=400, detail="End date must be after start date")
    
    if rental_db.car_id is None:
        raise HTTPException(status_code=400, detail="Car ID must be provided")
    
    car = db.query(Car).filter(Car.id == rental_db.car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    
    if car.status != "AVAILABLE":
        raise HTTPException(status_code=400, detail="Car is not available for rental")

    overlap = db.query(Rental).filter(
        Rental.car_id == rental.car_id,
        Rental.status != "CANCELLED",
        Rental.end_date > rental.start_date,
        Rental.start_date < rental.end_date
    ).first()
    if overlap:
        raise HTTPException(400, "Car already booked for this period")

    price_for_day = car.price_per_day
    days = max(1, ceil((rental_db.end_date - rental_db.start_date).total_seconds() / 86400))
    rental_db.price_for_day = price_for_day
    rental_db.price_sum = Decimal(price_for_day) * Decimal(days)

    rental_db.status = "NOT_STARTED"

    db.add(rental_db)
    db.commit()
    db.refresh(rental_db)

    return rental_db


@router.post("/{rental_id}/start", response_model=RentalResponseSchema)
def start_rental(rental_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    now = datetime.now(timezone.utc)
    r = db.query(Rental).filter(Rental.id == rental_id).first()
    if r is None:
        raise HTTPException(status_code=404, detail="Rental not found")
    if current_user.id != r.user_id and current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not allowed")
    if r.status != "NOT_STARTED":
        raise HTTPException(status_code=400, detail="Cannot start rental in current status")
    if now < r.start_date:
        raise HTTPException(status_code=400, detail="Rental can't be started yet")

    r.status = "ACTIVE"
    car = db.query(Car).filter(Car.id == r.car_id).first()
    if car:
        car.status = "UNAVAILABLE"
    r.started_at = now
    db.commit()
    db.refresh(r)
    return r


@router.post("/{rental_id}/finish", response_model=RentalResponseSchema)
def finish_rental(rental_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    now = datetime.now(timezone.utc)
    r = db.query(Rental).filter(Rental.id == rental_id).first()
    if r is None:
        raise HTTPException(status_code=404, detail="Rental not found")
    if current_user.id != r.user_id and current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not allowed")
    if r.status != "ACTIVE":
        raise HTTPException(status_code=400, detail="Cannot finish rental in current status")
    if now < r.end_date:
        raise HTTPException(status_code=400, detail="Rental can't be finished yet")

    if r.started_at:
        used_seconds = (now - r.started_at).total_seconds()
    else:
        used_seconds = (now - r.start_date).total_seconds()
    days = max(1, ceil(used_seconds / 86400))
    r.price_sum = Decimal(r.price_for_day) * Decimal(days)

    r.status = "FINISHED"
    car = db.query(Car).filter(Car.id == r.car_id).first()
    if car:
        car.status = "AVAILABLE"
    r.returned_at = now

    payment_db = None

    existing_payment = db.query(Payment).filter(Payment.rental_id == r.id).first()
    if existing_payment is None:
        payment_db = Payment(
            rental_id=r.id,
            amount=r.price_sum,
            payment_method="NOT_SPECIFIED",
            status="NOT_PAID",
        )
        db.add(payment_db)

    db.commit()
    db.refresh(r)
    if payment_db:
        db.refresh(payment_db)

    return r


@router.post("/{rental_id}/cancel", response_model=RentalResponseSchema)
def cancel_rental(rental_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    r = db.query(Rental).filter(Rental.id == rental_id).first()
    if r is None:
        raise HTTPException(status_code=404, detail="Rental not found")
    if current_user.id != r.user_id and current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not allowed")
    if r.status in ["FINISHED", "CANCELLED"]:
        raise HTTPException(status_code=400, detail="Cannot cancel a finished or already cancelled rental")
    if r.status == "ACTIVE":
        raise HTTPException(status_code=400, detail="Cannot cancel an active rental")

    r.status = "CANCELLED"
    car = db.query(Car).filter(Car.id == r.car_id).first()
    if car:
        car.status = "AVAILABLE"

    db.commit()
    db.refresh(r)
    return r


@router.get("/{rental_id}", response_model=RentalResponseSchema)
def get_rental(rental_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    rental_db = db.query(Rental).filter(Rental.id == rental_id).first()
    if not rental_db:
        raise HTTPException(status_code=404, detail="Rental not found")
    if current_user.id != rental_db.user_id and current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not allowed")

    return rental_db


@router.get("/me", response_model=List[RentalResponseSchema])
def get_my_rentals(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    rentals_db = db.query(Rental).filter(Rental.user_id == current_user.id).all()
    return rentals_db


@router.get("/", response_model=List[RentalResponseSchema])
def get_all_rentals(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "ADMIN":
        raise HTTPException(403, "Not allowed")
    rentals_db = db.query(Rental).all()
    return rentals_db