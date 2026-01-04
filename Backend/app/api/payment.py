from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.auth import get_current_user
from app.models.user import User
from app.core.database import get_db
from app.models.rental import Rental, Payment
from app.schemas.rental import PaymentCreateSchema, PaymentResponseSchema
from datetime import datetime, timezone
from decimal import Decimal

router = APIRouter(prefix = "/payments", tags = ["payments"])


@router.post("/{payment_id}/pay", response_model=PaymentResponseSchema)
def pay_rental(payment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    p = db.query(Payment).filter(Payment.id == payment_id).first()
    if p is None:
        raise HTTPException(status_code=404, detail="Payment not found")
    r = db.query(Rental).filter(Rental.id == p.rental_id).first()
    if r is None:
        raise HTTPException(status_code=404, detail="Rental not found")

    if r.user_id != current_user.id and current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not authorized to pay for this rental")

    if r.status != "FINISHED":
        raise HTTPException(status_code=400, detail="Rental is not finished yet")
    if p.status == "PAID":
        raise HTTPException(status_code=400, detail="Payment is already paid")

    p.status = "PAID"
    p.paid_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(p)
    return p


@router.get("/{payment_id}", response_model=PaymentResponseSchema)
def get_payment(payment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    p = db.query(Payment).filter(Payment.id == payment_id).first()
    if p is None:
        raise HTTPException(status_code=404, detail="Payment not found")
    r = db.query(Rental).filter(Rental.id == p.rental_id).first()
    if r is None:
        raise HTTPException(status_code=404, detail="Rental not found")
    if r.user_id != current_user.id and current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not authorized to view this payment")
    return p


@router.get("/me", response_model=List[PaymentResponseSchema])
def get_my_payments(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    payments = db.query(Payment).join(Rental).filter(Rental.user_id == current_user.id).all()
    return payments
