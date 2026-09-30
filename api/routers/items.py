from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_session
from dependencies.pagination import Pagination, get_pagination
from models.item import Item
from schemas.item import ItemList, ItemRead

router = APIRouter(prefix="/items", tags=["items"])


@router.get(
    "",
    response_model=ItemList,
    summary="Lister et rechercher les exercices",
)
async def list_items(
    session: Annotated[AsyncSession, Depends(get_session)],
    pagination: Annotated[Pagination, Depends(get_pagination)],
    q: str | None = Query(default=None, min_length=1, max_length=120),
    categorie: str | None = Query(default=None, max_length=80),
) -> ItemList:
    filters = []
    if q:
        pattern = f"%{q.strip()}%"
        filters.append(or_(Item.name.ilike(pattern), Item.description.ilike(pattern), Item.muscle_group.ilike(pattern)))
    if categorie:
        filters.append(Item.category == categorie)

    total = (await session.execute(select(func.count()).select_from(Item).where(*filters))).scalar_one()
    rows = await session.execute(
        select(Item)
        .where(*filters)
        .order_by(Item.category, Item.name)
        .offset((pagination.page - 1) * pagination.limit)
        .limit(pagination.limit)
    )
    return ItemList(
        results=rows.scalars().all(),
        total=total,
        page=pagination.page,
        limit=pagination.limit,
    )


@router.get(
    "/{item_id}",
    response_model=ItemRead,
    summary="Lire une fiche exercice",
    responses={404: {"description": "Exercice introuvable"}},
)
async def get_item(item_id: int, session: Annotated[AsyncSession, Depends(get_session)]) -> ItemRead:
    item = await session.get(Item, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail=f"Exercice {item_id} introuvable")
    return item
