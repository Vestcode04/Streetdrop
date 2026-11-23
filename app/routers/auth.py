from fastapi import APIRouter, Depends, HTTPException  
from fastapi.security import OAuth2PasswordRequestForm  # готовая форма входа (поля username и password)
from sqlalchemy import select  
from sqlalchemy.ext.asyncio import AsyncSession  

from app.database import get_db  # сессия базы
from app.models import User  # модель пользователя
from app.schemas import Token  # схема ответа
from app.security import create_access_token, verify_password  

router = APIRouter(
    prefix="/auth",  
    tags=["Auth"],  
)


@router.post("/login", response_model=Token)  # POST /auth/login
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),  # сессия базы
):
    # Стандартная форма называет поле "username", но мы кладём туда email.
    result = await db.execute(
        select(User).where(User.email == form_data.username.lower())  # ищем пользователя по email
    )
    user = result.scalar_one_or_none()  # берём найденного пользователя или None

    if user is None or not verify_password(form_data.password, user.password_hash):
        # Если пользователя нет или пароль не подошёл, отвечаем одинаково,
        # чтобы нельзя было узнать, зарегистрирован ли такой email
        raise HTTPException(
            status_code=401,  # 401 = не авторизован
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},  # так принято по стандарту для токенов
        )

    token = create_access_token(user.id)  # создаём токен для этого пользователя

    return {"access_token": token, "token_type": "bearer"}  # отдаём токен клиенту