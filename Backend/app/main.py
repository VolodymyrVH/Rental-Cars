from fastapi import FastAPI
from app.api import auth
from app.api import cars
from app.api import rentals
from app.api import users

app = FastAPI()
app.include_router(auth.router)
app.include_router(cars.router)
app.include_router(rentals.router)
app.include_router(users.router)

@app.get('/')
async def root():
    return {"message": "Hello, World!"}