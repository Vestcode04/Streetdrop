from fastapi import APIRouter, Depends, HTTPException  
from sqlalchemy.exc import IntegrityError  
from sqlalchemy.ext.asyncio import AsyncSession  

from app.dependencies import get_current_user  
from app.database import get_db  # функция, которая выдаёт сессию базы
from app.models import User  # модель пользователя
from app.schemas import UserCreate, UserResponse  # наши схемы
from app.security import hash_password  # функция хеширования

router = APIRouter(
    prefix="/users",  
    tags=["Users"],  
)

@router.post("/", response_model=UserResponse, status_code=201)  
async def create_user(
    user: UserCreate,  # FastAPI сам проверит присланный JSON по схеме UserCreate
    db: AsyncSession = Depends(get_db),  # FastAPI сам подставит сессию базы
):
    new_user = User(  # создаём объект пользователя (пока только в памяти)
        username=user.username,  # имя берём как есть
        email=user.email.lower(),  # почту приводим к маленьким буквам, чтобы A@x.com и a@x.com были одним адресом
        password_hash=hash_password(user.password),  # в базу кладём хеш, а не пароль
    )

    db.add(new_user)  

    try:
        await db.commit()  # сохраняем в базу
    except IntegrityError:  # если такой username или email уже есть
        await db.rollback()  # отменяем неудачное сохранение
        raise HTTPException(
            status_code=409,  # 409 = конфликт
            detail="Пользователь с таким username или email уже существует",
        )

    await db.refresh(new_user)  # перечитываем из базы, чтобы появился id

    return new_user  # возвращаем; response_model оставит только id, username, email

@router.get("/me", response_model=UserResponse)
async def read_current_user(
    current_user: User = Depends(get_current_user),  
):
    return current_user  # возвращаем текущего пользователя