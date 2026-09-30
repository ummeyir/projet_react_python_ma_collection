from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import create_access_token, hash_password, verify_password
from db.database import get_session
from dependencies.auth import get_current_user
from models.user import User
from schemas.user import LoginRequest, TokenRead, UserCreate, UserRead

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Créer un compte",
    responses={409: {"description": "Adresse e-mail déjà utilisée"}},
)
async def register_user(
    payload: UserCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UserRead:
    email = str(payload.email).lower()
    existing = await session.execute(select(User).where(User.email == email))
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(status_code=409, detail="Cette adresse e-mail est déjà utilisée")

    user = User(email=email, hashed_password=hash_password(payload.password))
    session.add(user)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=409, detail="Cette adresse e-mail est déjà utilisée") from None
    await session.refresh(user)
    return user


@router.post(
    "/login",
    response_model=TokenRead,
    summary="Se connecter",
    responses={401: {"description": "Identifiants invalides"}},
)
async def login_user(
    payload: LoginRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> TokenRead:
    result = await session.execute(select(User).where(User.email == str(payload.email).lower()))
    user = result.scalar_one_or_none()
    if user is None or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Adresse e-mail ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return TokenRead(access_token=create_access_token(str(user.id)))


@router.get(
    "/me",
    response_model=UserRead,
    summary="Lire le compte courant",
    responses={401: {"description": "Authentification requise"}},
)
async def read_current_user(current_user: Annotated[User, Depends(get_current_user)]) -> UserRead:
    return current_user
