from datetime import datetime
from enum import Enum
import re
from pydantic import BaseModel, field_validator


class CarStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    UNAVAILABLE = "UNAVAILABLE"


class CarImageSchema(BaseModel):
    car_id: int
    image_url: str
    is_primary: bool


class CarImageResponseSchema(BaseModel):
    id: int
    car_id: int
    image_url: str
    is_primary: bool

    model_config = {"from_attributes": True}


class TagSchema(BaseModel):
    name: str


class TagResponseSchema(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class CarTypeResponseSchema(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class FuelTypeResponseSchema(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class GearboxTypeResponseSchema(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class CarCreateSchema(BaseModel):
    brand: str
    model: str
    type_id: int
    fuel_id: int
    gearbox_id: int
    price_per_day: float
    fuel_per_km: float
    seats: int
    doors: int
    color: str
    year: int
    mileage: int
    plate: str

    @field_validator('plate')
    def validate_plate(cls, v: str) -> str:
        v = v.strip().upper()
        if not re.fullmatch(r'^[A-Z0-9-]{1,10}$', v):
            raise ValueError('plate must be 1-10 characters; letters, numbers and hyphen allowed')
        return v

    @field_validator('year')
    def validate_year(cls, v: int) -> int:
        current_year = datetime.now().year
        if v < 1886 or v > current_year:
            raise ValueError(f'year must be between 1886 and {current_year}')
        return v

    @field_validator('price_per_day', 'fuel_per_km')
    def validate_non_negative(cls, v: float) -> float:
        if v < 0:
            raise ValueError('must be non-negative')
        return v

    @field_validator('seats', 'doors')
    def validate_positive_ints(cls, v: int) -> int:
        if v < 1:
            raise ValueError('must be >= 1')
        return v

    @field_validator('mileage')
    def validate_mileage(cls, v: int) -> int:
        if v < 0:
            raise ValueError('mileage must be non-negative')
        return v


class CarUpdateSchema(BaseModel):
    brand: str | None
    model: str | None
    type_id: int | None
    fuel_id: int | None
    gearbox_id: int | None
    price_per_day: float | None
    fuel_per_km: float | None
    seats: int | None
    doors: int | None
    color: str | None
    year: int | None
    mileage: int | None
    plate: str | None

    @field_validator('plate')
    def validate_plate(cls, v):
        if v is None:
            return v
        v = v.strip().upper()
        if not re.fullmatch(r'^[A-Z0-9-]{1,10}$', v):
            raise ValueError('plate must be 1-10 characters; letters, numbers and hyphen allowed')
        return v

    @field_validator('year')
    def validate_year(cls, v):
        if v is None:
            return v
        current_year = datetime.now().year
        if v < 1886 or v > current_year:
            raise ValueError(f'year must be between 1886 and {current_year}')
        return v

    @field_validator('price_per_day', 'fuel_per_km')
    def validate_non_negative(cls, v):
        if v is None:
            return v
        if v < 0:
            raise ValueError('must be non-negative')
        return v

    @field_validator('seats', 'doors')
    def validate_positive_ints(cls, v):
        if v is None:
            return v
        if v < 1:
            raise ValueError('must be >= 1')
        return v

    @field_validator('mileage')
    def validate_mileage(cls, v):
        if v is None:
            return v
        if v < 0:
            raise ValueError('mileage must be non-negative')
        return v


class CarResponseSchema(BaseModel):
    id: int
    brand: str
    model: str
    status: CarStatus
    condition: str | None
    car_type: CarTypeResponseSchema | None
    fuel_type: FuelTypeResponseSchema | None
    gearbox_type: GearboxTypeResponseSchema | None
    plate: str
    seats: int
    doors: int
    color: str | None
    fuel_per_km: float
    mileage: int
    price_per_day: float
    year: int
    images: list[CarImageResponseSchema] | None
    tags: list[TagResponseSchema] | None

    model_config = {"from_attributes": True}


class CarFilterSchema(BaseModel):
    type: str | None
    fuel: str | None
    gearbox: str | None
    price_from: float | None
    price_to: float | None
    tags: list[str] | None
    seats: int | None
    doors: int | None

