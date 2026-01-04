from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

engine = create_engine("sqlite+pysqlite:///C:/Users/HomePC/Desktop/FreeTimeCodes/Rental-Car-Project/Rental-Cars/Backend/app/db/database.db", echo=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

from app.models.user import User
from app.models.car import Car
from app.models.rental import Rental