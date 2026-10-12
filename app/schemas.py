from pydantic import BaseModel, ConfigDict, Field


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
    price: float = Field(gt=0)
    category_id: int    

class ProductResponse(BaseModel):
    id : int

    model_config = ConfigDict(from_attributes=True)

class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    description: str | None = Field(default=None, max_length=255)
    price: Decimal | None = Field(
        default=None, gt=0, max_digits=10, decimal_places=2
    )
    category_id: int | None = Field(default=None, gt=0)
    