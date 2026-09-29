from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_session
from dependencies.auth import get_current_user
from models.entry import Entry
from models.user import User
from schemas.entry import EntryStatus
from schemas.stats import CollectionStats

router = APIRouter(prefix="/me/stats", tags=["stats"])


@router.get("", response_model=CollectionStats)
async def get_stats(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    total_collection = (
        await session.execute(select(func.count()).select_from(Entry).where(Entry.user_id == current_user.id))
    ).scalar_one()
    status_counts: dict[EntryStatus, int] = {
        "a_decouvrir": 0,
        "en_cours": 0,
        "termine": 0,
    }
    grouped_counts = await session.execute(
        select(Entry.status, func.count())
        .where(Entry.user_id == current_user.id)
        .group_by(Entry.status)
    )
    for entry_status, count in grouped_counts:
        if entry_status in status_counts:
            status_counts[entry_status] = count

    average_rating = (
        await session.execute(select(func.avg(Entry.rating)).where(Entry.user_id == current_user.id))
    ).scalar_one()
    return CollectionStats(
        total=total_collection,
        by_status=status_counts,
        average_rating=float(average_rating) if average_rating is not None else None,
    )
