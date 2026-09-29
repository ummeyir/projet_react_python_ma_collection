from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from db.database import get_session
from models.user import User
from core.security import decode_access_token

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
	credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
	session: Annotated[AsyncSession, Depends(get_session)],
) -> User:
	unauthorized = HTTPException(
		status_code=status.HTTP_401_UNAUTHORIZED,
		detail="Authentification requise ou jeton invalide",
		headers={"WWW-Authenticate": "Bearer"},
	)
	if credentials is None:
		raise unauthorized
	try:
		payload = decode_access_token(credentials.credentials)
		user_id = int(payload["sub"])
	except (jwt.InvalidTokenError, KeyError, TypeError, ValueError):
		raise unauthorized from None
	user = await session.get(User, user_id)
	if user is None:
		raise unauthorized
	return user
