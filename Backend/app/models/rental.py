from sqlalchemy import String, DateTime, Enum, ForeignKey, DECIMAL
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from core.database import Base
from models.user import User
from models.car import Car


class Rental(Base):
    __tablename__ = "rentals"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    car_id: Mapped[int] = mapped_column(ForeignKey("cars.id", ondelete="CASCADE"), nullable=False)
    start_date = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    end_date = mapped_column(DateTime(timezone=True), nullable=False)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    returned_at = mapped_column(DateTime(timezone=True), onupdate=func.now())
    price_for_day: Mapped[DECIMAL] = mapped_column(DECIMAL(10, 2), nullable=False)
    price_sum: Mapped[DECIMAL] = mapped_column(DECIMAL(10, 2), nullable=False)
    status: Mapped[str] = mapped_column(Enum("NOT_STARTED", "ACTIVE", "FINISHED", native_enum=False), default="NOT_STARTED")

    user: Mapped["User"] = relationship(back_populates="rentals")
    car: Mapped["Car"] = relationship(back_populates="rentals")

    payment: Mapped["Payment"] = relationship(back_populates="rental" , cascade="all, delete-orphan", uselist=False)

    def __repr__(self):
        return f"Rentals(id={self.id!r}, user_id={self.user_id!r}), car_id={self.car_id!r})"
    

class Payment(Base): 
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True)
    rental_id: Mapped[int] = mapped_column(ForeignKey("rentals.id", ondelete="CASCADE"), nullable=False, unique=True)
    amount: Mapped[DECIMAL] = mapped_column(DECIMAL(10, 2), nullable=False)
    payment_method: Mapped[str] = mapped_column(String(30), nullable=False)
    status: Mapped[str] = mapped_column(Enum("PAYED", "NOT_PAID", native_enum=False), nullable=False)
    paid_at = mapped_column(DateTime(timezone=True), server_default=func.now())

    rental: Mapped["Rental"] = relationship(back_populates="payment")

    def __repr__(self):
        return f"Payments(id={self.rental_id!r}, amount={self.amount!r})"