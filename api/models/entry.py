from datetime import datetime, timezone

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel


class Entry(SQLModel, table=True):
	__table_args__ = (UniqueConstraint("user_id", "item_id", name="uq_entry_user_item"),)

	id: int | None = Field(default=None, primary_key=True)
	user_id: int = Field(foreign_key="user.id", index=True)
	item_id: int = Field(foreign_key="item.id", index=True)
	is_favorite: bool = False
	notes: str | None = None
	added_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
