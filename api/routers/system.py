from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_session
from schemas.system import HealthRead, RootRead

router = APIRouter(tags=["system"])


@router.get("/", response_model=RootRead, summary="Vérifier que l'API répond")
async def root() -> RootRead:
    return RootRead(message="Ma Collection API")


@router.get("/health", response_model=HealthRead, summary="Vérifier la connexion à la base")
async def health_check(session: Annotated[AsyncSession, Depends(get_session)]) -> HealthRead:
    await session.execute(text("SELECT 1"))
    return HealthRead(status="ok")