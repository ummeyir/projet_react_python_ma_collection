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
from schemas.entry import EntryCreate, EntryRead, EntryStatus, EntryUpdate
from schemas.item import ItemRead

router = APIRouter(prefix="/me/collection", tags=["collection"])


def _entry_response(entry: Entry, item: Item) -> EntryRead:
    return EntryRead(
        id=entry.id,
        statut=entry.status,
        note=entry.rating,
        commentaire=entry.comment,
        date_ajout=entry.added_at,
        item=ItemRead.model_validate(item),
    )


@router.get(
    "",
    response_model=list[EntryRead],
    summary="Consulter la collection personnelle",
    responses={401: {"description": "Authentification requise"}},
)
async def get_collection(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
    statut: EntryStatus | None = None,
    tri: Literal["date", "note"] = "date",
) -> list[EntryRead]:
    filters = [Entry.user_id == current_user.id]
    if statut is not None:
        filters.append(Entry.status == statut)
    statement = select(Entry, Item).join(Item, Entry.item_id == Item.id).where(*filters)
    if tri == "note":
        statement = statement.order_by(
            Entry.rating.desc().nulls_last(), Entry.added_at.desc(), Entry.id.desc()
        )
    else:
        statement = statement.order_by(Entry.added_at.desc(), Entry.id.desc())
    result = await session.execute(statement)
    entries = result.all()
    return [_entry_response(entry, item) for entry, item in entries]


@router.post(
    "",
    response_model=EntryRead,
    status_code=status.HTTP_201_CREATED,
    summary="Ajouter un exercice à la collection",
    responses={
        401: {"description": "Authentification requise"},
        404: {"description": "Exercice introuvable"},
        409: {"description": "Exercice déjà présent"},
    },
)
async def add_to_collection(
    payload: EntryCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> EntryRead:
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
        status=payload.statut,
        rating=payload.note,
        comment=payload.commentaire,
    )
    session.add(entry)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=409, detail="Cet exercice est déjà dans votre collection") from None
    await session.refresh(entry)
    return _entry_response(entry, item)


@router.get(
    "/{entry_id}",
    response_model=EntryRead,
    summary="Lire une entrée de collection",
    responses={401: {"description": "Authentification requise"}, 404: {"description": "Entrée introuvable"}},
)
async def get_collection_item(
    entry_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> EntryRead:
    result = await session.execute(
        select(Entry).where(Entry.user_id == current_user.id, Entry.id == entry_id)
    )
    entry = result.scalar_one_or_none()
    if entry is None:
        raise HTTPException(status_code=404, detail="Exercice absent de votre collection")
    item = await session.get(Item, entry.item_id)
    return _entry_response(entry, item)


@router.patch(
    "/{entry_id}",
    response_model=EntryRead,
    summary="Modifier une entrée de collection",
    responses={
        400: {"description": "Modification invalide"},
        401: {"description": "Authentification requise"},
        404: {"description": "Entrée introuvable"},
    },
)
async def update_collection_item(
    entry_id: int,
    payload: EntryUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> EntryRead:
    result = await session.execute(
        select(Entry).where(Entry.user_id == current_user.id, Entry.id == entry_id)
    )
    entry = result.scalar_one_or_none()
    if entry is None:
        raise HTTPException(status_code=404, detail="Exercice absent de votre collection")
    changes = payload.model_dump(exclude_unset=True)
    if not changes:
        raise HTTPException(status_code=400, detail="Aucune modification fournie")
    if "statut" in changes and changes["statut"] is None:
        raise HTTPException(status_code=400, detail="statut ne peut pas être null")
    field_names = {"statut": "status", "note": "rating", "commentaire": "comment"}
    for field, value in changes.items():
        setattr(entry, field_names[field], value)
    await session.commit()
    await session.refresh(entry)
    item = await session.get(Item, entry.item_id)
    return _entry_response(entry, item)


@router.delete(
    "/{entry_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Supprimer une entrée de collection",
    responses={401: {"description": "Authentification requise"}, 404: {"description": "Entrée introuvable"}},
)
async def remove_from_collection(
    entry_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> Response:
    result = await session.execute(
        select(Entry).where(Entry.user_id == current_user.id, Entry.id == entry_id)
    )
    entry = result.scalar_one_or_none()
    if entry is None:
        raise HTTPException(status_code=404, detail="Exercice absent de votre collection")
    await session.delete(entry)
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
