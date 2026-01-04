from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.car import Car, CarImage, Tag
from app.schemas.car import CarCreateSchema, CarResponseSchema, CarImageCreateSchema, TagSchema
from app.api.auth import get_current_user
from app.api.auth import User

router = APIRouter(prefix="/cars", tags=["cars"])


@router.get("/{car_id}", response_model=CarResponseSchema)
def get_car(car_id: int, db: Session = Depends(get_db)):
    car_db = db.query(Car).filter(Car.id == car_id).first()

    if not car_db:
        raise HTTPException(status_code=404, detail="Car not found")

    return car_db


@router.post("/", response_model=CarResponseSchema)
def create_car(car: CarCreateSchema, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role not in {"ADMIN", "AGENT"}:
        raise HTTPException(status_code=403, detail="Not authorized")

    existing = db.query(Car).filter(Car.plate == car.plate).first()
    if existing:
        raise HTTPException(status_code=400, detail="Car with this plate already exists")

    car_db = Car(
        brand = car.brand,
        model = car.model,
        type_id = car.type_id,
        fuel_id = car.fuel_id,
        gearbox_id = car.gearbox_id,
        plate = car.plate,
        seats = car.seats,
        doors = car.doors,
        color = car.color,
        fuel_per_km = car.fuel_per_km,
        mileage = car.mileage,
        price_per_day = car.price_per_day,
        year = car.year,
    )

    db.add(car_db)
    db.flush()

    if car.images:
        for img in car.images:
            img_obj = CarImage(car_id=car_db.id, image_url=img.image_url, is_primary=bool(img.is_primary))
            db.add(img_obj)

    if car.tags:
        for t in car.tags:
            tag_obj = db.query(Tag).filter(Tag.name == t.name).first()
            if not tag_obj:
                tag_obj = Tag(name=t.name)
                db.add(tag_obj)
                db.flush()
            car_db.tags.append(tag_obj)

    db.commit()
    db.refresh(car_db)

    return car_db
