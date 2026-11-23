from fastapi import FastAPI
from sqlalchemy import text

from app.database import engine
from app.routers import categories , products, users, auth

app = FastAPI(title="StreetDrop API")
app.include_router(categories.router)
app.include_router(products.router)
app.include_router(users.router)
app.include_router(auth.router)

@app.get("/")
async def home():
    return {"message": "Welcome to StreetDrop"}


@app.get("/health/db")
async def check_database():
    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))

    return {"database": "connected"}