from dataclasses import dataclass

from fastapi import Query


@dataclass(frozen=True)
class Pagination:
	page: int
	limit: int


def get_pagination(
	page: int = Query(default=1, ge=1),
	limit: int = Query(default=12, ge=1, le=50),
) -> Pagination:
	return Pagination(page=page, limit=limit)
