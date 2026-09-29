from datetime import datetime
from typing import Literal

from pydantic import ConfigDict, Field
from sqlmodel import SQLModel

from schemas.item import ItemRead

EntryStatus = Literal["a_decouvrir", "en_cours", "termine"]


class EntryCreate(SQLModel):
	item_id: int
	status: EntryStatus = "a_decouvrir"
	rating: int | None = Field(default=None, ge=1, le=5)
	comment: str | None = Field(default=None, max_length=2000)


class EntryUpdate(SQLModel):
	status: EntryStatus | None = None
	rating: int | None = Field(default=None, ge=1, le=5)
	comment: str | None = Field(default=None, max_length=2000)


class EntryRead(SQLModel):
	model_config = ConfigDict(from_attributes=True)

	id: int
	item_id: int
	status: EntryStatus
	rating: int | None
	comment: str | None
	added_at: datetime
	item: ItemRead


class EntryList(SQLModel):
	items: list[EntryRead]
	total: int
