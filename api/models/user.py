from uuid import uuid4

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
	id: int | None = Field(default=None, primary_key=True)
	username: str = Field(default_factory=lambda: uuid4().hex, index=True, unique=True, max_length=50)
	email: str = Field(index=True, unique=True, max_length=254)
	hashed_password: str
