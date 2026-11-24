import os 
from datetime import datetime, timedelta, timezone  

import jwt  
from dotenv import load_dotenv 
from pwdlib import PasswordHash  

load_dotenv()  

SECRET_KEY = os.getenv("SECRET_KEY")  
ALGORITHM = os.getenv("ALGORITHM", "HS256")  
ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")  
)

if not SECRET_KEY:  
    raise RuntimeError("SECRET_KEY не найден в .env")

hasher = PasswordHash.recommended()  

def hash_password(password: str) -> str:  
    return hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:  # проверяет пароль по хешу
    return hasher.verify(password, password_hash)  # True, если пароль подходит; иначе False


def create_access_token(user_id: int) -> str:  # создаёт токен для пользователя с этим id
    expire = datetime.now(timezone.utc) + timedelta(  # момент, когда токен перестанет действовать
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {  # содержимое токена
        "sub": str(user_id),  # «subject»: кому выдан токен; по стандарту это строка
        "exp": expire,  # «expires»: когда истекает; библиотека сама проверит это при чтении
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)  # подписываем и получаем строку-токен