from pydantic import BaseModel, ConfigDict, Field, EmailStr
from decimal import Decimal


class CategoryCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)


class CategoryResponse(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)

class CategoryUpdate(BaseModel):
    name: str = Field(min_length=2, max_length=100)

class ProductCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    description: str | None = Field(default=None, max_length=255)
    price: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    category_id: int = Field(gt=0)


class ProductResponse(ProductCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)

class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    description: str | None = Field(default=None, max_length=255)
    price: Decimal | None = Field(
        default=None, gt=0, max_digits=10, decimal_places=2
    )
    category_id: int | None = Field(default=None, gt=0)
    
class UserCreate(BaseModel):  # что клиент присылает при регистрации
    username: str = Field(min_length=3, max_length=50)  # имя: от 3 до 50 символов (как в базе)
    email: EmailStr  # Pydantic проверит, что это email (есть @, домен и так далее)
    password: str = Field(min_length=8, max_length=128)  # пароль: минимум 8 символов


class UserResponse(BaseModel):  # что мы отправляем клиенту в ответ
    id: int  # номер пользователя
    username: str  # имя
    email: EmailStr  # почта
    # Поля password здесь нет специально: пароль и хеш клиенту отдавать нельзя

    model_config = ConfigDict(from_attributes=True)  # разрешаем строить ответ из объекта SQLAlchemy (User)

class Token(BaseModel):  
    access_token: str  
    token_type: str  # тип токена; у нас всегда "bearer"