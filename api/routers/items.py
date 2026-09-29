from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_session
from models.item import Item
from schemas.item import ItemList, ItemRead

router = APIRouter(prefix="/items", tags=["items"])


@router.get("", response_model=ItemList)
async def list_items(
    session: Annotated[AsyncSession, Depends(get_session)],
    q: str | None = Query(default=None, max_length=120),
    category: str | None = Query(default=None, max_length=80),
    difficulty: str | None = Query(default=None, max_length=40),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=12, ge=1, le=100),
):
    filters = []
    if q:
        pattern = f"%{q.strip()}%"
        filters.append(or_(Item.name.ilike(pattern), Item.description.ilike(pattern), Item.muscle_group.ilike(pattern)))
    if category:
        filters.append(Item.category == category)
    if difficulty:
        filters.append(Item.difficulty == difficulty)

    total = (await session.execute(select(func.count()).select_from(Item).where(*filters))).scalar_one()
    rows = await session.execute(
        select(Item).where(*filters).order_by(Item.category, Item.name).offset((page - 1) * size).limit(size)
    )
    categories = await session.execute(select(Item.category).distinct().order_by(Item.category))
    return ItemList(
        items=rows.scalars().all(),
        total=total,
        page=page,
        size=size,
        categories=categories.scalars().all(),
    )


@router.get("/{item_id}", response_model=ItemRead)
async def get_item(item_id: int, session: Annotated[AsyncSession, Depends(get_session)]):
    item = await session.get(Item, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail=f"Exercice {item_id} introuvable")
    return item
