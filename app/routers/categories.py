from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models import Category, Product, User
from app.schemas import CategoryCreate, CategoryResponse, CategoryUpdate
from app.dependencies import get_current_admin

router = APIRouter(
    prefix="/categories",
    tags=["Categories"],
)

@router.post("/", response_model=CategoryResponse,status_code=201)
async def create_category(
    category: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin)  
):
    new_category = Category(name=category.name)

    db.add(new_category)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Не удалось создать категорию. Возможно, она уже существует"
        )

    await db.refresh(new_category)

    return new_category


@router.get("/", response_model=list[CategoryResponse])
async def get_categories(
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Category))

    categories = result.scalars().all()

    return categories

@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: int,
    db: AsyncSession = Depends(get_db)
):
    category = await db.get(Category, category_id)

    if category is None:
        raise HTTPException(
            status_code=404,
            detail="Категория не найдена"
        )

    return category

@router.patch("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    category_update: CategoryUpdate,
    db: AsyncSession = Depends(get_db)
):
    category = await db.get(Category, category_id)

    if category is None:
        raise HTTPException(
            status_code=404,
            detail="Категория не найдена"
        )

    category.name = category_update.name

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Не удалось обновить категорию. Возможно, она уже существует"
        )

    await db.refresh(category)

    return category

@router.delete("/{category_id}", status_code=204)
async def delete_category(
    category_id: int,
    db: AsyncSession = Depends(get_db)
):
    category = await db.get(Category, category_id)

    if category is None:
        raise HTTPException(
            status_code=404,
            detail="Категория не найдена"
        )

    result = await db.execute(
        select(Product.id)
        .where(Product.category_id == category_id)
        .limit(1)
    )

    if result.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=409,
            detail="Нельзя удалить категорию, в которой есть товары"
        )

    await db.delete(category)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Категория связана с товарами"
        )