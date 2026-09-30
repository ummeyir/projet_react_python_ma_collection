from datetime import datetime
from typing import Literal

from pydantic import ConfigDict, Field
from sqlmodel import SQLModel

from schemas.item import ItemRead

EntryStatus = Literal["a_decouvrir", "en_cours", "termine"]


class EntryCreate(SQLModel):
	item_id: int
	statut: EntryStatus = "a_decouvrir"
	note: int | None = Field(default=None, ge=1, le=5)
	commentaire: str | None = Field(default=None, max_length=2000)


class EntryUpdate(SQLModel):
	statut: EntryStatus | None = None
	note: int | None = Field(default=None, ge=1, le=5)
	commentaire: str | None = Field(default=None, max_length=2000)


class EntryRead(SQLModel):
	model_config = ConfigDict(from_attributes=True, populate_by_name=True)

	id: int
	statut: EntryStatus = Field(validation_alias="status")
	note: int | None = Field(validation_alias="rating")
	commentaire: str | None = Field(validation_alias="comment")
	date_ajout: datetime = Field(validation_alias="added_at")
	item: ItemRead
