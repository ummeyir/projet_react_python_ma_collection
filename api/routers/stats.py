from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_session
from dependencies.auth import get_current_user
from models.entry import Entry
from models.item import Item
from models.user import User

router = APIRouter(prefix="/me/stats", tags=["stats"])


@router.get("")
async def get_stats(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    total_items = (await session.execute(select(func.count()).select_from(Item))).scalar_one()
    total_collection = (
        await session.execute(select(func.count()).select_from(Entry).where(Entry.user_id == current_user.id))
    ).scalar_one()
    favorite_count = (
        await session.execute(
            select(func.count()).select_from(Entry).where(Entry.user_id == current_user.id, Entry.is_favorite.is_(True))
        )
    ).scalar_one()
    return {
        "total_items": total_items,
        "total_collection": total_collection,
        "favorite_count": favorite_count,
    }
