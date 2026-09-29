from pydantic import ConfigDict
from sqlmodel import SQLModel


class ItemRead(SQLModel):
	model_config = ConfigDict(from_attributes=True)

	id: int
	category: str
	name: str
	muscle_group: str
	equipment: str
	difficulty: str
	description: str
	image_url: str | None = None


class ItemList(SQLModel):
	items: list[ItemRead]
	total: int
	page: int
	size: int
	categories: list[str]
