import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession  # тип сессии

from app.database import get_db  # сессия базы
from app.models import User  # модель пользователя
from app.security import ALGORITHM, SECRET_KEY  # настройки токена из security.py

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")  # путь к эндпоинту логина

async def get_current_user(
    token: str = Depends(oauth2_scheme),  # FastAPI сам достанет токен из заголовка
    db: AsyncSession = Depends(get_db),  
) -> User:
    
    credentials_exception = HTTPException(
        status_code=401,  
        detail="Не удалось проверить токен",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Проверяем подпись и срок действия; если всё в порядке, получаем содержимое токена
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.InvalidTokenError:  # токен подделан, повреждён или просрочен
        raise credentials_exception

    user_id = payload.get("sub")  # достаём номер пользователя, который мы клали при входе

    if user_id is None:  
        raise credentials_exception

    user = await db.get(User, int(user_id))  # ищем пользователя в базе по номеру

    if user is None:  
        raise credentials_exception

    return user  # возвращаем найденного пользователя


async def get_current_admin(
    current_user: User = Depends(get_current_user),  # сначала проверяем вход, как выше
) -> User:
    if not current_user.is_admin:  # пользователь вошёл, но он не админ
        raise HTTPException(
            status_code=403,  # 403 = доступ запрещён
            detail="Недостаточно прав",
        )

    return current_user 