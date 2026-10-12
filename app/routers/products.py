from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Product, Category
from app.schemas import ProductCreate, ProductResponse


router = APIRouter(prefix="/products", tags=["Products"])


@router.post("/", response_model=ProductResponse, status_code=201)
async def create_product(
    product: ProductCreate,
    db: AsyncSession = Depends(get_db)
):
    category = await db.get(Category, product.category_id)

    if category is None:
        raise HTTPException(
            status_code=404,
            detail="Категория не найдена"
        )

    new_product = Product(**product.model_dump())

    db.add(new_product)
    await db.commit()
    await db.refresh(new_product)

    return new_product

@router.get("/", response_model=list[ProductResponse])
async def get_products(
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Product).options(selectinload(Product.category))
    )
    products = result.scalars().all()

    return products

@router.patch("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_update: ProductCreate,
    db: AsyncSession = Depends(get_db)
):
    product = await db.get(Product, product_id)

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Продукт не найден"
        )

    for key, value in product_update.model_dump().items():
        setattr(product, key, value)

    await db.commit()
    await db.refresh(product)

    return product

@router.delete("/{product_id}", status_code=204)
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):
    product = await db.get(Product, product_id)

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Продукт не найден"
        )

    await db.delete(product)
    await db.commit()

    return None
    