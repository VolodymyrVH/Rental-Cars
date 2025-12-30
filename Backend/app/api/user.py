from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.schemas.user import UserCreateSchema, UserResponseSchema
from app.core.security import get_password_hash

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/{user_id}", response_model=UserResponseSchema)
def get_user(user_id: int, db = Depends(get_db)):
    user_db = db.query(User).filter(User.id == user_id).first()
    if not user_db:
        raise HTTPException(status_code=404, detail="User not found")
    return user_db


@router.post("/", response_model=UserResponseSchema)
def create_user(user: UserCreateSchema, db: Session = Depends(get_db)):
    normalized_email = user.email.lower()
    existing = db.query(User).filter((User.email == normalized_email) | (User.phone_number == user.phone_number)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email or phone already registered")

    user_db = User(
        first_name = user.first_name,
        last_name = user.last_name,
        email = normalized_email,
        phone_number = user.phone_number,
        hashed_password = get_password_hash(user.password),
    )

    db.add(user_db)
    db.commit()
    db.refresh(user_db)

    return user_db

