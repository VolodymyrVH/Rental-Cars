from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.car import Car, CarImage, Tag, CarType, FuelType, GearboxType
from app.schemas.car import CarCreateSchema, CarResponseSchema, CarUpdateSchema, CarFilterSchema, PaginatedCarResponse
from app.api.auth import get_current_user
from app.api.auth import User

router = APIRouter(prefix="/cars", tags=["cars"])


@router.get("/{car_id}", response_model=CarResponseSchema)
def get_car(car_id: int, db: Session = Depends(get_db)):
    car_db = db.query(Car).filter(Car.id == car_id).first()

    if not car_db:
        raise HTTPException(status_code=404, detail="Car not found")

    return car_db


@router.get("/", response_model=PaginatedCarResponse)
def list_cars(filters: CarFilterSchema = Depends(), db: Session = Depends(get_db), 
              page: int = Query(1, ge=1), limit: int = Query(10, ge=1, le=100),
              sort: str = Query("price_per_day")):
    allowed_sort_fields = {"price_per_day": Car.price_per_day, 
                           "year": Car.year, 
                           "mileage": Car.mileage, 
                           "brand": Car.brand, 
                           "fuel_per_km": Car.fuel_per_km, 
                           "seats": Car.seats, 
                           "doors": Car.doors}
    
    order_by = []

    for raw_field in sort.split(","):
        field = raw_field.strip()
        if not field:
            continue
        desc = field.startswith("-")
        field_name = field[1:] if desc else field

        if field_name not in allowed_sort_fields:
            raise HTTPException(status_code=400, detail=f"Invalid sort field: {field_name}")

        column = allowed_sort_fields[field_name]
        order_by.append(column.desc() if desc else column.asc())

    query = db.query(Car).filter(Car.status == "AVAILABLE")

    if filters.type:
        query = query.join(Car.car_type).filter(CarType.name == filters.type)
    if filters.fuel:
        query = query.join(Car.fuel_type).filter(FuelType.name == filters.fuel)
    if filters.gearbox:
        query = query.join(Car.gearbox_type).filter(GearboxType.name == filters.gearbox)
    if filters.price_from is not None:
        query = query.filter(Car.price_per_day >= filters.price_from)
    if filters.price_to is not None:
        query = query.filter(Car.price_per_day <= filters.price_to)
    if filters.seats is not None:
        query = query.filter(Car.seats == filters.seats)
    if filters.tags:
        for tag_name in filters.tags:
            query = query.filter(Car.tags.any(Tag.name == tag_name))

    if order_by:
        query = query.order_by(*order_by)

    total = query.distinct(Car.id).count()
    cars = query.distinct(Car.id).offset((page - 1) * limit).limit(limit).all()

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "items": cars
    }


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


@router.patch("/{car_id}", response_model=CarResponseSchema)
def update_car(car_id: int, car: CarUpdateSchema, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role not in {"ADMIN", "AGENT"}:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    car_db = db.query(Car).filter(Car.id == car_id).first()

    if not car_db:
        raise HTTPException(status_code=404, detail="Car not found")
    
    if car.plate and car.plate != car_db.plate:
        existing = db.query(Car).filter(Car.plate == car.plate).first()
        if existing:
            raise HTTPException(status_code=400, detail="Car with this plate already exists")

    updatable_fields = [
        "brand",
        "model",
        "type_id",
        "fuel_id",
        "gearbox_id",
        "price_per_day",
        "fuel_per_km",
        "seats",
        "doors",
        "color",
        "year",
        "mileage",
        "plate",
    ]

    for field in updatable_fields:
        value = getattr(car, field)
        if value is not None:
            setattr(car_db, field, value)

    db.add(car_db)
    db.commit()
    db.refresh(car_db)

    return car_db
    

@router.delete("/{car_id}", status_code=204)
def delete_car(car_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role not in {"ADMIN", "AGENT"}:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    car_db = db.query(Car).filter(Car.id == car_id).first()

    if not car_db:
        raise HTTPException(status_code=404, detail="Car not found")

    car_db.status = "DISABLED"
    db.commit()

    return {"detail": "Car deleted successfully"}

