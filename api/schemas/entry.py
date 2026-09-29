from datetime import datetime

from pydantic import ConfigDict, Field
from sqlmodel import SQLModel

from schemas.item import ItemRead


class EntryCreate(SQLModel):
	item_id: int


class EntryUpdate(SQLModel):
	is_favorite: bool | None = None
	notes: str | None = Field(default=None, max_length=2000)


class EntryRead(SQLModel):
	model_config = ConfigDict(from_attributes=True)

	id: int
	item_id: int
	is_favorite: bool
	notes: str | None
	added_at: datetime
	item: ItemRead


class EntryList(SQLModel):
	items: list[EntryRead]
	total: int
