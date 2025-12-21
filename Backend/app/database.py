from sqlalchemy import DateTime, create_engine
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import Enum
from sqlalchemy import DECIMAL
from sqlalchemy import Text
from sqlalchemy.orm import Session
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

engine = create_engine(, echo=True)

class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(30), nullable=False)
    last_name: Mapped[str] = mapped_column(String(30), nullable=False)
    email: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    phone_number: Mapped[str] = mapped_column(String(15), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[str] = mapped_column(Enum("ADMIN", "AGENT", "USER", native_enum=False), default="USER")
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = mapped_column(DateTime(timezone=True), onupdate=func.now())

    rentals: Mapped[list["Rental"]] = relationship(back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, first_name={self.first_name!r}, last_name={self.last_name!r}, email={self.email!r}, role={self.role!r})"


class Car(Base):
    __tablename__ = "cars"

    id: Mapped[int] = mapped_column(primary_key=True)
    brand: Mapped[str] = mapped_column(String(30), nullable=False)
    model: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(Enum("AVAILABLE", "UNAVAILABLE", native_enum=False), default="AVAILABLE")
    condition: Mapped[str] = mapped_column(String(30))
    type_id: Mapped[int] = mapped_column(ForeignKey("car_types.id", ondelete="RESTRICT"))
    plate: Mapped[str] = mapped_column(String(10), nullable=False)
    seats: Mapped[int] = mapped_column()
    doors: Mapped[int] = mapped_column()
    color: Mapped[str] = mapped_column(String(30))
    fuel_id: Mapped[int] = mapped_column(ForeignKey("fuel_types.id", ondelete="RESTRICT"))
    fuel_per_km: Mapped[float] = mapped_column()
    gearbox_id: Mapped[int] = mapped_column(ForeignKey("gearbox_types.id", ondelete="RESTRICT"))
    mileage: Mapped[int] = mapped_column()
    price_per_day: Mapped[DECIMAL] = mapped_column(DECIMAL(10, 2), nullable=False)
    year: Mapped[int] = mapped_column()

    service_history: Mapped[list["CarServiceHistory"]] = relationship(back_populates="car", cascade="all, delete-orphan")
    rentals: Mapped[list["Rental"]] = relationship(back_populates="car", cascade="all, delete-orphan")

    car_type: Mapped["CarType"] = relationship(back_populates="cars")
    fuel_type: Mapped["FuelType"] = relationship(back_populates="cars")
    gearbox_type: Mapped["GearboxType"] = relationship(back_populates="cars")

    tags: Mapped[list["Tag"]] = relationship(secondary="car_tags", back_populates="cars")

    images: Mapped[list["CarImage"]] = relationship(back_populates="car", cascade="all, delete-orphan")

    def __repr__(self):
        return f"Car(id={self.id!r}, brand={self.brand!r}, model={self.model!r}, plate={self.plate!r}"


class CarImage(Base):
    __tablename__ = "cars_image"

    id: Mapped[int] = mapped_column(primary_key=True)
    car_id: Mapped[int] = mapped_column(ForeignKey("cars.id", ondelete="CASCADE"), nullable=False)
    image_url: Mapped[str] = mapped_column(String(255))
    is_primary: Mapped[bool] = mapped_column(default=False, nullable=False)

    car: Mapped["Car"] = relationship(back_populates="images")


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)

    cars: Mapped[list["Car"]] = relationship(secondary="car_tags", back_populates="tags")
    

class CarTags(Base):
    __tablename__ = "car_tags"

    car_id: Mapped[int] = mapped_column(ForeignKey("cars.id", ondelete="CASCADE"), primary_key=True)
    tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)
    

class CarType(Base):
    __tablename__ = "car_types"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))

    cars: Mapped[list["Car"]] = relationship(back_populates="car_type")

    def __repr__(self):
        return f"CarType(id={self.id!r}, name={self.name!r})"


class FuelType(Base):
    __tablename__ = "fuel_types"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))

    cars: Mapped[list["Car"]] = relationship(back_populates="fuel_type")
    
    def __repr__(self):
        return f"FuelType(id={self.id!r}, name={self.name!r})"
    

class GearboxType(Base):
    __tablename__ = "gearbox_types"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))

    cars: Mapped[list["Car"]] = relationship(back_populates="gearbox_type")

    def __repr__(self):
        return f"GearboxType(id={self.id!r}, name={self.name!r})"
    

class CarServiceHistory(Base): 
    __tablename__ = "car_service_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    car_id: Mapped[int] = mapped_column(ForeignKey("cars.id", ondelete="CASCADE"), nullable=False)
    description: Mapped[str] = mapped_column(Text)
    service_date = mapped_column(DateTime(timezone=True), server_default=func.now())
    mileage: Mapped[int] = mapped_column()

    car: Mapped["Car"] = relationship(back_populates="service_history")

    def __repr__(self):
        return f"Service History (id={self.car_id!r}, description={self.description!r})"
    

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


Base.metadata.create_all(engine)


with Session(engine) as session:
    TestUser = User(
        first_name = "Tester",
        last_name = "Testororvich",
        email = "testemail@gmail.com",
        phone_number = "0983838123213",
        password = "1234567890"
    )

    session.add_all([TestUser])

    session.commit()