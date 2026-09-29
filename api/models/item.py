from sqlmodel import Field, SQLModel


class Item(SQLModel, table=True):
	id: int | None = Field(default=None, primary_key=True)
	category: str = Field(index=True, max_length=80)
	name: str = Field(index=True, max_length=120)
	muscle_group: str = Field(max_length=100)
	equipment: str = Field(max_length=120)
	difficulty: str = Field(max_length=40)
	description: str
	image_url: str | None = None
