from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_session
from dependencies.auth import get_current_user
from models.entry import Entry
from models.item import Item
from models.user import User
from schemas.entry import EntryCreate, EntryList, EntryRead, EntryStatus, EntryUpdate
from schemas.item import ItemRead

router = APIRouter(prefix="/me/collection", tags=["collection"])


async def _entry_response(session: AsyncSession, entry: Entry) -> EntryRead:
    item = await session.get(Item, entry.item_id)
    return EntryRead(
        id=entry.id,
        item_id=entry.item_id,
        status=entry.status,
        rating=entry.rating,
        comment=entry.comment,
        added_at=entry.added_at,
        item=ItemRead.model_validate(item),
    )


@router.get("", response_model=EntryList)
async def get_collection(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
    status_filter: Annotated[EntryStatus | None, Query(alias="status")] = None,
    sort: Literal["date", "rating"] = "date",
):
    statement = select(Entry).where(Entry.user_id == current_user.id)
    if status_filter is not None:
        statement = statement.where(Entry.status == status_filter)
    if sort == "rating":
        statement = statement.order_by(Entry.rating.desc().nulls_last(), Entry.added_at.desc())
    else:
        statement = statement.order_by(Entry.added_at.desc())
    result = await session.execute(statement)
    entries = result.scalars().all()
    return EntryList(items=[await _entry_response(session, entry) for entry in entries], total=len(entries))


@router.post("", response_model=EntryRead, status_code=status.HTTP_201_CREATED)
async def add_to_collection(
    payload: EntryCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    item = await session.get(Item, payload.item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Exercice introuvable")
    existing = await session.execute(
        select(Entry).where(Entry.user_id == current_user.id, Entry.item_id == payload.item_id)
    )
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(status_code=409, detail="Cet exercice est déjà dans votre collection")
    entry = Entry(
        user_id=current_user.id,
        item_id=payload.item_id,
        status=payload.status,
        rating=payload.rating,
        comment=payload.comment,
    )
    session.add(entry)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=409, detail="Cet exercice est déjà dans votre collection") from None
    await session.refresh(entry)
    return EntryRead(
        id=entry.id,
        item_id=entry.item_id,
        status=entry.status,
        rating=entry.rating,
        comment=entry.comment,
        added_at=entry.added_at,
        item=ItemRead.model_validate(item),
    )


@router.get("/{item_id}", response_model=EntryRead)
async def get_collection_item(
    item_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    result = await session.execute(
        select(Entry).where(Entry.user_id == current_user.id, Entry.item_id == item_id)
    )
    entry = result.scalar_one_or_none()
    if entry is None:
        raise HTTPException(status_code=404, detail="Exercice absent de votre collection")
    return await _entry_response(session, entry)


@router.patch("/{item_id}", response_model=EntryRead)
async def update_collection_item(
    item_id: int,
    payload: EntryUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    result = await session.execute(
        select(Entry).where(Entry.user_id == current_user.id, Entry.item_id == item_id)
    )
    entry = result.scalar_one_or_none()
    if entry is None:
        raise HTTPException(status_code=404, detail="Exercice absent de votre collection")
    changes = payload.model_dump(exclude_unset=True)
    if not changes:
        raise HTTPException(status_code=422, detail="Aucune modification fournie")
    if "status" in changes and changes["status"] is None:
        raise HTTPException(status_code=422, detail="status ne peut pas être null")
    for field, value in changes.items():
        setattr(entry, field, value)
    await session.commit()
    await session.refresh(entry)
    return await _entry_response(session, entry)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_collection(
    item_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    result = await session.execute(
        select(Entry).where(Entry.user_id == current_user.id, Entry.item_id == item_id)
    )
    entry = result.scalar_one_or_none()
    if entry is None:
        raise HTTPException(status_code=404, detail="Exercice absent de votre collection")
    await session.delete(entry)
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
