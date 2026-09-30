from typing import Literal

from sqlmodel import SQLModel


class RootRead(SQLModel):
    message: str


class HealthRead(SQLModel):
    status: Literal["ok"]