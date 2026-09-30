from sqlmodel import SQLModel

from schemas.entry import EntryStatus


class CollectionStats(SQLModel):
	total: int
	par_statut: dict[EntryStatus, int]
	note_moyenne: float | None