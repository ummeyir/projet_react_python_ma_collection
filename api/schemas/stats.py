from sqlmodel import SQLModel

from schemas.entry import EntryStatus


class CollectionStats(SQLModel):
	total: int
	by_status: dict[EntryStatus, int]
	average_rating: float | None