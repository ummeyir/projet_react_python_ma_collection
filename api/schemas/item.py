from pydantic import ConfigDict, Field
from sqlmodel import SQLModel


class ItemRead(SQLModel):
	model_config = ConfigDict(from_attributes=True)

	id: int
	titre: str = Field(validation_alias="name")
	categorie: str = Field(validation_alias="category")
	description: str
	image_url: str | None
	annee: int | None = Field(default=None, validation_alias="year")
	groupe_musculaire: str = Field(validation_alias="muscle_group")
	equipement: str = Field(validation_alias="equipment")
	difficulte: str = Field(validation_alias="difficulty")


class ItemList(SQLModel):
	results: list[ItemRead]
	total: int
	page: int
	limit: int
