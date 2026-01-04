from sqlalchemy import String, DateTime, Enum, DECIMAL, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.core.database import Base
#from app.models.rental import Rental


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