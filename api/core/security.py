from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext

from core.config import settings

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
	return password_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
	return password_context.verify(password, hashed_password)


def create_access_token(subject: str) -> str:
	expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
	return jwt.encode({"sub": subject, "exp": expires_at}, settings.secret_key, algorithm=settings.algorithm)


def decode_access_token(token: str) -> dict:
	return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
